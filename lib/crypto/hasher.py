
from enum import Enum
from Crypto.Hash import SHA256 as s256, SHA512 as s512


class ID(Enum):
    SHA256 = "SHA256"
    SHA512 = "SHA512"


class HashInterface:

    @staticmethod
    def hash(*data: bytes) -> bytes:
        raise NotImpelementedErr("HashInterface.hash is not implemented")

    @staticmethod
    def id() -> ID:
        raise NotImpelementedErr("HashInterface.id is not implemented")


def from_id(id_: str) -> HashInterface:
    match id_:
        case ID.SHA256.value:
            return SHA256
        case ID.SHA512.value:
            return SHA512
        case _:
            return None


class SHA256(HashInterface):

    @staticmethod
    def hash(*data: bytes) -> bytes:
        h = s256.new()
        for d in data:
            h.update(d)

        return h.digest()

    @staticmethod
    def id() -> ID:
        return ID.SHA256


class SHA512(HashInterface):

    @staticmethod
    def hash(*data: bytes) -> bytes:
        h = s512.new()
        for d in data:
            h.update(d)

        return h.digest()

    @staticmethod
    def id() -> ID:
        return ID.SHA512
