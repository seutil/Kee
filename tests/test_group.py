
import unittest
import typing

from lib.core.data.group import Type, PasswordsGroup
from lib.core.data.item import PasswordItem, CardItem


class TestPasswordsGroup(unittest.TestCase):

    def setUp(self) -> None:
        ...

    def test_type(self) -> None:
        group = PasswordsGroup(name="Passwords", items=[])
        self.assertEqual(group.type(), Type.PASSWORD)

    def test_items(self) -> None:
        group = PasswordsGroup(name="Passwords", items=[])
        self.assertEqual(len(group.items()), 0)

    def test_add_item(self) -> None:
        group = PasswordsGroup(name="Passwords", items=[])
        password = PasswordItem({
            "url": "https://google.com",
            "login": "login",
            "password": "password",
        })
        card = CardItem({
            "number": "1234 5678 1234 1234",
            "cvv": "1234",
        })
        self.assertRaises(TypeError, lambda: group.add_item(card))
        group.add_item(password)
        self.assertEqual(len(group.items()), 1)
        self.assertEqual(password.group(), group)

    def test_remove_item(self) -> None:
        group = PasswordsGroup(name="Passwords", items=[])
        password = PasswordItem({
            "url": "https://google.com",
            "login": "login",
            "password": "password",
        })
        card = CardItem({
            "number": "1234 5678 1234 1234",
            "cvv": "1234",
        })
        self.assertRaises(TypeError, lambda: group.remove_item(card))
        group.add_item(password)
        self.assertEqual(len(group.items()), 1)
        group.remove_item(password)
        self.assertEqual(len(group.items()), 0)
