from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox
from PyQt6.QtGui import QPixmap, QPalette, QBrush
from PyQt6.QtCore import Qt, QTimer
from game.engine import GameEngine
from game.models import RoleType
from ..components.card import CardWidget

class BoardScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.engine = None
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        
        # Header Info
        header = QHBoxLayout()
        self.status_label = QLabel("Waiting for game...")
        self.status_label.setStyleSheet("color: gold; font-size: 20px; font-weight: bold;")
        header.addWidget(self.status_label)
        
        self.score_label = QLabel("Scores: ")
        self.score_label.setStyleSheet("color: white; font-size: 16px;")
        header.addWidget(self.score_label)
        
        self.layout.addLayout(header)
        
        # Opponents Area
        self.opponents_layout = QHBoxLayout()
        self.layout.addLayout(self.opponents_layout)
        
        self.layout.addStretch()
        
        # Logs Area
        self.log_label = QLabel("Game Started")
        self.log_label.setStyleSheet("color: #ccc; font-style: italic; background: rgba(0,0,0,0.5); padding: 5px;")
        self.layout.addWidget(self.log_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Player Area (Hand)
        self.hand_container = QFrame()
        self.hand_container.setFixedHeight(220)
        self.hand_layout = QHBoxLayout()
        self.hand_container.setLayout(self.hand_layout)
        self.layout.addWidget(self.hand_container)
        
        self.setLayout(self.layout)

    def start_game(self, player_names, ai_count):
        self.engine = GameEngine(player_names, ai_count)
        self.engine.setup_round()
        self.refresh_board()

    def refresh_board(self):
        # Update status
        current_player = self.engine.players[self.engine.current_turn_index]
        self.status_label.setText(f"Round {self.engine.round_number} - {current_player.name}'s Turn")
        
        # Update scores
        scores = ", ".join([f"{p.name}: {p.score}" for p in self.engine.players])
        self.score_label.setText(f"Scores: {scores}")
        
        # Update logs
        if self.engine.logs:
            self.log_label.setText(self.engine.logs[-1])

        # Clear layouts
        self.clear_layout(self.opponents_layout)
        self.clear_layout(self.hand_layout)
        
        # Draw opponents
        for i, player in enumerate(self.engine.players):
            if i == 0: continue # Skip human (assuming player 0)
            p_widget = QVBoxLayout()
            p_label = QLabel(f"{player.name}\n({len(player.hand)} cards)")
            p_label.setStyleSheet("color: white; text-align: center;")
            p_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            p_widget.addWidget(p_label)
            
            # Simple card representation
            cards_box = QHBoxLayout()
            for _ in range(len(player.hand)):
                c = QLabel()
                c.setFixedSize(30, 45)
                c.setPixmap(QPixmap("resources/images/card_back.png").scaled(30, 45))
                cards_box.addWidget(c)
            p_widget.addLayout(cards_box)
            
            container = QWidget()
            container.setLayout(p_widget)
            self.opponents_layout.addWidget(container)

        # Draw human player's hand
        human = self.engine.players[0]
        for i, card in enumerate(human.hand):
            c_widget = CardWidget(card, is_hidden=False, parent=self)
            c_widget.index = i
            self.hand_layout.addWidget(c_widget)
            
        if self.engine.game_over:
            QMessageBox.information(self, "Game Over", f"The game is over! {self.engine.winner.name} is the winner of the Masquerade.")
            self.main_window.show_stats()
            return

        if self.engine.current_turn_index != 0:
            # AI's turn
            QTimer.singleShot(1500, self.ai_turn)

    def ai_turn(self):
        if self.engine.game_over: return
        p_idx = self.engine.current_turn_index
        player = self.engine.players[p_idx]
        
        # Slightly smarter AI
        card_idx = 0
        if player.has_role(RoleType.CULPRIT):
            # Try to find a defensive card if possible
            for i, c in enumerate(player.hand):
                if c.role_type in [RoleType.ALIBI, RoleType.SERVANT]:
                    card_idx = i
                    break
        
        # Target logic
        target = 0 # Target human by default
        
        self.engine.play_card(p_idx, card_idx, target)
        self.refresh_board()

    def card_clicked(self, card_widget):
        if self.engine.current_turn_index == 0:
            # Human plays
            # For simplicity, target the next player
            target = 1 if len(self.engine.players) > 1 else 0
            self.engine.play_card(0, card_widget.index, target)
            self.refresh_board()

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def paintEvent(self, event):
        painter = QBrush(QPixmap("resources/images/board_bg.png").scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding))
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, painter)
        self.setPalette(palette)
