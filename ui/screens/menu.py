from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QHBoxLayout, QLineEdit, QSpinBox, QFrame, QMessageBox
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

        # Player 1 name
        p1_label = QLabel("Player 1 Name")
        p1_label.setStyleSheet("color: #c084f5; font-weight: bold; font-size: 12px;")
        panel_layout.addWidget(p1_label)

        self.p1_input = QLineEdit()
        self.p1_input.setPlaceholderText("Enter your name…")
        self.p1_input.setStyleSheet(self._input_style())
        panel_layout.addWidget(self.p1_input)

        # Player 2 name (optional second human player)
        p2_label = QLabel("Player 2 Name  (leave blank for AI)")
        p2_label.setStyleSheet("color: #c084f5; font-weight: bold; font-size: 12px;")
        panel_layout.addWidget(p2_label)

        self.p2_input = QLineEdit()
        self.p2_input.setPlaceholderText("Optional second player…")
        self.p2_input.setStyleSheet(self._input_style())
        panel_layout.addWidget(self.p2_input)

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
        p2_name = self.p2_input.text().strip()
        ai_count = self.ai_spinner.value()

        player_names = [p1_name]
        if p2_name:
            player_names.append(p2_name)
            # Ensure at least 1 AI when 2 humans
            if ai_count < 1:
                ai_count = 1

        total = len(player_names) + ai_count
        if total < 3:
            QMessageBox.warning(self, "Not Enough Players",
                                "You need at least 3 players total (humans + AI).")
            return

        self.main_window.show_board(player_names, ai_count)

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
