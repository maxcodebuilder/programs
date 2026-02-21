import pygame
import math

# --- Setup ---
WIDTH, HEIGHT = 800, 600
FPS = 60
# Level 1 Path
PATH = [(0, 300), (200, 300), (200, 100), (500, 100), (500, 500), (800, 500)]

class Gear(pygame.sprite.Sprite):
    def __init__(self, x, y, level=1):
        super().__init__()
        self.level = level
        self.update_appearance()
        self.rect = self.image.get_rect(center=(x, y))
        self.range = 100 + (self.level * 20)
        self.cooldown = 0
        self.is_dragging = False

    def update_appearance(self):
        # Color changes based on level
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        color = (100, 100, 100) if self.level == 1 else (50, 150, 255) if self.level == 2 else (255, 200, 0)
        pygame.draw.circle(self.image, color, (20, 20), 18)
        # Draw level number
        font = pygame.font.SysFont("Arial", 18, bold=True)
        text = font.render(str(self.level), True, (255, 255, 255))
        self.image.blit(text, (13, 10))

    def update(self, enemies, bullets):
        if self.is_dragging:
            self.rect.center = pygame.mouse.get_pos()
            return
            
        if self.cooldown > 0: self.cooldown -= 1
        for enemy in enemies:
            dist = math.hypot(enemy.rect.centerx - self.rect.centerx, enemy.rect.centery - self.rect.centery)
            if dist <= self.range and self.cooldown == 0:
                bullets.add(Bullet(self.rect.centerx, self.rect.centery, enemy, self.level))
                self.cooldown = max(10, 40 - (self.level * 10)) # Faster fire rate per level
                break

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed=2):
        super().__init__()
        self.image = pygame.Surface((30, 30)); self.image.fill((200, 0, 0))
        self.path = PATH; self.speed = speed; self.waypoint = 0
        self.pos = pygame.Vector2(self.path[0]); self.rect = self.image.get_rect(center=self.pos)
        self.health = 3
    def update(self):
        if self.waypoint < len(self.path) - 1:
            target = pygame.Vector2(self.path[self.waypoint + 1])
            dir = (target - self.pos)
            if dir.length() <= self.speed: self.waypoint += 1
            else: self.pos += dir.normalize() * self.speed
            self.rect.center = self.pos
        else: self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target, power):
        super().__init__(); self.image = pygame.Surface((8, 8)); self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y)); self.target, self.speed, self.power = target, 8, power
    def update(self):
        if not self.target.alive(): self.kill(); return
        dir = pygame.Vector2(self.target.rect.center) - pygame.Vector2(self.rect.center)
        if dir.length() < 10: 
            self.target.health -= self.power
            if self.target.health <= 0: self.target.kill()
            self.kill()
        else: self.rect.center += dir.normalize() * self.speed

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    gears, enemies, bullets = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
    selected_gear = None
    spawn_timer = 0

    while True:
        screen.fill((20, 20, 20))
        pygame.draw.lines(screen, (40, 40, 40), False, PATH, 8) # Draw path

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if clicking existing gear to drag
                for g in gears:
                    if g.rect.collidepoint(event.pos):
                        selected_gear = g
                        g.is_dragging = True
                        break
                else: # Place new gear
                    gears.add(Gear(*event.pos))

            if event.type == pygame.MOUSEBUTTONUP and selected_gear:
                selected_gear.is_dragging = False
                # Check for Merge
                hits = pygame.sprite.spritecollide(selected_gear, gears, False)
                for other in hits:
                    if other != selected_gear and other.level == selected_gear.level:
                        new_level = selected_gear.level + 1
                        new_pos = other.rect.center
                        other.kill()
                        selected_gear.kill()
                        gears.add(Gear(*new_pos, level=new_level))
                        break
                selected_gear = None

        spawn_timer += 1
        if spawn_timer >= 60:
            enemies.add(Enemy(speed=3)); spawn_timer = 0

        gears.update(enemies, bullets); enemies.update(); bullets.update()
        gears.draw(screen); enemies.draw(screen); bullets.draw(screen)
        pygame.display.flip(); clock.tick(FPS)

if __name__ == "__main__": main()
