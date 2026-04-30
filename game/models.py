from enum import Enum, auto
import random

class RoleType(Enum):
    CULPRIT = auto()
    ACCOMPLICE = auto()
    DETECTIVE = auto()
    WITNESS = auto()
    ALIBI = auto()
    TOBY = auto()
    SHERIFF = auto()
    FIRST_ON_SCENE = auto()
    SERVANT = auto()
    CITIZEN = auto()

class Card:
    def __init__(self, role_type, name, description):
        self.role_type = role_type
        self.name = name
        self.description = description

    def __repr__(self):
        return f"Card({self.name})"

class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.is_ai = is_ai
        self.hand = []
        self.score = 0
        self.is_handcuffed = False
        self.protected = False # Protected by Servant/Alibi for one turn

    def add_card(self, card):
        self.hand.append(card)

    def remove_card(self, card):
        self.hand.remove(card)

    def has_role(self, role_type):
        return any(card.role_type == role_type for card in self.hand)

    def __repr__(self):
        return f"Player({self.name}, Score: {self.score})"
