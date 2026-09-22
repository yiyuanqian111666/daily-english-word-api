from datetime import datetime
import random
import sqlite3
from flask import Flask, g, jsonify, request

app = Flask(__name__)

DB_NAME = "words.db"
CHALLENGE_LIMIT = 20
CHALLENGE_TRIGGER = 3


# ==================== 📦 数据库连接管理 ====================
def get_db():
    """使用 Flask 的 g 对象实现请求级别的数据库连接复用"""
    if "db" not in g:
        g.db = sqlite3.connect(DB_NAME)
        g.db.row_factory = sqlite3.Row  # 启用字典/行映射，方便后续取值
    return g.db


@app.teardown_appcontext
def close_db(exception):
    """请求结束时自动关闭数据库连接"""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """初始化数据库表及内置测试数据"""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # 1. 单词表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                meaning TEXT,
                example TEXT,
                level INTEGER DEFAULT 1,
                category TEXT DEFAULT 'general'
            )
        """
        )

        # 2. 对话表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS dialogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                scene TEXT DEFAULT 'daily'
            )
        """
        )

        # 3. 挑战记录表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mode TEXT,
                content TEXT,
                used_time INTEGER,
                grade TEXT,
                streak INTEGER,
                created_at TEXT
            )
        """
        )

        seed_words(cursor)
        db.commit()


# ==================== 🌱 初始词库 ====================
def seed_words(cursor):
    cursor.execute("SELECT COUNT(*) FROM words")
    count = cursor.fetchone()[0]

    if count > 0:
        return

    basic_words = [
        ("apple", "苹果", "I eat an apple every day."),
        ("run", "跑步", "He runs fast."),
        ("happy", "开心的", "She feels happy."),
        ("computer", "电脑", "This computer is fast."),
        ("learn", "学习", "I learn English."),
        ("challenge", "挑战", "This is a challenge."),
        ("future", "未来", "The future is bright."),
        ("focus", "专注", "Stay focused."),
        ("create", "创造", "We create games."),
        ("power", "力量", "Knowledge is power."),
    ]

    cursor.executemany(
        """
        INSERT INTO words (word, meaning, example)
        VALUES (?, ?, ?)
    """,
        basic_words,
    )


# ==================== 🎯 评分系统 ====================
def calculate_grade(used_time, success, streak):
    if not success or used_time > CHALLENGE_LIMIT:
        return "F", 0

    rules = [
        (3, "SS"),
        (5, "S"),
        (8, "A"),
        (11, "B"),
        (14, "C"),
        (17, "D"),
    ]

    for t, g in rules:
        if used_time <= t:
            return g, streak + 1 if g in ["SS", "S", "A", "B"] else 0

    return "E", 0


# ==================== 🏠 首页 ====================
@app.route("/")
def home():
    return jsonify(
        {
            "message": "🎮 Daily English Word API (Optimized Version)",
            "version": "2.0",
            "features": [
                "Word / Dialog learning with filters",
                "Challenge & Streak scoring system",
                "Paginated Leaderboard",
                "Data management & search",
            ],
        }
    )


# ==================== 📘 学习接口 ====================
@app.route("/api/learn", methods=["GET"])
def learn():
    mode = request.args.get("mode", "word")
    category = request.args.get("category")
    scene = request.args.get("scene")

    db = get_db()
    cursor = db.cursor()

    if mode == "dialog":
        query = "SELECT content, scene FROM dialogs"
        params = []

        if scene:
            query += " WHERE scene = ?"
            params.append(scene)

        query += " ORDER BY RANDOM() LIMIT 1"
        cursor.execute(query, params)
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": "No dialogs found for the given scene"}), 404

        return jsonify(
            {
                "mode": "dialog",
                "content": row["content"],
                "scene": row["scene"],
                "challenge_after": CHALLENGE_TRIGGER,
            }
        )

    elif mode == "word":
        query = "SELECT word, meaning, example, category, level FROM words"
        params = []

        if category:
            query += " WHERE category = ?"
            params.append(category)

        query += " ORDER BY RANDOM() LIMIT 1"
        cursor.execute(query, params)
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": "No words found for the given category"}), 404

        return jsonify(
            {
                "mode": "word",
                "word": row["word"],
                "meaning": row["meaning"],
                "example": row["example"],
                "category": row["category"],
                "level": row["level"],
                "challenge_after": CHALLENGE_TRIGGER,
            }
        )
    else:
        return jsonify({"error": "Invalid learning mode. Use 'word' or 'dialog'."}), 400


# ==================== 🧠 提交挑战 ====================
@app.route("/api/challenge/submit", methods=["POST"])
def submit_challenge():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    try:
        used_time = int(data.get("used_time", CHALLENGE_LIMIT))
        success = bool(data.get("success", False))
        mode = data.get("mode", "word")
        content = data.get("content", "")
        streak = int(data.get("streak", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid data format for parameters"}), 400

    grade, new_streak = calculate_grade(used_time, success, streak)

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO challenges 
            (mode, content, used_time, grade, streak, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                mode,
                content,
                used_time,
                grade,
                new_streak,
                datetime.now().isoformat(),
            ),
        )
        db.commit()
    except Exception as e:
        db.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    return jsonify(
        {
            "success": success,
            "grade": grade,
            "used_time": used_time,
            "streak": new_streak,
        }
    )


# ==================== 🏆 排行榜 (支持分页) ====================
@app.route("/api/leaderboard", methods=["GET"])
def leaderboard():
    try:
        limit = int(request.args.get("limit", 20))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return jsonify({"error": "Invalid limit or offset parameters"}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT mode, content, used_time, grade, streak, created_at
        FROM challenges
        ORDER BY
            CASE grade
                WHEN 'SS' THEN 0
                WHEN 'S' THEN 1
                WHEN 'A' THEN 2
                WHEN 'B' THEN 3
                WHEN 'C' THEN 4
                WHEN 'D' THEN 5
                WHEN 'E' THEN 6
                ELSE 7
            END,
            used_time ASC
        LIMIT ? OFFSET ?
    """,
        (limit, offset),
    )

    rows = cursor.fetchall()

    return jsonify(
        [
            {
                "mode": r["mode"],
                "content": r["content"],
                "time": r["used_time"],
                "grade": r["grade"],
                "streak": r["streak"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]
    )


# ==================== 🔍 单词检索接口 ====================
@app.route("/api/words/search", methods=["GET"])
def search_words():
    keyword = request.args.get("q", "")
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT id, word, meaning, example, level, category 
        FROM words 
        WHERE word LIKE ? OR meaning LIKE ?
        LIMIT 50
    """,
        (f"%{keyword}%", f"%{keyword}%"),
    )

    rows = cursor.fetchall()
    return jsonify(
        [
            {
                "id": r["id"],
                "word": r["word"],
                "meaning": r["meaning"],
                "example": r["example"],
                "level": r["level"],
                "category": r["category"],
            }
            for r in rows
        ]
    )


# ==================== ➕ 添加数据 ====================
@app.route("/api/add", methods=["POST"])
def add_data():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    db = get_db()
    cursor = db.cursor()

    try:
        if "word" in data:
            cursor.execute(
                """
                INSERT INTO words (word, meaning, example, level, category)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    data["word"],
                    data.get("meaning", ""),
                    data.get("example", ""),
                    data.get("level", 1),
                    data.get("category", "general"),
                ),
            )
        elif "dialog" in data:
            cursor.execute(
                """
                INSERT INTO dialogs (content, scene)
                VALUES (?, ?)
            """,
                (data["dialog"], data.get("scene", "daily")),
            )
        else:
            return (
                jsonify(
                    {"error": "Invalid data structure. Provide 'word' or 'dialog'."}
                ),
                400,
            )

        db.commit()
    except Exception as e:
        db.rollback()
        return jsonify({"error": f"Failed to add data: {str(e)}"}), 500

    return jsonify({"message": "✅ Added successfully"}), 201


# ==================== 🚀 启动 ====================
if __name__ == "__main__":
    init_db()
    print("🚀 API running at http://127.0.0.1:5000")
    app.run(debug=True)