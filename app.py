from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime
import random

app = Flask(__name__)

DB_NAME = "words.db"
CHALLENGE_LIMIT = 20
CHALLENGE_TRIGGER = 3


# ==================== 📦 数据库工具 ====================
def get_db():
    return sqlite3.connect(DB_NAME)


def init_db():
    with get_db() as conn:
        cursor = conn.cursor()

        # 单词表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                meaning TEXT,
                example TEXT,
                level INTEGER DEFAULT 1,
                category TEXT DEFAULT 'general'
            )
        """)

        # 对话表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dialogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                scene TEXT DEFAULT 'daily'
            )
        """)

        # 挑战记录
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mode TEXT,
                content TEXT,
                used_time INTEGER,
                grade TEXT,
                streak INTEGER,
                created_at TEXT
            )
        """)

        seed_words(cursor)

        conn.commit()


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

    cursor.executemany("""
        INSERT INTO words (word, meaning, example)
        VALUES (?, ?, ?)
    """, basic_words)


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
    return jsonify({
        "message": "🎮 Daily English Word API (Enhanced)",
        "features": [
            "Word / Dialog learning",
            "Auto seed vocabulary",
            "Challenge system",
            "Leaderboard ranking",
            "Better maintainability"
        ]
    })


# ==================== 📘 学习接口 ====================
@app.route("/api/learn")
def learn():
    mode = request.args.get("mode", "word")
    category = request.args.get("category")
    scene = request.args.get("scene")

    with get_db() as conn:
        cursor = conn.cursor()

        if mode == "dialog":
            query = "SELECT content FROM dialogs"
            params = []

            if scene:
                query += " WHERE scene=?"
                params.append(scene)

            query += " ORDER BY RANDOM() LIMIT 1"

            cursor.execute(query, params)
            row = cursor.fetchone()

            content = row[0] if row else "No dialog found"

            return jsonify({
                "mode": "dialog",
                "content": content,
                "challenge_after": CHALLENGE_TRIGGER
            })

        else:
            query = "SELECT word, meaning, example FROM words"
            params = []

            if category:
                query += " WHERE category=?"
                params.append(category)

            query += " ORDER BY RANDOM() LIMIT 1"

            cursor.execute(query, params)
            row = cursor.fetchone()

            if not row:
                return jsonify({"error": "No words found"}), 404

            return jsonify({
                "mode": "word",
                "word": row[0],
                "meaning": row[1],
                "example": row[2],
                "challenge_after": CHALLENGE_TRIGGER
            })


# ==================== 🧠 提交挑战 ====================
@app.route("/api/challenge/submit", methods=["POST"])
def submit_challenge():
    data = request.json or {}

    used_time = int(data.get("used_time", CHALLENGE_LIMIT))
    success = bool(data.get("success", False))
    mode = data.get("mode", "word")
    content = data.get("content", "")
    streak = int(data.get("streak", 0))

    grade, new_streak = calculate_grade(used_time, success, streak)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO challenges 
            (mode, content, used_time, grade, streak, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            mode,
            content,
            used_time,
            grade,
            new_streak,
            datetime.now().isoformat()
        ))

        conn.commit()

    return jsonify({
        "success": success,
        "grade": grade,
        "used_time": used_time,
        "streak": new_streak
    })


# ==================== 🏆 排行榜 ====================
@app.route("/api/leaderboard")
def leaderboard():
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
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
            LIMIT 20
        """)

        rows = cursor.fetchall()

    return jsonify([
        {
            "mode": r[0],
            "content": r[1],
            "time": r[2],
            "grade": r[3],
            "streak": r[4],
            "created_at": r[5]
        } for r in rows
    ])


# ==================== ➕ 添加数据 ====================
@app.route("/api/add", methods=["POST"])
def add_data():
    data = request.json or {}

    with get_db() as conn:
        cursor = conn.cursor()

        if "word" in data:
            cursor.execute("""
                INSERT INTO words (word, meaning, example, level, category)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data["word"],
                data.get("meaning", ""),
                data.get("example", ""),
                data.get("level", 1),
                data.get("category", "general")
            ))

        elif "dialog" in data:
            cursor.execute("""
                INSERT INTO dialogs (content, scene)
                VALUES (?, ?)
            """, (
                data["dialog"],
                data.get("scene", "daily")
            ))

        else:
            return jsonify({"error": "Invalid data"}), 400

        conn.commit()

    return jsonify({"message": "✅ Added successfully"})


# ==================== 🚀 启动 ====================
if __name__ == "__main__":
    init_db()
    print("🚀 API running at http://127.0.0.1:5000")
    app.run(debug=True)