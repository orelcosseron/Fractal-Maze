from PySide6.QtWidgets import QHBoxLayout, QGraphicsScene, QGraphicsView
from PySide6.QtGui import QTransform, QPixmap
from PySide6.QtCore import Signal, Property, QPointF, Slot, Qt, QAbstractAnimation, QPropertyAnimation, QSequentialAnimationGroup, QRect, QEasingCurve, QParallelAnimationGroup, QFileInfo, QFile, QIODevice, QTextStream

from directions import Direction
from tiles import Tile
from block import Block
from player import Player
from trophy import Trophy


class Maze(QGraphicsView):

    change_block = Signal(list)
    game_over = Signal(bool)

    def __init__(self, maze_name):
        QGraphicsView.__init__(self)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameStyle(0)

        self.scene = QGraphicsScene()
        self.setLabyrinth(maze_name)

    @ Slot()
    def setLabyrinth(self, maze_name):
        self.scene.clear()
        self.scene = QGraphicsScene()
        self.setTransform(QTransform())
        self.tiles = []
        self.blocks = {}
        self.exits = {}
        self.trophies = []
        self.winning_positions = []
        self.block_stack = ["0"]
        self.win = False

        self.m_animation_zoom = {}
        self.m_animation_pan = {}
        self.zoom_animation = {}
        self.block_change_animation = QSequentialAnimationGroup()
        self.block_change_animation.finished.connect(self.animation_handler)
        self.block_buffer = []

        maze_name = "_".join([word.lower()
                              for word in maze_name.split(" ")])
        f = QFile(QFileInfo(__file__).absolutePath() +
                  "/mazes/" + maze_name + ".maze")
        f.open(QIODevice.ReadOnly)
        lines = QTextStream(f)
        i = 0
        while not lines.atEnd():
            line = lines.readLine()
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
                block_path = block_name.split("+")
                exit_tile = self.tiles[self.exits[exit_name]
                                       [0]][self.exits[exit_name][1]]
                self.tiles[int(link_row)][int(link_col)].setLink(
                    block_path[-1], exit_tile, exit_name)
                self.blocks[block_path[-1]].add_exit(
                    exit_name, int(link_row), int(link_col), block_path)
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
                    int(player_row), int(player_col), self.tile_size, player_color, self.path_color, self.scene)
                self.tiles[int(player_row)][int(player_col)].setStartingPoint()
                continue

            if line[:6] == "TROPHY":
                _, trophy_row, trophy_col, trophy_color = line.split(" ")
                self.trophies += [Trophy(int(trophy_row),
                                         int(trophy_col), trophy_color, self.path_color, self.tile_size, self.scene)]
                self.winning_positions += [
                    QPointF(int(trophy_col), int(trophy_row))]
                self.tiles[int(trophy_row)][int(trophy_col)].setStartingPoint()
                continue

            self.tiles += [[Tile(i, j, int(line[2*j:2*j+2]), self.tile_size, self.background_color, self.path_color, self.line_color, self.scene)
                            for j in range(len(line) >> 1)]]
            for tile in self.tiles[-1]:
                self.change_block.connect(tile.refresh)
            i += 1

        self.player.hide()
        for trophy in self.trophies:
            trophy.hide()
        for _ in range(5):
            for block in self.blocks.values():
                for exit in self.exits:
                    if exit in block.exits:
                        self.tiles[self.exits[exit][0]
                                   ][self.exits[exit][1]].showExit(exit)
                    else:
                        self.tiles[self.exits[exit][0]
                                   ][self.exits[exit][1]].hideExit(exit)
                block.pre_render()
            for block in self.blocks.values():
                block.render()
        for exit in self.exits:
            if len(self.trophies) == 0:
                self.tiles[self.exits[exit][0]
                           ][self.exits[exit][1]].showExit(exit)
            else:
                self.tiles[self.exits[exit][0]
                           ][self.exits[exit][1]].hideExit(exit)

        for trophy in self.trophies:
            trophy.show()
        self.player.show()
        f.close()

        self.setScene(self.scene)
        self.setFixedSize(self.scene.sceneRect().size().toSize())

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
        self.player.reset()
        for row in self.tiles:
            for tile in row:
                tile.reset()
        for block in self.blocks.values():
            block.reset()
        self.remove_block(len(self.block_stack) - 1)

    def update_player(self, direction):
        teleport = None
        tile = self.tiles[int(self.player.coordinates.y())
                          ][int(self.player.coordinates.x())]

        if direction in tile.reach:
            if direction == Direction.NORTH:
                self.player.coordinates += QPointF(
                    0, -tile.reach[direction])
            elif direction == Direction.EAST:
                self.player.coordinates += QPointF(
                    tile.reach[direction], 0)
            elif direction == Direction.SOUTH:
                self.player.coordinates += QPointF(
                    0, tile.reach[direction])
            elif direction == Direction.WEST:
                self.player.coordinates += QPointF(
                    -tile.reach[direction], 0)
            tile.drawPath(direction, False)
            self.tiles[int(self.player.coordinates.y())][int(self.player.coordinates.x())].drawPath(
                direction.opposite(), True)

        if direction in tile.linked_block:
            block_name, exit_name = tile.linked_block[direction]
            exit_tile = self.tiles[self.exits[exit_name]
                                   [0]][self.exits[exit_name][1]]
            self.player.coordinates = QPointF(exit_tile.coordinates)
            tile.drawPath(direction, False)
            self.add_blocks(self.blocks[block_name].block_path[exit_name])
            self.tiles[int(self.player.coordinates.y())][int(self.player.coordinates.x())].drawPath(
                direction.opposite(), inward=True, stack=self.block_stack + self.blocks[block_name].block_path[exit_name])
            teleport = direction

        if direction in tile.exit_name:
            if self.block_stack[-1] != '0':
                exit_name = tile.exit_name[direction]
                current_block = self.blocks[self.block_stack[-1]]

                if exit_name in current_block.exits.keys() and current_block.block_path[exit_name] == self.block_stack[-len(current_block.block_path[exit_name]):]:
                    self.player.coordinates = QPointF(
                        current_block.exits[exit_name])
                    tile.drawPath(direction, False)
                    self.remove_block(
                        len(current_block.block_path[exit_name]))

                    self.tiles[int(self.player.coordinates.y())][int(self.player.coordinates.x())].drawPath(
                        direction.opposite(), inward=True, stack=self.block_stack[:-len(current_block.block_path[exit_name])])
                    teleport = direction
            else:
                if len(self.trophies) == 0:
                    self._game_over()
                    return

        self.player.move(teleport=teleport)
        if self.block_stack[-1] == '0' and self.player.coordinates in self.winning_positions:
            self._game_over()

    def _game_over(self):
        self.win = True
        self.setStyleSheet("background-color: black")
        for trophy in self.trophies:
            trophy.m_rotation.stop()
        self.scene.clear()
        self.scene.addPixmap(
            QPixmap(QFileInfo(__file__).absolutePath() + "/images/game_over.jpg"))
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.fitInView(
            self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.game_over.emit(False)

    @ Slot()
    def animation_handler(self, init=False):
        if not init:
            block, direction = self.block_buffer.pop(0)
            self.zoom_animation[block] = self.block_change_animation.takeAnimation(
                0)
            if direction == QAbstractAnimation.Direction().Backward:
                self.block_stack.pop()
                self.change_block.emit(self.block_stack)
            else:
                self.block_stack += [block]

            for block in self.blocks.values():
                block.render(hash("-".join(self.block_stack)))

            if self.block_stack[-1] == '0':
                self.setStyleSheet(
                    "background-color: " + self.outside_color)
                for exit in self.exits:
                    if len(self.trophies) == 0:
                        self.tiles[self.exits[exit][0]
                                   ][self.exits[exit][1]].showExit(exit)
                    else:
                        self.tiles[self.exits[exit][0]
                                   ][self.exits[exit][1]].hideExit(exit)
                for trophy in self.trophies:
                    trophy.show()
            else:
                for trophy in self.trophies:
                    trophy.hide()
                current_block = self.blocks[self.block_stack[-1]]
                self.setStyleSheet("background-color: " + current_block.color)
                for exit in self.exits:
                    if exit in current_block.exits and current_block.block_path[exit] == self.block_stack[-len(current_block.block_path[exit]):]:
                        self.tiles[self.exits[exit][0]
                                   ][self.exits[exit][1]].showExit(exit)
                    else:
                        self.tiles[self.exits[exit][0]
                                   ][self.exits[exit][1]].hideExit(exit)

        if len(self.block_buffer) == 0:
            return

        block, direction = self.block_buffer[0]
        self.block_change_animation.addAnimation(self.zoom_animation[block])
        if direction == QAbstractAnimation.Direction().Backward:
            self.player.hide()
            self.blocks[block].pre_render(
                hash("-".join(self.block_stack[:-1])))
            self.player.show()

        if direction == QAbstractAnimation.Direction().Forward:
            self.change_block.emit(self.block_stack + [block])

        self.block_change_animation.setDirection(direction)
        self.block_change_animation.start()

    def add_block_to_zoom_animation(self, block, direction):
        self.block_buffer += [(block, direction)]
        if len(self.block_buffer) == 1:
            self.animation_handler(init=True)

    def add_blocks(self, blocks):
        for block in blocks:
            self.add_block_to_zoom_animation(
                block, QAbstractAnimation.Direction().Forward)

    def remove_block(self, length):
        if length == 0:
            return
        for block in self.block_stack[-length:][::-1]:
            self.add_block_to_zoom_animation(
                block, QAbstractAnimation.Direction().Backward)

    def keyPressEvent(self, event):
        if self.win or self.block_change_animation.state() == QAbstractAnimation.State().Running:
            return
        if event.key() in [Qt.Key_Z, Qt.Key_W, Qt.Key_I, Qt.Key_Up]:
            self.update_player(Direction.NORTH)
        elif event.key() in [Qt.Key_Q, Qt.Key_A, Qt.Key_J, Qt.Key_Left]:
            self.update_player(Direction.WEST)
        elif event.key() in [Qt.Key_S, Qt.Key_K, Qt.Key_Down]:
            self.update_player(Direction.SOUTH)
        elif event.key() in [Qt.Key_D, Qt.Key_L, Qt.Key_Right]:
            self.update_player(Direction.EAST)
