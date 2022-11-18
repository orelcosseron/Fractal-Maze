from PySide6.QtCore import QObject, QRect, Qt
from PySide6.QtGui import QColor


class Trophy(QObject):

    def __init__(self, row, col, color, tile_size, scene):
        QObject.__init__(self)
        self.drawing = scene.addEllipse(
            QRect(tile_size * (col + 0.3), tile_size * (row + 0.3), tile_size * 0.4, tile_size * 0.4), Qt.NoPen, QColor(color))
        self.drawing.setZValue(5)

    def show(self):
        self.drawing.show()

    def hide(self):
        self.drawing.hide()
