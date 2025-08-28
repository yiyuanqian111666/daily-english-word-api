@echo off
echo 正在检查 Python...
python --version || (echo 请先安装 Python & pause & exit /b)

echo 安装依赖...
pip install -r requirements.txt

echo 启动 API 服务...
python start.py
pause
