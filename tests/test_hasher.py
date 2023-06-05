
import unittest
from lib.crypto.hasher import from_id, ID, SHA256, SHA512


class TestFactoryFunction(unittest.TestCase):

    def test_sha256(self) -> None:
        self.assertEqual(from_id("SHA256"), SHA256)

    def test_sha512(self) -> None:
        self.assertEqual(from_id("SHA512"), SHA512)


class TestSHA256(unittest.TestCase):

    def setUp(self) -> None:
        self.hasher = SHA256
        self.test_tbl = [
            {
                "data": "test1",
                "expect": "1b4f0e9851971998e732078544c96b36c3d01cedf7caa332359d6f1d83567014",
            },
            {
                "data": "test2",
                "expect": "60303ae22b998861bce3b28f33eec1be758a213c86c93c076dbe9f558c11c752",
            },
            {
                "data": "test3",
                "expect": "fd61a03af4f77d870fc21e05e7e80678095c92d808cfb3b5c279ee04c74aca13",
            },
        ]

    def test_hash(self) -> None:
        for t in self.test_tbl:
            self.assertEqual(self.hasher.hash(t["data"].encode()).hex(), t["expect"])

    def test_id(self) -> None:
        self.assertEqual(self.hasher.id(), ID.SHA256)


class TestSHA512(unittest.TestCase):

    def setUp(self) -> None:
        self.hash = SHA512
        self.test_tbl = [
            {
                "data": "test1",
                "expect": "b16ed7d24b3ecbd4164dcdad374e08c0ab7518aa07f9d3683f34c2b3c67a15830268cb4a56c1ff6f54c8e54a795f5b87c08668b51f82d0093f7baee7d2981181",
            },
            {
                "data": "test2",
                "expect": "6d201beeefb589b08ef0672dac82353d0cbd9ad99e1642c83a1601f3d647bcca003257b5e8f31bdc1d73fbec84fb085c79d6e2677b7ff927e823a54e789140d9",
            },
            {
                "data": "test3",
                "expect": "cb872de2b8d2509c54344435ce9cb43b4faa27f97d486ff4de35af03e4919fb4ec53267caf8def06ef177d69fe0abab3c12fbdc2f267d895fd07c36a62bff4bf",
            },
        ]

    def test_hash(self) -> None:
        for t in self.test_tbl:
            self.assertEqual(self.hash.hash(t["data"].encode()).hex(), t["expect"])

    def test_id(self) -> None:
        self.assertEqual(self.hash.id(), ID.SHA512)


if __name__ == "__main__":
    unittest.main()