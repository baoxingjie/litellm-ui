# LiteLLM 多模型调用项目

这个项目演示了如何使用 LiteLLM 库来调用不同的 AI 模型（OpenAI 和 Anthropic）。

## 功能特性

- 🤖 **多模型支持**：支持 5 种主流 AI 模型
  - OpenAI GPT-4o
  - Anthropic Claude 3 Sonnet
  - Azure OpenAI GPT-4o
  - 阿里云 DashScope Qwen3
  - 百川 AI Baichuan4-turbo
- 🌐 **现代化 Web UI**：美观的聊天界面，支持实时对话
- 🔄 **模型切换**：可在界面中随时切换不同的 AI 模型
- 💬 **交互式聊天**：支持多轮对话，类似 ChatGPT 体验
- 📱 **响应式设计**：支持桌面和移动设备
- 🛠️ **命令行版本**：同时提供命令行批量测试功能
- 🔧 **统一接口**：通过 LiteLLM 统一调用不同模型
- 🔐 **环境变量管理**：安全的 API 密钥管理

## 环境设置

### 1. 创建并激活虚拟环境

项目已包含虚拟环境，可以直接激活：

```bash
# 激活虚拟环境（推荐使用提供的脚本）
./activate_venv.sh

# 或者手动激活
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 退出虚拟环境

```bash
deactivate
```

## 配置

1. 复制环境变量模板文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入您的实际 API 密钥：
```
OPENAI_API_KEY=your-actual-openai-key
ANTHROPIC_API_KEY=your-actual-anthropic-key
AZURE_API_KEY=your-actual-azure-api-key
AZURE_API_BASE=https://your-resource-name.openai.azure.com/
AZURE_API_VERSION=2024-08-01-preview
DASHSCOPE_API_KEY=your-actual-dashscope-api-key
BAICHUAN_API_KEY=your-actual-baichuan-api-key
BAICHUAN_BASE_URL=https://api.baichuan-ai.com/v1/
```

## 使用方法

### 🌐 Web UI 版本（推荐）

1. **启动 Web 服务器**：
   ```bash
   python app.py
   ```

2. **访问聊天界面**：
   打开浏览器访问 http://localhost:5000

3. **功能特性**：
   - 🎨 现代化聊天界面，支持数学公式渲染（MathJax）
   - 🔄 实时模型切换
   - 📱 响应式设计，支持移动设备
   - 💬 多轮对话支持
   - ⚡ 实时错误处理和状态反馈

### 🖥️ 命令行版本

**批量测试所有模型**：
```bash
python main.py
```

**专业模型测试工具**：
```bash
python test_models.py
```

### 🔧 高级配置

**自定义服务器配置**：
```bash
# 设置端口和主机
export PORT=8080
export HOST=0.0.0.0
export DEBUG=true

# 设置模型参数
export MAX_TOKENS=2000
export TEMPERATURE=0.8

python app.py
```

## 项目结构

```
litellm-ui/
├── main.py              # 命令行版本主程序
├── app.py               # Flask Web 应用
├── config.py            # 配置管理模块
├── logger.py            # 日志管理模块
├── utils.py             # 工具函数模块
├── test_models.py       # 模型测试工具
├── templates/           # HTML 模板目录
│   └── index.html      # 聊天界面模板（支持数学公式）
├── logs/               # 日志文件目录（自动创建）
├── requirements.txt     # 依赖包列表
├── .env.example        # 环境变量模板
├── .env               # 环境变量配置（需要自己创建）
├── activate_venv.sh    # 虚拟环境激活脚本
├── venv/              # Python 虚拟环境目录
├── .gitignore         # Git 忽略文件
└── README.md          # 项目说明
```

## 🚀 代码质量特性

### 📊 架构设计
- **模块化设计**：配置、日志、工具函数分离
- **统一配置管理**：集中管理所有模型配置
- **错误处理**：完善的异常捕获和用户友好的错误提示
- **日志系统**：详细的操作日志和 API 调用记录

### 🛡️ 安全性
- **API 密钥保护**：环境变量管理，避免硬编码
- **错误信息清理**：自动移除日志中的敏感信息
- **输入验证**：API 密钥格式验证

### ⚡ 性能优化
- **重试机制**：自动重试失败的 API 调用
- **响应时间监控**：记录每次调用的耗时
- **成本估算**：实时计算 API 调用成本
- **异步处理**：Web UI 支持并发请求

### 🧪 测试与监控
- **专业测试工具**：`test_models.py` 批量测试所有模型
- **健康检查**：自动检测模型可用性
- **详细报告**：测试结果、响应时间、成本分析

### 📝 代码质量
- **类型提示**：完整的 Python 类型注解
- **文档字符串**：详细的函数和类说明
- **代码规范**：遵循 PEP 8 标准
- **错误处理**：优雅的异常处理机制

## 注意事项

- 请确保您有有效的 OpenAI、Anthropic、Azure OpenAI、阿里云 DashScope 和百川 AI API 密钥
- 对于 Azure OpenAI，需要先在 Azure 门户中创建 OpenAI 资源并部署模型
- 对于阿里云 DashScope，需要在阿里云控制台开通 DashScope 服务并获取 API 密钥
- 对于百川 AI，需要在百川智能官网注册账号并获取 API 密钥
- API 调用可能会产生费用，请注意使用量
- 不要将真实的 API 密钥提交到版本控制系统中
- Azure OpenAI 的 API Base URL 格式为：`https://your-resource-name.openai.azure.com/`
- 阿里云 DashScope 支持多种模型，如 qwen-turbo、qwen-plus、qwen-max 等
- 百川 AI 支持多种模型，如 Baichuan4-turbo、Baichuan3-turbo 等
- 建议定期运行 `test_models.py` 检查模型状态
- 查看 `logs/app.log` 了解详细的运行日志