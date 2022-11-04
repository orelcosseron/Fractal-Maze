from PySide6.QtCore import QObject
from PySide6.QtGui import QPixmap


class Tile(QObject):
    def __init__(self, x, y, tile_type, scene):
        QObject.__init__(self)
        self.x = x
        self.y = y
        self.type = int(tile_type)
        self.is_teleport = False
        self.is_link = False
        self.is_exit = False
        self.background = scene.addPixmap(
            QPixmap("./images/tiles/tile_" + tile_type + ".png"))
        self.background.setOffset(y*20, x*20)

    def setTeleporter(self, is_teleport, direction=None, reach=None, scene=None):
        self.is_teleport = is_teleport
        if not self.is_teleport:
            return
        self.teleport_direction = int(direction)
        self.teleport_reach = int(reach)
        self.teleporter = scene.addPixmap(QPixmap(
            "./images/teleporters/teleport_" + direction + ".png"))
        self.teleporter.setOffset(self.y*20-5, self.x*20-5)

    def setExit(self, is_exit, exit_name=None, orientation=None, scene=None):
        self.is_exit = is_exit
        if not self.is_exit:
            return
        self.exit_name = exit_name
        self.exit = scene.addPixmap(QPixmap(
            "./images/exits/exit_" + orientation + ".png"))
        self.exit.setOffset(self.y*20-5, self.x*20-5)
        self.exit_orientation = int(orientation)

    def setLink(self, is_link, block_name=None, exit_tile=None, scene=None):
        self.is_link = is_link
        if not self.is_link:
            return
        self.block_name = block_name
        self.link_name = exit_tile.exit_name
        orientation = exit_tile.exit_orientation + 2
        if orientation > 4:
            orientation -= 4
        self.link = scene.addPixmap(QPixmap(
            "./images/links/link_"+str(orientation)+".png"))
        self.link.setOffset(self.y*20-5, self.x*20-5)

    def hideExit(self):
        if self.is_exit:
            self.exit.hide()

    def showExit(self):
        if self.is_exit:
            self.exit.show()
