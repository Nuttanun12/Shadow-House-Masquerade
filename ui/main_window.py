import sys
import os
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from .screens.menu import MenuScreen
from .screens.board import BoardScreen
from .screens.stats import StatsScreen


# Global dark stylesheet applied to the entire application
APP_STYLESHEET = """
    QWidget {
        font-family: 'Arial', sans-serif;
        font-size: 13px;
    }
    QMainWindow {
        background-color: #05000f;
    }
    QScrollBar:vertical {
        background: rgba(0,0,0,0.3);
        width: 8px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background: rgba(120, 0, 200, 0.7);
        border-radius: 4px;
    }
    QScrollBar:horizontal {
        background: rgba(0,0,0,0.3);
        height: 8px;
        border-radius: 4px;
    }
    QScrollBar::handle:horizontal {
        background: rgba(120, 0, 200, 0.7);
        border-radius: 4px;
    }
    QMessageBox {
        background-color: #0d0020;
        color: white;
    }
    QMessageBox QLabel {
        color: white;
        font-size: 14px;
    }
    QMessageBox QPushButton {
        background: #7b00bb;
        color: white;
        border-radius: 6px;
        padding: 8px 20px;
        font-weight: bold;
    }
    QMessageBox QPushButton:hover {
        background: #9b20db;
    }
"""


class MainWindow(QMainWindow):
    """
    Application main window. Manages the screen stack and provides
    navigation methods used by all child screens.
    """

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager

        self.setWindowTitle("Shadow House: Masquerade")
        self.setFixedSize(1100, 750)
        self.setStyleSheet(APP_STYLESHEET)

        # Verify required resources exist
        self._check_resources()

        # Stacked widget holds all screens
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Initialise all screens
        self.menu_screen = MenuScreen(self)
        self.board_screen = BoardScreen(self)
        self.stats_screen = StatsScreen(self)

        self.central_widget.addWidget(self.menu_screen)
        self.central_widget.addWidget(self.board_screen)
        self.central_widget.addWidget(self.stats_screen)

        self.show_menu()

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def show_menu(self):
        self.central_widget.setCurrentWidget(self.menu_screen)

    def show_board(self, player_names: list[str], ai_count: int):
        self.board_screen.start_game(player_names, ai_count)
        self.central_widget.setCurrentWidget(self.board_screen)

    def show_stats(self):
        self.stats_screen.refresh_data()
        self.central_widget.setCurrentWidget(self.stats_screen)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _check_resources(self):
        required = [
            "resources/images/menu_bg.png",
            "resources/images/board_bg.png",
            "resources/images/card_back.png",
        ]
        missing = [r for r in required if not os.path.exists(r)]
        if missing:
            # Non-fatal: game will still run without images
            print(f"WARNING: Missing resources: {', '.join(missing)}")
