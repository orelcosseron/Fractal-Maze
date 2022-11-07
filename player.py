from PySide6.QtCore import Qt, QObject, Property, QPointF, QPropertyAnimation, QSequentialAnimationGroup, QRect
from PySide6.QtGui import QPixmap, QColor


class Player(QObject):

    def __init__(self, row, col, color, scene, parent=None):
        QObject.__init__(self, parent)
        self.m_pixmap = scene.addEllipse(
            QRect(0, 0, 6, 6), Qt.NoPen, QColor(color))
        self.m_pixmap.setZValue(9999)

        self.row = row
        self.col = col
        self.row_init = row
        self.col_init = col

        self.move(animate=False)

    def _pos(self):
        return self.m_pixmap.pos()

    def _setPos(self, value):
        self.m_pixmap.setPos(value)

    pos = Property(QPointF, _pos, _setPos)

    def move(self, animate=True, teleport=None):
        if animate:
            if teleport is not None:
                if teleport == 0:
                    teleport_direction = QPointF(0, -5)
                elif teleport == 1:
                    teleport_direction = QPointF(5, 0)
                elif teleport == 2:
                    teleport_direction = QPointF(0, 5)
                elif teleport == 3:
                    teleport_direction = QPointF(-5, 0)

                self.m_animation_1 = QPropertyAnimation(
                    self,
                    b"pos",
                    parent=self,
                    duration=50,
                )
                self.m_animation_1.setStartValue(self.pos)
                self.m_animation_1.setEndValue(
                    self.pos+teleport_direction)

                self.m_animation_2 = QPropertyAnimation(
                    self,
                    b"pos",
                    parent=self,
                    duration=50,
                )
                self.m_animation_2.setStartValue(
                    QPointF(self.col*20+7, self.row*20+7)-teleport_direction)
                self.m_animation_2.setEndValue(
                    QPointF(self.col*20+7, self.row*20+7))

                self.m_animation = QSequentialAnimationGroup()
                self.m_animation.addAnimation(self.m_animation_1)
                self.m_animation.addAnimation(self.m_animation_2)
                self.m_animation.start()
            else:
                self.m_animation_1 = QPropertyAnimation(
                    self,
                    b"pos",
                    parent=self,
                    duration=100,
                )
                self.m_animation_1.setStartValue(self.pos)
                self.m_animation_1.setEndValue(
                    QPointF(self.col*20+7, self.row*20+7))
                self.m_animation_1.start()

        else:
            self._setPos(QPointF(self.col*20+7, self.row*20+7))

    def reset(self):
        self.row = self.row_init
        self.col = self.col_init
        self.move(animate=False)
