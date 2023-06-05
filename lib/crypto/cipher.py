
from enum import Enum

from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from .generate import random_bytes


class ID(Enum):
    AES_CBC = "AES-CBC"


class CipherInterface:

    @staticmethod
    def encrypt(data: bytes, key: bytes, salt: bytes) -> bytes:
        raise NotImpelementedErr("CipherInterface.encrypt is not implemented")

    @staticmethod
    def decrypt(data: bytes, key: bytes, salt: bytes) -> bytes:
        raise NotImpelementedErr("CipherInterface.decrypt is not implemented")

    @staticmethod
    def id() -> ID:
        raise NotImpelementedErr("CipherInterface.id is not implemented")


def from_id(id_: str) -> CipherInterface:
    match id_:
        case ID.AES_CBC.value:
            return AES_CBC
        case _:
            return None


class _AES(CipherInterface):
    ''' base aes implementation '''

    @staticmethod
    def encrypt(data: bytes, key: bytes, salt: bytes, mode) -> bytes:
        iv = random_bytes(AES.block_size)
        cipher = AES.new(_AES._pbkdf2(key, salt), mode, iv)
        return iv + cipher.encrypt(pad(data, AES.block_size))   
    
    @staticmethod
    def decrypt(data: bytes, key: bytes, salt: bytes, mode) -> bytes:
        cipher = AES.new(_AES._pbkdf2(key, salt), mode, data[:AES.block_size])
        return unpad(cipher.decrypt(data[AES.block_size:]), AES.block_size)

    @staticmethod
    def _pbkdf2(key: bytes, salt: bytes) -> bytes:
        return PBKDF2(key, salt, count=4096, hmac_hash_module=SHA256)


class AES_CBC(_AES):

    @staticmethod
    def encrypt(data: bytes, key: bytes, salt: bytes) -> bytes:
        return _AES.encrypt(data, key, salt, AES.MODE_CBC)

    @staticmethod
    def decrypt(data: bytes, key: bytes, salt: bytes) -> bytes:
        return _AES.decrypt(data, key, salt, AES.MODE_CBC)

    def id() -> ID:
        return ID.AES_CBC