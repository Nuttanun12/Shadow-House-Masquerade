import sys
import os
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QApplication
from PyQt6.QtCore import Qt
from .screens.menu import MenuScreen
from .screens.board import BoardScreen
from .screens.stats import StatsScreen

class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Shadow House: Masquerade")
        self.setFixedSize(1024, 768)
        
        self.check_resources()

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Initialize screens
        self.menu_screen = MenuScreen(self)
        self.board_screen = BoardScreen(self)
        self.stats_screen = StatsScreen(self)

        self.central_widget.addWidget(self.menu_screen)
        self.central_widget.addWidget(self.board_screen)
        self.central_widget.addWidget(self.stats_screen)

        self.show_menu()

    def show_menu(self):
        self.central_widget.setCurrentWidget(self.menu_screen)

    def show_board(self, player_names, ai_count):
        self.board_screen.start_game(player_names, ai_count)
        self.central_widget.setCurrentWidget(self.board_screen)

    def show_stats(self):
        self.stats_screen.refresh_data()
        self.central_widget.setCurrentWidget(self.stats_screen)

    def check_resources(self):
        required = ["resources/images/menu_bg.png", "resources/images/board_bg.png", "resources/images/card_back.png"]
        for res in required:
            if not os.path.exists(res):
                print(f"CRITICAL ERROR: Missing resource {res}")
                # In a real app, show a message box
