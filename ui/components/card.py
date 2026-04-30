from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QSize

class CardWidget(QWidget):
    def __init__(self, card, is_hidden=True, parent=None):
        super().__init__(parent)
        self.card = card
        self.is_hidden = is_hidden
        self.setFixedSize(120, 180)
        
        self.back_pixmap = QPixmap("resources/images/card_back.png").scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        if self.is_hidden:
            painter.drawPixmap(0, 0, self.back_pixmap)
        else:
            # Draw front (Simplified for now)
            painter.setBrush(QColor("#fdfdfd"))
            painter.drawRoundedRect(0, 0, self.width()-1, self.height()-1, 10, 10)
            
            painter.setPen(QColor("black"))
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(10, 30, self.card.name)
            
            painter.setFont(QFont("Arial", 8))
            painter.drawText(10, 50, self.width()-20, 100, Qt.TextFlag.TextWordWrap, self.card.description)
            
    def mousePressEvent(self, event):
        self.parent().card_clicked(self)
