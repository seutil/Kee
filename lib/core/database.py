
import typing
from enum import Enum

from PyQt5.QtCore import QMetaType

from lib.crypto.hasher import HashInterface
from lib.crypto.cipher import CipherInterface
from lib.crypto.encoder import EncoderInterface


SALT_LENGTH = 32

class Status(Enum):
    CLOSED = "Closed"
    OPENED = "Opened"
    MODIFIED = "Modified"


class ClosedError(Exception):
    ...


class DatabaseInterface(QMetaType):

    def location(self) -> str:
        raise NotImplementedError("DatabaseInterface.location is not implemented")

    def name(self, new_name: str = None) -> str | None:
        raise NotImplementedError("DatabaseInterface.name is not implemented")

    def status(self) -> Status:
        raise NotImplementedError("DatabaseInterface.status is not implemented")

    def master_key(self, new_master_key: str = None) -> str | None:
        raise NotImplementedError("DatabaseInterface.master_key is not implemented")

    def hasher(self, new_hasher: HashInterface = None) -> HashInterface | None:
        raise NotImplementedError("DatabaseInterface.hasher is not implemented")

    def cipher(self, new_cipher: CipherInterface = None) -> CipherInterface | None:
        raise NotImplementedError("DatabaseInterface.cipher is not implemented")

    def encoder(self, new_encoder: EncoderInterface = None) -> EncoderInterface | None:
        raise NotImplementedError("DatabaseInterface.encoder is not implemented")

    def open(self, master_key: str) -> None:
        raise NotImplementedError("DatabaseInterface.open is not implemented")

    def close(self) -> None:
        raise NotImplementedError("DatabaseInterface.close is not implemented")

    def save(self) -> None:
        raise NotImplementedError("DatabaseInterface.save is not implemented")

    def group(self, name: str) -> "GroupInterface":
        raise NotImplementedError("DatabaseInterface.group is not implemented")

    def groups(self) -> typing.List["GroupInterface"]:
        raise NotImplementedError("DatabaseInterface.groups is not implemented")

    def add_group(self, group: "GroupInterface") -> None:
        raise NotImplementedError("DatabaseInterface.add_group is not implemented")

    def remove(self) -> None:
        raise NotImplementedError("DatabaseInterface.remove is not implemented")

    def remove_group(self, group: "GroupInterface") -> None:
        raise NotImplementedError("DatabaseInterface.delete_group is not implemented")
