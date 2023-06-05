
import base64
from enum import Enum


class ID(Enum):
    BASE32 = "Base32"
    BASE64 = "Base64"


class EncoderInterface:

    @staticmethod
    def encode(data: bytes) -> bytes:
        raise NotImpelementedErr("EncodeInterface.encode is not implemented")

    @staticmethod
    def decode(data: bytes) -> bytes:
        raise NotImpelementedErr("EncodeInterface.decode is not implemented")

    @staticmethod
    def id() -> str:
        raise NotImpelementedErr("EncodeInterface.id is not implemented")


def from_id(id_: str) -> EncoderInterface:
    match id_:
        case ID.BASE32.value:
            return Base32
        case ID.BASE64.value:
            return Base64
        case _:
            return None

class Base32(EncoderInterface):

    @staticmethod
    def encode(data: bytes) -> bytes:
        return base64.b32encode(data)

    @staticmethod
    def decode(data: bytes) -> bytes:
        return base64.b32decode(data)

    @staticmethod
    def id() -> ID:
        return ID.BASE32


class Base64(EncoderInterface):

    @staticmethod
    def encode(data: bytes) -> bytes:
        return base64.b64encode(data)

    @staticmethod
    def decode(data: bytes) -> bytes:
        return base64.b64decode(data)

    @staticmethod
    def id() -> ID:
        return ID.BASE64
