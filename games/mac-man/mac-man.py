import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH, HEIGHT = 560, 620
CELL_SIZE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man")

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255, 182, 193)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Maze layout (1 = wall, 0 = dot, 2 = empty, 3 = power pellet)
MAZE = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,0,1,1,1,1,1,0,1,1,0,1,1,1,1,1,0,1,1,1,1,0,1],
    [1,3,1,1,1,1,0,1,1,1,1,1,0,1,1,0,1,1,1,1,1,0,1,1,1,1,3,1],
    [1,0,1,1,1,1,0,1,1,1,1,1,0,1,1,0,1,1,1,1,1,0,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,0,1],
    [1,0,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,1,1,0,0,0,0,0,1,1,0,0,0,0,0,1,1,0,0,0,0,0,1],
    [1,1,1,1,1,0,1,1,1,1,1,0,0,1,1,0,0,1,1,1,1,1,0,1,1,1,1,1],
    [0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0],
    [1,1,1,1,1,0,1,1,0,1,1,1,1,2,2,1,1,1,1,0,1,1,0,1,1,1,1,1],
    [0,0,0,0,0,0,1,1,0,1,2,2,2,2,2,2,2,2,1,0,1,1,0,0,0,0,0,0],
    [1,1,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,1,1],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,1,1],
    [0,0,0,0,0,0,1,1,0,1,2,2,2,2,2,2,2,2,1,0,1,1,0,0,0,0,0,0],
    [1,1,1,1,1,0,1,1,0,1,1,1,1,2,2,1,1,1,1,0,1,1,0,1,1,1,1,1],
    [0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0],
    [1,1,1,1,1,0,1,1,1,1,1,0,0,1,1,0,0,1,1,1,1,1,0,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,0,1],
    [1,3,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,0,0,3,1],
    [1,1,1,0,1,0,1,1,0,1,1,0,0,1,1,0,0,1,1,0,1,1,0,1,0,1,1,1],
    [1,0,0,0,0,0,1,1,0,1,1,0,0,1,1,0,0,1,1,0,1,1,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,0,1,1,0,0,1,1,0,0,1,1,0,1,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

# Pac-Man starting position
pacman_x, pacman_y = 14 * CELL_SIZE, 23 * CELL_SIZE
pacman_dir = [0, 0]  # [dx, dy]

# Ghosts
ghosts = [
    {"x": 12 * CELL_SIZE, "y": 14 * CELL_SIZE, "color": RED, "dir": [0, -CELL_SIZE]},
    {"x": 13 * CELL_SIZE, "y": 14 * CELL_SIZE, "color": PINK, "dir": [0, -CELL_SIZE]},
    {"x": 14 * CELL_SIZE, "y": 14 * CELL_SIZE, "color": CYAN, "dir": [0, -CELL_SIZE]},
    {"x": 15 * CELL_SIZE, "y": 14 * CELL_SIZE, "color": ORANGE, "dir": [0, -CELL_SIZE]}
]

# Score
score = 0
lives = 3
font = pygame.font.Font(None, 36)

# Game loop
clock = pygame.time.Clock()
FPS = 10

def draw_maze():
    for y in range(len(MAZE)):
        for x in range(len(MAZE[y])):
            if MAZE[y][x] == 1:
                pygame.draw.rect(screen, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif MAZE[y][x] == 0:
                pygame.draw.circle(screen, WHITE, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), 3)
            elif MAZE[y][x] == 3:
                pygame.draw.circle(screen, WHITE, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), 8)

def move_pacman():
    global pacman_x, pacman_y, score
    new_x = pacman_x + pacman_dir[0]
    new_y = pacman_y + pacman_dir[1]
    
    # Check wall collision
    grid_x = new_x // CELL_SIZE
    grid_y = new_y // CELL_SIZE
    if MAZE[grid_y][grid_x] != 1:
        pacman_x = new_x
        pacman_y = new_y
        
        # Eat dots
        if MAZE[grid_y][grid_x] == 0:
            MAZE[grid_y][grid_x] = 2
            score += 10
        elif MAZE[grid_y][grid_x] == 3:
            MAZE[grid_y][grid_x] = 2
            score += 50

def move_ghosts():
    for ghost in ghosts:
        # Simple random movement for now
        directions = [[0, -CELL_SIZE], [0, CELL_SIZE], [-CELL_SIZE, 0], [CELL_SIZE, 0]]
        random.shuffle(directions)
        for dx, dy in directions:
            new_x = ghost["x"] + dx
            new_y = ghost["y"] + dy
            grid_x = new_x // CELL_SIZE
            grid_y = new_y // CELL_SIZE
            if MAZE[grid_y][grid_x] != 1:
                ghost["x"] = new_x
                ghost["y"] = new_y
                ghost["dir"] = [dx, dy]
                break

def check_collisions():
    global lives, pacman_x, pacman_y, pacman_dir
    for ghost in ghosts:
        if abs(pacman_x - ghost["x"]) < CELL_SIZE and abs(pacman_y - ghost["y"]) < CELL_SIZE:
            lives -= 1
            if lives <= 0:
                print("Game Over! Final score:", score)
                pygame.quit()
                sys.exit()
            # Reset positions
            pacman_x, pacman_y = 14 * CELL_SIZE, 23 * CELL_SIZE
            pacman_dir = [0, 0]
            for ghost in ghosts:
                ghost["x"] = 13 * CELL_SIZE + ghosts.index(ghost) * CELL_SIZE
                ghost["y"] = 14 * CELL_SIZE

running = True
while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                pacman_dir = [-CELL_SIZE, 0]
            elif event.key == pygame.K_RIGHT:
                pacman_dir = [CELL_SIZE, 0]
            elif event.key == pygame.K_UP:
                pacman_dir = [0, -CELL_SIZE]
            elif event.key == pygame.K_DOWN:
                pacman_dir = [0, CELL_SIZE]
    
    move_pacman()
    move_ghosts()
    check_collisions()
    
    draw_maze()
    
    # Draw Pac-Man
    pygame.draw.circle(screen, YELLOW, (pacman_x + CELL_SIZE // 2, pacman_y + CELL_SIZE // 2), CELL_SIZE // 2)
    
    # Draw Ghosts
    for ghost in ghosts:
        pygame.draw.circle(screen, ghost["color"], (ghost["x"] + CELL_SIZE // 2, ghost["y"] + CELL_SIZE // 2), CELL_SIZE // 2)
    
    # Draw score and lives
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 40))
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
