from tiles import Tile
from block import Block
from player import Player
from PySide6.QtWidgets import (
    QHBoxLayout, QWidget, QGraphicsView, QGraphicsScene)
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtCore import Qt, Signal, Slot, QPropertyAnimation, QParallelAnimationGroup, QSequentialAnimationGroup, QEasingCurve, QRect, QPointF, QPoint, QSize, Property


class Maze(QWidget):

    change_block = Signal(list)
    game_over = Signal(bool)

    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setStyleSheet("background-color: #477f1e")
        self.layout.addWidget(self.view)

        self.tiles = []
        self.blocks = {}
        self.exits = {}
        self.block_stack = ["0"]
        self.win = False

        i = 0
        f = open(r"./labyrinth", "r")
        lines = f.readlines()

        for line in lines:
            line = line.replace("\n", "").strip()

            if line == "" or line[0] == "#":
                continue

            if line[:8] == "TELEPORT":
                _, teleport_row, teleport_col, teleport_spec = line.split(" ")
                teleport_direction, teleport_reach = teleport_spec.split("+")
                self.tiles[int(teleport_row)][int(teleport_col)].setTeleporter(
                    True, int(teleport_direction), int(teleport_reach), self.scene)
                continue

            if line[:5] == "BLOCK":
                _, block_name, block_row, block_col = line.split(" ")
                self.blocks[block_name] = Block(
                    int(block_row), int(block_col), block_name, self.scene)
                continue

            if line[:4] == "LINK":
                _, block_name, exit_name, link_row, link_col = line.split(" ")
                exit_tile = self.tiles[self.exits[exit_name]
                                       [0]][self.exits[exit_name][1]]
                self.tiles[int(link_row)][int(link_col)].setLink(
                    True, block_name, exit_tile, self.scene)
                self.blocks[block_name].add_exit(
                    exit_name, int(link_row), int(link_col))
                continue

            if line[:4] == "EXIT":
                _, exit_name, exit_orientation, exit_row, exit_col = line.split(
                    " ")
                self.tiles[int(exit_row)][int(exit_col)].setExit(
                    True, exit_name, int(exit_orientation), self.scene)
                self.exits[exit_name] = (int(exit_row), int(exit_col))
                continue

            if line[:6] == "PLAYER":
                _, player_row, player_col = line.split(" ")
                self.player = Player(
                    int(player_row), int(player_col), self.scene)
                continue

            self.tiles += [[Tile(i, j, int(line[2*j:2*j+2]), self.scene)
                            for j in range(len(line) >> 1)]]
            for tile in self.tiles[-1]:
                self.change_block.connect(tile.refresh)
            i += 1

    @ Slot()
    def reset(self):
        if not self.win:
            self.player.reset()
            self.block_stack = ["0"]
            for row in self.tiles:
                for tile in row:
                    tile.reset()
            self.block_changed()

    def update_player(self, key):
        if not self.win:
            teleport = None
            tile = self.tiles[self.player.row][self.player.col]
            north = tile.type & 8 == 8
            east = tile.type & 4 == 4
            south = tile.type & 2 == 2
            west = tile.type & 1 == 1
            if key == Qt.Key_Z and north:
                self.player.row -= 1
                tile.addPath(8)
                self.tiles[self.player.row][self.player.col].addPath(2)
            elif key == Qt.Key_D and east:
                self.player.col += 1
                tile.addPath(4)
                self.tiles[self.player.row][self.player.col].addPath(1)
            elif key == Qt.Key_S and south:
                self.player.row += 1
                tile.addPath(2)
                self.tiles[self.player.row][self.player.col].addPath(8)
            elif key == Qt.Key_Q and west:
                self.player.col -= 1
                tile.addPath(1)
                self.tiles[self.player.row][self.player.col].addPath(4)

            if tile.is_teleport:
                north = tile.teleport_direction == 4
                east = tile.teleport_direction == 1
                south = tile.teleport_direction == 2
                west = tile.teleport_direction == 3
                if key == Qt.Key_Z and north:
                    self.player.row -= tile.teleport_reach
                    tile.addPath(8)
                    self.tiles[self.player.row][self.player.col].addPath(2)
                elif key == Qt.Key_D and east:
                    self.player.col += tile.teleport_reach
                    tile.addPath(4)
                    self.tiles[self.player.row][self.player.col].addPath(1)
                elif key == Qt.Key_S and south:
                    self.player.row += tile.teleport_reach
                    tile.addPath(2)
                    self.tiles[self.player.row][self.player.col].addPath(8)
                elif key == Qt.Key_Q and west:
                    self.player.col -= tile.teleport_reach
                    tile.addPath(1)
                    self.tiles[self.player.row][self.player.col].addPath(4)

            if tile.is_link:
                exit_tile = self.tiles[self.exits[tile.link_name]
                                       [0]][self.exits[tile.link_name][1]]
                link_orientation = exit_tile.exit_orientation + 2
                if link_orientation > 4:
                    link_orientation -= 4
                north = link_orientation == 4
                east = link_orientation == 1
                south = link_orientation == 2
                west = link_orientation == 3
                if (key == Qt.Key_Z and north) or (key == Qt.Key_Q and west) or (key == Qt.Key_S and south) or (key == Qt.Key_D and east):
                    self.player.row = exit_tile.row
                    self.player.col = exit_tile.col
                    self.block_stack += [tile.block_name]
                    tile.addPath(1 << (3-(link_orientation % 4)))
                    self.block_changed()
                    self.tiles[self.player.row][self.player.col].addPath(
                        1 << (3-((link_orientation + 2) % 4)))
                    teleport = link_orientation
                    self.zoomIn(tile.block_name)

            if tile.is_exit:
                north = tile.exit_orientation == 4
                east = tile.exit_orientation == 1
                south = tile.exit_orientation == 2
                west = tile.exit_orientation == 3
                if (key == Qt.Key_Z and north) or (key == Qt.Key_Q and west) or (key == Qt.Key_S and south) or (key == Qt.Key_D and east):
                    if self.block_stack[-1] != '0':
                        current_block = self.blocks[self.block_stack[-1]]

                        if tile.exit_name in current_block.exits.keys():
                            self.player.row = current_block.exits[tile.exit_name][0]
                            self.player.col = current_block.exits[tile.exit_name][1]
                            tile.addPath(1 << (3-(tile.exit_orientation % 4)))
                            self.zoomOut(self.block_stack.pop())
                            self.block_changed()
                            self.tiles[self.player.row][self.player.col].addPath(
                                1 << (3-((tile.exit_orientation + 2) % 4)))
                            teleport = tile.exit_orientation
                    else:
                        self.win = True
                        self.view.setStyleSheet("background-color: black")
                        self.scene.clear()
                        self.scene.addPixmap(QPixmap("./images/game_over.jpg"))
                        self.scene.setSceneRect(self.scene.itemsBoundingRect())
                        self.view.fitInView(
                            self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
                        self.game_over.emit(False)
                        return

            self.player.move(teleport=teleport)

    def block_changed(self):
        if self.block_stack[-1] == '0':
            for exit in self.exits.values():
                self.tiles[exit[0]][exit[1]].showExit()
        else:
            current_block = self.blocks[self.block_stack[-1]]
            for exit in self.exits.keys():
                if exit in current_block.exits.keys():
                    self.tiles[self.exits[exit][0]
                               ][self.exits[exit][1]].showExit()
                else:
                    self.tiles[self.exits[exit][0]
                               ][self.exits[exit][1]].hideExit()
        self.change_block.emit(self.block_stack)

    def zoomIn(self, block_name):
        block = self.blocks[block_name]

        initial_rect = self.scene.sceneRect()
        zoom = QPointF(initial_rect.width()/60.0, initial_rect.height()/60.0)

        self.m_animation_fade_out = QPropertyAnimation(
            block,
            b"opacity",
            parent=self,
            duration=300
        )
        self.m_animation_fade_out.setStartValue(1.0)
        self.m_animation_fade_out.setEndValue(0.1)

        self.m_animation_pan_in = QPropertyAnimation(
            self.scene,
            b"sceneRect",
            parent=self,
            duration=350,
        )
        self.m_animation_pan_in.setStartValue(initial_rect)
        self.m_animation_pan_in.setEndValue(QRect(
            block.col*20, block.row*20, block.col*20+60, block.row*20+60))
        self.m_animation_pan_in.setEasingCurve(QEasingCurve.InOutQuad)

        self.m_animation_zoom_in = QPropertyAnimation(
            self,
            b"zoom",
            parent=self,
            duration=350,
        )
        self.m_animation_zoom_in.setStartValue(self.zoom)
        self.m_animation_zoom_in.setEndValue(zoom)
        self.m_animation_zoom_in.setEasingCurve(QEasingCurve.InOutQuad)

        self.zoom_1 = QParallelAnimationGroup()
        self.zoom_1.addAnimation(self.m_animation_fade_out)
        self.zoom_1.addAnimation(self.m_animation_pan_in)
        self.zoom_1.addAnimation(self.m_animation_zoom_in)

        self.m_animation_fade_in = QPropertyAnimation(
            block,
            b"opacity",
            parent=self,
            duration=0
        )
        self.m_animation_fade_in.setStartValue(0.1)
        self.m_animation_fade_in.setEndValue(1.0)

        self.m_animation_pan_out = QPropertyAnimation(
            self.scene,
            b"sceneRect",
            parent=self,
            duration=0,
        )
        self.m_animation_pan_out.setStartValue(
            self.scene.sceneRect())
        self.m_animation_pan_out.setEndValue(initial_rect)

        self.m_animation_zoom_out = QPropertyAnimation(
            self,
            b"zoom",
            parent=self,
            duration=0,
        )
        self.m_animation_zoom_out.setStartValue(self.zoom)
        self.m_animation_zoom_out.setEndValue(QPointF(1, 1))

        self.zoom_2 = QParallelAnimationGroup()
        self.zoom_2.addAnimation(self.m_animation_fade_in)
        self.zoom_2.addAnimation(self.m_animation_pan_out)
        self.zoom_2.addAnimation(self.m_animation_zoom_out)

        self.m_animation_zoom = QSequentialAnimationGroup()
        self.m_animation_zoom.addAnimation(self.zoom_1)
        self.m_animation_zoom.addPause(75)
        self.m_animation_zoom.addAnimation(self.zoom_2)
        self.m_animation_zoom.start()

    def zoomOut(self, block_name):
        block = self.blocks[block_name]

        initial_rect = self.scene.sceneRect()

        zoom = QPointF(20.0/initial_rect.width(), 20.0/initial_rect.height())

        self.m_animation_zoom_out = QPropertyAnimation(
            self,
            b"zoom",
            parent=self,
            duration=350,
        )
        self.m_animation_zoom_out.setStartValue(self.zoom)
        self.m_animation_zoom_out.setEndValue(zoom)
        self.m_animation_zoom_out.setEasingCurve(QEasingCurve.InOutQuad)

        self.m_animation_zoom_in = QPropertyAnimation(
            self,
            b"zoom",
            parent=self,
            duration=0,
        )
        self.m_animation_zoom_in.setStartValue(self.zoom)
        self.m_animation_zoom_in.setEndValue(QPointF(1, 1))

        self.m_animation_zoom = QSequentialAnimationGroup()
        self.m_animation_zoom.addAnimation(self.m_animation_zoom_out)
        self.m_animation_zoom.addPause(75)
        self.m_animation_zoom.addAnimation(self.m_animation_zoom_in)
        self.m_animation_zoom.start()

    def _zoom(self):
        return QPointF(self.view.transform().m11(), self.view.transform().m22())

    def _setZoom(self, scale):
        self.view.setTransform(QTransform(scale.x(), self.view.transform().m12(), self.view.transform().m13(), self.view.transform().m21(), scale.y(),
                                          self.view.transform().m23(), self.view.transform().m31(), self.view.transform().m32(), self.view.transform().m33()))

    zoom = Property(QPointF, _zoom, _setZoom)
