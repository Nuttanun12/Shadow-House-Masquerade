from __future__ import annotations

import random
from .models import RoleType, Card, Player


WIN_SCORE = 5  # Score threshold to win the entire game


class GameEngine:
    """
    Core game engine for Shadow House: Masquerade.

    Manages players, deck, turns, card effects, scoring, and round/game end logic.
    """

    def __init__(self, player_names: list[str], ai_count: int = 0):
        self.players: list[Player] = [Player(name) for name in player_names]
        for i in range(ai_count):
            self.players.append(Player(f"AI {i + 1}", is_ai=True))

        self.deck: list[Card] = []
        self.discard_pile: list[Card] = []   # cards played this round (for visual stack)
        self.current_turn_index: int = 0
        self.round_number: int = 1
        self.game_over: bool = False
        self.winner: Player | None = None
        self.logs: list[str] = []

        # Callback fired when the game ends (set by UI layer)
        self.on_game_over = None

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def log(self, message: str):
        self.logs.append(message)
        print(f"[Engine] {message}")

    def last_log(self) -> str:
        return self.logs[-1] if self.logs else ""

    # ------------------------------------------------------------------
    # Round setup
    # ------------------------------------------------------------------

    def setup_round(self):
        self.log(f"─── Round {self.round_number} begins ───")
        self._create_deck()
        random.shuffle(self.deck)
        self.discard_pile = []   # clear the discard pile for the new round

        # Reset player round state
        for p in self.players:
            p.hand = []
            p.is_handcuffed = False
            p.protected = False

        # Deal 4 cards to each player
        for _ in range(4):
            for p in self.players:
                if self.deck:
                    p.add_card(self.deck.pop())

        # Determine starting player: First on Scene, else random
        for i, p in enumerate(self.players):
            if p.has_role(RoleType.FIRST_ON_SCENE):
                self.current_turn_index = i
                self.log(f"{p.name} holds 'First on Scene' — they go first.")
                return

        self.current_turn_index = random.randint(0, len(self.players) - 1)
        self.log(f"{self.players[self.current_turn_index].name} goes first (random).")

    def _create_deck(self):
        """Build the deck according to the official player-count configuration."""
        n = len(self.players)
        self.deck = []

        # Starter card distribution per player count
        configs = {
            3: {RoleType.CULPRIT: 1, RoleType.ACCOMPLICE: 1, RoleType.DETECTIVE: 1,
                RoleType.FIRST_ON_SCENE: 1, RoleType.SHERIFF: 1, RoleType.ALIBI: 1, RoleType.TOBY: 1},
            4: {RoleType.CULPRIT: 1, RoleType.ACCOMPLICE: 1, RoleType.DETECTIVE: 1,
                RoleType.FIRST_ON_SCENE: 1, RoleType.SHERIFF: 1, RoleType.ALIBI: 1, RoleType.TOBY: 1},
            5: {RoleType.CULPRIT: 1, RoleType.ACCOMPLICE: 2, RoleType.DETECTIVE: 2,
                RoleType.FIRST_ON_SCENE: 1, RoleType.SHERIFF: 1, RoleType.ALIBI: 2, RoleType.TOBY: 1},
            6: {RoleType.CULPRIT: 1, RoleType.ACCOMPLICE: 2, RoleType.DETECTIVE: 2,
                RoleType.FIRST_ON_SCENE: 1, RoleType.SHERIFF: 1, RoleType.ALIBI: 2, RoleType.TOBY: 1},
            7: {RoleType.CULPRIT: 1, RoleType.ACCOMPLICE: 3, RoleType.DETECTIVE: 3,
                RoleType.FIRST_ON_SCENE: 1, RoleType.SHERIFF: 1, RoleType.ALIBI: 3, RoleType.TOBY: 1},
            8: {RoleType.CULPRIT: 1, RoleType.ACCOMPLICE: 3, RoleType.DETECTIVE: 3,
                RoleType.FIRST_ON_SCENE: 1, RoleType.SHERIFF: 1, RoleType.ALIBI: 3, RoleType.TOBY: 1},
        }

        config = configs.get(n, configs[3])
        for role, count in config.items():
            for _ in range(count):
                self.deck.append(Card(role))

        # Fill remaining slots with filler cards
        filler_roles = [RoleType.ALIBI, RoleType.WITNESS, RoleType.SERVANT, RoleType.CITIZEN]
        needed = (n * 4) - len(self.deck)
        for _ in range(max(0, needed)):
            self.deck.append(Card(random.choice(filler_roles)))

    # ------------------------------------------------------------------
    # Turn management
    # ------------------------------------------------------------------

    def advance_turn(self):
        """Move to the next player's turn, skipping none (handcuff is checked in UI)."""
        self.current_turn_index = (self.current_turn_index + 1) % len(self.players)
        # Unset protection at the start of the protected player's next turn
        self.players[self.current_turn_index].protected = False

    @property
    def current_player(self) -> Player:
        return self.players[self.current_turn_index]

    # ------------------------------------------------------------------
    # Card play
    # ------------------------------------------------------------------

    def play_card(self, player_index: int, card_index: int,
                  target_player_index: int | None = None) -> str:
        """
        Play the card at `card_index` from `player_index`'s hand.
        Returns a result string: "ROUND_END", "GAME_OVER", or "CONTINUE".
        """
        player = self.players[player_index]

        # Validate indices
        if card_index < 0 or card_index >= len(player.hand):
            self.log("Invalid card index!")
            return "CONTINUE"

        card = player.hand.pop(card_index)
        self.discard_pile.append(card)   # track played card for the visual discard stack
        self.log(f"{player.name} played '{card.name}'.")

        result = self._resolve_effect(player, card, target_player_index)

        if result == "ROUND_END":
            outcome = self._end_round(arresting_player=player)
            if self.game_over:
                return "GAME_OVER"
            return "ROUND_END"

        # Check if all hands are empty → culprit escaped if still holding culprit
        if not any(p.hand for p in self.players):
            culprit_holder = self._find_culprit_holder()
            self.log("All hands are empty — the round ends!")
            self._end_round(arresting_player=None)
            if self.game_over:
                return "GAME_OVER"
            return "ROUND_END"

        self.advance_turn()
        return "CONTINUE"

    def _resolve_effect(self, player: Player, card: Card,
                        target_index: int | None) -> str:
        """Apply the card effect. Returns 'ROUND_END' or 'CONTINUE'."""

        role = card.role_type

        if role == RoleType.DETECTIVE:
            if target_index is not None:
                target = self.players[target_index]
                if target.protected:
                    self.log(f"🛡️ {target.name} is protected — Detective is blocked!")
                    return "CONTINUE"
                if target.has_role(RoleType.CULPRIT):
                    self.log(f"🔍 Detective found the Culprit in {target.name}'s hand! Round ends!")
                    return "ROUND_END"
                else:
                    self.log(f"🔍 Detective searched {target.name} — no Culprit found.")
            return "CONTINUE"

        elif role == RoleType.TOBY:
            if target_index is not None:
                target = self.players[target_index]
                if target.protected:
                    self.log(f"🛡️ {target.name} is protected — Toby is chased off!")
                    return "CONTINUE"
                if target.has_role(RoleType.CULPRIT):
                    self.log(f"🐕 Toby sniffed out the Culprit at {target.name}! Round ends!")
                    return "ROUND_END"
                else:
                    self.log(f"🐕 Toby sniffed {target.name} — nothing suspicious found.")
            return "CONTINUE"

        elif role == RoleType.SHERIFF:
            if target_index is not None:
                target = self.players[target_index]
                target.is_handcuffed = True
                self.log(f"🔒 {target.name} has been handcuffed by the Sheriff!")
                # If handcuffed player holds the Culprit, they are immediately arrested
                if target.has_role(RoleType.CULPRIT):
                    self.log(f"⚖️ {target.name} is handcuffed AND holds the Culprit — arrested!")
                    return "ROUND_END"
            return "CONTINUE"

        elif role == RoleType.WITNESS:
            if target_index is not None:
                target = self.players[target_index]
                hand_names = [c.name for c in target.hand]
                self.log(f"👁️ {player.name} witnessed {target.name}'s hand: {', '.join(hand_names)}")
                # Return special marker so UI can show the witness result
                return "WITNESS"
            return "CONTINUE"

        elif role in (RoleType.ALIBI, RoleType.SERVANT):
            player.protected = True
            self.log(f"🛡️ {player.name} played {card.name} — protected until next turn.")
            return "CONTINUE"

        elif role == RoleType.CITIZEN:
            # Swap top card with next player
            if len(self.players) > 1:
                next_idx = (self.players.index(player) + 1) % len(self.players)
                other = self.players[next_idx]
                if player.hand and other.hand:
                    c1 = player.hand.pop(0)
                    c2 = other.hand.pop(0)
                    player.add_card(c2)
                    other.add_card(c1)
                    self.log(f"🔄 {player.name} swapped a card with {other.name}.")
            return "CONTINUE"

        elif role == RoleType.CULPRIT:
            self.log(f"💀 {player.name} played the Culprit card — they are revealed!")
            return "ROUND_END"

        elif role == RoleType.FIRST_ON_SCENE:
            self.log(f"🕵️ {player.name} played First on Scene — no special effect mid-game.")
            return "CONTINUE"

        return "CONTINUE"

    # ------------------------------------------------------------------
    # Round & Game end
    # ------------------------------------------------------------------

    def _find_culprit_holder(self) -> Player | None:
        for p in self.players:
            if p.has_role(RoleType.CULPRIT):
                return p
        return None

    def _end_round(self, arresting_player: Player | None):
        """
        Score the round.
        - If culprit arrested: arresting player +2, other innocents +1
        - If culprit escaped (last card / all hands empty without arrest): culprit +2, accomplices +1
        """
        culprit_player = self._find_culprit_holder()

        # Determine if culprit was caught
        culprit_caught = False
        if culprit_player:
            if arresting_player and arresting_player != culprit_player:
                culprit_caught = True
            elif culprit_player.is_handcuffed:
                culprit_caught = True

        if culprit_caught and arresting_player:
            self.log(f"⚖️ ROUND END — {arresting_player.name} arrested the Culprit ({culprit_player.name if culprit_player else '?'})!")
            arresting_player.score += 2
            for p in self.players:
                if p != arresting_player and not p.has_role(RoleType.ACCOMPLICE):
                    p.score += 1
        elif culprit_caught and culprit_player and culprit_player.is_handcuffed:
            # Handcuffed arrest — award whoever handcuffed (can't determine, give generic +1 to all innocents)
            self.log(f"⚖️ ROUND END — {culprit_player.name} (the Culprit) was caught by the handcuffs!")
            for p in self.players:
                if not p.has_role(RoleType.ACCOMPLICE) and p != culprit_player:
                    p.score += 1
        else:
            cp_name = culprit_player.name if culprit_player else "Unknown"
            self.log(f"🌑 ROUND END — The Culprit ({cp_name}) escaped!")
            if culprit_player:
                culprit_player.score += 2
            for p in self.players:
                if p.has_role(RoleType.ACCOMPLICE) and p != culprit_player:
                    p.score += 1

        self.round_number += 1
        self._check_game_over()

    def _check_game_over(self):
        """Check if any player has reached the win threshold."""
        top_scorer = max(self.players, key=lambda p: p.score)
        if top_scorer.score >= WIN_SCORE:
            self.game_over = True
            self.winner = top_scorer
            self.log(f"🏆 GAME OVER — {top_scorer.name} wins the Masquerade with {top_scorer.score} points!")
            self._save_to_db()
        else:
            self.setup_round()

    def _save_to_db(self):
        """Persist game result to the database."""
        try:
            from storage.database import DatabaseManager
            db = DatabaseManager()
            scores = {p.name: p.score for p in self.players}
            db.record_game(self.winner.name, scores)
            for p in self.players:
                db.update_player_stats(p.name, p == self.winner, p.score)
            self.log("📊 Game record saved to database.")
        except Exception as e:
            self.log(f"⚠️ Could not save game record: {e}")

    # ------------------------------------------------------------------
    # AI logic
    # ------------------------------------------------------------------

    def ai_play(self) -> dict:
        """
        Compute and execute an AI turn.
        Returns a dict with keys: card_index, target_index, result.
        """
        p_idx = self.current_turn_index
        player = self.players[p_idx]

        # Choose card: avoid playing Culprit if possible
        card_idx = 0
        for i, c in enumerate(player.hand):
            if c.role_type != RoleType.CULPRIT:
                card_idx = i
                break

        # Choose target: favour targeting human players (index 0)
        aggressive_roles = {RoleType.DETECTIVE, RoleType.TOBY, RoleType.SHERIFF, RoleType.WITNESS}
        played_card = player.hand[card_idx]
        target_idx = None

        if played_card.role_type in aggressive_roles:
            # Pick a non-protected, non-self target, prefer unprotected
            candidates = [
                i for i, p in enumerate(self.players)
                if i != p_idx and not p.protected
            ]
            if candidates:
                target_idx = random.choice(candidates)
            else:
                target_idx = (p_idx + 1) % len(self.players)

        result = self.play_card(p_idx, card_idx, target_idx)
        return {"card_index": card_idx, "target_index": target_idx, "result": result}
