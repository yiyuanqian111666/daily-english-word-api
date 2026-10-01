🌟 Daily English Word & Idiom API

🎮 一个开源级游戏化地道美语、俚语与语法学习后端 API
500+ 海量词库 · 四重难度关卡 · 挑战 · 评级 · 排行榜 —— 全部开箱即用

🚀 为什么这个项目值得 Star？

🎯 极致地道的美语学习：内置 500+ 条覆盖生活、职场、美剧俚语与高级长难句语法的高质量词库。

🎮 游戏化核心机制：集成了「多难度关卡 + 限时打字默写挑战 + 评级 + 连胜机制 + 排行榜」。

⚡ Clone 即用：基于 Flask，轻量且健壮，支持零配置本地启动、自动数据库初始化与浏览器唤起。

🔍 功能完备：支持按难度与分类多维获取学习内容、语法解析、关键词模糊检索与高效分页排行榜。

📦 单文件与规范结构：极易二次开发与扩展，完全符合 MTL 开源标准。

✨ 核心功能一览

📘 学习与关卡模式

✅ 多难度关卡（Easy 至 Hell）：

🟢 Easy (简单)：基础高频生活词汇与单句。

🟡 Normal (正常)：美国人日常高频短语。

🔴 Hard (困难)：地道美式俚语与社交黑话。

💀 Hell (地狱)：高阶习语、美剧连读与复杂语法长难句。

✅ 语法解析：提供详尽的语法和场景注释（grammar_note）。

🧠 挑战系统

⏱ 限时 20 秒完成拼写挑战。

✍ 严格记录用时、准确度与连续打卡（Streak）。

🏅 评级系统

SS · S · A · B · C · D · E · F

用时越短，评级越高。

挑战失败或超时直接评为 F，连胜清零。

🏆 挑战排行榜

支持按难度筛选的高效排行榜。

支持分页查询（limit / offset），数据再多也不崩溃。

智能多级排序（评级优选 > 用时最短 > 提交时间）。

⚡ 30 秒快速启动

git clone https://github.com/yiyuanqian111666/daily-english-word-api.git
cd daily-english-word-api

# 安装依赖
pip install -r requirements.txt

# 启动服务 (会自动初始化海量词库、打开浏览器并进入 Debug 模式)
python run.py


打开浏览器访问：http://127.0.0.1:5000

🔥 API 使用示例

🎓 1. 获取学习内容（支持难度筛选）

HTTP GET

/api/learn?difficulty=hard&category=slang


JSON 响应示例：

{
  "id": 105,
  "word": "spill the tea",
  "meaning": "八卦/吐露实情",
  "example": "Come on, spill the tea! What happened at the party last night?",
  "level": 3,
  "difficulty": "hard",
  "category": "slang",
  "grammar_note": "现代美式流行俚语：爆料、八卦。",
  "challenge_after": 3
}


🧠 2. 提交挑战

HTTP POST /api/challenge/submit

Content-Type: application/json

JSON 请求体：

{
  "difficulty": "normal",
  "content": "hang out",
  "used_time": 4,
  "success": true,
  "streak": 2
}


返回响应：

{
  "success": true,
  "grade": "S",
  "used_time": 4,
  "streak": 3
}


🏆 3. 查看排行榜（支持分页）

HTTP GET /api/leaderboard?limit=10&offset=0

🧱 技术栈

Python 3.8+

Flask 3.x（现代化 Web 框架，采用应用上下文与请求生命周期管理）

SQLite（内置轻量数据库，零外部服务依赖）

RESTful API 设计规范与完整单元测试覆盖

🌱 未来规划

[ ] 用户名 / 昵称排行榜系统

[ ] 网页端炫酷 RPG 闯关 UI 界面

[ ] Unity 官方接入示例代码

[ ] 成就系统与连续打卡统计面板

⭐ 支持这个项目

如果这个项目对你有帮助或启发：

⭐ 给仓库点个 Star

🍴 Fork 进行二次开发

🐛 提交 Issue 或提出建议

一个 Star 就是持续维护的最大动力 ❤️️

📜 License

MIT License © 2026 yiyuanqian111666