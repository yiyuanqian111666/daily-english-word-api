@echo off
echo 🔧 启动 daily-english-word-api...

REM 检查是否已激活虚拟环境（可选，根据你实际情况）
if not defined VIRTUAL_ENV (
    echo ⚠️ 你还没有激活 Python 虚拟环境，请先激活环境！
    pause
    exit /b
)

REM 设置 Flask 启动文件和环境
set FLASK_APP=start.py
set FLASK_ENV=development

echo 🚀 运行 Flask 开发服务器...
flask run

echo 服务器已停止，按任意键退出。
pause
