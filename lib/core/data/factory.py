
from .group import Type, PasswordsGroup, CardsGroup, IdentitiesGroup
from .item import PasswordItem, CardItem, IdentityItem


def group_from_type(type_: str):
    match type_:
        case Type.PASSWORD.value:
            return PasswordsGroup
        case Type.CARD.value:
            return CardsGroup
        case Type.IDENTITY.value:
            return IdentitiesGroup
        case _:
            return None

def item_from_type(type_: Type):
    match type_:
        case Type.PASSWORD:
            return PasswordItem
        case Type.CARD:
            return CardItem
        case Type.IDENTITY:
            return IdentityItem
        case _:
            return None
