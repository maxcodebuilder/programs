import pygame, math, random, json

# --- Settings ---
WIDTH, HEIGHT = 950, 600
FPS = 60
PATH = [(0, 300), (200, 300), (200, 100), (500, 100), (500, 500), (750, 500)]
MAX_WAVE = 500
ULTIMATE_COST = 10000

# Weapon Database: Super Laser costs $99,999 and does 10,000 DMG
WEAPONS = {
    '1': {'name': 'Gun', 'cost': 30, 'base_dmg': 3, 'range': 120, 'color': (150, 150, 150)},
    '2': {'name': 'RPG', 'cost': 50, 'base_dmg': 5, 'range': 150, 'color': (50, 150, 50)},
    '3': {'name': 'Mini Laser', 'cost': 100, 'base_dmg': 10, 'range': 180, 'color': (0, 200, 255)},
    '4': {'name': 'Laser', 'cost': 500, 'base_dmg': 30, 'range': 220, 'color': (255, 0, 255)},
    '5': {'name': 'Missile', 'cost': 1000, 'base_dmg': 100, 'range': 300, 'color': (255, 100, 0)},
    '6': {'name': 'Super Laser', 'cost': 99999, 'base_dmg': 10000, 'range': 450, 'color': (255, 0, 0)},
}

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size=40):
        super().__init__(); self.timer, self.pos, self.size = 12, (x, y), size
    def draw(self, surf):
        if self.timer > 0:
            rad = (13 - self.timer) * (self.size // 10)
            pygame.draw.circle(surf, (255, 150, 0), self.pos, rad, 2); self.timer -= 1

class Enemy(pygame.sprite.Sprite):
    def __init__(self, hp, speed, is_boss=False, is_super=False):
        super().__init__(); self.is_boss, self.is_super = is_boss, is_super
        self.max_hp, self.health = hp, hp
        sz = 75 if is_super else 55 if is_boss else 25
        self.image = pygame.Surface((sz, sz))
        color = (180, 0, 255) if is_super else (255, 0, 0) if is_boss else (220, 20, 60)
        self.image.fill(color); self.path, self.speed, self.waypoint = PATH, speed, 0
        self.pos = pygame.math.Vector2(self.path[0]) # FIXED: Only take first point
        self.rect = self.image.get_rect(center=self.pos)
    def update(self):
        if self.waypoint < len(self.path) - 1:
            target = pygame.math.Vector2(self.path[self.waypoint + 1])
            dir_vec = target - self.pos
            if dir_vec.length() <= self.speed: self.waypoint += 1
            else: self.pos += dir_vec.normalize() * self.speed
            self.rect.center = (int(self.pos.x), int(self.pos.y)); return False
        return True
    def draw_health(self, surf, font):
        bar_w = self.rect.width * 1.2; ratio = max(0, self.health / self.max_hp)
        pygame.draw.rect(surf, (150, 0, 0), (self.rect.x, self.rect.y-12, bar_w, 6))
        pygame.draw.rect(surf, (0, 255, 0), (self.rect.x, self.rect.y-12, bar_w*ratio, 6))
        txt = font.render(f"{int(self.health)}", True, (255,255,255)); surf.blit(txt, (self.rect.x, self.rect.y-25))

class Gear(pygame.sprite.Sprite):
    def __init__(self, x, y, type_key):
        super().__init__(); self.type_key, self.level = type_key, 1; self.data = WEAPONS[type_key]
        self.rect = pygame.Rect(x-20, y-20, 40, 40); self.range, self.cooldown = self.data['range'], 0
    def update(self, enemies, bullets):
        if self.cooldown > 0: self.cooldown -= 1
        for e in enemies:
            if math.hypot(e.rect.centerx - self.rect.centerx, e.rect.centery - self.rect.centery) <= self.range and self.cooldown == 0:
                # DAMAGE DOUBLES PER INDIVIDUAL LEVEL
                dmg = self.data['base_dmg'] * (2 ** (self.level - 1))
                bullets.append(Bullet(self.rect.centerx, self.rect.centery, e, dmg, self.data['color']))
                self.cooldown = 8 if self.type_key == '6' else 15; break

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target, power, color):
        super().__init__(); self.target, self.speed, self.power, self.color = target, 25, power, color
        self.rect = pygame.Rect(x, y, 6, 6)
    def update(self, explosions):
        if not self.target.alive(): return True
        dir_vec = pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)
        if dir_vec.length() < 15: self.target.health -= self.power; explosions.append(Explosion(*self.rect.center, 20)); return True
        if dir_vec.length() > 0: self.rect.center += dir_vec.normalize() * self.speed; return False

def main():
    pygame.init(); screen = pygame.display.set_mode((WIDTH, HEIGHT)); clock = pygame.time.Clock()
    font, ui_f = pygame.font.SysFont("Consolas", 14, bold=True), pygame.font.SysFont("Consolas", 18, bold=True)
    gears, enemies, bullets, explosions = [], pygame.sprite.Group(), [], []
    gold, health, wave, spawned_count, spawning, selected_type = 1000, 10, 1, 0, False, '1'
    btn_rect = pygame.Rect(770, 500, 160, 45)

    while True:
        screen.fill((20, 20, 20)); pygame.draw.lines(screen, (40, 40, 40), False, PATH, 10)
        pygame.draw.rect(screen, (35, 35, 35), (750, 0, 200, 600))
        screen.blit(ui_f.render(f"GOLD: ${gold}  HP: {health}", True, (255, 255, 255)), (765, 20))
        screen.blit(ui_f.render(f"WAVE: {wave}/{MAX_WAVE}", True, (0, 255, 100)), (765, 50))
        for i, (k, v) in enumerate(WEAPONS.items()):
            if k == '6' and wave < 250: continue # UNLOCK AT W250
            c = (255, 255, 255) if selected_type == k else (80, 80, 80)
            screen.blit(ui_f.render(f"{k}:{v['name']} (${v['cost']})", True, c), (765, 100+i*55))

        if not spawning:
            pygame.draw.rect(screen, (0, 150, 0), btn_rect); screen.blit(ui_f.render("START WAVE", True, (255, 255, 255)), (790, 512))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.KEYDOWN:
                if event.unicode in WEAPONS: 
                    if event.unicode != '6' or wave >= 250: selected_type = event.unicode
                if event.key == pygame.K_SPACE and gold >= ULTIMATE_COST and wave >= 100:
                    for e in enemies: e.health = 0; gold -= ULTIMATE_COST
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # LEFT CLICK
                    if btn_rect.collidepoint(event.pos) and not spawning:
                        spawning, spawned_count = True, 0
                        if wave % 70 == 0 or wave == MAX_WAVE: # MISSILE FLEET
                            for _ in range(15): explosions.append(Explosion(random.randint(0,700), random.randint(0,600), 100))
                            for e in enemies: e.health = 0
                    elif event.pos[0] < 750: # FIXED COORDINATE TUPLE CHECK
                        # FIND IF CLICKING EXISTING GEAR
                        clicked = next((g for g in gears if g.rect.collidepoint(event.pos)), None)
                        if clicked:
                            if gold >= WEAPONS[clicked.type_key]['cost']:
                                clicked.level += 1; gold -= WEAPONS[clicked.type_key]['cost']
                        elif gold >= WEAPONS[selected_type]['cost']:
                            gears.append(Gear(event.pos[0], event.pos[1], selected_type)); gold -= WEAPONS[selected_type]['cost']
                elif event.button == 3: # RIGHT CLICK SELL
                    for g in gears:
                        if g.rect.collidepoint(event.pos): gold += int(WEAPONS[g.type_key]['cost'] * 0.7); gears.remove(g); break

        if spawning and random.random() < 0.05 and spawned_count < 10:
            is_sup, is_bos = (spawned_count == 9 and wave % 50 == 0), (spawned_count == 9 and wave % 10 == 0)
            hp = int(15 * (1.12 ** (wave-1)))
            if is_sup: hp *= 60 # SUPER BOSS 2X NORMAL BOSS
            elif is_bos: hp *= 30
            enemies.add(Enemy(hp, 2.2 if (is_bos or is_sup) else 2.8, is_bos, is_sup)); spawned_count += 1
        
        if spawning and len(enemies) == 0 and spawned_count >= 10: spawning, wave = False, wave + 1
        for e in enemies:
            if e.update(): health -= 1; e.kill()
            elif e.health <= 0: gold += int(30 * (1.07 ** (wave-1))); e.kill()

        for g in gears: 
            g.update(enemies, bullets); pygame.draw.circle(screen, g.data['color'], g.rect.center, 18)
            screen.blit(font.render(f"L{g.level}", True, (255, 255, 255)), (g.rect.centerx-10, g.rect.centery-8))
            
        bullets = [b for b in bullets if not b.update(explosions)]
        for b in bullets: pygame.draw.circle(screen, b.color, b.rect.center, 4)
        for e in enemies: screen.blit(e.image, e.rect); e.draw_health(screen, font)
        for ex in explosions: ex.draw(screen); explosions = [ex for ex in explosions if ex.timer > 0]
        if health <= 0 or wave > MAX_WAVE: return
        pygame.display.flip(); clock.tick(FPS)

if __name__ == "__main__": main()
