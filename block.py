from PySide6.QtCore import QObject, QRect, Qt, Property
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication


class Block(QObject):
    def __init__(self, row, col, width, height, name, color, scene):
        QObject.__init__(self)

        self.name = name
        self.color = color
        self.exits = {}

        self.block = scene.addRect(QRect(col*20, row*20, width*20, height*20),
                                   Qt.NoPen, QColor(color))
        font = QApplication.font()
        font.setPixelSize(min(width*20, height*20))
        text = scene.addSimpleText(name, font)
        text.setPos(col*20+width*10-text.boundingRect().width()/2,
                    row*20+height*10-text.boundingRect().height()/2)
        text.setBrush(QColor(color).darker())

        self.over_block = scene.addRect(QRect(col*20, row*20, width*20, height*20),
                                        Qt.NoPen, QColor(color))
        self.over_text = scene.addSimpleText(name, font)
        self.over_text.setPos(col*20+width*10-self.over_text.boundingRect().width()/2,
                              row*20+height*10-self.over_text.boundingRect().height()/2)
        self.over_text.setBrush(QColor(color).darker())
        self.over_block.setZValue(9999)
        self.over_text.setZValue(9999)
        self.over_block.setOpacity(0)
        self.over_text.setOpacity(0)

    def add_exit(self, name, row, col):
        self.exits[name] = (row, col)

    def _overBlockOpacity(self):
        if self.over_text.opacity() != self.over_block.opacity():
            self.over_text.setOpacity(self.over_block.opacity())
        return self.over_block.opacity()

    def _setOverBlockOpacity(self, opacity):
        self.over_block.setOpacity(opacity)
        self.over_text.setOpacity(opacity)

    overBlockOpacity = Property(float, _overBlockOpacity, _setOverBlockOpacity)

    def _overBlockRect(self):
        return self.over_block.rect().toRect()

    def _setOverBlockRect(self, rect):
        self.over_block.setRect(rect)

        font = QApplication.font()
        font.setPixelSize(min(rect.width(), rect.height()))
        self.over_text.setFont(font)
        self.over_text.setPos(rect.x()+rect.width()/2-self.over_text.boundingRect().width()/2,
                              rect.y()+rect.height()/2-self.over_text.boundingRect().height()/2)

    overBlockRect = Property(QRect, _overBlockRect, _setOverBlockRect)
