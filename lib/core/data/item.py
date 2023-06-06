
import typing
import re
import phonenumbers
import validators
from collections import defaultdict

from PyQt5.QtCore import QMetaType


NO_ID = -1


class ItemInterface(QMetaType):

    def group(self) -> "GroupInterface":
        raise NotImpelementedErr("ItemInterface.group is not implemented")

    def data(self) -> typing.Dict[str, typing.Any]:
        raise NotImpelementedErr("ItemInterface.data is not implemented")

    def entry(self, k: str, v: typing.Any = None) -> typing.Any | None:
        raise NotImpelementedErr("ItemInterface.entry is not implemented")

    def delete(self) -> None:
        raise NotImpelementedErr("ItemInterface.delete is not implemented")


class ItemInterfaceInternal:

    def _set_group(self, group: "GroupInterface") -> None:
        raise NotImpelementedErr("ItemInterfaceInternal._set_group is not implemented")

    def _set_id(self, id: int) -> None:
        raise NotImpelementedErr("ItemInterfaceInternal._set_id is not implemented")


class GroupError(Exception):
    ...


class IDError(Exception):
    ...


class _BaseItem(ItemInterface, ItemInterfaceInternal):
    
    def __init__(self, required_keys: typing.List[str], keys: typing.Dict[str, typing.Callable], data: typing.Dict[str, str]):
        super(ItemInterface, self).__init__()
        super(ItemInterfaceInternal, self).__init__()
        self._group = None
        self._id = NO_ID
        self._keys = keys
        self._data = defaultdict(str)
        if not set(required_keys) <= set(data.keys()):
            raise ValueError("data required key not specified")

        for k, v in data.items():
            self.entry(k, v)

    def group(self) -> "GroupInterface":
        return self._group

    def data(self) -> typing.Dict[str, str]:
        return self._data

    def entry(self, k: str, v: str = None) -> str | None:
        if k not in self._keys.keys():
            raise KeyError(f"invalid key: {k}")

        if v is None:
            return self._data[k]

        if not self._keys[k](v):
            raise ValueError(f"invalid value \"{v}\" for key \"{k}\"")

        self._data[k] = v
        self._modify()

    def delete(self) -> None:
        if self._id == NO_ID:
            raise IDError("id has not been specified")
        elif not (self.group() and self.group().database()):
            raise GroupError("group or database has not been setted")

        cur = self.group().database()._cursor
        cur.execute("""
            DELETE FROM item
            WHERE id = ?
        """, [self._id])

    def _set_group(self, group: "GroupInterface") -> None:
        if self.group():
            raise GroupError("group already setted")

        self._group = group
        self._modify()

    def _set_id(self, id_: int) -> None:
        if self._id != NO_ID:
            raise IDError("group ID already setted")

        self._id = id_

    def _modify(self) -> None:
        if not (self.group() and self.group().database()):
            return

        self.group().database()._set_state(self.group().database()._modified_state)


class PasswordItem(_BaseItem):

    def __init__(self, data: typing.Dict[str, str]):
        super().__init__(
            required_keys=["url", "login", "password"],
            keys={
                "title": self.__check_title,
                "url": self.__check_url,
                "login": self.__check_login,
                "email": self.__check_email,
                "password": self.__check_password,
                "notes": self.__check_notes,
            },
            data=data,
        )

    def __check_title(self, title) -> bool:
        return True

    def __check_url(self, url) -> bool:
        return False if url == "" else validators.url(url)

    def __check_login(self, login) -> bool:
        return login != ""

    def __check_email(self, email) -> bool:
        return validators.email(email) is True

    def __check_password(self, password) -> bool:
        return password != ""

    def __check_notes(self, note) -> bool:
        return True


class CardItem(_BaseItem):
    
    def __init__(self, data: typing.Dict[str, str]):
        super().__init__(
            required_keys=["number", "cvv"],
            keys={
                "title": self.__check_title,
                "number": self.__check_number,
                "cvv": self.__check_cvv,
                "expiration": self.__check_expiration,
                "holder": self.__check_holder,
                "notes": self.__check_notes,
            },
            data=data,
        )

    def __check_title(self, title) -> bool:
        return True

    def __check_number(self, number: str) -> bool:
        return re.match("\d{4} \d{4} \d{4} \d{4}", number)

    def __check_cvv(self, cvv: str) -> bool:
        return re.match("\d{3,4}", cvv)

    def __check_expiration(self, expiration: str) -> bool:
        return True if not expiration else re.match("\d{2}/\d{2}", expiration)

    def __check_holder(self, holder: str) -> bool:
        return True

    def __check_notes(self, notes: str) -> bool:
        return True


class IdentityItem(_BaseItem):
 
    def __init__(self, data: typing.Dict[str, str]):
        super().__init__(
            required_keys=["full_name"],
            keys={
                "title": self.__check_title,
                "full_name": self.__check_full_name,
                "phone": self.__check_phone,
                "email": self.__check_email,
                "notes": self.__check_notes,
            },
            data=data,
        )

    def __check_title(self, title: str) -> bool:
        return True

    def __check_full_name(self, full_name: str) -> bool:
        return full_name != ""

    def __check_phone(self, phone: str) -> bool:
        return True if not phone else phonenumbers.is_valid_number(phone)

    def __check_email(self, email: str) -> bool:
        return True if not email else re.match("[^@]+@[^@]+\.[^@]+", email)

    def __check_notes(self, notes: str) -> bool:
        return True
