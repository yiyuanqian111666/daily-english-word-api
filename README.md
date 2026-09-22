# 🌟 Daily English Word API

🎮 一个游戏化英语学习 API
学习 · 挑战 · 评级 · 排行榜 · 搜索 —— 全部开箱即用

---

## 🚀 为什么这个项目值得 Star？
- **🎯 不是普通背单词 API**：内置「挑战 + 评级 + 连胜 + 排行榜」完整游戏化机制。
- **🎮 天然适合**：Unity 游戏、英语学习 App、Web 前端/后端练手。
- **⚡ Clone 即用**：基于 Flask，轻量且健壮，支持零配置本地启动。
- **🔍 功能完备**：不仅能背单词，还支持场景对话、多维度分类、关键词模糊检索与分页。
- **📦 单文件结构清晰**：极易二次开发与扩展，符合 MTL 开源标准。

---

## ✨ 核心功能一览
### 📘 学习模式
- **✅ 单词学习**：支持按分类（Category）随机抽取单词及例句。
- **✅ 场景对话学习**：支持按场景（Scene）随机抽取地道日常对话。

### 🔍 单词检索
- **✅ 关键词搜索**：支持通过关键字对单词或释义进行模糊匹配（`/api/words/search`）。

### 🧠 挑战系统
- ⏱ 限时 20 秒完成挑战。
- ✍ 严格记录用时与准确度。

### 🏅 评级系统
`SS` · `S` · `A` · `B` · `C` · `D` · `E` · `F`
- 用时越短，评级越高。
- 挑战失败或超时直接评为 `F`，连胜清零。

### 🏆 挑战排行榜
- 全局及多维度排行榜。
- **支持分页查询**（`limit` / `offset`），数据再多也不崩溃。
- 智能多级排序（评级优选 > 用时最短 > 提交时间）。

---

## ⚡ 30 秒快速启动

```bash
git clone [https://github.com/yiyuanqian111666/daily-english-word-api.git](https://github.com/yiyuanqian111666/daily-english-word-api.git)
cd daily-english-word-api

# 安装依赖
pip install -r requirements.txt

# 启动服务 (会自动打开浏览器并初始化数据库)
python start.py

或者使用一键脚本：

Linux / macOS: ./run.sh

Windows: 双击 run.bat

打开浏览器访问：http://127.0.0.1:5000

🔥 API 使用示例
🎓 1. 获取学习内容
HTTP
GET /api/learn?mode=word&category=general
GET /api/learn?mode=dialog&scene=daily

{
  "mode": "word",
  "word": "serendipity",
  "meaning": "机缘巧合",
  "example": "Finding this app was pure serendipity.",
  "challenge_after": 3
}

🔍 2. 搜索单词
GET /api/words/search?q=apple

🧠 3. 提交挑战
HTTP
POST /api/challenge/submit
Content-Type: application/json

{
  "mode": "word",
  "content": "apple",
  "used_time": 4,
  "success": true,
  "streak": 2
}

返回示例：{
  "success": true,
  "grade": "S",
  "used_time": 4,
  "streak": 3
}

🏆 4. 查看排行榜（支持分页）
HTTP
GET /api/leaderboard?limit=10&offset=0

➕ 5. 添加新数据
HTTP
POST /api/add
Content-Type: application/json

{
  "word": "innovation",
  "meaning": "创新",
  "example": "Innovation drives the future.",
  "category": "tech"
}
🧱 技术栈
Python 3.8+

Flask 3.x（现代化 Web 框架，采用应用上下文与请求生命周期管理）

SQLite（内置轻量数据库，零外部服务依赖）

RESTful API 设计规范

🌱 未来规划
[ ] 用户名 / 昵称排行榜系统

[ ] 在线 Demo 演示

[ ] Unity 官方接入示例代码

[ ] 成就系统与连续打卡统计面板

⭐ 支持这个项目
如果这个项目对你有帮助或启发：

⭐ 给仓库点个 Star

🍴 Fork 进行二次开发

🐛 提交 Issue 或提建议

一个 Star 就是继续维护的最大动力 ❤️

📜 License
MIT License © 2026 yiyuanqian111666