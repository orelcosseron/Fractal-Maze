import sys
from hud import Hud
from maze import Maze

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QWidget)


class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.hud = Hud()

        self.maze = Maze()

        self.reset = QPushButton("Reset")
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
        if event.key() in [Qt.Key_Z, Qt.Key_Q, Qt.Key_D, Qt.Key_S]:
            self.maze.update_player(event.key())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
