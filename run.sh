#!/bin/bash

echo "=================================================="
echo "🚀 正在启动 RPG 英语冒险与商店系统 (v10.0 模块化进阶版)..."
echo "=================================================="

# 1. 检查 Python3 是否可用
if ! command -v python3 &> /dev/null
then
    echo "❌ 未检测到 Python3，请先安装 Python3 并加入环境变量！"
    exit 1
fi

# 2. 如果存在虚拟环境则优先激活
if [ -d "venv" ]; then
    echo "📂 检测到虚拟环境 venv，正在激活..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "📂 检测到虚拟环境 .venv，正在激活..."
    source .venv/bin/activate
fi

# 3. 检查并安装 requirements.txt 依赖
if [ -f "requirements.txt" ]; then
    if ! python3 -m pip show flask > /dev/null 2>&1; then
        echo "📦 未检测到核心依赖，正在根据 requirements.txt 安装..."
        python3 -m pip install --upgrade pip
        python3 -m pip install -r requirements.txt
    fi
else
    echo "⚠️ 提示: 未找到 requirements.txt 文件，跳过依赖安装。"
fi

echo "🌐 启动 Flask 开发服务器、多邻国三阶段特训系统与冒险商店 (run.py)..."
echo "=================================================="

# 4. 运行 Python 启动入口脚本 (run.py 会自动初始化数据库并拉起浏览器)
python3 run.py