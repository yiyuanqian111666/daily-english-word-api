"""
======================================================================
项目名称：RPG 英语冒险与商店系统 (启动入口 run.py)
当前版本：v10.0 (模块化架构与多邻国三阶段阶梯学习版)
主要功能：
  1. 在服务启动前自动初始化 SQLite 数据库、多维度词库与商店道具。
  2. 兼容 Flask Debug 模式下的重载机制，避免重复初始化或多次拉起浏览器。
  3. 优雅地唤起默认浏览器并打开沉浸式学习主页。
======================================================================
"""

import os
import webbrowser
from typing import Optional
from app import app, init_db


def main() -> None:
    """主启动函数：管理数据库初始化、控制台日志与浏览器拉起"""
    host = "127.0.0.1"
    port = 5000
    url = f"http://{host}:{port}"

    # WERKZEUG_RUN_MAIN 用于判断是否是 Flask debug 模式下的重载子进程，
    # 这样可以防止 debug 模式下初始化数据库和打开浏览器执行两次。
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        init_db()
        print("==================================================")
        print("🚀 RPG 英语冒险系统 (v10.0 模块化进阶版) 已成功启动！")
        print(f"🌐 访问地址: {url}")
        print("💡 特性：认读 -> 拼写 -> 极限默写，多难度关卡与冒险商店全线开启！")
        print("==================================================")
        
        # 自动唤起默认浏览器
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"⚠️ 自动打开浏览器失败: {e}")

    # 启动 Flask 自带的开发服务器
    app.run(host=host, port=port, debug=True)


if __name__ == "__main__":
    main()