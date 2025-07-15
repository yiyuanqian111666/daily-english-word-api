from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# 🧠 词库数据（可改为从 JSON 读取）
word_data = {
    "2024-05-01": {"word": "hello", "definition": "a greeting"},
    "2024-05-02": {"word": "world", "definition": "the earth, or the universe"},
    "2024-05-03": {"word": "sun", "definition": "the star at the center of our solar system"}
}

# ✅ API 1: 根据日期返回单词
@app.route('/word', methods=['GET'])
def get_word():
    date_str = request.args.get('date')
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')

    word_info = word_data.get(date_str)
    if word_info:
        return jsonify({
            "date": date_str,
            "word": word_info["word"],
            "definition": word_info["definition"]
        })
    else:
        return jsonify({"error": "No word found for this date"}), 404

# ✅ API 2: 获取发音音频链接
@app.route('/word/pronounce', methods=['GET'])
def get_pronounce():
    word = request.args.get('word')
    if not word:
        return jsonify({"error": "Please provide a word parameter"}), 400

    audio_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={word}&tl=en&client=tw-ob"
    return jsonify({"word": word, "audio_url": audio_url})

# ✅ 启动服务
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
