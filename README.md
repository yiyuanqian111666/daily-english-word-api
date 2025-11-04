📘 Daily English Word API

一个 零配置、即开即用、可扩展 的英文词汇学习 API
让任何人都能一键获取每日英语单词，适合学习、教学、项目练习或前端调用。






✨ 项目亮点
特性	描述
🚀 零配置即可运行	无需数据库安装、无 Token、clone 即可启动
📅 每日一词	自动根据日期切换每日单词
🎲 随机模式	支持随机单词获取
➕ 可扩展词库	支持 API 方式添加新单词
📚 教学友好	适合作为 Python Flask 入门实战项目
✅ 支持 MTL 开源要求	已符合 MTL 项目结构标准
🚀 快速开始（只需复制即可运行）
1️⃣ 克隆项目并安装依赖
git clone https://github.com/yiyuanqian111666/daily-english-word-api.git
cd daily-english-word-api
pip install flask

2️⃣ 一键启动（Windows）

在项目根目录双击运行：
run.bat

或在终端执行：

run.bat

3️⃣ 一键启动（Mac / Linux）

首次先赋予执行权限：

chmod +x run.sh
./run.sh


运行成功后访问：
http://127.0.0.1:5000

🧠 可用 API 接口
路由	方法	说明
/	GET	查看 API 状态与接口说明
/api/today	GET	获取今日英文单词
/api/random	GET	获取随机英文单词
/api/add	POST	添加新单词（需 JSON body）
/api/list	GET	查看所有单词列表
📍 示例：添加单词（POST）

URL:

POST /api/add


Body（JSON）：

{
  "word": "brilliant",
  "meaning": "very impressive or successful",
  "example": "She had a brilliant idea."
}


返回示例：

{
  "message": "✅ Word added successfully!",
  "word": "brilliant"
}

🧪 浏览器快速测试（无需代码）
操作	浏览器访问
今日单词	http://127.0.0.1:5000/api/today

随机单词	http://127.0.0.1:5000/api/random

查看所有词汇	http://127.0.0.1:5000/api/list
📌 项目结构
📦 daily-english-word-api
├─ app.py                # 主程序（已集成功能）
├─ run.bat               # Windows 一键启动
├─ run.sh                # Mac/Linux 一键启动
├─ README.md             # 项目说明
└─ words.db              # 单词数据库（启动后自动生成）

🤝 支持 & 开源说明

本项目遵循 MIT License
你可以自由使用、修改、分发，支持商用。

欢迎 Fork、Star ⭐、提交 PR 改进。