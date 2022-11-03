from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPixmap


class Player(QWidget):
    def __init__(self, x, y):
        QWidget.__init__(self)
        self.x = x
        self.y = y

        self.pixmap = QPixmap("./images/player.png")
