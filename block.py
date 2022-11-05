from PySide6.QtCore import QObject, Property
from PySide6.QtGui import QPixmap


class Block(QObject):
    def __init__(self, row, col, name, scene):
        QObject.__init__(self)
        self.row = row
        self.col = col
        self.name = name

        self.exits = {}

        self.pixmap = scene.addPixmap(
            QPixmap("./images/blocks/" + name + ".png"))
        self.pixmap.setOffset(self.col*20, self.row*20)

    def add_exit(self, name, row, col):
        self.exits[name] = (row, col)

    def _opacity(self):
        return self.pixmap.opacity()

    def _setOpacity(self, opacity):
        self.pixmap.setOpacity(opacity)

    opacity = Property(float, _opacity, _setOpacity)
