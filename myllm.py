#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 统一调用工具类
提供统一的模型配置管理和调用接口
"""

import os
import litellm
from typing import List, Dict, Any, Optional
from config import Config
from logger import logger

class MyLLM:
    """
    LLM 统一调用工具类
    负责模型配置管理和统一调用接口
    """
    
    def __init__(self):
        self.available_models = Config.get_enabled_models()
        self._setup_environment()
    
    def _setup_environment(self):
        """设置环境变量"""
        # 配置环境变量
        for model_config in Config.MODELS:
            if os.getenv(model_config.api_key_env):
                os.environ[model_config.api_key_env] = os.getenv(model_config.api_key_env)
        
        # 设置 Azure 特殊配置
        if os.getenv("AZURE_API_VERSION"):
            os.environ["AZURE_API_VERSION"] = os.getenv("AZURE_API_VERSION", "2024-02-15-preview")
    
    def get_model_config(self, model_key: str):
        """获取模型配置"""
        return Config.get_model_by_name(model_key)
    
    def get_available_models(self):
        """获取可用模型列表"""
        return self.available_models
    
    def validate_model(self, model_key: str) -> tuple[bool, str, Optional[Any]]:
        """
        验证模型是否可用
        返回: (是否有效, 错误信息, 模型配置)
        """
        model_config = self.get_model_config(model_key)
        if not model_config:
            return False, f"不支持的模型: {model_key}", None
        
        # 检查 API 密钥
        if not os.getenv(model_config.api_key_env):
            return False, f"模型 {model_config.display_name} 未配置 API 密钥", None
        
        return True, "", model_config
    
    def build_completion_params(self, model_config, messages: List[Dict], 
                              max_tokens: int = None, temperature: float = None, 
                              stream: bool = False, **kwargs) -> Dict[str, Any]:
        """
        构建 litellm.completion 参数
        """
        completion_params = {
            'model': model_config.model_name,
            'messages': messages,
            'max_tokens': max_tokens or Config.MAX_TOKENS,
            'temperature': temperature or Config.TEMPERATURE,
            'stream': stream
        }
        
        # 添加特定模型的配置
        if model_config.base_url:
            completion_params['base_url'] = model_config.base_url
            # 对于使用base_url的模型，需要显式传递api_key
            completion_params['api_key'] = os.getenv(model_config.api_key_env)
        
        if model_config.custom_llm_provider:
            completion_params['custom_llm_provider'] = model_config.custom_llm_provider
        
        # 对于某些模型，设置较低的温度
        if 'azure' in model_config.model_name or 'qwen' in model_config.model_name:
            completion_params['temperature'] = 0.1
        
        # 添加额外参数
        completion_params.update(kwargs)
        
        return completion_params
    
    def completion(self, model_key: str, messages: List[Dict], 
                  max_tokens: int = None, temperature: float = None, 
                  stream: bool = False, **kwargs):
        """
        统一的模型调用接口
        """
        # 验证模型
        is_valid, error_msg, model_config = self.validate_model(model_key)
        if not is_valid:
            raise ValueError(error_msg)
        
        # 构建参数
        completion_params = self.build_completion_params(
            model_config, messages, max_tokens, temperature, stream, **kwargs
        )
        
        # 调用模型
        try:
            logger.info(f"调用模型: {model_config.display_name}, 参数: {completion_params.keys()}")
            response = litellm.completion(**completion_params)
            return response
        except Exception as e:
            logger.error(f"模型调用失败 - {model_config.display_name}: {e}")
            raise
    
    def get_default_model_key(self) -> str:
        """
        获取默认模型键名
        优先选择 GPT-4o，如果不可用则选择第一个可用模型
        """
        # 优先选择 gpt-4o
        for model in self.available_models:
            if 'gpt-4o' in model.name.lower():
                return model.name
        
        # 如果没有 gpt-4o，选择第一个可用模型
        if self.available_models:
            return self.available_models[0].name
        
        raise ValueError("没有可用的模型")
    
    def get_lightweight_model_key(self) -> str:
        """
        获取轻量级模型键名（用于意图分析等辅助任务）
        优先选择 gpt-4o-mini 或其他轻量级模型
        """
        # 优先选择轻量级模型
        lightweight_models = ['gpt-4o-mini', 'gpt-3.5-turbo', 'qwen']
        
        for lightweight in lightweight_models:
            for model in self.available_models:
                if lightweight in model.name.lower():
                    return model.name
        
        # 如果没有轻量级模型，使用默认模型
        return self.get_default_model_key()
    
    def simple_completion(self, prompt: str, model_key: str = None, 
                         max_tokens: int = 100, temperature: float = 0.3) -> str:
        """
        简单的文本补全接口
        用于意图分析等简单任务
        """
        if model_key is None:
            model_key = self.get_lightweight_model_key()
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.completion(
                model_key=model_key,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False
            )
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            else:
                raise ValueError("模型返回空响应")
                
        except Exception as e:
            logger.error(f"简单补全失败: {e}")
            raise

# 全局实例
myllm = MyLLM()