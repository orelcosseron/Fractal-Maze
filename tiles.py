from PySide6.QtCore import QObject, Slot, Property, QPropertyAnimation, QRect
from PySide6.QtGui import QPixmap, QBrush, QColor
from time import sleep


class Tile(QObject):
    def __init__(self, row, col, tile_type, scene):
        QObject.__init__(self)
        self.row = row
        self.col = col
        self.type = tile_type
        self.is_teleport = False
        self.is_link = False
        self.is_exit = False
        self.background = scene.addPixmap(
            QPixmap("./images/tiles/tile_" + str(tile_type).zfill(2) + ".png"))
        self.background.setOffset(self.col*20, self.row*20)
        self.visited = {}
        self.hash = hash("-".join(["0"]))

        self.path = {}
        self.path[8] = scene.addLine(10, 10, 10,  0, QColor("red"))
        self.path[4] = scene.addLine(10, 10, 20, 10, QColor("red"))
        self.path[2] = scene.addLine(10, 10, 10, 20, QColor("red"))
        self.path[1] = scene.addLine(10, 10,  0, 10, QColor("red"))

        self.path[8].setPos(self.col*20, self.row*20)
        self.path[4].setPos(self.col*20, self.row*20)
        self.path[2].setPos(self.col*20, self.row*20)
        self.path[1].setPos(self.col*20, self.row*20)

        self.path[8].setZValue(2)
        self.path[4].setZValue(2)
        self.path[2].setZValue(2)
        self.path[1].setZValue(2)

        self.path[8].hide()
        self.path[4].hide()
        self.path[2].hide()
        self.path[1].hide()

    def setTeleporter(self, is_teleport, direction=None, reach=None, scene=None):
        if self.is_teleport == is_teleport:
            return

        self.is_teleport = is_teleport
        if not self.is_teleport:
            self.teleporter.scene().removeItem(self.teleporter)
            del (self.teleporter_direction, self.teleport_reach, self.teleporter)
            return
        self.teleport_direction = direction
        self.teleport_reach = reach
        self.teleporter = scene.addPixmap(QPixmap(
            "./images/teleporters/teleport_" + str(direction) + ".png"))
        self.teleporter.setOffset(self.col*20-5, self.row*20-5)

    def setExit(self, is_exit, exit_name=None, orientation=None, scene=None):
        if self.is_exit == is_exit:
            return

        self.is_exit = is_exit
        if not self.is_exit:
            self.exit.scene().removeItem(self.exit)
            del (self.exit_name, self.exit, self.exit_orientation)
            return
        self.exit_name = exit_name
        self.exit = scene.addPixmap(QPixmap(
            "./images/exits/exit_" + str(orientation) + ".png"))
        self.exit.setOffset(self.col*20-5, self.row*20-5)
        self.exit_orientation = orientation

    def setLink(self, is_link, block_name=None, exit_tile=None, scene=None):
        if self.is_link == is_link:
            return

        self.is_link = is_link
        if not self.is_link:
            self.link.scene().removeItem(self.link)
            del (self.block_name, self.link_name, self.link)
            return
        self.block_name = block_name
        self.link_name = exit_tile.exit_name
        orientation = exit_tile.exit_orientation + 2
        if orientation > 4:
            orientation -= 4
        self.link = scene.addPixmap(QPixmap(
            "./images/links/link_" + str(orientation) + ".png"))
        self.link.setOffset(self.col*20-5, self.row*20-5)

    def hideExit(self):
        if self.is_exit:
            self.exit.hide()

    def showExit(self):
        if self.is_exit:
            self.exit.show()

    def addPath(self, direction):
        if self.hash in self.visited.keys():
            if self.visited[self.hash] & direction != 0:
                self.path[direction].hide()
            else:
                self.path[direction].show()
            self.visited[self.hash] ^= direction
        else:
            self.visited[self.hash] = direction
            self.path[direction].show()

    @ Slot()
    def refresh(self, stack):
        self.path[8].hide()
        self.path[4].hide()
        self.path[2].hide()
        self.path[1].hide()
        self.hash = hash("-".join(stack))
        if self.hash in self.visited.keys():
            if self.visited[self.hash] & 8 == 8:
                self.path[8].show()
            if self.visited[self.hash] & 4 == 4:
                self.path[4].show()
            if self.visited[self.hash] & 2 == 2:
                self.path[2].show()
            if self.visited[self.hash] & 1 == 1:
                self.path[1].show()

    @ Slot()
    def reset(self):
        if self.hash in self.path.keys():
            self.path[self.hash].hide()
        self.path = {}
        self.visited = {}
        self.hash = hash("-".join(["0"]))
