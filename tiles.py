from PySide6.QtCore import QObject
from PySide6.QtGui import QPixmap


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
