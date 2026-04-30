from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtGui import QPainter, QColor, QFont, QLinearGradient, QBrush, QPen
from PyQt6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, pyqtProperty


class CardWidget(QWidget):
    """
    A styled, interactive card widget that renders the card face or back.
    Supports hover animations and click handling.
    """

    CARD_W = 120
    CARD_H = 180

    def __init__(self, card, is_hidden: bool = True, parent=None):
        super().__init__(parent)
        self.card = card
        self.is_hidden = is_hidden
        self.index = -1          # Card index in hand (set by board screen)
        self._hover = False
        self._lift = 0           # Lift offset for hover animation (pixels)

        self.setFixedSize(self.CARD_W, self.CARD_H)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setMouseTracking(True)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

    # ------------------------------------------------------------------
    # Qt property for animation
    # ------------------------------------------------------------------

    def get_lift(self):
        return self._lift

    def set_lift(self, val):
        self._lift = val
        self.update()

    lift = pyqtProperty(int, get_lift, set_lift)

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def enterEvent(self, event):
        self._hover = True
        anim = QPropertyAnimation(self, b"lift", self)
        anim.setDuration(120)
        anim.setEndValue(18)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        anim = QPropertyAnimation(self, b"lift", self)
        anim.setDuration(120)
        anim.setEndValue(0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Bubble up to the board screen
            p = self.parent()
            while p:
                if hasattr(p, "card_clicked"):
                    p.card_clicked(self)
                    break
                p = p.parent()

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Offset upward on hover
        painter.translate(0, -self._lift)

        if self.is_hidden:
            self._draw_back(painter)
        else:
            self._draw_front(painter)

    def _draw_back(self, painter: QPainter):
        """Render the mysterious card back."""
        w, h = self.CARD_W, self.CARD_H

        # Card background gradient (deep purple)
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0, QColor("#1a0028"))
        grad.setColorAt(1, QColor("#0d0016"))
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor("#6a0080"), 2))
        painter.drawRoundedRect(2, 2, w - 4, h - 4, 10, 10)

        # Border ornament
        painter.setPen(QPen(QColor("#b04aff"), 1))
        painter.drawRoundedRect(8, 8, w - 16, h - 16, 7, 7)

        # Decorative text
        painter.setPen(QColor("#d080ff"))
        painter.setFont(QFont("Serif", 9, QFont.Weight.Bold))
        painter.drawText(QRect(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, "⚜\n\nSHADOW\nHOUSE\n\n⚜")

    def _draw_front(self, painter: QPainter):
        """Render the card face with role name, color, and description."""
        w, h = self.CARD_W, self.CARD_H
        bg_color = QColor(self.card.color) if hasattr(self.card, "color") else QColor("#1a1a2e")
        text_color = QColor(self.card.text_color) if hasattr(self.card, "text_color") else QColor("#ffffff")

        # Card body gradient
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0, bg_color.lighter(140))
        grad.setColorAt(1, bg_color)
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(text_color.darker(150), 2))
        painter.drawRoundedRect(2, 2, w - 4, h - 4, 10, 10)

        # Inner border
        painter.setPen(QPen(text_color, 1))
        painter.drawRoundedRect(6, 6, w - 12, h - 12, 7, 7)

        # Role name banner
        banner_grad = QLinearGradient(0, 10, 0, 38)
        banner_grad.setColorAt(0, text_color.darker(180))
        banner_grad.setColorAt(1, text_color.darker(220))
        painter.setBrush(QBrush(banner_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(10, 10, w - 20, 28, 5, 5)

        painter.setPen(text_color)
        painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        painter.drawText(QRect(10, 10, w - 20, 28), Qt.AlignmentFlag.AlignCenter, self.card.name.upper())

        # Emoji center-piece
        emoji = getattr(self.card, "emoji", "❓")
        painter.setFont(QFont("Segoe UI Emoji", 36)) # Use emoji-capable font
        painter.drawText(QRect(0, 45, w, 70), Qt.AlignmentFlag.AlignCenter, emoji)

        # Description text
        painter.setFont(QFont("Arial", 7))
        painter.setPen(text_color.lighter(130))
        painter.drawText(QRect(10, 115, w - 20, h - 120), Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.card.description)

        # Hover highlight
        if self._hover:
            painter.setBrush(QColor(255, 255, 255, 18))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(2, 2, w - 4, h - 4, 10, 10)
