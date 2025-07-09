#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Web 应用 - 多模型 AI 聊天界面
支持 OpenAI、Anthropic、Azure、DashScope、百川 AI 等多种模型
"""

import os
import time
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import litellm
from config import Config
from logger import logger

# 加载环境变量
load_dotenv()

# 验证关键环境变量
logger.info("验证环境变量配置...")
for model_config in Config.MODELS:
    if model_config.enabled:
        api_key = os.getenv(model_config.api_key_env)
        if api_key:
            logger.info(f"✅ {model_config.display_name}: API密钥已配置")
        else:
            logger.warning(f"⚠️  {model_config.display_name}: 缺少API密钥 {model_config.api_key_env}")

app = Flask(__name__)
app.config.from_object(Config)

# 配置 JSON 编码，确保中文字符正确显示
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

# 配置环境变量
for model_config in Config.MODELS:
    if os.getenv(model_config.api_key_env):
        os.environ[model_config.api_key_env] = os.getenv(model_config.api_key_env)

# 设置 Azure 特殊配置
if os.getenv("AZURE_API_VERSION"):
    os.environ["AZURE_API_VERSION"] = os.getenv("AZURE_API_VERSION", "2024-02-15-preview")

# 获取可用模型
available_models = Config.get_enabled_models()
logger.info(f"已加载 {len(available_models)} 个可用模型")

@app.route('/')
def index():
    # 转换为模板需要的格式
    models_dict = {model.name: {'name': model.display_name} for model in available_models}
    return render_template('index.html', models=models_dict)

@app.route('/chat', methods=['POST'])
def chat():
    start_time = time.time()
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        model_key = data.get('model', 'gpt-4o')
        is_stream = data.get('stream', False)
        
        if not message:
            logger.warning(f"收到空消息请求 - 模型: {model_key}")
            return jsonify({'error': '消息不能为空'}), 400
        
        # 查找模型配置
        model_config = Config.get_model_by_name(model_key)
        if not model_config:
            logger.error(f"不支持的模型: {model_key}")
            return jsonify({'error': '不支持的模型'}), 400
        
        # 检查 API 密钥
        if not os.getenv(model_config.api_key_env):
            logger.error(f"模型 {model_key} 缺少 API 密钥: {model_config.api_key_env}")
            return jsonify({'error': f'模型 {model_config.display_name} 未配置 API 密钥'}), 400
        
        logger.info(f"处理聊天请求 - 模型: {model_config.display_name}, 消息长度: {len(message)}, 流式: {is_stream}")
        
        messages = [{'role': 'user', 'content': message}]
        
        # 构建请求参数
        completion_params = {
            'model': model_config.model_name,
            'messages': messages,
            'max_tokens': Config.MAX_TOKENS,
            'temperature': Config.TEMPERATURE,
            'stream': is_stream
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
        
        if is_stream:
            # 流式响应
            return handle_streaming_response(completion_params, model_config, start_time)
        else:
            # 非流式响应
            return handle_normal_response(completion_params, model_config, start_time)
            
    except Exception as e:
        response_time = time.time() - start_time
        error_msg = str(e)
        model_name = model_config.display_name if 'model_config' in locals() else model_key
        logger.log_api_call(model_name, False, response_time, error_msg)
        return jsonify({'error': f'请求失败: {error_msg}'}), 500

def handle_normal_response(completion_params, model_config, start_time):
    """处理非流式响应"""
    try:
        response = litellm.completion(**completion_params)
        
        # 计算响应时间
        response_time = time.time() - start_time
        
        # 提取响应内容
        if response.choices and len(response.choices) > 0:
            reply = response.choices[0].message.content
            logger.log_api_call(model_config.display_name, True, response_time)
            return jsonify({'reply': reply})
        else:
            logger.log_api_call(model_config.display_name, False, response_time, "模型返回空响应")
            return jsonify({'error': '模型返回空响应'}), 500
    except Exception as e:
        response_time = time.time() - start_time
        error_msg = str(e)
        logger.log_api_call(model_config.display_name, False, response_time, error_msg)
        return jsonify({'error': f'请求失败: {error_msg}'}), 500

def handle_streaming_response(completion_params, model_config, start_time):
    """处理流式响应"""
    from flask import Response
    import json
    
    def generate():
        try:
            response = litellm.completion(**completion_params)
            
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        # 发送流式数据
                        data = json.dumps({'content': delta.content}, ensure_ascii=False)
                        yield f"data: {data}\n\n"
            
            # 发送结束标记
            yield "data: [DONE]\n\n"
            
            # 记录成功的API调用
            response_time = time.time() - start_time
            logger.log_api_call(model_config.display_name, True, response_time)
            
        except Exception as e:
            # 发送错误信息
            error_msg = str(e)
            error_data = json.dumps({'error': error_msg}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"
            
            # 记录失败的API调用
            response_time = time.time() - start_time
            logger.log_api_call(model_config.display_name, False, response_time, error_msg)
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    )

if __name__ == '__main__':
    logger.info(f"启动 LiteLLM Web UI 服务器")
    logger.info(f"监听地址: {Config.HOST}:{Config.PORT}")
    logger.info(f"调试模式: {Config.DEBUG}")
    
    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )