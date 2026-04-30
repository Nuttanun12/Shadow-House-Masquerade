from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QDialog, QScrollArea, QGraphicsOpacityEffect
)
from PyQt6.QtGui import (
    QPixmap, QColor, QFont, QPainter, QLinearGradient, QBrush, QPen
)
from PyQt6.QtCore import Qt, QTimer, QRect, QPoint
from game.engine import GameEngine
from game.models import RoleType
from ..components.card import CardWidget


# ---------------------------------------------------------------------------
# Target selection dialog
# ---------------------------------------------------------------------------

class TargetDialog(QDialog):
    def __init__(self, players, exclude_index: int, parent=None):
        super().__init__(parent)
        self.selected_index = None
        self.setWindowTitle("Choose a Target")
        self.setModal(True)
        self.setFixedSize(320, 300)
        self.setStyleSheet("""
            QDialog { background-color: #0d0020; border: 2px solid #7b00bb; border-radius: 12px; }
            QLabel { color: #e0c0ff; }
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #5a0090,stop:1 #3a0060);
                color: #fff; border: 1px solid #9040c0; border-radius: 8px;
                padding: 10px 20px; font-size: 13px; font-weight: bold; margin: 3px 10px;
            }
            QPushButton:hover { background: #7a00c0; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        title = QLabel("🎯  Select Your Target")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(self._sep())

        for i, player in enumerate(players):
            if i == exclude_index:
                continue
            parts = []
            if player.is_handcuffed: parts.append("🔒 Cuffed")
            if player.protected:     parts.append("🛡️ Protected")
            suffix = "  [" + ", ".join(parts) + "]" if parts else ""
            btn = QPushButton(player.name + suffix)
            btn.clicked.connect(lambda _, idx=i: self._select(idx))
            layout.addWidget(btn)

        layout.addStretch()
        cancel = QPushButton("✖  Cancel")
        cancel.setStyleSheet("background: #330000; border-color: #880000;")
        cancel.clicked.connect(self.reject)
        layout.addWidget(cancel)

    def _sep(self):
        f = QFrame(); f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet("color: #5a0090;"); return f

    def _select(self, index: int):
        self.selected_index = index; self.accept()


# ---------------------------------------------------------------------------
# Witness reveal dialog
# ---------------------------------------------------------------------------

class WitnessDialog(QDialog):
    def __init__(self, target_name: str, hand, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Witness — " + target_name + "'s Hand")
        self.setModal(True); self.setFixedSize(560, 280)
        self.setStyleSheet("""
            QDialog { background-color: #001a10; border: 2px solid #00bb60; border-radius: 12px; }
            QLabel { color: #90ffcc; }
        """)
        layout = QVBoxLayout(self)
        title = QLabel("👁  You secretly witness " + target_name + "'s hand:")
        title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        row = QHBoxLayout(); row.setAlignment(Qt.AlignmentFlag.AlignCenter); row.setSpacing(10)
        for card in hand:
            row.addWidget(CardWidget(card, is_hidden=False))
        layout.addLayout(row)
        ok = QPushButton("Close")
        ok.setStyleSheet("""
            QPushButton { background:#004020; color:#90ffcc; border:1px solid #00bb60;
                border-radius:8px; padding:8px 24px; }
            QPushButton:hover { background:#006030; }
        """)
        ok.clicked.connect(self.accept)
        layout.addWidget(ok, alignment=Qt.AlignmentFlag.AlignCenter)


# ---------------------------------------------------------------------------
# Player panel (top row – compact)
# ---------------------------------------------------------------------------

class PlayerPanel(QFrame):
    def __init__(self, player, is_human: bool = False, parent=None):
        super().__init__(parent)
        self.is_human = is_human
        self.setFixedSize(150, 100)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6); layout.setSpacing(3)

        name_row = QHBoxLayout()
        self.you_badge = QLabel("YOU")
        self.you_badge.setFixedSize(30, 16)
        self.you_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.you_badge.setStyleSheet(
            "background:#ffd700;color:#000;border-radius:3px;font-size:8px;font-weight:bold;")
        self.you_badge.setVisible(is_human)
        name_row.addWidget(self.you_badge)
        self.name_lbl = QLabel(player.name)
        self.name_lbl.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.name_lbl.setStyleSheet("color:#e0d0ff;"); self.name_lbl.setWordWrap(True)
        name_row.addWidget(self.name_lbl)
        layout.addLayout(name_row)

        self.cards_row = QHBoxLayout()
        self.cards_row.setAlignment(Qt.AlignmentFlag.AlignLeft); self.cards_row.setSpacing(3)
        layout.addLayout(self.cards_row)

        self.score_lbl = QLabel("⭐ 0 pts")
        self.score_lbl.setStyleSheet("color:gold;font-size:11px;")
        self.score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.score_lbl)

        self.status_lbl = QLabel("")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setFont(QFont("Arial", 10))
        layout.addWidget(self.status_lbl)

        self._apply_style(False)

    def _apply_style(self, active: bool):
        if active:
            border, bg = "#ffd700", "rgba(60,40,0,0.75)"
        elif self.is_human:
            border, bg = "rgba(255,215,0,0.5)", "rgba(30,20,0,0.65)"
        else:
            border, bg = "rgba(160,80,255,0.4)", "rgba(0,0,0,0.55)"
        self.setStyleSheet(
            f"QFrame{{background:{bg};border:2px solid {border};border-radius:10px;}}"
            " QLabel{color:#ddd;}"
        )

    def refresh(self, player, is_active: bool):
        self._apply_style(is_active)
        self.name_lbl.setText(("▶ " if is_active else "") + player.name)
        while self.cards_row.count():
            item = self.cards_row.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for _ in range(min(len(player.hand), 5)):
            lbl = QLabel(); lbl.setFixedSize(14, 20)
            lbl.setStyleSheet("background:#3a0060;border:1px solid #9040c0;border-radius:2px;")
            self.cards_row.addWidget(lbl)
        if len(player.hand) > 5:
            self.cards_row.addWidget(QLabel("+" + str(len(player.hand) - 5)))
        self.score_lbl.setText("⭐ " + str(player.score) + " pts")
        badges = []
        if player.is_handcuffed: badges.append("🔒")
        if player.protected:     badges.append("🛡️")
        self.status_lbl.setText("  ".join(badges))


# ---------------------------------------------------------------------------
# Discard pile widget – draws cards fanned/stacked in the centre
# ---------------------------------------------------------------------------

class DiscardPileWidget(QWidget):
    """
    Renders a visual stack of played cards fanned slightly so you can see
    each card's colour band.  The topmost (most-recently played) card is
    fully visible; older cards peek out behind it.
    """

    FAN_OFFSET_X = 6   # horizontal shift per buried card
    FAN_OFFSET_Y = 4   # vertical shift per buried card
    MAX_SHOW    = 6    # max buried cards shown

    CARD_W = 110
    CARD_H = 165

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pile: list = []          # list of Card objects
        self.setMinimumSize(220, 220)

    def set_pile(self, cards: list):
        self._pile = list(cards)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self._pile:
            self._draw_empty(painter)
            return

        w, h = self.width(), self.height()
        cw, ch = self.CARD_W, self.CARD_H
        cx = (w - cw) // 2
        cy = (h - ch) // 2

        # Draw buried cards (oldest first, peeking behind)
        visible = self._pile[-(self.MAX_SHOW + 1):]   # up to MAX_SHOW+1 cards
        buried  = visible[:-1]                         # all but the last

        for depth, card in enumerate(reversed(buried)):
            n = len(buried) - depth           # 1-based from top-of-buried
            ox = cx - n * self.FAN_OFFSET_X
            oy = cy - n * self.FAN_OFFSET_Y
            self._draw_card_face(painter, card, ox, oy, cw, ch, alpha=180)

        # Draw the topmost card fully
        top = self._pile[-1]
        self._draw_card_face(painter, top, cx, cy, cw, ch, alpha=255)

        # Count label
        if len(self._pile) > 1:
            painter.setPen(QColor(255, 255, 255, 200))
            painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            painter.drawText(
                QRect(cx, cy + ch + 6, cw, 20),
                Qt.AlignmentFlag.AlignCenter,
                f"{len(self._pile)} cards played"
            )

    def _draw_card_face(self, painter: QPainter, card, x, y, w, h, alpha=255):
        bg = QColor(card.color if hasattr(card, "color") else "#1a1a2e")
        bg.setAlpha(alpha)
        txt = QColor(card.text_color if hasattr(card, "text_color") else "#ffffff")
        txt.setAlpha(alpha)

        grad = QLinearGradient(x, y, x, y + h)
        lighter = bg.lighter(140); lighter.setAlpha(alpha)
        grad.setColorAt(0, lighter)
        grad.setColorAt(1, bg)

        painter.setBrush(QBrush(grad))
        border = txt.darker(150); border.setAlpha(alpha)
        painter.setPen(QPen(border, 2))
        painter.drawRoundedRect(x + 2, y + 2, w - 4, h - 4, 10, 10)

        inner = QColor(txt); inner.setAlpha(min(alpha, 180))
        painter.setPen(QPen(inner, 1))
        painter.drawRoundedRect(x + 6, y + 6, w - 12, h - 12, 7, 7)

        # Banner
        ban_col = txt.darker(200); ban_col.setAlpha(alpha)
        painter.setBrush(QBrush(ban_col))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(x + 10, y + 10, w - 20, 26, 5, 5)

        painter.setPen(txt)
        painter.setFont(QFont("Arial", 7, QFont.Weight.Bold))
        painter.drawText(QRect(x + 10, y + 10, w - 20, 26),
                         Qt.AlignmentFlag.AlignCenter, card.name.upper())

    def _draw_empty(self, painter: QPainter):
        w, h = self.width(), self.height()
        cw, ch = self.CARD_W, self.CARD_H
        x, y = (w - cw) // 2, (h - ch) // 2
        painter.setBrush(QBrush(QColor(30, 0, 50, 80)))
        painter.setPen(QPen(QColor(120, 0, 200, 100), 2, Qt.PenStyle.DashLine))
        painter.drawRoundedRect(x + 2, y + 2, cw - 4, ch - 4, 10, 10)
        painter.setPen(QColor(160, 100, 255, 120))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(QRect(x, y, cw, ch), Qt.AlignmentFlag.AlignCenter, "No cards\nplayed yet")


# ---------------------------------------------------------------------------
# Board Screen
# ---------------------------------------------------------------------------

class BoardScreen(QWidget):
    """
    Layout
    ──────
    ┌─────────────────────────────────────────────────────┐
    │  Round X          [Turn Label]             [Menu]   │
    ├─────────────────────────────────────────────────────┤
    │  [AI 1]  [AI 2]  [AI 3]  …  (opponent panels)      │
    ├─────────────────────────────────────────────────────┤
    │  Game Log (scrollable, left)  │  Discard pile (right│
    │                               │  stacked cards)     │
    ├─────────────────────────────────────────────────────┤
    │  ── Your Hand ──  [Card] [Card] [Card] [Card]       │  ← bottom bar
    └─────────────────────────────────────────────────────┘
    """

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.engine = None
        self._all_panels = []
        self._pending_witness = None
        self._init_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──────────────────────────────────────────────────────
        header_wrap = QWidget()
        header_wrap.setStyleSheet("background: rgba(0,0,0,0.55);")
        header_wrap.setFixedHeight(48)
        header = QHBoxLayout(header_wrap)
        header.setContentsMargins(16, 0, 16, 0)

        self.round_label = QLabel("Round 1")
        self.round_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.round_label.setStyleSheet("color: gold;")
        header.addWidget(self.round_label)
        header.addStretch()

        self.turn_label = QLabel("")
        self.turn_label.setFont(QFont("Arial", 12))
        self.turn_label.setStyleSheet("color: #e0c0ff;")
        header.addWidget(self.turn_label)
        header.addStretch()

        menu_btn = QPushButton("⬅  Menu")
        menu_btn.setStyleSheet("""
            QPushButton { background:rgba(60,0,0,0.7); color:#ff8080;
                border:1px solid #880000; border-radius:6px; padding:6px 14px; }
            QPushButton:hover { background:rgba(120,0,0,0.85); }
        """)
        menu_btn.clicked.connect(self._confirm_quit)
        header.addWidget(menu_btn)
        root.addWidget(header_wrap)

        # ── Opponent panels row ──────────────────────────────────────────
        opp_scroll = QScrollArea()
        opp_scroll.setFixedHeight(115)
        opp_scroll.setWidgetResizable(True)
        opp_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        opp_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        opp_scroll.setStyleSheet("background:transparent;border:none;")
        self.players_container = QWidget()
        self.players_layout = QHBoxLayout(self.players_container)
        self.players_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.players_layout.setSpacing(10)
        self.players_layout.setContentsMargins(12, 6, 12, 6)
        opp_scroll.setWidget(self.players_container)
        root.addWidget(opp_scroll)

        root.addWidget(self._h_line())

        # ── Middle area: log + discard pile ─────────────────────────────
        middle = QHBoxLayout()
        middle.setContentsMargins(12, 8, 12, 8)
        middle.setSpacing(12)

        # Game log (left side)
        log_wrap = QVBoxLayout()
        log_title = QLabel("📜  Game Log")
        log_title.setStyleSheet("color:rgba(200,180,255,0.7);font-size:10px;letter-spacing:1px;")
        log_wrap.addWidget(log_title)

        self.log_scroll = QScrollArea()
        self.log_scroll.setWidgetResizable(True)
        self.log_scroll.setStyleSheet(
            "background:rgba(0,0,0,0.40);border:1px solid #3a0060;border-radius:8px;")
        self.log_container = QWidget()
        self.log_layout = QVBoxLayout(self.log_container)
        self.log_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.log_layout.setSpacing(1)
        self.log_scroll.setWidget(self.log_container)
        log_wrap.addWidget(self.log_scroll, stretch=1)
        middle.addLayout(log_wrap, stretch=2)

        # Discard pile (right side)
        pile_wrap = QVBoxLayout()
        pile_wrap.setAlignment(Qt.AlignmentFlag.AlignTop)
        pile_title = QLabel("🃏  Played Cards")
        pile_title.setStyleSheet("color:rgba(200,180,255,0.7);font-size:10px;letter-spacing:1px;")
        pile_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pile_wrap.addWidget(pile_title)

        self.discard_widget = DiscardPileWidget()
        pile_wrap.addWidget(self.discard_widget, stretch=1)
        middle.addLayout(pile_wrap, stretch=1)

        root.addLayout(middle, stretch=1)

        root.addWidget(self._h_line())

        # ── Player hand bar (bottom) ─────────────────────────────────────
        hand_bar = QWidget()
        hand_bar.setObjectName("hand_bar")
        hand_bar.setStyleSheet("""
            #hand_bar {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 rgba(20,0,40,0.92), stop:1 rgba(5,0,15,0.98));
                border-top: 2px solid rgba(160,0,255,0.5);
            }
        """)
        hand_bar.setFixedHeight(240)

        hand_v = QVBoxLayout(hand_bar)
        hand_v.setContentsMargins(12, 8, 12, 12)
        hand_v.setSpacing(6)

        your_label = QLabel("✋  Your Hand  —  click a card to play it")
        your_label.setStyleSheet(
            "color:rgba(200,180,255,0.8);font-size:11px;letter-spacing:1px;"
        )
        your_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hand_v.addWidget(your_label)

        self.hand_container = QWidget()
        self.hand_layout = QHBoxLayout(self.hand_container)
        self.hand_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hand_layout.setSpacing(18)
        hand_v.addWidget(self.hand_container, stretch=1)

        root.addWidget(hand_bar)
        self.setLayout(root)

    def _h_line(self):
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color:rgba(120,0,200,0.3);"); return line

    # ------------------------------------------------------------------
    # Background
    # ------------------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        bg = QPixmap("resources/images/board_bg.png")
        if not bg.isNull():
            bg = bg.scaled(self.size(),
                           Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                           Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(0, 0, bg)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor(0, 0, 0, 155))
        grad.setColorAt(1, QColor(8, 0, 22, 185))
        painter.fillRect(self.rect(), grad)

    # ------------------------------------------------------------------
    # Game control
    # ------------------------------------------------------------------

    def start_game(self, player_names, ai_count):
        self.engine = GameEngine(player_names, ai_count)
        self.engine.setup_round()
        self._build_player_panels()
        self.refresh_board()

    def _build_player_panels(self):
        while self.players_layout.count():
            item = self.players_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self._all_panels = []
        for i, player in enumerate(self.engine.players):
            is_human = (i == 0)
            panel = PlayerPanel(player, is_human=is_human)
            self._all_panels.append((i, panel))
            self.players_layout.addWidget(panel)

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def refresh_board(self):
        if not self.engine:
            return

        current = self.engine.current_player
        self.round_label.setText("Round " + str(self.engine.round_number))
        self.turn_label.setText(
            "⬡  Your Turn" if self.engine.current_turn_index == 0
            else "⬡  " + current.name + "'s Turn"
        )

        for i, panel in self._all_panels:
            panel.refresh(self.engine.players[i], i == self.engine.current_turn_index)

        # Game log
        while self.log_layout.count():
            item = self.log_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for msg in self.engine.logs[-8:]:
            lbl = QLabel(msg)
            lbl.setStyleSheet("color:#c8c8c8;font-size:10px;padding:1px 8px;")
            lbl.setWordWrap(True)
            self.log_layout.addWidget(lbl)
        self.log_scroll.verticalScrollBar().setValue(
            self.log_scroll.verticalScrollBar().maximum())

        # Discard pile
        self.discard_widget.set_pile(self.engine.discard_pile)

        # Human hand
        while self.hand_layout.count():
            item = self.hand_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        human = self.engine.players[0]
        for i, card in enumerate(human.hand):
            cw = CardWidget(card, is_hidden=False, parent=self)
            cw.index = i
            cw.setFixedSize(130, 195)
            self.hand_layout.addWidget(cw)

        # Pending witness dialog
        if self._pending_witness:
            target_name, hand = self._pending_witness
            self._pending_witness = None
            dlg = WitnessDialog(target_name, hand, self)
            dlg.exec()

        # Game over
        if self.engine.game_over:
            winner = self.engine.winner
            scores = "\n".join(
                "  " + p.name + ": " + str(p.score) + " pts"
                for p in self.engine.players
            )
            QMessageBox.information(
                self, "🏆 Masquerade Ends!",
                winner.name + " wins the Shadow House Masquerade!\n\nFinal Scores:\n" + scores,
            )
            self.main_window.show_stats()
            return

        if self.engine.current_turn_index != 0 and not self.engine.game_over:
            QTimer.singleShot(1400, self._ai_turn)

    # ------------------------------------------------------------------
    # AI turn
    # ------------------------------------------------------------------

    def _ai_turn(self):
        if not self.engine or self.engine.game_over: return
        if self.engine.current_turn_index == 0: return
        self.engine.ai_play()
        self.refresh_board()

    # ------------------------------------------------------------------
    # Human card click
    # ------------------------------------------------------------------

    def card_clicked(self, card_widget):
        if not self.engine or self.engine.current_turn_index != 0:
            return
        card = self.engine.players[0].hand[card_widget.index]
        requires_target = card.role_type in {
            RoleType.DETECTIVE, RoleType.TOBY, RoleType.SHERIFF, RoleType.WITNESS,
        }
        target_idx = None
        if requires_target:
            dlg = TargetDialog(self.engine.players, exclude_index=0, parent=self)
            if dlg.exec() != QDialog.DialogCode.Accepted or dlg.selected_index is None:
                return
            target_idx = dlg.selected_index

        witness_target = None
        if card.role_type == RoleType.WITNESS and target_idx is not None:
            witness_target = self.engine.players[target_idx]

        result = self.engine.play_card(0, card_widget.index, target_idx)
        if result == "WITNESS" and witness_target is not None:
            self._pending_witness = (witness_target.name, list(witness_target.hand))

        self.refresh_board()

    # ------------------------------------------------------------------
    # Quit
    # ------------------------------------------------------------------

    def _confirm_quit(self):
        reply = QMessageBox.question(
            self, "Leave Game?",
            "Return to the main menu? Current game progress will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.main_window.show_menu()
