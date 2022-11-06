from PySide6.QtCore import Qt, QObject, Slot, Property, QPropertyAnimation, QRect
from PySide6.QtGui import QPixmap, QBrush, QColor, QLinearGradient
from line import Line


class Tile(QObject):
    def __init__(self, row, col, tile_type, background_color, path_color, scene):
        QObject.__init__(self)
        self.row = row
        self.col = col
        self.type = tile_type
        self.is_exit = False
        self.visited = {}
        self.hash = hash("-".join(["0"]))

        scene.addRect(QRect(
            self.col*20, self.row*20, 20, 20), Qt.NoPen, QColor(background_color))

        if tile_type & 8 != 0:
            scene.addRect(QRect(self.col * 20 + 5, self.row * 20,
                          10, 15), Qt.NoPen, QColor(path_color))
        if tile_type & 4 != 0:
            scene.addRect(QRect(self.col * 20 + 5, self.row *
                          20 + 5, 15, 10), Qt.NoPen, QColor(path_color))
        if tile_type & 2 != 0:
            scene.addRect(QRect(self.col * 20 + 5, self.row *
                          20 + 5, 10, 15), Qt.NoPen, QColor(path_color))
        if tile_type & 1 != 0:
            scene.addRect(QRect(self.col * 20,     self.row *
                          20 + 5, 15, 10), Qt.NoPen, QColor(path_color))

        teleporter_gradient_N = QLinearGradient(
            self.col * 20, self.row * 20, self.col * 20, self.row * 20 - 5)
        teleporter_gradient_N.setColorAt(0, QColor(path_color))
        teleporter_gradient_N.setColorAt(1, QColor(path_color).darker(150))
        teleporter_gradient_E = QLinearGradient(
            self.col * 20 + 20, self.row * 20, self.col * 20 + 25, self.row * 20)
        teleporter_gradient_E.setColorAt(0, QColor(path_color))
        teleporter_gradient_E.setColorAt(1, QColor(path_color).darker(150))
        teleporter_gradient_S = QLinearGradient(
            self.col * 20, self.row * 20 + 20, self.col * 20, self.row * 20 + 25)
        teleporter_gradient_S.setColorAt(0, QColor(path_color))
        teleporter_gradient_S.setColorAt(1, QColor(path_color).darker(150))
        teleporter_gradient_W = QLinearGradient(
            self.col * 20, self.row * 20, self.col * 20-5, self.row * 20)
        teleporter_gradient_W.setColorAt(0, QColor(path_color))
        teleporter_gradient_W.setColorAt(1, QColor(path_color).darker(150))

        self.teleporter_reach = {}
        self.teleporters = {}
        self.teleporters[4] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 - 5, 10, 20), Qt.NoPen, teleporter_gradient_N)
        self.teleporters[1] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 + 5, 20, 10), Qt.NoPen, teleporter_gradient_E)
        self.teleporters[2] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 + 5, 10, 20), Qt.NoPen, teleporter_gradient_S)
        self.teleporters[3] = scene.addRect(QRect(
            self.col * 20 - 5, self.row * 20 + 5, 20, 10), Qt.NoPen, teleporter_gradient_W)

        for teleporter in self.teleporters.values():
            teleporter.setZValue(2)
            teleporter.hide()

        link_gradient_N = QLinearGradient(
            self.col * 20, self.row * 20, self.col * 20, self.row * 20 - 5)
        link_gradient_N.setColorAt(0, QColor(path_color))
        link_gradient_N.setColorAt(1, QColor(0, 0, 0, 0))
        link_gradient_E = QLinearGradient(
            self.col * 20 + 20, self.row * 20, self.col * 20 + 25, self.row * 20)
        link_gradient_E.setColorAt(0, QColor(path_color))
        link_gradient_E.setColorAt(1, QColor(0, 0, 0, 0))
        link_gradient_S = QLinearGradient(
            self.col * 20, self.row * 20 + 20, self.col * 20, self.row * 20 + 25)
        link_gradient_S.setColorAt(0, QColor(path_color))
        link_gradient_S.setColorAt(1, QColor(0, 0, 0, 0))
        link_gradient_W = QLinearGradient(
            self.col * 20, self.row * 20, self.col * 20-5, self.row * 20)
        link_gradient_W.setColorAt(0, QColor(path_color))
        link_gradient_W.setColorAt(1, QColor(0, 0, 0, 0))

        self.linked_block = {}
        self.link_reach = {}
        self.links = {}
        self.links[4] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 - 5, 10, 20), Qt.NoPen, link_gradient_N)
        self.links[1] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 + 5, 20, 10), Qt.NoPen, link_gradient_E)
        self.links[2] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 + 5, 10, 20), Qt.NoPen, link_gradient_S)
        self.links[3] = scene.addRect(QRect(
            self.col * 20 - 5, self.row * 20 + 5, 20, 10), Qt.NoPen, link_gradient_W)

        for link in self.links.values():
            link.setZValue(2)
            link.hide()

        self.exit_name = {}
        self.exit_bg = {}
        self.exit_bg[4] = scene.addRect(QRect(
            self.col * 20, self.row * 20 - 5, 20, 5), Qt.NoPen, QColor(background_color))
        self.exit_bg[1] = scene.addRect(QRect(
            self.col * 20 + 20, self.row * 20, 5, 20), Qt.NoPen, QColor(background_color))
        self.exit_bg[2] = scene.addRect(QRect(
            self.col * 20, self.row * 20 + 20, 20, 5), Qt.NoPen, QColor(background_color))
        self.exit_bg[3] = scene.addRect(QRect(
            self.col * 20 - 5, self.row * 20, 5, 20), Qt.NoPen, QColor(background_color))

        for exit in self.exit_bg.values():
            exit.setZValue(2)
            exit.hide()

        self.exits_path = {}
        self.exits_path[4] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 - 5, 10, 20), Qt.NoPen, QColor(path_color))
        self.exits_path[1] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 + 5, 20, 10), Qt.NoPen, QColor(path_color))
        self.exits_path[2] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 + 5, 10, 20), Qt.NoPen, QColor(path_color))
        self.exits_path[3] = scene.addRect(QRect(
            self.col * 20 - 5, self.row * 20 + 5, 20, 10), Qt.NoPen, QColor(path_color))

        for exit in self.exits_path.values():
            exit.setZValue(2)
            exit.hide()

        self.line = {}
        self.line[8] = Line(self.row, self.col, 8, scene)
        self.line[4] = Line(self.row, self.col, 4, scene)
        self.line[2] = Line(self.row, self.col, 2, scene)
        self.line[1] = Line(self.row, self.col, 1, scene)
        for line in self.line.values():
            line.setZValue(3)
            line.hide()

    def setTeleporter(self, direction=None, reach=None):
        self.teleporter_reach[direction] = reach
        self.teleporters[direction].show()

    def unsetTeleporter(self, direction):
        self.teleporter_reach.pop(direction)
        self.teleporters[direction].hide()

    def isTeleporter(self):
        return len(self.teleporter_reach) > 0

    def setLink(self, block_name, exit_tile, exit_name):
        orientation = exit_tile.exitOrientation(exit_name) + 2
        if orientation > 4:
            orientation -= 4
        self.links[orientation].show()
        self.linked_block[orientation] = (block_name, exit_name)

    def unsetLink(self, block_name, exit_tile):
        orientation = exit_tile.exit_orientation + 2
        if orientation > 4:
            orientation -= 4
        self.links[orientation].hide()
        self.linked_block.pop(orientation)

    def isLink(self):
        return len(self.linked_block) > 0

    def setExit(self, exit_name=None, orientation=None):
        self.exit_name[orientation] = exit_name
        self.exit_bg[orientation].show()
        self.exits_path[orientation].show()

    def unsetExit(self, orientation=None):
        self.exit_name.pop(orientation)
        self.exit_bg[orientation].hide()
        self.exits_path[orientation].hide()

    def showExit(self, exit_name):
        orientation = self.exitOrientation(exit_name)
        self.exit_bg[orientation].show()
        self.exits_path[orientation].show()

    def hideExit(self, exit_name):
        orientation = self.exitOrientation(exit_name)
        self.exit_bg[orientation].hide()
        self.exits_path[orientation].hide()

    def isExit(self):
        return len(self.exit_name) > 0

    def exitOrientation(self, exit_name):
        orientations = list(self.exit_name.keys())
        index = list(self.exit_name.values()).index(exit_name)
        return orientations[index]

    def drawPath(self, direction, inward=True):
        if self.hash in self.visited.keys():
            if self.visited[self.hash] & direction != 0:
                self.line[direction].hide()
            else:
                self.line[direction].show(inward)
            self.visited[self.hash] ^= direction
        else:
            self.visited[self.hash] = direction
            self.line[direction].show(inward)

    @ Slot()
    def refresh(self, stack):
        self.line[8].hide()
        self.line[4].hide()
        self.line[2].hide()
        self.line[1].hide()
        self.hash = hash("-".join(stack))
        if self.hash in self.visited.keys():
            if self.visited[self.hash] & 8 == 8:
                self.line[8].show()
            if self.visited[self.hash] & 4 == 4:
                self.line[4].show()
            if self.visited[self.hash] & 2 == 2:
                self.line[2].show()
            if self.visited[self.hash] & 1 == 1:
                self.line[1].show()

    @ Slot()
    def reset(self):
        self.visited = {}
        self.hash = hash("-".join(["0"]))
