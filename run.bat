@echo off
:: 设置编码为 UTF-8，防止中文输出乱码
chcp 65001 >nul

echo =====================================
echo  🚀 正在准备启动 Daily English Word API...
echo =====================================

:: 1. 检查 Python 环境
echo 正在检查 Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未检测到 python 命令，请确保已安装 Python 并将其加入环境变量。
    pause
    exit /b
)
echo ✅ Python 环境正常。

:: 2. 安装依赖
if exist requirements.txt (
    echo 📦 正在检查并安装依赖...
    pip install -r requirements.txt
) else (
    echo ⚠️ 提示: 未找到 requirements.txt 文件，跳过依赖安装。
)

:: 3. 启动服务
echo 🌟 正在启动 API 服务 (start.py)...
echo =====================================
python start.py

pause