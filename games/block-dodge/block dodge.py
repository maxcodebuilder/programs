import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 400
PLAYER_SIZE = 20
PROJECTILE_SIZE = 10
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Setup Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Popcorn Doodle Clone")
clock = pygame.time.Clock()

# Player Setup
player_pos = [WIDTH // 2, HEIGHT - 50]
player_speed = 5

# Projectile Setup
projectiles = []

def spawn_projectile():
    x = random.randint(0, WIDTH)
    y = 0
    speed = random.randint(3, 7)
    projectiles.append([x, y, speed])

# Game Loop
running = True
frame_count = 0
while running:
    screen.fill(BLACK)
    frame_count += 1

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_pos[0] > 0:
        player_pos[0] -= player_speed
    if keys[pygame.K_RIGHT] and player_pos[0] < WIDTH - PLAYER_SIZE:
        player_pos[0] += player_speed
    if keys[pygame.K_UP] and player_pos[1] > 0:
        player_pos[1] -= player_speed
    if keys[pygame.K_DOWN] and player_pos[1] < HEIGHT - PLAYER_SIZE:
        player_pos[1] += player_speed

    # Projectile Logic
    if frame_count % 10 == 0:
        spawn_projectile()

    for p in projectiles[:]:
        p[1] += p[2] # Move down
        
        # Collision Detection
        p_rect = pygame.Rect(p[0], p[1], PROJECTILE_SIZE, PROJECTILE_SIZE)
        player_rect = pygame.Rect(player_pos[0], player_pos[1], PLAYER_SIZE, PLAYER_SIZE)
        
        if p_rect.colliderect(player_rect):
            print("Game Over")
            running = False
            
        if p[1] > HEIGHT:
            projectiles.remove(p)
        else:
            pygame.draw.rect(screen, YELLOW, p_rect)

    # Draw Player
    pygame.draw.rect(screen, WHITE, (player_pos[0], player_pos[1], PLAYER_SIZE, PLAYER_SIZE))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()