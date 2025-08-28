# 📘 Daily English Word API

> 一个轻量级、开箱即用的每日英文单词 API，适合英语学习者和 Python / FastAPI 初学者练习使用。

![MTL](https://img.shields.io/badge/MTL-Open%20Source-green?style=flat-square)
![License](https://img.shields.io/github/license/yiyuanqian111666/daily-english-word-api)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)

---

## 🌱 项目简介

**Daily English Word API** 是一个基于 **FastAPI** 的开源项目，每日提供一个英语单词及释义示例，便于学习者积累词汇，也适合开发者练习 Web API 开发。  

适用场景：

- 📚 英语初学者每日背词  
- 👨‍💻 Python / FastAPI 初学者练习 API 开发  
- 👩‍🏫 教师制作词汇教学工具  
- 🧪 前端工程师调试 JSON 接口  

✅ 本项目遵循 MIT 协议，符合 [MTL 开源标准](https://github.com/MTL-open-source)。

---

## 🚀 功能

- 📖 每日一个单词（带示例翻译）  
- 🌐 提供 RESTful API 接口  
- ⚡ 支持快速部署（Windows / Linux / Mac）  
- 📄 自动生成 API 文档（访问 `/docs`）  

---

## 🛠️ 安装与运行

### 1️⃣ 克隆项目

```bash
git clone https://github.com/yiyuanqian111666/daily-english-word-api.git
cd daily-english-word-api
2️⃣ 安装依赖
bash
复制代码
pip install -r requirements.txt
3️⃣ 启动服务
你有三种方式启动服务：

方法 1：直接运行 Python

bash
复制代码
python start.py
方法 2：Windows（推荐）

双击 run.bat，或者在命令行执行：

bash
复制代码
run.bat
方法 3：Linux / Mac

先赋予脚本执行权限（只需一次）：

bash
复制代码
chmod +x run.sh
然后运行：

bash
复制代码
./run.sh
🌐 使用 API
启动成功后，在浏览器访问：

arduino
复制代码
http://127.0.0.1:8000/docs
即可查看自动生成的 API 文档，并测试接口 /word 和 /mtl。

接口示例 /word 返回 JSON：

json
复制代码
{
  "word": "apple",
  "meaning": "This is the meaning of 'apple' (示例翻译)"
}
接口示例 /mtl 返回 JSON：

json
复制代码
{
  "project": "MTL Open Source",
  "description": "示例数据，可替换为真实 MTL 数据源",
  "version": "1.0"
}
🎯 项目亮点
✅ 简单易用：下载项目即可运行

🌎 跨平台：支持 Windows、Linux、Mac

📚 教育友好：适合初学者快速学习 API 和 FastAPI

📜 License
MIT License

yaml
复制代码
