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

    # 单词表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            meaning TEXT NOT NULL,
            example TEXT
        )
    """)

    # 场景对话表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dialogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        )
    """)

    # 挑战记录表（可选，但推荐）
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
        "message": "✅ Daily English Word API is running",
        "learn_modes": ["word", "dialog"],
        "endpoints": {
            "/api/today": "Get today's word",
            "/api/random": "Get random word",
            "/api/learn?mode=word|dialog": "Learn content",
            "/api/challenge/submit": "Submit challenge result (POST)",
            "/api/add": "Add word (POST)",
            "/api/list": "List words"
        }
    })


# ==================== 📅 今日单词 ====================
@app.route("/api/today")
def today_word():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT word, meaning, example FROM words")
    words = cursor.fetchall()
    conn.close()

    if not words:
        return jsonify({"error": "No words in database"}), 404

    index = date.today().toordinal() % len(words)
    word, meaning, example = words[index]

    return jsonify({
        "date": str(date.today()),
        "word": word,
        "meaning": meaning,
        "example": example
    })


# ==================== 🎲 随机单词 ====================
@app.route("/api/random")
def random_word():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT word, meaning, example FROM words")
    words = cursor.fetchall()
    conn.close()

    if not words:
        return jsonify({"error": "No words found"}), 404

    word, meaning, example = random.choice(words)
    return jsonify({
        "word": word,
        "meaning": meaning,
        "example": example
    })


# ==================== 📘 学习模式（核心升级） ====================
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


# ==================== 🧠 挑战提交 + 评级 ====================
@app.route("/api/challenge/submit", methods=["POST"])
def submit_challenge():
    data = request.json
    used_time = data.get("used_time")  # 秒
    success = data.get("success")      # true / false
    mode = data.get("mode", "word")

    if success is False:
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
        "result": "pass" if success else "fail",
        "grade": grade,
        "time_limit": 20
    })


# ==================== ➕ 添加单词 ====================
@app.route("/api/add", methods=["POST"])
def add_word():
    data = request.json
    if not data or "word" not in data or "meaning" not in data:
        return jsonify({"error": "Missing word or meaning"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO words (word, meaning, example) VALUES (?, ?, ?)",
        (data["word"], data["meaning"], data.get("example", ""))
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Word added successfully"})


# ==================== 📃 单词列表 ====================
@app.route("/api/list")
def list_words():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, word, meaning, example FROM words ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    return jsonify([
        {"id": r[0], "word": r[1], "meaning": r[2], "example": r[3]}
        for r in rows
    ])


if __name__ == "__main__":
    init_db()
    print("🚀 API running at http://127.0.0.1:5000")
    app.run(debug=True)
