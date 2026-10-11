"""
======================================================================
项目名称：RPG 英语冒险与商店系统 (启动入口 run.py)
当前版本：v9.0 (多邻国三阶段阶梯学习与挑战版)
主要功能：
  1. 确保在服务启动前自动初始化 SQLite 数据库、海量分级词库与商店道具。
  2. 兼容 Flask Debug 模式下的重载机制，避免重复初始化或多次拉起浏览器。
  3. 自动唤起默认浏览器并打开沉浸式学习主页。
======================================================================
"""

import os
import webbrowser
from app import app, init_db

if __name__ == "__main__":
    # 确保在启动前初始化数据库（载入海量词库、长难句、冒险商店道具与 RPG 互动数据集）
    # WERKZEUG_RUN_MAIN 用于判断是否是 Flask debug 模式下的重载子进程，
    # 这样可以防止 debug 模式下初始化和打开浏览器执行两次。
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        init_db()
        url = "http://127.0.0.1:5000"
        print(f"🚀 Open-Source RPG English API (v9.0 多邻国三阶段渐进版) 已启动！请访问 {url} 查看沉浸式冒险首页～")
        webbrowser.open(url)

    # 启动 Flask 自带的开发服务器
    app.run(host="127.0.0.1", port=5000, debug=True)