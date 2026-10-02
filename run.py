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
        print(f"🚀 Open-Source RPG English API (v7.0 Shop & Gambler Edition) 已成功启动！请访问 {url} 查看沉浸式冒险首页～")
        webbrowser.open(url)

    # 启动 Flask 自带的开发服务器
    app.run(host="127.0.0.1", port=5000, debug=True)