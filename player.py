from PySide6.QtCore import QObject, Property, QPointF, QSizeF, QRect, Qt, QPropertyAnimation, QSequentialAnimationGroup
from PySide6.QtGui import QColor

from directions import Direction


class Player(QObject):

    def __init__(self, row, col, tile_size, player_color, path_color, scene, parent=None):
        QObject.__init__(self, parent)

        self.coordinates = QPointF(col, row)
        self.coordinates_init = QPointF(col, row)

        scene.addEllipse(
            QRect((tile_size * self.coordinates).toPoint(), QSizeF(tile_size, tile_size).toSize()), Qt.NoPen, QColor(path_color))
        self.drawing = scene.addEllipse(
            QRect(QPointF(0, 0).toPoint(), (tile_size * QSizeF(0.25, 0.25)).toSize()), Qt.NoPen, QColor(player_color))
        self.drawing.setZValue(5)

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
                    teleport_direction = QPointF(0, -0.25)
                elif teleport == Direction.EAST:
                    teleport_direction = QPointF(0.25, 0)
                elif teleport == Direction.SOUTH:
                    teleport_direction = QPointF(0, 0.25)
                elif teleport == Direction.WEST:
                    teleport_direction = QPointF(-0.25, 0)

                self.m_animation.setDuration(200)
                self.m_animation.setKeyValueAt(
                    0.25, self.pos + self.tile_size * teleport_direction)
                self.m_animation.setKeyValueAt(
                    0.75, self.pos + self.tile_size * teleport_direction)
                self.m_animation.setKeyValueAt(
                    0.750001, self.tile_size * (self.coordinates + QPointF(0.375, 0.375) - teleport_direction))

            self.m_animation.setEndValue(
                self.tile_size * (self.coordinates + QPointF(0.375, 0.375)))
            self.m_animation.start()

        else:
            self._setPos(self.tile_size *
                         (self.coordinates + QPointF(0.375, 0.375)))

    def reset(self):
        self.coordinates = QPointF(self.coordinates_init)
        self.move(animate=False)
