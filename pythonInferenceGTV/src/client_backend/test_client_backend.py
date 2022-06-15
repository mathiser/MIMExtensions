import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from client_backend.client_backend import ClientBackend

class TestClientBackend(unittest.TestCase):
    def setUp(self) -> None:
        self.cb = ClientBackend("https://httpbin.org/", verify=True)

    def test_get(self):
        res = self.cb.get("/get")
        self.assertEqual(res.status_code, 200)

    def test_post(self):
        res = self.cb.post("/post", {}, {})
        self.assertEqual(res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
