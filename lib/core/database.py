
import typing
from enum import Enum
from PyQt5.QtCore import QMetaType

from lib.crypto.hasher import HashInterface
from lib.crypto.cipher import CipherInterface
from lib.crypto.encoder import EncoderInterface


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

    def master_key(self, new_master_key: str = None) -> str | None:
        raise NotImpelementedErr("DatabaseInterface.master_key is not implemented")

    def hasher(self, new_hasher: HashInterface = None) -> HashInterface | None:
        raise NotImpelementedErr("DatabaseInterface.hasher is not implemented")

    def cipher(self, new_cipher: CipherInterface = None) -> CipherInterface | None:
        raise NotImpelementedErr("DatabaseInterface.cipher is not implemented")

    def encoder(self, new_encoder: EncoderInterface = None) -> EncoderInterface | None:
        raise NotImpelementedErr("DatabaseInterface.encoder is not implemented")

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
