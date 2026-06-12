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
C_LEVEL_BG = (20, 24, 30)
C_LEVEL_BORDER = (80, 110, 150)
C_LEVEL_DOT = (180, 220, 255)
C_SEEN_GREY = (20, 20, 20)
C_SPRITE_BG = (255, 255, 255)
C_SALT = (236, 240, 241)
C_FLAME = (243, 156, 18)
C_BLUE_ORB = (52, 152, 219)
CAMERA_SCALE = 1.35

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


class LaserWarning(pygame.sprite.Sprite):
    def __init__(self, center, direction, delay=60):
        super().__init__()
        self.pos = pygame.math.Vector2(center)
        self.direction = pygame.math.Vector2(direction).normalize()
        self.delay = delay
        self.harmful = False
        size = 240
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self._render_warning()

    def _render_warning(self):
        self.image.fill((0, 0, 0, 0))
        cx = self.rect.width // 2
        cy = self.rect.height // 2
        pygame.draw.line(self.image, (230, 110, 50, 180), (cx, cy), (cx + int(self.direction.x * 110), cy + int(self.direction.y * 110)), 8)
        pygame.draw.circle(self.image, (255, 200, 100, 180), (cx + int(self.direction.x * 110), cy + int(self.direction.y * 110)), 12)

    def update(self, *args):
        self.delay -= 1
        if self.delay <= 0:
            beam = LaserBeam(self.pos, self.direction)
            groups = list(self.groups())
            self.kill()
            for group in groups:
                group.add(beam)


class LaserBeam(pygame.sprite.Sprite):
    def __init__(self, center, direction, length=900, width=18, duration=45):
        super().__init__()
        self.pos = pygame.math.Vector2(center)
        self.direction = pygame.math.Vector2(direction).normalize()
        self.harmful = True
        surf = pygame.Surface((width, length), pygame.SRCALPHA)
        surf.fill((255, 85, 85, 200))
        self.image = pygame.transform.rotate(surf, -math.degrees(math.atan2(self.direction.y, self.direction.x)) - 90)
        self.rect = self.image.get_rect(center=center)
        self.life = duration

    def update(self, *args):
        self.life -= 1
        if self.life <= 0:
            self.kill()


class PieHazard(pygame.sprite.Sprite):
    def __init__(self, center, slices=8, delay=300):
        super().__init__()
        self.pos = pygame.math.Vector2(center)
        self.slices = slices
        self.delay = delay
        self.safe_slice = random.randrange(slices)
        self.harmful = False
        self.radius = 260
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self._render_warning()

    def _render_warning(self):
        self.image.fill((0, 0, 0, 0))
        cx = self.radius
        cy = self.radius
        for i in range(self.slices):
            angle = (2 * math.pi / self.slices) * i
            next_angle = (2 * math.pi / self.slices) * (i + 1)
            color = (40, 180, 220, 180) if i == self.safe_slice else (220, 40, 80, 160)
            points = [
                (cx, cy),
                (cx + math.cos(angle) * self.radius, cy + math.sin(angle) * self.radius),
                (cx + math.cos(next_angle) * self.radius, cy + math.sin(next_angle) * self.radius),
            ]
            pygame.draw.polygon(self.image, color, points)
        pygame.draw.circle(self.image, (20, 20, 35, 120), (cx, cy), int(self.radius * 0.25))

    def update(self, *args):
        self.delay -= 1
        if self.delay <= 0:
            center = self.pos
            groups = list(self.groups())
            self.kill()
            for i in range(self.slices):
                if i == self.safe_slice:
                    continue
                angle = (2 * math.pi / self.slices) * i + math.pi / self.slices
                beam = LaserBeam(center, (math.cos(angle), math.sin(angle)), length=900, width=18, duration=90)
                for group in groups:
                    group.add(beam)


class Fireball(pygame.sprite.Sprite):
    def __init__(self, start_pos):
        super().__init__()
        self.pos = pygame.math.Vector2(start_pos)
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.direction.length_squared() == 0:
            self.direction = pygame.math.Vector2(1, 0)
        self.direction = self.direction.normalize()
        self.speed = 1.0
        self.harmful = True
        self.image = pygame.Surface((22, 22), pygame.SRCALPHA)
        pygame.draw.circle(self.image, C_FLAME, (11, 11), 11)
        pygame.draw.circle(self.image, (255, 220, 120), (11, 9), 5)
        self.rect = self.image.get_rect(center=start_pos)

    def update(self, *args):
        self.pos += self.direction * self.speed
        if self.pos.distance_to((WIDTH // 2, HEIGHT // 2)) > 340:
            self.direction *= -1
        self.rect.center = self.pos


def draw_hearts(surface, health, total=2, x=16, y=46):
    for i in range(total):
        heart_x = x + i * 36
        heart_surf = pygame.Surface((24, 20), pygame.SRCALPHA)
        pygame.draw.circle(heart_surf, (200, 0, 0) if i < health else (80, 0, 0), (8, 8), 8)
        pygame.draw.circle(heart_surf, (200, 0, 0) if i < health else (80, 0, 0), (16, 8), 8)
        pygame.draw.polygon(heart_surf, (200, 0, 0) if i < health else (80, 0, 0), [(2, 10), (22, 10), (12, 20)])
        surface.blit(heart_surf, (heart_x, y))


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


def draw_boss(surface, kind, center, defeated=False, scale=1.0):
    x, y = center
    def s(value):
        return int(value * scale)

    if kind == "butter":
        pygame.draw.rect(surface, C_BUTTER, (x - s(60), y - s(40), s(120), s(80)), border_radius=s(20))
        pygame.draw.rect(surface, (255, 230, 128), (x - s(50), y - s(30), s(100), s(50)), border_radius=s(14))
        pygame.draw.rect(surface, (190, 144, 70), (x - s(60), y - s(40), s(120), s(12)), border_radius=s(20))
        pygame.draw.circle(surface, (60, 42, 20), (x - s(20), y - s(4)), s(8))
        pygame.draw.circle(surface, (60, 42, 20), (x + s(20), y - s(4)), s(8))
        pygame.draw.circle(surface, (255, 255, 255), (x - s(20), y - s(6)), s(3))
        pygame.draw.circle(surface, (255, 255, 255), (x + s(20), y - s(6)), s(3))
        pygame.draw.arc(surface, (140, 80, 30), (x - s(24), y + s(4), s(48), s(30)), 3.14, 0, s(4))
    elif kind == "salt":
        pygame.draw.rect(surface, (189, 195, 199), (x - s(48), y - s(52), s(96), s(104)), border_radius=s(20))
        pygame.draw.rect(surface, C_SALT, (x - s(44), y - s(48), s(88), s(42)), border_radius=s(14))
        for row in range(3):
            for col in range(4):
                pygame.draw.circle(surface, (127, 140, 141), (x - s(30) + col * s(20), y - s(30) + row * s(18)), s(4))
        pygame.draw.circle(surface, (50, 50, 50), (x - s(18), y - s(8)), s(6))
        pygame.draw.circle(surface, (50, 50, 50), (x + s(18), y - s(8)), s(6))
        pygame.draw.arc(surface, (130, 130, 130), (x - s(22), y + s(4), s(44), s(24)), 0.5, 2.6, s(3))
    elif kind == "flame":
        points = [(x, y - s(60)), (x + s(34), y + s(20)), (x + s(18), y + s(60)), (x, y + s(28)), (x - s(18), y + s(60)), (x - s(34), y + s(20))]
        pygame.draw.polygon(surface, C_FLAME, points)
        pygame.draw.polygon(surface, (249, 231, 159), [(x, y - s(40)), (x + s(18), y + s(16)), (x + s(8), y + s(44)), (x, y + s(24)), (x - s(8), y + s(44)), (x - s(18), y + s(16))])
        pygame.draw.circle(surface, (40, 40, 40), (x - s(12), y - s(10)), s(6))
        pygame.draw.circle(surface, (40, 40, 40), (x + s(12), y - s(10)), s(6))
        pygame.draw.circle(surface, (255, 255, 255), (x - s(12), y - s(12)), s(3))
        pygame.draw.circle(surface, (255, 255, 255), (x + s(12), y - s(12)), s(3))
        pygame.draw.arc(surface, (225, 90, 25), (x - s(18), y + s(2), s(36), s(20)), 0.4, 2.7, s(4))
    elif kind == "blue_orb":
        pygame.draw.circle(surface, C_BLUE_ORB, (x, y), s(42))
        pygame.draw.circle(surface, (173, 216, 230), (x, y), s(24))
        pygame.draw.circle(surface, (255, 255, 255), (x - s(8), y - s(8)), s(8))
        pygame.draw.circle(surface, C_BLUE_ORB, (x, y), s(42), s(4))
        pygame.draw.circle(surface, (20, 20, 80), (x - s(12), y - s(6)), s(8))
        pygame.draw.circle(surface, (20, 20, 80), (x + s(12), y - s(6)), s(8))
        pygame.draw.circle(surface, (255, 255, 255), (x - s(11), y - s(7)), s(3))
        pygame.draw.circle(surface, (255, 255, 255), (x + s(13), y - s(7)), s(3))
        pygame.draw.arc(surface, (50, 140, 220), (x - s(18), y + s(6), s(36), s(22)), 0.5, 2.6, s(3))
    if defeated:
        pygame.draw.line(surface, (200, 40, 40), (x - s(30), y - s(30)), (x + s(30), y + s(30)), s(6))
        pygame.draw.line(surface, (200, 40, 40), (x + s(30), y - s(30)), (x - s(30), y + s(30)), s(6))

# Game Orchestrator Execution Module
def world_to_screen(pos, cam_topleft):
    return ((pos - cam_topleft) * CAMERA_SCALE)


def draw_world_circle(surface, color, center, radius, width=0, border_radius=0):
    screen_center = world_to_screen(pygame.math.Vector2(center), draw_world_circle.cam_topleft)
    scaled_radius = int(radius * CAMERA_SCALE)
    if width == 0:
        pygame.draw.circle(surface, color, (int(screen_center.x), int(screen_center.y)), scaled_radius)
    else:
        pygame.draw.circle(surface, color, (int(screen_center.x), int(screen_center.y)), scaled_radius, max(1, int(width * CAMERA_SCALE)))


def draw_world_rect(surface, color, rect, border_radius=0, width=0):
    scaled_rect = pygame.Rect(
        int((rect[0] - draw_world_rect.cam_topleft.x) * CAMERA_SCALE),
        int((rect[1] - draw_world_rect.cam_topleft.y) * CAMERA_SCALE),
        int(rect[2] * CAMERA_SCALE),
        int(rect[3] * CAMERA_SCALE),
    )
    pygame.draw.rect(surface, color, scaled_rect, width, border_radius=int(border_radius * CAMERA_SCALE))


def draw_world_sprite(surface, sprite, cam_topleft):
    sprite_center = pygame.math.Vector2(sprite.pos)
    screen_center = world_to_screen(sprite_center, cam_topleft)
    scaled_size = (max(1, int(sprite.image.get_width() * CAMERA_SCALE)), max(1, int(sprite.image.get_height() * CAMERA_SCALE)))
    image = pygame.transform.smoothscale(sprite.image, scaled_size)
    rect = image.get_rect(center=(int(screen_center.x), int(screen_center.y)))
    surface.blit(image, rect)


def draw_level_bar(surface, levels, seen_levels, defeated_levels, font, alive_count):
    bar_height = 100
    bar_y = HEIGHT - bar_height
    pygame.draw.rect(surface, C_LEVEL_BG, (0, bar_y, WIDTH, bar_height))
    pygame.draw.rect(surface, C_LEVEL_BORDER, (10, bar_y + 10, WIDTH - 20, bar_height - 20), 2, border_radius=12)

    node_count = len(levels)
    spacing = (WIDTH - 120) // (node_count - 1)
    base_x = 60
    node_y = bar_y + 40
    points = [(base_x + i * spacing, node_y) for i in range(node_count)]

    for i in range(node_count - 1):
        start = points[i]
        end = points[i + 1]
        seg_length = 8
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dist = math.hypot(dx, dy)
        steps = max(1, int(dist // seg_length))
        for j in range(steps):
            t = j / steps
            segment_x = start[0] + dx * t
            segment_y = start[1] + dy * t
            if j % 2 == 0:
                pygame.draw.circle(surface, C_LEVEL_DOT, (int(segment_x), int(segment_y)), 3)

    for idx, level in enumerate(levels):
        x, y = points[idx]
        if idx in seen_levels:
            color = C_BUTTER if level['kind'] == 'butter' else C_SALT if level['kind'] == 'salt' else C_FLAME if level['kind'] == 'flame' else C_BLUE_ORB
        else:
            color = (15, 15, 15)
        pygame.draw.circle(surface, color, (x, y), 18)
        pygame.draw.circle(surface, C_LEVEL_BORDER, (x, y), 18, 2)
        if idx in defeated_levels:
            pygame.draw.line(surface, (220, 40, 40), (x - 12, y - 12), (x + 12, y + 12), 4)
            pygame.draw.line(surface, (220, 40, 40), (x + 12, y - 12), (x - 12, y + 12), 4)
        label = font.render(level['name'], True, (235, 235, 235) if idx in seen_levels else (80, 80, 80))
        surface.blit(label, (x - label.get_width() // 2, y + 26))

    text = font.render(f"{alive_count}/60 left", True, (225, 225, 225))
    surface.blit(text, (20, bar_y + 8))


def run_game():
    running = True
    player = Player(WIDTH // 2, HEIGHT // 2 + 150)
    all_sprites = pygame.sprite.Group(player)
    projectiles = pygame.sprite.Group()
    hazards = pygame.sprite.Group()
    virtual_players = pygame.sprite.Group()
    popcorn_covers = pygame.sprite.Group()
    
    boss_attack_timer = 0
    fire_laser_timer = 0
    pie_hazard_timer = 0
    
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
    hud_font = pygame.font.Font(None, 20)
    seen_levels = set([0])
    defeated_levels = set()
    last_level_index = 0
    spawn_timer = 0
    start_time = time.time()
    
    while running:
        clock.tick(60)
        keys = pygame.key.get_pressed()
        elapsed = time.time() - start_time
        level_index = min(len(levels) - 1, int(elapsed // level_duration))
        current_level = levels[level_index]
        if level_index != last_level_index:
            defeated_levels.add(last_level_index)
            seen_levels.add(level_index)
            last_level_index = level_index

        seen_levels.add(level_index)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.activate_ability()

        # Update Scene Graph Logic
        all_sprites.update(keys)
        projectiles.update()
        hazards.update()
        
        # Threat Engine Generation (Simulating a hostile Center Boss)
        spawn_timer += 1
        if spawn_timer >= current_level["interval"]:
            spawn_timer = 0
            boss_pos = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
            if current_level["kind"] == "butter":
                boss_attack_timer += 1
                if boss_attack_timer % 2 == 1:
                    for offset in (-20, 0, 20):
                        target = pygame.math.Vector2(player.pos.x + offset, player.pos.y + offset)
                        p = Projectile(boss_pos, target, kind="butter", speed=random.uniform(4, 5))
                        projectiles.add(p)
                        all_sprites.add(p)
                else:
                    for i in range(8):
                        angle = i * (2 * math.pi / 8)
                        target = boss_pos + pygame.math.Vector2(math.cos(angle), math.sin(angle)) * 260
                        p = Projectile(boss_pos, target, kind="butter", speed=4)
                        projectiles.add(p)
                        all_sprites.add(p)
            elif current_level["kind"] == "salt":
                if random.choice([True, False]):
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            target = boss_pos + pygame.math.Vector2(dx * 60, dy * 60)
                            p = Projectile(boss_pos, target, kind="salt", speed=4)
                            projectiles.add(p)
                            all_sprites.add(p)
                else:
                    for i in range(10):
                        angle = i * (2 * math.pi / 10)
                        target = boss_pos + pygame.math.Vector2(math.cos(angle), math.sin(angle)) * 260
                        p = Projectile(boss_pos, target, kind="salt", speed=4)
                        projectiles.add(p)
                        all_sprites.add(p)
            elif current_level["kind"] == "flame":
                if fire_laser_timer <= 0:
                    for direction in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        hazards.add(LaserWarning(boss_pos, direction, delay=60))
                    fire_laser_timer = 180
                for _ in range(3):
                    start = boss_pos + pygame.math.Vector2(random.uniform(-180, 180), random.uniform(-180, 180))
                    f = Fireball(start)
                    projectiles.add(f)
                    all_sprites.add(f)
            elif current_level["kind"] == "blue_orb":
                if fire_laser_timer <= 0:
                    for direction in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        hazards.add(LaserWarning(boss_pos, direction, delay=60))
                    fire_laser_timer = 240
                if pie_hazard_timer <= 0:
                    hazards.add(PieHazard(boss_pos, slices=8, delay=300))
                    pie_hazard_timer = 420
            else:
                target = pygame.math.Vector2(player.pos.x + random.randint(-50, 50), player.pos.y + random.randint(-50, 50))
                p = Projectile(boss_pos, target, kind=current_level["kind"], speed=random.uniform(*current_level["speed"]))
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

        for hazard in list(hazards):
            if getattr(hazard, 'harmful', False) and player.rect.colliderect(hazard.rect):
                player.take_damage()
                hazard.kill()

        if fire_laser_timer > 0:
            fire_laser_timer -= 1
        if pie_hazard_timer > 0:
            pie_hazard_timer -= 1

        # Render Sequence Graphics
        screen.fill(C_STOVE) # Clear frame buffer background
        pygame.draw.rect(screen, (28, 31, 34), (0, HEIGHT - 120, WIDTH, 120))

        cam_half_w = WIDTH / (2 * CAMERA_SCALE)
        cam_half_h = HEIGHT / (2 * CAMERA_SCALE)
        cam_center = pygame.math.Vector2(player.pos)
        cam_center.x = max(cam_half_w, min(cam_center.x, WIDTH - cam_half_w))
        cam_center.y = max(cam_half_h, min(cam_center.y, HEIGHT - cam_half_h))
        cam_topleft = pygame.math.Vector2(cam_center.x - cam_half_w, cam_center.y - cam_half_h)
        draw_world_circle.cam_topleft = cam_topleft
        draw_world_rect.cam_topleft = cam_topleft

        pygame.draw.rect(screen, (38, 45, 52), (WIDTH // 2 - 60, HEIGHT - 120, 120, 80), border_radius=18)
        pygame.draw.circle(screen, (55, 70, 85), (WIDTH // 2, HEIGHT // 2 + 95), 120)
        pygame.draw.circle(screen, (70, 90, 110), (WIDTH // 2, HEIGHT // 2 + 95), 110, 8)

        # Render Circular Pan Field Arena Elements
        draw_world_circle(screen, C_PAN, (WIDTH // 2, HEIGHT // 2), 350)
        draw_world_circle(screen, C_PAN_EDGE, (WIDTH // 2, HEIGHT // 2), 334, width=4)
        draw_world_rect(screen, C_HANDLE, (WIDTH // 2 + 320, HEIGHT // 2 - 20, 240, 40), border_radius=20)
        draw_world_rect(screen, (30, 35, 40), (WIDTH // 2 + 342, HEIGHT // 2 - 14, 196, 28), border_radius=14)
        boss_screen = world_to_screen(pygame.math.Vector2(WIDTH // 2, HEIGHT // 2), cam_topleft)
        draw_boss(screen, current_level["kind"], (int(boss_screen.x), int(boss_screen.y)), defeated=False, scale=CAMERA_SCALE)
        
        # Iteratively draw sprites explicitly 
        for entity in all_sprites:
            draw_world_sprite(screen, entity, cam_topleft)
        for proj in projectiles:
            draw_world_sprite(screen, proj, cam_topleft)

        level_label = level_font.render(
            f"Level {level_index + 1}: {current_level['name']}", True, (236, 240, 241)
        )
        screen.blit(level_label, (16, 16))
        draw_hearts(screen, player.health, total=2, x=16, y=52)
        alive_count = (0 if player.is_popped else 1) + len(virtual_players)
        draw_level_bar(screen, levels, seen_levels, defeated_levels, hud_font, alive_count)
                
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    run_game()
