import pygame
import sys
import random
import json
import os
import time
import math

# Geometry Dash - Mini
# Features: auto-scroll, precise single jump, spikes and blocks, score (distance), best score saved.

WIDTH = 900
HEIGHT = 400
FPS = 60
GROUND_Y = HEIGHT - 80

PLAYER_SIZE = 36
PLAYER_X = 120

OBSTACLE_WIDTH = 30
# gameplay: how many jumps allowed before touching ground (2 = double-jump)
MAX_JUMPS = 2
# difficulty multiplier: >1 makes curve steeper (harder earlier), <1 makes it shallower
DIFFICULTY = 1.0
MIN_DIFFICULTY = 0.3
MAX_DIFFICULTY = 3.0
DIFF_STEP = 0.1
DIFF_MSG_DURATION = 1.6

SAVE_FILE = os.path.join(os.path.dirname(__file__), "geometry_save.json")

pygame.init()
pygame.font.init()
FONT = pygame.font.SysFont("Arial", 22)
FONT_BIG = pygame.font.SysFont("Arial", 56)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash - Mini")
clock = pygame.time.Clock()


class Player:
    def __init__(self):
        self.x = PLAYER_X
        self.y = GROUND_Y - PLAYER_SIZE
        self.w = PLAYER_SIZE
        self.h = PLAYER_SIZE
        self.vy = 0.0
        self.on_ground = True
        self.max_jumps = MAX_JUMPS
        self.jumps_left = self.max_jumps

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def jump(self):
        # allow jump if on ground or have jumps remaining (double-jump)
        if self.jumps_left > 0:
            # Geometry Dash feels snappy: a strong instant impulse
            self.vy = -13.5
            self.on_ground = False
            self.jumps_left -= 1

    def update(self, dt):
        # gravity
        self.vy += 35.0 * dt
        self.y += self.vy
        if self.y >= GROUND_Y - self.h:
            self.y = GROUND_Y - self.h
            self.vy = 0.0
            # landed: reset jumps
            self.on_ground = True
            self.jumps_left = self.max_jumps


class Obstacle:
    def __init__(self, x, w, h):
        self.x = x
        self.w = w
        self.h = h
        self.y = GROUND_Y - h

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)


class Level:
    def __init__(self, seed=0):
        # deterministic level generation using a fixed seed so the level
        # is the same every time for the same seed.
        self.seed = seed
        self.objects = []  # list of (x, type, w, h)
        self.length = 0
        self._make_pattern()

    def _make_pattern(self):
        rng = random.Random(self.seed)
        x = WIDTH + 200
        # Add a sequence of patterns with a difficulty curve: easier at start (bigger gaps,
        # fewer clusters, shorter obstacles) and harder toward the end.
        sections = 50
        for section in range(sections):
            t = section / max(1, sections - 1)  # 0..1 progression through level
            # adjust progression by global difficulty multiplier
            t_adj = min(1.0, t * DIFFICULTY)
            # gaps shrink as t increases (start easier -> larger gaps)
            min_gap = max(120, int(320 - 160 * t_adj))
            max_gap = max(180, int(520 - 340 * t_adj))
            gap = rng.randint(min_gap, max_gap)

            # cluster chance increases with adjusted t
            cluster_chance = 0.08 + 0.5 * t_adj
            if rng.random() < cluster_chance:
                # cluster of spikes/blocks; early clusters are smaller
                cluster_count = rng.randint(1, 2 + int(2 * t_adj))
                for i in range(cluster_count):
                    h = rng.randint(24, 60 + int(40 * t_adj))
                    self.objects.append((x + i * (OBSTACLE_WIDTH + 8), 'block', OBSTACLE_WIDTH, h))
                x += gap
            else:
                # single block, height grows slightly with t_adj
                h = rng.randint(24, 60 + int(40 * t_adj))
                self.objects.append((x, 'block', OBSTACLE_WIDTH, h))
                x += gap

        self.length = x


def draw_text(surf, txt, x, y, color=(255, 255, 255)):
    img = FONT.render(txt, True, color)
    surf.blit(img, (x, y))


def difficulty_label(d: float) -> str:
    """Return a Geometry Dash-style difficulty label for a numeric difficulty."""
    if d <= 0.5:
        return "Easy"
    if d <= 1.0:
        return "Normal"
    if d <= 1.5:
        return "Hard"
    if d <= 2.0:
        return "Harder"
    if d <= 2.5:
        return "Insane"
    return "Demon"


def difficulty_color(d: float):
    # map difficulty to an attention-grabbing color
    if d <= 0.5:
        return (90, 200, 120)  # green
    if d <= 1.0:
        return (120, 180, 240)  # blue
    if d <= 1.5:
        return (255, 200, 60)  # yellow
    if d <= 2.0:
        return (255, 140, 40)  # orange
    if d <= 2.5:
        return (220, 80, 120)  # purple/pink
    return (220, 40, 40)  # red (demon)


def save_best(best):
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump({'best': best}, f)
    except Exception:
        pass


def load_best():
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('best', 0)
    except Exception:
        pass
    return 0


def main():
    # fixed level seeds - reproducible levels. Choose index to play a level.
    LEVEL_SEEDS = [42, 1234, 9999]
    level_index = 0
    player = Player()
    level = Level(seed=LEVEL_SEEDS[level_index])
    obstacles = [Obstacle(x, w, h) for (x, t, w, h) in level.objects]
    diff_msg = None
    diff_msg_time = 0.0

    scroll = 0.0
    # start a bit slower so early sections feel easier
    speed = 260.0  # horizontal scroll speed (px/s)
    running = True
    game_over = False
    start_time = time.time()
    score = 0.0
    best = load_best()

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if game_over:
                        # restart same level
                        player = Player()
                        level = Level(seed=LEVEL_SEEDS[level_index])
                        obstacles = [Obstacle(x, w, h) for (x, t, w, h) in level.objects]
                        scroll = 0.0
                        start_time = time.time()
                        score = 0.0
                        game_over = False
                    else:
                        player.jump()
                elif event.key == pygame.K_r:
                    # restart
                    player = Player()
                    level = Level(seed=LEVEL_SEEDS[level_index])
                    obstacles = [Obstacle(x, w, h) for (x, t, w, h) in level.objects]
                    scroll = 0.0
                    start_time = time.time()
                    score = 0.0
                    game_over = False
                # level select keys 1..N
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    sel = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}[event.key]
                    if sel < len(LEVEL_SEEDS):
                        level_index = sel
                        # restart at selected level
                        player = Player()
                        level = Level(seed=LEVEL_SEEDS[level_index])
                        obstacles = [Obstacle(x, w, h) for (x, t, w, h) in level.objects]
                        scroll = 0.0
                        start_time = time.time()
                        score = 0.0
                        game_over = False
                elif event.key == pygame.K_ESCAPE:
                    running = False
                # difficulty controls (bracket keys)
                elif event.key == pygame.K_LEFTBRACKET:
                    DIFF = max(MIN_DIFFICULTY, DIFFICULTY - DIFF_STEP)
                    globals()['DIFFICULTY'] = DIFF
                    # regenerate level with same seed to reflect new difficulty curve
                    level = Level(seed=LEVEL_SEEDS[level_index])
                    obstacles = [Obstacle(x, w, h) for (x, t, w, h) in level.objects]
                    scroll = 0.0
                    start_time = time.time()
                    score = 0.0
                    game_over = False
                    # visual feedback
                    diff_msg = f"Difficulty: {difficulty_label(DIFF)} ({DIFF:.1f})"
                    diff_msg_time = time.time()
                elif event.key == pygame.K_RIGHTBRACKET:
                    DIFF = min(MAX_DIFFICULTY, DIFFICULTY + DIFF_STEP)
                    globals()['DIFFICULTY'] = DIFF
                    level = Level(seed=LEVEL_SEEDS[level_index])
                    obstacles = [Obstacle(x, w, h) for (x, t, w, h) in level.objects]
                    scroll = 0.0
                    start_time = time.time()
                    score = 0.0
                    game_over = False
                    diff_msg = f"Difficulty: {difficulty_label(DIFF)} ({DIFF:.1f})"
                    diff_msg_time = time.time()

        if not game_over:
            # update player
            player.update(dt)

            # scroll level
            scroll += speed * dt

            # update obstacle positions implicitly by scroll
            # check collisions
            pr = player.rect()
            for o in obstacles:
                ox = o.x - scroll
                if ox + o.w < -100:
                    continue
                rect = pygame.Rect(int(ox), int(o.y), o.w, o.h)
                if pr.colliderect(rect):
                    game_over = True
                    best = max(best, int(score))
                    save_best(best)
                    break

            # update score
            score = (time.time() - start_time) * 10.0  # scale to make score increase faster
            # gradually increase speed more strongly as you progress; scale with DIFFICULTY
            speed = 260.0 + score * (3.0 * DIFFICULTY)

        # draw
        screen.fill((30, 30, 30))

        # background decor (parallax dots)
        for i in range(20):
            pygame.draw.circle(screen, (50, 50, 60), ((i * 73 - int(scroll * 0.2)) % WIDTH, 60 + (i % 3) * 20), 3)

        # ground
        pygame.draw.rect(screen, (40, 40, 40), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))

        # draw obstacles
        for o in obstacles:
            ox = o.x - scroll
            if ox < -200 or ox > WIDTH + 200:
                continue
            pygame.draw.rect(screen, (200, 30, 30), (int(ox), int(o.y), o.w, o.h))
            # draw spike top for visual
            pygame.draw.polygon(screen, (150, 10, 10), [(int(ox), int(o.y)), (int(ox + o.w / 2), int(o.y - 12)), (int(ox + o.w), int(o.y))])

        # player
        pygame.draw.rect(screen, (60, 200, 240), player.rect())

        # HUD
        draw_text(screen, f"Score: {int(score)}", 12, 12)
        draw_text(screen, f"Best: {best}", 12, 38)
        draw_text(screen, f"Difficulty: {DIFFICULTY:.1f}  ( [ / ] to change )", 12, 64)
        draw_text(screen, "Space/Up: jump  R: restart  Esc: quit", 12, 90)

        # difficulty/progress bar (shows how far through level and relative difficulty)
        prog = min(1.0, scroll / max(1.0, level.length))
        bar_w = int((WIDTH - 24) * prog)
        pygame.draw.rect(screen, (80, 80, 80), (12, HEIGHT - 28, WIDTH - 24, 12))
        pygame.draw.rect(screen, (200, 120, 40), (12, HEIGHT - 28, bar_w, 12))

        if game_over:
            draw_text(screen, "GAME OVER - Press Space or R to restart", WIDTH // 2 - 200, HEIGHT // 2 - 10, (240, 80, 80))

        # show transient difficulty message when changed (bigger, colored, pulsing)
        if diff_msg is not None:
            elapsed = time.time() - diff_msg_time
            if elapsed < DIFF_MSG_DURATION:
                fade = 1.0 - (elapsed / DIFF_MSG_DURATION)
                # pulsing scale that damps as message ages
                pulse = 1.0 + 0.25 * math.sin(elapsed * 8.0)
                scale = 1.0 + (pulse - 1.0) * fade
                # choose a color based on current numeric DIFFICULTY
                color = difficulty_color(DIFFICULTY)

                surf = FONT_BIG.render(diff_msg, True, color)
                sw, sh = surf.get_size()
                sw2 = max(1, int(sw * scale))
                sh2 = max(1, int(sh * scale))
                try:
                    surf2 = pygame.transform.smoothscale(surf, (sw2, sh2))
                except Exception:
                    surf2 = surf

                # shadow/background for contrast
                bx = WIDTH // 2 - sw2 // 2 - 12
                by = HEIGHT // 2 - 60 - 8
                pygame.draw.rect(screen, (10, 10, 10), (bx, by, sw2 + 24, sh2 + 16))

                # apply fade alpha
                alpha = int(255 * fade)
                try:
                    surf2.set_alpha(alpha)
                except Exception:
                    pass

                screen.blit(surf2, (WIDTH // 2 - sw2 // 2, HEIGHT // 2 - 60))
            else:
                diff_msg = None

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
