import pygame
import sys
import socket
import threading
import queue

data_queue = queue.Queue()

class Checker:
    def __init__(self, color, x, y):
        self.color = color
        self.x = x
        self.y = y
        self.tile_size = 80

    def draw(self, screen):
        color = (0, 0, 0) if self.color == 'black' else (255, 255, 255)
        pygame.draw.circle(screen, color, (self.x * self.tile_size + self.tile_size // 2,
                                             self.y * self.tile_size + self.tile_size // 2),
                           self.tile_size // 3)

    def can_move(self, target_x, target_y):
        if self.color != 'black':
            return (target_x == self.x + 1 and target_y == self.y + 1) or (target_x == self.x - 1 and target_y == self.y + 1)
        else:
            return (target_x == self.x + 1 and target_y == self.y - 1) or (target_x == self.x - 1 and target_y == self.y - 1)

class Game:
    def __init__(self):
        self.checkers = []
        for x in range(8):
            for y in range(3):
                if (x + y) % 2 == 1:
                    self.checkers.append(Checker('black', x, y))

        for x in range(8):
            for y in range(5, 8):
                if (x + y) % 2 == 1:
                    self.checkers.append(Checker('white', x, y))

    def start_server(self):
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

            for checker in self.checkers:
                if checker.color == color and checker.x == x1 and checker.y == y1:
                    checker.x = x2
                    checker.y = y2
                    break

        client.close()

    def draw_chessboard(self):
        pygame.init()
        WIDTH, HEIGHT = 640, 640
        SQUARE_SIZE = 80
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Шашки")

        colors = [pygame.Color(255, 222, 153), pygame.Color(139, 69, 19)]

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill((255, 255, 255))

            for row in range(8):
                for col in range(8):
                    color = colors[(row + col) % 2]
                    pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            for checker in self.checkers:
                checker.draw(screen)

            pygame.display.flip()
            pygame.time.Clock().tick(60)


if __name__ == "__main__":
    game = Game()
    server_thread = threading.Thread(target=game.start_server)
    server_thread.start()
    game.draw_chessboard()