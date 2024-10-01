import pygame
import sys
import socket
import threading

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 12345))
    server.listen(1)
    print("Сервер запущен. Ожидание подключения...")
    client, address = server.accept()
    print("Клиент подключился!")

def draw_chessboard():
    pygame.init()
    screen = pygame.display.set_mode((640, 640))
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
                pygame.draw.rect(screen, color, pygame.Rect(col * 80, row * 80, 80, 80))

        pygame.display.update()  # Обновление экрана
        pygame.time.Clock().tick(60)  # Ограничение частоты кадров

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    draw_chessboard()