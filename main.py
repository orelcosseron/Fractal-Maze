import sys
from hud import Hud
from maze import Maze, Key

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QWidget)
import os


class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setStyleSheet("background-color: #c0c0c0")

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Z:
            self.maze.update_player(Key.UP)
        elif event.key() == Qt.Key_Q:
            self.maze.update_player(Key.LEFT)
        elif event.key() == Qt.Key_S:
            self.maze.update_player(Key.DOWN)
        elif event.key() == Qt.Key_D:
            self.maze.update_player(Key.RIGHT)


if __name__ == "__main__":

    cwd = os.getcwd()
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()
    main_window.setFixedSize(main_window.size())

    sys.exit(app.exec())
    os.chdir(cwd)
