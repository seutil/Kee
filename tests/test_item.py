
import unittest
import typing

from lib.core.data.item import NO_ID, IDError, PasswordItem


class TestPasswordItem(unittest.TestCase):

    def setUp(self) -> None:
        self.test_tbl = [
            {
                "url": "https://site.com",
                "login": "login",
                "password": "password",
            },
        ]

    def test_init(self) -> None:
        for t in self.test_tbl:
            try:
                password = PasswordItem(t)
            except Exception as e:
                self.fail(f"init failed with exception: {e}")

            self.assertEqual(password._id, NO_ID)
            self.assertIsNone(password._group)

    def test_title(self) -> None:
        key = "title"
        for t in self.test_tbl:
            password = PasswordItem(t)
            try:
                password.entry(key, "")
                password.entry(key, "title")
            except Exception as e:
                self.fail(f"title failed with exception: {e}")

    def test_url(self) -> None:
        key = "url"
        for t in self.test_tbl:
            password = PasswordItem(t)
            self.assertRaises(ValueError, lambda: password.entry(key, ""))
            try:
                password.entry(key, "https://google.com")
            except Exception as e:
                self.fail(f"url failed with exception: {e}")

    def test_login(self) -> None:
        key = "login"
        for t in self.test_tbl:
            password = PasswordItem(t)
            self.assertRaises(ValueError, lambda: password.entry(key, ""))
            try:
                password.entry(key, "login")
            except Exception as e:
                self.fail(f"login failed with exception: {e}")

    def test_email(self) -> None:
        key = "email"
        for t in self.test_tbl:
            password = PasswordItem(t)
            self.assertRaises(ValueError, lambda: password.entry(key, "invalid"))
            try:
                password.entry(key, "email@mail.net")
            except Exception as e:
                self.fail(f"email failed with exception: {e}")

    def test_password(self) -> None:
        key = "password"
        for t in self.test_tbl:
            password = PasswordItem(t)
            self.assertRaises(ValueError, lambda: password.entry(key, ""))
            try:
                password.entry(key, "password")
            except Exception as e:
                self.fail(f"email failed with exception: {e}")

    def test_notes(self) -> None:
        key = "notes"
        for t in self.test_tbl:
            password = PasswordItem(t)
            try:
                password.entry(key, "")
                password.entry(key, "notes")
            except Exception as e:
                self.fail(f"email failed with exception: {e}")

    def test_delete(self) -> None:
        for t in self.test_tbl:
            password = PasswordItem(t)
            self.assertRaises(IDError, lambda: password.delete())


if __name__ == "__main__":
    unittest.main()

