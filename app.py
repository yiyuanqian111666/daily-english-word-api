"""
======================================================================
项目名称：RPG 英语冒险与商店系统 (后端多邻国多阶段进阶版 v10.0)
当前文件：app.py
更新说明：深度植入道具策略系统（免死金牌自动触发、双倍药水实时生效）
======================================================================
"""

import logging
import os
import random
import sqlite3
from typing import Any, Dict, Optional
from flask import Flask, Blueprint, g, jsonify, render_template, request
from flask_cors import CORS

# ==========================================
# 0. 配置与初始化
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "rpg_english.db")

app = Flask(__name__)
CORS(app)

api_bp = Blueprint("api", __name__, url_prefix="/api")


# ==========================================
# 1. 数据库与核心辅助函数
# ==========================================
def get_db() -> sqlite3.Connection:
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def calculate_title(xp: int) -> str:
    if xp >= 1500:
        return "传说中英灵"
    elif xp >= 800:
        return "英语大宗师"
    elif xp >= 350:
        return "地道美语精锐"
    elif xp >= 100:
        return "语言学徒"
    return "初学冒险者"


def get_challenge_config(difficulty: str) -> Dict[str, Any]:
    configs = {
        "easy": {"time_limit": 15.0, "base_xp": 10},
        "normal": {"time_limit": 12.0, "base_xp": 25},
        "hard": {"time_limit": 8.0, "base_xp": 60},
        "hell": {"time_limit": 22.0, "base_xp": 120},
    }
    return configs.get(difficulty, {"time_limit": 10.0, "base_xp": 15})


def init_db() -> None:
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        logging.info(f"正在检查并初始化数据库表结构 (路径: {DATABASE})...")

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
        db.commit()

        cursor.execute("SELECT COUNT(*) FROM shop_items")
        if cursor.fetchone()[0] == 0:
            default_items = [
                ("双倍经验药水 (1局)", "接下来的1次挑战成功后，获得的 XP 翻倍！", 60, "buff", "double_xp"),
                ("错题免死金牌", "挑战失败时自动触发，抵扣扣分与连击中断！", 90, "consumable", "save_streak"),
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

        cursor.execute("SELECT COUNT(*) FROM words")
        if cursor.fetchone()[0] == 0:
            seed_data = [
                ("apple", "苹果", "An apple a day keeps the doctor away.", 1, "easy", "fruit", "基础可数名词单数形式。", "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=600"),
                ("banana", "香蕉", "Monkeys love eating fresh bananas.", 1, "easy", "fruit", "常见水果名词。", "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=600"),
                ("curious", "好奇的", "Children are naturally curious about the world.", 1, "easy", "adjective", "常与 about 连用。", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600"),
                ("achieve", "实现/达成", "Work hard and you will achieve your dreams.", 2, "easy", "verb", "核心动词。", "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=600"),
                ("journey", "旅程/历程", "Life is a journey, not a destination.", 2, "easy", "noun", "励志高频词。", "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=600"),
                ("hang out", "闲逛/聚会", "We like to hang out at the café.", 2, "normal", "phrasal_verb", "生活高频动词短语。", "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=600"),
                ("figure out", "弄清楚", "I need time to figure out this problem.", 3, "normal", "phrasal_verb", "思考并彻底解决。", "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600"),
                ("pragmatic", "务实的", "We need a pragmatic approach to solve this.", 3, "normal", "business", "强调注重实际效果。", "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600"),
                ("momentum", "势头/动力", "The project gained strong momentum this quarter.", 3, "normal", "business", "商业发展速度词汇。", "https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=600"),
                ("resilience", "恢复力/坚韧", "Her resilience helped her overcome setbacks.", 3, "normal", "psychology", "心理抗压能力。", "https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?w=600"),
                ("spill the tea", "八卦/爆料", "Come on, spill the tea! What happened?", 3, "hard", "slang", "美式流行俚语。", "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=600"),
                ("bite the bullet", "咬牙坚持", "We have no choice but to bite the bullet.", 4, "hard", "idiom", "习惯用语，面对困境坚持。", "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=600"),
                ("ubiquitous", "无处不在的", "Smartphones have become ubiquitous nowadays.", 4, "hard", "academic", "高级学术形容词。", "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=600"),
                ("paradigm shift", "范式转移", "AI represents a major paradigm shift in tech.", 4, "hard", "business", "科技与商业核心概念。", "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600"),
                ("Actions speak louder than words.", "事实胜于雄辩", "Remember that actions speak louder.", 4, "hell", "proverb", "经典英语谚语。", "https://images.unsplash.com/photo-1552664730-d307ca884978?w=600"),
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


# ==========================================
# 2. API 路由定义
# ==========================================
@api_bp.route("/learn", methods=["GET"])
def learn_word() -> Any:
    difficulty = request.args.get("difficulty", "easy")
    stage = int(request.args.get("stage", 1))

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
            "xp": stats["xp"] if stats else 100,
            "total_solved": stats["total_solved"] if stats else 0,
            "title": stats["title"] if stats else "初学冒险者",
        },
    }
    return jsonify(response_data)


@api_bp.route("/challenge/submit", methods=["POST"])
def submit_challenge() -> Any:
    """闯关提交：深度联动背包中的【免死金牌】与【双倍经验药水】"""
    data = request.get_json() or {}

    word_id = data.get("word_id")
    stage = int(data.get("stage", 3))
    used_time = float(data.get("used_time", 1.0))
    
    raw_success = data.get("success", False)
    if isinstance(raw_success, str):
        success = raw_success.lower() in ("true", "1", "yes")
    else:
        success = bool(raw_success)

    difficulty = str(data.get("difficulty", "normal"))
    streak = int(data.get("streak", 0))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT xp, total_solved FROM user_stats WHERE id = 1")
    stats = cursor.fetchone()
    current_xp = stats["xp"] if stats else 100

    config = get_challenge_config(difficulty)
    time_limit = config["time_limit"]

    if stage == 3 and used_time > (time_limit + 0.5):
        success = False

    # 🌟 核心战略机制 1：如果挑战失败（打错或超时），检查背包中是否有【错题免死金牌】
    item_effect_triggered = None
    if not success and stage == 3:
        cursor.execute(
            """
            V.id, inv.id as inv_id, inv.quantity, s.effect_value 
            FROM user_inventory inv
            JOIN shop_items s ON inv.item_id = s.id
            WHERE s.effect_value = 'save_streak' AND inv.quantity > 0
        """
        ) # 兼容查询
        # 上面写法防错，直接用安全的子查询：
        cursor.execute("""
            SELECT inv.id, inv.quantity FROM user_inventory inv
            JOIN shop_items s ON inv.item_id = s.id
            WHERE s.effect_value = 'save_streak' AND inv.quantity > 0
        """)
        shield = cursor.fetchone()
        if shield:
            # 消耗一张免死金牌！
            cursor.execute("UPDATE user_inventory SET quantity = quantity - 1 WHERE id = ?", (shield["id"],))
            cursor.execute("DELETE FROM user_inventory WHERE id = ? AND quantity <= 0", (shield["id"],))
            success = True  # 逆转失败！
            item_effect_triggered = "🛡️【错题免死金牌】自动触发！抵消了本次失败与连击中断！"

    earned_xp = 0
    grade = "F"
    interactive_comment = "学习进度推进成功！"

    if stage == 1:
        earned_xp = 5 if success else 0
        grade = "A" if success else "F"
        interactive_comment = "📖 认读完成，获得 +5 XP！"
    elif stage == 2:
        earned_xp = 15 if success else 0
        grade = "S" if success else "F"
        interactive_comment = "✍️ 拼写训练通过，获得 +15 XP！"
    elif stage == 3:
        if success:
            base_xp = config["base_xp"]
            earned_xp = base_xp

            if used_time <= time_limit * 0.3:
                grade = "SS"
                earned_xp += int(base_xp * 0.5)
            elif used_time <= time_limit * 0.6:
                grade = "S"
                earned_xp += int(base_xp * 0.3)
            else:
                grade = "A"

            if streak >= 2:
                earned_xp += streak * 5

            # 🌟 核心战略机制 2：如果成功，检查背包中是否有【双倍经验药水】
            if not item_effect_triggered:
                cursor.execute("""
                    SELECT inv.id, inv.quantity FROM user_inventory inv
                    JOIN shop_items s ON inv.item_id = s.id
                    WHERE s.effect_value = 'double_xp' AND inv.quantity > 0
                """)
                potion = cursor.fetchone()
                if potion:
                    # 消耗一瓶双倍药水！
                    cursor.execute("UPDATE user_inventory SET quantity = quantity - 1 WHERE id = ?", (potion["id"],))
                    cursor.execute("DELETE FROM user_inventory WHERE id = ? AND quantity <= 0", (potion["id"],))
                    earned_xp *= 2  # 经验直接翻倍！
                    item_effect_triggered = "🧪【双倍经验药水】生效！本局获得的 XP 成功翻倍！"

            interactive_comment = f"⚡ 挑战成功！获得 {earned_xp} XP 奖励！"
            if item_effect_triggered:
                interactive_comment += f" ({item_effect_triggered})"
        else:
            earned_xp = 0
            grade = "F"
            interactive_comment = "❌ 默写超时或拼写错误，挑战失败，连击已重置！"

    if item_effect_triggered and not success:
        # 如果是免死金牌触发的成功
        interactive_comment = f"🛡️ 惊险过关！{item_effect_triggered}"

    new_xp = max(0, current_xp + earned_xp)
    new_solved = (stats["total_solved"] if stats else 0) + (1 if success and stage == 3 else 0)
    new_title = calculate_title(new_xp)

    logging.info(f"【结算日志】Stage:{stage} | Success:{success} | 变动XP:+{earned_xp} | 总XP:{current_xp} -> {new_xp}")

    cursor.execute(
        """
        UPDATE user_stats 
        SET xp = ?, total_solved = ?, title = ?
        WHERE id = 1
    """,
        (new_xp, new_solved, new_title),
    )

    cursor.execute(
        """
        INSERT INTO challenges (word_id, difficulty, stage, used_time, success, grade)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (word_id, difficulty, stage, used_time, success, grade),
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


@api_bp.route("/shop/items", methods=["GET"])
def get_shop_items() -> Any:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM shop_items")
    items = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT xp FROM user_stats WHERE id = 1")
    row = cursor.fetchone()
    user_xp = row["xp"] if row else 100
    return jsonify({"items": items, "user_xp": user_xp})


@api_bp.route("/shop/buy", methods=["POST"])
def buy_item() -> Any:
    data = request.get_json() or {}
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
    if not stats or stats["xp"] < item["price"]:
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
        "user_profile": {"xp": updated["xp"], "title": updated["title"]},
    })


@api_bp.route("/inventory", methods=["GET"])
def get_inventory() -> Any:
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


app.register_blueprint(api_bp)


@app.teardown_appcontext
def close_connection(exception: Optional[BaseException]) -> None:
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def home() -> str:
    return render_template("index.html")


if __name__ == "__main__":
    init_db()
    logging.info("==================================================")
    logging.info("🚀 RPG 英语冒险后端服务已成功启动（v10.0 模块化进阶版）！")
    logging.info("🌐 监听地址: http://127.0.0.1:5000")
    logging.info("==================================================")
    app.run(host="127.0.0.1", port=5000, debug=True)