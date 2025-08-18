@echo off
echo 🔧 启动 Daily-English-Word-API...

REM 检查 Python 是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Python，请先安装 Python 并配置环境变量！
    pause
    exit /b
)

REM 检查是否安装了依赖
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 📦 未检测到 FastAPI，正在安装依赖...
    pip install -r requirements.txt
)

echo 🚀 启动 FastAPI 开发服务器...
start http://127.0.0.1:8000/docs
python app.py

echo 服务器已停止，按任意键退出。
pause
