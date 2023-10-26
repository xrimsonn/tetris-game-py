# Imports
import sched
import time
import pygame
from tetris_pieces import pieces
import random

# Initialize pygame
MIN_WINDOW_WIDTH = 120
MIN_WINDOW_HEIGHT = 240
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 480
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

# Initialize variables
BLOCK_SIZE = SCREEN_WIDTH/12
fall_counter = 0
fall_speed = 0
score = 0
rotation_state = 0
w_key_pressed = False
game_over = False
highscore = 0
increased_speed = 15
minus_speed = 2

# Initialize the board (12x24), every cell is 0
board = []
for i in range(12):
    row = []
    for j in range(24):
        row.append(0)
    board.append(row)

# Initialize the current piece


def setPiece():
    global current_piece, piece_x, piece_y
    current_piece = random.choice(list(pieces.values()))
    piece_x = random.randrange(4, 8)
    piece_y = 0

# Recalculate the size of the blocks


def recalculate_block_size():
    return screen.get_width() / 12

# Draw the board
# 0 = background
# 1 = current piece
# 2 = piece on the board


def draw():
    for i in range(12):
        for j in range(24):
            rand_gray = random.randrange(60, 150)
            rand_dark = random.randrange(0, 6)
            if board[i][j] == 1:
                pygame.draw.rect(screen, (random.randrange(120, 220), random.randrange(
                    120, 220), random.randrange(120, 220)), (i * BLOCK_SIZE, j * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
            elif board[i][j] == 2:
                pygame.draw.rect(screen, (rand_gray, rand_gray, rand_gray),
                                 (i * BLOCK_SIZE, j * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
            else:
                pygame.draw.rect(screen, (rand_dark, rand_dark, rand_dark),
                                 (i * BLOCK_SIZE, j * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    pygame.display.update()

# Clear the previous position of the piece


def clear_previous_position():
    piece = current_piece
    for x in range(len(piece)):
        for y in range(len(piece[0])):
            if piece[x][y] == 1:
                board[piece_x + x][piece_y + y] = 0

# Initialize the piece on the board


def init_pieces():
    piece = current_piece
    for x in range(len(piece)):
        for y in range(len(piece[0])):
            if piece[x][y] == 1:
                if 0 <= piece_x + x < 12 and 0 <= piece_y + y < 24:  # Verifica los límites
                    board[piece_x + x][piece_y + y] = 1

# Check if the piece is in a valid position


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

# Add the piece to the board


def piece_to_board():
    piece = current_piece
    for x in range(len(piece)):
        for y in range(len(piece[0])):
            if piece[x][y] == 1:
                board[piece_x + x][piece_y + y] = 2

# Remove completed rows


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
    return len(rows_to_remove)

# Rotate the piece clockwise


def rotate_clockwise(piece):
    rotated_piece = [[piece[y][x]
                      for y in range(len(piece))] for x in range(len(piece[0]))]
    rotated_piece = rotated_piece[::-1]
    return rotated_piece


# Initialize the first piece and others parameters
running = True
clock = pygame.time.Clock()
setPiece()
wkey_pressed = False


# Main loop
while running:
    # Check if the game is over
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and not wkey_pressed:
                wkey_pressed = True
                clear_previous_position()
                current_piece = rotate_clockwise(current_piece)
                rotation_state = (rotation_state + 1) % 4
                if not is_valid_position():
                    current_piece = rotate_clockwise(current_piece)
                    current_piece = rotate_clockwise(current_piece)
                    current_piece = rotate_clockwise(current_piece)
                    rotation_state = (rotation_state - 3) % 4
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                wkey_pressed = False

        # Check if all columns have a piece on the board (game over)
    all_columns_have_one = all(
        any(board[i][j] == 2 for i in range(12)) for j in range(24))
    if all_columns_have_one:
        game_over = True

        # Check if the player pressed "r" to restart the game after it's over
    if game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            # Reinicia el juego
            board = [[0] * 24 for _ in range(12)]
            score = 0
            increased_speed = 12
            game_over = False
            setPiece()
        else:
            continue

    keys = pygame.key.get_pressed()

    # Check if the player pressed "a" or "d" to move the piece
    if keys[pygame.K_a] and piece_x > 0:
        clear_previous_position()
        piece_x -= 1
        if not is_valid_position():
            piece_x += 1

    if keys[pygame.K_d] and piece_x + len(current_piece) < 12:
        clear_previous_position()
        piece_x += 1
        if not is_valid_position():
            piece_x -= 1

    # Check if the player pressed "w" to rotate the piece
    # if keys[pygame.K_w]:
    #     clear_previous_position()
    #     current_piece = rotate_clockwise(current_piece)
    #     rotation_state = (rotation_state + 1) % 4
    #     if not is_valid_position():
    #         current_piece = rotate_clockwise(current_piece)
    #         current_piece = rotate_clockwise(current_piece)
    #         current_piece = rotate_clockwise(current_piece)
    #         rotation_state = (rotation_state - 3) % 4

    # Check if the player pressed "s" to increase the speed of the piece
    if keys[pygame.K_s]:
        fall_speed = 1
    else:
        fall_speed = increased_speed

    # Check the fall speed of the piece
    fall_counter += 1
    if fall_counter >= fall_speed:
        clear_previous_position()
        piece_y += 1
        if not is_valid_position():
            piece_y -= 1
            piece_to_board()
            # Check if the player completed a row to sum points
            num_rows_removed = remove_completed_rows()
            if num_rows_removed > 0:
                score += num_rows_removed * 12
                # Check if the player beat the highscore
                if score > highscore:
                    with open('highscore', 'w') as file:
                        file.write(str(score))
                # Increase the speed of the pieces
                if score % 60 == 0 and score != 0:
                    if increased_speed > 1:
                        increased_speed -= minus_speed
                        # minus_speed += 1
                try:
                    with open('highscore', 'r') as file:
                        highscore = int(file.readline())
                except FileNotFoundError:
                    with open('highscore', 'w') as file:
                        file.write(str(highscore))
                print(f'Highscore: {highscore}')
                print(f'Score: {score}')
                print(f'Increased_speed: {increased_speed}')
            setPiece()
        fall_counter = 0

        # Write the highscore in a file

    # Draw the board
    init_pieces()
    draw()

    # Set the FPS
    clock.tick(10)

# Close the game
pygame.quit()
file.close()
