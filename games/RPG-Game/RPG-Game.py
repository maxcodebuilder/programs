"""
mini_rpg.py - Minimal singleplayer RPG using only pygame.

Features:
- Top-down tile map (procedural)
- Player movement, simple collision with walls
- Random encounters while exploring -> turn-based combat
- Player stats, XP, leveling, health potions (inventory)
- Save/Load to savegame.json (press S to save, L to load)
- Pause (Esc) and Inventory (I)
- Overarching goal: collect Ancient Runes and defeat the Ancient Guardian boss
- Victory screen shows a short moral and lets you restart or quit
- Works on macOS, Windows, Linux. Requires Python 3.8+ and pygame.

Run:
  pip3 install pygame
  python3 mini_rpg.py
"""

import pygame
import random
import json
import os
import sys
from typing import Tuple

pygame.init()
FONT = pygame.font.SysFont("arial", 18)
BIG_FONT = pygame.font.SysFont("arial", 28, bold=True)

# Settings
SCREEN_W, SCREEN_H = 800, 600
TILE = 32
MAP_W, MAP_H = 25, 18  # tiles
FPS = 60
ENCOUNTER_CHANCE = 0.08  # chance per step
RUNES_TO_WIN = 3

SAVE_FILE = "savegame.json"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGRAY = (40, 40, 40)
GREEN = (90, 200, 120)
RED = (230, 80, 80)
YELLOW = (240, 220, 100)
BLUE = (100, 160, 240)
BROWN = (120, 90, 60)
PURPLE = (180, 100, 200)


def draw_text(surface, text, pos, color=WHITE, font=FONT):
    surface.blit(font.render(text, True, color), pos)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_hp = 30
        self.hp = self.max_hp
        self.level = 1
        self.xp = 0
        self.gold = 0
        self.atk = 5
        self.defense = 1
        self.potions = 3
        self.runes = 0

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "level": self.level,
            "xp": self.xp,
            "gold": self.gold,
            "atk": self.atk,
            "defense": self.defense,
            "potions": self.potions,
            "runes": self.runes,
        }

    @classmethod
    def from_dict(cls, data):
        p = cls(data.get("x", 1), data.get("y", 1))
        p.max_hp = data.get("max_hp", p.max_hp)
        p.hp = data.get("hp", p.hp)
        p.level = data.get("level", p.level)
        p.xp = data.get("xp", p.xp)
        p.gold = data.get("gold", p.gold)
        p.atk = data.get("atk", p.atk)
        p.defense = data.get("defense", p.defense)
        p.potions = data.get("potions", p.potions)
        p.runes = data.get("runes", p.runes)
        return p

    def give_xp(self, amount):
        self.xp += amount
        # Level up threshold simple formula
        while self.xp >= self.level * 20:
            self.xp -= self.level * 20
            self.level += 1
            self.max_hp += 6
            self.atk += 2
            self.defense += 1
            self.hp = self.max_hp

    def heal_potion(self):
        if self.potions > 0 and self.hp < self.max_hp:
            self.potions -= 1
            heal = min(self.max_hp - self.hp, 20 + self.level * 2)
            self.hp += heal
            return heal
        return 0


class Enemy:
    def __init__(self, name, hp, atk, defense, xp_reward, gold):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.xp_reward = xp_reward
        self.gold = gold

    @classmethod
    def random_enemy(cls, level):
        # scaled by level
        t = random.choice([
            ("Goblin", 12, 4, 1, 8, 5),
            ("Wolf", 10, 5, 0, 9, 6),
            ("Bandit", 16, 6, 2, 12, 8),
            ("Slime", 8, 3, 0, 5, 3),
        ])
        hp = max(6, int(t[1] + level * 2 + random.randint(-2, 3)))
        atk = max(1, int(t[2] + level // 1 + random.randint(-1, 2)))
        defense = max(0, int(t[3] + level // 3))
        xp = int(t[4] + level * 2)
        gold = int(t[5] + level)
        return cls(t[0], hp, atk, defense, xp, gold)


class GameMap:
    def __init__(self, seed=None):
        self.seed = seed or random.randint(0, 999999)
        self.tiles = [["." for _ in range(MAP_W)] for _ in range(MAP_H)]
        self.generate()

    def generate(self):
        random.seed(self.seed)
        # Fill with floor and outer walls
        for y in range(MAP_H):
            for x in range(MAP_W):
                if x == 0 or y == 0 or x == MAP_W - 1 or y == MAP_H - 1:
                    self.tiles[y][x] = "#"
                else:
                    self.tiles[y][x] = "." if random.random() > 0.14 else "#"
        # Carve a simple path and place an exit
        sx, sy = 2, 2
        ex, ey = MAP_W - 3, MAP_H - 3
        x, y = sx, sy
        while x != ex or y != ey:
            self.tiles[y][x] = "."
            if random.random() < 0.6 and x < ex:
                x += 1
            elif y < ey:
                y += 1
        self.tiles[ey][ex] = ">"
        # Scatter some chests (C)
        for _ in range(8):
            rx = random.randint(1, MAP_W - 2)
            ry = random.randint(1, MAP_H - 2)
            if self.tiles[ry][rx] == ".":
                if random.random() < 0.12:
                    self.tiles[ry][rx] = "C"
        # Scatter 0-2 Ancient Runes (R) per map
        for _ in range(random.randint(0, 2)):
            for _tries in range(40):
                rx = random.randint(1, MAP_W - 2)
                ry = random.randint(1, MAP_H - 2)
                if self.tiles[ry][rx] == ".":
                    self.tiles[ry][rx] = "R"
                    break

    def passable(self, x, y):
        if 0 <= x < MAP_W and 0 <= y < MAP_H:
            return self.tiles[y][x] != "#"
        return False


class MiniRPG:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Mini RPG - Pygame")
        self.clock = pygame.time.Clock()
        self.map = GameMap()
        self.player = Player(2, 2)
        self.camera_offset = (0, 0)
        self.mode = "explore"  # or "combat", "menu", "inventory", "dead", "victory"
        self.running = True
        self.enemy = None
        self.message = ""
        self.encounters_disabled = False
        self.steps_since_encounter = 0
        self.victory_moral = (
            "Moral: Curiosity, small acts of courage, and kindness\n"
            "often lead to greater rewards than brute force alone."
        )

    def save(self):
        data = {
            "player": self.player.to_dict(),
            "map_seed": self.map.seed,
        }
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(data, f)
            self.message = "Game saved."
        except Exception as e:
            self.message = f"Save failed: {e}"

    def load(self):
        if not os.path.exists(SAVE_FILE):
            self.message = "No save file found."
            return
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            self.player = Player.from_dict(data.get("player", {}))
            self.map = GameMap(seed=data.get("map_seed"))
            self.message = "Game loaded."
            # If player had runes and is on an exit tile, ensure game treats it correctly
        except Exception as e:
            self.message = f"Load failed: {e}"

    def start_combat(self, enemy):
        self.enemy = enemy
        self.mode = "combat"
        self.combat_turn = "player"
        self.message = f"Encounter: {enemy.name} appears!"

    def end_game(self):
        # Victory achieved
        self.mode = "victory"
        self.message = "You have defeated the Ancient Guardian!"
        # Optionally, you could clear save or keep it; we'll leave save as-is.

    def resolve_player_attack(self):
        dmg = max(0, self.player.atk - self.enemy.defense + random.randint(-1, 3))
        self.enemy.hp -= max(1, dmg)
        return dmg

    def resolve_enemy_attack(self):
        dmg = max(0, self.enemy.atk - self.player.defense + random.randint(-2, 2))
        self.player.hp -= max(1, dmg)
        return dmg

    def handle_combat_input(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if self.combat_turn != "player":
            return
        if event.key == pygame.K_1:
            # Attack
            dmg = self.resolve_player_attack()
            self.message = f"You attack {self.enemy.name} for {dmg} damage."
            self.combat_turn = "enemy"
        elif event.key == pygame.K_2:
            # Defend -> reduce next enemy damage
            self.message = "You brace yourself (Defend). Reduced incoming damage next turn."
            self.player.defense += 2
            self.combat_turn = "enemy"
        elif event.key == pygame.K_3:
            # Potion
            healed = self.player.heal_potion()
            if healed:
                self.message = f"You drink a potion and recover {healed} HP."
            else:
                self.message = "No potions or already at full HP."
            self.combat_turn = "enemy"
        elif event.key == pygame.K_4:
            # Run attempt
            if random.random() < 0.6:
                self.message = "You escaped!"
                self.mode = "explore"
                self.enemy = None
                self.encounters_disabled = True
                self.steps_since_encounter = 0
            else:
                self.message = "Escape failed!"
                self.combat_turn = "enemy"

    def combat_update(self):
        if not self.enemy:
            self.mode = "explore"
            return
        # Check if enemy died
        if self.enemy.hp <= 0:
            # If this was the final boss, trigger victory
            if self.enemy.name == "Ancient Guardian":
                self.player.give_xp(self.enemy.xp_reward)
                self.player.gold += self.enemy.gold
                self.message = f"You defeated {self.enemy.name}! Victory!"
                self.enemy = None
                self.end_game()
                return

            self.player.give_xp(self.enemy.xp_reward)
            self.player.gold += self.enemy.gold
            # small chance to drop potion
            drop = ""
            if random.random() < 0.25:
                self.player.potions += 1
                drop = " You found a potion!"
            # small chance to drop a rune
            if random.random() < 0.02:
                self.player.runes += 1
                drop += " The enemy dropped an Ancient Rune!"
            self.message = f"You defeated {self.enemy.name}! +{self.enemy.xp_reward} XP +{self.enemy.gold} gold.{drop}"
            self.enemy = None
            self.mode = "explore"
            self.encounters_disabled = True
            self.steps_since_encounter = 0
            return

        # Enemy's turn
        if self.combat_turn == "enemy":
            dmg = self.resolve_enemy_attack()
            self.message = f"{self.enemy.name} hits you for {dmg} damage."
            # undo defend bonus if applied
            if self.player.defense > 1 and self.player.level >= 1:
                # we added +2 during defend; remove it once after enemy attacks
                self.player.defense = max(1, self.player.defense - 2)
            self.combat_turn = "player"

            # Check if player died
            if self.player.hp <= 0:
                self.player.hp = 0
                self.mode = "dead"
                self.message = "You were defeated... Press L to load or Q to quit."

    def try_random_encounter(self):
        if self.encounters_disabled:
            self.steps_since_encounter += 1
            if self.steps_since_encounter > 6:
                self.encounters_disabled = False
            return
        if random.random() < ENCOUNTER_CHANCE:
            e = Enemy.random_enemy(self.player.level)
            self.start_combat(e)

    def move_player(self, dx, dy):
        nx = self.player.x + dx
        ny = self.player.y + dy
        if 0 <= nx < MAP_W and 0 <= ny < MAP_H and self.map.passable(nx, ny):
            self.player.x = nx
            self.player.y = ny
            cell = self.map.tiles[ny][nx]
            # stepping on an Ancient Rune tile
            if cell == "R":
                self.player.runes += 1
                self.map.tiles[ny][nx] = "."
                self.message = f"You picked up an Ancient Rune! ({self.player.runes}/{RUNES_TO_WIN})"
                # small chance to trigger an encounter immediately
                if random.random() < 0.12:
                    e = Enemy.random_enemy(self.player.level)
                    self.start_combat(e)
                return
            # step -> chance of encounter
            self.try_random_encounter()
            # chest
            if cell == "C":
                self.map.tiles[ny][nx] = "."
                found = random.choice(["gold", "potion", "nothing", "rune"])
                if found == "gold":
                    g = random.randint(5, 20)
                    self.player.gold += g
                    self.message = f"You found {g} gold in a chest!"
                elif found == "potion":
                    self.player.potions += 1
                    self.message = "You found a potion in a chest!"
                elif found == "rune":
                    # rarer chest rune
                    if random.random() < 0.5:
                        self.player.runes += 1
                        self.message = f"You found an Ancient Rune in a chest! ({self.player.runes}/{RUNES_TO_WIN})"
                    else:
                        self.message = "The chest held an odd stone (nothing useful)."
                else:
                    self.message = "The chest was empty."
            # exit tile
            if cell == ">":
                # If player has enough runes, summon the final boss
                if self.player.runes >= RUNES_TO_WIN:
                    boss_hp = 60 + self.player.level * 12
                    boss_atk = 10 + self.player.level * 2
                    boss_def = 4 + self.player.level // 1
                    boss = Enemy("Ancient Guardian", boss_hp, boss_atk, boss_def, xp_reward=100 + self.player.level * 10, gold=100)
                    self.start_combat(boss)
                else:
                    # generate next map, small reward
                    self.player.give_xp(10)
                    self.player.gold += 10
                    self.map = GameMap()
                    self.player.x, self.player.y = 2, 2
                    self.message = f"You enter a new area. +10 XP +10 gold. Runes: {self.player.runes}/{RUNES_TO_WIN}"

    def handle_explore_input(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_UP, pygame.K_w):
            self.move_player(0, -1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.move_player(0, 1)
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            self.move_player(-1, 0)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.move_player(1, 0)
        elif event.key == pygame.K_i:
            self.mode = "inventory"
        elif event.key == pygame.K_s:
            self.save()
        elif event.key == pygame.K_l:
            self.load()
        elif event.key == pygame.K_ESCAPE:
            self.mode = "menu"

    def handle_inventory_input(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_1:
            healed = self.player.heal_potion()
            if healed:
                self.message = f"You used a potion and healed {healed} HP."
            else:
                self.message = "Cannot use potion now."
        elif event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
            self.mode = "explore"

    def draw_map(self):
        # center camera on player but clamp
        view_w = SCREEN_W // TILE
        view_h = SCREEN_H // TILE
        cam_x = max(0, min(self.player.x - view_w // 2, MAP_W - view_w))
        cam_y = max(0, min(self.player.y - view_h // 2, MAP_H - view_h))
        self.camera_offset = (cam_x, cam_y)
        for y in range(view_h):
            for x in range(view_w):
                mx = cam_x + x
                my = cam_y + y
                if 0 <= mx < MAP_W and 0 <= my < MAP_H:
                    rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                    tile = self.map.tiles[my][mx]
                    if tile == "#":
                        pygame.draw.rect(self.screen, DARKGRAY, rect)
                    elif tile == ".":
                        pygame.draw.rect(self.screen, BROWN, rect)
                        pygame.draw.rect(self.screen, (100, 70, 40), rect, 1)
                    elif tile == "C":
                        pygame.draw.rect(self.screen, BROWN, rect)
                        pygame.draw.rect(self.screen, YELLOW, rect.inflate(-8, -8))
                    elif tile == ">":
                        pygame.draw.rect(self.screen, BROWN, rect)
                        pygame.draw.rect(self.screen, BLUE, rect.inflate(-8, -8))
                    elif tile == "R":
                        pygame.draw.rect(self.screen, BROWN, rect)
                        pygame.draw.rect(self.screen, PURPLE, rect.inflate(-12, -12))
        # draw player
        px = (self.player.x - cam_x) * TILE
        py = (self.player.y - cam_y) * TILE
        pygame.draw.rect(self.screen, GREEN, (px + 4, py + 4, TILE - 8, TILE - 8))
        # hud
        hud_y = SCREEN_H - 120
        pygame.draw.rect(self.screen, BLACK, (0, hud_y, SCREEN_W, 120))
        draw_text(self.screen, f"HP: {self.player.hp}/{self.player.max_hp}  ATK: {self.player.atk}  DEF: {self.player.defense}", (8, hud_y + 8))
        draw_text(self.screen, f"Level: {self.player.level}  XP: {self.player.xp}/{self.player.level*20}  Gold: {self.player.gold}", (8, hud_y + 32))
        draw_text(self.screen, f"Potions: {self.player.potions}   Runes: {self.player.runes}/{RUNES_TO_WIN}   (I inventory)  S save  L load", (8, hud_y + 56))
        if self.message:
            draw_text(self.screen, f"Message: {self.message}", (8, hud_y + 84), color=YELLOW)

    def draw_combat(self):
        # dark background
        self.screen.fill((16, 16, 24))
        # draw enemy
        draw_text(self.screen, f"Enemy: {self.enemy.name}", (40, 40), color=RED, font=BIG_FONT)
        draw_text(self.screen, f"HP: {self.enemy.hp}/{self.enemy.max_hp}", (40, 80))
        pygame.draw.rect(self.screen, RED, (40, 110, 200 * max(0, self.enemy.hp) // max(1, self.enemy.max_hp), 20))
        # draw player stats
        draw_text(self.screen, f"You - Level {self.player.level}", (SCREEN_W - 300, 40), color=GREEN, font=BIG_FONT)
        draw_text(self.screen, f"HP: {self.player.hp}/{self.player.max_hp}", (SCREEN_W - 300, 80))
        pygame.draw.rect(self.screen, GREEN, (SCREEN_W - 300, 110, 200 * max(0, self.player.hp) // max(1, self.player.max_hp), 20))
        # actions
        draw_text(self.screen, "Choose action (1-4):", (40, 160), color=YELLOW)
        draw_text(self.screen, "1) Attack", (40, 200))
        draw_text(self.screen, "2) Defend (temporary)", (40, 230))
        draw_text(self.screen, "3) Use Potion", (40, 260))
        draw_text(self.screen, "4) Run", (40, 290))
        # message
        if self.message:
            draw_text(self.screen, self.message, (40, 340), color=WHITE)
        draw_text(self.screen, "(Defend adds +2 DEF for one incoming attack)", (40, 380), color=(180, 180, 180))

    def draw_menu(self):
        self.screen.fill((10, 10, 20))
        draw_text(self.screen, "Game Menu", (SCREEN_W // 2 - 50, 40), font=BIG_FONT)
        draw_text(self.screen, "Esc to resume", (40, 120))
        draw_text(self.screen, "Press Q to quit", (40, 160))
        draw_text(self.screen, "Press L to load save", (40, 200))
        draw_text(self.screen, "Press S to save", (40, 240))

    def draw_inventory(self):
        self.screen.fill((18, 14, 26))
        draw_text(self.screen, "Inventory", (40, 40), font=BIG_FONT)
        draw_text(self.screen, f"Potions: {self.player.potions}  (press 1 to use)", (40, 120))
        draw_text(self.screen, "Esc or I to return to exploration", (40, 220))
        draw_text(self.screen, f"HP: {self.player.hp}/{self.player.max_hp}", (40, 160))
        draw_text(self.screen, f"Runes: {self.player.runes}/{RUNES_TO_WIN}", (40, 190))

    def draw_dead(self):
        self.screen.fill((0, 0, 0))
        draw_text(self.screen, "You Died", (SCREEN_W // 2 - 60, SCREEN_H // 2 - 20), font=BIG_FONT, color=RED)
        draw_text(self.screen, "Press L to load save or Q to quit", (SCREEN_W // 2 - 140, SCREEN_H // 2 + 20))

    def draw_victory(self):
        self.screen.fill((8, 10, 30))
        draw_text(self.screen, "Victory!", (SCREEN_W // 2 - 60, 40), font=BIG_FONT, color=YELLOW)
        # Show short summary
        draw_text(self.screen, f"You collected {self.player.runes} Ancient Runes and defeated the Guardian.", (40, 120))
        draw_text(self.screen, f"Final Level: {self.player.level}  Gold: {self.player.gold}", (40, 160))
        # Moral text (wrap a bit)
        lines = self.victory_moral.split("\n")
        y = 220
        for ln in lines:
            draw_text(self.screen, ln, (40, y), color=PURPLE)
            y += 28
        draw_text(self.screen, "Press R to play again, or Q to quit.", (40, y + 20), color=WHITE)

    def mainloop(self):
        while self.running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.mode == "explore":
                    self.handle_explore_input(event)
                elif self.mode == "combat":
                    self.handle_combat_input(event)
                elif self.mode == "menu":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.mode = "explore"
                        elif event.key == pygame.K_q:
                            self.running = False
                        elif event.key == pygame.K_s:
                            self.save()
                        elif event.key == pygame.K_l:
                            self.load()
                elif self.mode == "inventory":
                    self.handle_inventory_input(event)
                elif self.mode == "dead":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_l:
                            self.load()
                            if self.mode != "dead":
                                self.message = "Loaded."
                        elif event.key == pygame.K_q:
                            self.running = False
                elif self.mode == "victory":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            # restart game fresh
                            self.map = GameMap()
                            self.player = Player(2, 2)
                            self.mode = "explore"
                            self.enemy = None
                            self.message = "New adventure!"
                        elif event.key == pygame.K_q:
                            self.running = False

            # combat resolution happens even when no events (enemy actions)
            if self.mode == "combat":
                # If it's enemy turn, proceed a little slower: let events resolve then update
                self.combat_update()

            # render
            if self.mode == "explore":
                self.draw_map()
            elif self.mode == "combat":
                self.draw_combat()
            elif self.mode == "menu":
                self.draw_menu()
            elif self.mode == "inventory":
                self.draw_inventory()
            elif self.mode == "dead":
                self.draw_dead()
            elif self.mode == "victory":
                self.draw_victory()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = MiniRPG()
    game.mainloop()