from PySide6.QtCore import QObject, QRect, Qt
from PySide6.QtGui import QColor, QPixmap, QPainter
from PySide6.QtWidgets import QApplication


class Block(QObject):
    def __init__(self, row, col, width, height, name, color, scene):
        QObject.__init__(self)

        self.name = name
        self.color = color
        self.exits = {}

        self.block = scene.addRect(QRect(0, 0, width*20, height*20),
                                   Qt.NoPen, QColor(color))
        self.block.setPos(col*20, row*20)

        self.recursion_pixmap = QPixmap(
            self.block.boundingRect().size().toSize())
        self.recursion_pixmap.fill(self.color)
        self.painter = QPainter(self.recursion_pixmap)

    def add_exit(self, name, row, col):
        self.exits[name] = (row, col)

    def render(self, scene):
        pos = self.block.pos()
        self.block = scene.addPixmap(self.recursion_pixmap)
        self.block.setPos(pos)
