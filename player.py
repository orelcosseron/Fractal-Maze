from PySide6.QtCore import QObject, Property, QPointF, QPropertyAnimation, QSequentialAnimationGroup
from PySide6.QtGui import QPixmap


class Player(QObject):

    def __init__(self, row, col, scene, parent=None):
        QObject.__init__(self, parent)
        self.m_pixmap = scene.addPixmap(QPixmap("./images/player.png"))
        self.m_pixmap.setZValue(9999)

        self.row = col
        self.col = row
        self.row_init = row
        self.col_init = col

        self.move(animate=False)

    def offset(self):
        return self.m_pixmap.offset()

    def setOffset(self, value):
        self.m_pixmap.setOffset(value)

    pos = Property(QPointF, offset, setOffset)

    def move(self, animate=True, teleport=None):
        if animate:
            if teleport is not None:
                if teleport == 1:
                    teleport_direction = QPointF(5, 0)
                elif teleport == 2:
                    teleport_direction = QPointF(0, 5)
                elif teleport == 3:
                    teleport_direction = QPointF(-5, 0)
                elif teleport == 4:
                    teleport_direction = QPointF(0, -5)

                self.m_animation_1 = QPropertyAnimation(
                    self,
                    b"pos",
                    parent=self,
                    duration=50,
                )
                self.m_animation_1.setStartValue(self.offset())
                self.m_animation_1.setEndValue(
                    self.offset()+teleport_direction)

                self.m_animation_2 = QPropertyAnimation(
                    self,
                    b"pos",
                    parent=self,
                    duration=50,
                )
                self.m_animation_2.setStartValue(
                    QPointF(self.col*20, self.row*20)-teleport_direction)
                self.m_animation_2.setEndValue(
                    QPointF(self.col*20, self.row*20))

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
                self.m_animation_1.setStartValue(self.offset())
                self.m_animation_1.setEndValue(
                    QPointF(self.col*20, self.row*20))
                self.m_animation_1.start()

        else:
            self.setOffset(QPointF(self.col*20, self.row*20))

    def reset(self):
        self.row = self.row_init
        self.col = self.col_init
        self.move(animate=False)
