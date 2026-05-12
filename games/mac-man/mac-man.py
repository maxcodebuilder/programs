import pygame
import sys
import random
import random

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH, HEIGHT = 560, 560
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
    [1,1,1,0,1,0,1,1,0,1,1,1,0,1,1,1,0,1,1,0,1,1,0,1,0,1,1,1],
    [1,0,0,0,0,0,1,1,0,1,1,1,0,1,1,1,0,1,1,0,1,1,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,0,1,1,1,0,1,1,1,0,1,1,0,1,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

# Pac-Man starting position
pacman_x, pacman_y = 14 * CELL_SIZE, 23 * CELL_SIZE
pacman_dir = [0, 0]  # [dx, dy]

# Ghosts
ghosts = [
    {"x": 12 * CELL_SIZE, "y": 14 * CELL_SIZE, "color": RED, "base_color": RED, "dir": [0, -CELL_SIZE], "state": "chase", "start_x": 12 * CELL_SIZE, "start_y": 14 * CELL_SIZE},
    {"x": 13 * CELL_SIZE, "y": 14 * CELL_SIZE, "color": PINK, "base_color": PINK, "dir": [0, -CELL_SIZE], "state": "chase", "start_x": 13 * CELL_SIZE, "start_y": 14 * CELL_SIZE},
    {"x": 14 * CELL_SIZE, "y": 14 * CELL_SIZE, "color": CYAN, "base_color": CYAN, "dir": [0, -CELL_SIZE], "state": "chase", "start_x": 14 * CELL_SIZE, "start_y": 14 * CELL_SIZE},
    {"x": 15 * CELL_SIZE, "y": 14 * CELL_SIZE, "color": ORANGE, "base_color": ORANGE, "dir": [0, -CELL_SIZE], "state": "chase", "start_x": 15 * CELL_SIZE, "start_y": 14 * CELL_SIZE}
]

power_timer = 0
POWER_DURATION = 100

# Score
score = 0
lives = 3
font = pygame.font.Font(None, 36)

# Animation
frame_count = 0

def draw_pacman(x, y, direction):
    center_x = x + CELL_SIZE // 2
    center_y = y + CELL_SIZE // 2
    radius = CELL_SIZE // 2
    
    # Mouth animation
    mouth_angle = (frame_count % 20) * 9  # 0 to 180 degrees over 20 frames
    if mouth_angle > 90:
        mouth_angle = 180 - mouth_angle  # Close mouth
    
    # Determine mouth direction based on movement
    if direction == [CELL_SIZE, 0]:  # right
        start_angle = 360 - mouth_angle // 2
        end_angle = mouth_angle // 2
    elif direction == [-CELL_SIZE, 0]:  # left
        start_angle = 180 - mouth_angle // 2
        end_angle = 180 + mouth_angle // 2
    elif direction == [0, -CELL_SIZE]:  # up
        start_angle = 90 - mouth_angle // 2
        end_angle = 90 + mouth_angle // 2
    elif direction == [0, CELL_SIZE]:  # down
        start_angle = 270 - mouth_angle // 2
        end_angle = 270 + mouth_angle // 2
    else:  # not moving
        start_angle = 30
        end_angle = 330
    
    # Draw Pac-Man body
    pygame.draw.circle(screen, YELLOW, (center_x, center_y), radius)
    
    # Draw mouth (black triangle)
    mouth_points = [
        (center_x, center_y),
        (center_x + radius * pygame.math.Vector2(1, 0).rotate(start_angle).x,
         center_y + radius * pygame.math.Vector2(1, 0).rotate(start_angle).y),
        (center_x + radius * pygame.math.Vector2(1, 0).rotate(end_angle).x,
         center_y + radius * pygame.math.Vector2(1, 0).rotate(end_angle).y)
    ]
    pygame.draw.polygon(screen, BLACK, mouth_points)

def draw_ghost(x, y, color):
    center_x = x + CELL_SIZE // 2
    center_y = y + CELL_SIZE // 2
    radius = CELL_SIZE // 2
    
    # Ghost body (top half circle, bottom wavy)
    body_points = []
    
    # Top half circle
    for angle in range(0, 181, 10):
        px = center_x + radius * pygame.math.Vector2(1, 0).rotate(angle).x
        py = center_y + radius * pygame.math.Vector2(1, 0).rotate(angle).y
        body_points.append((px, py))
    
    # Bottom wavy part
    wave_height = 3
    for i in range(4):
        wx = center_x - radius + (i * radius * 2 // 3)
        wy = center_y + radius - wave_height if i % 2 == 0 else center_y + radius + wave_height
        body_points.append((wx, wy))
    
    body_points.append((center_x + radius, center_y + radius))
    
    pygame.draw.polygon(screen, color, body_points)
    
    # Eyes
    eye_radius = 3
    eye_offset_x = 4
    eye_offset_y = -2
    
    # Left eye
    pygame.draw.circle(screen, WHITE, (center_x - eye_offset_x, center_y + eye_offset_y), eye_radius)
    pygame.draw.circle(screen, BLACK, (center_x - eye_offset_x - 1, center_y + eye_offset_y), 1)
    
    # Right eye
    pygame.draw.circle(screen, WHITE, (center_x + eye_offset_x, center_y + eye_offset_y), eye_radius)
    pygame.draw.circle(screen, BLACK, (center_x + eye_offset_x - 1, center_y + eye_offset_y), 1)

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
                pygame.draw.circle(screen, PINK, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), 8)

def move_pacman():
    global pacman_x, pacman_y, score, power_timer
    new_x = pacman_x + pacman_dir[0]
    new_y = pacman_y + pacman_dir[1]
    
    # Check vertical bounds (no wrapping for top/bottom)
    if new_y < 0 or new_y >= HEIGHT:
        return
    
    # Check wall collision
    grid_x = new_x // CELL_SIZE
    grid_y = new_y // CELL_SIZE
    
    # Handle wrapping through tunnels
    if new_x < 0:
        if MAZE[grid_y][0] != 1:  # Left tunnel exists
            new_x = (len(MAZE[0]) - 1) * CELL_SIZE
        else:
            return  # Can't move left
    elif new_x >= WIDTH:
        if MAZE[grid_y][len(MAZE[0]) - 1] != 1:  # Right tunnel exists
            new_x = 0
        else:
            return  # Can't move right
    
    # Recalculate grid after wrapping
    grid_x = new_x // CELL_SIZE
    
    if 0 <= grid_x < len(MAZE[0]) and MAZE[grid_y][grid_x] != 1:
        pacman_x = new_x
        pacman_y = new_y
        
        # Eat dots
        if MAZE[grid_y][grid_x] == 0:
            MAZE[grid_y][grid_x] = 2
            score += 10
        elif MAZE[grid_y][grid_x] == 3:
            MAZE[grid_y][grid_x] = 2
            score += 50
            power_timer = POWER_DURATION
            for ghost in ghosts:
                if ghost["state"] == "chase":
                    ghost["state"] = "vulnerable"
                    ghost["color"] = BLUE

def get_ghost_target(ghost, index):
    if ghost["state"] == "dead":
        return ghost["start_x"], ghost["start_y"]

    if index == 0:
        return pacman_x, pacman_y
    elif index == 1:
        # Pink ghost tries to intercept ahead of Pac-Man
        return pacman_x + pacman_dir[0] * 3, pacman_y + pacman_dir[1] * 3
    elif index == 2:
        return pacman_x - 3 * CELL_SIZE, pacman_y - 3 * CELL_SIZE
    else:
        return pacman_x + 3 * CELL_SIZE, pacman_y + 3 * CELL_SIZE


def move_ghosts():
    for index, ghost in enumerate(ghosts):
        if ghost["state"] == "dead":
            target_x, target_y = ghost["start_x"], ghost["start_y"]
        elif ghost["state"] == "vulnerable":
            # Run away from Pac-Man when vulnerable
            target_x, target_y = 2 * ghost["x"] - pacman_x, 2 * ghost["y"] - pacman_y
        else:
            target_x, target_y = get_ghost_target(ghost, index)

        best_move = None
        best_score = None
        directions = [[0, -CELL_SIZE], [0, CELL_SIZE], [-CELL_SIZE, 0], [CELL_SIZE, 0]]
        random.shuffle(directions)
        for dir_dx, dir_dy in directions:
            new_x = ghost["x"] + dir_dx
            new_y = ghost["y"] + dir_dy
            grid_x = new_x // CELL_SIZE
            grid_y = new_y // CELL_SIZE
            if not (0 <= grid_x < len(MAZE[0]) and 0 <= grid_y < len(MAZE)):
                continue
            if MAZE[grid_y][grid_x] == 1:
                continue
            distance = abs(target_x - new_x) + abs(target_y - new_y)
            if ghost["state"] == "vulnerable":
                distance = -distance
            if best_score is None or distance < best_score:
                best_score = distance
                best_move = (dir_dx, dir_dy)

        if best_move:
            ghost["x"] += best_move[0]
            ghost["y"] += best_move[1]
            ghost["dir"] = [best_move[0], best_move[1]]
            if ghost["state"] == "dead" and ghost["x"] == ghost["start_x"] and ghost["y"] == ghost["start_y"]:
                ghost["state"] = "chase"
                ghost["color"] = ghost["base_color"]

def check_collisions():
    global lives, pacman_x, pacman_y, pacman_dir, score
    for ghost in ghosts:
        if abs(pacman_x - ghost["x"]) < CELL_SIZE and abs(pacman_y - ghost["y"]) < CELL_SIZE:
            if ghost["state"] == "vulnerable":
                score += 200
                ghost["state"] = "dead"
                ghost["color"] = WHITE
                ghost["dir"] = [0, 0]
                continue
            if ghost["state"] == "dead":
                continue
            lives -= 1
            if lives <= 0:
                print("Game Over! Final score:", score)
                pygame.quit()
                sys.exit()
            # Reset positions
            pacman_x, pacman_y = 14 * CELL_SIZE, 23 * CELL_SIZE
            pacman_dir = [0, 0]
            for i, ghost in enumerate(ghosts):
                ghost["x"] = 12 * CELL_SIZE + i * CELL_SIZE
                ghost["y"] = 14 * CELL_SIZE
                ghost["state"] = "chase"
                ghost["color"] = ghost["base_color"]
                ghost["dir"] = [0, -CELL_SIZE]

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

    if power_timer > 0:
        power_timer -= 1
        if power_timer <= 0:
            for ghost in ghosts:
                if ghost["state"] == "vulnerable":
                    ghost["state"] = "chase"
                    ghost["color"] = ghost["base_color"]
    
    draw_maze()
    
    # Draw Pac-Man
    draw_pacman(pacman_x, pacman_y, pacman_dir)
    
    # Draw Ghosts
    for ghost in ghosts:
        draw_ghost(ghost["x"], ghost["y"], ghost["color"])
    
    # Draw score and lives
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 40))
    
    pygame.display.flip()
    clock.tick(FPS)
    
    # Increment frame count for animation
    frame_count += 1

pygame.quit()
sys.restart()
