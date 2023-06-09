
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

    def _set_group(self, group: "GroupInterface") -> None:
        raise NotImpelementedErr("ItemInterfaceInternal._set_group is not implemented")

    def _set_id(self, id: int) -> None:
        raise NotImpelementedErr("ItemInterface._set_id is not implemented")


class GroupError(Exception):
    ...


class IDError(Exception):
    ...


class _BaseItem(ItemInterface):
    
    def __init__(self, required_keys: typing.List[str], keys: typing.Dict[str, typing.Callable], data: typing.Dict[str, str]):
        super().__init__()
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
                "title": PasswordItem.check_title,
                "url": PasswordItem.check_url,
                "login": PasswordItem.check_login,
                "email": PasswordItem.check_email,
                "password": PasswordItem.check_password,
                "notes": PasswordItem.check_notes,
            },
            data=data,
        )

    def check_title(title) -> bool:
        return True

    def check_url(url) -> bool:
        return False if url == "" else validators.url(url)

    def check_login(login) -> bool:
        return login != ""

    def check_email(email) -> bool:
        return True if not email else validators.email(email) is True

    def check_password(password) -> bool:
        return password != ""

    def check_notes(note) -> bool:
        return True


class CardItem(_BaseItem):
    
    def __init__(self, data: typing.Dict[str, str]):
        super().__init__(
            required_keys=["number", "cvv"],
            keys={
                "title": CardItem.check_title,
                "number": CardItem.check_number,
                "cvv": CardItem.check_cvv,
                "expiration": CardItem.check_expiration,
                "holder": CardItem.check_holder,
                "notes": CardItem.check_notes,
            },
            data=data,
        )

    def check_title(title) -> bool:
        return True

    def check_number(number: str) -> bool:
        return re.match("\d{4} \d{4} \d{4} \d{4}", number)

    def check_cvv(cvv: str) -> bool:
        return re.match("\d{3,4}", cvv)

    def check_expiration(expiration: str) -> bool:
        return True if not expiration else re.match("\d{2}/\d{2}", expiration)

    def check_holder(holder: str) -> bool:
        return True

    def check_notes(notes: str) -> bool:
        return True


class IdentityItem(_BaseItem):
 
    def __init__(self, data: typing.Dict[str, str]):
        super().__init__(
            required_keys=["full_name"],
            keys={
                "title": IdentityItem.check_title,
                "full_name": IdentityItem.check_full_name,
                "phone": IdentityItem.check_phone,
                "email": IdentityItem.check_email,
                "notes": IdentityItem.check_notes,
            },
            data=data,
        )

    def check_title(title: str) -> bool:
        return True

    def check_full_name(full_name: str) -> bool:
        return full_name != ""

    def check_phone(phone: str) -> bool:
        if not phone:
            return True

        ph = phonenumbers.parse(phone)
        return phonenumbers.is_valid_number(ph)

    def check_email(email: str) -> bool:
        return True if not email else validators.email(email) is True

    def check_notes(notes: str) -> bool:
        return True
