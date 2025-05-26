@echo off
echo 🔧 启动 daily-english-word-api...
set FLASK_APP=start.py
set FLASK_ENV=development
flask run
pause
