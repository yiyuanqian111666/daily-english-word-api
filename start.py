import os
from app import app  # 假设你在 app.py 中定义了一个 Flask app 对象

if __name__ == "__main__":
    # 设置环境变量
    os.environ["FLASK_APP"] = "app.py"
    os.environ["FLASK_ENV"] = "development"  # 开发环境

    # 启动 Flask 应用
    app.run(debug=True, host="0.0.0.0", port=5000)
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

word_data = {
    "2024-05-01": {"word": "hello", "definition": "a greeting"},
    "2024-05-02": {"word": "world", "definition": "the earth, or the universe"},
    "2024-05-03": {"word": "sun", "definition": "the star at the center of our solar system"}
}

@app.route('/word', methods=['GET'])
def get_word():
    date_str = request.args.get('date')
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')

    word_info = word_data.get(date_str)
    if word_info:
        return jsonify({"date": date_str, "word": word_info["word"], "definition": word_info["definition"]})
    else:
        return jsonify({"error": "No word found for this date"}), 404

@app.route('/word/pronounce', methods=['GET'])
def get_pronounce():
    word = request.args.get('word')
    if not word:
        return jsonify({"error": "Please provide a word parameter"}), 400

    audio_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={word}&tl=en&client=tw-ob"
    
    return jsonify({"word": word, "audio_url": audio_url})

if __name__ == '__main__':
    app.run(debug=True)
