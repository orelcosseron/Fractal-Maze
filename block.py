from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPixmap


class Block(QWidget):
    def __init__(self, row, col, name):
        QWidget.__init__(self)
        self.row = row
        self.col = col
        self.name = name

        self.exits = {}

        self.pixmap = QPixmap("./images/blocks/" + name + ".png")

    def add_exit(self, name, x, y):
        self.exits[name] = (x, y)
