import pygame
import random

pygame.font.init()
# ---------------------- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ---------------------- #
s_width = 800
s_height = 700
play_width = 300
play_height = 600
block_size = 30
top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 50

# ---------------------- ОПРЕДЕЛЕНИЕ ФОРМ ТЕТРИС ---------------------- #

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

# Список всех фигур и соответствующие цвета (цвет задаётся в формате RGB)
shapes = [S, Z, I, O, J, L, T]
shape_colors = [
    (0, 255, 0),  # Зеленый (S)
    (255, 0, 0),  # Красный (Z)
    (0, 255, 255),  # Голубой (I)
    (255, 255, 0),  # Желтый (O)
    (255, 165, 0),  # Оранжевый (J)
    (0, 0, 255),  # Синий (L)
    (128, 0, 128)  # Фиолетовый (T)
]


# ---------------------- КЛАСС ФИГУРЫ ---------------------- #
class Piece:
    """
    Класс, описывающий фигуру (тетримино).
    Атрибуты:
      - x, y: позиция фигуры на сетке (в клетках, а не пикселях);
      - shape: список строковых представлений формы фигуры с разными вращениями;
      - color: цвет фигуры;
      - rotation: текущая ориентация (индекс списка shape).
    """

    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


# ---------------------- ФУНКЦИИ ДЛЯ ИГРОВОГО ПОЛЯ ---------------------- #
def create_grid(locked_positions={}):
    """
    Создает игровое поле (двумерный список 20x10) с учётом уже закреплённых фигур.
    Каждая клетка представлена кортежем цвета (RGB). Пустые клетки окрашиваются в чёрный.
    """
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

    # Заполняем клетки, в которых уже закреплены фигуры (locked_positions)
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                grid[i][j] = locked_positions[(j, i)]
    return grid


def convert_shape_format(piece):
    """
    Преобразует строковое представление фигуры в список позиций на сетке,
    где расположены заполненные клетки.
    """
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                # Отнимаем сдвиги, чтобы форма корректно располагалась относительно центра
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions


def valid_space(piece, grid):
    """
    Проверяет, находится ли фигура в допустимом положении (не выходит за границы поля
    и не пересекается с уже закреплёнными фигурами).
    """
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_positions = [pos for sub in accepted_positions for pos in sub]

    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:  # Если позиция находится над игровым полем, допускаем её
                return False
    return True


def check_lost(locked_positions):
    """
    Проверяет, достигли ли закреплённые фигуры верхней части игрового поля.
    Если да, то игра заканчивается.
    """
    for pos in locked_positions:
        x, y = pos
        if y < 1:
            return True
    return False


def get_shape():
    """
    Выбирает случайную фигуру из списка и возвращает объект Piece.
    """
    return Piece(5, 0, random.choice(shapes))


# ---------------------- ФУНКЦИИ ОТОБРАЖЕНИЯ ---------------------- #
def draw_text_middle(surface, text, size, color):
    """
    Рисует текст в центре переданной поверхности.
    """
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, True, color)

    surface.blit(label, (
        top_left_x + play_width / 2 - label.get_width() / 2,
        top_left_y + play_height / 2 - label.get_height() / 2
    ))


def draw_grid(surface, grid):
    """
    Отрисовывает линии сетки на игровой области.
    """
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        # Горизонтальные линии
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + i * block_size), (sx + play_width, sy + i * block_size))
        for j in range(len(grid[i])):
            # Вертикальные линии
            pygame.draw.line(surface, (128, 128, 128), (sx + j * block_size, sy),
                             (sx + j * block_size, sy + play_height))


def clear_rows(grid, locked):
    """
    Проверяет заполненные ряды, удаляет их и сдвигает все ряды выше вниз.
    За каждый очищенный ряд начисляется определённое количество очков.
    """
    inc = 0  # счетчик очищенных рядов

    # Идём с нижней строки вверх
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            index = i
            # Удаляем позиции в этом ряду
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        # Сдвигаем все ряды выше очищенного ряда вниз на количество очищенных рядов
        for key in sorted(list(locked), key=lambda x: x[1], reverse=True):
            x, y = key
            if y < index:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc


def draw_next_shape(piece, surface):
    """
    Отображает следующую фигуру (Next Shape) справа от игрового поля.
    """
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', True, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(
                    surface, piece.color,
                    (sx + j * block_size, sy + i * block_size, block_size, block_size), 0
                )

    surface.blit(label, (sx + 10, sy - 30))


def update_score(nscore):
    """
    Обновляет сохранённый лучший счёт (high score) в файле scores.txt.
    """
    score = max_score()
    with open('scores.txt', 'w') as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))


def max_score():
    """
    Читает лучший счёт из файла scores.txt.
    Если файла нет, возвращает 0.
    """
    try:
        with open('scores.txt', 'r') as f:
            lines = f.readlines()
            score = lines[0].strip()
    except:
        score = '0'
    return score


def draw_window(surface, grid, score=0, last_score=0):
    """
    Отображает основное окно игры:
      - Заголовок;
      - Игровую область (с заполненными клетками);
      - Текущий и лучший счёт.
    """
    surface.fill((0, 0, 0))
    # Заголовок "Tetris"
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', True, (255, 255, 255))
    surface.blit(label, (top_left_x + play_width / 2 - label.get_width() / 2, 30))
    # Текущий счёт
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Score: ' + str(score), True, (255, 255, 255))
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    surface.blit(label, (sx + 20, sy + 160))
    # Лучший счёт (High Score)
    label = font.render('High Score: ' + str(last_score), True, (255, 255, 255))
    sx = top_left_x - 200
    sy = top_left_y + 200
    surface.blit(label, (sx + 20, sy + 160))
    # Отображение самой игровой области (каждая клетка)
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(
                surface, grid[i][j],
                (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0
            )
    # Рисуем линии сетки и рамку вокруг игровой области
    draw_grid(surface, grid)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)


# ---------------------- ОСНОВНОЙ ИГРОВОЙ ЦИКЛ ---------------------- #
def main(win):
    """
    Основная функция, управляющая игровым процессом:
      - создание и обновление игрового поля;
      - обработка движения фигуры и нажатий клавиш;
      - фиксация фигуры при достижении нижней границы;
      - проверка завершения игры.
    """
    locked_positions = {}  # Словарь с позициями уже закреплённых фигур
    grid = create_grid(locked_positions)
    change_piece = False  # Флаг для фиксации фигуры
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27  # Начальная скорость падения
    level_time = 0
    score = 0
    last_score = int(max_score())
    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()
        # Со временем повышается сложность (увеличивается скорость падения)
        if level_time / 1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005
        # Падение фигуры через заданный интервал времени
        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
        # Обработка событий (нажатия клавиш)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
            if event.type == pygame.KEYDOWN:
                # Движение влево
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                # Движение вправо
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                # Ускоренное падение вниз
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                # Поворот фигуры
                if event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
        shape_pos = convert_shape_format(current_piece)
        # Добавляем текущую фигуру в игровое поле
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color
        # Если фигура не может дальше двигаться, закрепляем её и выбираем новую
        if change_piece:
            for pos in shape_pos:
                locked_positions[(pos[0], pos[1])] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10
        draw_window(win, grid, score, last_score)
        draw_next_shape(next_piece, win)
        pygame.display.update()
        # Проверяем условие проигрыша (фигуры достигли верха игрового поля)
        if check_lost(locked_positions):
            draw_text_middle(win, "YOU LOST!", 80, (255, 255, 255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            update_score(score)


# ---------------------- МЕНЮ И ЗАПУСК ИГРЫ ---------------------- #
def main_menu(win):
    """
    Отображает стартовое меню с приглашением нажать любую клавишу для начала игры.
    """
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text_middle(win, "Press any key to begin", 60, (255, 255, 255))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win)
    pygame.quit()


if __name__ == '__main__':
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris')
    main_menu(win)
