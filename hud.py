from PySide6.QtCore import Slot
from PySide6.QtWidgets import (QLabel, QHBoxLayout, QWidget)


class Hud(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.depth = QLabel("Depth: 0")
        self.block = QLabel("Position: 0")

        self.layout = QHBoxLayout(self)

        self.layout.addWidget(self.depth)
        self.layout.addWidget(self.block)

    @Slot()
    def reset(self):
        self.depth.setText("Depth: 0")
        self.block.setText("Position: 0")

    @Slot()
    def update(self, stack):
        self.depth.setText("Depth: " + str(len(stack)-1))
        str_stack = "Position: 0"
        for block in stack[1:]:
            str_stack += " <- " + block
        self.block.setText(str_stack)

    @Slot()
    def game_over(self, b):
        self.depth.setText("")
        self.block.setText("Congratulations, you escaped!")
