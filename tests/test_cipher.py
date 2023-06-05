
import unittest
from lib.crypto.cipher import AES_CBC


class TestAES_CBC(unittest.TestCase):

    def setUp(self) -> None:
        self.cipher = AES_CBC
        self.test_tbl = [
            {
                "data": "rg4evpAlNk",
                "key": "MrQgccPorz",
                "salt": "UsApwgjMcz",
            },
        ]

    def test_cipher_cycle(self) -> None:
        for t in self.test_tbl:
            key, salt = t["key"].encode(), t["salt"].encode()
            encrypted = self.cipher.encrypt(t["data"].encode(), key, salt)
            decrypted = self.cipher.decrypt(encrypted, key, salt)
            self.assertEqual(decrypted, t["data"].encode())


if __name__ == "__main__":
    unittest.main()
