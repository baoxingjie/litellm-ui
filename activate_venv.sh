#!/bin/bash
# 激活虚拟环境的脚本

echo "正在激活虚拟环境..."
source venv/bin/activate
echo "虚拟环境已激活！"
echo "当前 Python 路径: $(which python)"
echo "当前 pip 路径: $(which pip)"
echo ""
echo "要退出虚拟环境，请输入: deactivate"
echo "要安装项目依赖，请运行: pip install -r requirements.txt"