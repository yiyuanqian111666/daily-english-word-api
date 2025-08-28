#!/bin/bash
echo "🔧 启动 Daily-English-Word-API..."

# 检查 Python 是否可用
if ! command -v python3 &> /dev/null
then
    echo "❌ 未检测到 Python3，请先安装 Python3！"
    exit 1
fi

# 检查是否安装了依赖
if ! python3 -m pip show fastapi > /dev/null 2>&1; then
    echo "📦 未检测到 FastAPI，正在安装依赖..."
    python3 -m pip install -r requirements.txt
fi

echo "🚀 启动 FastAPI 开发服务器..."
python3 app.py &

# 给服务器一点时间启动
sleep 2

# 自动打开浏览器 (Mac: open, Linux: xdg-open)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://127.0.0.1:8000/docs"
else
    xdg-open "http://127.0.0.1:8000/docs"
fi

# 保持前台运行
wait
