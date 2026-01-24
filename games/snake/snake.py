import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Set up the game window
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake")

# Colors and settings
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 150, 0)
BLACK = (0, 0, 0)
CELL = 20
FPS = 10

# Font for score
font = pygame.font.Font(None, 36)

# Snake is a list of [x, y] segments (head is index 0)
# Start snake centered and aligned to the CELL grid so it can collide with food
snake = [[(width // 2) // CELL * CELL, (height // 2) // CELL * CELL]]
# Start moving right
direction = [CELL, 0]

# Place food on the grid
def random_food():
    return [random.randint(0, (width - CELL) // CELL) * CELL,
            random.randint(0, (height - CELL) // CELL) * CELL]

food = random_food()
score = 0

clock = pygame.time.Clock()

while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                if direction != [0, CELL]:
                    direction = [0, -CELL]
            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                if direction != [0, -CELL]:
                    direction = [0, CELL]
            elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                if direction != [CELL, 0]:
                    direction = [-CELL, 0]
            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                if direction != [-CELL, 0]:
                    direction = [CELL, 0]

    # Compute new head position
    head = snake[0]
    new_head = [head[0] + direction[0], head[1] + direction[1]]

    # Check collisions with walls
    if (new_head[0] < 0 or new_head[0] >= width or
            new_head[1] < 0 or new_head[1] >= height):
        print("Game Over! Final score:", score)
        pygame.quit()
        sys.exit()

    # Check collision with self
    if new_head in snake:
        print("Game Over! Final score:", score)
        pygame.quit()
        sys.exit()

    # Move snake
    snake.insert(0, new_head)

    # Check for food collision (exact grid match)
    if new_head == food:
        score += 1
        food = random_food()
    else:
        snake.pop()
    
    # Draw everything
    screen.fill(WHITE)
    # Draw food
    pygame.draw.rect(screen, RED, (food[0], food[1], CELL, CELL))
    # Draw snake
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL, CELL))

    # Draw score
    score_surf = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_surf, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)
