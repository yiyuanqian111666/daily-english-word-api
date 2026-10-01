import json
import unittest
from app import app, init_db


class TestFlaskAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """所有测试运行前执行一次：初始化应用与数据库"""
        app.config["TESTING"] = True
        init_db()

    def setUp(self):
        """每个测试用例运行前执行：创建客户端和上下文"""
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = app.test_client()

    def tearDown(self):
        """每个测试用例运行后执行：清理上下文"""
        self.app_context.pop()

    # ==================== 🏠 首页 ====================
    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("message", data)
        self.assertIn("version", data)
        self.assertIn("difficulties", data)
        self.assertIn("features", data)

    # ==================== 📘 学习接口（多难度测试） ====================
    def test_learn_by_difficulty(self):
        # 测试默认 easy 难度
        response = self.client.get("/api/learn")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["difficulty"], "easy")
        self.assertIn("word", data)
        self.assertIn("meaning", data)
        self.assertIn("example", data)
        self.assertIn("grammar_note", data)

    def test_learn_hard_difficulty(self):
        # 测试地道俚语 Hard / Hell 难度
        response = self.client.get("/api/learn?difficulty=hard")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["difficulty"], "hard")
        self.assertIn("word", data)
        self.assertIn("meaning", data)

    def test_learn_invalid_difficulty(self):
        # 测试不存在的难度应当返回 404
        response = self.client.get("/api/learn?difficulty=super_impossible")
        self.assertEqual(response.status_code, 404)

    # ==================== 🧠 提交挑战 ====================
    def test_submit_challenge(self):
        payload = {
            "used_time": 4,
            "success": True,
            "difficulty": "normal",
            "content": "hang out",
            "streak": 2,
        }

        response = self.client.post(
            "/api/challenge/submit",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("grade", data)
        self.assertIn("streak", data)
        self.assertTrue(data["success"])

    def test_submit_challenge_bad_request(self):
        # 传递非法类型参数
        payload = {"used_time": "not-a-number"}
        response = self.client.post(
            "/api/challenge/submit",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    # ==================== 🏆 排行榜（含分页） ====================
    def test_leaderboard(self):
        response = self.client.get("/api/leaderboard?limit=5&offset=0")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertLessEqual(len(data), 5)


if __name__ == "__main__":
    unittest.main()