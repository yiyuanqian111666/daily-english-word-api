import unittest
from fastapi.testclient import TestClient
from app import app, WORDS, MTL_DATA

client = TestClient(app)

class TestFastAPI(unittest.TestCase):
    def test_root_endpoint(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("/word", response.json()["endpoints"])

    def test_word_endpoint(self):
        response = client.get("/word")
        self.assertEqual(response.status_code, 200)
        self.assertIn("word", response.json())
        self.assertIn("meaning", response.json())

    def test_mtl_endpoint(self):
        response = client.get("/mtl")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), MTL_DATA)

if __name__ == "__main__":
    unittest.main()
