#!/bin/bash
echo "=================================================="
echo "🚀 正在启动 RPG 英语冒险与商店系统 (v9.0)..."
echo "=================================================="

# 检查 Python 是否可用
if ! command -v python3 &> /dev/null
then
    echo "❌ 未检测到 Python3，请先安装 Python3！"
    exit 1
fi

# 检查是否安装了 Flask 依赖
if ! python3 -m pip show flask > /dev/null 2>&1; then
    echo "📦 未检测到 Flask，正在根据 requirements.txt 安装依赖..."
    python3 -m pip install -r requirements.txt
fi

echo "🌐 启动 Flask 开发服务器与多邻国三阶段特训系统..."

# 如果存在虚拟环境则优先激活
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 运行 Python 启动入口脚本 (run.py 会自动初始化数据库并拉起浏览器)
python3 run.py