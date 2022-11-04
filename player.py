from PySide6.QtCore import QObject, Property, QPointF, QPropertyAnimation
from PySide6.QtGui import QPixmap


class Player(QObject):

    def __init__(self, x, y, scene, parent=None):
        QObject.__init__(self, parent)
        self.m_pixmap = scene.addPixmap(QPixmap("./images/player.png"))
        self.m_animation = QPropertyAnimation(
            self,
            b"pos",
            parent=self,
            duration=100,
        )
        self.x = x
        self.y = y
        self.x_init = x
        self.y_init = y

        self.move(animate=False)

    def offset(self):
        return self.m_pixmap.offset()

    def setOffset(self, value):
        self.m_pixmap.setOffset(value)

    pos = Property(QPointF, offset, setOffset)

    def move(self, animate=True):
        if animate:
            self.m_animation.setStartValue(self.offset())
            self.m_animation.setEndValue(QPointF(self.x*20, self.y*20))
            self.m_animation.start()
        else:
            self.setOffset(QPointF(self.x*20, self.y*20))

    def reset(self):
        self.x = self.x_init
        self.y = self.y_init
        self.move(animate=False)
