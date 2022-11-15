from PySide6.QtCore import QObject, Slot, QRect, Qt
from PySide6.QtGui import QColor, QLinearGradient

from line import Line
from directions import Direction


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

        self.reach = {}
        if tile_type & (Direction.NORTH.value) != 0:
            self.reach[Direction.NORTH] = 1
            scene.addRect(QRect(self.col * 20 + 5, self.row * 20,
                          10, 15), Qt.NoPen, QColor(path_color))
        if tile_type & (Direction.EAST.value) != 0:
            self.reach[Direction.EAST] = 1
            scene.addRect(QRect(self.col * 20 + 5, self.row *
                          20 + 5, 15, 10), Qt.NoPen, QColor(path_color))
        if tile_type & (Direction.SOUTH.value) != 0:
            self.reach[Direction.SOUTH] = 1
            scene.addRect(QRect(self.col * 20 + 5, self.row *
                          20 + 5, 10, 15), Qt.NoPen, QColor(path_color))
        if tile_type & (Direction.WEST.value) != 0:
            self.reach[Direction.WEST] = 1
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

        self.teleporters = {}
        self.teleporters[Direction.NORTH] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 - 5, 10, 20), Qt.NoPen, teleporter_gradient_N)
        self.teleporters[Direction.EAST] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 + 5, 20, 10), Qt.NoPen, teleporter_gradient_E)
        self.teleporters[Direction.SOUTH] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 + 5, 10, 20), Qt.NoPen, teleporter_gradient_S)
        self.teleporters[Direction.WEST] = scene.addRect(QRect(
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
        self.links = {}
        self.links[Direction.NORTH] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 - 5, 10, 20), Qt.NoPen, link_gradient_N)
        self.links[Direction.EAST] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 + 5, 20, 10), Qt.NoPen, link_gradient_E)
        self.links[Direction.SOUTH] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 + 5, 10, 20), Qt.NoPen, link_gradient_S)
        self.links[Direction.WEST] = scene.addRect(QRect(
            self.col * 20 - 5, self.row * 20 + 5, 20, 10), Qt.NoPen, link_gradient_W)

        for link in self.links.values():
            link.setZValue(2)
            link.hide()

        self.exit_name = {}
        self.exit_bg = {}
        self.exit_bg[Direction.NORTH] = scene.addRect(QRect(
            self.col * 20, self.row * 20 - 5, 20, 5), Qt.NoPen, QColor(background_color))
        self.exit_bg[Direction.EAST] = scene.addRect(QRect(
            self.col * 20 + 20, self.row * 20, 5, 20), Qt.NoPen, QColor(background_color))
        self.exit_bg[Direction.SOUTH] = scene.addRect(QRect(
            self.col * 20, self.row * 20 + 20, 20, 5), Qt.NoPen, QColor(background_color))
        self.exit_bg[Direction.WEST] = scene.addRect(QRect(
            self.col * 20 - 5, self.row * 20, 5, 20), Qt.NoPen, QColor(background_color))

        for exit in self.exit_bg.values():
            exit.setZValue(2)
            exit.hide()

        self.exits_path = {}
        self.exits_path[Direction.NORTH] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 - 5, 10, 20), Qt.NoPen, QColor(path_color))
        self.exits_path[Direction.EAST] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 + 5, 20, 10), Qt.NoPen, QColor(path_color))
        self.exits_path[Direction.SOUTH] = scene.addRect(QRect(
            self.col * 20 + 5, self.row * 20 + 5, 10, 20), Qt.NoPen, QColor(path_color))
        self.exits_path[Direction.WEST] = scene.addRect(QRect(
            self.col * 20 - 5, self.row * 20 + 5, 20, 10), Qt.NoPen, QColor(path_color))

        for exit in self.exits_path.values():
            exit.setZValue(2)
            exit.hide()

        self.lines = {}
        self.lines[Direction.NORTH] = Line(
            self.row, self.col, Direction.NORTH, scene)
        self.lines[Direction.EAST] = Line(
            self.row, self.col, Direction.EAST, scene)
        self.lines[Direction.SOUTH] = Line(
            self.row, self.col, Direction.SOUTH, scene)
        self.lines[Direction.WEST] = Line(
            self.row, self.col, Direction.WEST, scene)

    def setTeleporter(self, direction, reach):
        self.reach[direction] = reach
        self.teleporters[direction].show()

    def unsetTeleporter(self, direction):
        self.reach.pop(direction)
        self.teleporters[direction].hide()

    def setLink(self, block_name, exit_tile, exit_name):
        orientation = exit_tile.exitOrientation(exit_name).opposite()
        self.links[orientation].show()
        self.linked_block[orientation] = (block_name, exit_name)

    def unsetLink(self, block_name, exit_tile):
        orientation = exit_tile.exitOrientation(exit_name).opposite()
        self.links[orientation].hide()
        self.linked_block.pop(orientation)

    def setExit(self, exit_name=None, orientation=None):
        self.exit_name[orientation] = exit_name
        self.exit_bg[orientation].show()
        self.exits_path[orientation].show()
        self.lines[orientation].setExit()

    def unsetExit(self, orientation=None):
        self.exit_name.pop(orientation)
        self.exit_bg[orientation].hide()
        self.exits_path[orientation].hide()
        self.lines[orientation].unsetExit()

    def showExit(self, exit_name):
        orientation = self.exitOrientation(exit_name)
        self.exit_bg[orientation].show()
        self.exits_path[orientation].show()

    def hideExit(self, exit_name):
        orientation = self.exitOrientation(exit_name)
        self.exit_bg[orientation].hide()
        self.exits_path[orientation].hide()

    def exitOrientation(self, exit_name):
        orientations = list(self.exit_name.keys())
        index = list(self.exit_name.values()).index(exit_name)
        return orientations[index]

    def drawPath(self, direction, inward=True):
        if self.hash in self.visited.keys():
            if self.visited[self.hash] & direction.value != 0:
                self.lines[direction].hide(inward)
            else:
                self.lines[direction].show(inward)
            self.visited[self.hash] ^= direction.value
        else:
            self.visited[self.hash] = direction.value
            self.lines[direction].show(inward)

    @ Slot()
    def refresh(self, stack):
        for line in self.lines.values():
            line.hide(now=True)

        self.hash = hash("-".join(stack))

        if self.hash in self.visited.keys():
            for direction in Direction:
                if self.visited[self.hash] & direction.value != 0:
                    self.lines[direction].show(now=True)

    @ Slot()
    def reset(self):
        self.visited = {}
        self.hash = hash("-".join(["0"]))
