#!/usr/bin/env python3
"""Popcorn - a small Pygame remake of the Google Popcorn Doodle.

Click kernels to pop them into popcorn. Score as many as you can
before the timer runs out. High score is saved to popcorn_save.json.
"""
import json
import os
import random
import sys
import time
import math
import wave
import struct

try:
    import pygame
except Exception:
    print("This game requires pygame. Install with: pip install pygame")
    sys.exit(1)

SAVE_FILE = os.path.join(os.path.dirname(__file__), "popcorn_save.json")


def load_high_score():
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return int(data.get("high_score", 0))
    except Exception:
        return 0


def save_high_score(score):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump({"high_score": int(score)}, f)
    except Exception:
        pass


def _ensure_sound(path, samples, framerate=44100):
    """Write a WAV file at path if it doesn't exist using provided samples (float -1..1)."""
    if os.path.exists(path):
        return
    try:
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(framerate)
            frames = b"".join(struct.pack('<h', int(max(-1, min(1, s)) * 32767)) for s in samples)
            wf.writeframes(frames)
    except Exception:
        pass


def generate_sound_files(base_dir):
    pop_path = os.path.join(base_dir, "pop.wav")
    sizzle_path = os.path.join(base_dir, "sizzle.wav")

    # simple pop: short decaying sine + harmonic
    sr = 44100
    pop_len = int(0.08 * sr)
    pop_samples = []
    for i in range(pop_len):
        t = i / sr
        env = (1.0 - t / 0.08) ** 2
        val = 0.6 * math.sin(2 * math.pi * 1200 * t) + 0.4 * math.sin(2 * math.pi * 2200 * t)
        pop_samples.append(val * env)

    # sizzle: filtered noise with slow decay (loopable)
    sizzle_len = int(0.6 * sr)
    sizzle_samples = []
    for i in range(sizzle_len):
        t = i / sr
        env = 0.6 + 0.4 * math.sin(2 * math.pi * t / 0.6)
        # layered noise
        n = (random.uniform(-1, 1) * 0.6 + random.uniform(-1, 1) * 0.3)
        sizzle_samples.append(n * 0.12 * env)

    _ensure_sound(pop_path, pop_samples, sr)
    _ensure_sound(sizzle_path, sizzle_samples, sr)
    return pop_path, sizzle_path


class Kernel:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(8, 12)
        self.popped = False
        self.vx = random.uniform(-0.6, 0.6)
        self.vy = -random.uniform(1.0, 2.4)
        self.age = 0.0

    def draw(self, surf):
        color = (139, 69, 19)  # brown kernel
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.radius)

    def collide_point(self, px, py):
        return (self.x - px) ** 2 + (self.y - py) ** 2 <= (self.radius) ** 2


class Popcorn:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = -6 + random.uniform(-1.5, 1.5)
        self.vx = random.uniform(-1.0, 1.0)
        self.life = 2.0
        self.radius = random.randint(10, 16)
        self.rotation = random.uniform(-360, 360)
        self.growth = 0.0

    def update(self, dt):
        self.vy += 9.8 * dt  # gravity
        self.x += self.vx
        self.y += self.vy * dt * 60
        self.life -= dt

    def draw(self, surf):
        alpha = max(0, min(255, int(255 * (self.life / 2.0))))
        color = (255, 250, 240)
        r = int(self.radius * (1.0 + (0.5 - self.life / 4.0)))
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color + (alpha,), (r, r), r)
        rotated = pygame.transform.rotate(s, self.rotation * (1 - self.life / 2.0))
        surf.blit(rotated, (int(self.x - rotated.get_width() / 2), int(self.y - rotated.get_height() / 2)))


def run_game():
    pygame.init()
    try:
        pygame.mixer.init(frequency=44100)
    except Exception:
        pass
    WIDTH, HEIGHT = 640, 480
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Popcorn")
    clock = pygame.time.Clock()

    FONT = pygame.font.SysFont(None, 28)
    BIG = pygame.font.SysFont(None, 48)

    kernels = []
    popcorns = []

    spawn_timer = 0.0
    spawn_interval = 0.35
    duration = 30.0
    start_time = time.time()
    score = 0
    high_score = load_high_score()

    # Pan area
    pan_center = (WIDTH // 2, HEIGHT - 70)
    pan_radius = 160
    heating = False
    heat = 0.0
    heat_max = 1.0
    heat_rate_up = 0.9
    heat_rate_down = 0.5
    tilt = 0.0

    # start menu
    show_menu = True

    # ensure sound files exist and load sounds
    base_dir = os.path.dirname(__file__)
    try:
        pop_file, sizzle_file = generate_sound_files(base_dir)
        pop_sound = pygame.mixer.Sound(pop_file)
        sizzle_sound = pygame.mixer.Sound(sizzle_file)
        sizzle_sound.set_volume(0.35)
        sizzle_channel = None
    except Exception:
        pop_sound = None
        sizzle_sound = None
        sizzle_channel = None

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        elapsed = time.time() - start_time
        remaining = max(0.0, duration - elapsed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    heating = True
                if event.key == pygame.K_p:
                    # pop nearest kernel to pan center
                    if kernels:
                        px, py = pan_center
                        nearest = min(kernels, key=lambda k: (k.x - px) ** 2 + (k.y - py) ** 2)
                        if not nearest.popped:
                            nearest.popped = True
                            score += 1
                            for _ in range(random.randint(3, 5)):
                                popcorns.append(Popcorn(nearest.x, nearest.y))
                            if pop_sound:
                                pop_sound.play()
                if show_menu and event.key == pygame.K_RETURN:
                    show_menu = False
                    start_time = time.time()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if show_menu:
                    show_menu = False
                    start_time = time.time()
                else:
                    # click on pan to heat
                    dx = mx - pan_center[0]
                    dy = my - pan_center[1]
                    if dx * dx + dy * dy <= pan_radius * pan_radius:
                        heating = True
                    # check kernels in reverse so top-most are popped first
                    for k in reversed(kernels):
                        if not k.popped and k.collide_point(mx, my):
                            k.popped = True
                            score += 1
                            for _ in range(random.randint(3, 5)):
                                popcorns.append(Popcorn(k.x, k.y))
                            if pop_sound:
                                pop_sound.play()
                            break
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                heating = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    heating = False
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                tilt = max(-1.0, min(1.0, (mx - pan_center[0]) / float(pan_radius)))

        # spawn kernels inside pan area
        spawn_timer += dt
        if spawn_timer >= spawn_interval and not show_menu:
            spawn_timer = 0.0
            spawn_interval = random.uniform(0.25, 0.6)
            angle = random.uniform(0, 2 * 3.1415)
            r = random.uniform(20, pan_radius - 20)
            x = pan_center[0] + r * math.cos(angle)
            y = pan_center[1] + r * math.sin(angle)
            kernels.append(Kernel(x, y))

        # update popcorns
        for p in popcorns[:]:
            p.update(dt)
            if p.life <= 0 or p.y > HEIGHT + 50:
                popcorns.remove(p)

        # update heat (heating increases, otherwise cools)
        if heating:
            heat = min(heat_max, heat + heat_rate_up * dt)
        else:
            heat = max(0.0, heat - heat_rate_down * dt)

        # update kernels physics and pop if conditions met (heat + tilt influence)
        for k in kernels:
            if not k.popped:
                k.age += dt
                # heat applies upward impulse gradually
                if heating:
                    k.vy -= 0.08 * (1.0 + heat)
                # tilt nudges kernels sideways while in pan
                k.vx += tilt * 0.01
                k.vy += 9.8 * dt
                k.x += k.vx * dt * 60
                k.y += k.vy * dt * 60

                # pop conditions: high upward velocity or reach near top of pan + heat chance
                pop_height = pan_center[1] - pan_radius * 0.55
                upward_strong = k.vy < -3.0
                heat_chance = random.random() < (heat * 0.03)
                if (k.y < pop_height and (upward_strong or heat_chance)):
                    k.popped = True
                    score += 1
                    for _ in range(random.randint(3, 6)):
                        popcorns.append(Popcorn(k.x + random.uniform(-6, 6), k.y + random.uniform(-6, 6)))
                    if pop_sound:
                        pop_sound.play()

        # remove kernels that popped and are off-screen
        kernels = [k for k in kernels if not (k.popped and k.y > HEIGHT + 50)][:140]

        # draw
        screen.fill((20, 24, 30))

        # background decorations
        for i in range(6):
            pygame.draw.rect(screen, (25 + i * 2, 28 + i * 2, 32 + i * 2), (0, i * 30, WIDTH, 30), 0)

        # pan
        pygame.draw.circle(screen, (60, 60, 70), pan_center, pan_radius + 20)
        pygame.draw.circle(screen, (40, 40, 48), pan_center, pan_radius)
        # highlight when heating
        if heating:
            pygame.draw.circle(screen, (255, 120, 30), pan_center, pan_radius, 6)
            # start sizzle sound
            try:
                if sizzle_sound and (sizzle_channel is None or not sizzle_channel.get_busy()):
                    sizzle_channel = sizzle_sound.play(-1)
            except Exception:
                pass
        else:
            pygame.draw.circle(screen, (0, 0, 0), pan_center, pan_radius, 6)
            # stop sizzle sound
            try:
                if sizzle_channel is not None and sizzle_channel.get_busy():
                    sizzle_channel.stop()
                    sizzle_channel = None
            except Exception:
                pass

        # ground
        pygame.draw.rect(screen, (18, 18, 18), (0, HEIGHT - 40, WIDTH, 40))

        for k in kernels:
            if not k.popped:
                k.draw(screen)

        for p in popcorns:
            p.draw(screen)

        # draw heat meter
        meter_w = 200
        meter_h = 12
        mx = WIDTH//2 - meter_w//2
        my = HEIGHT - 20
        pygame.draw.rect(screen, (50, 50, 50), (mx, my, meter_w, meter_h))
        inner_w = int(meter_w * (heat / heat_max))
        pygame.draw.rect(screen, (255, 100, 30), (mx, my, inner_w, meter_h))
        hm = FONT.render("Heat", True, (220,220,220))
        screen.blit(hm, (mx - 50, my - 2))

        score_s = FONT.render(f"Score: {score}", True, (240, 240, 240))
        time_s = FONT.render(f"Time: {int(remaining)}", True, (240, 240, 240))
        high_s = FONT.render(f"High: {high_score}", True, (255, 215, 0))

        screen.blit(score_s, (10, 10))
        screen.blit(time_s, (10, 40))
        screen.blit(high_s, (WIDTH - 140, 10))

        if show_menu:
            title = BIG.render("Popcorn", True, (255, 230, 120))
            inst = FONT.render("Click or press Enter to start. Hold Space or click pan to heat.", True, (220, 220, 220))
            screen.blit(title, (WIDTH/2 - title.get_width()/2, HEIGHT/2 - 80))
            screen.blit(inst, (WIDTH/2 - inst.get_width()/2, HEIGHT/2))
            pygame.display.flip()
            continue

        if remaining <= 0:
            # game over screen
            over = BIG.render("Time's up!", True, (255, 200, 0))
            sub = FONT.render(f"Final score: {score}", True, (255, 255, 255))
            screen.blit(over, (WIDTH/2 - over.get_width()/2, HEIGHT/2 - 60))
            screen.blit(sub, (WIDTH/2 - sub.get_width()/2, HEIGHT/2))
            pygame.display.flip()
            if score > high_score:
                save_high_score(score)
            # wait for a key or mouse to quit or restart
            waiting = True
            while waiting:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        waiting = False
                        running = False
                    elif ev.type == pygame.KEYDOWN or (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1):
                        waiting = False
                clock.tick(30)
            # exit after one round
            running = False

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run_game()