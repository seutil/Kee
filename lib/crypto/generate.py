
import string as mstring
import secrets
from Crypto.Random import get_random_bytes


ALPHABET = mstring.ascii_letters + mstring.digits + mstring.punctuation + mstring.whitespace


def random_bytes(nbytes: int) -> bytes:
    return get_random_bytes(nbytes)

def string(nchars: int) -> str:
    return secrets.token_hex(nchars)

def password(nchars: int, alphabet = ALPHABET) -> str:
    if not alphabet:
        raise ValueError("Empty alphabet")

    return ''.join(secrets.choice(alphabet) for _ in range(nchars))
