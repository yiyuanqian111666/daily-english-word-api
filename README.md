# 🌟 Daily English Word & Idiom API
🎮 一个开源级游戏化地道美语、俚语、长句与语法学习后端 API
500+ 海量词库 · 四重难度关卡 · 跨域前后端分离 · AI 互动评语 · RPG 成长体系 · 排行榜 —— 全部开箱即用

---

## 🚀 为什么这个项目值得 Star？
- **🎯 极致地道的美语与长句学习**：内置 500+ 条覆盖生活、职场、美剧俚语与高级真实长难句的高质量词库。
- **🎮 游戏化与 RPG 核心机制**：集成了「多难度关卡 + 限时打字挑战 + AI 趣味评语 + XP 经验值与动态称号升级 + 连胜机制 + 排行榜」。
- **🌐 现代化跨域前后端分离**：内置 Flask-CORS 跨域支持，无缝对接各类前端静态页面与可视化闯关客户端。
- **⚡ Clone 即用**：基于 Flask，轻量且健壮，支持零配置本地启动、自动数据库初始化与浏览器自动唤起。
- **🔍 功能完备**：支持按难度与分类多维获取学习内容、语法解析、关键词模糊检索与高效分页排行榜。

---

## ✨ 核心功能一览

### 📘 学习与关卡模式
- **四重游戏化难度关卡（Easy 至 Hell）**：
  - 🟢 **Easy (简单)**：基础高频生活词汇与单句。
  - 🟡 **Normal (正常)**：美国人日常高频短语。
  - 🔴 **Hard (困难)**：地道美式俚语与社交黑话。
  - 💀 **Hell (地狱)**：高阶习语、美剧连读与复杂语法长难句。
- **语法解析**：提供详尽的语法和场景注释 (`grammar_note`)。
- **RPG 个人状态追踪**：每次获取学习内容时同步返回当前的经验值（XP）与动态称号。

### 🧠 挑战与 AI 互动评语系统
- ⏱ 限时 20 秒完成拼写或打字挑战。
- ✍ 严格记录用时、准确度与连续打卡 (`Streak`)。
- 🤖 **AI 互动评语 (`interactive_comment`)**：根据通关表现智能生成趣味鼓励或吐槽。
- 📈 **XP 经验值晋升**：通关成功即可累积经验，自动解锁更高阶的语言家称号（如“初学冒险者” -> “语言学徒” -> “地道美语精锐” -> “英语大宗师”）。

### 🏅 评级与排行榜系统
- **评级体系**：`SS · S · A · B · C · D · E · F`（用时越短，评级越高；超时或失败直接评为 F，连胜清零）。
- **高效排行榜**：
  - 支持按难度筛选。
  - 支持分页查询（`limit` / `offset`），数据再多也不崩溃。
  - 智能多级排序（评级优选 > 用时最短 > 提交时间）。

---

## ⚡ 30 秒快速启动

### 1. 启动后端 API
```bash
git clone [https://github.com/yiyuanqian111666/daily-english-word-api.git](https://github.com/yiyuanqian111666/daily-english-word-api.git)
cd daily-english-word-api

# 安装依赖（包含 Flask-CORS 等最新扩展）
pip install -r requirements.txt

# 启动服务 (会自动初始化海量词库、打开浏览器并进入 Debug 模式)
python run.py
(或者在 Windows 下直接双击运行 run.bat，Linux/macOS 下运行 ./run.sh)

2. 打开前端可视化页面
直接双击打开项目中的 index.html 即可开始沉浸式闯关背单词，前端会自动与运行在 http://127.0.0.1:5000 的后端 API 进行通信！

🔥 API 使用示例
🎓 1. 获取学习内容（支持难度筛选）
HTTP GET: /api/learn?difficulty=hard&category=slang

JSON 响应示例：

JSON
{
  "id": 105,
  "word": "spill the tea",
  "meaning": "八卦/吐露实情",
  "example": "Come on, spill the tea! What happened at the party last night?",
  "level": 3,
  "difficulty": "hard",
  "category": "slang",
  "grammar_note": "现代美式流行俚语：爆料、八卦。",
  "challenge_after": 3,
  "user_status": {
    "xp": 120,
    "total_solved": 12,
    "title": "语言学徒"
  }
}
🧠 2. 提交挑战
HTTP POST: /api/challenge/submit

Content-Type: application/json

JSON 请求体：

JSON
{
  "difficulty": "normal",
  "content": "hang out",
  "used_time": 4,
  "success": true,
  "streak": 2
}
返回响应：

JSON
{
  "success": true,
  "grade": "S",
  "used_time": 4,
  "streak": 3,
  "interactive_comment": "干得漂亮！S 级通关，你的手速和记忆力简直无可挑剔！🔥",
  "earned_xp": 25,
  "user_profile": {
    "xp": 145,
    "total_solved": 13,
    "title": "语言学徒"
  }
}
🏆 3. 查看排行榜（支持分页）
HTTP GET: /api/leaderboard?limit=10&offset=0

🧱 技术栈
Python 3.8+

Flask 3.x（现代化 Web 框架，采用应用上下文与请求生命周期管理）

Flask-CORS（处理跨域请求，完美支撑前后端分离架构）

SQLite（内置轻量数据库，零外部服务依赖）

RESTful API 设计规范与完整 unittest 单元测试覆盖

🌱 未来规划
[ ] 用户名 / 昵称排行榜系统

[ ] 网页端炫酷 RPG 闯关 UI 皮肤自由切换

[ ] 成就系统与连续打卡统计面板

⭐ 支持这个项目
如果这个项目对你有帮助或启发：

⭐ 给仓库点个 Star

🍴 Fork 进行二次开发

🐛 提 Issue 或提出建议

一个 Star 就是持续维护的最大动力 ❤

📜 License
MIT License © 2026 yiyuanqian111666