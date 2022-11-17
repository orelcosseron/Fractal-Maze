from PySide6.QtWidgets import QHBoxLayout, QGraphicsScene, QGraphicsView
from PySide6.QtGui import QTransform, QPixmap
from PySide6.QtCore import Signal, Property, QPointF, Slot, Qt, QAbstractAnimation, QPropertyAnimation, QSequentialAnimationGroup, QRect, QEasingCurve, QParallelAnimationGroup

from directions import Direction
from tiles import Tile
from block import Block
from player import Player

from time import sleep


class Maze(QGraphicsView):

    change_block = Signal(list)
    game_over = Signal(bool)

    def __init__(self):
        self.scene = QGraphicsScene()
        QGraphicsView.__init__(self, self.scene)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameStyle(0)

        self.tiles = []
        self.blocks = {}
        self.exits = {}
        self.block_stack = ["0"]
        self.win = False

        self.m_animation_zoom = {}
        self.m_animation_pan = {}
        self.zoom_animation = {}

        self.setLabyrinth()
        self.setFixedSize(self.scene.width(),
                          self.scene.height())

    def setLabyrinth(self):
        i = 0
        f = open(r"./labyrinth", "r")
        lines = f.readlines()

        for line in lines:
            line = line.replace("\n", "").strip()

            if line == "" or line[0] == "#":
                continue

            if line[:9] == "TILE_SIZE":
                _, tile_size = line.split(" ")
                self.tile_size = int(tile_size)
                continue

            if line[:13] == "OUTSIDE_COLOR":
                _, self.outside_color = line.split(" ")
                self.setStyleSheet("background-color: " + self.outside_color)
                continue

            if line[:16] == "BACKGROUND_COLOR":
                _, self.background_color = line.split(" ")
                continue

            if line[:10] == "PATH_COLOR":
                _, self.path_color = line.split(" ")
                continue

            if line[:10] == "LINE_COLOR":
                _, self.line_color = line.split(" ")
                continue

            if line[:8] == "TELEPORT":
                _, teleport_row, teleport_col, teleport_spec = line.split(" ")
                teleport_direction, teleport_reach = teleport_spec.split("+")
                self.tiles[int(teleport_row)][int(teleport_col)].setTeleporter(
                    Direction(int(teleport_direction)), int(teleport_reach))
                continue

            if line[:5] == "BLOCK":
                _, block_name, block_row, block_col, width, height, block_color = line.split(
                    " ")
                self.blocks[block_name] = Block(
                    int(block_row), int(block_col), int(width), int(height), self.tile_size, block_name, block_color, self.scene)
                self.setZoom(self.blocks[block_name])
                continue

            if line[:4] == "LINK":
                _, block_name, exit_name, link_row, link_col = line.split(" ")
                exit_tile = self.tiles[self.exits[exit_name]
                                       [0]][self.exits[exit_name][1]]
                self.tiles[int(link_row)][int(link_col)].setLink(
                    block_name, exit_tile, exit_name)
                self.blocks[block_name].add_exit(
                    exit_name, int(link_row), int(link_col))
                continue

            if line[:4] == "EXIT":
                _, exit_name, exit_orientation, exit_row, exit_col = line.split(
                    " ")
                self.tiles[int(exit_row)][int(exit_col)].setExit(
                    exit_name, Direction(int(exit_orientation)))
                self.exits[exit_name] = (int(exit_row), int(exit_col))
                continue

            if line[:6] == "PLAYER":
                _, player_row, player_col, player_color = line.split(" ")
                self.player = Player(
                    int(player_row), int(player_col), self.tile_size, player_color, self.scene)
                continue

            self.tiles += [[Tile(i, j, int(line[2*j:2*j+2]), self.tile_size, self.background_color, self.path_color, self.line_color, self.scene)
                            for j in range(len(line) >> 1)]]
            for tile in self.tiles[-1]:
                self.change_block.connect(tile.refresh)
            i += 1

        self.player.hide()
        for _ in range(5):
            for block in self.blocks.values():
                for exit in self.exits.keys():
                    if exit in block.exits.keys():
                        self.tiles[self.exits[exit][0]
                                   ][self.exits[exit][1]].showExit(exit)
                    else:
                        self.tiles[self.exits[exit][0]
                                   ][self.exits[exit][1]].hideExit(exit)
                block.pre_render()
            for block in self.blocks.values():
                block.render()
        for exit in self.exits:
            self.tiles[self.exits[exit][0]][self.exits[exit][1]].showExit(exit)
        self.player.show()

    def setZoom(self, block):
        initial_rect = self.scene.sceneRect()
        zoomed_in_rect = QRect(
            block.block.pos().toPoint(), block.block.boundingRect().size().toSize())
        zoom_horizontal_ratio = initial_rect.width()/zoomed_in_rect.width()
        zoom_vertical_ratio = initial_rect.height()/zoomed_in_rect.height()

        duration = 450

        self.m_animation_zoom[block.name] = QPropertyAnimation(
            self,
            b"zoom",
            parent=self,
            duration=duration,
        )
        self.m_animation_zoom[block.name].setStartValue(self.zoom)
        self.m_animation_zoom[block.name].setKeyValueAt(
            0.88888, QPointF(zoom_horizontal_ratio, zoom_vertical_ratio))
        self.m_animation_zoom[block.name].setKeyValueAt(
            0.99999, QPointF(zoom_horizontal_ratio, zoom_vertical_ratio))
        self.m_animation_zoom[block.name].setEndValue(self.zoom)

        self.m_animation_pan[block.name] = QPropertyAnimation(
            self.scene,
            b"sceneRect",
            parent=self,
            duration=duration,
        )
        self.m_animation_pan[block.name].setStartValue(initial_rect)
        self.m_animation_pan[block.name].setKeyValueAt(
            0.88888, zoomed_in_rect)
        self.m_animation_pan[block.name].setKeyValueAt(
            0.99999, zoomed_in_rect)
        self.m_animation_pan[block.name].setEndValue(initial_rect)

        self.zoom_animation[block.name] = QParallelAnimationGroup()
        self.zoom_animation[block.name].addAnimation(
            self.m_animation_pan[block.name])
        self.zoom_animation[block.name].addAnimation(
            self.m_animation_zoom[block.name])

    def _zoom(self):
        return QPointF(self.transform().m11(), self.transform().m22())

    def _setZoom(self, scale):
        self.setTransform(QTransform(scale.x(), self.transform().m12(), self.transform().m13(), self.transform().m21(), scale.y(),
                                     self.transform().m23(), self.transform().m31(), self.transform().m32(), self.transform().m33()))

    zoom = Property(QPointF, _zoom, _setZoom)

    @ Slot()
    def reset(self):
        if not self.win:
            self.player.reset()
            for row in self.tiles:
                for tile in row:
                    tile.reset()
            for block in self.blocks.values():
                block.reset()
            self.zoom_animation[self.block_stack[1]].setDirection(
                QAbstractAnimation.Direction().Backward)
            self.zoom_animation[self.block_stack[1]].start()
            self.block_stack = ["0"]
            self.block_changed()

    def update_player(self, direction):
        if not self.win:
            teleport = None
            tile = self.tiles[self.player.row][self.player.col]

            if direction in tile.reach:
                if direction == Direction.NORTH:
                    self.player.row -= tile.reach[direction]
                elif direction == Direction.EAST:
                    self.player.col += tile.reach[direction]
                elif direction == Direction.SOUTH:
                    self.player.row += tile.reach[direction]
                elif direction == Direction.WEST:
                    self.player.col -= tile.reach[direction]
                tile.drawPath(direction, False)
                self.tiles[self.player.row][self.player.col].drawPath(
                    direction.opposite(), True)

            if direction in tile.linked_block:
                block_name, exit_name = tile.linked_block[direction]
                exit_tile = self.tiles[self.exits[exit_name]
                                       [0]][self.exits[exit_name][1]]
                self.player.row = exit_tile.row
                self.player.col = exit_tile.col
                tile.drawPath(direction, False)
                self.add_block(block_name)
                self.tiles[self.player.row][self.player.col].drawPath(
                    direction.opposite(), True)
                teleport = direction
                self.zoom_animation[block_name].setDirection(
                    QAbstractAnimation.Direction().Forward)
                self.zoom_animation[block_name].start()

            if direction in tile.exit_name:
                if self.block_stack[-1] != '0':
                    exit_name = tile.exit_name[direction]
                    current_block = self.blocks[self.block_stack[-1]]

                    if exit_name in current_block.exits.keys():
                        self.player.row = current_block.exits[exit_name][0]
                        self.player.col = current_block.exits[exit_name][1]
                        tile.drawPath(direction, False)
                        block_name = self.pop_block()
                        self.zoom_animation[block_name].setDirection(
                            QAbstractAnimation.Direction().Backward)
                        self.zoom_animation[block_name].start()
                        self.tiles[self.player.row][self.player.col].drawPath(
                            direction.opposite(), True)
                        teleport = direction
                else:
                    self.win = True
                    self.setStyleSheet("background-color: black")
                    self.scene.clear()
                    self.scene.addPixmap(QPixmap("./images/game_over.jpg"))
                    self.scene.setSceneRect(self.scene.itemsBoundingRect())
                    self.fitInView(
                        self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
                    self.game_over.emit(False)
                    return

            if not self.win:
                self.player.move(teleport=teleport)

    def add_block(self, block):
        self.block_stack += [block]
        self.block_changed()

    def pop_block(self):
        pop = self.block_stack.pop()
        self.player.hide()
        self.blocks[pop].pre_render(hash("-".join(self.block_stack)))
        self.player.show()
        self.block_changed()
        return pop

    def block_changed(self):
        for block in self.blocks.values():
            block.render(hash("-".join(self.block_stack)))
        if self.block_stack[-1] == '0':
            self.setStyleSheet(
                "background-color: " + self.outside_color)
            for exit in self.exits:
                self.tiles[self.exits[exit][0]
                           ][self.exits[exit][1]].showExit(exit)
        else:
            current_block = self.blocks[self.block_stack[-1]]
            self.setStyleSheet("background-color: " + current_block.color)
            for exit in self.exits.keys():
                if exit in current_block.exits.keys():
                    self.tiles[self.exits[exit][0]
                               ][self.exits[exit][1]].showExit(exit)
                else:
                    self.tiles[self.exits[exit][0]
                               ][self.exits[exit][1]].hideExit(exit)
        self.change_block.emit(self.block_stack)

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Z, Qt.Key_W, Qt.Key_I, Qt.Key_Up]:
            self.update_player(Direction.NORTH)
        elif event.key() in [Qt.Key_Q, Qt.Key_A, Qt.Key_J, Qt.Key_Left]:
            self.update_player(Direction.WEST)
        elif event.key() in [Qt.Key_S, Qt.Key_K, Qt.Key_Down]:
            self.update_player(Direction.SOUTH)
        elif event.key() in [Qt.Key_D, Qt.Key_L, Qt.Key_Right]:
            self.update_player(Direction.EAST)
