from __future__ import annotations

import random
from .models import RoleType, Card, Player

WIN_SCORE = 5


class GameEngine:
    """
    Core game engine — rules from ShadowHouseMasquerade-Rules-EN.pdf.

    Round-end scenarios (any ends immediately):
      1. Detective identifies culprit (target holds Culprit + no Alibi, detective is not accomplice)
      2. Toby reveals the Culprit card from a target's hand (Toby not accomplice)
      3. Sheriff's handcuffs are on the culprit when identified
      4. Culprit plays their Culprit card as their very last card
    """

    def __init__(self, player_names: list[str], ai_count: int = 0):
        self.players: list[Player] = [Player(name) for name in player_names]
        for i in range(ai_count):
            self.players.append(Player(f"AI {i + 1}", is_ai=True))

        self.deck: list[Card] = []
        self.discard_pile: list[Card] = []
        self.handcuffs_owner: int | None = None   # index of player with handcuffs token
        self.current_turn_index: int = 0
        self.round_number: int = 1
        self.game_over: bool = False
        self.winner: Player | None = None
        self.logs: list[str] = []
        self.fos_must_play: bool = False  # True until First on Scene is placed

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def log(self, msg: str):
        self.logs.append(msg)
        print(f"[Engine] {msg}")

    # ------------------------------------------------------------------
    # Round setup
    # ------------------------------------------------------------------

    def setup_round(self):
        self.log(f"─── Round {self.round_number} begins ───")
        self.discard_pile = []
        self.handcuffs_owner = None
        self.fos_must_play = False

        for p in self.players:
            p.reset_round_state()

        self._create_deck()
        random.shuffle(self.deck)

        # Deal 4 cards each
        for _ in range(4):
            for p in self.players:
                if self.deck:
                    p.add_card(self.deck.pop())

        # First on Scene holder goes first AND must open by playing it
        for i, p in enumerate(self.players):
            if p.has_role(RoleType.FIRST_ON_SCENE):
                self.current_turn_index = i
                self.fos_must_play = True
                self.log(f"{p.name} holds 'First on Scene' — they MUST play it to start.")
                return

        self.current_turn_index = random.randint(0, len(self.players) - 1)
        self.log(f"{self.players[self.current_turn_index].name} goes first (random).")

    def _create_deck(self):
        """Build deck per official player-count table."""
        n = len(self.players)
        # (first_on_scene, culprit, detective, accomplice, sheriff, alibi, other_count)
        configs = {
            3: (1, 1, 1, 0, 1, 1, 7),
            4: (1, 1, 1, 1, 1, 1, 10),
            5: (1, 1, 1, 1, 1, 2, 13),
            6: (1, 1, 2, 2, 1, 2, 15),
            7: (1, 1, 2, 2, 1, 3, 18),
            8: (1, 1, 2, 2, 1, 3, 22),
        }
        fos, cul, det, acc, shr, ali, other_n = configs.get(n, configs[4])

        self.deck = []
        for role, cnt in [
            (RoleType.FIRST_ON_SCENE, fos),
            (RoleType.CULPRIT,        cul),
            (RoleType.DETECTIVE,      det),
            (RoleType.ACCOMPLICE,     acc),
            (RoleType.SHERIFF,        shr),
            (RoleType.ALIBI,          ali),
        ]:
            self.deck += [Card(role) for _ in range(cnt)]

        other_pool = [
            RoleType.TOBY, RoleType.WITNESS, RoleType.SERVANT,
            RoleType.HOUSEKEEPER, RoleType.BABY_OF_FAMILY,
            RoleType.SHARE, RoleType.RUMORS, RoleType.FRENZY,
            RoleType.SOOTHSAYER, RoleType.SWAP,
        ]
        for _ in range(other_n):
            self.deck.append(Card(random.choice(other_pool)))

    # ------------------------------------------------------------------
    # Turn management
    # ------------------------------------------------------------------

    def advance_turn(self):
        self.current_turn_index = (self.current_turn_index + 1) % len(self.players)
        # Reset per-turn protections for the player whose turn it now is
        p = self.players[self.current_turn_index]
        p.servant_protected    = False
        p.housekeeper_protected = False

    @property
    def current_player(self) -> Player:
        return self.players[self.current_turn_index]

    # ------------------------------------------------------------------
    # Public: play a card
    # ------------------------------------------------------------------

    def can_play_culprit(self, player_index: int) -> bool:
        """Culprit may only be played/discarded as the last card in hand."""
        p = self.players[player_index]
        return len(p.hand) == 1 and p.hand[0].role_type == RoleType.CULPRIT

    def play_card(self, player_index: int, card_index: int,
                  target_index: int | None = None,
                  extra: dict | None = None) -> str:
        """
        Play the card at card_index from player_index's hand.
        extra dict keys (card-specific):
          - 'toby_card_idx'    : int   (which card in target's hand Toby reveals)
          - 'accomplice_card_idx': int  (which card target discards)
          - 'witness_swap'     : bool  (True to swap after witnessing)
          - 'witness_my_idx'   : int   (my card to swap)
          - 'witness_their_idx': int   (their card I'm swapping for)
          - 'swap_their_idx'   : int   (SWAP card: which card target gives)
          - 'swap_my_idx'      : int   (SWAP card: which card I give)
          - 'share_card_idx'   : int   (which card current player passes in SHARE)
          - 'frenzy_card_idx'  : int   (which card current player contributes in FRENZY)
        Returns: "CONTINUE" | "ROUND_END" | "GAME_OVER" | "WITNESS" | "BABY" | "SOOTHSAYER"
        """
        if extra is None:
            extra = {}

        player = self.players[player_index]
        if not (0 <= card_index < len(player.hand)):
            return "CONTINUE"

        card = player.hand[card_index]

        # Enforce First on Scene rule: must be the very first card played
        if self.fos_must_play and card.role_type != RoleType.FIRST_ON_SCENE:
            self.log(f"⚠️ {player.name} must play 'First on Scene' to open the round!")
            return "FOS_REQUIRED"

        # Enforce Culprit rule: can only play if last card
        if card.role_type == RoleType.CULPRIT and len(player.hand) > 1:
            self.log(f"⚠️ {player.name} cannot play the Culprit — it must be the last card!")
            return "CONTINUE"

        player.hand.pop(card_index)
        self.discard_pile.append(card)
        self.log(f"{player.name} played '{card.name}'.")

        result = self._resolve_effect(player, card, target_index, extra)

        if result == "ROUND_END":
            self._end_round(arresting_player=player)
            return "GAME_OVER" if self.game_over else "ROUND_END"

        if result == "CULPRIT_WINS":
            self._end_round(arresting_player=None)
            return "GAME_OVER" if self.game_over else "ROUND_END"

        # If all hands empty and no one caught the culprit → culprit escapes
        if not any(p.hand for p in self.players):
            self.log("All hands empty — round ends!")
            self._end_round(arresting_player=None)
            return "GAME_OVER" if self.game_over else "ROUND_END"

        if result not in ("WITNESS", "BABY", "SOOTHSAYER"):
            self.advance_turn()

        return result if result in ("WITNESS", "BABY", "SOOTHSAYER") else "CONTINUE"

    # ------------------------------------------------------------------
    # Effect resolution
    # ------------------------------------------------------------------

    def _resolve_effect(self, player: Player, card: Card,
                        target_index: int | None, extra: dict) -> str:
        role = card.role_type

        # ── First on Scene ──────────────────────────────────────────────
        if role == RoleType.FIRST_ON_SCENE:
            self.fos_must_play = False   # unlock the rest of the round
            self.log(f"🕵️ {player.name} places First on Scene — round begins!")
            return "CONTINUE"

        # ── Alibi ───────────────────────────────────────────────────────
        if role == RoleType.ALIBI:
            self.log(f"📋 {player.name} plays Alibi — no immediate effect.")
            return "CONTINUE"

        # ── Culprit ─────────────────────────────────────────────────────
        if role == RoleType.CULPRIT:
            self.log(f"💀 {player.name} played their last card — the Culprit! They escape!")
            return "CULPRIT_WINS"

        # ── Detective ───────────────────────────────────────────────────
        if role == RoleType.DETECTIVE:
            if target_index is None:
                return "CONTINUE"
            target = self.players[target_index]
            if target.servant_protected:
                self.log(f"🛡️ {target.name} is protected by The Servant — Detective blocked!")
                return "CONTINUE"
            if player.is_accomplice:
                self.log(f"🔍 {player.name} is an accomplice — Detective wins nothing.")
                return "CONTINUE"
            if target.has_role(RoleType.CULPRIT) and not target.has_role(RoleType.ALIBI):
                self.log(f"🔍 Detective caught the Culprit in {target.name}'s hand! Round ends!")
                return "ROUND_END"
            else:
                self.log(f"🔍 {target.name} answered: 'No, I'm not the culprit.'")
            return "CONTINUE"

        # ── Accomplice ──────────────────────────────────────────────────
        if role == RoleType.ACCOMPLICE:
            player.is_accomplice = True
            self.log(f"🤝 {player.name} is now an accomplice!")
            if target_index is None:
                return "CONTINUE"
            target = self.players[target_index]
            # Determine which card target discards
            discard_idx = extra.get("accomplice_card_idx", 0)
            if not target.hand:
                return "CONTINUE"
            discard_idx = max(0, min(discard_idx, len(target.hand) - 1))
            last_card_before = len(target.hand) == 1
            discarded = target.hand.pop(discard_idx)
            self.discard_pile.append(discarded)
            self.log(f"🤝 {target.name} discarded '{discarded.name}' face up.")
            # If it was Culprit and their last card → culprit wins
            if discarded.role_type == RoleType.CULPRIT and last_card_before:
                self.log(f"💀 {target.name} discarded the Culprit as their last card — they win!")
                return "CULPRIT_WINS"
            # Target draws a new card
            if self.deck:
                new_card = self.deck.pop()
                target.add_card(new_card)
                self.log(f"🃏 {target.name} drew a new card.")
            return "CONTINUE"

        # ── Sheriff ─────────────────────────────────────────────────────
        if role == RoleType.SHERIFF:
            if target_index is None:
                return "CONTINUE"
            target = self.players[target_index]
            if target.housekeeper_protected:
                self.log(f"🛡️ {target.name} is protected by The Housekeeper — Sheriff blocked!")
                return "CONTINUE"
            # Remove handcuffs from previous holder
            for p in self.players:
                p.has_handcuffs = False
            target.has_handcuffs = True
            self.handcuffs_owner = target_index
            self.log(f"🔒 {target.name} now holds the handcuffs token!")
            # If target is culprit → immediate arrest
            if target.has_role(RoleType.CULPRIT):
                self.log(f"⚖️ Culprit {target.name} is handcuffed — arrested immediately!")
                return "ROUND_END"
            return "CONTINUE"

        # ── Toby ────────────────────────────────────────────────────────
        if role == RoleType.TOBY:
            if target_index is None:
                return "CONTINUE"
            target = self.players[target_index]
            if target.housekeeper_protected:
                self.log(f"🛡️ {target.name} is protected — Toby blocked!")
                return "CONTINUE"
            if player.is_accomplice:
                self.log(f"🐕 {player.name} is an accomplice — Toby wins nothing.")
                return "CONTINUE"
            if not target.hand:
                return "CONTINUE"
            card_idx = extra.get("toby_card_idx", 0)
            card_idx = max(0, min(card_idx, len(target.hand) - 1))
            revealed = target.hand[card_idx]
            self.log(f"🐕 Toby revealed '{revealed.name}' from {target.name}'s hand!")
            if revealed.role_type == RoleType.CULPRIT:
                self.log(f"🐕 It's the Culprit! {target.name} is caught! Round ends!")
                return "ROUND_END"
            return "CONTINUE"

        # ── Witness ─────────────────────────────────────────────────────
        if role == RoleType.WITNESS:
            if target_index is None:
                return "CONTINUE"
            target = self.players[target_index]
            hand_names = [c.name for c in target.hand]
            self.log(f"👁️ {player.name} secretly views {target.name}'s hand: {', '.join(hand_names)}")
            # Optional swap handled after WITNESS return via UI
            return "WITNESS"

        # ── Servant ─────────────────────────────────────────────────────
        if role == RoleType.SERVANT:
            player.servant_protected = True
            self.log(f"🛡️ {player.name} is protected — Detective cannot question until next turn.")
            return "CONTINUE"

        # ── Housekeeper ─────────────────────────────────────────────────
        if role == RoleType.HOUSEKEEPER:
            player.housekeeper_protected = True
            self.log(f"🛡️ {player.name} is protected — Toby/Sheriff cannot target until next turn.")
            return "CONTINUE"

        # ── Swap ────────────────────────────────────────────────────────
        if role == RoleType.SWAP:
            if target_index is None:
                return "CONTINUE"
            target = self.players[target_index]
            if not player.hand:
                self.log(f"🔄 {player.name} has no cards to swap!")
                return "CONTINUE"
            if not target.hand:
                self.log(f"🔄 {target.name} has no cards to swap!")
                return "CONTINUE"
            
            their_idx = extra.get("swap_their_idx", 0)
            my_idx    = extra.get("swap_my_idx", 0)
            their_idx = max(0, min(their_idx, len(target.hand) - 1))
            my_idx    = max(0, min(my_idx,    len(player.hand) - 1))
            
            c1 = player.hand.pop(my_idx)
            c2 = target.hand.pop(their_idx)
            player.add_card(c2)
            target.add_card(c1)
            self.log(f"🔄 {player.name} and {target.name} swapped cards.")
            return "CONTINUE"

        # ── Share ────────────────────────────────────────────────────────
        if role == RoleType.SHARE:
            n = len(self.players)
            chosen_cards = []
            # Each player picks a card (human's choice in extra, AI picks first)
            for i, p in enumerate(self.players):
                if not p.hand:
                    chosen_cards.append(None)
                    continue
                if i == self.players.index(player):
                    idx = extra.get("share_card_idx", 0)
                else:
                    idx = 0  # AI gives first card
                idx = max(0, min(idx, len(p.hand) - 1))
                chosen_cards.append(p.hand.pop(idx))
            # Pass each to the left
            for i, p in enumerate(self.players):
                from_right = chosen_cards[(i - 1) % n]
                if from_right:
                    p.add_card(from_right)
            self.log("🔄 Share: each player passed a card to the left.")
            return "CONTINUE"

        # ── Rumors ──────────────────────────────────────────────────────
        if role == RoleType.RUMORS:
            n = len(self.players)
            # Collect cards first to make it simultaneous
            rumor_pool = {}
            for i in range(n):
                right_idx = (i + 1) % n
                right_p = self.players[right_idx]
                if right_p.hand:
                    drawn = right_p.hand.pop(random.randint(0, len(right_p.hand) - 1))
                    rumor_pool[i] = drawn
            
            if rumor_pool:
                for i, card in rumor_pool.items():
                    self.players[i].add_card(card)
                self.log("🗣️ Rumors: each player drew a random card from their right neighbour.")
            else:
                self.log("🗣️ Rumors: no one had cards to share.")
            return "CONTINUE"

        # ── Frenzy ──────────────────────────────────────────────────────
        if role == RoleType.FRENZY:
            player_idx = self.players.index(player)
            contributing_players = []
            pool_cards = []

            for i, p in enumerate(self.players):
                if not p.hand:
                    continue
                if i == player_idx:
                    idx = extra.get("frenzy_card_idx", 0)
                else:
                    idx = 0
                idx = max(0, min(idx, len(p.hand) - 1))
                contributing_players.append(i)
                pool_cards.append(p.hand.pop(idx))
            
            if len(pool_cards) > 1:
                random.shuffle(pool_cards)
                for i, p_idx in enumerate(contributing_players):
                    self.players[p_idx].add_card(pool_cards[i])
                self.log("🌀 Frenzy: cards were shuffled and dealt back randomly.")
            elif len(pool_cards) == 1:
                # Give back the single card
                self.players[contributing_players[0]].add_card(pool_cards[0])
                self.log("🌀 Frenzy: only one player had a card, so nothing changed.")
            else:
                self.log("🌀 Frenzy: no one had cards to contribute.")
            return "CONTINUE"

        # ── Baby of the Family ───────────────────────────────────────────
        if role == RoleType.BABY_OF_FAMILY:
            culprit_holder = self._find_culprit_holder()
            name = culprit_holder.name if culprit_holder else "unknown"
            self.log(f"👶 Baby of the Family: culprit secretly opens their eyes. ({name} knows who they are.)")
            return "BABY"

        # ── Soothsayer ──────────────────────────────────────────────────
        if role == RoleType.SOOTHSAYER:
            thought = extra.get("soothsayer_text", "...")
            self.log(f"🔮 {player.name} (Soothsayer): \"{thought}\"")
            return "SOOTHSAYER"

        return "CONTINUE"

    # ------------------------------------------------------------------
    # Round / Game end
    # ------------------------------------------------------------------

    def _find_culprit_holder(self) -> Player | None:
        for p in self.players:
            if p.has_role(RoleType.CULPRIT):
                return p
        return None

    def _end_round(self, arresting_player: Player | None):
        """
        Score the round:
        - Innocents win (detective/toby caught, sheriff handcuffs):
            arresting player +2, all other non-accomplice players +1
        - Culprit escapes (played last card, or all hands empty):
            culprit +2, each accomplice +1
        """
        culprit_player = self._find_culprit_holder()

        culprit_caught = (
            arresting_player is not None
            and arresting_player != culprit_player
        )

        if culprit_caught and arresting_player:
            cp_name = culprit_player.name if culprit_player else "?"
            self.log(f"⚖️ ROUND END — {arresting_player.name} arrested the Culprit ({cp_name})!")
            arresting_player.score += 2
            for p in self.players:
                if p != arresting_player and not p.is_accomplice:
                    p.score += 1
        else:
            # Culprit escapes — also covers culprit playing last card (arresting_player=None)
            if culprit_player is None:
                # edge case: find who just played culprit (last discarded)
                for c in reversed(self.discard_pile):
                    if c.role_type == RoleType.CULPRIT:
                        break
                self.log("🌑 ROUND END — The Culprit escaped!")
            else:
                self.log(f"🌑 ROUND END — {culprit_player.name} (Culprit) escaped!")
                culprit_player.score += 2
            for p in self.players:
                if p.is_accomplice and p != culprit_player:
                    p.score += 1

        self.round_number += 1
        self._check_game_over()

    def _check_game_over(self):
        top = max(self.players, key=lambda p: p.score)
        if top.score >= WIN_SCORE:
            self.game_over = True
            self.winner = top
            self.log(f"🏆 GAME OVER — {top.name} wins with {top.score} points!")
            self._save_to_db()
        else:
            self.setup_round()

    def _save_to_db(self):
        try:
            from storage.database import DatabaseManager
            db = DatabaseManager()
            db.record_game(self.winner.name, {p.name: p.score for p in self.players})
            for p in self.players:
                db.update_player_stats(p.name, p == self.winner, p.score)
            self.log("📊 Game record saved.")
        except Exception as e:
            self.log(f"⚠️ DB save failed: {e}")

    # ------------------------------------------------------------------
    # AI
    # ------------------------------------------------------------------

    def ai_play(self) -> dict:
        p_idx  = self.current_turn_index
        player = self.players[p_idx]

        # Guard: if hand is empty, just advance the turn
        if not player.hand:
            self.log(f"{player.name} has no cards — skipping turn.")
            self.advance_turn()
            return {"card_index": None, "target_index": None, "result": "CONTINUE"}

        # If FoS must be played first, find it
        if self.fos_must_play:
            card_idx = next(
                (i for i, c in enumerate(player.hand)
                 if c.role_type == RoleType.FIRST_ON_SCENE), 0
            )
        else:
            # Choose card — never play Culprit unless it's the only card
            card_idx = 0
            for i, c in enumerate(player.hand):
                if c.role_type == RoleType.CULPRIT:
                    continue
                # Logic: don't play Swap if it's our only card (nothing to swap with)
                if c.role_type == RoleType.SWAP and len(player.hand) == 1:
                    continue
                card_idx = i; break
        
        # If we only have Culprit or only have Swap(last), pick it anyway
        if not player.hand: # Should be caught by guard but safety first
             return {"card_index": None, "target_index": None, "result": "CONTINUE"}
        
        card = player.hand[card_idx]
        needs_target = card.role_type in {
            RoleType.DETECTIVE, RoleType.TOBY, RoleType.SHERIFF,
            RoleType.WITNESS, RoleType.ACCOMPLICE, RoleType.SWAP,
        }

        target_idx = None
        if needs_target:
            candidates = [
                i for i, p in enumerate(self.players)
                if i != p_idx
                and not (card.role_type == RoleType.DETECTIVE and p.servant_protected)
                and not (card.role_type in {RoleType.TOBY, RoleType.SHERIFF} and p.housekeeper_protected)
            ]
            target_idx = random.choice(candidates) if candidates else None

        extra: dict = {}
        if card.role_type == RoleType.TOBY and target_idx is not None:
            t = self.players[target_idx]
            extra["toby_card_idx"] = random.randint(0, max(0, len(t.hand) - 1))
        if card.role_type == RoleType.ACCOMPLICE and target_idx is not None:
            t = self.players[target_idx]
            # AI picks the card least likely to be Culprit (last card in hand)
            extra["accomplice_card_idx"] = 0
        if card.role_type == RoleType.SWAP and target_idx is not None:
            t = self.players[target_idx]
            extra["swap_their_idx"] = 0
            extra["swap_my_idx"]    = 0
        if card.role_type == RoleType.SHARE:
            extra["share_card_idx"] = 0
        if card.role_type == RoleType.FRENZY:
            extra["frenzy_card_idx"] = 0
        if card.role_type == RoleType.SOOTHSAYER:
            extra["soothsayer_text"] = "I think the culprit is hiding among us..."

        result = self.play_card(p_idx, card_idx, target_idx, extra)

        # For WITNESS/BABY/SOOTHSAYER, play_card skips advance_turn so AI must do it.
        # For all other results, play_card already advanced the turn.
        if result == "WITNESS" and target_idx is not None:
            target = self.players[target_idx]
            has_important = any(
                c.role_type in {RoleType.CULPRIT, RoleType.ACCOMPLICE}
                for c in target.hand
            )
            if has_important and player.hand and target.hand:
                t_idx = next(
                    (i for i, c in enumerate(target.hand)
                     if c.role_type in {RoleType.CULPRIT, RoleType.ACCOMPLICE}), 0
                )
                self._do_witness_swap(p_idx, target_idx, 0, t_idx)

        if result in ("WITNESS", "BABY", "SOOTHSAYER"):
            self.advance_turn()

        return {"card_index": card_idx, "target_index": target_idx, "result": result}

    # ------------------------------------------------------------------
    # Witness swap helper (called by both AI and UI)
    # ------------------------------------------------------------------

    def do_witness_swap(self, player_idx: int, target_idx: int,
                        my_card_idx: int, their_card_idx: int):
        """Execute the optional card swap after a Witness play."""
        self._do_witness_swap(player_idx, target_idx, my_card_idx, their_card_idx)
        self.advance_turn()

    def _do_witness_swap(self, player_idx: int, target_idx: int,
                         my_card_idx: int, their_card_idx: int):
        p = self.players[player_idx]
        t = self.players[target_idx]
        if not p.hand or not t.hand:
            return
        my_card_idx    = max(0, min(my_card_idx,    len(p.hand) - 1))
        their_card_idx = max(0, min(their_card_idx, len(t.hand) - 1))
        c1 = p.hand.pop(my_card_idx)
        c2 = t.hand.pop(their_card_idx)
        p.add_card(c2)
        t.add_card(c1)
        self.log(f"👁️ Witness swapped a card with {t.name}.")
