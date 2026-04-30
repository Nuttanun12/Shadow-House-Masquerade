from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QLineEdit, QSpinBox
from PyQt6.QtGui import QPixmap, QFont, QPalette, QBrush
from PyQt6.QtCore import Qt

class MenuScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        title = QLabel("SHADOW HOUSE\nMASQUERADE")
        title.setFont(QFont("Playfair Display", 48, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffd700; text-align: center;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(50)

        # Game Options
        options_layout = QVBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Your Name")
        self.name_input.setFixedWidth(300)
        self.name_input.setStyleSheet("padding: 10px; border-radius: 5px; background: rgba(255,255,255,0.1); color: white;")
        options_layout.addWidget(self.name_input, alignment=Qt.AlignmentFlag.AlignCenter)

        ai_layout = QHBoxLayout()
        ai_label = QLabel("AI Players:")
        ai_label.setStyleSheet("color: white;")
        self.ai_spinner = QSpinBox()
        self.ai_spinner.setRange(2, 7)
        self.ai_spinner.setValue(3)
        self.ai_spinner.setStyleSheet("padding: 5px;")
        ai_layout.addWidget(ai_label)
        ai_layout.addWidget(self.ai_spinner)
        ai_container = QWidget()
        ai_container.setLayout(ai_layout)
        ai_container.setFixedWidth(300)
        options_layout.addWidget(ai_container, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(options_layout)
        layout.addSpacing(30)

        # Buttons
        btn_style = """
            QPushButton {
                background-color: #e94560;
                color: white;
                border-radius: 10px;
                padding: 15px 40px;
                font-size: 18px;
                font-weight: bold;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #ff5e78;
            }
        """

        start_btn = QPushButton("START GAME")
        start_btn.setStyleSheet(btn_style)
        start_btn.clicked.connect(self.on_start)
        layout.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        stats_btn = QPushButton("STATISTICS")
        stats_btn.setStyleSheet(btn_style.replace("#e94560", "#16213e"))
        stats_btn.clicked.connect(self.main_window.show_stats)
        layout.addWidget(stats_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        quit_btn = QPushButton("QUIT")
        quit_btn.setStyleSheet(btn_style.replace("#e94560", "#444"))
        quit_btn.clicked.connect(self.main_window.close)
        layout.addWidget(quit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def on_start(self):
        name = self.name_input.text() or "Player 1"
        ai_count = self.ai_spinner.value()
        self.main_window.show_board([name], ai_count)

    def paintEvent(self, event):
        # Set background image
        painter = QBrush(QPixmap("resources/images/menu_bg.png").scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding))
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, painter)
        self.setPalette(palette)
