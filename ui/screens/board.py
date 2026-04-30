from __future__ import annotations
import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QDialog, QScrollArea
)
from PyQt6.QtGui import (
    QPixmap, QColor, QFont, QPainter, QLinearGradient, QBrush, QPen
)
from PyQt6.QtCore import Qt, QTimer, QRect
from game.engine import GameEngine
from game.models import RoleType
from ..components.card import CardWidget
from ..components.dialogs import (
    TobySnoopDialog, WitnessSwapDialog, PickHandCardDialog,
    SoothsayerDialog, BabyRevealDialog, TargetDialog
)


# ---------------------------------------------------------------------------
# Board Screen
# ---------------------------------------------------------------------------


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
        if player.has_handcuffs:   badges.append("🔒")
        if player.servant_protected or player.housekeeper_protected: badges.append("🛡️")
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

    FAN_OFFSET_X = 8   # horizontal shift per buried card
    FAN_OFFSET_Y = 6   # vertical shift per buried card
    MAX_SHOW    = 6    # max buried cards shown

    CARD_W = 140
    CARD_H = 210

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pile: list = []          # list of Card objects
        self.setMinimumSize(320, 320)

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

        # Emoji
        painter.setFont(QFont("Segoe UI Emoji", 32))
        painter.drawText(QRect(x, y + 45, w, 70),
                         Qt.AlignmentFlag.AlignCenter, getattr(card, "emoji", "❓"))

        # Details (Description)
        painter.setFont(QFont("Arial", 8))
        painter.setPen(txt.lighter(130))
        painter.drawText(QRect(x + 12, y + 120, w - 24, h - 125),
                         Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
                         getattr(card, "description", ""))

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

        fs_btn = QPushButton("📺  FULLSCREEN")
        fs_btn.setFixedWidth(110)
        fs_btn.setStyleSheet("""
            QPushButton { background:rgba(60,0,100,0.6); color:white; border-radius:4px; font-size:10px; font-weight:bold; }
            QPushButton:hover { background:rgba(80,0,140,0.8); }
        """)
        fs_btn.clicked.connect(self.main_window.toggle_fullscreen)
        header.addWidget(fs_btn)

        menu_btn = QPushButton("🚪  EXIT")
        menu_btn.setFixedWidth(80)
        menu_btn.setStyleSheet("""
            QPushButton { background:rgba(80,0,0,0.7); color:white; border-radius:4px; font-size:10px; font-weight:bold; }
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
        log_title.setStyleSheet("color:rgba(200,180,255,0.9);font-size:12px;font-weight:bold;letter-spacing:1px;padding-bottom:4px;")
        log_wrap.addWidget(log_title)

        self.log_scroll = QScrollArea()
        self.log_scroll.setWidgetResizable(True)
        self.log_scroll.setStyleSheet(
            "background:rgba(0,0,0,0.40);border:1px solid #3a0060;border-radius:8px;")
        self.log_container = QWidget()
        self.log_layout = QVBoxLayout(self.log_container)
        self.log_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.log_layout.setSpacing(1)
        self.log_layout.setContentsMargins(0, 0, 0, 0)
        self.log_scroll.setWidget(self.log_container)
        log_wrap.addWidget(self.log_scroll, stretch=1)
        middle.addLayout(log_wrap, stretch=3) # Increased stretch for log area

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

        if self.engine.fos_must_play and self.engine.current_turn_index == 0:
            self.turn_label.setText("🕵️  Play 'First on Scene' to start the round!")
            self.turn_label.setStyleSheet("color: gold; font-weight: bold;")
        elif self.engine.fos_must_play:
            self.turn_label.setText("🕵️  " + self.engine.current_player.name + " must play First on Scene…")
            self.turn_label.setStyleSheet("color: #ffd080; font-weight: bold;")
        elif self.engine.current_turn_index == 0:
            self.turn_label.setText("⬡  Your Turn")
            self.turn_label.setStyleSheet("color: #e0c0ff;")
        else:
            self.turn_label.setText("⬡  " + self.engine.current_player.name + "'s Turn")
            self.turn_label.setStyleSheet("color: #e0c0ff;")

        for i, panel in self._all_panels:
            panel.refresh(self.engine.players[i], i == self.engine.current_turn_index)

        # Game log
        while self.log_layout.count():
            item = self.log_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        
        # Show more logs (last 50) and make text bigger
        for msg in self.engine.logs[-50:]:
            lbl = QLabel(msg)
            lbl.setStyleSheet("color:#e0c0ff; font-size:13px; padding:3px 10px;")
            lbl.setWordWrap(True)
            self.log_layout.addWidget(lbl)
        
        # Add a flexible spacer at the bottom to push logs to the top
        self.log_layout.addStretch()

        # Force scroll to bottom after layout update
        QTimer.singleShot(50, lambda: self.log_scroll.verticalScrollBar().setValue(
            self.log_scroll.verticalScrollBar().maximum()))

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
            delay = random.randint(3000, 5000)
            self.turn_label.setText(
                "⏳  " + self.engine.current_player.name + " is thinking…"
            )
            self.turn_label.setStyleSheet("color: #a0a0a0; font-style: italic;")
            QTimer.singleShot(delay, self._ai_turn)

    # ------------------------------------------------------------------
    # AI turn
    # ------------------------------------------------------------------

    def _ai_turn(self):
        if not self.engine or self.engine.game_over: return
        if self.engine.current_turn_index == 0: return
        # Skip if current AI has no cards (edge case after Share/Frenzy)
        current = self.engine.players[self.engine.current_turn_index]
        if not current.hand:
            self.engine.advance_turn()
            self.refresh_board()
            return
        try:
            self.engine.ai_play()
        except Exception as e:
            self.engine.log(f"⚠️ AI error: {e} — skipping turn.")
            self.engine.advance_turn()
        self.refresh_board()

    # ------------------------------------------------------------------
    # Human card click
    # ------------------------------------------------------------------

    def card_clicked(self, card_widget):
        if not self.engine or self.engine.current_turn_index != 0:
            return

        human = self.engine.players[0]
        if card_widget.index >= len(human.hand):
            return
        card = human.hand[card_widget.index]

        # Block non-FoS card if First on Scene must be played first
        if self.engine.fos_must_play and card.role_type != RoleType.FIRST_ON_SCENE:
            QMessageBox.information(self, "🕵️ First on Scene",
                "You must play the 'First on Scene' card to open this round!\n"
                "Click the First on Scene card in your hand.")
            return

        # Block Culprit if not last card
        if card.role_type == RoleType.CULPRIT and len(human.hand) > 1:
            QMessageBox.warning(self, "Cannot Play",
                "You can only play the Culprit card when it is your LAST card!")
            return

        # Cards that need a target player
        needs_target = card.role_type in {
            RoleType.DETECTIVE, RoleType.TOBY, RoleType.SHERIFF,
            RoleType.WITNESS, RoleType.ACCOMPLICE, RoleType.SWAP,
        }
        target_idx = None
        if needs_target:
            dlg = TargetDialog(self.engine.players, exclude_index=0, parent=self)
            if dlg.exec() != QDialog.DialogCode.Accepted or dlg.selected_index is None:
                return
            target_idx = dlg.selected_index

        extra: dict = {}

        # TOBY: pick which card to reveal
        if card.role_type == RoleType.TOBY and target_idx is not None:
            t = self.engine.players[target_idx]
            dlg2 = TobySnoopDialog(t.name, len(t.hand), self)
            if dlg2.exec() != QDialog.DialogCode.Accepted or dlg2.chosen_idx is None:
                return
            extra["toby_card_idx"] = dlg2.chosen_idx

        # SHARE / FRENZY: pick which card to pass
        if card.role_type in (RoleType.SHARE, RoleType.FRENZY):
            key = "share_card_idx" if card.role_type == RoleType.SHARE else "frenzy_card_idx"
            label = "Pass to left" if card.role_type == RoleType.SHARE else "Contribute to pool"
            dlg3 = PickHandCardDialog(card.name, f"Which card to {label}?", human.hand, self)
            if dlg3.exec() != QDialog.DialogCode.Accepted or dlg3.chosen_idx is None:
                return
            extra[key] = dlg3.chosen_idx

        # SWAP: player picks which card to give (exclude the Swap card itself)
        if card.role_type == RoleType.SWAP and target_idx is not None:
            swap_card_pos = card_widget.index   # position of Swap card in current hand
            # Build list of (real_hand_idx, card) excluding the Swap card
            other_cards = [(ri, c) for ri, c in enumerate(human.hand) if ri != swap_card_pos]
            if not other_cards:
                QMessageBox.information(self, "Swap", "No other cards to give!")
                return
            dlg4 = PickHandCardDialog("Swap", "Which card do YOU give?",
                                      [c for _, c in other_cards], self)
            if dlg4.exec() != QDialog.DialogCode.Accepted or dlg4.chosen_idx is None:
                return
            # Map dialog index → real hand index, then adjust for Swap card removal
            real_idx = other_cards[dlg4.chosen_idx][0]
            # play_card will pop swap_card_pos first, so indices above it shift down by 1
            adjusted_idx = real_idx - 1 if real_idx > swap_card_pos else real_idx
            
            extra["swap_my_idx"] = adjusted_idx
            # Target (AI) "chooses" a random card to give you
            target_p = self.engine.players[target_idx]
            if target_p.hand:
                extra["swap_their_idx"] = random.randint(0, len(target_p.hand) - 1)
            else:
                extra["swap_their_idx"] = 0

        # SOOTHSAYER: enter text
        if card.role_type == RoleType.SOOTHSAYER:
            dlg5 = SoothsayerDialog(human.name, self)
            if dlg5.exec() != QDialog.DialogCode.Accepted:
                return
            extra["soothsayer_text"] = dlg5.text

        # Snapshot witness target before card consumed
        witness_target = None
        if card.role_type == RoleType.WITNESS and target_idx is not None:
            witness_target = self.engine.players[target_idx]

        # Reset swap notification tracker
        self.engine.last_swap_received = None

        result = self.engine.play_card(0, card_widget.index, target_idx, extra)

        # Show notification if a Swap card gave us something new
        if self.engine.last_swap_received:
            QMessageBox.information(self, "🔄 Card Swapped", 
                                   f"You received a **{self.engine.last_swap_received}**!")
            self.engine.last_swap_received = None

        # WITNESS: show hand, optionally swap
        if result == "WITNESS" and witness_target is not None:
            wdlg = WitnessSwapDialog(
                witness_target.name,
                list(witness_target.hand),
                list(human.hand),
                self,
            )
            if wdlg.exec() == QDialog.DialogCode.Accepted and wdlg.do_swap:
                self.engine.do_witness_swap(
                    0, target_idx, wdlg.my_idx, wdlg.their_idx
                )
            else:
                self.engine.advance_turn()

        # BABY OF FAMILY: brief reveal
        elif result == "BABY":
            is_culprit = human.has_role(RoleType.CULPRIT)
            BabyRevealDialog(is_culprit, self).exec()
            self.engine.advance_turn()

        # SOOTHSAYER: just advance
        elif result == "SOOTHSAYER":
            self.engine.advance_turn()

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
