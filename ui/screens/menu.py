from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QHBoxLayout, QLineEdit, QSpinBox, QFrame, QMessageBox,
    QDialog, QScrollArea
)
from PyQt6.QtGui import QPixmap, QFont, QPalette, QBrush, QPainter, QColor, QLinearGradient
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve


class MenuScreen(QWidget):
    """
    Main menu screen — allows entering player names, setting AI count,
    and navigating to the game or statistics.
    """

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(0)

        # ── Title ────────────────────────────────────────────────────
        title_shadow = QLabel("SHADOW HOUSE")
        title_shadow.setFont(QFont("Georgia", 46, QFont.Weight.Bold))
        title_shadow.setStyleSheet("color: #ffd700; letter-spacing: 4px;")
        title_shadow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_shadow)

        subtitle = QLabel("M  A  S  Q  U  E  R  A  D  E")
        subtitle.setFont(QFont("Georgia", 18))
        subtitle.setStyleSheet("color: #c084f5; letter-spacing: 8px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(6)

        tagline = QLabel("A Social Deduction Card Game")
        tagline.setFont(QFont("Arial", 11))
        tagline.setStyleSheet("color: rgba(255,255,255,0.45); font-style: italic;")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tagline)

        layout.addSpacing(40)

        # ── Input panel ──────────────────────────────────────────────
        panel = QFrame()
        panel.setFixedWidth(380)
        panel.setStyleSheet("""
            QFrame {
                background: rgba(10, 0, 25, 0.72);
                border: 1px solid rgba(120, 0, 200, 0.6);
                border-radius: 16px;
            }
        """)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(28, 24, 28, 24)
        panel_layout.setSpacing(12)

        self.p1_input = QLineEdit()
        self.p1_input.setPlaceholderText("Enter your name…")
        self.p1_input.setStyleSheet(self._input_style())
        panel_layout.addWidget(self.p1_input)

        # AI count
        ai_row = QHBoxLayout()
        ai_label = QLabel("AI Opponents:")
        ai_label.setStyleSheet("color: #c084f5; font-weight: bold; font-size: 12px;")
        ai_row.addWidget(ai_label)
        ai_row.addStretch()

        self.ai_spinner = QSpinBox()
        self.ai_spinner.setRange(1, 7)
        self.ai_spinner.setValue(3)
        self.ai_spinner.setFixedWidth(70)
        self.ai_spinner.setStyleSheet("""
            QSpinBox {
                background: rgba(255,255,255,0.08);
                color: white;
                border: 1px solid rgba(160,80,255,0.5);
                border-radius: 6px;
                padding: 6px;
                font-size: 13px;
            }
            QSpinBox::up-button, QSpinBox::down-button { width: 18px; }
        """)
        ai_row.addWidget(self.ai_spinner)
        panel_layout.addLayout(ai_row)

        layout.addWidget(panel, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(28)

        # ── Buttons ───────────────────────────────────────────────────
        start_btn = QPushButton("▶   START GAME")
        start_btn.setFixedWidth(280)
        start_btn.setStyleSheet(self._btn_style("#7b00bb", "#9b20db"))
        start_btn.clicked.connect(self._on_start)
        layout.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(10)

        rules_btn = QPushButton("📖   HOW TO PLAY")
        rules_btn.setFixedWidth(280)
        rules_btn.setStyleSheet(self._btn_style("#3a0060", "#5a0090"))
        rules_btn.clicked.connect(self._show_rules)
        layout.addWidget(rules_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(10)

        stats_btn = QPushButton("📊   STATISTICS")
        stats_btn.setFixedWidth(280)
        stats_btn.setStyleSheet(self._btn_style("#163048", "#1e4a70"))
        stats_btn.clicked.connect(self.main_window.show_stats)
        layout.addWidget(stats_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(10)

        quit_btn = QPushButton("✖   QUIT")
        quit_btn.setFixedWidth(280)
        quit_btn.setStyleSheet(self._btn_style("#2a0a0a", "#500000"))
        quit_btn.clicked.connect(self.main_window.close)
        layout.addWidget(quit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(20)

        fs_toggle = QPushButton("📺   TOGGLE FULLSCREEN (F11)")
        fs_toggle.setFixedWidth(280)
        fs_toggle.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: rgba(255,255,255,0.4);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 6px;
                font-size: 10px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.05);
                color: white;
            }
        """)
        fs_toggle.clicked.connect(self.main_window.toggle_fullscreen)
        layout.addWidget(fs_toggle, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _input_style(self):
        return """
            QLineEdit {
                background: rgba(255,255,255,0.07);
                color: white;
                border: 1px solid rgba(160,80,255,0.5);
                border-radius: 8px;
                padding: 9px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #c084f5;
            }
        """

    def _btn_style(self, bg, hover_bg):
        return f"""
            QPushButton {{
                background: {bg};
                color: white;
                border-radius: 10px;
                padding: 14px 0;
                font-size: 15px;
                font-weight: bold;
                border: 1px solid rgba(255,255,255,0.15);
            }}
            QPushButton:hover {{
                background: {hover_bg};
            }}
            QPushButton:pressed {{
                background: #000;
            }}
        """

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def _on_start(self):
        p1_name = self.p1_input.text().strip() or "Player 1"
        ai_count = self.ai_spinner.value()

        player_names = [p1_name]
        total = len(player_names) + ai_count
        if total < 3:
            QMessageBox.warning(self, "Not Enough Players",
                                "You need at least 3 players total (human + AI).")
            return

        self.main_window.show_board(player_names, ai_count)

    def _show_rules(self):
        dlg = RulesDialog(self)
        dlg.exec()

    # ------------------------------------------------------------------
    # Background
    # ------------------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        bg = QPixmap("resources/images/menu_bg.png")
        if not bg.isNull():
            bg = bg.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                           Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(0, 0, bg)
        # Dark gradient overlay
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor(0, 0, 0, 140))
        grad.setColorAt(1, QColor(10, 0, 30, 200))
        painter.fillRect(self.rect(), grad)


class RulesDialog(QDialog):
    """Scrollable dialog showing game rules and card effects."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Shadow House: Masquerade — Rules")
        self.setFixedSize(500, 600)
        self.setStyleSheet("""
            QDialog { background: #0a001a; color: white; }
            QLabel { color: #ddd; font-size: 13px; }
            #title { color: #ffd700; font-size: 20px; font-weight: bold; padding-bottom: 10px; }
            #header { color: #c084f5; font-size: 16px; font-weight: bold; margin-top: 15px; }
            #card_row { background: rgba(255,255,255,0.05); padding: 8px; border-radius: 6px; margin: 4px 0; }
        """)

        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        content = QWidget()
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(20, 20, 20, 20)

        # ── General Rules ──────────────────────────────────────────
        t1 = QLabel("Welcome to the Masquerade")
        t1.setObjectName("title")
        content_lay.addWidget(t1)

        intro = QLabel(
            "In Shadow House: Masquerade, you are trying to find the Culprit hidden among you—or "
            "successfully hide if you ARE the Culprit!\n\n"
            "Each round, one player starts with the 'First on Scene' card and takes the first turn. "
            "Play continues clockwise. The round ends when the Culprit is caught or escapes."
        )
        intro.setWordWrap(True)
        content_lay.addWidget(intro)

        h1 = QLabel("Victory Conditions")
        h1.setObjectName("header")
        content_lay.addWidget(h1)

        v1 = QLabel(
            "• ⚖️ **The Detective Wins** if they find the Culprit (using Detective or Toby cards).\n"
            "• 💀 **The Culprit Wins** if they play the Culprit card as their VERY LAST card.\n"
            "• 🤝 **The Accomplice Wins** if the Culprit wins."
        )
        v1.setWordWrap(True)
        content_lay.addWidget(v1)

        h2 = QLabel("Roles & Card Effects")
        h2.setObjectName("header")
        content_lay.addWidget(h2)

        # Pull from metadata
        from game.models import ROLE_METADATA
        for role, meta in ROLE_METADATA.items():
            name, desc, _, _, emoji = meta
            row = QFrame()
            row.setObjectName("card_row")
            row_lay = QHBoxLayout(row)
            
            e_lbl = QLabel(emoji)
            e_lbl.setFixedWidth(30)
            e_lbl.setStyleSheet("font-size: 18px;")
            
            txt_lay = QVBoxLayout()
            n_lbl = QLabel(name.upper())
            n_lbl.setStyleSheet("font-weight: bold; color: #ffd700; font-size: 12px;")
            d_lbl = QLabel(desc)
            d_lbl.setWordWrap(True)
            d_lbl.setStyleSheet("color: #bbb; font-size: 11px;")
            
            txt_lay.addWidget(n_lbl)
            txt_lay.addWidget(d_lbl)
            
            row_lay.addWidget(e_lbl)
            row_lay.addLayout(txt_lay)
            content_lay.addWidget(row)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        close_btn = QPushButton("Got it!")
        close_btn.setStyleSheet("""
            QPushButton { 
                background: #c084f5; color: black; font-weight: bold; 
                padding: 10px; border-radius: 6px; margin-top: 10px;
            }
            QPushButton:hover { background: #d4b4ff; }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

