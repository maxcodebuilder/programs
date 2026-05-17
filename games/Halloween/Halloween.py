import pygame
import random
import math
import time

# Initialize Core System
pygame.init()
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Google Popcorn Doodle - Advanced Engine")
clock = pygame.time.Clock()

# Color Palette Definitions
C_CORN = (255, 223, 0)
C_POPPED = (255, 253, 208)
C_BUTTER = (244, 208, 63)
C_SHIELD = (52, 152, 219)
C_PAN = (44, 62, 80)
C_PAN_EDGE = (122, 184, 255)
C_STOVE = (36, 45, 50)
C_HANDLE = (20, 24, 28)
C_SALT = (236, 240, 241)
C_FLAME = (243, 156, 18)
C_BLUE_ORB = (52, 152, 219)

class Player(pygame.sprite.Sprite):
    """Represents the player kernel utilizing Vector physics and cooldown states."""
    def __init__(self, x, y, archetype="Shield"):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, C_CORN, (15, 15), 15)
        self.rect = self.image.get_rect(center=(x, y))
        
        # Physics Engines
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.speed = 5
        
        # Game Metrics
        self.archetype = archetype  
        self.health = 2  # Hearts
        self.is_popped = False
        
        # Cooldown State Trackers
        self.ability_active = False
        self.ability_duration = 0
        self.ability_cooldown = 0

    def update(self, keys):
        if self.is_popped:
            return

        # Vector Movement Mechanics
        self.vel.x = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT] or keys[pygame.K_d] - keys[pygame.K_a]
        self.vel.y = keys[pygame.K_DOWN] - keys[pygame.K_UP] or keys[pygame.K_s] - keys[pygame.K_w]
        
        if self.vel.length() > 0:
            self.pos += self.vel.normalize() * self.speed
            
        # Constrain Position to the Circular Frying Pan Arena Bounds
        center_dist = self.pos.distance_to((WIDTH // 2, HEIGHT // 2))
        if center_dist > 330:  # 350 Arena radius minus character bounding size
            to_center = (pygame.math.Vector2(WIDTH // 2, HEIGHT // 2) - self.pos).normalize()
            self.pos = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2) - to_center * 330
            
        self.rect.center = self.pos

        # Update Ability & Cooldown Cycles
        if self.ability_active:
            self.ability_duration -= 1
            if self.ability_duration <= 0:
                self.ability_active = False
        if self.ability_cooldown > 0:
            self.ability_cooldown -= 1

    def activate_ability(self):
        """Triggers character archetype specific buffs."""
        if self.ability_cooldown == 0 and not self.ability_active:
            self.ability_active = True
            self.ability_duration = 60  # Tracks activity frames (1 second at 60 FPS)
            self.ability_cooldown = 180 # 3 Second cooldown recharge sequence

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.ability_active and self.archetype == "Shield":
            # Visually render the perimeter force field
            pygame.draw.circle(surface, C_SHIELD, self.rect.center, 35, 3)

    def take_damage(self):
        if not self.ability_active:
            self.health -= 1
            if self.health <= 0:
                self.is_popped = True
                # Dynamically re-render the surface to a white popped corn state
                pygame.draw.circle(self.image, C_POPPED, (15, 15), 15)

class Projectile(pygame.sprite.Sprite):
    """An optimized, mathematically vector-driven threat tracking object."""
    def __init__(self, start_pos, target_pos, kind="butter", speed=4):
        super().__init__()
        self.kind = kind
        self.pos = pygame.math.Vector2(start_pos)
        self.vel = (pygame.math.Vector2(target_pos) - self.pos).normalize() * speed
        self.image = self._make_image(kind)
        self.rect = self.image.get_rect(center=start_pos)

    def _make_image(self, kind):
        surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        if kind == "butter":
            pygame.draw.ellipse(surf, C_BUTTER, (2, 4, 16, 10))
            pygame.draw.ellipse(surf, (255, 230, 128), (4, 6, 12, 6))
            pygame.draw.circle(surf, (255, 255, 240), (8, 8), 2)
            pygame.draw.circle(surf, (255, 255, 240), (12, 7), 2)
            pygame.draw.ellipse(surf, (255, 220, 120), (7, 10, 6, 6))
        elif kind == "salt":
            pygame.draw.circle(surf, (245, 245, 245), (10, 10), 9)
            pygame.draw.circle(surf, (225, 225, 225), (10, 10), 6)
            pygame.draw.circle(surf, (210, 210, 210), (6, 8), 2)
            pygame.draw.circle(surf, (210, 210, 210), (14, 7), 2)
            pygame.draw.circle(surf, (210, 210, 210), (10, 14), 2)
        elif kind == "flame":
            pygame.draw.polygon(surf, C_FLAME, [(10, 2), (18, 12), (12, 18), (10, 14), (8, 18), (2, 12)])
            pygame.draw.polygon(surf, (249, 231, 159), [(10, 5), (14, 12), (10, 16), (6, 12)])
            pygame.draw.circle(surf, (40, 40, 40), (7, 10), 3)
            pygame.draw.circle(surf, (40, 40, 40), (13, 10), 3)
            pygame.draw.circle(surf, (255, 255, 255), (7, 9), 1)
            pygame.draw.circle(surf, (255, 255, 255), (13, 9), 1)
            pygame.draw.arc(surf, (220, 80, 20), (6, 12, 8, 6), 3.4, 6.0, 2)
        elif kind == "blue_orb":
            pygame.draw.circle(surf, (64, 224, 208), (10, 10), 9)
            pygame.draw.circle(surf, (175, 238, 238), (10, 8), 4)
            pygame.draw.circle(surf, (235, 255, 255), (12, 6), 2)
            pygame.draw.circle(surf, (0, 128, 128), (10, 10), 9, 2)
        else:
            pygame.draw.circle(surf, (255, 255, 240), (10, 10), 8)
        return surf

    def update(self, *args):
        self.pos += self.vel
        self.rect.center = self.pos
        # Prune memory stack when bounds are breached
        if not (0 <= self.pos.x <= WIDTH and 0 <= self.pos.y <= HEIGHT):
            self.kill()


class VirtualPlayer(pygame.sprite.Sprite):
    """A CPU player that wanders and becomes cover when destroyed."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, C_CORN, (15, 15), 15)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.speed = 5
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.direction.length_squared() == 0:
            self.direction = pygame.math.Vector2(1, 0)
        self.change_timer = random.randint(30, 90)

    def update(self, *args):
        self.change_timer -= 1
        if self.change_timer <= 0 or self.direction.length_squared() == 0:
            self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            if self.direction.length_squared() == 0:
                self.direction = pygame.math.Vector2(1, 0)
            self.change_timer = random.randint(30, 90)

        boss_center = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        away_from_boss = self.pos - boss_center
        if away_from_boss.length_squared() > 0:
            avoid_force = away_from_boss.normalize() * 1.3
        else:
            avoid_force = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))

        center_dist = self.pos.distance_to(boss_center)
        if center_dist < 220:
            self.direction = (self.direction.normalize() * 0.4 + avoid_force * 0.8)
        else:
            self.direction = (self.direction.normalize() * 0.9 + avoid_force * 0.1)

        if self.direction.length_squared() == 0:
            self.direction = pygame.math.Vector2(1, 0)

        self.pos += self.direction.normalize() * self.speed

        pan_center = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        pan_radius = 330 - 12
        center_dist = self.pos.distance_to(pan_center)
        if center_dist > pan_radius:
            self.pos = pan_center + (self.pos - pan_center).normalize() * pan_radius
            self.direction = (self.pos - pan_center).normalize()

        self.rect.center = self.pos

    def die(self, all_sprites, popcorn_group):
        cover = PopcornCover(self.rect.center)
        popcorn_group.add(cover)
        all_sprites.add(cover)
        self.kill()


class PopcornCover(pygame.sprite.Sprite):
    """Protective popcorn kernel cover that absorbs three projectile hits."""
    def __init__(self, center):
        super().__init__()
        self.hits_left = 3
        self.pos = pygame.math.Vector2(center)
        self.image = pygame.Surface((26, 26), pygame.SRCALPHA)
        self._render()
        self.rect = self.image.get_rect(center=center)

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, C_POPPED, (13, 13), 12)
        pygame.draw.circle(self.image, (225, 220, 150), (11, 11), 4)
        pygame.draw.circle(self.image, (240, 235, 170), (15, 15), 3)
        for i in range(self.hits_left):
            pygame.draw.circle(self.image, (180, 150, 90), (6 + i * 7, 22), 3)

    def update(self, *args):
        self.rect.center = self.pos

    def hit(self):
        self.hits_left -= 1
        if self.hits_left <= 0:
            self.kill()
        else:
            self._render()


def draw_boss(surface, kind, center):
    x, y = center
    if kind == "butter":
        pygame.draw.rect(surface, C_BUTTER, (x - 60, y - 40, 120, 80), border_radius=20)
        pygame.draw.rect(surface, (255, 230, 128), (x - 50, y - 30, 100, 50), border_radius=14)
        pygame.draw.rect(surface, (190, 144, 70), (x - 60, y - 40, 120, 12), border_radius=20)
        pygame.draw.circle(surface, (60, 42, 20), (x - 20, y - 4), 8)
        pygame.draw.circle(surface, (60, 42, 20), (x + 20, y - 4), 8)
        pygame.draw.circle(surface, (255, 255, 255), (x - 20, y - 6), 3)
        pygame.draw.circle(surface, (255, 255, 255), (x + 20, y - 6), 3)
        pygame.draw.arc(surface, (140, 80, 30), (x - 24, y + 4, 48, 30), 3.14, 0, 4)
    elif kind == "salt":
        pygame.draw.rect(surface, (189, 195, 199), (x - 48, y - 52, 96, 104), border_radius=20)
        pygame.draw.rect(surface, C_SALT, (x - 44, y - 48, 88, 42), border_radius=14)
        for row in range(3):
            for col in range(4):
                pygame.draw.circle(surface, (127, 140, 141), (x - 30 + col * 20, y - 30 + row * 18), 4)
        pygame.draw.circle(surface, (50, 50, 50), (x - 18, y - 8), 6)
        pygame.draw.circle(surface, (50, 50, 50), (x + 18, y - 8), 6)
        pygame.draw.arc(surface, (130, 130, 130), (x - 22, y + 4, 44, 24), 0.5, 2.6, 3)
    elif kind == "flame":
        points = [(x, y - 60), (x + 34, y + 20), (x + 18, y + 60), (x, y + 28), (x - 18, y + 60), (x - 34, y + 20)]
        pygame.draw.polygon(surface, C_FLAME, points)
        pygame.draw.polygon(surface, (249, 231, 159), [(x, y - 40), (x + 18, y + 16), (x + 8, y + 44), (x, y + 24), (x - 8, y + 44), (x - 18, y + 16)])
        pygame.draw.circle(surface, (40, 40, 40), (x - 12, y - 10), 6)
        pygame.draw.circle(surface, (40, 40, 40), (x + 12, y - 10), 6)
        pygame.draw.circle(surface, (255, 255, 255), (x - 12, y - 12), 3)
        pygame.draw.circle(surface, (255, 255, 255), (x + 12, y - 12), 3)
        pygame.draw.arc(surface, (225, 90, 25), (x - 18, y + 2, 36, 20), 0.4, 2.7, 4)
    elif kind == "blue_orb":
        pygame.draw.circle(surface, C_BLUE_ORB, (x, y), 42)
        pygame.draw.circle(surface, (173, 216, 230), (x, y), 24)
        pygame.draw.circle(surface, (255, 255, 255), (x - 8, y - 8), 8)
        pygame.draw.circle(surface, C_BLUE_ORB, (x, y), 42, 4)
        pygame.draw.circle(surface, (20, 20, 80), (x - 12, y - 6), 8)
        pygame.draw.circle(surface, (20, 20, 80), (x + 12, y - 6), 8)
        pygame.draw.circle(surface, (255, 255, 255), (x - 11, y - 7), 3)
        pygame.draw.circle(surface, (255, 255, 255), (x + 13, y - 7), 3)
        pygame.draw.arc(surface, (50, 140, 220), (x - 18, y + 6, 36, 22), 0.5, 2.6, 3)

# Game Orchestrator Execution Module
def run_game():
    running = True
    player = Player(WIDTH // 2, HEIGHT // 2 + 150)
    all_sprites = pygame.sprite.Group(player)
    projectiles = pygame.sprite.Group()
    virtual_players = pygame.sprite.Group()
    popcorn_covers = pygame.sprite.Group()
    
    # Spawn 59 virtual players as additional cover sources
    while len(virtual_players) < 59:
        x = random.randint(80, WIDTH - 80)
        y = random.randint(80, HEIGHT - 80)
        if pygame.math.Vector2(x, y).distance_to((WIDTH // 2, HEIGHT // 2)) < 320:
            vp = VirtualPlayer(x, y)
            virtual_players.add(vp)
            all_sprites.add(vp)

    levels = [
        {"name": "Butter", "kind": "butter", "speed": (3, 4), "interval": 40},
        {"name": "Salt Shaker", "kind": "salt", "speed": (4, 5), "interval": 34},
        {"name": "Flame", "kind": "flame", "speed": (5, 6), "interval": 28},
        {"name": "Blue Orb", "kind": "blue_orb", "speed": (6, 7), "interval": 22},
    ]
    level_duration = 20
    level_font = pygame.font.Font(None, 28)
    spawn_timer = 0
    start_time = time.time()
    
    while running:
        clock.tick(60)
        keys = pygame.key.get_pressed()
        elapsed = time.time() - start_time
        level_index = min(len(levels) - 1, int(elapsed // level_duration))
        current_level = levels[level_index]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.activate_ability()

        # Update Scene Graph Logic
        all_sprites.update(keys)
        projectiles.update()
        
        # Threat Engine Generation (Simulating a hostile Center Boss)
        spawn_timer += 1
        if spawn_timer >= current_level["interval"]:
            spawn_timer = 0
            boss_pos = (WIDTH // 2, HEIGHT // 2)
            target = (player.pos.x + random.randint(-50, 50), player.pos.y + random.randint(-50, 50))
            p = Projectile(
                boss_pos,
                target,
                kind=current_level["kind"],
                speed=random.uniform(*current_level["speed"]),
            )
            projectiles.add(p)
            all_sprites.add(p)

        # Precise Spherical Matrix Collision Checks
        for proj in projectiles:
            popcorn_hit = pygame.sprite.spritecollideany(proj, popcorn_covers)
            if popcorn_hit:
                proj.kill()
                popcorn_hit.hit()
                continue

            vplayer_hit = pygame.sprite.spritecollideany(proj, virtual_players)
            if vplayer_hit:
                proj.kill()
                vplayer_hit.die(all_sprites, popcorn_covers)
                continue

            distance = player.pos.distance_to(proj.pos)
            if player.ability_active and player.archetype == "Shield":
                if distance < 35: # Contact resolved strictly against outer perimeter shield wall
                    proj.kill()
            elif distance < 23:   # Contact resolved against character frame
                proj.kill()
                player.take_damage()

        # Render Sequence Graphics
        screen.fill(C_STOVE) # Clear frame buffer background
        pygame.draw.rect(screen, (28, 31, 34), (0, HEIGHT - 120, WIDTH, 120))
        pygame.draw.rect(screen, (38, 45, 52), (WIDTH // 2 - 60, HEIGHT - 120, 120, 80), border_radius=18)
        pygame.draw.circle(screen, (55, 70, 85), (WIDTH // 2, HEIGHT // 2 + 95), 120)
        pygame.draw.circle(screen, (70, 90, 110), (WIDTH // 2, HEIGHT // 2 + 95), 110, 8)

        # Render Circular Pan Field Arena Elements
        pygame.draw.circle(screen, C_PAN, (WIDTH // 2, HEIGHT // 2), 350)
        pygame.draw.circle(screen, C_PAN_EDGE, (WIDTH // 2, HEIGHT // 2), 334, 4)
        pygame.draw.rect(screen, C_HANDLE, (WIDTH // 2 + 320, HEIGHT // 2 - 20, 240, 40), border_radius=20)
        pygame.draw.rect(screen, (30, 35, 40), (WIDTH // 2 + 342, HEIGHT // 2 - 14, 196, 28), border_radius=14)
        draw_boss(screen, current_level["kind"], (WIDTH // 2, HEIGHT // 2))
        
        # Iteratively draw sprites explicitly 
        for entity in all_sprites:
            if hasattr(entity, 'draw'):
                entity.draw(screen)
            else:
                screen.blit(entity.image, entity.rect)

        level_label = level_font.render(
            f"Level {level_index + 1}: {current_level['name']}", True, (236, 240, 241)
        )
        screen.blit(level_label, (16, 16))
                
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    run_game()
