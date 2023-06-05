
import unittest

from lib.crypto.encoder import Base32, Base64, ID


class TestBase32(unittest.TestCase):

    def setUp(self) -> None:
        self.encoder = Base32
        self.test_tbl = [
            {
                "data": "xktG63JMni",
                "expect": "PBVXIRZWGNFE23TJ",
            },
            {
                "data": "ENXsnvLHBb",
                "expect": "IVHFQ43OOZGEQQTC",
            },
            {
                "data": "",
                "expect": "",
            },
        ]

    def test_encode(self) -> None:
        for t in self.test_tbl:
            self.assertEqual(self.encoder.encode(t["data"].encode()), t["expect"].encode())

    def test_decode(self) -> None:
        for t in self.test_tbl:
            self.assertEqual(self.encoder.decode(t["expect"].encode()), t["data"].encode())

    def test_id(self) -> None:
        self.assertEqual(self.encoder.id(), ID.BASE32)


class TestBase64(unittest.TestCase):

    def setUp(self) -> None:
        self.encoder = Base64
        self.test_tbl = [
            {
                "data": "xktG63JMni",
                "expect": "eGt0RzYzSk1uaQ==",
            },
            {
                "data": "ENXsnvLHBb",
                "expect": "RU5Yc252TEhCYg==",
            },
            {
                "data": "",
                "expect": "",
            },
        ]

    def test_encode(self) -> None:
        for t in self.test_tbl:
            self.assertEqual(self.encoder.encode(t["data"].encode()), t["expect"].encode())

    def test_decode(self) -> None:
        for t in self.test_tbl:
            self.assertEqual(self.encoder.decode(t["expect"].encode()), t["data"].encode())

    def test_id(self) -> None:
        self.assertEqual(self.encoder.id(), ID.BASE64)


if __name__ == "__main__":
    unittest.main()