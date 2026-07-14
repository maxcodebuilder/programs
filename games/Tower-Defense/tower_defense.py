import pygame
import math
import random
import sys

# --- CONFIGURATION & CONSTANTS ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
GREY  = (100, 100, 100)
GREEN = (34, 139, 34)
RED   = (220, 20, 60)
BLUE  = (30, 144, 255)
GOLD  = (255, 215, 0)
BLACK = (0, 0, 0)

# Pre-defined path waypoints for enemies to follow
PATH = [(0, 300), (200, 300), (200, 100), (500, 100), (500, 450), (800, 450)]

# --- GAME ENTITIES ---

class Enemy:
    def __init__(self):
        self.x, self.y = PATH[0]
        self.target_waypoint_idx = 1
        self.speed = 1.5
        self.max_health = 100
        self.health = self.max_health
        self.radius = 12
        self.reward = 25
        self.reached_end = False

    def move(self):
        if self.target_waypoint_idx >= len(PATH):
            self.reached_end = True
            return

        target_x, target_y = PATH[self.target_waypoint_idx]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)

        if distance <= self.speed:
            self.x, self.y = target_x, target_y
            self.target_waypoint_idx += 1
        else:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

    def draw(self, surface):
        # Enemy body
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)
        # Health bar background
        pygame.draw.rect(surface, GREY, (int(self.x) - 15, int(self.y) - 22, 30, 5))
        # Health bar remaining
        health_ratio = max(0, self.health / self.max_health)
        pygame.draw.rect(surface, GREEN, (int(self.x) - 15, int(self.y) - 22, int(30 * health_ratio), 5))


class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.range = 130
        self.cooldown = 30  # Frames between shots
        self.timer = 0
        self.cost = 100

    def update(self, enemies, projectiles):
        if self.timer > 0:
            self.timer -= 1

        if self.timer == 0:
            # Target the enemy closest to the base inside our range
            for enemy in reversed(enemies):
                if math.hypot(enemy.x - self.x, enemy.y - self.y) <= self.range:
                    projectiles.append(Projectile(self.x, self.y, enemy))
                    self.timer = self.cooldown
                    break

    def draw(self, surface):
        # Draw range circle indicator faintly
        range_surf = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
        pygame.draw.circle(range_surf, (30, 144, 255, 30), (self.range, self.range), self.range)
        surface.blit(range_surf, (self.x - self.range, self.y - self.range))
        
        # Tower body
        pygame.draw.circle(surface, BLUE, (self.x, self.y), 18)
        pygame.draw.circle(surface, BLACK, (self.x, self.y), 18, 2)


class Projectile:
    def __init__(self, x, y, target):
        self.x = x
        self.y = y
        self.target = target
        self.speed = 7
        self.damage = 20
        self.hit = False

    def move(self):
        # If target dies before arrival, self-destruct logic simplifies to straight line
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.hypot(dx, dy)

        if distance <= self.speed:
            self.target.health -= self.damage
            self.hit = True
        else:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

    def draw(self, surface):
        pygame.draw.circle(surface, GOLD, (int(self.x), int(self.y)), 5)


# --- MAIN GAME CLASS ---

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Python Tower Defense")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)

        # Game State Variables
        self.lives = 10
        self.money = 250
        self.enemies = []
        self.towers = []
        self.projectiles = []
        
        self.spawn_timer = 0
        self.spawn_delay = 90  # Frames between enemy spawns
        self.running = True

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Left Click to place a tower
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Prevent building directly on top of other towers or too close to the UI
                if self.money >= 100:
                    too_close = False
                    for t in self.towers:
                        if math.hypot(t.x - mouse_pos[0], t.y - mouse_pos[1]) < 30:
                            too_close = True
                    
                    if not too_close:
                        self.towers.append(Tower(mouse_pos[0], mouse_pos[1]))
                        self.money -= 100

    def update(self):
        if self.lives <= 0:
            return

        # Spawning logic
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.enemies.append(Enemy())
            self.spawn_timer = 0

        # Update Enemies
        for enemy in self.enemies[:]:
            enemy.move()
            if enemy.reached_end:
                self.lives -= 1
                self.enemies.remove(enemy)
            elif enemy.health <= 0:
                self.money += enemy.reward
                self.enemies.remove(enemy)

        # Update Towers
        for tower in self.towers:
            tower.update(self.enemies, self.projectiles)

        # Update Projectiles
        for proj in self.projectiles[:]:
            proj.move()
            if proj.hit or proj.target not in self.enemies:
                if proj in self.projectiles:
                    self.projectiles.remove(proj)

    def draw(self):
        # Fill Map Background
        self.screen.fill(GREEN)

        # Draw the enemy pathway track
        if len(PATH) > 1:
            pygame.draw.lines(self.screen, GREY, False, PATH, 40)

        # Draw Entities
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for tower in self.towers:
            tower.draw(self.screen)
        for proj in self.projectiles:
            proj.draw(self.screen)

        # Draw Simple HUD
        hud_text = f"Lives: {self.lives}  |  Gold: ${self.money}  |  Tower Cost: $100"
        text_surface = self.font.render(hud_text, True, WHITE)
        # Background bar for HUD text
        pygame.draw.rect(self.screen, BLACK, (0, 0, SCREEN_WIDTH, 40))
        self.screen.blit(text_surface, (15, 8))

        # Game Over Screen overlays
        if self.lives <= 0:
            game_over_surface = self.font.render("GAME OVER - Press Esc to Exit", True, RED)
            self.screen.blit(game_over_surface, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.process_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
