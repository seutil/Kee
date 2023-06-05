
import os
import typing
import unittest
import tempfile

from lib.core.database import Status
from lib.core.sqlite_database import SQLiteDatabase
from lib.core.data.item import PasswordItem
from lib.core.data.group import PasswordsGroup

from lib.crypto import hasher
from lib.crypto import cipher
from lib.crypto import encoder
from lib.crypto import generate


class TestSQLite(unittest.TestCase):
    
    def setUp(self) -> None:
        self.test_tbl = [
            {
                "name": "Personal",
                "master_key": "master-key",
                "hasher": hasher.SHA256,
                "cipher": cipher.AES_CBC,
                "encoder": encoder.Base64,
            },
        ]

    def test_create(self) -> None:
        for t in self.test_tbl:
            db = self.__create_temp_db(t)
            res = db._meta
            self.assertEqual(db.status(), Status.OPENED)
            self.assertEqual(res["name"], t["name"])
            self.assertIsInstance(res["master_key_hash"], bytes)
            self.assertIsInstance(res["hash_salt"], bytes)
            self.assertIsInstance(res["cipher_salt"], bytes)
            self.assertEqual(res["master_key_hash"], t["encoder"].encode(t["hasher"].hash(t["master_key"].encode(), res["hash_salt"])))
            self.assertEqual(res["hasher"].id().value, t["hasher"].id().value)
            self.assertEqual(res["cipher"].id().value, t["cipher"].id().value)
            self.assertEqual(res["encoder"].id().value, t["encoder"].id().value)

    def test_name(self) -> None:
        for t in self.test_tbl:
            db = self.__create_temp_db(t)
            self.assertEqual(db.name(), t["name"])
            db.close()

    def test_close(self) -> None:
        for t in self.test_tbl:
            db = self.__create_temp_db(t)
            db.close()
            self.assertEqual(db.status(), Status.CLOSED)

    def test_open(self) -> None:
        for t in self.test_tbl:
            db = self.__create_temp_db(t)
            db.close()
            db.open(t["master_key"])
            self.assertEqual(db.status(), Status.OPENED)
            db.close()

    def test_save(self) -> None:
        for t in self.test_tbl:
            db = self.__create_temp_db(t)
            password = PasswordItem({
                "url": "https://google.com",
                "login": "login",
                "password": "password",
            })
            group = PasswordsGroup(name="Passwords", items=[password])
            db.add_group(group)
            self.assertEqual(db.status(), Status.MODIFIED)
            db.save()
            db.close()
            db.open(t["master_key"])
            self.assertEqual(db.status(), Status.OPENED)
            self.assertEqual(len(db.groups()), 1)
            self.assertEqual(db.group(group.name()).name(), group.name())
            self.assertEqual(group.item(0), password)
            self.assertEqual(len(group.items()), 1)
            self.assertEqual(password._id, 1)

    def test_add_group(self) -> None:
        for t in self.test_tbl:
            db = self.__create_temp_db(t)
            group = PasswordsGroup(name="Passwords", items=[])
            try:
                db.add_group(group)
            except Exception as e:
                self.fail(f"add_group failed with exception: {e}")

            self.assertEqual(db.status(), Status.MODIFIED)
            self.assertEqual(db.group(group.name()), group)
            self.assertEqual(len(db.groups()), 1)
            db.close()

    def test_remove_group(self) -> None:
        for t in self.test_tbl:
            db = self.__create_temp_db(t)
            group = PasswordsGroup(name="Passwords", items=[])
            self.assertRaises(ValueError, lambda: db.remove_group(group))
            db.add_group(group)
            db.remove_group(group)
            self.assertEqual(db.status(), Status.MODIFIED)
            self.assertEqual(len(db.groups()), 0)

    def test_remove(self) -> None:
        for t in self.test_tbl:
            db = self.__create_temp_db(t)
            location = db.location()
            db.remove()
            self.assertFalse(os.path.exists(location))

    def __create_temp_db(self, data: typing.Dict[str, str]) -> SQLiteDatabase:
        return SQLiteDatabase.create(location=":memory:", **data)

    def __create_temp_db(self, data: typing.Dict[str, str]) -> SQLiteDatabase:
        return SQLiteDatabase.create(
            location=os.path.join(tempfile.gettempdir(), generate.string(10)),
            **data
        )

if __name__ == "__main__":
    unittest.main()
