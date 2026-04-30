from __future__ import annotations
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QWidget, QFrame
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

_STYLE = """
QDialog { background:#0d0020; border:2px solid #7b00bb; border-radius:12px; }
QLabel  { color:#e0c0ff; }
QPushButton {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #5a0090,stop:1 #3a0060);
    color:#fff; border:1px solid #9040c0; border-radius:8px;
    padding:8px 18px; font-size:12px; font-weight:bold; margin:3px 8px;
}
QPushButton:hover { background:#7a00c0; }
"""


def _sep():
    f = QFrame(); f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet("color:#5a0090;"); return f


class TobySnoopDialog(QDialog):
    """Human picks which card (by position) to reveal from target's hand."""
    def __init__(self, target_name: str, card_count: int, parent=None):
        super().__init__(parent)
        self.chosen_idx = None
        self.setWindowTitle("Toby — Snoop")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)
        self.setStyleSheet(_STYLE)
        
        main_lay = QVBoxLayout(self)
        
        title = QLabel(f"🐕  Snoop through {target_name}'s hand:")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffd700; margin: 10px;")
        title.setWordWrap(True)
        main_lay.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent; border:none;")
        scroll_widget = QWidget()
        lay = QVBoxLayout(scroll_widget)
        
        for i in range(card_count):
            btn = QPushButton(f"🃏  Face-down Card #{i + 1}")
            btn.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            btn.setFixedHeight(50)
            btn.clicked.connect(lambda _, x=i: self._pick(x))
            lay.addWidget(btn)
        
        scroll.setWidget(scroll_widget)
        main_lay.addWidget(scroll)

        cancel = QPushButton("✖ Cancel")
        cancel.setFixedHeight(45)
        cancel.setStyleSheet("background:#330000; border:1px solid #800; color:#ffb0b0; border-radius:10px;")
        cancel.clicked.connect(self.reject)
        main_lay.addWidget(cancel)

    def _pick(self, idx):
        self.chosen_idx = idx
        self.accept()


class TargetDialog(QDialog):
    """Pick which player to target."""
    def __init__(self, players, exclude_index: int, parent=None):
        super().__init__(parent)
        self.selected_index = None
        self.setWindowTitle("Select Target")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(450)
        self.setStyleSheet(_STYLE)
        
        main_lay = QVBoxLayout(self)
        
        title = QLabel("🎯  Choose Your Target:")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffd700; margin: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_lay.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent; border:none;")
        scroll_widget = QWidget()
        lay = QVBoxLayout(scroll_widget)
        
        for i, player in enumerate(players):
            if i == exclude_index:
                continue
            
            parts = []
            if player.has_handcuffs: parts.append("🔒 Cuffed")
            if player.servant_protected or player.housekeeper_protected: parts.append("🛡️ Protected")
            status = "  [" + ", ".join(parts) + "]" if parts else ""
            
            btn = QPushButton(f"👤  {player.name}{status}")
            btn.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            btn.setFixedHeight(55)
            btn.clicked.connect(lambda _, x=i: self._select(x))
            lay.addWidget(btn)
        
        scroll.setWidget(scroll_widget)
        main_lay.addWidget(scroll)

        cancel = QPushButton("✖ Cancel")
        cancel.setFixedHeight(45)
        cancel.setStyleSheet("background:#222; color:#888; border:1px solid #444; border-radius:10px;")
        cancel.clicked.connect(self.reject)
        main_lay.addWidget(cancel)

    def _select(self, idx):
        self.selected_index = idx
        self.accept()


class WitnessSwapDialog(QDialog):
    """After witnessing, ask player if they want to swap a card."""

    _SEL   = "background:#008000; border:2px solid #00ff80; color:#fff; font-weight:bold; border-radius:10px; padding:10px;"
    _UNSEL = "background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #4a0070,stop:1 #2a0040); " \
             "border:1px solid #7b00bb; color:#fff; border-radius:10px; padding:10px;"

    def __init__(self, target_name: str, target_hand, my_hand, parent=None):
        super().__init__(parent)
        self.do_swap   = False
        self.my_idx    = None
        self.their_idx = None
        self.setWindowTitle("Witness — Optional Swap")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        self.setStyleSheet(_STYLE)
        
        main_layout = QVBoxLayout(self)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent; border:none;")
        scroll_widget = QWidget()
        lay = QVBoxLayout(scroll_widget)
        lay.setContentsMargins(15, 15, 15, 15)
        lay.setSpacing(10)

        title_lbl = QLabel(f"👁  {target_name}'s hand (you secretly see):")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffd700;")
        lay.addWidget(title_lbl)
        
        for c in target_hand:
            emoji = getattr(c, "emoji", "🃏")
            lbl = QLabel(f"   {emoji}  {c.name}")
            lbl.setStyleSheet("font-size: 14px; padding: 2px;")
            lay.addWidget(lbl)
        
        lay.addWidget(_sep())

        # My card row
        header1 = QLabel("Select a card from YOUR hand to GIVE:")
        header1.setStyleSheet("font-weight: bold; color: #c084f5; font-size: 14px;")
        lay.addWidget(header1)
        
        self._my_status = QLabel("(no card selected)")
        self._my_status.setStyleSheet("color:#888; font-style:italic; font-size:12px;")
        lay.addWidget(self._my_status)
        
        self._my_btns = []
        for i, c in enumerate(my_hand):
            emoji = getattr(c, "emoji", "🃏")
            btn = QPushButton(f"{emoji}  {c.name}")
            btn.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            btn.setStyleSheet(self._UNSEL)
            btn.clicked.connect(lambda _, x=i, n=c.name, e=emoji: self._sel_my(x, n, e))
            lay.addWidget(btn)
            self._my_btns.append(btn)

        lay.addWidget(_sep())

        # Their card row
        header2 = QLabel(f"Select a card from {target_name}'s hand to TAKE:")
        header2.setStyleSheet("font-weight: bold; color: #c084f5; font-size: 14px;")
        lay.addWidget(header2)
        
        self._their_status = QLabel("(no card selected)")
        self._their_status.setStyleSheet("color:#888; font-style:italic; font-size:12px;")
        lay.addWidget(self._their_status)
        
        self._their_btns = []
        for i, c in enumerate(target_hand):
            emoji = getattr(c, "emoji", "🃏")
            btn = QPushButton(f"{emoji}  {c.name}")
            btn.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            btn.setStyleSheet(self._UNSEL)
            btn.clicked.connect(lambda _, x=i, n=c.name, e=emoji: self._sel_their(x, n, e))
            lay.addWidget(btn)
            self._their_btns.append(btn)

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        # Bottom buttons
        btn_box = QHBoxLayout()
        self._confirm_btn = QPushButton("✔ Confirm Swap")
        self._confirm_btn.setEnabled(False)
        self._confirm_btn.setFixedHeight(50)
        self._confirm_btn.setStyleSheet("background:#222; color:#555; border:1px solid #444; border-radius:10px;")
        self._confirm_btn.clicked.connect(self._confirm)
        
        skip = QPushButton("Skip (no swap)")
        skip.setFixedHeight(50)
        skip.setStyleSheet("background:#2a0a0a; border:1px solid #800; color:#ffb0b0; border-radius:10px;")
        skip.clicked.connect(self.accept)
        
        btn_box.addWidget(skip)
        btn_box.addWidget(self._confirm_btn)
        main_layout.addLayout(btn_box)

    def _sel_my(self, idx: int, name: str, emoji: str):
        self.my_idx = idx
        self._my_status.setText(f"✅ Give: {emoji} {name}")
        self._my_status.setStyleSheet("color:#00ff80; font-weight:bold; font-size:13px;")
        for i, b in enumerate(self._my_btns):
            b.setStyleSheet(self._SEL if i == idx else self._UNSEL)
        self._update_confirm()

    def _sel_their(self, idx: int, name: str, emoji: str):
        self.their_idx = idx
        self._their_status.setText(f"✅ Take: {emoji} {name}")
        self._their_status.setStyleSheet("color:#00ff80; font-weight:bold; font-size:13px;")
        for i, b in enumerate(self._their_btns):
            b.setStyleSheet(self._SEL if i == idx else self._UNSEL)
        self._update_confirm()

    def _update_confirm(self):
        ready = self.my_idx is not None and self.their_idx is not None
        self._confirm_btn.setEnabled(ready)
        if ready:
            self._confirm_btn.setStyleSheet(
                "background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #00aa00,stop:1 #006600);"
                "color:#fff; border:2px solid #00ff80; font-weight:bold; border-radius:10px;"
            )

    def _confirm(self):
        self.do_swap = True
        self.accept()


class PickHandCardDialog(QDialog):
    """
    Generic 'pick one card from your hand' dialog (SHARE, FRENZY, SWAP).
    Buttons stay visible; selected card is highlighted green with a checkmark.
    A Confirm button is enabled once a selection is made.
    """

    _SEL   = "background:#008000; border:2px solid #00ff80; color:#fff; font-weight:bold; border-radius:10px; padding:12px;"
    _UNSEL = "background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #4a0070,stop:1 #2a0040); " \
             "border:1px solid #7b00bb; color:#fff; border-radius:10px; padding:12px;"

    def __init__(self, card_name: str, instruction: str, hand, parent=None):
        super().__init__(parent)
        self.chosen_idx = None
        self.setWindowTitle(f"{card_name}")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(500)
        self.setStyleSheet(_STYLE)
        
        main_layout = QVBoxLayout(self)
        
        instr = QLabel(instruction)
        instr.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffd700; margin-bottom: 5px;")
        instr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(instr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent; border:none;")
        scroll_widget = QWidget()
        lay = QVBoxLayout(scroll_widget)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(8)

        self._btns = []
        for i, c in enumerate(hand):
            emoji = getattr(c, "emoji", "🃏")
            btn = QPushButton(f"{emoji}  {c.name}")
            btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            btn.setStyleSheet(self._UNSEL)
            btn.clicked.connect(lambda _, x=i, n=c.name, e=emoji: self._on_click(x, n, e))
            lay.addWidget(btn)
            self._btns.append(btn)
        
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        self._status = QLabel("(no card selected)")
        self._status.setStyleSheet("color:#888; font-style:italic; font-size:12px;")
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self._status)

        self._confirm_btn = QPushButton("✔ Confirm Selection")
        self._confirm_btn.setEnabled(False)
        self._confirm_btn.setFixedHeight(50)
        self._confirm_btn.setStyleSheet("background:#222; color:#555; border:1px solid #444; border-radius:10px;")
        self._confirm_btn.clicked.connect(self.accept)
        main_layout.addWidget(self._confirm_btn)

    def _on_click(self, idx: int, name: str, emoji: str):
        self.chosen_idx = idx
        self._status.setText(f"✅ Selected: {emoji} {name}")
        self._status.setStyleSheet("color:#00ff80; font-weight:bold; font-size:14px;")
        for i, b in enumerate(self._btns):
            b.setStyleSheet(self._SEL if i == idx else self._UNSEL)
        
        self._confirm_btn.setEnabled(True)
        self._confirm_btn.setStyleSheet(
            "background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #00aa00,stop:1 #006600);"
            "color:#fff; border:2px solid #00ff80; font-weight:bold; border-radius:10px;"
        )


class SoothsayerDialog(QDialog):
    """Player types their accusation."""
    def __init__(self, player_name: str, parent=None):
        super().__init__(parent)
        self.text = ""
        self.setWindowTitle("Soothsayer")
        self.setModal(True)
        self.setFixedSize(400, 240)
        self.setStyleSheet(_STYLE)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(15)

        title = QLabel(f"🔮  {player_name}, share your prophecy:")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #ffd700;")
        lay.addWidget(title)

        self._edit = QLineEdit()
        self._edit.setPlaceholderText("e.g. I think AI 2 is the culprit...")
        self._edit.setStyleSheet("""
            QLineEdit {
                background: #1a0030; color: white; border: 1px solid #9040c0; 
                border-radius: 8px; padding: 12px; font-size: 14px;
            }
        """)
        lay.addWidget(self._edit)
        
        ok = QPushButton("Declare Prophecy!")
        ok.setFixedHeight(50)
        ok.setStyleSheet("background:#7b00bb; color:white; font-weight:bold; border-radius:10px;")
        ok.clicked.connect(self._ok)
        lay.addWidget(ok)

    def _ok(self):
        self.text = self._edit.text() or "..."
        self.accept()


class BabyRevealDialog(QDialog):
    """Shown to the human only if they are the culprit."""
    def __init__(self, is_culprit: bool, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Baby of the Family")
        self.setModal(True)
        self.setFixedSize(400, 240)
        self.setStyleSheet(_STYLE)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(20)

        msg = QLabel()
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        msg.setStyleSheet("font-size: 15px; line-height: 1.4;")
        
        if is_culprit:
            msg.setText("👀  <b>You are the CULPRIT.</b><br><br>Don't reveal yourself — close your eyes now.")
        else:
            msg.setText("😴  <b>Close your eyes...</b><br><br>The culprit secretly signals.<br>Now everyone opens their eyes.")
        
        lay.addWidget(msg)
        
        ok = QPushButton("Understood")
        ok.setFixedHeight(45)
        ok.setStyleSheet("background:#c084f5; color:black; font-weight:bold; border-radius:10px;")
        ok.clicked.connect(self.accept)
        lay.addWidget(ok)
