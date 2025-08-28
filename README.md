# 📘 Daily English Word API

> 一个轻量级、开箱即用的每日英文单词 API，适合英语学习者和 Python / Flask 初学者练习使用。

![MTL](https://img.shields.io/badge/MTL-Open%20Source-green?style=flat-square)
![License](https://img.shields.io/github/license/yiyuanqian111666/daily-english-word-api)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)

---

## 🌱 项目简介

**Daily English Word API** 是一个基于 Flask 的开源项目，旨在每日提供一个英语单词及解释、语音等信息，便于学习者积累词汇，也适合开发者作为练习用 API 项目。

适用场景：

- 📚 英语初学者每日背词
- 👨‍💻 Python / Flask 初学者练习 Web API 开发
- 👩‍🏫 教师制作词汇教学工具
- 🧪 前端工程师调试 JSON 接口数据

✅ 本项目遵循 MIT 协议，符合 [MTL 开源标准](https://github.com/MTL-open-source)，并附带 `mtl.json` 元数据文件，长期维护中。

---

## 🚀 快速启动（本地运行）

> ✅ 无需数据库、无需密钥，Clone 后即可运行！

```bash
git clone https://github.com/yiyuanqian111666/daily-english-word-api.git
cd daily-english-word-api
pip install flask
python start.py

# 📘 Daily English Word API

一个简单有趣的英语单词 API 项目，基于 Flask 构建。  
它可以每天返回一个新的英语单词，帮助你更轻松地学习英语。  

---

## 🚀 功能
- 📖 每日一个单词（带释义和例句）
- 🌐 提供 RESTful API 接口
- ⚡ 支持快速部署（Windows / Linux / Mac）

---

## 🛠️ 安装

1. 克隆项目：
   ```bash
   git clone https://github.com/yiyuanqian111666/daily-english-word-api.git
   cd daily-english-word-api

▶️ 启动方法

你有三种方式启动服务：

方法 1：直接运行 Python
python app.py

方法 2：Windows（推荐）

双击运行 run.bat 文件，或者在命令行执行：

run.bat

方法 3：Linux / Mac

先给脚本赋予执行权限（只需执行一次）：

chmod +x run.sh


然后运行：

./run.sh

🌐 使用 API

启动成功后，你可以在浏览器访问：

http://127.0.0.1:5000/api/word


它会返回一个 JSON，例如：

{
  "word": "serendipity",
  "definition": "the occurrence of events by chance in a happy or beneficial way",
  "example": "Meeting her was pure serendipity."
}

🎯 项目亮点

简单易用：复制项目即可直接运行

跨平台：同时支持 Windows 和 Linux/Mac

教育友好：适合初学者、学生快速学习 API 和 Python

📜 License

MIT License