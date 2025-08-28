from fastapi import FastAPI
from fastapi.responses import JSONResponse
import random

# ------------------------------
# 配置常量
# ------------------------------

APP_TITLE = "Daily English Word API"
APP_DESCRIPTION = "一个简单又有趣的英语单词学习 API 🚀"
APP_VERSION = "2.0.0"

WORDS = [
    "apple", "banana", "cat", "dog",
    "elephant", "future", "growth", "happiness"
]

MTL_DATA = {
    "project": "MTL Open Source",
    "description": "示例数据，可替换为真实 MTL 数据源",
    "version": "1.0"
}

# ------------------------------
# 初始化 FastAPI
# ------------------------------

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION
)

# ------------------------------
# 辅助函数
# ------------------------------

def get_random_word():
    """从单词库随机选择一个单词"""
    word = random.choice(WORDS)
    meaning = f"This is the meaning of '{word}' (示例翻译)"
    return {"word": word, "meaning": meaning}

# ------------------------------
# API 路由
# ------------------------------

@app.get("/", summary="首页信息")
def read_root():
    """返回首页信息及 API 文档链接"""
    return JSONResponse({
        "message": "欢迎来到 Daily English Word API 🎉",
        "docs": "访问 http://127.0.0.1:8000/docs 查看 API 文档",
        "endpoints": ["/word", "/mtl"]
    })

@app.get("/word", summary="随机单词")
def get_word():
    """返回一个随机单词及示例翻译"""
    return JSONResponse(get_random_word())

@app.get("/mtl", summary="MTL 数据")
def get_mtl_data():
    """返回示例 MTL 数据"""
    return JSONResponse(MTL_DATA)
