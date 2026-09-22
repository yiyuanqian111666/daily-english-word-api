import webbrowser
from app import app, init_db

if __name__ == "__main__":
    # 确保在启动前初始化数据库
    init_db()

    url = "http://127.0.0.1:5000"
    print(f"🚀 API 已启动！请访问 {url} 查看首页状态～")
    webbrowser.open(url)

    # 启动 Flask 自带的开发服务器
    app.run(host="127.0.0.1", port=5000, debug=True)