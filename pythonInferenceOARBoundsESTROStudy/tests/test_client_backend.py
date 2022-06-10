import os
import unittest

from .client_backend import ClientBackend


class TestClientBackend(unittest.TestCase):
    def setUp(self) -> None:
        self.cb = ClientBackend("https://httpbin.org/", cert_path=True)

    def test_get(self):
        res = self.cb.get("/get")
        self.assertEqual(res.status_code, 200)

    def test_post(self):
        res = self.cb.post("/post", {}, {})
        self.assertEqual(res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
