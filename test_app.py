import unittest
import json
from app import app, init_db

class TestFlaskAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # 初始化数据库
        init_db()
        app.testing = True
        cls.client = app.test_client()

    # ==================== 🏠 首页 ====================
    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("message", data)
        self.assertIn("features", data)

    # ==================== 📘 学习接口 ====================
    def test_learn_word(self):
        response = self.client.get("/api/learn?mode=word")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("word", data)
        self.assertIn("meaning", data)
        self.assertIn("example", data)

    def test_learn_dialog(self):
        response = self.client.get("/api/learn?mode=dialog")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("content", data)

    # ==================== 🧠 提交挑战 ====================
    def test_submit_challenge(self):
        payload = {
            "used_time": 5,
            "success": True,
            "mode": "word",
            "content": "test",
            "streak": 1
        }

        response = self.client.post(
            "/api/challenge/submit",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("grade", data)
        self.assertIn("streak", data)

    # ==================== 🏆 排行榜 ====================
    def test_leaderboard(self):
        response = self.client.get("/api/leaderboard")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIsInstance(data, list)

    # ==================== ➕ 添加数据 ====================
    def test_add_word(self):
        payload = {
            "word": "testword",
            "meaning": "测试",
            "example": "This is a test."
        }

        response = self.client.post(
            "/api/add",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("message", data)


if __name__ == "__main__":
    unittest.main()