from litellm import completion
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 检查必要的环境变量是否已设置
required_env_vars = {
    "AZURE_API_KEY": "Azure OpenAI API 密钥",
    "AZURE_API_BASE": "Azure OpenAI API 基础URL", 
    "AZURE_API_VERSION": "Azure OpenAI API 版本",
    "DASHSCOPE_API_KEY": "阿里云 DashScope API 密钥",
    "BAICHUAN_API_KEY": "百川 AI API 密钥",
    "BAICHUAN_BASE_URL": "百川 AI API 基础URL"
}

print("检查环境变量配置...")
for env_var, description in required_env_vars.items():
    if not os.getenv(env_var):
        print(f"⚠️  警告: 缺少 {env_var} ({description})")
    else:
        print(f"✅ {env_var}: 已配置")

messages = [{"content": "介绍你自己", "role": "user"}]

print("正在调用 OpenAI GPT-4o...")
# openai call
try:
    response = completion(model="gpt-4o", messages=messages)
    print("OpenAI 响应:")
    print(response)
except Exception as e:
    print(f"OpenAI 调用失败: {e}")
print("\n" + "="*50 + "\n")

print("正在调用 Anthropic Claude Sonnet...")
# anthropic call
try:
    response = completion(model="claude-3-sonnet-20240229", messages=messages)
    print("Anthropic 响应:")
    print(response)
except Exception as e:
    print(f"Anthropic 调用失败: {e}")
print("\n" + "="*50 + "\n")

print("正在调用 Azure OpenAI GPT-4o...")
# azure openai call
try:
    response = completion(
        model="azure/gpt-4o",
        messages=messages,
        api_key=os.getenv("AZURE_API_KEY"),
        api_base=os.getenv("AZURE_API_BASE"),
        api_version=os.getenv("AZURE_API_VERSION"),
        temperature=0
    )
    print("Azure OpenAI 响应:")
    print(response)
except Exception as e:
    print(f"Azure OpenAI 调用失败: {e}")
print("\n" + "="*50 + "\n")

print("正在调用阿里云 DashScope Qwen3...")
# dashscope call
try:
    response = completion(
        model="openai/qwen2.5-72b-instruct",
        messages=messages,
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    print("阿里云 DashScope 响应:")
    print(response)
except Exception as e:
    print(f"DashScope 调用失败: {e}")
print("\n" + "="*50 + "\n")

print("正在调用百川 AI Baichuan4-turbo...")
# baichuan call
try:
    response = completion(
        model="openai/Baichuan4-turbo",
        messages=messages,
        api_key=os.getenv("BAICHUAN_API_KEY"),
        base_url=os.getenv("BAICHUAN_BASE_URL")
    )
    print("百川 AI 响应:")
    print(response)
except Exception as e:
    print(f"百川 AI 调用失败: {e}")