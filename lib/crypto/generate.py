
import string as mstring
import secrets
from Crypto.Random import get_random_bytes


def random_bytes(nbytes: int) -> bytes:
    return get_random_bytes(nbytes)

def string(nchars: int) -> str:
    return secrets.token_hex(nchars)

def password(nchars: int) -> str:
    alphabet = mstring.ascii_letters + mstring.digits + mstring.punctuation + mstring.whitespace
    return ''.join(secrets.choice(alphabet) for _ in range(nchars))
