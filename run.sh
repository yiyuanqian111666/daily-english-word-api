#!/bin/bash

遇到错误立即退出

set -e

echo "="
echo " 🚀 正在准备启动 Daily English Word & Idiom API..."
echo "="

1. 检查 Python3 环境

if ! command -v python3 &> /dev/null; then
echo "❌ 错误: 未检测到 python3，请先安装 Python。"
exit 1
fi
echo "✅ 检测到 Python: $(python3 --version)"

2. 检查并创建/激活虚拟环境（可选推荐）

if [ -d "venv" ]; then
echo "📂 检测到虚拟环境 venv，正在激活..."
source venv/bin/activate
elif [ -d ".venv" ]; then
echo "📂 检测到虚拟环境 .venv，正在激活..."
source .venv/bin/activate
fi

3. 安装/更新依赖

if [ -f "requirements.txt" ]; then
echo "📦 正在检查并安装项目依赖..."
pip install -r requirements.txt
else
echo "⚠ 提示: 未找到 requirements.txt，跳过依赖安装。"
fi

4. 启动服务

echo "🌟 正在启动服务 (run.py)..."
python3 run.py