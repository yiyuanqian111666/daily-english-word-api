# 🌟 RPG English & Shop API (v10.0 多邻国三阶段模块化进阶版)

🎮 一个开源级游戏化地道美语、俚语、长句与商店经济系统的后端 API  
海量分级词库 · 多邻国三阶段渐进特训 · 跨域前后端分离 · 冒险商店与背包管理 · RPG 称号晋升 —— 全部开箱即用

---

## 🚀 为什么这个项目值得 Star？
- **🎯 极致地道的美语与长句学习**：内置高质量的多维度词库，覆盖日常起居、职场商务、美剧俚语与高级哲学长难句。
- **🎮 多邻国式三阶段渐进特训**：独创「沉浸式认读 → 互动拼写辅助 → 极限盲打默写」标准流程，科学巩固记忆。
- **🛒 完整的 RPG 经济与商店系统**：支持通关赚取 XP 经验值、在冒险商店中购买双倍经验药水、错题免死金牌、高级提示卷轴及尊贵动态称号。
- **🌐 现代化模块化架构**：采用 Flask Blueprint 蓝图解耦，内置 Flask-CORS 跨域支持，无缝对接前后端分离客户端。
- **⚡ Clone 即用**：轻量健壮，支持零配置本地启动、SQLite 数据库自动初始化、一键脚本部署与浏览器自动唤起。

---

## ✨ 核心功能一览

### 📘 学习与多阶段闯关模式
- **四重游戏化难度关卡（Easy 至 Hell）**：
  - 🟢 **Easy (简单)**：日常高频基础词汇。
  - 🔵 **Normal (进阶)**：职场常用短语与表达。
  - 🟠 **Hard (困难)**：美式俚语与社交黑话。
  - 🔴 **Hell (地狱)**：高级哲学长难句与名言。
- **多阶段特训流程 (`/api/learn`)**：
  - **阶段一（认读）**：图文结合、标准发音与语法解析（`grammar_note`）。
  - **阶段二（拼写辅助）**：打乱字母参考与首字母提示。
  - **阶段三（极限默写）**：限时盲打默写挑战与防作弊校验。
- **RPG 个人状态追踪**：实时同步当前的经验值（XP）、已通关总数与动态称号（初学冒险者 → 语言学徒 → 地道美语精锐 → 英语大宗师 → 传说中英灵）。

### 🛒 冒险商店与背包系统 (`/api/shop/*`)
- **丰富的补给道具（战术联动）**：
  - 🧪 **双倍经验药水**：通关成功时自动触发，XP 翻倍加成。
  - 🛡️ **错题免死金牌**：挑战失败时自动触发，抵扣扣分与连击中断。
  - 📜 **高级提示卷轴**：自动点亮字母提示。
  - 👑 **专属炫酷称号**：一键解锁并佩戴【学霸附体】、【英语大宗师】、【传说中英灵】等巅峰荣誉。
- **背包管理**：实时查看已购道具与库存数量。

---

## ⚡ 30 秒快速启动

### 1. 一键脚本启动（推荐）
- **Windows**：双击运行 `run.bat`（自带编码修复、环境检查与依赖自动安装）。
- **Linux / macOS**：赋予权限后运行 `./run.sh`。

### 2. 手动启动后端
```bash
git clone [https://github.com/yiyuanqian111666/daily-english-word-api.git](https://github.com/yiyuanqian111666/daily-english-word-api.git)
cd daily-english-word-api

# 安装依赖
pip install -r requirements.txt

# 启动服务 (会自动初始化数据库、打开浏览器并进入 Debug 模式)
python run.py
3. 打开前端页面
直接双击打开项目中的 index.html，前端将自动与运行在 http://127.0.0.1:5000 的后端 API 建立通信并开启沉浸式闯关！

🔥 API 接口使用示例
🎓 1. 获取多阶段学习内容
HTTP GET: /api/learn?difficulty=easy&stage=1

JSON 响应示例：

JSON
{
  "id": 1,
  "word": "apple",
  "meaning": "苹果",
  "example": "An apple a day keeps the doctor away.",
  "level": 1,
  "difficulty": "easy",
  "category": "fruit",
  "grammar_note": "基础可数名词单数形式。",
  "image_url": "[https://images.unsplash.com/](https://images.unsplash.com/)...",
  "stage": 1,
  "challenge_config": {
    "time_limit": 15.0,
    "base_xp": 10
  },
  "user_status": {
    "xp": 100,
    "total_solved": 0,
    "title": "初学冒险者"
  }
}
🧠 2. 提交挑战结算
HTTP POST: /api/challenge/submit

请求体 (Content-Type: application/json)：

JSON
{
  "word_id": 1,
  "stage": 3,
  "used_time": 3.5,
  "success": true,
  "difficulty": "normal",
  "streak": 2,
  "bet_amount": 0
}
响应示例：

JSON
{
  "success": true,
  "grade": "SS",
  "stage": 3,
  "used_time": 3.5,
  "streak": 3,
  "interactive_comment": "⚡ 闪电极速（3.5秒），SS级完美默写！",
  "earned_xp": 25,
  "user_profile": {
    "xp": 125,
    "total_solved": 1,
    "title": "初学冒险者"
  }
}
🧱 技术栈
Python 3.8+

Flask 3.x（现代化 Web 框架，采用 Blueprint 蓝图模块化与应用上下文管理）

Flask-CORS（处理跨域资源共享，完美支撑前后端分离）

SQLite（内置轻量数据库，采用绝对路径绑定，零外部服务依赖）

unittest（内建完整的自动化单元测试覆盖，运行 python -m unittest test_app.py 即可验证）

⭐ 支持这个项目
如果这个项目对你的英语学习或项目开发有所帮助：

⭐ 给仓库点个 Star

🍴 Fork 进行二次开发

🐛 提 Issue 或提出宝贵建议

一个 Star 就是持续维护的最大动力 ❤

📜 License
MIT License © 2026 yiyuanqian111666