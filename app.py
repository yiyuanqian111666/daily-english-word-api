from fastapi import FastAPI
import random
import webbrowser
import uvicorn

app = FastAPI(
    title="Daily English Word API",
    description="一个简单又有趣的英语单词学习 API 🚀",
    version="2.0.0"
)

# 模拟单词库
WORDS = ["apple", "banana", "cat", "dog", "elephant", "future", "growth", "happiness"]

# 模拟 MTL 开源数据
MTL_DATA = {
    "project": "MTL Open Source",
    "description": "这是一个示例数据，未来可以替换成真实的 MTL 数据源。",
    "version": "1.0"
}


@app.get("/")
def read_root():
    return {
        "message": "欢迎来到 Daily English Word API 🎉",
        "docs": "访问 http://127.0.0.1:8000/docs 查看 API 文档",
        "endpoints": ["/word", "/mtl"]
    }


@app.get("/word")
def get_word():
    word = random.choice(WORDS)
    return {
        "word": word,
        "meaning": f"This is the meaning of '{word}' (示例翻译)"
    }


@app.get("/mtl")
def get_mtl_data():
    return MTL_DATA


if __name__ == "__main__":
    url = "http://127.0.0.1:8000/docs"
    print(f"✅ API 已启动！打开 {url} 试试吧～")
    # 自动打开浏览器
    webbrowser.open(url)
    uvicorn.run(app, host="127.0.0.1", port=8000)
