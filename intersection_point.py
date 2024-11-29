import uuid
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QPen


class IntersectionPoint(QGraphicsEllipseItem):
    def __init__(self, x, y, index, radius=4):
        super().__init__(x - radius, y - radius, radius * 2, radius * 2)
        self.setBrush(QBrush(Qt.red))
        self.setFlags(QGraphicsEllipseItem.ItemIsSelectable)
        self.setZValue(2)
        self.index = index

        # Create label for the index
        self.label = QGraphicsTextItem(str(index), self)
        self.label.setPos(x - radius, y - radius - 10)  # Position label above the point

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.setPen(QPen(Qt.blue, 2))
            painter.drawEllipse(self.rect())
