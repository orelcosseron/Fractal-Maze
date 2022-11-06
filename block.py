from PySide6.QtCore import Qt, QObject, Property, QRect
from PySide6.QtGui import QPixmap, QColor, QFont


class Block(QObject):
    def __init__(self, row, col, name, color, scene):
        QObject.__init__(self)
        self.row = row
        self.col = col
        self.name = name
        self.color = color

        self.exits = {}

        scene.addRect(QRect(self.col*20, self.row*20, 60, 60),
                      Qt.NoPen, QColor(color))
        text = scene.addSimpleText(name, QFont("Impact", 25))
        text.setPos(self.col*20+30-text.boundingRect().width()/2,
                    self.row*20+30-text.boundingRect().height()/2)
        text.setBrush(QColor(color).darker())

    def add_exit(self, name, row, col):
        self.exits[name] = (row, col)
