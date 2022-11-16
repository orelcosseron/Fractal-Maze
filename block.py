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

        self.recursion_pixmap = {}
        self.painters = {}

    def add_exit(self, name, row, col):
        self.exits[name] = (row, col)

    def pre_render(self, position="Default"):
        if position not in self.recursion_pixmap:
            self.recursion_pixmap[position] = QPixmap(
                self.block.boundingRect().size().toSize())
            self.recursion_pixmap[position].fill(self.color)
            self.painters[position] = QPainter(self.recursion_pixmap[position])
        self.block.scene().render(self.painters[position])

    def render(self, position="Default"):
        position = position if position in self.recursion_pixmap else "Default"
        pos = self.block.pos()
        scene = self.block.scene()
        scene.removeItem(self.block)
        self.block = scene.addPixmap(self.recursion_pixmap[position])
        self.block.setPos(pos)

    def reset(self):
        for name in list(self.recursion_pixmap.keys()):
            if name != "Default":
                self.painters.pop(name)
                self.recursion_pixmap.pop(name)
        self.render(self.block.scene())
