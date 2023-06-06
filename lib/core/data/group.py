
import typing
from enum import Enum

from .item import PasswordItem, CardItem, IdentityItem

from PyQt5.QtCore import QMetaType


class Type(Enum):
    PASSWORD = "Password"
    IDENTITY = "Identity"
    CARD = "Card"


class GroupInterface(QMetaType):

    def database(self) -> "DatabaseInterface":
        raise NotImpelementedErr("GroupInterface.database is not implemented")

    def name(self, new_name: str = None) -> str | None:
        raise NotImpelementedErr("GroupInterface.name is not implemented")

    def type(self) -> Type:
        raise NotImpelementedErr("GroupInterface.type is not implemented")

    def remove(self) -> None:
        raise NotImpelementedErr("GroupInterface.remove is not implemented")

    def item(self, pos: int) -> "ItemInterface":
        raise NotImpelementedErr("GroupInterface.item is not implemented")

    def items(self) -> typing.List["ItemInterface"]:
        raise NotImpelementedErr("GroupInterface.items is not implemented")

    def add_item(self, item: "ItemInterface") -> None:
        raise NotImpelementedErr("GroupInterface.add_item is not implemented")

    def remove_item(self, item: "ItemInterface") -> None:
        raise NotImpelementedErr("GroupInterface.delete_item is not implemented")


class GroupInterfaceInternal:

    def _set_database(self, database: "DatabaseInterface") -> None:
        raise NotImpelementedErr("GroupInterfaceInternal._set_database is not implemented")


class DatabaseError(Exception):
    ...


class _BaseGroup(GroupInterface, GroupInterfaceInternal):

    def __init__(self, name: str, type_: Type, item_type: "ItemInterface", items: typing.List["ItemInterface"]):
        super(GroupInterface, self).__init__()
        super(GroupInterfaceInternal, self).__init__()
        self._database = None 
        self._name = name
        self._type = type_
        self._item_type = item_type
        self._items = []
        for item in items:
            self.add_item(item)

    def database(self) -> "DatabaseInterface":
        return self._database

    def name(self, new_name: str = None) -> str | None:
        if new_name is None:
            return self._name
        elif new_name == self._name:
            return

        cur = self.database()._cursor
        cur.execute("UPDATE `group` SET name = ? WHERE name = ?", [new_name, self._name])
        self._name = new_name
        self._modify()

    def type(self) -> Type:
        return self._type

    def item(self, pos: int) -> "ItemInterface":
        return self._items[pos]

    def items(self) -> typing.List["ItemInterface"]:
        return self._items

    def add_item(self, item: "ItemInterface") -> None:
        self._check_item_type(item)
        if item.group() is None:
            item._set_group(self)

        self._items.append(item)
        self._modify()

    def remove_item(self, item: "ItemInterface") -> None:
        self._check_item_type(item)
        self.items().remove(item)
        self._modify()

    def remove(self) -> None:
        if not self.database():
            raise DatabaseError("database is not setted")

        cur = self.database()._cursor
        cur.execute("""
            DELETE FROM `group`
            WHERE name = ?
        """, [self.name()])
        del self.database()._groups[self.name()]
        self._modify()

    def _set_database(self, database: "DatabaseInterface") -> None:
        if self.database() is not None:
            raise DatabaseError("database already setted")

        self._database = database

    def _check_item_type(self, item: "ItemInterface") -> None:
        if not isinstance(item, self._item_type):
            raise TypeError(f"invalid item type: {type(item)}")

    def _modify(self) -> None:
        if not self.database():
            return

        self.database()._set_state(self.database()._modified_state)


class PasswordsGroup(_BaseGroup):

    def __init__(self, name: str, items: typing.List[PasswordItem]):
        super().__init__(name, Type.PASSWORD, PasswordItem, items)


class CardsGroup(_BaseGroup):

    def __init__(self, name: str, items: typing.List[CardItem]):
        super().__init__(name, Type.CARD, CardItem, items)


class IdentitiesGroup(_BaseGroup):

    def __init__(self, name: str, items: typing.List[IdentityItem]):
        super().__init__(name, Type.IDENTITY, IdentityItem, items)

