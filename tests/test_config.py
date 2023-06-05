
import unittest
import yaml

from lib.core.config import Config


class TestConfig(unittest.TestCase):

    def test_singleton(self) -> None:
        self.assertIsNotNone(Config())
        self.assertIs(Config(), Config())


if __name__ == "__main__":
    unittest.main()
