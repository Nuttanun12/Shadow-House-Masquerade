import random
from .models import RoleType, Card, Player

class GameEngine:
    def __init__(self, player_names, ai_count=0):
        self.players = [Player(name) for name in player_names]
        for i in range(ai_count):
            self.players.append(Player(f"AI_{i+1}", is_ai=True))
            
        self.deck = []
        self.current_turn_index = 0
        self.round_number = 1
        self.game_over = False
        self.winner = None
        self.logs = []

    def log(self, message):
        self.logs.append(message)
        print(message)

    def setup_round(self):
        self.log(f"--- Round {self.round_number} ---")
        self.create_deck()
        random.shuffle(self.deck)
        
        # Clear hands
        for p in self.players:
            p.hand = []
            p.is_handcuffed = False
            p.protected = False

        # Deal 4 cards to each player
        for _ in range(4):
            for p in self.players:
                if self.deck:
                    p.add_card(self.deck.pop())

        # Determine who starts
        for i, p in enumerate(self.players):
            if p.has_role(RoleType.FIRST_ON_SCENE):
                self.current_turn_index = i
                break
        else:
            self.current_turn_index = random.randint(0, len(self.players) - 1)

    def create_deck(self):
        # Basic deck setup based on player count
        # In a real implementation, this would follow the rulebook exactly
        num_players = len(self.players)
        self.deck = []
        
        # Core cards
        self.deck.append(Card(RoleType.CULPRIT, "Culprit", "If you are caught, you lose. If you play this last, you win."))
        self.deck.append(Card(RoleType.DETECTIVE, "Detective", "Choose a player. If they have the Culprit, the round ends."))
        self.deck.append(Card(RoleType.ACCOMPLICE, "Accomplice", "You win if the Culprit wins."))
        self.deck.append(Card(RoleType.FIRST_ON_SCENE, "First on Scene", "You start the round."))
        
        # Fill rest with Alibi, Toby, Sheriff, etc.
        extra_roles = [
            (RoleType.ALIBI, "Alibi", "Protects you from being exposed."),
            (RoleType.TOBY, "Toby", "Reveal a specific card from another player."),
            (RoleType.SHERIFF, "Sheriff", "Place handcuffs on a player."),
            (RoleType.WITNESS, "Witness", "Look at a player's hand."),
            (RoleType.SERVANT, "Servant", "You are protected until your next turn."),
            (RoleType.CITIZEN, "Citizen", "No special effect.")
        ]
        
        needed = (num_players * 4) - len(self.deck)
        for _ in range(needed):
            role = random.choice(extra_roles)
            self.deck.append(Card(role[0], role[1], role[2]))

    def next_turn(self):
        self.current_turn_index = (self.current_turn_index + 1) % len(self.players)
        # Reset protection for the player whose turn it is
        self.players[self.current_turn_index].protected = False

    def play_card(self, player_index, card_index, target_player_index=None):
        player = self.players[player_index]
        card = player.hand.pop(card_index)
        self.log(f"{player.name} played {card.name}")
        
        result = self.resolve_card_effect(player, card, target_player_index)
        
        # Check round end conditions
        if result == "ROUND_END":
            self.end_round()
        elif not any(p.hand for p in self.players):
            self.end_round()
        else:
            self.next_turn()
            
    def resolve_card_effect(self, player, card, target_index):
        # Basic implementation of effects
        if card.role_type == RoleType.DETECTIVE:
            if target_index is not None:
                target = self.players[target_index]
                if target.protected:
                    self.log(f"Detective was blocked by {target.name}'s protection!")
                    return "CONTINUE"
                if target.has_role(RoleType.CULPRIT):
                    self.log(f"Detective found the Culprit in {target.name}'s hand!")
                    return "ROUND_END"
                else:
                    self.log(f"Detective failed. {target.name} does not have the Culprit.")
        
        elif card.role_type == RoleType.TOBY:
            if target_index is not None:
                target = self.players[target_index]
                if target.protected:
                    self.log(f"Toby was chased away by {target.name}'s protection!")
                    return "CONTINUE"
                self.log(f"Toby sniffs around {target.name}...")
                if target.has_role(RoleType.CULPRIT):
                    self.log(f"Toby found the Culprit!")
                    return "ROUND_END"
                else:
                    self.log(f"Toby found nothing.")

        elif card.role_type == RoleType.SHERIFF:
            if target_index is not None:
                self.players[target_index].is_handcuffed = True
                self.log(f"{self.players[target_index].name} has been handcuffed!")

        elif card.role_type == RoleType.WITNESS:
            if target_index is not None:
                target = self.players[target_index]
                hand_names = [c.name for c in target.hand]
                self.log(f"{player.name} witnessed {target.name}'s hand: {', '.join(hand_names)}")

        elif card.role_type == RoleType.SERVANT or card.role_type == RoleType.ALIBI:
            player.protected = True
            self.log(f"{player.name} is now protected until their next turn.")

        elif card.role_type == RoleType.CITIZEN:
             # Randomly swap a card with someone else (Custom rule for more fun)
             if len(self.players) > 1:
                 other_idx = (self.players.index(player) + 1) % len(self.players)
                 other = self.players[other_idx]
                 if player.hand and other.hand:
                     c1 = player.hand.pop(0)
                     c2 = other.hand.pop(0)
                     player.add_card(c2)
                     other.add_card(c1)
                     self.log(f"{player.name} swapped cards with {other.name}!")

        return "CONTINUE"

    def end_round(self):
        # Scoring logic
        culprit_player = None
        for p in self.players:
            if p.has_role(RoleType.CULPRIT):
                culprit_player = p
                break
        
        if not culprit_player:
            self.log("ERROR: No culprit found at end of round!")
            self.setup_round()
            return

        # Determine winner of round
        if culprit_player.is_handcuffed:
            self.log(f"VICTORY: The Culprit ({culprit_player.name}) was handcuffed!")
            for p in self.players:
                if p != culprit_player and not p.has_role(RoleType.ACCOMPLICE):
                    p.score += 1
        else:
            # Check if culprit escaped (played all cards or round ended without arrest)
            self.log(f"DEFEAT: The Culprit ({culprit_player.name}) escaped!")
            culprit_player.score += 2
            for p in self.players:
                if p.has_role(RoleType.ACCOMPLICE) and p != culprit_player:
                    p.score += 1

        # Check game winner
        for p in self.players:
            if p.score >= 5:
                self.game_over = True
                self.winner = p
                self.log(f"GAME OVER: {p.name} WINS THE MASQUERADE!")
                
                # Record to DB
                from storage.database import DatabaseManager
                db = DatabaseManager()
                scores = {pl.name: pl.score for pl in self.engine.players} if hasattr(self, 'engine') else {pl.name: pl.score for pl in self.players}
                db.record_game(p.name, scores)
                for pl in self.players:
                    db.update_player_stats(pl.name, pl == p, pl.score)
                break
        
        if not self.game_over:
            self.setup_round()
