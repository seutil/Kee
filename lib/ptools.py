
from enum import Enum
from zxcvbn import zxcvbn


class Strength(Enum):
    WEAK = 1
    MODERATE = 2
    STRONG = 3


def strength(passw: str) -> Strength:
    score = zxcvbn(passw)["score"]
    if 0 <= score <= 2:
        return Strength.WEAK
    elif score == 3:
        return Strength.MODERATE
    else:
        return Strength.STRONG
