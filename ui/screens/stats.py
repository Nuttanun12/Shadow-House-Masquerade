import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QTabWidget, QFrame
)
from PyQt6.QtGui import QPixmap, QPalette, QBrush, QPainter, QColor, QFont, QLinearGradient
from PyQt6.QtCore import Qt


class StatsScreen(QWidget):
    """
    Statistics screen with two tabs:
    - Leaderboard: all-time player stats (games, wins, score)
    - History: last 10 completed games with winner and final scores
    """

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._init_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(12)

        # Title
        title = QLabel("🏆  Statistics & Leaderboard")
        title.setFont(QFont("Georgia", 26, QFont.Weight.Bold))
        title.setStyleSheet("color: gold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: rgba(160,80,255,0.5);")
        layout.addWidget(line)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid rgba(120, 0, 200, 0.5);
                border-radius: 8px;
                background: rgba(0, 0, 0, 0.5);
            }
            QTabBar::tab {
                background: rgba(20, 0, 50, 0.8);
                color: #c084f5;
                padding: 10px 24px;
                border-radius: 6px 6px 0 0;
                font-size: 13px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: rgba(80, 0, 160, 0.9);
                color: white;
            }
            QTabBar::tab:hover {
                background: rgba(60, 0, 120, 0.8);
            }
        """)
        layout.addWidget(self.tabs)

        # ── Leaderboard Tab ──────────────────────────────────────────
        lb_widget = QWidget()
        lb_layout = QVBoxLayout(lb_widget)
        lb_layout.setContentsMargins(8, 8, 8, 8)

        self.leaderboard_table = self._make_table(
            ["🥇 Player", "Games Played", "Wins", "Total Score"]
        )
        lb_layout.addWidget(self.leaderboard_table)
        self.tabs.addTab(lb_widget, "🏅  Leaderboard")

        # ── History Tab ───────────────────────────────────────────────
        hist_widget = QWidget()
        hist_layout = QVBoxLayout(hist_widget)
        hist_layout.setContentsMargins(8, 8, 8, 8)

        self.history_table = self._make_table(
            ["#", "Date & Time", "Winner", "Final Scores"]
        )
        hist_layout.addWidget(self.history_table)
        self.tabs.addTab(hist_widget, "📜  Game History")

        # Back button
        back_btn = QPushButton("⬅   Back to Menu")
        back_btn.setFixedWidth(220)
        back_btn.setStyleSheet("""
            QPushButton {
                background: #7b00bb;
                color: white;
                border-radius: 10px;
                padding: 13px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background: #9b20db; }
        """)
        back_btn.clicked.connect(self.main_window.show_menu)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def _make_table(self, headers: list[str]) -> QTableWidget:
        tbl = QTableWidget()
        tbl.setColumnCount(len(headers))
        tbl.setHorizontalHeaderLabels(headers)
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tbl.verticalHeader().setVisible(False)
        tbl.setStyleSheet("""
            QTableWidget {
                background: transparent;
                color: #e0d0ff;
                gridline-color: rgba(100, 0, 180, 0.3);
                border: none;
                font-size: 13px;
            }
            QHeaderView::section {
                background: rgba(60, 0, 120, 0.9);
                color: gold;
                padding: 10px;
                border: 1px solid rgba(120, 0, 200, 0.4);
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background: rgba(120, 0, 200, 0.4);
            }
            QTableWidget::item:alternate {
                background: rgba(255, 255, 255, 0.03);
            }
        """)
        tbl.setAlternatingRowColors(True)
        return tbl

    # ------------------------------------------------------------------
    # Data refresh
    # ------------------------------------------------------------------

    def refresh_data(self):
        self._refresh_leaderboard()
        self._refresh_history()

    def _refresh_leaderboard(self):
        rows = self.main_window.db_manager.get_leaderboard()
        self.leaderboard_table.setRowCount(len(rows))
        for row_idx, (name, games, wins, total_score) in enumerate(rows):
            values = [name, str(games), str(wins), str(total_score)]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if row_idx == 0:
                    item.setForeground(QColor("gold"))
                self.leaderboard_table.setItem(row_idx, col, item)

    def _refresh_history(self):
        rows = self.main_window.db_manager.get_history()
        self.history_table.setRowCount(len(rows))
        for row_idx, (game_id, date_str, winner, scores_json) in enumerate(rows):
            # Parse scores JSON into readable string
            try:
                scores_dict = json.loads(scores_json)
                scores_text = "  |  ".join(f"{n}: {s}" for n, s in scores_dict.items())
            except Exception:
                scores_text = scores_json or ""

            date_display = str(date_str)[:16].replace("T", " ")

            values = [str(game_id), date_display, winner, scores_text]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col == 2:  # winner column — gold
                    item.setForeground(QColor("gold"))
                self.history_table.setItem(row_idx, col, item)

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
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0, QColor(0, 0, 0, 160))
        grad.setColorAt(1, QColor(10, 0, 30, 210))
        painter.fillRect(self.rect(), grad)
