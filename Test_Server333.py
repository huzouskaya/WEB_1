import pygame
import sys
import socket
import threading
import queue

# Create a queue to store the received data
data_queue = queue.Queue()

class Checker:
    def __init__(self, color, x, y):
        self.color = color  # Цвет шашки ('red' или 'black')
        self.x = x  # Координата клетки по оси X
        self.y = y  # Координата клетки по оси Y
        self.tile_size = 80  # Размер клетки доски

    def draw(self, screen):
        # Рисуем шашку на экране
        color = (255, 0, 0) if self.color == 'red' else (255, 255, 255)
        pygame.draw.circle(screen, color, (self.x * self.tile_size + self.tile_size // 2,
                                             self.y * self.tile_size + self.tile_size // 2),
                           self.tile_size // 3)

    def can_move(self, target_x, target_y):
        # Логика движения шашки. Например, шашка может двигаться на одну клетку по диагонали
        if self.color != 'red':
            return (target_x == self.x + 1 and target_y == self.y + 1) or (target_x == self.x - 1 and target_y == self.y + 1)
        else:
            return (target_x == self.x + 1 and target_y == self.y - 1) or (target_x == self.x - 1 and target_y == self.y - 1)

class Game:
    def __init__(self):
        self.checkers = []
        for x in range(8):
            for y in range(3):  # Верхние 3 строки для красных шашек
                if (x + y) % 2 == 1:  # Расставляем только на черных клетках
                    self.checkers.append(Checker('red', x, y))

        for x in range(8):
            for y in range(5, 8):  # Нижние 3 строки для черных шашек
                if (x + y) % 2 == 1:
                    self.checkers.append(Checker('wight', x, y))

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('192.168.146.136', 12345))
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

        colors = [pygame.Color(255, 255, 255), pygame.Color(0, 0, 0)]

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            screen.fill((255, 255, 255))  # Очистка экрана

            for row in range(8):
                for col in range(8):
                    color = colors[(row + col) % 2]
                    pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            for checker in self.checkers:
                checker.draw(screen)

            pygame.display.flip()# Обновление экрана
            pygame.time.Clock().tick(60)  # Ограничение частоты кадров

if __name__ == "__main__":
    game = Game()
    server_thread = threading.Thread(target=game.start_server)
    server_thread.start()
    game.draw_chessboard()