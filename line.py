from PySide6.QtCore import QObject, Property, QPropertyAnimation, QSequentialAnimationGroup, QPointF
from PySide6.QtGui import QColor


class Line(QObject):
    def __init__(self, row, col, direction, scene):
        QObject.__init__(self)
        self.direction = direction
        if direction == 8:
            self.line = scene.addLine(
                col * 20 + 10, row * 20, col * 20 + 10, row * 20 + 10, QColor("red"))
        elif direction == 4:
            self.line = scene.addLine(
                col * 20 + 10, row * 20 + 10, col * 20 + 20, row * 20 + 10, QColor("red"))
        elif direction == 2:
            self.line = scene.addLine(
                col * 20 + 10, row * 20 + 10, col * 20 + 10, row * 20 + 20, QColor("red"))
        elif direction == 1:
            self.line = scene.addLine(
                col * 20, row * 20 + 10, col * 20 + 10, row * 20 + 10, QColor("red"))
        self.m_length = 0

    def setZValue(self, z):
        self.line.setZValue(z)

    def hide(self, inward=True):
        self.line.hide()

    def show(self, inward=True):
        self.inward = inward
        self.line.show()
        self.m_animation = QPropertyAnimation(
            self,
            b"length",
            parent=self,
            duration=50,
        )
        self.m_animation.setStartValue(0)
        self.m_animation.setEndValue(10)

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
        line = self.line.line()
        if self.inward:
            if self.direction == 8:
                self.line.setLine(line.x1(), line.y1(),
                                  line.x2(), line.y1() + length)
            if self.direction == 4:
                self.line.setLine(line.x2() - length, line.y1(),
                                  line.x2(), line.y2())
            if self.direction == 2:
                self.line.setLine(line.x1(), line.y2() -
                                  length, line.x2(), line.y2())
            if self.direction == 1:
                self.line.setLine(line.x1(), line.y1(),
                                  line.x1()+length, line.y2())
        else:
            if self.direction == 8:
                self.line.setLine(line.x1(), line.y2() - length,
                                  line.x2(), line.y2())
            if self.direction == 4:
                self.line.setLine(line.x1(), line.y1(),
                                  line.x1() + length, line.y2())
            if self.direction == 2:
                self.line.setLine(line.x1(), line.y1(),
                                  line.x2(), line.y1()+length)
            if self.direction == 1:
                self.line.setLine(line.x2() - length, line.y1(),
                                  line.x2(), line.y2())

    length = Property(float, _length, _setLength)

    def _opacity(self):
        return self.line.opacity()

    def _setOpacity(self, opacity):
        self.line.setOpacity(opacity)

    opacity = Property(float, _opacity, _setOpacity)
