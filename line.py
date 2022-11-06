from PySide6.QtCore import QObject, Property, QPropertyAnimation, QSequentialAnimationGroup, QPointF
from PySide6.QtGui import QColor


class Line(QObject):
    def __init__(self, row, col, direction, scene):
        QObject.__init__(self)
        if direction == 8:
            self.orientation = 0
            self.line = scene.addLine(
                col * 20 + 10, row * 20, col * 20 + 10, row * 20 + 10, QColor("red"))
        elif direction == 4:
            self.orientation = 1
            self.line = scene.addLine(
                col * 20 + 10, row * 20 + 10, col * 20 + 20, row * 20 + 10, QColor("red"))
        elif direction == 2:
            self.orientation = 2
            self.line = scene.addLine(
                col * 20 + 10, row * 20 + 10, col * 20 + 10, row * 20 + 20, QColor("red"))
        elif direction == 1:
            self.orientation = 3
            self.line = scene.addLine(
                col * 20, row * 20 + 10, col * 20 + 10, row * 20 + 10, QColor("red"))
        self.m_length = 0
        self.x1 = self.line.line().x1()
        self.x2 = self.line.line().x2()
        self.y1 = self.line.line().y1()
        self.y2 = self.line.line().y2()
        self.full_length = 10
        self.line.setOpacity(0)

    def setZValue(self, z):
        self.line.setZValue(z)

    def setExit(self, exit):
        self.exit = exit
        if self.exit:
            if self.orientation == 0:
                self.y1 -= 5
            if self.orientation == 1:
                self.x2 += 5
            if self.orientation == 2:
                self.y2 += 5
            if self.orientation == 3:
                self.x1 -= 5
            self.full_length += 5

    def hide(self, outward=True, now=False):
        if now:
            self.line.setOpacity(0)
            return
        self.inward = not outward
        self.m_animation = QPropertyAnimation(
            self,
            b"length",
            parent=self,
            duration=50,
        )
        self.m_animation.setStartValue(self.full_length)
        self.m_animation.setEndValue(0)

        self.animation = QSequentialAnimationGroup()

        if outward:
            self.animation.addPause(50)
        self.animation.addAnimation(self.m_animation)
        self.opacity_animation = QPropertyAnimation(
            self, b"opacity", parent=self, duration=0)
        self.opacity_animation.setStartValue(1)
        self.opacity_animation.setEndValue(0)
        self.animation.addAnimation(self.opacity_animation)
        self.animation.start()

    def show(self, inward=True, now=False):
        if now:
            self.line.setOpacity(1)
            return
        self.inward = inward
        self.line.show()
        self.line.setOpacity(1)
        self.m_animation = QPropertyAnimation(
            self,
            b"length",
            parent=self,
            duration=50,
        )
        self.m_animation.setStartValue(0)
        self.m_animation.setEndValue(self.full_length)

        self.animation = QSequentialAnimationGroup()

        if inward:
            self.opacity_animation = QPropertyAnimation(
                self, b"opacity", parent=self, duration=50)
            self.opacity_animation.setStartValue(0)
            self.opacity_animation.setEndValue(1)
            self.opacity_animation.setKeyValueAt(0.999, 0)
            self.animation.addAnimation(self.opacity_animation)
        self.animation.addAnimation(self.m_animation)
        self.animation.start()

    def _length(self):
        return self.line.line().length()

    def _setLength(self, length):
        if self.inward:
            if self.orientation == 0:
                self.line.setLine(self.x1, self.y1, self.x2, self.y1 + length)
            if self.orientation == 1:
                self.line.setLine(self.x2 - length, self.y1, self.x2, self.y2)
            if self.orientation == 2:
                self.line.setLine(self.x1, self.y2 - length, self.x2, self.y2)
            if self.orientation == 3:
                self.line.setLine(self.x1, self.y1, self.x1 + length, self.y2)
        else:
            if self.orientation == 0:
                self.line.setLine(self.x1, self.y2 - length, self.x2, self.y2)
            if self.orientation == 1:
                self.line.setLine(self.x1, self.y1, self.x1 + length, self.y2)
            if self.orientation == 2:
                self.line.setLine(self.x1, self.y1, self.x2, self.y1 + length)
            if self.orientation == 3:
                self.line.setLine(self.x2 - length, self.y1, self.x2, self.y2)

    length = Property(float, _length, _setLength)

    def _opacity(self):
        return self.line.opacity()

    def _setOpacity(self, opacity):
        self.line.setOpacity(opacity)

    opacity = Property(float, _opacity, _setOpacity)
