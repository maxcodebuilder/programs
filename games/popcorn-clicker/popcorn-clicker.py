import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
KERNEL_RADIUS = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
LIGHT_YELLOW = (255, 255, 200)

# Setup Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Popcorn Clicker")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 24)

# Popcorn Kernel Class
class Kernel:
    def __init__(self):
        self.x = random.randint(KERNEL_RADIUS + 50, WIDTH - KERNEL_RADIUS - 50)
        self.y = random.randint(KERNEL_RADIUS + 50, HEIGHT - KERNEL_RADIUS - 50)
        self.radius = KERNEL_RADIUS
        self.popped = False
        self.pop_particles = []
    
    def draw(self, surface):
        if not self.popped:
            # Draw kernel
            pygame.draw.circle(surface, ORANGE, (self.x, self.y), self.radius)
            pygame.draw.circle(surface, YELLOW, (self.x, self.y), self.radius - 3)
            # Highlight
            pygame.draw.circle(surface, LIGHT_YELLOW, (self.x - 5, self.y - 5), 5)
        else:
            # Draw pop particles
            for particle in self.pop_particles:
                pygame.draw.circle(surface, particle['color'], (int(particle['x']), int(particle['y'])), particle['size'])
    
    def is_clicked(self, mouse_x, mouse_y):
        if self.popped:
            return False
        distance = math.sqrt((mouse_x - self.x) ** 2 + (mouse_y - self.y) ** 2)
        return distance <= self.radius
    
    def pop(self):
        self.popped = True
        # Create pop particles
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            self.pop_particles.append({
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.randint(2, 6),
                'color': random.choice([YELLOW, ORANGE, RED]),
                'life': 30
            })
    
    def update_particles(self):
        for particle in self.pop_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2  # Gravity
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.pop_particles.remove(particle)
    
    def is_done(self):
        return self.popped and len(self.pop_particles) == 0

# Game Variables
score = 0
kernels = [Kernel()]
combo = 0
combo_timer = 0

# Game Loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)
    
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for kernel in kernels:
                if kernel.is_clicked(mouse_x, mouse_y):
                    kernel.pop()
                    score += 1 + combo
                    combo += 1
                    combo_timer = 60
                    break
    
    # Spawn new kernels occasionally
    if len(kernels) < 3 and random.random() < 0.02:
        kernels.append(Kernel())
    
    # Update and draw kernels
    for kernel in kernels[:]:
        kernel.update_particles()
        kernel.draw(screen)
        if kernel.is_done():
            kernels.remove(kernel)
    
    # Update combo timer
    if combo_timer > 0:
        combo_timer -= 1
    else:
        combo = 0
    
    # Draw UI
    score_text = font.render(f"Score: {score}", True, YELLOW)
    screen.blit(score_text, (10, 10))
    
    if combo > 0:
        combo_text = small_font.render(f"Combo x{combo}!", True, RED)
        screen.blit(combo_text, (WIDTH - 200, 10))
    
    instructions = small_font.render("Click the popcorn kernels!", True, WHITE)
    screen.blit(instructions, (WIDTH // 2 - 150, HEIGHT - 30))
    
    pygame.display.flip()

pygame.quit()
