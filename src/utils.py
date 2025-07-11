#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
提供错误处理、重试机制等通用功能
"""

import time
import functools
from typing import Callable, Any, Optional
from logger import logger


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟倍数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"函数 {func.__name__} 第 {attempt + 1} 次调用失败: {str(e)}, "
                            f"{current_delay:.1f}s 后重试"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"函数 {func.__name__} 在 {max_retries} 次重试后仍然失败: {str(e)}"
                        )
            
            raise last_exception
        return wrapper
    return decorator


def validate_api_key(api_key: str, provider: str) -> bool:
    """
    验证 API 密钥格式
    
    Args:
        api_key: API 密钥
        provider: 提供商名称
    
    Returns:
        bool: 是否有效
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # 基本长度检查
    if len(api_key.strip()) < 10:
        return False
    
    # 特定提供商的格式检查
    api_key = api_key.strip()
    
    if provider.lower() == 'openai':
        return api_key.startswith('sk-')
    elif provider.lower() == 'anthropic':
        return api_key.startswith('sk-ant-')
    elif provider.lower() == 'azure':
        return len(api_key) >= 32  # Azure 密钥通常较长
    elif provider.lower() == 'dashscope':
        return api_key.startswith('sk-')
    elif provider.lower() == 'baichuan':
        return len(api_key) >= 20  # 百川 API 密钥格式
    
    return True  # 对于未知提供商，只做基本检查


def sanitize_error_message(error_msg: str) -> str:
    """
    清理错误消息，移除敏感信息
    
    Args:
        error_msg: 原始错误消息
    
    Returns:
        str: 清理后的错误消息
    """
    # 移除可能的 API 密钥
    import re
    
    # 匹配常见的 API 密钥模式
    patterns = [
        r'sk-[a-zA-Z0-9]{20,}',  # OpenAI 风格
        r'sk-ant-[a-zA-Z0-9-]{20,}',  # Anthropic 风格
        r'[a-f0-9]{32,}',  # 十六进制密钥
    ]
    
    cleaned_msg = error_msg
    for pattern in patterns:
        cleaned_msg = re.sub(pattern, '[API_KEY_HIDDEN]', cleaned_msg, flags=re.IGNORECASE)
    
    return cleaned_msg


def format_model_response(response: Any, model_name: str) -> dict:
    """
    格式化模型响应
    
    Args:
        response: 模型原始响应
        model_name: 模型名称
    
    Returns:
        dict: 格式化后的响应
    """
    try:
        if hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content
            
            # 获取使用统计信息
            usage = {}
            if hasattr(response, 'usage') and response.usage:
                usage = {
                    'prompt_tokens': getattr(response.usage, 'prompt_tokens', 0),
                    'completion_tokens': getattr(response.usage, 'completion_tokens', 0),
                    'total_tokens': getattr(response.usage, 'total_tokens', 0)
                }
            
            return {
                'content': content,
                'model': model_name,
                'usage': usage,
                'success': True
            }
        else:
            return {
                'content': '',
                'model': model_name,
                'usage': {},
                'success': False,
                'error': '模型返回空响应'
            }
    except Exception as e:
        return {
            'content': '',
            'model': model_name,
            'usage': {},
            'success': False,
            'error': sanitize_error_message(str(e))
        }


def calculate_cost(usage: dict, model_name: str) -> float:
    """
    计算 API 调用成本（估算）
    
    Args:
        usage: 使用统计信息
        model_name: 模型名称
    
    Returns:
        float: 估算成本（美元）
    """
    if not usage or 'total_tokens' not in usage:
        return 0.0
    
    # 简化的成本计算（实际价格可能不同）
    cost_per_1k_tokens = {
        'gpt-4o': 0.03,
        'claude-3-sonnet': 0.015,
        'azure/gpt-4o': 0.03,
        'qwen': 0.002,
        'baichuan': 0.005
    }
    
    # 查找匹配的模型
    rate = 0.01  # 默认费率
    for model_key, model_rate in cost_per_1k_tokens.items():
        if model_key.lower() in model_name.lower():
            rate = model_rate
            break
    
    total_tokens = usage.get('total_tokens', 0)
    return (total_tokens / 1000) * rate