#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通义千问模型测试脚本
"""

import os
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

def test_qwen():
    """
    测试通义千问模型
    """
    print("=== 通义千问模型测试 ===")
    
    # 从环境变量获取API密钥
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ 错误: 请在 .env 文件中设置 DASHSCOPE_API_KEY")
        print("请确保 .env 文件存在并包含有效的 DashScope API 密钥")
        return
    
    print(f"✅ 找到 API 密钥: {api_key[:8]}...")
    
    try:
        print("🚀 正在调用通义千问模型...")
        # 使用与main.py和config.py一致的配置
        response = completion(
            model="openai/qwen2.5-72b-instruct",  # 使用与config.py一致的模型名称
            messages=[{"role": "user", "content": "请介绍一下通义大模型"}],
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key=api_key  # 需要显式传递API密钥
        )
        
        print("\n✅ 模型响应:")
        print("-" * 50)
        print(response['choices'][0]['message']['content'])
        print("-" * 50)
        
        # 显示使用统计
        if 'usage' in response:
            usage = response['usage']
            print(f"\n📊 使用统计:")
            print(f"  输入tokens: {usage.get('prompt_tokens', 0)}")
            print(f"  输出tokens: {usage.get('completion_tokens', 0)}")
            print(f"  总计tokens: {usage.get('total_tokens', 0)}")
            
    except Exception as e:
        print(f"❌ 调用模型时出错: {e}")
        print("\n💡 可能的解决方案:")
        print("1. 检查 DASHSCOPE_API_KEY 是否正确")
        print("2. 确认网络连接正常")
        print("3. 验证 API 密钥是否有效且有足够余额")
        print("4. 确认使用的模型名称是否正确")

if __name__ == "__main__":
    test_qwen()