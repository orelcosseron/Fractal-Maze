from PySide6.QtCore import QObject, Property, QPointF, QRect, Qt, QPropertyAnimation, QSequentialAnimationGroup
from PySide6.QtGui import QColor

from directions import Direction


class Player(QObject):

    def __init__(self, row, col, tile_size, color, scene, parent=None):
        QObject.__init__(self, parent)
        self.drawing = scene.addEllipse(
            QRect(0, 0, tile_size*0.25, tile_size*0.25), Qt.NoPen, QColor(color))
        self.drawing.setZValue(5)

        self.row = row
        self.col = col
        self.row_init = row
        self.col_init = col

        self.tile_size = tile_size

        self.move(animate=False)

    def show(self):
        self.drawing.show()

    def hide(self):
        self.drawing.hide()

    def _pos(self):
        return self.drawing.pos()

    def _setPos(self, value):
        self.drawing.setPos(value)

    pos = Property(QPointF, _pos, _setPos)

    def move(self, animate=True, teleport=None):
        if animate:
            self.m_animation = QPropertyAnimation(
                self,
                b"pos",
                parent=self,
                duration=100,
            )
            self.m_animation.setStartValue(self.pos)

            if teleport is not None:
                if teleport == Direction.NORTH:
                    teleport_direction = QPointF(0, -self.tile_size * 0.25)
                elif teleport == Direction.EAST:
                    teleport_direction = QPointF(self.tile_size * 0.25, 0)
                elif teleport == Direction.SOUTH:
                    teleport_direction = QPointF(0, self.tile_size * 0.25)
                elif teleport == Direction.WEST:
                    teleport_direction = QPointF(-self.tile_size * 0.25, 0)

                self.m_animation.setDuration(200)
                self.m_animation.setKeyValueAt(
                    0.25, self.pos+teleport_direction)
                self.m_animation.setKeyValueAt(
                    0.75, self.pos+teleport_direction)
                self.m_animation.setKeyValueAt(0.750001, QPointF(
                    self.tile_size * (self.col + 0.375), self.tile_size * (self.row + 0.375)) - teleport_direction)

            self.m_animation.setEndValue(
                QPointF(self.tile_size * (self.col + 0.375),
                        self.tile_size * (self.row + 0.375)))
            self.m_animation.start()

        else:
            self._setPos(QPointF(self.tile_size * (self.col + 0.375),
                         self.tile_size * (self.row + 0.375)))

    def reset(self):
        self.row = self.row_init
        self.col = self.col_init
        self.move(animate=False)
