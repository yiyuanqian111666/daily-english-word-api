"""
======================================================================
项目名称：RPG 英语冒险与商店系统 (后端多邻国多阶段进阶版 v9.0)
当前文件：app.py
主要功能：
  1. SQLite 数据库自动初始化与海量多维度分级词库
  2. 多邻国式三阶段学习接口 (/api/learn)：认读 -> 拼写 -> 挑战
  3. 分级限时与动态难度的默写挑战及防作弊校验 (/api/challenge/submit)
  4. 冒险商店道具购买、称号晋升与用户背包管理
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
CORS(app)  # 启用跨域支持

DATABASE = "rpg_english.db"

# ==========================================
# 1. 数据库连接管理
# ==========================================

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


# ==========================================
# 2. 数据库初始化与海量词库植入
# ==========================================

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        logging.info("正在检查并初始化数据库表结构...")

        # 单词核心库
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
                image_url TEXT
            )
        """
        )

        # 挑战历史记录表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER,
                difficulty TEXT,
                stage INTEGER,
                used_time REAL,
                success BOOLEAN,
                grade TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # 用户 RPG 状态表
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

        # 商店商品表
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

        # 用户背包表
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

        # 初始化商店道具
        cursor.execute("SELECT COUNT(*) FROM shop_items")
        if cursor.fetchone()[0] == 0:
            logging.info("正在植入冒险商店道具...")
            default_items = [
                ("双倍经验药水 (1局)", "接下来的1次挑战成功后，获得的 XP 翻倍！", 60, "buff", "double_xp"),
                ("错题免死金牌", "挑战失败时抵扣一次扣分与连击中断。", 90, "consumable", "save_streak"),
                ("高级提示卷轴", "在拼写与默写挑战中自动点亮部分字母提示。", 100, "consumable", "auto_hint"),
                ("稀有称号：【学霸附体】", "购买后立即解锁并佩戴炫酷高级称号！", 350, "title", "学霸附体"),
                ("史诗称号：【英语大宗师】", "将冒险者称号晋升为大宗师！", 800, "title", "英语大宗师"),
                ("传说称号：【传说中英灵】", "通往英语世界的巅峰荣誉称号！", 1500, "title", "传说中英灵"),
            ]
            cursor.executemany(
                """
                INSERT INTO shop_items (name, description, price, item_type, effect_value)
                VALUES (?, ?, ?, ?, ?)
            """,
                default_items,
            )
            db.commit()

        # 初始化海量分级词库（扩充版）
        cursor.execute("SELECT COUNT(*) FROM words")
        if cursor.fetchone()[0] == 0:
            logging.info("正在植入海量、多难度的英语词汇种子数据...")
            seed_data = [
                # 简单 (Easy) - 日常生活与基础词汇
                ("apple", "苹果", "An apple a day keeps the doctor away.", 1, "easy", "fruit", "基础可数名词单数形式。", "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=600"),
                ("banana", "香蕉", "Monkeys love eating fresh bananas.", 1, "easy", "fruit", "常见水果名词。", "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=600"),
                ("orange", "橙子", "She drinks fresh orange juice every morning.", 1, "easy", "fruit", "水果与颜色双义词。", "https://images.unsplash.com/photo-1611080626919-7cf5a9dbab5b?w=600"),
                ("curious", "好奇的", "Children are naturally curious about the world.", 1, "easy", "adjective", "常与 about 连用。", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600"),
                ("achieve", "实现/达成", "Work hard and you will achieve your dreams.", 2, "easy", "verb", "核心动词。", "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=600"),
                ("breeze", "微风/轻而易举", "The English test was an absolute breeze.", 2, "easy", "noun", "生活名词。", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600"),
                ("journey", "旅程/历程", "Life is a journey, not a destination.", 2, "easy", "noun", "励志高频词。", "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=600"),

                # 进阶 (Normal) - 职场与常用短语
                ("hang out", "闲逛/聚会", "We like to hang out at the café.", 2, "normal", "phrasal_verb", "生活高频动词短语。", "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=600"),
                ("figure out", "弄清楚", "I need time to figure out this problem.", 3, "normal", "phrasal_verb", "思考并彻底解决。", "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600"),
                ("pragmatic", "务实的", "We need a pragmatic approach.", 3, "normal", "business", "强调注重实际效果。", "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600"),
                ("momentum", "势头/动量", "The project gained strong momentum.", 3, "normal", "business", "商业发展速度词汇。", "https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=600"),
                ("resilience", "恢复力/坚韧", "Her resilience helped her overcome setbacks.", 3, "normal", "psychology", "心理抗压能力。", "https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?w=600"),
                ("colleague", "同事", "She gets along well with all colleagues.", 3, "normal", "business", "职场日常用词。", "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=600"),

                # 困难 (Hard) - 学术与俚语
                ("spill the tea", "八卦/爆料", "Come on, spill the tea! What happened?", 3, "hard", "slang", "美式流行俚语。", "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=600"),
                ("bite the bullet", "咬牙坚持", "We have no choice but to bite the bullet.", 4, "hard", "idiom", "习惯用语，面对困境坚持。", "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=600"),
                ("ubiquitous", "无处不在的", "Smartphones have become ubiquitous.", 4, "hard", "academic", "高级学术形容词。", "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=600"),
                ("paradigm shift", "范式转移", "AI represents a major paradigm shift.", 4, "hard", "business", "科技与商业核心概念。", "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600"),
                ("meticulous", "一丝不苟的", "The scientist kept meticulous records.", 4, "hard", "academic", "形容极度严谨。", "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600"),

                # 地狱 (Hell) - 哲学与长难句
                ("Actions speak louder than words.", "事实胜于雄辩", "Remember that actions speak louder.", 4, "hell", "proverb", "经典英语谚语。", "https://images.unsplash.com/photo-1552664730-d307ca884978?w=600"),
                ("It is the mark of an educated mind to be able to entertain a thought without accepting it.", "能容纳一种观念而不急于认同，才是一个受过教育的头脑的标志.", "Aristotle's quote on intellect.", 5, "hell", "philosophy", "亚里士多德名言长句。", "https://images.unsplash.com/photo-1532012197267-da84d127e765?w=600"),
                ("He who has a why to live can bear almost any how.", "知其所为何以生，便能承受世间任何生存方式.", "Nietzsche's insight.", 5, "hell", "philosophy", "尼采名言。", "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=600"),
                ("In the middle of difficulty lies opportunity.", "困难之中蕴藏着机遇.", "Einstein's wisdom.", 5, "hell", "philosophy", "爱因斯坦箴言。", "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=600")
            ]
            cursor.executemany(
                """
                INSERT INTO words (word, meaning, example, level, difficulty, category, grammar_note, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                seed_data,
            )
            db.commit()
        
        logging.info("数据库初始化完成！")


# ==========================================
# 3. 辅助函数：计算称号与不同阶段规则
# ==========================================

def calculate_title(xp):
    if xp >= 1500:
        return "传说中英灵"
    elif xp >= 800:
        return "英语大宗师"
    elif xp >= 350:
        return "地道美语精锐"
    elif xp >= 100:
        return "语言学徒"
    return "初学冒险者"

def get_challenge_config(difficulty):
    """根据难度返回不同的倒计时时间限制与基础 XP 奖励"""
    configs = {
        "easy": {"time_limit": 15.0, "base_xp": 10},
        "normal": {"time_limit": 12.0, "base_xp": 25},
        "hard": {"time_limit": 8.0, "base_xp": 60},
        "hell": {"time_limit": 20.0, "base_xp": 120} # 长难句给更充裕的时间
    }
    return configs.get(difficulty, {"time_limit": 10.0, "base_xp": 15})


# ==========================================
# 4. 核心路由与 API 接口
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/learn", methods=["GET"])
def learn():
    """
    多邻国式多阶段学习接口：
    参数：
      - difficulty: easy, normal, hard, hell, gambler
      - stage: 1 (阶段一：认读/听音), 2 (阶段二：拼写辅助/选词填空), 3 (阶段三：极限默写)
    """
    difficulty = request.args.get("difficulty", "easy")
    stage = int(request.args.get("stage", 1)) # 默认阶段一

    db = get_db()
    cursor = db.cursor()

    if difficulty == "gambler":
        cursor.execute("SELECT * FROM words WHERE difficulty IN ('hard', 'hell')")
    else:
        cursor.execute("SELECT * FROM words WHERE difficulty = ?", (difficulty,))

    words = cursor.fetchall()
    if not words:
        cursor.execute("SELECT * FROM words")
        words = cursor.fetchall()

    word = random.choice(words)
    cursor.execute("SELECT xp, total_solved, title FROM user_stats WHERE id = 1")
    stats = cursor.fetchone()

    # 根据不同阶段构造返回的数据结构
    response_data = {
        "id": word["id"],
        "word": word["word"],
        "meaning": word["meaning"],
        "example": word["example"],
        "level": word["level"],
        "difficulty": word["difficulty"],
        "category": word["category"],
        "grammar_note": word["grammar_note"],
        "image_url": word["image_url"],
        "stage": stage,
        "challenge_config": get_challenge_config(word["difficulty"]),
        "user_status": {
            "xp": stats["xp"],
            "total_solved": stats["total_solved"],
            "title": stats["title"],
        }
    }

    # 阶段二：拼写辅助（可以附带混淆选项或首字母提示）
    if stage == 2:
        target_word = word["word"]
        # 生成几个干扰选项或提示
        letters = list(target_word.replace(" ", ""))
        random.shuffle(letters)
        response_data["scrambled_letters"] = letters
        response_data["hint"] = f"首字母大写提示: {target_word[0].upper()}... (总共 {len(target_word)} 个字符)"

    return jsonify(response_data)


@app.route("/api/challenge/submit", methods=["POST"])
def submit_challenge():
    """
    多阶段挑战与结算接口：
    支持 stage 1 (认读完成确认), stage 2 (拼写校验), stage 3 (极限默写挑战)
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "缺少请求JSON主体"}), 400

    word_id = data.get("word_id")
    stage = int(data.get("stage", 3))
    used_time = data.get("used_time", 5.0)
    success = data.get("success", False)
    difficulty = data.get("difficulty", "normal")
    streak = data.get("streak", 0)
    bet_amount = int(data.get("bet_amount", 0))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT xp, total_solved FROM user_stats WHERE id = 1")
    stats = cursor.fetchone()
    current_xp = stats["xp"]

    config = get_challenge_config(difficulty)
    time_limit = config["time_limit"]

    # 检查超时（仅在阶段三严格限时）
    if stage == 3 and used_time > time_limit:
        success = False

    earned_xp = 0
    grade = "F"
    interactive_comment = "学习进度推进成功！"

    if stage == 1:
        # 阶段一认读：给予少量鼓励 XP
        earned_xp = 5 if success else 0
        grade = "A" if success else "F"
        interactive_comment = "📖 认读完成，已建立记忆印象！"

    elif stage == 2:
        # 阶段二拼写：中等奖励
        earned_xp = 15 if success else 0
        grade = "S" if success else "F"
        interactive_comment = "✍️ 拼写训练通过，手感火热！"

    elif stage == 3:
        # 阶段三极限默写挑战结算
        if difficulty == "gambler":
            if bet_amount <= 0 or bet_amount > current_xp:
                return jsonify({"error": "不合法的下注金额！"}), 400
            if success:
                earned_xp = bet_amount
                grade = "SS"
                interactive_comment = f"🎰 赌徒模式大捷！赢取 {bet_amount} XP！"
            else:
                earned_xp = -bet_amount
                grade = "F"
                interactive_comment = f"💸 赌徒失利！扣除 {bet_amount} XP！"
        else:
            if success:
                base_xp = config["base_xp"]
                earned_xp = base_xp

                # 根据耗时评级
                if used_time <= time_limit * 0.3:
                    grade = "SS"
                    earned_xp += int(base_xp * 0.5)
                elif used_time <= time_limit * 0.6:
                    grade = "S"
                    earned_xp += int(base_xp * 0.3)
                else:
                    grade = "A"

                # 连击加成
                if streak >= 2:
                    earned_xp += streak * 5

                comments = {
                    "SS": f"⚡ 闪电极速（{round(used_time, 1)}秒），SS级完美默写！",
                    "S": f"🔥 反应敏捷，S级通关！",
                    "A": f"🌟 稳扎稳打，成功默写！",
                }
                interactive_comment = comments.get(grade, "挑战成功！")
            else:
                earned_xp = 0
                grade = "F"
                interactive_comment = "❌ 默写超时或拼写错误，挑战失败！"

    new_xp = max(0, current_xp + earned_xp)
    new_solved = stats["total_solved"] + (1 if success and stage == 3 and difficulty != "gambler" else 0)
    new_title = calculate_title(new_xp)

    cursor.execute(
        """
        UPDATE user_stats 
        SET xp = ?, total_solved = ?, title = ?
        WHERE id = 1
    """,
        (new_xp, new_solved, new_title),
    )
    
    # 记录挑战历史
    cursor.execute(
        """
        INSERT INTO challenges (word_id, difficulty, stage, used_time, success, grade)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (word_id, difficulty, stage, used_time, success, grade)
    )
    db.commit()

    return jsonify(
        {
            "success": success,
            "grade": grade,
            "stage": stage,
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
# 5. 商店与背包路由
# ==========================================

@app.route("/api/shop/items", methods=["GET"])
def get_shop_items():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM shop_items")
    items = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT xp FROM user_stats WHERE id = 1")
    user_xp = cursor.fetchone()["xp"]
    return jsonify({"items": items, "user_xp": user_xp})


@app.route("/api/shop/buy", methods=["POST"])
def buy_item():
    data = request.get_json()
    item_id = data.get("item_id")
    if not item_id:
        return jsonify({"error": "缺少商品ID"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM shop_items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    if not item:
        return jsonify({"error": "商品不存在"}), 404

    cursor.execute("SELECT xp, title FROM user_stats WHERE id = 1")
    stats = cursor.fetchone()
    if stats["xp"] < item["price"]:
        return jsonify({"error": "XP 不足，快去闯关赚取奖励吧！"}), 400

    new_xp = stats["xp"] - item["price"]
    cursor.execute("UPDATE user_stats SET xp = ? WHERE id = 1", (new_xp,))

    if item["item_type"] == "title":
        cursor.execute("UPDATE user_stats SET title = ? WHERE id = 1", (item["effect_value"],))

    cursor.execute("SELECT id, quantity FROM user_inventory WHERE item_id = ?", (item_id,))
    inv = cursor.fetchone()
    if inv:
        cursor.execute("UPDATE user_inventory SET quantity = quantity + 1 WHERE id = ?", (inv["id"],))
    else:
        cursor.execute("INSERT INTO user_inventory (item_id, quantity) VALUES (?, 1)", (item_id,))

    db.commit()
    cursor.execute("SELECT xp, title FROM user_stats WHERE id = 1")
    updated = cursor.fetchone()

    return jsonify({
        "success": True,
        "message": f"成功购买【{item['name']}】！",
        "remaining_xp": updated["xp"],
        "user_profile": {"xp": updated["xp"], "title": updated["title"]}
    })


@app.route("/api/inventory", methods=["GET"])
def get_inventory():
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


# ==========================================
# 6. 启动主入口
# ==========================================

if __name__ == "__main__":
    init_db()
    logging.info("==================================================")
    logging.info("🚀 RPG 英语冒险后端服务已成功启动（v9.0 多阶段多邻国版）！")
    logging.info("🌐 监听地址: http://127.0.0.1:5000")
    logging.info("==================================================")
    app.run(host="127.0.0.1", port=5000, debug=True)