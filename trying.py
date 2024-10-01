import socket
import time

import pygame
import sys
import threading


class Checker:
    def __init__(self, color, x, y):
        self.color = color
        self.x = x
        self.y = y
        self.tile_size = 80

    def draw(self, screen):
        color = (0, 0, 0) if self.color == 'black' else (255, 255, 255)
        pygame.draw.circle(screen, color, (self.x * self.tile_size + self.tile_size // 2,
                                             self.y * self.tile_size + self.tile_size // 2), self.tile_size // 3)

    def can_move(self, target_x, target_y):
        if self.color == 'black':
            return (target_x == self.x + 1 and target_y == self.y + 1) or (target_x == self.x - 1 and target_y == self.y + 1)
        else:
            return (target_x == self.x + 1 and target_y == self.y - 1) or (target_x == self.x - 1 and target_y == self.y - 1)


class Game:
    def __init__(self):
        self.checkers = []
        self.current_turn = 'white'
        for x in range(8):
            for y in range(3):
                if (x + y) % 2 == 1:
                    self.checkers.append(Checker('black', x, y))

        for x in range(8):
            for y in range(5, 8):
                if (x + y) % 2 == 1:
                    self.checkers.append(Checker('white', x, y))

    def get_opponent_color(self):
        if self.current_turn == 'white':
            return 'black'
        else:
            return 'white'

    def can_beat_opponent_checker(self, checker, target_x, target_y):
        if not checker.can_move(target_x, target_y):
            return False

        for opponent_checker in self.checkers:
            if opponent_checker.color == self.get_opponent_color() and opponent_checker.x == target_x and opponent_checker.y == target_y:
                return True

        return False

    def beat_opponent_checker(self, checker, target_x, target_y):
        for opponent_checker in self.checkers:
            if opponent_checker.color == self.get_opponent_color() and opponent_checker.x == target_x and opponent_checker.y == target_y:
                self.checkers.remove(opponent_checker)
                break

    def make_move(self, checker, target_x, target_y):
        if self.can_beat_opponent_checker(checker, target_x, target_y):
            self.beat_opponent_checker(checker, target_x, target_y)
        checker.x = target_x
        checker.y = target_y
        if self.current_turn == 'white':
            self.current_turn = 'black'
        else:
            self.current_turn = 'white'


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 12345))
    server.listen(1)
    print("Сервер запущен. Ожидание подключения...")

    client, address = server.accept()
    print("Успешное подключение клиента!")

    while True:
        data = client.recv(1024).decode('utf-8')
        if not data:
            break
        print(f"Получен ход: {data}")
        color, x1, y1, x2, y2 = data.split()
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        # Обновление доски
        print(f"Обновление доски: {color} {x1} {y1} {x2} {y2}")

    client.close()


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect(('127.0.0.1', 12345))
        print("Успешное подключение к серверу!")
        pygame.init()
        screen = pygame.display.set_mode((640, 640))
        pygame.display.set_caption("Шашки")
        game = Game()
        selected_checker = None

        def draw_chessboard():
            colors = [pygame.Color(255, 222, 153), pygame.Color(139, 69, 19)]
            for row in range(8):
                for col in range(8):
                    color = colors[(row + col) % 2]
                    pygame.draw.rect(screen, color, pygame.Rect(col * 80, row * 80, 80, 80))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    client.close()
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    clicked_x = mouse_x // 80
                    clicked_y = mouse_y // 80

                    for checker in game.checkers:
                        if checker.x == clicked_x and checker.y == clicked_y and checker.color == game.current_turn:
                            selected_checker = checker
                            break

                    if selected_checker:
                        target_x = clicked_x
                        target_y = clicked_y

                        if game.can_beat_opponent_checker(selected_checker, target_x, target_y):
                            game.beat_opponent_checker(selected_checker, target_x, target_y)
                            selected_checker.x = target_x
                            selected_checker.y = target_y

                        if selected_checker.can_move(target_x, target_y):
                            client.sendall(f'{selected_checker.color} {selected_checker.x} {selected_checker.y} {target_x} {target_y}'.encode('utf-8'))
                            selected_checker.x = target_x
                            selected_checker.y = target_y

                            game.make_move(selected_checker, target_x, target_y)
                            selected_checker = None

            draw_chessboard()

            for checker in game.checkers:
                checker.draw(screen)
            pygame.display.flip()

    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return


if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    time.sleep(1)

    client_thread = threading.Thread(target=start_client)
    client_thread.start()