from __future__ import annotations
from enum import Enum, auto


class RoleType(Enum):
    # Starter deck
    CULPRIT       = auto()
    ACCOMPLICE    = auto()
    DETECTIVE     = auto()
    FIRST_ON_SCENE = auto()
    SHERIFF       = auto()
    ALIBI         = auto()
    # "Other" pool
    TOBY          = auto()
    WITNESS       = auto()
    SERVANT       = auto()
    HOUSEKEEPER   = auto()
    BABY_OF_FAMILY = auto()
    SHARE         = auto()
    RUMORS        = auto()
    FRENZY        = auto()
    SOOTHSAYER    = auto()
    SWAP          = auto()


ROLE_METADATA = {
    RoleType.CULPRIT: (
        "Culprit",
        "Play ONLY as your last card to escape and win the round. Must play all other cards first.",
        "#7b0000", "#ffcccc", "💀",
    ),
    RoleType.ACCOMPLICE: (
        "Accomplice",
        "You become an accomplice. Force a player to discard one card face up and draw a new one.",
        "#3a003a", "#e8b4ff", "🤝",
    ),
    RoleType.DETECTIVE: (
        "Detective",
        "Ask a player: 'Are you the culprit?' If they hold the Culprit and no Alibi, you win!",
        "#003060", "#b0d4ff", "🔍",
    ),
    RoleType.FIRST_ON_SCENE: (
        "First on Scene",
        "You were first at the crime scene. Play this card to take the first turn this round.",
        "#002a2a", "#a0f0f0", "🕵️",
    ),
    RoleType.SHERIFF: (
        "Sheriff",
        "Give the handcuffs token to any player. Culprit with handcuffs at round end loses.",
        "#1a1a40", "#a0a8ff", "⚖️",
    ),
    RoleType.ALIBI: (
        "Alibi",
        "No effect when played. While held, you may answer 'No' to the Detective truthfully.",
        "#3a2a00", "#ffe9a0", "📋",
    ),
    RoleType.TOBY: (
        "Toby (The Dog)",
        "Choose one card in a player's hand and make them reveal it. If it's the Culprit, you win!",
        "#4a2200", "#ffd4a0", "🐕",
    ),
    RoleType.WITNESS: (
        "Witness",
        "Secretly look at a player's entire hand. If you see Culprit/Accomplice, you may swap a card.",
        "#1a3a00", "#b8ffb0", "👁️",
    ),
    RoleType.SERVANT: (
        "The Servant",
        "The Detective cannot question you until your next turn.",
        "#2a1a00", "#ffc080", "🛡️",
    ),
    RoleType.HOUSEKEEPER: (
        "The Housekeeper",
        "Toby and the Sheriff cannot choose you until your next turn.",
        "#1a0a2a", "#d4b0ff", "🧹",
    ),
    RoleType.BABY_OF_FAMILY: (
        "Baby of the Family",
        "Everyone closes their eyes. Only the culprit opens their eyes, then all open again.",
        "#0a2a0a", "#a0ffb0", "👶",
    ),
    RoleType.SHARE: (
        "Share",
        "Each player selects one card from their hand and passes it to the player on their left.",
        "#2a1a00", "#ffcc80", "🫳",
    ),
    RoleType.RUMORS: (
        "Rumors",
        "Each player draws one card at random from the hand of the player on their right.",
        "#001a2a", "#80ccff", "🗣️",
    ),
    RoleType.FRENZY: (
        "Frenzy!!!",
        "Everyone picks a card. They're shuffled and dealt back at random. (No effect on last turn.)",
        "#2a0010", "#ffb0c0", "🌀",
    ),
    RoleType.SOOTHSAYER: (
        "Soothsayer",
        "Share your thoughts: who you think is the culprit or an accomplice.",
        "#1a1a00", "#ffffa0", "🔮",
    ),
    RoleType.SWAP: (
        "Swap",
        "Swap a card with a player of your choice. That player chooses which card they give you.",
        "#001a1a", "#a0ffff", "🔄",
    ),
}


class Card:
    def __init__(self, role_type: RoleType):
        meta = ROLE_METADATA[role_type]
        self.role_type   = role_type
        self.name        = meta[0]
        self.description = meta[1]
        self.color       = meta[2]
        self.text_color  = meta[3]
        self.emoji       = meta[4]

    def __repr__(self):
        return f"Card({self.name})"


class Player:
    def __init__(self, name: str, is_ai: bool = False):
        self.name   = name
        self.is_ai  = is_ai
        self.hand: list[Card] = []
        self.score: int = 0
        # Reset each round:
        self.is_accomplice: bool = False        # set permanently once Accomplice card played
        self.has_handcuffs: bool = False        # holding the handcuffs token
        self.servant_protected: bool = False    # Detective can't question this turn
        self.housekeeper_protected: bool = False  # Toby/Sheriff can't target this turn

    def reset_round_state(self):
        self.hand = []
        self.is_accomplice        = False
        self.has_handcuffs        = False
        self.servant_protected    = False
        self.housekeeper_protected = False

    def add_card(self, card: Card):
        self.hand.append(card)

    def has_role(self, role_type: RoleType) -> bool:
        return any(c.role_type == role_type for c in self.hand)

    def __repr__(self):
        return f"Player({self.name}, Score:{self.score})"
