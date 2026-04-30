from __future__ import annotations

from enum import Enum, auto


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


# Maps each role to its display metadata: (display_name, description, card_color_hex, text_color_hex)
ROLE_METADATA = {
    RoleType.CULPRIT: (
        "Culprit",
        "You are the murderer!\nIf caught, you lose.\nPlay this as your last card to escape and win.",
        "#7b0000",
        "#ffcccc"
    ),
    RoleType.ACCOMPLICE: (
        "Accomplice",
        "You help the Culprit.\nYou win if the Culprit wins.\nStay hidden and protect the criminal.",
        "#3a003a",
        "#e8b4ff"
    ),
    RoleType.DETECTIVE: (
        "Detective",
        "Point at a player. If they hold the Culprit card, you arrest them and the round ends.",
        "#003060",
        "#b0d4ff"
    ),
    RoleType.WITNESS: (
        "Witness",
        "Secretly look at another player's entire hand. Gather evidence wisely.",
        "#1a3a00",
        "#b8ffb0"
    ),
    RoleType.ALIBI: (
        "Alibi",
        "You are protected until your next turn. Detectives and Toby cannot target you.",
        "#3a2a00",
        "#ffe9a0"
    ),
    RoleType.TOBY: (
        "Toby (The Dog)",
        "Point at a player. Toby sniffs them out — if they hold the Culprit, the round ends!",
        "#4a2200",
        "#ffd4a0"
    ),
    RoleType.SHERIFF: (
        "Sheriff",
        "Place handcuffs on any player. A handcuffed Culprit is immediately arrested!",
        "#1a1a40",
        "#a0a8ff"
    ),
    RoleType.FIRST_ON_SCENE: (
        "First on Scene",
        "You were first at the crime scene. You take the first turn this round.",
        "#002a2a",
        "#a0f0f0"
    ),
    RoleType.SERVANT: (
        "Servant",
        "You are protected until your next turn. No one may target you with card effects.",
        "#2a1a00",
        "#ffc080"
    ),
    RoleType.CITIZEN: (
        "Citizen",
        "An ordinary guest. Swap the top card of your hand with the next player's top card.",
        "#1a1a1a",
        "#cccccc"
    ),
}


class Card:
    """Represents a single playable card in the game."""

    def __init__(self, role_type: RoleType):
        meta = ROLE_METADATA[role_type]
        self.role_type = role_type
        self.name = meta[0]
        self.description = meta[1]
        self.color = meta[2]
        self.text_color = meta[3]

    def __repr__(self):
        return f"Card({self.name})"


class Player:
    """Represents a player (human or AI) in the game."""

    def __init__(self, name: str, is_ai: bool = False):
        self.name = name
        self.is_ai = is_ai
        self.hand: list[Card] = []
        self.score: int = 0
        self.is_handcuffed: bool = False
        self.protected: bool = False

    def add_card(self, card: Card):
        self.hand.append(card)

    def remove_card(self, card: Card):
        self.hand.remove(card)

    def has_role(self, role_type: RoleType) -> bool:
        return any(c.role_type == role_type for c in self.hand)

    def __repr__(self):
        return f"Player({self.name}, Score: {self.score})"
