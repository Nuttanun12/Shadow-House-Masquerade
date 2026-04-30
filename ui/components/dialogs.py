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
        self.setWindowTitle("Toby — Pick a Card to Reveal")
        self.setModal(True); self.setFixedSize(300, 80 + card_count * 48)
        self.setStyleSheet(_STYLE)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(f"🐕  Which card in {target_name}'s hand?"))
        lay.addWidget(_sep())
        for i in range(card_count):
            btn = QPushButton(f"Card #{i + 1}  (face-down)")
            btn.clicked.connect(lambda _, x=i: self._pick(x))
            lay.addWidget(btn)
        cancel = QPushButton("✖ Cancel"); cancel.setStyleSheet("background:#330000;")
        cancel.clicked.connect(self.reject); lay.addWidget(cancel)

    def _pick(self, idx):
        self.chosen_idx = idx; self.accept()


class WitnessSwapDialog(QDialog):
    """After witnessing, ask player if they want to swap a card."""

    _SEL   = "background:#006000;border:2px solid #00ff80;color:#fff;font-weight:bold;"
    _UNSEL = "background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #5a0090,stop:1 #3a0060);" \
             "border:1px solid #9040c0;color:#fff;"

    def __init__(self, target_name: str, target_hand, my_hand, parent=None):
        super().__init__(parent)
        self.do_swap   = False
        self.my_idx    = None
        self.their_idx = None
        self.setWindowTitle("Witness — Optional Swap")
        self.setModal(True)
        self.setFixedSize(460, 100 + (len(my_hand) + len(target_hand)) * 46 + 120)
        self.setStyleSheet(_STYLE)
        lay = QVBoxLayout(self)

        lay.addWidget(QLabel(f"👁  {target_name}'s hand (you secretly see):"))
        for i, c in enumerate(target_hand):
            lay.addWidget(QLabel(f"   → {c.name}"))
        lay.addWidget(_sep())

        # My card row
        lay.addWidget(QLabel("Your card to give:"))
        self._my_status = QLabel("(none selected)")
        self._my_status.setStyleSheet("color:#aaa;font-style:italic;")
        lay.addWidget(self._my_status)
        self._my_btns = []
        for i, c in enumerate(my_hand):
            btn = QPushButton(f"{c.name}")
            btn.setStyleSheet(self._UNSEL)
            btn.clicked.connect(lambda _, x=i, n=c.name: self._sel_my(x, n))
            lay.addWidget(btn)
            self._my_btns.append(btn)

        lay.addWidget(_sep())

        # Their card row
        lay.addWidget(QLabel("Their card to take:"))
        self._their_status = QLabel("(none selected)")
        self._their_status.setStyleSheet("color:#aaa;font-style:italic;")
        lay.addWidget(self._their_status)
        self._their_btns = []
        for i, c in enumerate(target_hand):
            btn = QPushButton(f"{c.name}")
            btn.setStyleSheet(self._UNSEL)
            btn.clicked.connect(lambda _, x=i, n=c.name: self._sel_their(x, n))
            lay.addWidget(btn)
            self._their_btns.append(btn)

        lay.addWidget(_sep())
        self._confirm_btn = QPushButton("✔ Confirm Swap")
        self._confirm_btn.setEnabled(False)
        self._confirm_btn.setStyleSheet("background:#333;color:#888;border:1px solid #555;")
        self._confirm_btn.clicked.connect(self._confirm)
        lay.addWidget(self._confirm_btn)

        skip = QPushButton("Skip (no swap)")
        skip.setStyleSheet("background:#220022;border-color:#660066;")
        skip.clicked.connect(self.accept)
        lay.addWidget(skip)

    def _sel_my(self, idx: int, name: str):
        self.my_idx = idx
        self._my_status.setText(f"✅ You give: {name}")
        self._my_status.setStyleSheet("color:#80ff80;font-weight:bold;")
        for i, b in enumerate(self._my_btns):
            b.setStyleSheet(self._SEL if i == idx else self._UNSEL)
            b.setText(("✔ " if i == idx else "") + b.text().lstrip("✔ "))
        self._update_confirm()

    def _sel_their(self, idx: int, name: str):
        self.their_idx = idx
        self._their_status.setText(f"✅ You take: {name}")
        self._their_status.setStyleSheet("color:#80ff80;font-weight:bold;")
        for i, b in enumerate(self._their_btns):
            b.setStyleSheet(self._SEL if i == idx else self._UNSEL)
            b.setText(("✔ " if i == idx else "") + b.text().lstrip("✔ "))
        self._update_confirm()

    def _update_confirm(self):
        ready = self.my_idx is not None and self.their_idx is not None
        self._confirm_btn.setEnabled(ready)
        if ready:
            self._confirm_btn.setStyleSheet(
                "background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #007000,stop:1 #004000);"
                "color:#fff;border:2px solid #00cc00;font-weight:bold;"
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

    _SEL   = "background:#006000;border:2px solid #00ff80;color:#fff;font-weight:bold;padding:8px 18px;border-radius:8px;"
    _UNSEL = "background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #5a0090,stop:1 #3a0060);" \
             "border:1px solid #9040c0;color:#fff;padding:8px 18px;border-radius:8px;"

    def __init__(self, title: str, prompt: str, hand, parent=None):
        super().__init__(parent)
        self.chosen_idx  = None
        self._card_names = [c.name for c in hand]
        self.setWindowTitle(title)
        self.setModal(True)
        # Extra height for status label + confirm button
        self.setFixedSize(340, 130 + len(hand) * 52)
        self.setStyleSheet(_STYLE)

        lay = QVBoxLayout(self)
        lay.setSpacing(6)

        lay.addWidget(QLabel(prompt))
        lay.addWidget(_sep())

        # Status label
        self._status = QLabel("(tap a card to select it)")
        self._status.setStyleSheet("color:#aaa;font-style:italic;font-size:11px;")
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self._status)

        # One button per card — stays visible, toggles highlight
        self._btns: list[QPushButton] = []
        for i, c in enumerate(hand):
            btn = QPushButton(f"{c.name}")
            btn.setStyleSheet(self._UNSEL)
            btn.clicked.connect(lambda _, x=i: self._pick(x))
            lay.addWidget(btn)
            self._btns.append(btn)

        lay.addWidget(_sep())

        # Confirm button (disabled until selection made)
        self._confirm = QPushButton("✔  Confirm")
        self._confirm.setEnabled(False)
        self._confirm.setStyleSheet("background:#333;color:#888;border:1px solid #555;padding:8px 18px;border-radius:8px;")
        self._confirm.clicked.connect(self.accept)
        lay.addWidget(self._confirm)

    def _pick(self, idx: int):
        self.chosen_idx = idx
        name = self._card_names[idx]

        # Update status label
        self._status.setText(f"✅ Selected: {name}")
        self._status.setStyleSheet("color:#80ff80;font-weight:bold;font-size:12px;")

        # Highlight selected, reset others
        for i, btn in enumerate(self._btns):
            if i == idx:
                btn.setStyleSheet(self._SEL)
                btn.setText(f"✔ {name}")
            else:
                btn.setStyleSheet(self._UNSEL)
                btn.setText(self._card_names[i])

        # Enable confirm button
        self._confirm.setEnabled(True)
        self._confirm.setStyleSheet(
            "background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #007000,stop:1 #004000);"
            "color:#fff;border:2px solid #00cc00;font-weight:bold;"
            "padding:8px 18px;border-radius:8px;"
        )


class SoothsayerDialog(QDialog):
    """Player types their accusation."""
    def __init__(self, player_name: str, parent=None):
        super().__init__(parent)
        self.text = ""
        self.setWindowTitle("Soothsayer"); self.setModal(True); self.setFixedSize(360, 180)
        self.setStyleSheet(_STYLE)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(f"🔮  {player_name}, share your thoughts:"))
        self._edit = QLineEdit(); self._edit.setPlaceholderText("e.g. I think AI 2 is the culprit...")
        self._edit.setStyleSheet("background:#1a0030;color:#e0c0ff;border:1px solid #9040c0;padding:4px;")
        lay.addWidget(self._edit)
        ok = QPushButton("Declare!"); ok.clicked.connect(self._ok); lay.addWidget(ok)

    def _ok(self):
        self.text = self._edit.text() or "..."; self.accept()


class BabyRevealDialog(QDialog):
    """Shown to the human only if they are the culprit."""
    def __init__(self, is_culprit: bool, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Baby of the Family"); self.setModal(True); self.setFixedSize(360, 180)
        self.setStyleSheet(_STYLE)
        lay = QVBoxLayout(self)
        if is_culprit:
            lay.addWidget(QLabel("👀  You are the CULPRIT.\nDon't reveal yourself — close your eyes now."))
        else:
            lay.addWidget(QLabel("😴  Close your eyes... the culprit secretly signals.\nNow everyone opens their eyes."))
        ok = QPushButton("OK"); ok.clicked.connect(self.accept); lay.addWidget(ok)
