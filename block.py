from PySide6.QtCore import QObject, QRect, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication


class Block(QObject):
    def __init__(self, row, col, width, height, name, color, scene):
        QObject.__init__(self)

        self.name = name
        self.color = color
        self.exits = {}

        scene.addRect(QRect(col*20, row*20, width*20, height*20),
                      Qt.NoPen, QColor(color))
        font = QApplication.font()
        font.setPixelSize(min(width*20, height*20))
        text = scene.addSimpleText(name, font)
        text.setPos(col*20+width*10-text.boundingRect().width()/2,
                    row*20+height*10-text.boundingRect().height()/2)
        text.setBrush(QColor(color).darker())

    def add_exit(self, name, row, col):
        self.exits[name] = (row, col)
