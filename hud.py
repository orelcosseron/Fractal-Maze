from PySide6.QtCore import Slot
from PySide6.QtWidgets import (QLabel, QHBoxLayout, QWidget)


class Hud(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.depth = QLabel("Depth: 0")
        self.block = QLabel("Block: ")

        self.layout = QHBoxLayout(self)

        self.layout.addWidget(self.depth)
        self.layout.addWidget(self.block)

    @Slot()
    def reset(self):
        self.depth.setText(" ".join(self.depth.text().split(" ")[
            :-1]) + " 0")
        self.block.setText(" ".join(
            self.block.text().split(" ")[:-1]) + " ")

    @Slot()
    def update(self, new_block="", inward=True):
        new_depth = self.depth.text()
        new_depth = new_depth.split(" ")[-1]
        new_depth = int(new_depth)
        new_depth += 1 if inward else -1
        self.depth.setText(" ".join(self.depth.text().split(" ")[
            :-1]) + " " + str(new_depth))
        self.block.setText(" ".join(
            self.block.text().split(" ")[:-1]) + " " + new_block)

    @Slot()
    def game_over(self, b):
        self.depth.setText("")
        self.block.setText("Congratulations, you escaped!")
