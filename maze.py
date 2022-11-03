from tiles import Tile
from block import Block
from player import Player
from exit import Exit
from PySide6.QtWidgets import (
    QGridLayout, QWidget, QGraphicsView, QGraphicsScene)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal, Slot


class Maze(QWidget):

    change_block = Signal(str, bool)

    def __init__(self):
        QWidget.__init__(self)

        self.layout = QGridLayout(self)
        self.layout.setSpacing(0)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.layout.addWidget(self.view, 0, 0)

        self.tiles = []
        self.blocks = {}
        self.exits = {}
        self.block_stack = [""]

        i = 0
        f = open(r"labyrinth", "r")
        lines = f.readlines()

        for line in lines:
            line = line.replace("\n", "").strip()

            if line == "" or line[0] == "#":
                continue

            if line[:8] == "TELEPORT":
                bits = line.split(" ")
                tile = self.tiles[int(bits[1])][int(bits[2])]
                teleport_spec = bits[3].split("+")
                tile.setTeleporter(True, teleport_spec[0], teleport_spec[1])
                self.scene.addPixmap(QPixmap(
                    "./images/teleporters/teleport_" + teleport_spec[0] + ".png")).setOffset(int(bits[2])*20-5, int(bits[1])*20-5)
                continue

            if line[:5] == "BLOCK":
                bits = line.split(" ")
                self.blocks[bits[1]] = Block(bits[3], bits[2], bits[1])
                self.scene.addPixmap(
                    self.blocks[bits[1]].pixmap).setOffset(int(bits[3])*20, int(bits[2])*20)
                continue

            if line[:4] == "LINK":
                bits = line.split(" ")
                tile = self.tiles[int(bits[-2])][int(bits[-1])]
                link_spec = bits[1:3]
                tile.setLink(True, link_spec[0], link_spec[1])
                self.blocks[link_spec[0]].add_exit(
                    link_spec[1], int(bits[-2]), int(bits[-1]))
                if self.exits[link_spec[1]].orientation == 1:
                    orientation = 3
                elif self.exits[link_spec[1]].orientation == 2:
                    orientation = 4
                elif self.exits[link_spec[1]].orientation == 3:
                    orientation = 1
                elif self.exits[link_spec[1]].orientation == 4:
                    orientation = 2
                else:
                    orientation = -1
                self.scene.addPixmap(QPixmap(
                    "./images/links/link_"+str(orientation)+".png")).setOffset(int(bits[-1])*20-5, int(bits[-2])*20-5)
                continue

            if line[:4] == "EXIT":
                bits = line.split(" ")
                tile = self.tiles[int(bits[-2])][int(bits[-1])]
                exit_spec = bits[1:3]
                self.exits[exit_spec[0]] = Exit(exit_spec[0], exit_spec[1], int(
                    bits[-2]), int(bits[-1]))
                tile.setExit(True, exit_spec[0])
                self.scene.addPixmap(QPixmap(
                    "./images/exits/exit_" + str(self.exits[exit_spec[0]].orientation) + ".png")).setOffset(int(bits[-1])*20-5, int(bits[-2])*20-5)
                continue

            row = []
            for j in range(len(line) >> 1):
                tile = Tile(i, j, line[2*j:2*j+2])
                self.scene.addPixmap(tile.pixmap).setOffset(j*20, i*20)
                row += [tile]
            i += 1
            self.tiles += [row]
        self.player = Player(2, 3)
        self.player_map = self.scene.addPixmap(self.player.pixmap)
        self.move_player()

    @Slot()
    def reset(self):
        self.player.x = 2
        self.player.y = 3
        self.block_stack = [""]
        self.move_player()

    def move_player(self):
        self.player_map.setOffset(
            self.player.x*20, self.player.y*20)

    def update_player(self, key):
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
            north = self.exits[tile.link_name].orientation == 2
            east = self.exits[tile.link_name].orientation == 3
            south = self.exits[tile.link_name].orientation == 4
            west = self.exits[tile.link_name].orientation == 1
            if (key == Qt.Key_Z and north) or (key == Qt.Key_Q and west) or (key == Qt.Key_S and south) or (key == Qt.Key_D and east):
                self.player.x = self.exits[tile.link_name].y
                self.player.y = self.exits[tile.link_name].x
                self.block_changed(new_block=tile.block_name)

        if tile.is_exit:
            north = self.exits[tile.exit_name].orientation == 4
            east = self.exits[tile.exit_name].orientation == 1
            south = self.exits[tile.exit_name].orientation == 2
            west = self.exits[tile.exit_name].orientation == 3
            if (key == Qt.Key_Z and north) or (key == Qt.Key_Q and west) or (key == Qt.Key_S and south) or (key == Qt.Key_D and east):
                current_block = self.blocks[self.block_stack[-1]]

                self.player.x = current_block.exits[tile.exit_name][1]
                self.player.y = current_block.exits[tile.exit_name][0]
                self.block_changed(inward=False)

        self.move_player()

    def block_changed(self, new_block="", inward=True):
        if inward:
            self.block_stack += [new_block]
        else:
            self.block_stack.pop()
        self.change_block.emit(self.block_stack[-1], inward)
