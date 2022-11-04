from PySide6.QtCore import QObject
from PySide6.QtGui import QPixmap


class Block(QObject):
    def __init__(self, x, y, name, scene):
        QObject.__init__(self)
        self.x = x
        self.y = y
        self.name = name

        self.exits = {}

        self.pixmap = scene.addPixmap(
            QPixmap("./images/blocks/" + name + ".png"))
        self.pixmap.setOffset(x*20, y*20)

    def add_exit(self, name, x, y):
        self.exits[name] = (x, y)
