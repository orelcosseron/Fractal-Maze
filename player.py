from PySide6.QtCore import QObject, Property, QPointF, QRect, Qt, QPropertyAnimation, QSequentialAnimationGroup
from PySide6.QtGui import QColor

from directions import Direction


class Player(QObject):

    def __init__(self, row, col, color, scene, parent=None):
        QObject.__init__(self, parent)
        self.drawing = scene.addEllipse(
            QRect(0, 0, 6, 6), Qt.NoPen, QColor(color))
        self.drawing.setZValue(5)

        self.row = row
        self.col = col
        self.row_init = row
        self.col_init = col

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
                    teleport_direction = QPointF(0, -5)
                elif teleport == Direction.EAST:
                    teleport_direction = QPointF(5, 0)
                elif teleport == Direction.SOUTH:
                    teleport_direction = QPointF(0, 5)
                elif teleport == Direction.WEST:
                    teleport_direction = QPointF(-5, 0)

                self.m_animation.setDuration(200)
                self.m_animation.setKeyValueAt(
                    0.25, self.pos+teleport_direction)
                self.m_animation.setKeyValueAt(
                    0.75, self.pos+teleport_direction)
                self.m_animation.setKeyValueAt(0.750001, QPointF(
                    self.col*20+7, self.row*20+7)-teleport_direction)

            self.m_animation.setEndValue(
                QPointF(self.col*20+7, self.row*20+7))
            self.m_animation.start()

        else:
            self._setPos(QPointF(self.col*20+7, self.row*20+7))

    def reset(self):
        self.row = self.row_init
        self.col = self.col_init
        self.move(animate=False)
