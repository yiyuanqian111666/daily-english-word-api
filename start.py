import uvicorn
from app import app
import webbrowser

if __name__ == "__main__":
    url = "http://127.0.0.1:8000/docs"
    print(f"✅ API 已启动！打开 {url} 查看文档～")
    webbrowser.open(url)
    uvicorn.run(app, host="127.0.0.1", port=8000)
