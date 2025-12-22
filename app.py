from flask import Flask, jsonify, request
import sqlite3
from datetime import date, datetime
import random

app = Flask(__name__)
DB_NAME = "words.db"


# ==================== 📦 数据库初始化 ====================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            meaning TEXT NOT NULL,
            example TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dialogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mode TEXT,
            used_time INTEGER,
            grade TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# ==================== 🏠 首页 ====================
@app.route("/")
def home():
    return jsonify({
        "message": "✅ Daily English Word API running",
        "modes": ["word", "dialog"],
        "endpoints": [
            "/api/learn?mode=word",
            "/api/learn?mode=dialog",
            "/api/challenge/submit",
            "/api/leaderboard"
        ]
    })


# ==================== 📘 学习接口 ====================
@app.route("/api/learn")
def learn():
    mode = request.args.get("mode", "word")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if mode == "dialog":
        cursor.execute("SELECT content FROM dialogs ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return jsonify({
            "mode": "dialog",
            "content": row[0] if row else "No dialog data"
        })

    cursor.execute("SELECT word FROM words ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return jsonify({
        "mode": "word",
        "content": row[0] if row else "No word data"
    })


# ==================== 🧠 提交挑战（20 秒 + 评级） ====================
@app.route("/api/challenge/submit", methods=["POST"])
def submit_challenge():
    data = request.json
    used_time = int(data.get("used_time", 20))
    success = bool(data.get("success", False))
    mode = data.get("mode", "word")

    if not success:
        grade = "F"
    elif used_time <= 5:
        grade = "S"
    elif used_time <= 8:
        grade = "A"
    elif used_time <= 11:
        grade = "B"
    elif used_time <= 14:
        grade = "C"
    elif used_time <= 17:
        grade = "D"
    else:
        grade = "E"

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO challenges (mode, used_time, grade, created_at) VALUES (?, ?, ?, ?)",
        (mode, used_time, grade, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    return jsonify({
        "success": success,
        "used_time": used_time,
        "grade": grade,
        "limit": 20
    })


# ==================== 🏆 挑战排行榜 ====================
@app.route("/api/leaderboard")
def leaderboard():
    mode = request.args.get("mode")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = """
        SELECT mode, used_time, grade, created_at
        FROM challenges
    """
    params = []

    if mode:
        query += " WHERE mode = ?"
        params.append(mode)

    query += """
        ORDER BY
            CASE grade
                WHEN 'S' THEN 1
                WHEN 'A' THEN 2
                WHEN 'B' THEN 3
                WHEN 'C' THEN 4
                WHEN 'D' THEN 5
                WHEN 'E' THEN 6
                ELSE 7
            END,
            used_time ASC,
            created_at DESC
        LIMIT 20
    """

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return jsonify([
        {
            "mode": r[0],
            "used_time": r[1],
            "grade": r[2],
            "time": r[3]
        } for r in rows
    ])


# ==================== ➕ 添加单词 / 对话 ====================
@app.route("/api/add", methods=["POST"])
def add_data():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if "word" in data:
        cursor.execute(
            "INSERT INTO words (word, meaning, example) VALUES (?, ?, ?)",
            (data["word"], data.get("meaning", ""), data.get("example", ""))
        )
    elif "dialog" in data:
        cursor.execute(
            "INSERT INTO dialogs (content) VALUES (?)",
            (data["dialog"],)
        )

    conn.commit()
    conn.close()
    return jsonify({"message": "Added successfully"})


# ==================== 🚀 启动 ====================
if __name__ == "__main__":
    init_db()
    print("🚀 API running at http://127.0.0.1:5000")
    app.run(debug=True)
