#!/bin/bash
echo "检查 Python..."
python3 --version || { echo "请先安装 Python"; exit 1; }

echo "安装依赖..."
pip3 install -r requirements.txt

echo "启动服务..."
python3 start.py
