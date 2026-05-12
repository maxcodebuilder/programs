import pygame
import math
import random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, waypoints, speed=2):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self._draw_enemy_sprite()
        self.rect = self.image.get_rect()
        self.waypoints = waypoints
        self.target_waypoint = 0
        self.pos = pygame.Vector2(waypoints[0])
        self.rect.center = self.pos
        self.speed = speed
        self.attacking = False

    def _draw_enemy_sprite(self):
        self.image.fill((0, 0, 0, 0))
        body_rect = pygame.Rect(0, 10, 40, 30)
        pygame.draw.ellipse(self.image, (200, 30, 30), body_rect)
        foot_color = (180, 20, 20)
        for i in range(4):
            foot_x = 4 + i * 9
            pygame.draw.ellipse(self.image, foot_color, (foot_x, 28, 10, 10))
        eye_y = 14
        pygame.draw.circle(self.image, (255, 255, 255), (13, eye_y), 7)
        pygame.draw.circle(self.image, (255, 255, 255), (27, eye_y), 7)
        pygame.draw.circle(self.image, (30, 30, 30), (13, eye_y), 3)
        pygame.draw.circle(self.image, (30, 30, 30), (27, eye_y), 3)
        pygame.draw.arc(self.image, (30, 30, 30), (12, 18, 16, 16), 3.14, 0, 2)

    def update(self):
        if self.target_waypoint < len(self.waypoints):
            target = pygame.Vector2(self.waypoints[self.target_waypoint])
            move_vec = target - self.pos
            if move_vec.length() > self.speed:
                move_vec.scale_to_length(self.speed)
                self.pos += move_vec
            else:
                self.target_waypoint += 1
            self.rect.center = self.pos
        else:
            self.attacking = True
            self.pos = pygame.Vector2(self.waypoints[-1])
            self.rect.center = self.pos


class Missile(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, damage_level=0):
        super().__init__()
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 200, 0), (4, 4), 4)
        self.rect = self.image.get_rect(center=start_pos)
        self.pos = pygame.Vector2(start_pos)
        self.target = pygame.Vector2(target_pos)
        self.speed = 6
        self.exploded = False
        self.explosion_radius = 10 + damage_level * 2
        self.life_timer = 0

    def update(self):
        if self.exploded:
            self.life_timer += 1
            if self.life_timer >= 10:
                self.kill()
            return

        direction = self.target - self.pos
        if direction.length() <= self.speed or self.life_timer >= 90:
            self._explode()
            return

        direction.scale_to_length(self.speed)
        self.pos += direction
        self.rect.center = self.pos
        self.life_timer += 1

    def _explode(self):
        self.exploded = True
        self.life_timer = 0
        self.image = pygame.Surface((self.explosion_radius * 2, self.explosion_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 140, 0, 180), (self.explosion_radius, self.explosion_radius), self.explosion_radius)
        self.rect = self.image.get_rect(center=self.pos)


def draw_start_screen(screen, font):
    screen.fill((0, 0, 0))
    title_text = font.render("Gear Defenders", True, (255, 255, 255))
    button_text = font.render("Start", True, (0, 0, 0))
    button_rect = pygame.Rect(300, 260, 200, 80)

    pygame.draw.rect(screen, (0, 255, 0), button_rect)
    screen.blit(title_text, title_text.get_rect(center=(400, 180)))
    screen.blit(button_text, button_text.get_rect(center=button_rect.center))
    pygame.display.flip()
    return button_rect


def get_turret_positions(base_rect, turret_count):
    positions = []
    offsets = [
        (base_rect.left + 10, base_rect.top + 10),
        (base_rect.right - 10, base_rect.top + 10),
        (base_rect.left + 10, base_rect.bottom - 10),
        (base_rect.right - 10, base_rect.bottom - 10),
        (base_rect.centerx, base_rect.top + 10),
        (base_rect.centerx, base_rect.bottom - 10),
        (base_rect.left + 10, base_rect.centery),
        (base_rect.right - 10, base_rect.centery)
    ]
    return offsets[:turret_count]


def draw_upgrade_panel(screen, font, credits, speed_level, damage_level, turret_level, base_level):
    panel_x = 580
    panel_y = 20
    panel_w = 200
    pygame.draw.rect(screen, (40, 40, 40), (panel_x, panel_y, panel_w, 280))
    pygame.draw.rect(screen, (120, 120, 120), (panel_x, panel_y, panel_w, 30))
    title = font.render("Upgrades", True, (255, 255, 255))
    screen.blit(title, (panel_x + 10, panel_y + 2))

    small = pygame.font.Font(None, 28)
    options = [
        (f"Speed Lv {speed_level}", f"Cost: {50 + speed_level * 30}", (panel_x + 10, panel_y + 50)),
        (f"Damage Lv {damage_level}", f"Cost: {80 + damage_level * 40}", (panel_x + 10, panel_y + 100)),
        (f"Turrets {4 + turret_level}", f"Cost: {100 + turret_level * 50}", (panel_x + 10, panel_y + 150)),
        (f"Base Lv {base_level}", f"Cost: {70 + base_level * 40}", (panel_x + 10, panel_y + 200))
    ]
    button_rects = []
    for idx, (text, cost_text, pos) in enumerate(options):
        label = small.render(text, True, (255, 255, 255))
        cost = small.render(cost_text, True, (200, 200, 0))
        rect = pygame.Rect(panel_x + 10, pos[1], panel_w - 20, 36)
        pygame.draw.rect(screen, (70, 70, 70), rect)
        screen.blit(label, (rect.x + 5, rect.y + 3))
        screen.blit(cost, (rect.x + 5, rect.y + 18))
        button_rects.append(rect)
    credits_text = small.render(f"Credits: {credits}", True, (255, 255, 255))
    screen.blit(credits_text, (panel_x + 10, panel_y + 250))
    return button_rects


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Gear Defenders")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 48)

    button_rect = draw_start_screen(screen, font)
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    waiting = False
        clock.tick(30)

    enemy_group = pygame.sprite.Group()
    missile_group = pygame.sprite.Group()
    spawn_points = [(-40, 100), (-40, 300), (-40, 500), (840, 100), (840, 300), (840, 500), (100, -40), (400, -40), (700, -40), (100, 640), (400, 640), (700, 640)]
    base_rect = pygame.Rect(360, 260, 80, 80)
    turret_level = 0
    speed_level = 0
    damage_level = 0
    base_level = 0
    base_health = 1000
    spawn_timer = 0
    spawn_interval = 20
    fire_timer = 0
    missiles_fired = 0
    minute_timer = 0
    attack_timer = 0
    credits = 0
    kill_count = 0
    monster_strength = 0
    fire_interval = max(1, int(60 * 60 / 50 * (0.9 ** speed_level)))
    turret_positions = get_turret_positions(base_rect, 4 + turret_level)

    for _ in range(6):
        start = random.choice(spawn_points)
        enemy_group.add(Enemy([start, base_rect.center], speed=2 + monster_strength * 0.5))

    running = True
    upgrade_buttons = []
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button_index, button_rect in enumerate(upgrade_buttons):
                    if button_rect.collidepoint(event.pos):
                        if button_index == 0:
                            cost = 50 + speed_level * 30
                            if credits >= cost:
                                credits -= cost
                                speed_level += 1
                                fire_interval = max(1, int(60 * 60 / 50 * (0.9 ** speed_level)))
                        elif button_index == 1:
                            cost = 80 + damage_level * 40
                            if credits >= cost:
                                credits -= cost
                                damage_level += 1
                        elif button_index == 2:
                            cost = 100 + turret_level * 50
                            if credits >= cost and turret_level < 4:
                                credits -= cost
                                turret_level += 1
                                turret_positions = get_turret_positions(base_rect, 4 + turret_level)
                        elif button_index == 3:
                            cost = 70 + base_level * 40
                            if credits >= cost:
                                credits -= cost
                                base_level += 1
                                base_health += 200

        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            spawn_timer = 0
            start = random.choice(spawn_points)
            enemy_group.add(Enemy([start, base_rect.center], speed=2 + monster_strength * 0.5))

        minute_timer += 1
        attack_timer += 1
        fire_timer += 1
        if missiles_fired < 50 and fire_timer >= fire_interval:
            fire_timer = 0
            missiles_fired += 1
            turret_pos = random.choice(turret_positions)
            if enemy_group:
                target_enemy = random.choice(enemy_group.sprites())
                missile_group.add(Missile(turret_pos, target_enemy.pos, damage_level))
            else:
                target = (random.randint(0, 800), random.randint(0, 600))
                missile_group.add(Missile(turret_pos, target, damage_level))
            attack_timer = 0
            attacking_enemies = [enemy for enemy in enemy_group if base_rect.collidepoint(enemy.pos)]
            base_health -= len(attacking_enemies)

        enemy_group.update()
        missile_group.update()

        for missile in list(missile_group):
            if missile.exploded:
                for enemy in list(enemy_group):
                    if missile.pos.distance_to(enemy.pos) <= missile.explosion_radius:
                        enemy.kill()
                        credits += 10
                        kill_count += 1
                        if kill_count % 100 == 0:
                            monster_strength += 1
                            for existing_enemy in enemy_group.sprites():
                                existing_enemy.speed = 2 + monster_strength * 0.5

        for enemy in enemy_group.sprites():
            if base_rect.collidepoint(enemy.pos):
                enemy.attacking = True

        screen.fill((30, 30, 30))
        pygame.draw.rect(screen, (80, 180, 80), base_rect)
        for turret_pos in turret_positions:
            pygame.draw.circle(screen, (100, 100, 100), turret_pos, 8)
            pygame.draw.circle(screen, (200, 200, 200), turret_pos, 4)

        enemy_group.draw(screen)
        missile_group.draw(screen)

        upgrade_buttons = draw_upgrade_panel(screen, font, credits, speed_level, damage_level, turret_level, base_level)

        health_text = font.render(f"Base Health: {base_health}", True, (255, 255, 255))
        missiles_text = font.render(f"Missiles: {missiles_fired}/50", True, (255, 255, 255))
        kills_text = font.render(f"Kills: {kill_count}", True, (255, 255, 255))
        credits_text = font.render(f"Credits: {credits}", True, (255, 255, 255))
        screen.blit(health_text, (10, 10))
        screen.blit(missiles_text, (10, 40))
        screen.blit(kills_text, (10, 70))
        screen.blit(credits_text, (10, 100))

        if base_health <= 0:
            game_over_text = font.render("Base Destroyed", True, (255, 50, 50))
            screen.blit(game_over_text, game_over_text.get_rect(center=(400, 300)))
            pygame.display.flip()
            pygame.time.wait(2000)
            break

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
