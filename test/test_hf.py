import os
from myllm import MyLLM
from config import Config

# 设置 Hugging Face Token (从环境变量获取)
if not os.getenv("HF_TOKEN"):
    print("错误：请设置 HF_TOKEN 环境变量")
    print("请在 .env 文件中添加: HF_TOKEN=your_huggingface_token")
    exit(1)

# 初始化 MyLLM 实例
llm = MyLLM()

# 获取 Hugging Face 模型配置
model_config = Config.get_model_by_name("DeepSeek-R1")
if not model_config:
    print("错误：未找到 DeepSeek-R1 模型配置")
    exit(1)

# 测试消息
messages = [
    {
        "role": "user",
        "content": "How many r's are in the word 'strawberry'?",
    }
]

try:
    # 使用 MyLLM 进行模型调用
    response = llm.completion(
        model_key=model_config.name,
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )
    
    print("=== 模型响应 ===")
    print(f"模型: {model_config.display_name}")
    print(f"响应: {response}")
    
except Exception as e:
    print(f"错误: {e}")