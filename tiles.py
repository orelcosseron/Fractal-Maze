from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPixmap


class Tile(QWidget):
    def __init__(self, row, col, tile_type):
        QWidget.__init__(self)
        self.row = row
        self.col = col
        self.type = int(tile_type)
        self.is_teleport = False
        self.is_link = False
        self.is_exit = False

        self.pixmap = QPixmap("./images/tiles/tile_" + tile_type + ".png")

    def setTeleporter(self, is_teleport, direction=-1, reach=-1):
        self.is_teleport = is_teleport
        if not self.is_teleport:
            return
        self.teleport_direction = int(direction)
        self.teleport_reach = int(reach)

    def setExit(self, is_exit, exit_name=-1):
        self.is_exit = is_exit
        if not self.is_exit:
            return
        self.exit_name = exit_name

    def setLink(self, is_link, block_name="", link_name=""):
        self.is_link = is_link
        if not self.is_link:
            return
        self.block_name = block_name
        self.link_name = link_name
