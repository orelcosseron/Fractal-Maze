import os
import sys

from PySide6.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout
from PySide6.QtGui import QFontDatabase, QFont

from hud import Hud
from maze import Maze


class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setStyleSheet("background-color: #c0c0c0")

        QFontDatabase.addApplicationFont(
            dname + "/fonts/Digital7Mono-Yz9J4.ttf")
        font = QFont("Digital-7 Mono")
        font.setStyleHint(QFont.Monospace)
        QApplication.setFont(font)

        self.hud = Hud()

        self.maze = Maze()

        self.reset = QPushButton("Reset")
        self.reset.setStyleSheet(
            ":enabled{background-color: black; color: white; margin-left:50%; margin-right: 50%} :disabled{background-color:#c0c0c0; color:#c0c0c0; border:0px}")
        self.reset.clicked.connect(self.maze.reset)
        self.reset.clicked.connect(self.hud.reset)

        self.maze.change_block.connect(self.hud.update)
        self.maze.game_over.connect(self.hud.game_over)
        self.maze.game_over.connect(self.reset.setEnabled)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.hud)
        self.layout.addWidget(self.maze)
        self.layout.addWidget(self.reset)


if __name__ == "__main__":
    cwd = os.getcwd()
    dname = os.path.dirname(__file__)
    os.chdir(dname)

    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    main_window.setFixedSize(main_window.size())

    sys.exit(app.exec())
    os.chdir(cwd)
