import os
import webbrowser
from app import app, init_db

if __name__ == "__main__":
    # 确保在启动前初始化数据库（载入 500+ 海量词库与多难度关卡）
    # WERKZEUG_RUN_MAIN 用于判断是否是 Flask debug 模式下的重载子进程，
    # 这样可以防止 debug 模式下初始化和打开浏览器执行两次。
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        init_db()
        url = "http://127.0.0.1:5000"
        print(f"🚀 Open-Source RPG English API 已启动！请访问 {url} 查看首页状态～")
        webbrowser.open(url)

    # 启动 Flask 自带的开发服务器
    app.run(host="127.0.0.1", port=5000, debug=True)