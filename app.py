"""
======================================================================
项目名称：RPG 英语冒险与商店系统 (后端终极扩展版 v8.0)
当前文件：app.py
主要功能：
  1. SQLite 数据库自动初始化与多表联动
  2. 海量多维度（日常、职场、学术、俚语、哲学长难句）分级词库
  3. 精确筛选接口 (/api/learn) 及随机抽取不同词条
  4. 多阶段拼写校验与挑战提交、响应时间与连击统计、防作弊校验 (/api/challenge/submit)
  5. 冒险商店丰富商品拉取与道具购买扣款、背包归档 (/api/shop/items, /api/shop/buy, /api/inventory)
  6. 用户 RPG 动态称号成长机制 (XP 驱动，各难度独立 XP 奖励)
======================================================================
"""

import os
import random
import sqlite3
import logging
from flask import Flask, g, jsonify, render_template, request
from flask_cors import CORS

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

app = Flask(__name__)
CORS(app)  # 启用跨域支持，确保前后端联调通畅

DATABASE = "rpg_english.db"

# ==========================================
# 1. 数据库连接管理与生命周期挂钩
# ==========================================

def get_db():
    """获取当前请求的数据库连接实例"""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # 启用行工厂，支持通过列名访问数据
    return db

@app.teardown_appcontext
def close_connection(exception):
    """请求结束后自动关闭数据库连接"""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


# ==========================================
# 2. 数据库初始化与海量种子数据植入
# ==========================================

def init_db():
    """初始化数据库表结构并填充初始测试数据"""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        logging.info("正在检查并初始化数据库表结构...")

        # 表一：单词与长句核心库
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                meaning TEXT NOT NULL,
                example TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                difficulty TEXT DEFAULT 'easy',
                category TEXT DEFAULT 'general',
                grammar_note TEXT,
                challenge_after INTEGER DEFAULT 1,
                image_url TEXT
            )
        """
        )

        # 表二：挑战历史记录表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER,
                difficulty TEXT,
                used_time REAL,
                success BOOLEAN,
                grade TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # 表三：用户 RPG 状态表 (单例模式 id = 1)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_stats (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                xp INTEGER DEFAULT 100,
                total_solved INTEGER DEFAULT 0,
                title TEXT DEFAULT '初学冒险者'
            )
        """
        )
        cursor.execute(
            """
            INSERT OR IGNORE INTO user_stats (id, xp, total_solved, title) 
            VALUES (1, 100, 0, '初学冒险者')
        """
        )

        # 表四：商店商品表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS shop_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price INTEGER NOT NULL,
                item_type TEXT NOT NULL,
                effect_value TEXT
            )
        """
        )

        # 表五：用户背包表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                quantity INTEGER DEFAULT 1,
                FOREIGN KEY (item_id) REFERENCES shop_items(id)
            )
        """
        )

        # 初始化丰富实用的冒险商店道具
        cursor.execute("SELECT COUNT(*) FROM shop_items")
        if cursor.fetchone()[0] == 0:
            logging.info("正在植入丰富实用的商店道具...")
            default_items = [
                ("双倍经验药水 (1局)", "在接下来的1次挑战成功后，获得的XP直接翻倍！", 60, "buff", "double_xp"),
                ("错题免死金牌", "挑战失败时抵扣一次扣分与连击中断，保护你的连胜。", 90, "consumable", "save_streak"),
                ("幸运转运符", "下一次赌徒模式（Gambler）失败时，返还一半下注XP。", 150, "consumable", "gambler_shield"),
                ("高级提示卷轴", "在拼写挑战中自动点亮关键字母提示，降低通关难度。", 100, "consumable", "auto_hint"),
                ("稀有称号：【学霸附体】", "购买后立即解锁并可佩戴炫酷的专属高级称号！", 350, "title", "学霸附体"),
                ("史诗称号：【英语大宗师】", "彰显尊贵身份，将冒险者称号晋升为大宗师！", 800, "title", "英语大宗师"),
                ("传说称号：【传说中英灵】", "至高无上的荣誉称号，通往英语世界的巅峰！", 1500, "title", "传说中英灵"),
            ]
            cursor.executemany(
                """
                INSERT INTO shop_items (name, description, price, item_type, effect_value)
                VALUES (?, ?, ?, ?, ?)
            """,
                default_items,
            )
            db.commit()

        # 初始化海量分级词库与长难句数据
        cursor.execute("SELECT COUNT(*) FROM words")
        if cursor.fetchone()[0] == 0:
            logging.info("正在植入海量、多难度的英语词汇与长难句种子数据...")
            seed_data = [
                # ----------------- 简单 (Easy) 基础日常/水果 -----------------
                ("apple", "苹果", "An apple a day keeps the doctor away.", 1, "easy", "fruit", "基础名词。可数名词单数形式。", 1, "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=600"),
                ("banana", "香蕉", "Monkeys love eating fresh bananas in the jungle.", 1, "easy", "fruit", "常见水果名词。", 1, "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=600"),
                ("orange", "橙子", "She drinks a glass of fresh orange juice every morning.", 1, "easy", "fruit", "水果与颜色双义词。", 1, "https://images.unsplash.com/photo-1611080626919-7cf5a9dbab5b?w=600"),
                ("curious", "好奇的", "Children are naturally curious about the world.", 1, "easy", "adjective", "常用形容词，常与 about 连用。", 1, "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600"),
                ("achieve", "实现/达成", "Work hard and you will achieve your dreams.", 2, "easy", "verb", "核心动词，意为通过努力达成目标。", 1, "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=600"),
                ("breeze", "微风/轻而易举", "The English test was an absolute breeze.", 2, "easy", "noun", "常见生活名词与比喻表达。", 1, "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600"),
                ("journey", "旅程/历程", "Life is a journey, not a destination.", 2, "easy", "noun", "励志高频词汇。", 1, "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=600"),

                # ----------------- 进阶 (Normal) 职场与短语 -----------------
                ("hang out", "闲逛/聚会", "We like to hang out at the café on weekends.", 2, "normal", "phrasal_verb", "生活高频动词短语。", 2, "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=600"),
                ("figure out", "弄清楚/想明白", "I need some time to figure out this problem.", 3, "normal", "phrasal_verb", "思考并彻底解决某事。", 2, "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600"),
                ("pragmatic", "务实的", "We need a pragmatic approach to solve this crisis.", 3, "normal", "business", "职场高频词，强调注重实际效果。", 2, "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600"),
                ("momentum", "势头/动量", "The project gained strong momentum after the new launch.", 3, "normal", "business", "描述发展速度与发展势头的商业词汇。", 2, "https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=600"),
                ("resilience", "恢复力/坚韧", "Her resilience helped her overcome major setbacks.", 3, "normal", "psychology", "心理抗压与适应逆境的能力。", 2, "https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?w=600"),
                ("colleague", "同事/同僚", "She gets along very well with all her colleagues.", 3, "normal", "business", "职场日常高频词汇。", 2, "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=600"),

                # ----------------- 困难 (Hard) 俚语与学术 -----------------
                ("spill the tea", "八卦/吐露实情", "Come on, spill the tea! What happened last night?", 3, "hard", "slang", "现代美式流行俚语，意为爆料。", 3, "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=600"),
                ("bite the bullet", "咬牙坚持", "We have no choice but to bite the bullet.", 4, "hard", "idiom", "经典习惯用语，面对艰难困境咬牙挺过去。", 3, "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=600"),
                ("ubiquitous", "无处不在的", "Smartphones have become ubiquitous in daily life.", 4, "hard", "academic", "高级学术形容词，指 omnipresent。", 3, "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=600"),
                ("paradigm shift", "范式转移/思维大变革", "AI represents a major paradigm shift in technology.", 4, "hard", "business", "商业和科技核心概念，指根本性的模式改变。", 3, "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600"),
                ("meticulous", "一丝不苟的/细致的", "The scientist kept meticulous records of every experiment.", 4, "hard", "academic", "形容对细节极度关注与严谨。", 3, "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600"),

                # ----------------- 地狱 (Hell) 谚语与哲学长难句 -----------------
                ("Actions speak louder than words.", "事实胜于雄辩", "Don't just make promises; remember that actions speak louder.", 4, "hell", "proverb", "经典英语谚语，强调行动重于承诺。", 4, "https://images.unsplash.com/photo-1552664730-d307ca884978?w=600"),
                ("It is the mark of an educated mind to be able to entertain a thought without accepting it.", "能容纳一种观念而不急于认同，才是一个受过教育的头脑的标志.", "Aristotle wisely noted that true intellect involves suspending immediate judgment.", 5, "hell", "philosophy", "亚里士多德名言，考察复杂从句理解能力。", 4, "https://images.unsplash.com/photo-1532012197267-da84d127e765?w=600"),
                ("He who has a why to live can bear almost any how.", "知其所为何以生，便能承受世间任何生存方式.", "Nietzsche's profound insight highlights the power of inner purpose.", 5, "hell", "philosophy", "尼采名言长难句挑战，探讨人生意义。", 4, "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=600"),
                ("In the middle of difficulty lies opportunity.", "困难之中蕴藏着机遇.", "Einstein reminded us to look past obstacles toward potential breakthroughs.", 5, "hell", "philosophy", "爱因斯坦深刻智慧箴言。", 4, "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=600")
            ]
            cursor.executemany(
                """
                INSERT INTO words (word, meaning, example, level, difficulty, category, grammar_note, challenge_after, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                seed_data,
            )
            db.commit()
        
        logging.info("数据库初始化完成！")


# ==========================================
# 3. 辅助计算函数
# ==========================================

def calculate_title(xp):
    """根据当前用户的 XP 动态计算冒险者称号"""
    if xp >= 1500:
        return "传说中英灵"
    elif xp >= 800:
        return "英语大宗师"
    elif xp >= 350:
        return "地道美语精锐"
    elif xp >= 100:
        return "语言学徒"
    return "初学冒险者"


# ==========================================
# 4. 核心路由与 API 接口定义
# ==========================================

@app.route("/")
def home():
    """渲染前端主页面"""
    return render_template("index.html")


@app.route("/api/learn", methods=["GET"])
def learn():
    """
    获取学习词条接口（根据难度随机获取不同单词或句子）
    参数支持：
      - difficulty: easy, normal, hard, hell, gambler
      - category: fruit, business, philosophy 等可选分类过滤
    """
    difficulty = request.args.get("difficulty", "easy")
    category = request.args.get("category")

    db = get_db()
    cursor = db.cursor()

    # 构建查询逻辑
    if difficulty == "gambler":
        cursor.execute("SELECT * FROM words WHERE difficulty IN ('hard', 'hell')")
    else:
        query = "SELECT * FROM words WHERE difficulty = ?"
        params = [difficulty]
        if category:
            query += " AND category = ?"
            params.append(category)
        cursor.execute(query, params)

    words = cursor.fetchall()
    
    # 若在特定分类下没有找到单词，则降级按当前难度全库查询
    if not words:
        cursor.execute("SELECT * FROM words WHERE difficulty = ?", (difficulty,))
        words = cursor.fetchall()
        
    # 如果该难度依然为空，则降级查询全库
    if not words:
        cursor.execute("SELECT * FROM words")
        words = cursor.fetchall()

    word = random.choice(words)

    # 获取当前用户状态
    cursor.execute("SELECT xp, total_solved, title FROM user_stats WHERE id = 1")
    stats = cursor.fetchone()

    logging.info(f"派发词条 ID: {word['id']}, 内容: {word['word']}, 当前难度: {difficulty}")

    return jsonify(
        {
            "id": word["id"],
            "word": word["word"],
            "meaning": word["meaning"],
            "example": word["example"],
            "level": word["level"],
            "difficulty": word["difficulty"],
            "category": word["category"],
            "grammar_note": word["grammar_note"],
            "challenge_after": word["challenge_after"],
            "image_url": word["image_url"],
            "user_status": {
                "xp": stats["xp"],
                "total_solved": stats["total_solved"],
                "title": stats["title"],
            },
        }
    )


@app.route("/api/shop/items", methods=["GET"])
def get_shop_items():
    """获取冒险商店的所有可用商品及当前用户的 XP 余额"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM shop_items")
    items = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT xp FROM user_stats WHERE id = 1")
    user_xp = cursor.fetchone()["xp"]

    return jsonify({"items": items, "user_xp": user_xp})


@app.route("/api/shop/buy", methods=["POST"])
def buy_item():
    """商店购买道具接口"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "缺少请求负载"}), 400

    item_id = data.get("item_id")
    if not item_id:
        return jsonify({"error": "缺少商品ID"}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM shop_items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    if not item:
        return jsonify({"error": "该商品不存在"}), 404

    cursor.execute("SELECT xp, title FROM user_stats WHERE id = 1")
    stats = cursor.fetchone()
    current_xp = stats["xp"]
    price = item["price"]

    if current_xp < price:
        return jsonify({"error": "您的 XP 不足，无法购买此道具！快去多通关赚取奖励吧~"}), 400

    new_xp = current_xp - price
    cursor.execute("UPDATE user_stats SET xp = ? WHERE id = 1", (new_xp,))

    # 如果购买的是称号道具，直接更新用户的当前称号
    if item["item_type"] == "title":
        new_title = item["effect_value"]
        cursor.execute("UPDATE user_stats SET title = ? WHERE id = 1", (new_title,))

    # 将道具记入用户背包
    cursor.execute("SELECT id, quantity FROM user_inventory WHERE item_id = ?", (item_id,))
    inv = cursor.fetchone()
    if inv:
        cursor.execute("UPDATE user_inventory SET quantity = quantity + 1 WHERE id = ?", (inv["id"],))
    else:
        cursor.execute("INSERT INTO user_inventory (item_id, quantity) VALUES (?, 1)", (item_id,))

    db.commit()

    cursor.execute("SELECT xp, title FROM user_stats WHERE id = 1")
    updated_stats = cursor.fetchone()

    return jsonify(
        {
            "success": True,
            "message": f"成功购买【{item['name']}】！",
            "remaining_xp": updated_stats["xp"],
            "user_profile": {
                "xp": updated_stats["xp"],
                "title": updated_stats["title"],
            },
        }
    )


@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    """获取用户背包中的道具列表"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT i.id, s.name, s.description, s.item_type, s.effect_value, i.quantity
        FROM user_inventory i
        JOIN shop_items s ON i.item_id = s.id
    """
    )
    items = [dict(row) for row in cursor.fetchall()]
    return jsonify({"inventory": items})


@app.route("/api/challenge/submit", methods=["POST"])
def submit_challenge():
    """
    核心挑战提交与经验结算接口（各难度采用独立、差异化的 XP 奖励基底）
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "缺少请求JSON主体"}), 400

    used_time = data.get("used_time", 5.0)
    success = data.get("success", False)
    difficulty = data.get("difficulty", "normal")
    streak = data.get("streak", 0)
    bet_amount = int(data.get("bet_amount", 0))

    if not isinstance(used_time, (int, float)):
        return jsonify({"error": "used_time 类型不合法"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT xp, total_solved FROM user_stats WHERE id = 1")
    stats = cursor.fetchone()
    current_xp = stats["xp"]

    # 防作弊检测：响应时间过快判定为异常
    if success and used_time < 0.3:
        return jsonify(
            {
                "success": False,
                "grade": "F",
                "interactive_comment": "⚠️ 检测到异常作弊行为，收益已被安全系统拦截。",
                "earned_xp": 0,
                "user_profile": {
                    "xp": current_xp,
                    "total_solved": stats["total_solved"],
                    "title": calculate_title(current_xp),
                },
            }
        )

    earned_xp = 0
    grade = "F"
    interactive_comment = "挑战完成！"

    # 1. 赌徒模式结算逻辑
    if difficulty == "gambler":
        if bet_amount <= 0 or bet_amount > current_xp:
            return jsonify({"error": "不合法的下注金额！"}), 400
        if success:
            earned_xp = bet_amount
            grade = "SS"
            interactive_comment = f"🎰 赌徒大捷！高风险下注赢取 {bet_amount} XP 奖励！"
        else:
            earned_xp = -bet_amount
            grade = "F"
            interactive_comment = f"💸 赌徒失利！扣除下注的 {bet_amount} XP！"
    
    # 2. 各难度独立差异化 XP 奖励机制
    else:
        if success:
            # 各难度独立的丰厚 XP 奖励基底
            base_rewards = {
                "easy": 10,     # 简单模式基础奖励
                "normal": 25,   # 进阶模式基础奖励
                "hard": 60,     # 困难模式高额奖励
                "hell": 120     # 地狱模式史诗长难句奖励
            }
            earned_xp = base_rewards.get(difficulty, 15)

            # 速度评级额外加速加成
            if used_time <= 2.5:
                grade = "SS"
                earned_xp += int(earned_xp * 0.5) # 极速额外加成 50%
            elif used_time <= 5.0:
                grade = "S"
                earned_xp += int(earned_xp * 0.3)
            elif used_time <= 9.0:
                grade = "A"
                earned_xp += int(earned_xp * 0.15)
            else:
                grade = "B"

            # 连击额外加成 (每连击一次额外+5 XP)
            if streak >= 2:
                earned_xp += streak * 5

            comments = {
                "SS": f"⚡ 闪电响应（{round(used_time, 1)}秒），SS级超凡通关！",
                "S": f"🔥 反应敏捷，S级完美通关！",
                "A": f"🌟 稳扎稳打，A级顺利通过！",
                "B": f"👍 通关成功！",
            }
            interactive_comment = comments.get(grade, "挑战成功！")
        else:
            earned_xp = 0
            grade = "F"
            interactive_comment = "挑战拼写失败，再接再厉！"

    new_xp = max(0, current_xp + earned_xp)
    new_solved = stats["total_solved"] + (1 if success and difficulty != "gambler" else 0)
    new_title = calculate_title(new_xp)

    cursor.execute(
        """
        UPDATE user_stats 
        SET xp = ?, total_solved = ?, title = ?
        WHERE id = 1
    """,
        (new_xp, new_solved, new_title),
    )
    db.commit()

    logging.info(f"挑战结算: 难度={difficulty}, 结果={'成功' if success else '失败'}, 获得XP={earned_xp}, 当前总XP={new_xp}")

    return jsonify(
        {
            "success": success,
            "grade": grade,
            "used_time": used_time,
            "streak": streak if success else 0,
            "interactive_comment": interactive_comment,
            "earned_xp": earned_xp,
            "user_profile": {
                "xp": new_xp,
                "total_solved": new_solved,
                "title": new_title,
            },
        }
    )


# ==========================================
# 5. 应用入口启动
# ==========================================

if __name__ == "__main__":
    init_db()
    logging.info("==================================================")
    logging.info("🚀 RPG 英语冒险后端服务已成功启动（v8.0 扩展版）！")
    logging.info("🌐 监听地址: http://127.0.0.1:5000")
    logging.info("==================================================")
    app.run(host="127.0.0.1", port=5000, debug=True)