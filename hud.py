from PySide6.QtCore import Slot
from PySide6.QtWidgets import (QLabel, QHBoxLayout, QWidget)


class Hud(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.path = QLabel("Position: 0")

        self.layout = QHBoxLayout(self)

        self.layout.addWidget(self.path)

    @Slot()
    def reset(self):
        self.path.setText("Position: 0")

    @Slot()
    def update(self, stack):
        stack[0] = "Position: 0"
        self.path.setText(" <- ".join(stack))

    @Slot()
    def game_over(self, b):
        self.path.setText("Congratulations, you escaped!")
