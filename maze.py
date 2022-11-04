from tiles import Tile
from block import Block
from player import Player
from PySide6.QtWidgets import (
    QHBoxLayout, QWidget, QGraphicsView, QGraphicsScene)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal, Slot


class Maze(QWidget):

    change_block = Signal(list)
    game_over = Signal(bool)

    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
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
                bits = line.split(" ")
                teleport_spec = bits[3].split("+")
                self.tiles[int(bits[1])][int(bits[2])].setTeleporter(
                    True, teleport_spec[0], teleport_spec[1], self.scene)
                continue

            if line[:5] == "BLOCK":
                bits = line.split(" ")
                self.blocks[bits[1]] = Block(
                    int(bits[3]), int(bits[2]), bits[1], self.scene)
                continue

            if line[:4] == "LINK":
                bits = line.split(" ")
                exit_tile = self.tiles[self.exits[bits[2]]
                                       [0]][self.exits[bits[2]][1]]
                self.tiles[int(bits[-2])][int(bits[-1])].setLink(
                    True, bits[1], exit_tile, self.scene)
                self.blocks[bits[1]].add_exit(
                    bits[2], int(bits[-2]), int(bits[-1]))
                continue

            if line[:4] == "EXIT":
                bits = line.split(" ")
                self.tiles[int(bits[-2])][int(bits[-1])
                                          ].setExit(True, bits[1], bits[2], self.scene)
                self.exits[bits[1]] = (int(bits[-2]), int(bits[-1]))
                continue

            if line[:6] == "PLAYER":
                player_init = line.split(" ")
                self.player = Player(
                    int(player_init[2]), int(player_init[1]), self.scene)
                continue

            self.tiles += [[Tile(i, j, line[2*j:2*j+2], self.scene)
                            for j in range(len(line) >> 1)]]
            i += 1

    @ Slot()
    def reset(self):
        if not self.win:
            self.player.reset()
            self.block_stack = ["0"]
            self.block_changed()

    def update_player(self, key):
        if not self.win:
            teleport = None
            tile = self.tiles[self.player.y][self.player.x]
            north = tile.type & 8 == 8
            east = tile.type & 4 == 4
            south = tile.type & 2 == 2
            west = tile.type & 1 == 1
            if key == Qt.Key_Z and north:
                self.player.y -= 1
            elif key == Qt.Key_Q and west:
                self.player.x -= 1
            elif key == Qt.Key_S and south:
                self.player.y += 1
            elif key == Qt.Key_D and east:
                self.player.x += 1

            if tile.is_teleport:
                north = tile.teleport_direction == 4
                east = tile.teleport_direction == 1
                south = tile.teleport_direction == 2
                west = tile.teleport_direction == 3
                if key == Qt.Key_Z and north:
                    self.player.y -= tile.teleport_reach
                elif key == Qt.Key_Q and west:
                    self.player.x -= tile.teleport_reach
                elif key == Qt.Key_S and south:
                    self.player.y += tile.teleport_reach
                elif key == Qt.Key_D and east:
                    self.player.x += tile.teleport_reach

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
                    self.player.x = exit_tile.y
                    self.player.y = exit_tile.x
                    self.block_stack += [tile.block_name]
                    self.block_changed()
                    teleport = link_orientation

            if tile.is_exit:
                north = tile.exit_orientation == 4
                east = tile.exit_orientation == 1
                south = tile.exit_orientation == 2
                west = tile.exit_orientation == 3
                if (key == Qt.Key_Z and north) or (key == Qt.Key_Q and west) or (key == Qt.Key_S and south) or (key == Qt.Key_D and east):
                    if self.block_stack[-1] != '0':
                        current_block = self.blocks[self.block_stack[-1]]

                        if tile.exit_name in current_block.exits.keys():
                            self.player.x = current_block.exits[tile.exit_name][1]
                            self.player.y = current_block.exits[tile.exit_name][0]
                            self.block_stack.pop()
                            self.block_changed()
                            teleport = tile.exit_orientation
                    else:
                        self.win = True
                        self.scene.clear()
                        self.scene.addPixmap(QPixmap("./images/game_over.jpg"))
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
