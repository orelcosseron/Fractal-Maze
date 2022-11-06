from tiles import Tile
from block import Block
from player import Player
from PySide6.QtWidgets import (
    QHBoxLayout, QWidget, QGraphicsView, QGraphicsScene, QGraphicsBlurEffect)
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
        self.layout.addWidget(self.view)

        self.tiles = []
        self.blocks = {}
        self.exits = {}
        self.block_stack = ["0"]
        self.win = False

        self.setLabyrinth()
        self.setBlur()
        self.setZoomIn()
        self.setZoomOut()

    def setLabyrinth(self):
        i = 0
        f = open(r"./labyrinth", "r")
        lines = f.readlines()

        for line in lines:
            line = line.replace("\n", "").strip()

            if line == "" or line[0] == "#":
                continue

            if line[:13] == "OUTSIDE_COLOR":
                _, self.outside_color = line.split(" ")
                self.view.setStyleSheet(
                    "background-color: " + self.outside_color)
                continue
            if line[:16] == "BACKGROUND_COLOR":
                _, self.background_color = line.split(" ")
                continue

            if line[:10] == "PATH_COLOR":
                _, self.path_color = line.split(" ")
                continue

            if line[:8] == "TELEPORT":
                _, teleport_row, teleport_col, teleport_spec = line.split(" ")
                teleport_direction, teleport_reach = teleport_spec.split("+")
                self.tiles[int(teleport_row)][int(teleport_col)].setTeleporter(
                    int(teleport_direction), int(teleport_reach))
                continue

            if line[:5] == "BLOCK":
                _, block_name, block_row, block_col, block_color = line.split(
                    " ")
                self.blocks[block_name] = Block(
                    int(block_row), int(block_col), block_name, block_color, self.scene)
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
                    exit_name, int(exit_orientation))
                self.exits[exit_name] = (int(exit_row), int(exit_col))
                continue

            if line[:6] == "PLAYER":
                _, player_row, player_col, player_color = line.split(" ")
                self.player = Player(
                    int(player_row), int(player_col), player_color, self.scene)
                continue

            self.tiles += [[Tile(i, j, int(line[2*j:2*j+2]), self.background_color, self.path_color, self.scene)
                            for j in range(len(line) >> 1)]]
            for tile in self.tiles[-1]:
                self.change_block.connect(tile.refresh)
            i += 1

    def setBlur(self):
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(0)
        self.view.setGraphicsEffect(self.blur_effect)

        self.m_animation_blur_in = QPropertyAnimation(
            self.blur_effect,
            b"blurRadius",
            parent=self,
            duration=175,
        )
        self.m_animation_blur_in.setStartValue(0)
        self.m_animation_blur_in.setEndValue(100)

        self.m_animation_blur_out = QPropertyAnimation(
            self.blur_effect,
            b"blurRadius",
            parent=self,
            duration=175,
        )
        self.m_animation_blur_out.setStartValue(100)
        self.m_animation_blur_out.setEndValue(0)

        self.blur_animation = QSequentialAnimationGroup()
        self.blur_animation.addAnimation(self.m_animation_blur_in)
        self.blur_animation.addAnimation(self.m_animation_blur_out)

    def setZoomIn(self):
        initial_rect = self.scene.sceneRect()
        initial_rect_width = initial_rect.width()
        initial_rect_height = initial_rect.height()
        zoomed_in_rect = QRect(
            QPointF(initial_rect.left()+initial_rect_width*0.125,
                    initial_rect.top()+initial_rect_height*0.125).toPoint(),
            initial_rect.size().toSize()/0.8)

        self.m_animation_zoom_in_in = QPropertyAnimation(
            self,
            b"zoom",
            parent=self,
            duration=175,
        )
        self.m_animation_zoom_in_in.setStartValue(self.zoom)
        self.m_animation_zoom_in_in.setEndValue(QPointF(1.25, 1.25))
        self.m_animation_zoom_in_in.setEasingCurve(QEasingCurve.InOutQuad)

        self.m_animation_zoom_in_out = QPropertyAnimation(
            self,
            b"zoom",
            parent=self,
            duration=175,
        )
        self.m_animation_zoom_in_out.setStartValue(QPointF(1.25, 1.25))
        self.m_animation_zoom_in_out.setEndValue(QPointF(1, 1))

        self.m_animation_pan_in = QPropertyAnimation(
            self.scene,
            b"sceneRect",
            parent=self,
            duration=175,
        )
        self.m_animation_pan_in.setStartValue(initial_rect)
        self.m_animation_pan_in.setEndValue(zoomed_in_rect)
        self.m_animation_pan_in.setEasingCurve(QEasingCurve.InOutQuad)

        self.m_animation_pan_out = QPropertyAnimation(
            self.scene,
            b"sceneRect",
            parent=self,
            duration=175,
        )
        self.m_animation_pan_out.setStartValue(
            zoomed_in_rect)
        self.m_animation_pan_out.setEndValue(initial_rect)

        self.m_animation_zoom_1 = QParallelAnimationGroup()
        self.m_animation_zoom_1.addAnimation(self.m_animation_zoom_in_in)
        self.m_animation_zoom_1.addAnimation(self.m_animation_pan_in)
        self.m_animation_zoom_2 = QParallelAnimationGroup()
        self.m_animation_zoom_2.addAnimation(self.m_animation_zoom_in_out)
        self.m_animation_zoom_2.addAnimation(self.m_animation_pan_out)
        self.m_animation_zoom_in = QSequentialAnimationGroup()
        self.m_animation_zoom_in.addAnimation(self.m_animation_zoom_1)
        self.m_animation_zoom_in.addAnimation(self.m_animation_zoom_2)
        self.zoomIn = QParallelAnimationGroup()
        self.zoomIn.addAnimation(self.m_animation_zoom_in)

    def setZoomOut(self):
        initial_rect = self.scene.sceneRect()

        self.m_animation_zoom_out_out = QPropertyAnimation(
            self,
            b"zoom",
            parent=self,
            duration=175,
        )
        self.m_animation_zoom_out_out.setStartValue(self.zoom)
        self.m_animation_zoom_out_out.setEndValue(QPointF(0.8, 0.8))
        self.m_animation_zoom_out_out.setEasingCurve(QEasingCurve.InOutQuad)

        self.m_animation_zoom_out_in = QPropertyAnimation(
            self,
            b"zoom",
            parent=self,
            duration=175,
        )
        self.m_animation_zoom_out_in.setStartValue(QPointF(0.8, 0.8))
        self.m_animation_zoom_out_in.setEndValue(QPointF(1, 1))

        self.m_animation_zoom_out = QSequentialAnimationGroup()
        self.m_animation_zoom_out.addAnimation(self.m_animation_zoom_out_out)
        self.m_animation_zoom_out.addAnimation(self.m_animation_zoom_out_in)
        self.zoomOut = QParallelAnimationGroup()
        self.zoomOut.addAnimation(self.m_animation_zoom_out)

    def _zoom(self):
        return QPointF(self.view.transform().m11(), self.view.transform().m22())

    def _setZoom(self, scale):
        self.view.setTransform(QTransform(scale.x(), self.view.transform().m12(), self.view.transform().m13(), self.view.transform().m21(), scale.y(),
                                          self.view.transform().m23(), self.view.transform().m31(), self.view.transform().m32(), self.view.transform().m33()))

    zoom = Property(QPointF, _zoom, _setZoom)

    @ Slot()
    def reset(self):
        if not self.win:
            self.player.reset()
            self.block_stack = ["0"]
            for row in self.tiles:
                for tile in row:
                    tile.reset()
            self.block_changed()
            self.zoomOut.addAnimation(self.blur_animation)
            self.zoomOut.start()

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

            if tile.isTeleporter():
                north = 4 in tile.teleporter_reach
                east = 1 in tile.teleporter_reach
                south = 2 in tile.teleporter_reach
                west = 3 in tile.teleporter_reach
                if key == Qt.Key_Z and north:
                    self.player.row -= tile.teleporter_reach[4]
                    tile.addPath(8)
                    self.tiles[self.player.row][self.player.col].addPath(2)
                elif key == Qt.Key_D and east:
                    self.player.col += tile.teleporter_reach[1]
                    tile.addPath(4)
                    self.tiles[self.player.row][self.player.col].addPath(1)
                elif key == Qt.Key_S and south:
                    self.player.row += tile.teleporter_reach[2]
                    tile.addPath(2)
                    self.tiles[self.player.row][self.player.col].addPath(8)
                elif key == Qt.Key_Q and west:
                    self.player.col -= tile.teleporter_reach[3]
                    tile.addPath(1)
                    self.tiles[self.player.row][self.player.col].addPath(4)

            if tile.isLink():
                north = 4 in tile.linked_block
                east = 1 in tile.linked_block
                south = 2 in tile.linked_block
                west = 3 in tile.linked_block

                block_name, exit_name = None, None
                if key == Qt.Key_Z and north:
                    block_name, exit_name = tile.linked_block[4]
                elif key == Qt.Key_Q and west:
                    block_name, exit_name = tile.linked_block[3]
                elif key == Qt.Key_S and south:
                    block_name, exit_name = tile.linked_block[2]
                elif key == Qt.Key_D and east:
                    block_name, exit_name = tile.linked_block[1]

                if block_name is not None:
                    exit_tile = self.tiles[self.exits[exit_name]
                                           [0]][self.exits[exit_name][1]]
                    link_orientation = (
                        exit_tile.exitOrientation(exit_name) + 2) % 4
                    self.player.row = exit_tile.row
                    self.player.col = exit_tile.col
                    tile.addPath(1 << (3-link_orientation))
                    self.block_stack += [block_name]
                    self.block_changed()
                    self.tiles[self.player.row][self.player.col].addPath(
                        1 << (3-(exit_tile.exitOrientation(exit_name) % 4)))
                    teleport = link_orientation if link_orientation > 0 else 4
                    self.zoomIn.addAnimation(self.blur_animation)
                    self.zoomIn.start()

            if tile.isExit():
                north = 4 in tile.exit_name
                east = 1 in tile.exit_name
                south = 2 in tile.exit_name
                west = 3 in tile.exit_name

                exit_name = None
                if key == Qt.Key_Z and north:
                    exit_name = tile.exit_name[4]
                if key == Qt.Key_Q and west:
                    exit_name = tile.exit_name[3]
                if key == Qt.Key_S and south:
                    exit_name = tile.exit_name[2]
                if key == Qt.Key_D and east:
                    exit_name = tile.exit_name[1]

                if exit_name is not None:
                    if self.block_stack[-1] != '0':
                        current_block = self.blocks[self.block_stack[-1]]

                        if exit_name in current_block.exits.keys():
                            self.player.row = current_block.exits[exit_name][0]
                            self.player.col = current_block.exits[exit_name][1]
                            tile.addPath(
                                1 << (3-(tile.exitOrientation(exit_name) % 4)))
                            self.block_stack.pop()
                            self.block_changed()
                            self.tiles[self.player.row][self.player.col].addPath(
                                1 << (3-((tile.exitOrientation(exit_name) + 2) % 4)))
                            teleport = tile.exitOrientation(exit_name)
                            self.zoomOut.addAnimation(self.blur_animation)
                            self.zoomOut.start()
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
            self.view.setStyleSheet(
                "background-color: " + self.outside_color)
            for exit in self.exits:
                self.tiles[self.exits[exit][0]
                           ][self.exits[exit][1]].showExit(exit)
        else:
            current_block = self.blocks[self.block_stack[-1]]
            self.view.setStyleSheet("background-color: " + current_block.color)
            for exit in self.exits.keys():
                if exit in current_block.exits.keys():
                    self.tiles[self.exits[exit][0]
                               ][self.exits[exit][1]].showExit(exit)
                else:
                    self.tiles[self.exits[exit][0]
                               ][self.exits[exit][1]].hideExit(exit)
        self.change_block.emit(self.block_stack)
