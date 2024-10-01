import socket
import pygame
import sys

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
        if self.color == 'red':
            return (target_x == self.x + 1 and target_y == self.y + 1) or (target_x == self.x - 1 and target_y == self.y + 1)
        else:  # черная шашка
            return (target_x == self.x + 1 and target_y == self.y - 1) or (target_x == self.x - 1 and target_y == self.y - 1)

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect(('192.168.146.136', 12345))
        print("Успешное подключение к серверу!")

        pygame.init()
        screen = pygame.display.set_mode((640, 640))
        pygame.display.set_caption("Шашки")

        # Создаем шашки и расставляем их по позиции
        checkers = []
        for x in range(8):
            for y in range(3):  # Верхние 3 строки для красных шашек
                if (x + y) % 2 == 1:  # Расставляем только на черных клетках
                    checkers.append(Checker('red', x, y))

        for x in range(8):
            for y in range(5, 8):  # Нижние 3 строки для черных шашек
                if (x + y) % 2 == 1:
                    checkers.append(Checker('white', x, y))

        selected_checker = None  # Для хранения выбранной шашки

        def draw_chessboard():
            colors = [pygame.Color(255, 255, 255), pygame.Color(0, 0, 0)]
            for row in range(8):
                for col in range(8):
                    color = colors[(row + col) % 2]
                    pygame.draw.rect(screen, color, pygame.Rect(col * 80, row * 80, 80, 80))

        # Основной игровой цикл
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

                    # Проверяем, выбрали ли шашку
                    for checker in checkers:
                        if checker.x == clicked_x and checker.y == clicked_y:
                            selected_checker = checker
                            break

                    if selected_checker:
                        # Пытаемся переместить шашку
                        target_x = clicked_x
                        target_y = clicked_y

                        if selected_checker.can_move(target_x, target_y):
                            selected_checker.x = target_x
                            selected_checker.y = target_y
                            # Отправляем координаты на сервер
                            client.sendall(f'Move {selected_checker.color} {target_x} {target_y}'.encode('utf-8'))

                            # Сбрасываем выделение после хода
                            selected_checker = None

            # Отрисовка доски и шашек
            draw_chessboard()
            for checker in checkers:
                checker.draw(screen)
            pygame.display.flip()

    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return

if __name__ == "__main__":
    start_client()
