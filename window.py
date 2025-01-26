import os
import time
import pygame
import tkinter as tk

from client import Client
from piece import get_piece
from constants import BOARD_LENGTH, SCREEN_WIDTH, SCREEN_HEIGHT, SERVER_ADDR, FONT, TILE_LENGTH, WHITE, CAPTION, BLACK, RED


def draw_start_menu(window: pygame.Surface, name: str, connection_lost: bool=False, connection_refused: bool=False) -> None:
    window.fill(BLACK)  # TODO: load bg image

    font = pygame.font.SysFont(FONT, SCREEN_HEIGHT//10)
    text1 = font.render("Press space key", True, WHITE)
    text2 = font.render("to enter a game", True, WHITE)
    text3 = font.render(name, True, WHITE)

    if connection_refused:
        conn_text = font.render("(connection refused)", True, RED)
        conn_text_rect = conn_text.get_rect()
        conn_text_rect.centerx = SCREEN_WIDTH/2
        window.blit(conn_text, conn_text_rect)
    
    if connection_lost:
        conn_text = font.render("(connection lost)", True, RED)
        conn_text_rect = conn_text.get_rect()
        conn_text_rect.centerx = SCREEN_WIDTH/2
        window.blit(conn_text, conn_text_rect)

    text1_rect = text1.get_rect()
    text1_rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - SCREEN_HEIGHT//10)
    text2_rect = text2.get_rect()
    text2_rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
    text3_rect = text3.get_rect()
    text3_rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + SCREEN_HEIGHT//10)

    window.blit(text1, text1_rect)
    window.blit(text2, text2_rect)
    window.blit(text3, text3_rect)

    pygame.display.update()

def draw_waiting(window: pygame.Surface) -> None:
    window.fill(BLACK)

    font = pygame.font.SysFont(FONT, SCREEN_HEIGHT//10)
    text = font.render("Waiting for enemy...", True, WHITE)
    text_rect = text.get_rect()
    text_rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
    
    window.blit(text, text_rect)
    pygame.display.update()

def menu_screen(window: pygame.Surface, name: str, connection_lost: bool=False) -> None:
    draw_start_menu(window, name, connection_lost)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    draw_waiting(window)
                    try:
                        client = Client(name, SERVER_ADDR)
                        chess_game(window, client)
                    except ConnectionRefusedError:
                        draw_start_menu(window, name, connection_refused=True)

def chess_game(window: pygame.Surface, client: Client) -> None:
    window.fill(BLACK)

    board = client.board

    board.draw(window, client.name)
    pygame.display.update()

    while True:
        if board.winner is not None:
            time.sleep(5)
            menu_screen(window, client.name)

        if client.name != board.turn:
            try:
                command = client.receive(4096)  # wait for their move
                command["window"] = window
                command["my_name"] = client.name
                board.command(command, window)
            except ConnectionResetError:  # connection closed
                menu_screen(window, client.name, connection_lost=True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client.disconnect()
                pygame.quit()
                exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                row = int((y - (SCREEN_HEIGHT - BOARD_LENGTH)/2)//TILE_LENGTH)
                col = int((x - (SCREEN_WIDTH - BOARD_LENGTH)/2)//TILE_LENGTH)
                
                if not 0 <= row <= 7 or not 0 <= col <= 7:
                    continue

                selected = board.selected

                if board.click(client.name, row, col, window):
                    replacement = None

                    if board.board[row][col].piece_name == "pawn" and (row == 0 and board.board[row][col].color == "w" or row == 7 and board.board[row][col].color == "b"):
                        new_piece = []

                        root = tk.Tk()
                        tk.Label(root, text="Enter the piece you want to replace your pawn with").grid(row=0)
                        piece_input = tk.Entry(root)
                        piece_input.grid(row=1)
                        tk.Button(root, text="Enter", command=lambda: new_piece.append(get_piece(root, piece_input, row, col, board.board[row][col].color))).grid(row=2, pady=4)

                        root.mainloop()

                        board.board[row][col] = new_piece[-1]
                        board.update_valid_moves()
                        board.board[row][col].draw(window)
                        
                        replacement = new_piece[-1].piece_name

                    client.send({
                        "command": "move",
                        "p_name": client.name,
                        "pos_before": selected,
                        "pos_after": (row, col),
                        "replacement": replacement,
                    })  # send your move

        pygame.display.update()


def get_name_input(window: pygame.Surface) -> str:
    font = pygame.font.SysFont(FONT, SCREEN_HEIGHT // 10)
    input_box = pygame.Rect(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 10)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if input_box.collidepoint(event.pos):
                    # Toggle the active variable.
                    active = not active
                else:
                    active = False
                # Change the current color of the input box.
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        window.fill(BLACK)
        # Render the current text.
        txt_surface = font.render(text, True, WHITE)
        # Resize the box if the text is too long.
        width = max(SCREEN_WIDTH // 2, txt_surface.get_width() + 10)
        input_box.w = width
        # Blit the text.
        window.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        # Blit the input_box rect.
        pygame.draw.rect(window, color, input_box, 2)

        prompt_surface = font.render("Enter your name:", True, WHITE)
        prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - SCREEN_HEIGHT // 10))
        window.blit(prompt_surface, prompt_rect)

        pygame.display.flip()

    return text

def main() -> None:
    pygame.init()

    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(CAPTION)
    pygame.display.set_icon(pygame.image.load(os.path.join("assets", "images", "window_icon.png")))

    name = get_name_input(window)  # Получаем имя пользователя через графический интерфейс

    menu_screen(window, name)

if __name__ == "__main__": main()