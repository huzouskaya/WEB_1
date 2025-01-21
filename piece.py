from __future__ import annotations
import os
import pygame
import tkinter as tk
from concurrent.futures.thread import ThreadPoolExecutor

from constants import BLACK, PIECE_GREEN_BG, TILE_LENGTH
from utils import coordinate_builder
from client import Client

# Load and scale images
def load_image(path: str, colorkey: tuple[int, int, int]) -> pygame.Surface:
    image = pygame.image.load(path)
    image.set_colorkey(colorkey)
    return image

def scale_image(image: pygame.Surface) -> pygame.Surface:
    return pygame.transform.scale(image, (TILE_LENGTH, TILE_LENGTH))

# Load piece images
def load_piece_images():
    images = {}
    piece_types = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']
    colors = ['white', 'black']
    selected_suffix = 's'

    for piece in piece_types:
        for color in colors:
            img_path = os.path.join("assets", "images", f"{color}_pieces.png")
            selected_path = os.path.join("assets", "images", "selected_pieces.png")
            img_subsurface = (0, 0, 128, 128)  # Default subsurface

            if piece == 'king':
                img_subsurface = (0, 256, 128, 128)
            elif piece == 'queen':
                img_subsurface = (256, 256, 128, 128)
            elif piece == 'rook':
                img_subsurface = (384, 256, 128, 128)
            elif piece == 'bishop':
                img_subsurface = (128, 0, 128, 128) if color == 'white' else (256, 0, 128, 128)
            elif piece == 'knight':
                img_subsurface = (128, 128, 128, 128) if color == 'white' else (256, 128, 128, 128)
            elif piece == 'pawn':
                img_subsurface = (0, 384, 128, 128)

            images[f"{piece}_{color[0]}"] = scale_image(load_image(img_path, BLACK).subsurface(img_subsurface))
            images[f"{piece}_{color[0]}{selected_suffix}"] = scale_image(load_image(selected_path, BLACK).subsurface(img_subsurface))

    images["valid_move_dot"] = scale_image(load_image(os.path.join("assets", "images", "valid_move_dot.png"), (0, 0, 0)))
    return images

images = load_piece_images()

def create_piece(row: int, col: int, piece_name: str, color: str) -> Piece | None:
    piece_classes = {
        "queen": Queen,
        "knight": Knight,
        "rook": Rook,
        "bishop": Bishop
    }
    return piece_classes.get(piece_name.lower())(row, col, color, piece_name) if piece_name.lower() in piece_classes else None

def get_piece(root: tk.Tk, piece_input: tk.Entry, row: int, col: int, color: str) -> Piece | None:
    piece = piece_input.get().lower()
    piece_classes = {
        "queen": Queen,
        "knight": Knight,
        "rook": Rook,
        "bishop": Bishop
    }

    if piece in piece_classes:
        root.destroy()
        return piece_classes[piece](row, col, color, piece)

    return create_piece(row, col, piece, color)

class Piece:
    def __init__(self, row: int, col: int, color: str, piece_name: str) -> None:
        self.row = row
        self.col = col
        self.color = color
        self.piece_name = piece_name
        self.img_name = f"{piece_name}_{color[0]}"
        self.is_selected = False
        self.valid_moves = set()
        self.first_move = True

    def select(self, window: pygame.Surface = None) -> None:
        self.is_selected = True
        if window is not None:
            self.draw(window)

    def unselect(self, window: pygame.Surface = None) -> None:
        self.is_selected = False
        if window is not None:
            self.draw(window)

    def one_direction(self, board: list[list[Piece | None]], candidates: set, row_change: int, col_change: int, check: set) -> None:
        row, col = self.row, self.col

        while True:
            row += row_change
            col += col_change

            if row < 0 or row >= len(board) or col < 0 or col >= len(board[row]):
                return

            if board[row][col] is None:
                candidates.add((row, col))
            elif board[row][col].color != self.color:
                candidates.add((row, col))
                return
            else:
                return

    def update_valid_moves(self, board: list[list[Piece | None]]) -> bool:
        self.valid_moves, check = self.all_valid_moves(board)
        return check

    def move(self, row: int, col: int, board: list[list[Piece | None]], window: pygame.Surface = None, replacement: str = None) -> bool:
        if (row, col) not in self.valid_moves:
            return False

        self.first_move = False
        board[row][col] = board[self.row][self.col]
        board[self.row][self.col] = None
        self.row = row
        self.col = col
        self.is_selected = False

        if replacement:
            board[self.row][self.col] = create_piece(self.row, self.col, replacement, self.color)
            board[self.row][self.col].first_move = False

        if window is not None:
            board[self.row][self.col].draw(window)

        return True

    def draw(self, window: pygame.Surface) -> None:
        x, y = coordinate_builder(self.row, self.col)
        img = images.get(self.img_name + ("s" if self.is_selected else ""))
        img_rect = img.get_rect(topleft=(x, y))
        window.blit(img, img_rect)

        if self.is_selected:
            for row, col in self.valid_moves:
                dotx, doty = coordinate_builder(row, col)
                dot_rect = images["valid_move_dot"].get_rect(topleft=(dotx, doty))
                window.blit(images["valid_move_dot"], dot_rect)

class King(Piece):
    def __init__(self, row: int, col: int, color: str, piece_name: str) -> None:
        super().__init__(row, col, color, piece_name)
        self.rochade = set()

    def move(self, row: int, col: int, board: list[list[Piece | None]], window: pygame.Surface = None, replacement: str = None) -> bool:
        if (row, col) in self.rochade:
            if col < self.col:
                board[self.row][0].move(self.row, self.col - 1, board, window, replacement)
            elif col > self.col:
                board[self.row][7].move(self.row, self.col + 1, board, window, replacement)

        return super().move(row, col, board, window, replacement)

    def all_valid_moves(self, board: list[list[Piece | None]]) -> tuple[set, bool]:
        candidates = set()
        self.rochade = set()
        check = False

        for x in range(self.row - 1, self.row + 2):
            for y in range(self.col - 1, self.col + 2):
                if 0 <= x < len(board) and 0 <= y < len(board[x]) and (x, y) != (self.row, self.col):
                    if board[x][y] is None or board[x][y].color != self.color:
                        candidates.add((x, y))
                        if board[x][y] is not None and board[x][y].piece_name == "king":
                            check = True

        # Check for rochade
        if self.first_move:
            if board[self.row][0] is not None and board[self.row][0].first_move:
                if all(board[self.row][col] is None for col in range(1, 3)):
                    candidates.add((self.row, self.col - 2))
                    self.rochade.add((self.row, self.col - 2))
            if board[self.row][7] is not None and board[self.row][7].first_move:
                if all(board[self.row][col] is None for col in range(5, 7)):
                    candidates.add((self.row, self.col + 2))
                    self.rochade.add((self.row, self.col + 2))

        return candidates, check

class Queen(Piece):
    def all_valid_moves(self, board: list[list[Piece | None]]) -> tuple[set, bool]:
        candidates = set()
        check = set()

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        with ThreadPoolExecutor(max_workers=4) as executor:
            for direction in directions:
                executor.submit(self._check_direction, board, candidates, *direction, check)

        return candidates, True in check

    def _check_direction(self, board: list[list[Piece | None]], candidates: set, row_change: int, col_change: int, check: set) -> None:
        row, col = self.row, self.col
        while True:
            row += row_change
            col += col_change

            if row < 0 or row >= len(board) or col < 0 or col >= len(board[row]):
                return

            if board[row][col] is None:
                candidates.add((row, col))
            elif board[row][col].color != self.color:
                candidates.add((row, col))
                if board[row][col].piece_name == "king":
                    check.add(True)
                return
            else:
                return

class Rook(Piece):
    def all_valid_moves(self, board: list[list[Piece | None]]) -> tuple[set, bool]:
        candidates = set()
        check = set()

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        with ThreadPoolExecutor(max_workers=4) as executor:
            for direction in directions:
                executor.submit(self._check_direction, board, candidates, *direction, check)

        return candidates, True in check

class Bishop(Piece):
    def all_valid_moves(self, board: list[list[Piece | None]]) -> tuple[set, bool]:
        candidates = set()
        check = set()

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        with ThreadPoolExecutor(max_workers=4) as executor:
            for direction in directions:
                executor.submit(self._check_direction, board, candidates, *direction, check)

        return candidates, True in check

class Knight(Piece):
    def all_valid_moves(self, board: list[list[Piece | None]]) -> tuple[set, bool]:
        candidates = set()
        check = False

        knight_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]

        for dx, dy in knight_moves:
            x, y = self.row + dx, self.col + dy
            if 0 <= x < len(board) and 0 <= y < len(board[x]):
                if board[x][y] is None or board[x][y].color != self.color:
                    candidates.add((x, y))
                    if board[x][y] is not None and board[x][y].piece_name == "king":
                        check = True

        return candidates, check

class Pawn(Piece):
    def all_valid_moves(self, board: list[list[Piece | None]]) -> tuple[set, bool]:
        candidates = set()
        check = False
        direction = -1 if self.color == "w" else 1

        # Forward movement
        for i in range(1, 3):  # 1 or 2 squares forward
            if self.row + i * direction >= 0 and self.row + i * direction < len(board):
                if board[self.row + i * direction][self.col] is None:
                    candidates.add((self.row + i * direction, self.col))
                else:
                    break
            else:
                break

        # Diagonal captures
        for dy in [-1, 1]:
            if 0 <= self.row + direction < len(board) and 0 <= self.col + dy < len(board[self.row + direction]):
                if board[self.row + direction][self.col + dy] is not None and board[self.row + direction][self.col + dy].color != self.color:
                    candidates.add((self.row + direction, self.col + dy))
                    if board[self.row + direction][self.col + dy].piece_name == "king":
                        check = True

        return candidates, check
