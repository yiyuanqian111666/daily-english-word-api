@echo off
:: 设置编码为 UTF-8，防止中文输出乱码
chcp 65001 >nul

echo ========================================================
echo    🚀 正在准备启动 RPG English API (v7.0 冒险商店与赌徒模式终极版)...
echo ========================================================

:: 1. 检查 Python 环境
echo 正在检查 Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未检测到 python 命令，请确保已安装 Python 并将其加入环境变量。
    pause
    exit /b
)
echo ✅ Python 环境正常。

:: 2. 检查并激活虚拟环境（如果存在）
if exist venv (
    echo 📂 检测到虚拟环境 venv，正在激活...
    call venv\Scripts\activate.bat
) else if exist .venv (
    echo 📂 检测到虚拟环境 .venv，正在激活...
    call .venv\Scripts\activate.bat
)

:: 3. 安装依赖（包含 Flask-CORS 等最新扩展）
if exist requirements.txt (
    echo 📦 正在检查并安装依赖...
    python -m pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt
) else (
    echo ⚠️ 提示: 未找到 requirements.txt 文件，跳过依赖安装。
)

:: 4. 启动服务
echo 🌟 正在启动 API 服务、冒险商店系统与古典音乐引擎 (run.py)...
echo ========================================================
python run.py

pause