import sched
import time
import pygame
from tetris_pieces import pieces
import random

pygame.init()

screen = pygame.display.set_mode((240, 480))
pygame.display.set_caption("Tetris")

BLOCK_SIZE = 20
fall_counter = 0
fall_speed = 10
score = 0
rotation_state = 0
w_key_pressed = False
game_over = False
highscore = 0
increased_speed = 15
delayer = sched.scheduler(time.time, time.sleep)
minus_speed = 1

board = []
for i in range(12):
    row = []
    for j in range(24):
        row.append(0)
    board.append(row)

def setPiece():
    global current_piece, piece_x, piece_y
    current_piece = random.choice(list(pieces.values()))
    piece_x = random.randrange(4, 8)
    piece_y = 0

def draw():
    for i in range(12):
        for j in range(24):   
            rand_gray =random.randrange(60, 150)
            rand_dark =random.randrange(0, 6)         
            if board[i][j] == 1:
                pygame.draw.rect(screen, (random.randrange(120, 220), random.randrange(120, 220), random.randrange(120, 220)), (i * BLOCK_SIZE, j * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
            elif board[i][j] == 2:
                pygame.draw.rect(screen, (rand_gray, rand_gray, rand_gray), (i * BLOCK_SIZE, j * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
            else:
                pygame.draw.rect(screen, (rand_dark, rand_dark, rand_dark), (i * BLOCK_SIZE, j * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    pygame.display.update()

def clear_previous_position():
    piece = current_piece
    for x in range(len(piece)):
        for y in range(len(piece[0])):
            if piece[x][y] == 1:
                board[piece_x + x][piece_y + y] = 0

def init_pieces():
    piece = current_piece
    for x in range(len(piece)):
        for y in range(len(piece[0])):
            if piece[x][y] == 1:
                if 0 <= piece_x + x < 12 and 0 <= piece_y + y < 24:  # Verifica los límites
                    board[piece_x + x][piece_y + y] = 1

def is_valid_position():
    piece = current_piece
    for x in range(len(piece)):
        for y in range(len(piece[0])):
            if piece[x][y] == 1:
                if (piece_x + x < 0 or piece_x + x >= 12 or piece_y + y >= 24):
                    return False
                if board[piece_x + x][piece_y + y] == 2:
                    return False
    return True

def piece_to_board():
    piece = current_piece
    for x in range(len(piece)):
        for y in range(len(piece[0])):
            if piece[x][y] == 1:
                board[piece_x + x][piece_y + y] = 2

def remove_completed_rows():
    global score, increased_speed
    rows_to_remove = []
    for j in range(24):
        if all(board[i][j] == 2 for i in range(12)):
            rows_to_remove.append(j)
    for row in rows_to_remove:
        for j in range(row, 0, -1):
            for i in range(12):
                board[i][j] = board[i][j - 1]
        print(increased_speed)
    return len(rows_to_remove)

def rotate_clockwise(piece):
    rotated_piece = [[piece[y][x] for y in range(len(piece))] for x in range(len(piece[0]))]
    rotated_piece = rotated_piece[::-1]
    return rotated_piece

# Bucle principal del juego
running = True
clock = pygame.time.Clock()
setPiece()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_columns_have_one = all(any(board[i][j] == 2 for i in range(12)) for j in range(24))
    if all_columns_have_one:
        game_over = True

    if game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            # Reinicia el juego
            board = [[0] * 24 for _ in range(12)]
            score = 0
            game_over = False
            setPiece()
        else:
            continue  # Espera a que el jugador presione "r" para reiniciar el juego

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a] and piece_x > 0:
        # Mover hacia la izquierda (A) y verificar los límites
        clear_previous_position()
        piece_x -= 1
        if not is_valid_position():
            piece_x += 1  # Deshace el movimiento si no es válido

    if keys[pygame.K_d] and piece_x + len(current_piece) < 12:
        # Mover hacia la derecha (D) y verificar los límites
        clear_previous_position()
        piece_x += 1
        if not is_valid_position():
            piece_x -= 1  # Deshace el movimiento si no es válido

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                w_key_pressed = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                w_key_pressed = False

    if keys[pygame.K_w]:
        clear_previous_position()
        # Rotar la pieza en sentido horario
        current_piece = rotate_clockwise(current_piece)
        rotation_state = (rotation_state + 1) % 4  # Actualiza el estado de rotación
        if not is_valid_position():
            # Deshace la rotación si no es válida
            current_piece = rotate_clockwise(current_piece)
            current_piece = rotate_clockwise(current_piece)
            current_piece = rotate_clockwise(current_piece)
            rotation_state = (rotation_state - 3) % 4

    if keys[pygame.K_s]:
        fall_speed = 1
    else:
        fall_speed = increased_speed

    fall_counter += 1
    if fall_counter >= fall_speed:
        clear_previous_position()
        piece_y += 1
        if not is_valid_position():
            piece_y -= 1  # Deshace el movimiento si no es válido
            piece_to_board()  # Agrega la pieza al tablero
            num_rows_removed = remove_completed_rows()
            if num_rows_removed > 0:
                score += num_rows_removed * 12
                if score > highscore:
                    with open('highscore', 'w') as file:
                        file.write(str(score))
                if score % 24 == 0 and score != 0:
                    if increased_speed > 1:
                        increased_speed -= minus_speed
                        minus_speed += 1
                print(f'Highscore: {highscore}')
                print(f'Score: {score}')
                print(f'Increased_speed: {increased_speed}')
            setPiece()  # Inicializa una nueva pieza
        fall_counter = 0

    try:
        with open('highscore', 'r') as file:
            highscore = int(file.readline())
    except FileNotFoundError:
        with open('highscore', 'w') as file:
            file.write(str(highscore))

    # Dibuja el tablero
    init_pieces()
    draw()

    clock.tick(10)  # Controla la velocidad de actualización de la pantalla

# Cierra Pygame al salir del bucle
pygame.quit()
file.close()
