import pygame
import random
import math

pygame.init()

W, H = 1280, 720
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Temple Runner")
clock = pygame.time.Clock()

# ----- colors -----
BG = (18, 25, 35)
GROUND = (54, 88, 63)
PLATFORM = (94, 118, 72)
PLAYER = (54, 136, 255)
WHITE = (255, 255, 255)
RED = (220, 60, 50)
GOLD = (255, 210, 85)
BLACK = (0, 0, 0)
PLAYER_PROJECTILE = (255, 240, 120)
ENEMY_PROJECTILE = (255, 100, 150)
SKIN = (220, 185, 140)
HAIR = (70, 40, 24)
TUNIC = (42, 118, 78)
TUNIC_ACCENT = (200, 165, 80)
BELT = (108, 78, 48)
BOOT = (32, 25, 20)

ENEMY_COLORS = {
    "slime": (80, 180, 120),
    "bat": (180, 110, 230),
    "skeleton": (200, 200, 180),
    "spider": (90, 55, 40),
    "bee": (220, 200, 50),
    "charger": (240, 115, 70),
    "wisp": (120, 240, 255),
    "mimic": (140, 95, 60),
    "golem": (80, 80, 90),
    "eye": (200, 40, 80),
}

# ----- helpers -----
def draw_text(txt, x, y, color=WHITE, size=32, centered=False):
    f = pygame.font.Font(None, size)
    surf = f.render(txt, True, color)
    if centered:
        x -= surf.get_width() // 2
    screen.blit(surf, (x, y))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 32
        self.h = 48
        self.vx = 0
        self.vy = 0
        self.speed = 260
        self.jump = 620
        self.on_ground = False
        self.face = 1
        self.health = 6
        self.max_health = 6
        self.invuln = 0.0
        self.attack_timer = 0.0
        self.attack_cooldown = 0.0
        self.attack_damage = 1
        self.projectile_cooldown = 0.0
        self.projectile_speed = 520

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        move = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move += 1

        accel = 1800 * dt
        if move != 0:
            self.face = 1 if move > 0 else -1
            if self.vx * move < 0:
                self.vx += move * accel * 2.5
            self.vx += move * accel
            self.vx = max(-self.speed, min(self.speed, self.vx))
        else:
            if self.on_ground:
                self.vx *= 0.78
            else:
                self.vx *= 0.96
            if abs(self.vx) < 5:
                self.vx = 0

        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vy = -self.jump
            self.on_ground = False

        if keys[pygame.K_j] and self.attack_cooldown <= 0:
            self.attack_timer = 0.18
            self.attack_cooldown = 0.35

        if keys[pygame.K_k] and self.projectile_cooldown <= 0:
            self.projectile_cooldown = 0.25

        self.attack_timer = max(0, self.attack_timer - dt)
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.projectile_cooldown = max(0, self.projectile_cooldown - dt)

    def shoot(self):
        dx = 1 if self.face > 0 else -1
        start_x = self.x + self.w / 2 + dx * 18
        start_y = self.y + self.h / 2
        return {
            "x": start_x,
            "y": start_y,
            "vx": dx * self.projectile_speed,
            "vy": 0,
            "r": 5,
            "color": PLAYER_PROJECTILE,
            "damage": 1
        }

    def update(self, dt, platforms):
        self.vy += 1600 * dt
        self.x += self.vx * dt
        self.collide_x(platforms)
        self.y += self.vy * dt
        self.on_ground = False
        self.collide_y(platforms)

        if self.invuln > 0:
            self.invuln -= dt

        self.x = max(0, min(1600 - self.w, self.x))
        self.y = max(0, min(H - self.h, self.y))

    def collide_x(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vx > 0:
                    self.x = p.x - self.w
                elif self.vx < 0:
                    self.x = p.x + p.width

    def collide_y(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vy > 0:
                    self.y = p.y - self.h
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = p.y + p.height
                    self.vy = 0

    def attack_rect(self):
        if self.face > 0:
            return pygame.Rect(self.x + self.w - 4, self.y + 8, 48, self.h - 12)
        return pygame.Rect(self.x - 48, self.y + 8, 48, self.h - 12)

    def take_damage(self, amount):
        if self.invuln > 0:
            return
        self.health -= amount
        self.invuln = 0.7
        if self.health <= 0:
            self.health = 0
            return True
        return False

    def draw(self):
        x = int(self.x)
        y = int(self.y)

        # subtle walking motion so the sprite feels grounded
        walk_offset = 0
        if abs(self.vx) > 10:
            walk_offset = int((pygame.time.get_ticks() / 120) % 2) * 2 - 2

        # legs / boots
        leg_lift = walk_offset if self.on_ground and abs(self.vx) > 10 else 0
        pygame.draw.rect(screen, BOOT, (x + 8, y + 38 + leg_lift, 7, 10))
        pygame.draw.rect(screen, BOOT, (x + 17, y + 38 - leg_lift, 7, 10))
        pygame.draw.rect(screen, (120, 90, 60), (x + 8, y + 29 + leg_lift, 6, 10))
        pygame.draw.rect(screen, (120, 90, 60), (x + 18, y + 29 - leg_lift, 6, 10))

        # arms
        arm_offset = 18 if self.face > 0 else -6
        arm_bob = walk_offset // 2 if self.on_ground and abs(self.vx) > 10 else 0
        pygame.draw.rect(screen, SKIN, (x + 3 + arm_offset, y + 21 + arm_bob, 5, 14))
        pygame.draw.rect(screen, SKIN, (x + 24 - arm_offset, y + 21 - arm_bob, 5, 14))

        # torso / tunic
        torso_y = y + 17 + (walk_offset // 2 if self.on_ground and abs(self.vx) > 10 else 0)
        pygame.draw.rect(screen, TUNIC, (x + 8, torso_y, 16, 20))
        pygame.draw.rect(screen, BELT, (x + 7, torso_y + 12, 18, 5))
        pygame.draw.rect(screen, TUNIC_ACCENT, (x + 11, torso_y + 1, 8, 4))

        # head and hair
        head_y = y + 3 + (walk_offset // 2 if self.on_ground and abs(self.vx) > 10 else 0)
        pygame.draw.ellipse(screen, SKIN, (x + 6, head_y, 20, 18))
        pygame.draw.rect(screen, HAIR, (x + 7, head_y - 1, 18, 6))
        pygame.draw.polygon(screen, HAIR, [(x + 7, head_y + 7), (x + 16, head_y - 1), (x + 25, head_y + 7)])

        # 2 eyes, one on each side
        if self.face > 0:
            eye_left = (x + 10, y + 9)
            eye_right = (x + 18, y + 9)
        else:
            eye_left = (x + 14, y + 9)
            eye_right = (x + 22, y + 9)

        for px, py in (eye_left, eye_right):
            pygame.draw.circle(screen, WHITE, (px, py), 2)
            pygame.draw.circle(screen, BLACK, (px, py), 1)

        # sword swing when attacking
        if self.attack_timer > 0:
            if self.face > 0:
                pygame.draw.line(screen, (200, 200, 210), (x + 26, y + 22), (x + 42, y + 10), 3)
                pygame.draw.line(screen, GOLD, (x + 42, y + 10), (x + 48, y + 16), 2)
            else:
                pygame.draw.line(screen, (200, 200, 210), (x + 6, y + 22), (x - 10, y + 10), 3)
                pygame.draw.line(screen, GOLD, (x - 10, y + 10), (x - 16, y + 16), 2)

        # little body outline for the classic silhouette feel
        pygame.draw.rect(screen, BLACK, (x + 8, torso_y, 16, 20), 1)

class Enemy:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.w = 28
        self.h = 28
        self.vx = 0
        self.vy = 0
        self.speed = 90
        self.direction = random.choice([-1, 1])
        self.on_ground = False
        self.health = 1
        self.max_health = 1
        self.cooldown = random.random() * 2.5
        self.flying = False
        self.damage = 1
        self.dead = False
        self.color = ENEMY_COLORS.get(kind, (200, 200, 200))

        if kind == "slime":
            self.health = 2; self.speed = 70; self.damage = 1
        elif kind == "bat":
            self.health = 2; self.speed = 130; self.damage = 1; self.flying = True
        elif kind == "skeleton":
            self.health = 3; self.speed = 100; self.damage = 1
        elif kind == "spider":
            self.health = 2; self.speed = 130; self.damage = 1
        elif kind == "bee":
            self.health = 2; self.speed = 150; self.damage = 1; self.flying = True
        elif kind == "charger":
            self.health = 3; self.speed = 155; self.damage = 1
        elif kind == "wisp":
            self.health = 2; self.speed = 120; self.damage = 1; self.flying = True
        elif kind == "mimic":
            self.health = 4; self.speed = 80; self.damage = 2
        elif kind == "golem":
            self.health = 5; self.speed = 60; self.damage = 2
        elif kind == "eye":
            self.health = 3; self.speed = 110; self.damage = 2; self.flying = True

        self.max_health = self.health

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, dt, player, platforms):
        if self.dead:
            return

        if self.flying:
            dx = player.x - self.x
            dy = player.y - self.y
            dist = max(1, math.hypot(dx, dy))
            self.vx = (dx / dist) * self.speed
            self.vy = (dy / dist) * self.speed
            self.x += self.vx * dt
            self.y += self.vy * dt
        else:
            dx = player.x - self.x
            if abs(dx) > 10:
                self.direction = 1 if dx > 0 else -1
            self.vx += self.direction * 220 * dt
            self.vx = max(-self.speed, min(self.speed, self.vx))
            self.vy += 1600 * dt
            self.x += self.vx * dt
            self.collide_x(platforms)
            self.y += self.vy * dt
            self.on_ground = False
            self.collide_y(platforms)

        self.x = max(0, min(1600 - self.w, self.x))
        self.y = max(0, min(H - self.h, self.y))

        if self.rect.colliderect(player.rect):
            if player.invuln <= 0:
                player.take_damage(self.damage)

    def collide_x(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vx > 0:
                    self.x = p.x - self.w
                    self.direction = -1
                elif self.vx < 0:
                    self.x = p.x + p.width
                    self.direction = 1

    def collide_y(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vy > 0:
                    self.y = p.y - self.h
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = p.y + p.height
                    self.vy = 0

    def take_hit(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.dead = True

    def fire_projectile(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = max(1, math.hypot(dx, dy))

        if self.kind == "slime":
            speed = 160
            radius = 7
            color = (120, 220, 160)
        elif self.kind == "bat":
            speed = 210
            radius = 5
            color = (200, 130, 255)
        elif self.kind == "skeleton":
            speed = 180
            radius = 6
            color = (240, 230, 190)
        elif self.kind == "spider":
            speed = 190
            radius = 5
            color = (160, 90, 70)
        elif self.kind == "bee":
            speed = 240
            radius = 5
            color = (255, 220, 90)
        elif self.kind == "charger":
            speed = 280
            radius = 7
            color = (255, 125, 90)
        elif self.kind == "wisp":
            speed = 230
            radius = 6
            color = (110, 230, 255)
        elif self.kind == "mimic":
            speed = 170
            radius = 8
            color = (180, 130, 90)
        elif self.kind == "golem":
            speed = 150
            radius = 9
            color = (110, 110, 130)
        else:
            speed = 220
            radius = 6
            color = (255, 80, 130)

        return {
            "x": self.x + self.w / 2,
            "y": self.y + self.h / 2,
            "vx": (dx / dist) * speed,
            "vy": (dy / dist) * speed,
            "r": radius,
            "color": color,
            "damage": 1
        }

    def draw(self):
        if self.dead:
            return

        x = int(self.x)
        y = int(self.y)

        if self.kind == "slime":
            pygame.draw.ellipse(screen, self.color, (x, y + 5, self.w, self.h - 6))
            pygame.draw.ellipse(screen, BLACK, (x, y + 5, self.w, self.h - 6), 2)
            pygame.draw.circle(screen, (30, 90, 60), (x + 8, y + 12), 2)
            pygame.draw.circle(screen, (30, 90, 60), (x + 18, y + 12), 2)
        elif self.kind == "bat":
            pygame.draw.polygon(screen, self.color, [(x, y + 12), (x + 8, y), (x + 18, y + 12), (x + 28, y + 10), (x + 18, y + 28), (x + 8, y + 22)])
            pygame.draw.polygon(screen, BLACK, [(x, y + 12), (x + 8, y), (x + 18, y + 12), (x + 28, y + 10), (x + 18, y + 28), (x + 8, y + 22)], 2)
            pygame.draw.circle(screen, BLACK, (x + 9, y + 12), 2)
            pygame.draw.circle(screen, BLACK, (x + 19, y + 12), 2)
        elif self.kind == "skeleton":
            pygame.draw.rect(screen, self.color, (x + 5, y + 4, 18, 18))
            pygame.draw.line(screen, BLACK, (x + 6, y + 24), (x + 10, y + 28), 2)
            pygame.draw.line(screen, BLACK, (x + 22, y + 24), (x + 18, y + 28), 2)
            pygame.draw.circle(screen, BLACK, (x + 10, y + 10), 2)
            pygame.draw.circle(screen, BLACK, (x + 18, y + 10), 2)
        elif self.kind == "spider":
            pygame.draw.ellipse(screen, self.color, (x + 3, y + 2, 22, 16))
            pygame.draw.ellipse(screen, BLACK, (x + 3, y + 2, 22, 16), 2)
            for sx in (x + 5, x + 13, x + 21):
                pygame.draw.line(screen, BLACK, (sx, y + 16), (sx, y + 26), 2)
            pygame.draw.circle(screen, BLACK, (x + 9, y + 9), 2)
            pygame.draw.circle(screen, BLACK, (x + 19, y + 9), 2)
        elif self.kind == "bee":
            pygame.draw.ellipse(screen, self.color, (x + 5, y + 6, 18, 16))
            pygame.draw.polygon(screen, (220, 170, 40), [(x + 19, y + 8), (x + 28, y + 2), (x + 26, y + 14)])
            pygame.draw.circle(screen, BLACK, (x + 10, y + 11), 2)
            pygame.draw.circle(screen, BLACK, (x + 18, y + 11), 2)
        elif self.kind == "charger":
            pygame.draw.rect(screen, self.color, (x + 4, y + 6, 20, 16))
            pygame.draw.polygon(screen, (220, 80, 50), [(x + 8, y + 22), (x + 16, y + 28), (x + 24, y + 22)])
            pygame.draw.circle(screen, BLACK, (x + 10, y + 10), 2)
            pygame.draw.circle(screen, BLACK, (x + 18, y + 10), 2)
        elif self.kind == "wisp":
            pygame.draw.circle(screen, self.color, (x + 14, y + 14), 12)
            pygame.draw.circle(screen, BLACK, (x + 10, y + 12), 2)
            pygame.draw.circle(screen, BLACK, (x + 18, y + 12), 2)
            pygame.draw.arc(screen, BLACK, (x + 7, y + 16, 14, 8), 0.2, 3.0, 2)
        elif self.kind == "mimic":
            pygame.draw.rect(screen, self.color, (x + 3, y + 4, 22, 20))
            pygame.draw.rect(screen, BLACK, (x + 3, y + 4, 22, 20), 2)
            pygame.draw.rect(screen, (70, 50, 35), (x + 7, y + 10, 14, 7))
            pygame.draw.circle(screen, BLACK, (x + 11, y + 13), 2)
            pygame.draw.circle(screen, BLACK, (x + 19, y + 13), 2)
        elif self.kind == "golem":
            pygame.draw.rect(screen, self.color, (x + 4, y + 8, 20, 18))
            pygame.draw.rect(screen, BLACK, (x + 4, y + 8, 20, 18), 2)
            pygame.draw.circle(screen, BLACK, (x + 10, y + 14), 2)
            pygame.draw.circle(screen, BLACK, (x + 18, y + 14), 2)
            pygame.draw.line(screen, BLACK, (x + 8, y + 22), (x + 20, y + 22), 2)
        elif self.kind == "eye":
            pygame.draw.ellipse(screen, self.color, (x + 2, y + 4, 24, 18))
            pygame.draw.ellipse(screen, BLACK, (x + 2, y + 4, 24, 18), 2)
            pygame.draw.circle(screen, WHITE, (x + 10, y + 10), 4)
            pygame.draw.circle(screen, BLACK, (x + 10, y + 10), 2)
            pygame.draw.circle(screen, WHITE, (x + 18, y + 10), 4)
            pygame.draw.circle(screen, BLACK, (x + 18, y + 10), 2)
        else:
            pygame.draw.rect(screen, self.color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)

        bar = pygame.Rect(self.x, self.y - 10, self.w, 5)
        pct = max(0, self.health / max(1, self.max_health))
        pygame.draw.rect(screen, RED, bar)
        pygame.draw.rect(screen, (80, 220, 110), (bar.x, bar.y, bar.w * pct, 5))

PUZZLE_PATTERNS = {
    "easy": [
        [(160, 610, 260, 18), (440, 580, 260, 18), (720, 550, 240, 18), (1000, 515, 240, 18), (1240, 470, 180, 18)],
        [(140, 620, 260, 18), (430, 590, 260, 18), (700, 560, 240, 18), (980, 525, 240, 18), (1220, 480, 180, 18)],
        [(180, 610, 260, 18), (470, 580, 260, 18), (760, 550, 240, 18), (1040, 515, 240, 18), (1240, 470, 180, 18)],
        [(120, 620, 260, 18), (400, 590, 260, 18), (680, 560, 240, 18), (950, 525, 240, 18), (1210, 485, 180, 18)],
        [(170, 610, 260, 18), (450, 580, 260, 18), (740, 550, 240, 18), (1020, 515, 240, 18), (1230, 470, 180, 18)],
    ],
    "medium": [
        [(150, 600, 180, 18), (360, 560, 180, 18), (590, 520, 180, 18), (830, 470, 180, 18), (1060, 420, 180, 18), (1210, 360, 150, 18)],
        [(120, 610, 180, 18), (330, 570, 180, 18), (560, 520, 180, 18), (780, 470, 180, 18), (1000, 420, 180, 18), (1210, 360, 150, 18)],
        [(180, 590, 180, 18), (400, 550, 180, 18), (630, 500, 180, 18), (860, 450, 180, 18), (1080, 400, 180, 18), (1220, 350, 150, 18)],
        [(140, 610, 170, 18), (360, 560, 170, 18), (630, 510, 170, 18), (870, 460, 170, 18), (1080, 410, 170, 18), (1230, 350, 150, 18)],
        [(170, 600, 170, 18), (390, 550, 170, 18), (620, 500, 170, 18), (850, 450, 170, 18), (1070, 400, 170, 18), (1210, 350, 150, 18)],
    ],
    "hard": [
        [(120, 600, 150, 18), (330, 560, 150, 18), (560, 520, 150, 18), (790, 480, 150, 18), (1020, 440, 150, 18), (1210, 390, 150, 18)],
        [(100, 610, 150, 18), (310, 570, 150, 18), (530, 530, 150, 18), (760, 490, 150, 18), (990, 450, 150, 18), (1180, 410, 150, 18)],
        [(130, 590, 150, 18), (350, 550, 150, 18), (580, 510, 150, 18), (800, 470, 150, 18), (1030, 430, 150, 18), (1210, 390, 150, 18)],
        [(90, 620, 150, 18), (290, 580, 150, 18), (510, 540, 150, 18), (740, 500, 150, 18), (970, 460, 150, 18), (1170, 420, 150, 18)],
        [(150, 600, 150, 18), (370, 560, 150, 18), (600, 520, 150, 18), (830, 480, 150, 18), (1060, 440, 150, 18), (1210, 400, 150, 18)],
    ],
    "insane": [
        [(90, 590, 90, 18), (250, 520, 110, 18), (420, 450, 110, 18), (570, 380, 110, 18), (720, 310, 110, 18), (870, 250, 110, 18), (1010, 320, 110, 18), (1150, 220, 110, 18)],
        [(80, 610, 100, 18), (240, 560, 110, 18), (390, 500, 110, 18), (560, 430, 110, 18), (730, 360, 110, 18), (900, 290, 110, 18), (1050, 340, 110, 18), (1170, 260, 120, 18)],
        [(110, 600, 90, 18), (300, 540, 110, 18), (470, 470, 110, 18), (640, 390, 110, 18), (820, 320, 110, 18), (990, 260, 110, 18), (1140, 180, 120, 18)],
        [(130, 590, 100, 18), (300, 520, 110, 18), (500, 460, 110, 18), (680, 390, 110, 18), (860, 320, 110, 18), (1040, 260, 110, 18), (1180, 200, 120, 18)],
        [(100, 620, 100, 18), (270, 560, 100, 18), (440, 500, 100, 18), (620, 430, 100, 18), (790, 350, 100, 18), (960, 280, 100, 18), (1120, 210, 110, 18)],
    ],
}

class Hazard:
    def __init__(self, x, y, w, h, kind):
        self.rect = pygame.Rect(x, y, w, h)
        self.kind = kind

    def draw(self):
        if self.kind == "spikes":
            step = max(8, self.rect.width // 5)
            for x in range(self.rect.x, self.rect.x + self.rect.width, step):
                pygame.draw.polygon(screen, (180, 190, 205), [
                    (x, self.rect.bottom),
                    (x + step // 2, self.rect.top),
                    (x + step, self.rect.bottom),
                ])
        elif self.kind == "lava":
            pygame.draw.rect(screen, (255, 110, 40), self.rect)
            for offset in range(0, self.rect.width, 12):
                pygame.draw.rect(screen, (255, 180, 60), (self.rect.x + offset, self.rect.y + 4, 8, 8))
        elif self.kind == "barrier":
            pygame.draw.rect(screen, (90, 120, 140), self.rect)
            pygame.draw.rect(screen, (200, 220, 255), self.rect, 2)
        else:
            pygame.draw.rect(screen, (170, 170, 170), self.rect)

class Fan:
    def __init__(self, x, y, w=60, h=90, on=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.gust = pygame.Rect(x - 20, y - 130, w + 40, 150)
        self.on = on

    def draw(self):
        base_color = (120, 245, 255) if self.on else (100, 110, 130)
        pygame.draw.rect(screen, base_color, (self.rect.x + 10, self.rect.y + 22, self.rect.width - 20, self.rect.height - 26))
        pygame.draw.rect(screen, BLACK, (self.rect.x + 10, self.rect.y + 22, self.rect.width - 20, self.rect.height - 26), 2)
        for i in range(4):
            angle = i * (math.pi / 2)
            px = self.rect.centerx + math.cos(angle) * 12
            py = self.rect.centery + math.sin(angle) * 12
            pygame.draw.line(screen, (200, 240, 255), (self.rect.centerx, self.rect.centery), (px, py), 3)
        if self.on:
            gust_color = (160, 240, 255)
            pygame.draw.polygon(screen, gust_color, [
                (self.gust.left, self.gust.bottom - 20),
                (self.gust.centerx, self.gust.top),
                (self.gust.right, self.gust.bottom - 20),
            ])
            pygame.draw.rect(screen, (100, 180, 255), self.gust, 2)

class FanSwitch:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 18, 18)
        self.activated = False

    def draw(self):
        color = (255, 220, 90) if self.activated else (120, 110, 90)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

class PuzzleRoom:
    def __init__(self, difficulty, layout=None):
        self.difficulty = difficulty
        self.layout = layout
        self.platforms = []
        self.hazards = []
        self.fans = []
        self.switches = []
        self.goal = pygame.Rect(1200, 100, 30, 30)
        self.spawn = (80, 560)
        self.generate()

    def generate(self):
        self.platforms = [pygame.Rect(0, 650, 1600, 80)]

        if self.layout is not None:
            chosen = [pygame.Rect(*rect) for rect in self.layout]
            self.platforms += chosen
            self.goal = pygame.Rect(chosen[-1].x + max(10, chosen[-1].width // 2), chosen[-1].y - 60, 30, 30)
        else:
            chosen = random.choice(PUZZLE_PATTERNS.get(self.difficulty, PUZZLE_PATTERNS["easy"]))
            self.platforms += [pygame.Rect(*rect) for rect in chosen]
            self.goal = pygame.Rect(self.platforms[-1].x + max(10, self.platforms[-1].width // 2), self.platforms[-1].y - 60, 30, 30)

        hazard_specs = {
            "easy": [
                ("spikes", 0),
                ("lava", 1),
                ("spikes", 2),
            ],
            "medium": [
                ("spikes", 0),
                ("lava", 1),
                ("spikes", 2),
                ("lava", 3),
            ],
            "hard": [
                ("spikes", 0),
                ("lava", 1),
                ("spikes", 2),
                ("lava", 3),
                ("spikes", 4),
            ],
            "insane": [
                ("spikes", 0),
                ("lava", 1),
                ("spikes", 2),
                ("lava", 3),
                ("spikes", 4),
                ("lava", 5),
            ],
        }

        self.hazards = []
        platform_hazards = hazard_specs.get(self.difficulty, hazard_specs["easy"])
        for kind, idx in platform_hazards:
            if idx >= len(self.platforms[1:]):
                continue
            plat = self.platforms[1:][idx]
            if plat.width < 80:
                continue
            if kind == "spikes":
                w = max(30, int(plat.width * 0.45))
                x = plat.x + (plat.width - w) // 2
                self.hazards.append(Hazard(x, plat.y - 18, w, 18, "spikes"))
            else:
                w = max(26, int(plat.width * 0.32))
                x = plat.x + (plat.width - w) // 2
                self.hazards.append(Hazard(x, plat.y, w, max(20, plat.height), "lava"))

        self.spawn = (80, 560)

class Temple:
    def __init__(self, idx):
        self.idx = idx
        self.name = TEMPLE_NAMES[idx]
        self.bg = TEMPLE_BG[idx]
        self.platforms = []
        self.hazards = []
        self.enemies = []
        self.portal = None
        self.player_spawn = (90, 560)
        self.boss_kind = ["slime", "bat", "skeleton", "spider", "bee", "charger", "wisp", "golem"][idx]
        self.boss_spawn = (1040, 560)
        self.puzzle_plan = self.build_puzzle_plan()
        self.puzzles = []
        used_layouts = set()
        for difficulty in self.puzzle_plan:
            available = [pattern for pattern in PUZZLE_PATTERNS[difficulty] if tuple(tuple(p) for p in pattern) not in used_layouts]
            if not available:
                available = PUZZLE_PATTERNS[difficulty]
            chosen = random.choice(available)
            used_layouts.add(tuple(tuple(p) for p in chosen))
            self.puzzles.append(PuzzleRoom(difficulty, chosen))

        if self.idx == 0:
            first_room_layouts = [
                [(160, 610, 220, 18), (430, 540, 160, 18), (660, 470, 140, 18), (860, 390, 150, 18), (1090, 520, 200, 18), (1320, 450, 160, 18)],
                [(150, 620, 220, 18), (420, 555, 150, 18), (650, 485, 140, 18), (860, 415, 150, 18), (1080, 530, 200, 18), (1310, 460, 170, 18)],
                [(170, 610, 220, 18), (440, 545, 150, 18), (670, 470, 140, 18), (880, 400, 150, 18), (1100, 520, 200, 18), (1330, 450, 160, 18)],
                [(140, 620, 220, 18), (410, 550, 160, 18), (650, 480, 140, 18), (870, 410, 150, 18), (1090, 530, 200, 18), (1315, 460, 170, 18)],
            ]

            for i, room in enumerate(self.puzzles):
                room.layout = first_room_layouts[i % len(first_room_layouts)]
                room.generate()
                room.hazards = [Hazard(0, 660, 1600, 70, "lava")]
                room.fans = []
                room.switches = []

                if len(room.platforms) > 5:
                    switch_platform = room.platforms[2]
                    fan_platform = room.platforms[4]
                    room.platforms.remove(fan_platform)
                    fan = Fan(fan_platform.x + 24, fan_platform.y - 90, 52, 90, False)
                    switch = FanSwitch(switch_platform.x + max(10, switch_platform.width // 2 - 10), switch_platform.y - 18)
                    room.fans.append(fan)
                    room.switches.append(switch)

                    end_platform = room.platforms[-1]
                    room.goal = pygame.Rect(end_platform.x + max(10, end_platform.width // 2), end_platform.y - 60, 30, 30)
        self.setup()

    def spawn_wave(self):
        kind = self.boss_kind
        wave = []
        for i in range(10):
            x = 120 + (i % 5) * 200
            y = 200 + (i // 5) * 120
            wave.append(Enemy(kind, x, y))
        self.enemies = wave
        self.platforms = [pygame.Rect(0, 650, 1600, 80)]
        self.hazards = []
        self.portal = pygame.Rect(1200, 560, 52, 80)

    def get_wave_targets(self):
        return [self.boss_kind]

    def build_puzzle_plan(self):
        if self.idx == 0:
            return ["easy"] * 5
        if self.idx == 1:
            return ["easy", "easy", "medium", "medium", "medium"]
        if self.idx == 2:
            return ["easy", "easy", "medium", "medium", "hard"]
        if self.idx == 3:
            return ["easy", "medium", "hard", "hard", "insane"]
        if self.idx == 4:
            return ["easy", "medium", "hard", "insane", "hard"]
        return [random.choice(["easy", "medium", "hard", "insane"]) for _ in range(5)]

    def setup(self):
        self.platforms = self.puzzles[0].platforms
        self.hazards = self.puzzles[0].hazards
        self.fans = self.puzzles[0].fans
        self.switches = self.puzzles[0].switches
        self.portal = self.puzzles[0].goal
        self.player_spawn = self.puzzles[0].spawn
        self.enemies = []

class Game:
    def __init__(self):
        self.player = Player(100, 560)
        self.level_index = 0
        self.level = Temple(self.level_index)
        self.state = "title"
        self.player_projectiles = []
        self.enemy_projectiles = []
        self.final_victory = False
        self.death_timer = 0.0
        self.puzzle_index = 0
        self.current_puzzle = self.level.puzzles[0]
        self.level.platforms = self.current_puzzle.platforms
        self.level.hazards = self.current_puzzle.hazards
        self.level.fans = self.current_puzzle.fans
        self.level.switches = self.current_puzzle.switches
        self.level.portal = self.current_puzzle.goal
        self.player.x, self.player.y = self.current_puzzle.spawn

    def reset_level(self):
        self.level = Temple(self.level_index)
        self.player = Player(self.level.player_spawn[0], self.level.player_spawn[1])
        self.player.health = self.player.max_health
        self.player.invuln = 0
        self.player.attack_timer = 0.0
        self.player.attack_cooldown = 0.0
        self.player.projectile_cooldown = 0.0
        self.player.x, self.player.y = self.level.player_spawn
        self.player_projectiles = []
        self.enemy_projectiles = []
        self.state = "playing"
        self.death_timer = 0.0
        self.puzzle_index = 0
        self.current_puzzle = self.level.puzzles[0]
        self.level.platforms = self.current_puzzle.platforms
        self.level.hazards = self.current_puzzle.hazards
        self.level.fans = self.current_puzzle.fans
        self.level.switches = self.current_puzzle.switches
        self.level.portal = self.current_puzzle.goal
        self.player.x, self.player.y = self.current_puzzle.spawn

    def advance(self):
        self.level_index += 1
        if self.level_index >= len(TEMPLE_NAMES):
            self.state = "win"
            self.final_victory = True
        else:
            self.level = Temple(self.level_index)
            self.player.x, self.player.y = self.level.player_spawn
            self.player.health = self.player.max_health
            self.player.invuln = 0
            self.player.attack_timer = 0.0
            self.player.attack_cooldown = 0.0
            self.player.projectile_cooldown = 0.0
            self.player_projectiles = []
            self.enemy_projectiles = []
            self.state = "playing"
            self.puzzle_index = 0
            self.current_puzzle = self.level.puzzles[0]
            self.level.platforms = self.current_puzzle.platforms
            self.level.hazards = self.current_puzzle.hazards
            self.level.fans = self.current_puzzle.fans
            self.level.switches = self.current_puzzle.switches
            self.level.portal = self.current_puzzle.goal
            self.player.x, self.player.y = self.current_puzzle.spawn

    def update(self, dt):
        if self.state == "title":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                self.state = "playing"
            return

        if self.state == "win":
            return

        if self.state == "dead":
            self.death_timer -= dt
            if self.death_timer <= 0:
                self.reset_level()
            return

        if not self.level.enemies:
            self.player.handle_input(dt)
            self.player.update(dt, self.level.platforms)

            for switch in self.level.switches:
                if self.player.rect.colliderect(switch.rect):
                    switch.activated = True
                    for fan in self.level.fans:
                        fan.on = True

            for fan in self.level.fans:
                if fan.on and self.player.rect.colliderect(fan.gust):
                    self.player.vy = min(self.player.vy, -420)
                    self.player.y -= 2
                    self.player.on_ground = False

            for hazard in self.level.hazards:
                if self.player.rect.colliderect(hazard.rect):
                    if self.player.invuln <= 0:
                        if self.player.take_damage(999):
                            self.state = "dead"
                            self.death_timer = 0.75
                            return

            if self.level_index == 0:
                for switch in self.level.switches:
                    if switch.activated and self.player.rect.colliderect(self.level.portal):
                        self.puzzle_index += 1
                        if self.puzzle_index >= len(self.level.puzzles):
                            self.level.spawn_wave()
                            self.level.portal = pygame.Rect(1200, 560, 52, 80)
                            self.player.x, self.player.y = (80, 560)
                            self.player_projectiles = []
                            self.enemy_projectiles = []
                        else:
                            self.current_puzzle = self.level.puzzles[self.puzzle_index]
                            self.level.platforms = self.current_puzzle.platforms
                            self.level.hazards = self.current_puzzle.hazards
                            self.level.fans = self.current_puzzle.fans
                            self.level.switches = self.current_puzzle.switches
                            self.level.portal = self.current_puzzle.goal
                            self.player.x, self.player.y = self.current_puzzle.spawn
                            self.player_projectiles = []
                            self.enemy_projectiles = []
                        return

            if self.player.rect.colliderect(self.level.portal):
                self.puzzle_index += 1
                if self.puzzle_index >= len(self.level.puzzles):
                    self.level.spawn_wave()
                    self.level.portal = pygame.Rect(1200, 560, 52, 80)
                    self.player.x, self.player.y = (80, 560)
                    self.player_projectiles = []
                    self.enemy_projectiles = []
                else:
                    self.current_puzzle = self.level.puzzles[self.puzzle_index]
                    self.level.platforms = self.current_puzzle.platforms
                    self.level.hazards = self.current_puzzle.hazards
                    self.level.fans = self.current_puzzle.fans
                    self.level.switches = self.current_puzzle.switches
                    self.level.portal = self.current_puzzle.goal
                    self.player.x, self.player.y = self.current_puzzle.spawn
                    self.player_projectiles = []
                    self.enemy_projectiles = []
            return

        if self.level.portal == pygame.Rect(1200, 560, 52, 80) and self.level.enemies and all(enemy.dead for enemy in self.level.enemies):
            if self.level_index >= len(TEMPLE_NAMES) - 1:
                self.state = "win"
                self.final_victory = True
                return
            self.advance()
            return

        # controls
        self.player.handle_input(dt)
        self.player.update(dt, self.level.platforms)

        for switch in self.level.switches:
            if self.player.rect.colliderect(switch.rect):
                switch.activated = True
                for fan in self.level.fans:
                    fan.on = True

        for fan in self.level.fans:
            if fan.on and self.player.rect.colliderect(fan.gust):
                self.player.vy = min(self.player.vy, -420)
                self.player.y -= 2

        for hazard in self.level.hazards:
            if self.player.rect.colliderect(hazard.rect):
                if self.player.invuln <= 0:
                    if self.player.take_damage(999):
                        self.state = "dead"
                        self.death_timer = 0.75
                        return

        # player projectile firing
        if self.player.projectile_cooldown == 0 and pygame.key.get_pressed()[pygame.K_k]:
            self.player_projectiles.append(self.player.shoot())

        # melee attack
        if self.player.attack_timer > 0:
            attack_area = self.player.attack_rect()
            for enemy in self.level.enemies:
                if not enemy.dead and attack_area.colliderect(enemy.rect):
                    enemy.take_hit(self.player.attack_damage)

        # enemy movement
        for enemy in self.level.enemies:
            enemy.update(dt, self.player, self.level.platforms)

        # update player projectiles
        for proj in self.player_projectiles[:]:
            proj["x"] += proj["vx"] * dt
            proj["y"] += proj["vy"] * dt

            if proj["x"] < 0 or proj["x"] > W or proj["y"] < 0 or proj["y"] > H:
                if proj in self.player_projectiles:
                    self.player_projectiles.remove(proj)
                continue

            hit_enemy = False
            for enemy in self.level.enemies:
                if enemy.dead:
                    continue
                if pygame.Rect(proj["x"] - proj["r"], proj["y"] - proj["r"], proj["r"] * 2, proj["r"] * 2).colliderect(enemy.rect):
                    enemy.take_hit(proj["damage"])
                    hit_enemy = True
                    break

            if hit_enemy and proj in self.player_projectiles:
                self.player_projectiles.remove(proj)

        # enemy ranged attacks
        for enemy in self.level.enemies:
            if enemy.kind in ["eye", "wisp", "bat", "bee"]:
                if enemy.cooldown > 0:
                    enemy.cooldown -= dt
                elif enemy.rect.colliderect(self.player.rect.inflate(180, 120)):
                    self.enemy_projectiles.append(enemy.fire_projectile(self.player))
                    enemy.cooldown = 1.5

        # update enemy projectiles
        for proj in self.enemy_projectiles[:]:
            proj["x"] += proj["vx"] * dt
            proj["y"] += proj["vy"] * dt

            if proj["x"] < 0 or proj["x"] > W or proj["y"] < 0 or proj["y"] > H:
                if proj in self.enemy_projectiles:
                    self.enemy_projectiles.remove(proj)
                continue

            p_rect = pygame.Rect(proj["x"] - proj["r"], proj["y"] - proj["r"], proj["r"] * 2, proj["r"] * 2)
            if p_rect.colliderect(self.player.rect):
                if self.player.invuln <= 0:
                    if self.player.take_damage(proj["damage"]):
                        self.reset_level()
                if proj in self.enemy_projectiles:
                    self.enemy_projectiles.remove(proj)

        # lose condition
        if self.player.health <= 0 and self.state != "dead":
            self.state = "dead"
            self.death_timer = 0.75
            return

        # portal win
        if self.level.portal.colliderect(self.player.rect):
            alive = [e for e in self.level.enemies if not e.dead]
            if len(alive) == 0 and self.level_index < len(TEMPLE_NAMES) - 1:
                self.advance()

    def draw(self):
        screen.fill(self.level.bg)

        for p in self.level.platforms:
            pygame.draw.rect(screen, PLATFORM, p)
            pygame.draw.rect(screen, BLACK, p, 2)

        for switch in self.level.switches:
            switch.draw()

        for fan in self.level.fans:
            fan.draw()

        for hazard in self.level.hazards:
            hazard.draw()

        pygame.draw.ellipse(screen, GOLD, self.level.portal)
        pygame.draw.ellipse(screen, BLACK, self.level.portal, 3)

        for proj in self.player_projectiles:
            pygame.draw.circle(screen, proj["color"], (int(proj["x"]), int(proj["y"])), proj["r"])

        for proj in self.enemy_projectiles:
            pygame.draw.circle(screen, proj["color"], (int(proj["x"]), int(proj["y"])), proj["r"])

        for enemy in self.level.enemies:
            enemy.draw()

        self.player.draw()

        for i in range(self.player.max_health):
            heart_x = 30 + i * 30
            heart_color = RED if i < self.player.health else (90, 90, 90)
            pygame.draw.polygon(screen, heart_color, [
                (heart_x, 18), (heart_x + 8, 8), (heart_x + 16, 18),
                (heart_x + 24, 8), (heart_x + 32, 18), (heart_x + 16, 30)
            ])
        draw_text(f"Temple {self.level_index + 1}: {self.level.name}", 30, 45, GOLD, 26)

        if self.state == "title":
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            draw_text("Temple Runner", W // 2, H // 2 - 60, WHITE, 64, centered=True)
            draw_text("Press SPACE to Begin", W // 2, H // 2 + 10, WHITE, 32, centered=True)
            draw_text("Move: A/D or Arrows   Jump: W / Space   Attack: J   Shoot: K", W // 2, H // 2 + 60, WHITE, 22, centered=True)

        elif self.state == "win":
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            screen.blit(overlay, (0, 0))
            draw_text("Victory!", W // 2, H // 2 - 60, GOLD, 64, centered=True)
            draw_text(f"You cleared all {len(TEMPLE_NAMES)} temples.", W // 2, H // 2 + 10, WHITE, 28, centered=True)
            draw_text("Press R to restart", W // 2, H // 2 + 60, WHITE, 22, centered=True)
            if pygame.key.get_pressed()[pygame.K_r]:
                self.__init__()

        elif self.state == "dead":
            draw_text("You Died", W // 2, H // 2, RED, 48, centered=True)
            draw_text("Respawning...", W // 2, H // 2 + 52, WHITE, 26, centered=True)

        pygame.display.flip()

TEMPLE_NAMES = [
    "Temple of Roots",
    "Temple of Ember",
    "Temple of Echoes",
    "Temple of Iron",
    "Temple of the Sky",
    "Temple of Thorns",
    "Temple of Tides",
    "Temple of Eclipse",
]

TEMPLE_BG = [
    (55, 92, 66),
    (145, 72, 55),
    (74, 82, 122),
    (94, 98, 108),
    (70, 96, 130),
    (58, 82, 68),
    (58, 92, 122),
    (72, 62, 88),
]

game = Game()

running = True
while running:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game.state == "win":
            game = Game()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    if game.state != "win":
        game.update(dt)
    game.draw()

pygame.quit()