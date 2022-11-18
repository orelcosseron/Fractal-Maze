from PySide6.QtCore import QObject, Property, QPropertyAnimation, QSequentialAnimationGroup
from PySide6.QtGui import QColor

from directions import Direction


class Line(QObject):
    def __init__(self, coordinates, tile_size, line_color, orientation, scene):
        QObject.__init__(self)
        self.orientation = orientation
        row = coordinates.y()
        col = coordinates.x()
        if self.orientation == Direction.NORTH:
            self.line = scene.addLine(
                tile_size * (col + 0.5), tile_size * row, tile_size * (col + 0.5), tile_size * (row + 0.5), QColor(line_color))
        elif self.orientation == Direction.EAST:
            self.line = scene.addLine(
                tile_size * (col + 0.5), tile_size * (row + 0.5), tile_size * (col + 1), tile_size * (row + 0.5), QColor(line_color))
        elif self.orientation == Direction.SOUTH:
            self.line = scene.addLine(
                tile_size * (col + 0.5), tile_size * (row + 0.5), tile_size * (col + 0.5), tile_size * (row + 1), QColor(line_color))
        elif self.orientation == Direction.WEST:
            self.line = scene.addLine(
                tile_size * col, tile_size * (row + 0.5), tile_size * (col + 0.5), tile_size * (row + 0.5), QColor(line_color))
        self.m_length = 0
        self.x1 = self.line.line().x1()
        self.x2 = self.line.line().x2()
        self.y1 = self.line.line().y1()
        self.y2 = self.line.line().y2()
        self.full_length = tile_size * 0.5
        self.line.setOpacity(0)
        self.line.setZValue(3)
        self.exit = False

    def setExit(self):
        if not self.exit:
            self.exit = True
            if self.orientation == Direction.NORTH:
                self.y1 -= 0.5 * self.full_length
            if self.orientation == Direction.EAST:
                self.x2 += 0.5 * self.full_length
            if self.orientation == Direction.SOUTH:
                self.y2 += 0.5 * self.full_length
            if self.orientation == Direction.WEST:
                self.x1 -= 0.5 * self.full_length
            self.full_length *= 1.5

    def unsetExit(self):
        if self.exit:
            self.exit = False
            if self.orientation == Direction.NORTH:
                self.y1 += self.full_length / 3
            if self.orientation == Direction.EAST:
                self.x2 -= self.full_length / 3
            if self.orientation == Direction.SOUTH:
                self.y2 -= self.full_length / 3
            if self.orientation == Direction.WEST:
                self.x1 += self.full_length / 3
            self.full_length *= 2 / 3

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
        self.line.show()
        self.line.setOpacity(1)
        if now:
            self.length = self.full_length
            return
        self.inward = inward
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
            direction = self.orientation
        else:
            direction = self.orientation.opposite()

        if direction == Direction.NORTH:
            self.line.setLine(self.x1, self.y1, self.x2, self.y1 + length)
        if direction == Direction.EAST:
            self.line.setLine(self.x2 - length, self.y1, self.x2, self.y2)
        if direction == Direction.SOUTH:
            self.line.setLine(self.x1, self.y2 - length, self.x2, self.y2)
        if direction == Direction.WEST:
            self.line.setLine(self.x1, self.y1, self.x1 + length, self.y2)

    length = Property(float, _length, _setLength)

    def _opacity(self):
        return self.line.opacity()

    def _setOpacity(self, opacity):
        self.line.setOpacity(opacity)

    opacity = Property(float, _opacity, _setOpacity)
