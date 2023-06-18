
from enum import Enum
from Crypto.Hash import SHA256 as s256, SHA512 as s512, MD5 as md5


class ID(Enum):
    SHA256 = "SHA256"
    SHA512 = "SHA512"
    MD5 = "MD5"


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
        case ID.MD5.value:
            return MD5
        case _:
            return None

class MD5(HashInterface):

    @staticmethod
    def hash(*data: bytes) -> bytes:
        h = md5.new()
        for d in data:
            h.update(d)

        return h.digest()

    @staticmethod
    def id() -> ID:
        return ID.MD5

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
