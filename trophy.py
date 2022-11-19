from PySide6.QtCore import QObject, QRect, Qt
from PySide6.QtGui import QColor


class Trophy(QObject):

    def __init__(self, row, col, trophy_color, path_color, tile_size, scene):
        QObject.__init__(self)

        scene.addEllipse(
            QRect(tile_size * col, tile_size * row, tile_size, tile_size), Qt.NoPen, QColor(path_color))

        self.drawing = scene.addEllipse(
            QRect(tile_size * (col + 0.3), tile_size * (row + 0.3), tile_size * 0.4, tile_size * 0.4), Qt.NoPen, QColor(trophy_color))
        self.drawing.setZValue(5)

    def show(self):
        self.drawing.show()

    def hide(self):
        self.drawing.hide()
