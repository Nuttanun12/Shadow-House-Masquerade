from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
from PyQt6.QtGui import QPixmap, QPalette, QBrush
from PyQt6.QtCore import Qt

class StatsScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        
        title = QLabel("LEADERBOARD")
        title.setStyleSheet("color: gold; font-size: 36px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Player", "Games", "Wins", "Total Score"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(0, 0, 0, 0.7);
                color: white;
                gridline-color: #444;
                border: none;
            }
            QHeaderView::section {
                background-color: #1a1a2e;
                color: gold;
                padding: 10px;
                border: 1px solid #444;
            }
        """)
        layout.addWidget(self.table)
        
        back_btn = QPushButton("BACK TO MENU")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #e94560;
                color: white;
                border-radius: 10px;
                padding: 15px;
                font-weight: bold;
            }
        """)
        back_btn.clicked.connect(self.main_window.show_menu)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)

    def refresh_data(self):
        stats = self.main_window.db_manager.get_leaderboard()
        self.table.setRowCount(len(stats))
        for row, data in enumerate(stats):
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)

    def paintEvent(self, event):
        painter = QBrush(QPixmap("resources/images/menu_bg.png").scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding))
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, painter)
        self.setPalette(palette)
