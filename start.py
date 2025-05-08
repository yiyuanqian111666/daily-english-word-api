import os
from app import app  # 假设你在 app.py 中定义了一个 Flask app 对象

if __name__ == "__main__":
    # 设置环境变量
    os.environ["FLASK_APP"] = "app.py"
    os.environ["FLASK_ENV"] = "development"  # 开发环境

    # 启动 Flask 应用
    app.run(debug=True, host="0.0.0.0", port=5000)
