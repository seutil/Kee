
import typing
from enum import Enum

from PyQt5.QtCore import QMetaType


SALT_LENGTH = 32

class Status:
    CLOSED = "Closed"
    OPENED = "Opened"
    MODIFIED = "Modified"


class ClosedError(Exception):
    ...


class DatabaseInterface(QMetaType):

    def location(self) -> str:
        raise NotImpelementedErr("DatabaseInterface.location is not implemented")

    def name(self, new_name: str = None) -> str | None:
        raise NotImpelementedErr("DatabaseInterface.name is not implemented")

    def status(self) -> Status:
        raise NotImpelementedErr("DatabaseInterface.status is not implemented")

    def open(self, master_key: str) -> None:
        raise NotImpelementedErr("DatabaseInterface.open is not implemented")

    def close(self) -> None:
        raise NotImpelementedErr("DatabaseInterface.close is not implemented")

    def save(self) -> None:
        raise NotImpelementedErr("DatabaseInterface.save is not implemented")

    def group(self, name: str) -> "GroupInterface":
        raise NotImpelementedErr("DatabaseInterface.group is not implemented")

    def groups(self) -> typing.List["GroupInterface"]:
        raise NotImpelementedErr("DatabaseInterface.groups is not implemented")

    def add_group(self, group: "GroupInterface") -> None:
        raise NotImpelementedErr("DatabaseInterface.add_group is not implemented")

    def remove(self) -> None:
        raise NotImpelementedErr("DatabaseInterface.remove is not implemented")

    def remove_group(self, group: "GroupInterface") -> None:
        raise NotImpelementedErr("DatabaseInterface.delete_group is not implemented")
