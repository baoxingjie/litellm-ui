#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
统一管理所有模型配置和应用设置
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """AI 模型配置类"""
    name: str
    display_name: str
    provider: str
    model_name: str
    api_key_env: str
    base_url: Optional[str] = None
    custom_llm_provider: Optional[str] = None
    enabled: bool = True


class Config:
    """应用配置类"""
    
    # Flask 配置
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 5000))
    
    # 聊天配置
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', 1000))
    TEMPERATURE = float(os.getenv('TEMPERATURE', 0.7))
    
    # 模型配置
    MODELS: List[ModelConfig] = [
        ModelConfig(
            name="gpt-4o",
            display_name="OpenAI GPT-4o",
            provider="openai",
            model_name="gpt-4o",
            api_key_env="OPENAI_API_KEY",
            enabled=False  # 暂时屏蔽
        ),
        ModelConfig(
            name="claude-3-sonnet",
            display_name="Anthropic Claude 3 Sonnet",
            provider="anthropic",
            model_name="claude-3-sonnet-20240229",
            api_key_env="ANTHROPIC_API_KEY",
            enabled=False  # 暂时屏蔽
        ),
        ModelConfig(
            name="azure-gpt-4o",
            display_name="Azure OpenAI GPT-4o",
            provider="azure",
            model_name="azure/gpt-4o",
            api_key_env="AZURE_API_KEY",
            base_url=os.getenv('AZURE_API_BASE')
        ),
        ModelConfig(
            name="qwen2.5-72b-instruct",
            display_name="阿里云 DashScope qwen2.5-72b-instruct",
            provider="openai",
            model_name="openai/qwen2.5-72b-instruct",
            api_key_env="DASHSCOPE_API_KEY",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        ),
        ModelConfig(
            name="baichuan4",
            display_name="百川 AI Baichuan4-turbo",
            provider="openai",
            model_name="openai/Baichuan4-turbo",
            api_key_env="BAICHUAN_API_KEY",
            base_url=os.getenv('BAICHUAN_BASE_URL')
        ),
        ModelConfig(
            name="DeepSeek-R1",
            display_name="Hugging Face DeepSeek-R1",
            provider="huggingface",
            model_name="huggingface/together/deepseek-ai/DeepSeek-R1",
            api_key_env="HF_TOKEN",
            custom_llm_provider="huggingface"
        ),
        ModelConfig(
            name="qwq",
            display_name="Ollama QwQ",
            provider="ollama",
            model_name="ollama/qwq",
            api_key_env="OLLAMA_API_KEY",
            base_url="http://localhost:11434",
            enabled=True
        )
    ]
    
    @classmethod
    def get_enabled_models(cls) -> List[ModelConfig]:
        """获取已启用的模型列表"""
        enabled_models = []
        for model in cls.MODELS:
            # 对于 Ollama 模型，不需要检查 API 密钥
            if model.provider == "ollama" and model.enabled:
                enabled_models.append(model)
            # 检查其他模型的 API 密钥是否存在
            elif os.getenv(model.api_key_env) and model.enabled:
                enabled_models.append(model)
        return enabled_models
    
    @classmethod
    def get_model_by_name(cls, name: str) -> Optional[ModelConfig]:
        """根据名称获取模型配置"""
        for model in cls.MODELS:
            if model.name == name:
                return model
        return None