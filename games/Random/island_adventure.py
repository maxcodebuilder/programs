import pygame
import random
import math

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (25, 50, 150)
LIGHT_BLUE = (100, 150, 255)
SAND = (238, 214, 175)
GREEN = (34, 139, 34)
DARK_GREEN = (20, 100, 20)
YELLOW = (255, 215, 0)
RED = (220, 20, 60)
PURPLE = (200, 100, 200)
GREY = (150, 150, 150)
CYAN = (0, 255, 255)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.gold = 0
        self.inventory = []
        
    def move(self, keys, width, height):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x = max(self.radius, self.x - self.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x = min(width - self.radius, self.x + self.speed)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y = max(self.radius, self.y - self.speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y = min(height - self.radius, self.y + self.speed)
    
    def draw(self, surface):
        # Draw player
        pygame.draw.circle(surface, PURPLE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 2)
        
        # Draw health bar
        health_bar_width = 30
        pygame.draw.rect(surface, GREY, (self.x - 15, self.y - 25, health_bar_width, 6))
        health_ratio = self.health / self.max_health
        pygame.draw.rect(surface, GREEN, (self.x - 15, self.y - 25, health_bar_width * health_ratio, 6))

class Island:
    def __init__(self, x, y, size, gold_amount, treasure_type="normal"):
        self.x = x
        self.y = y
        self.size = size
        self.radius = size
        self.gold_amount = gold_amount
        self.treasure_type = treasure_type
        self.collected = False
        
    def draw(self, surface):
        if self.collected:
            color = GREY
        else:
            if self.treasure_type == "rare":
                color = YELLOW
            elif self.treasure_type == "epic":
                color = PURPLE
            else:
                color = GREEN
        
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, DARK_GREEN, (int(self.x), int(self.y)), self.radius, 2)
        
        # Draw gold indicator
        if not self.collected and self.gold_amount > 0:
            text_font = pygame.font.Font(None, 20)
            text = text_font.render(f"{self.gold_amount}G", True, YELLOW)
            surface.blit(text, (self.x - 15, self.y - 8))
    
    def check_collision(self, player):
        distance = math.dist((self.x, self.y), (player.x, player.y))
        return distance < self.radius + player.radius

class Enemy:
    def __init__(self, x, y, speed=2):
        self.x = x
        self.y = y
        self.radius = 10
        self.speed = speed
        self.health = 30
        self.max_health = 30
        self.target = None
        self.direction = random.choice([-1, 1])
        self.move_timer = 0
        
    def move(self, player, width, height):
        # Chase player if close
        distance = math.dist((self.x, self.y), (player.x, player.y))
        
        if distance < 300:
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
        else:
            # Random patrol
            self.move_timer += 1
            if self.move_timer > 60:
                self.direction = random.choice([-1, 1])
                self.move_timer = 0
            
            self.x += self.speed * self.direction
        
        # Boundary wrap
        if self.x > width:
            self.x = 0
        elif self.x < 0:
            self.x = width
        if self.y > height:
            self.y = 0
        elif self.y < 0:
            self.y = height
    
    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius, 2)
        
        # Health bar
        health_bar_width = 20
        pygame.draw.rect(surface, GREY, (self.x - 10, self.y - 18, health_bar_width, 4))
        health_ratio = self.health / self.max_health
        pygame.draw.rect(surface, GREEN, (self.x - 10, self.y - 18, health_bar_width * health_ratio, 4))
    
    def check_collision(self, player):
        distance = math.dist((self.x, self.y), (player.x, player.y))
        return distance < self.radius + player.radius

class IslandAdventure:
    def __init__(self):
        pygame.init()
        self.WIDTH = 1200
        self.HEIGHT = 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Island Adventure - Collect Gold!")
        self.clock = pygame.time.Clock()
        
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Initialize game
        self.player = Player(self.WIDTH // 2, self.HEIGHT // 2)
        self.islands = self.generate_islands()
        self.enemies = self.generate_enemies()
        self.wave = 1
        self.score_timer = 0
        self.game_time = 0
        self.paused = False
        self.game_over = False
        self.message = ""
        self.message_timer = 0
        
    def generate_islands(self):
        islands = []
        for _ in range(15):
            x = random.randint(100, self.WIDTH - 100)
            y = random.randint(100, self.HEIGHT - 100)
            size = random.randint(15, 25)
            
            # Weighted treasure type
            rand = random.random()
            if rand < 0.7:
                treasure_type = "normal"
                gold_amount = random.randint(10, 30)
            elif rand < 0.9:
                treasure_type = "rare"
                gold_amount = random.randint(50, 100)
            else:
                treasure_type = "epic"
                gold_amount = random.randint(150, 300)
            
            islands.append(Island(x, y, size, gold_amount, treasure_type))
        
        return islands
    
    def generate_enemies(self):
        enemies = []
        for _ in range(3 + self.wave):
            x = random.randint(50, self.WIDTH - 50)
            y = random.randint(50, self.HEIGHT - 50)
            speed = 2 + (self.wave * 0.5)
            enemies.append(Enemy(x, y, speed))
        return enemies
    
    def show_message(self, text, duration=3):
        self.message = text
        self.message_timer = duration * 60
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                if event.key == pygame.K_r and self.game_over:
                    self.__init__()
        return True
    
    def update(self):
        if self.paused or self.game_over:
            return
        
        self.game_time += 1
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.WIDTH, self.HEIGHT)
        
        # Move enemies
        for enemy in self.enemies:
            enemy.move(self.player, self.WIDTH, self.HEIGHT)
        
        # Collect gold from islands
        for island in self.islands:
            if not island.collected and island.check_collision(self.player):
                self.player.gold += island.gold_amount
                island.collected = True
                self.show_message(f"+{island.gold_amount} Gold! Total: {self.player.gold}")
        
        # Combat with enemies
        for enemy in self.enemies[:]:
            if enemy.check_collision(self.player):
                self.player.health -= 1
                enemy.health -= 2
                
                if enemy.health <= 0:
                    self.enemies.remove(enemy)
                    self.player.gold += 20
                    self.show_message("+20 Gold from defeating enemy!")
        
        if self.player.health <= 0:
            self.game_over = True
            self.show_message("Game Over! You were defeated!", 999)
        
        # Wave progression
        collected_islands = sum(1 for i in self.islands if i.collected)
        if collected_islands == len(self.islands):
            self.wave += 1
            self.islands = self.generate_islands()
            self.enemies = self.generate_enemies()
            self.player.health = self.player.max_health
            self.show_message(f"Wave {self.wave}! New islands appeared!")
        
        # Regenerate health slowly
        if self.game_time % 30 == 0:
            self.player.health = min(self.player.max_health, self.player.health + 1)
        
        # Reduce message timer
        if self.message_timer > 0:
            self.message_timer -= 1
    
    def draw(self):
        # Water background
        self.screen.fill(DARK_BLUE)
        
        # Animate water
        wave_offset = (self.game_time // 5) % 20
        for x in range(0, self.WIDTH, 40):
            for y in range(0, self.HEIGHT, 40):
                offset = math.sin((x + y + self.game_time / 10) / 100) * 3
                pygame.draw.line(self.screen, LIGHT_BLUE, (x, y + offset), (x + 40, y + offset), 1)
        
        # Draw islands
        for island in self.islands:
            island.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
        
        # Draw paused message
        if self.paused:
            pause_text = self.font_large.render("PAUSED", True, YELLOW)
            self.screen.blit(pause_text, (self.WIDTH // 2 - pause_text.get_width() // 2, 50))
        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_hud(self):
        # Top left stats
        gold_text = self.font_medium.render(f"Gold: {self.player.gold}", True, YELLOW)
        self.screen.blit(gold_text, (20, 20))
        
        health_text = self.font_medium.render(f"Health: {int(self.player.health)}/{self.player.max_health}", True, GREEN)
        self.screen.blit(health_text, (20, 60))
        
        wave_text = self.font_medium.render(f"Wave: {self.wave}", True, CYAN)
        self.screen.blit(wave_text, (20, 100))
        
        # Island progress
        collected = sum(1 for i in self.islands if i.collected)
        total = len(self.islands)
        progress_text = self.font_small.render(f"Islands: {collected}/{total}", True, WHITE)
        self.screen.blit(progress_text, (20, 140))
        
        # Bottom right - enemies left
        enemies_text = self.font_small.render(f"Enemies: {len(self.enemies)}", True, RED)
        self.screen.blit(enemies_text, (self.WIDTH - 220, self.HEIGHT - 40))
        
        # Messages
        if self.message_timer > 0:
            msg_text = self.font_small.render(self.message, True, YELLOW)
            self.screen.blit(msg_text, (self.WIDTH // 2 - msg_text.get_width() // 2, 30))
        
        # Controls hint
        controls = self.font_small.render("WASD/Arrows: Move | SPACE: Pause", True, WHITE)
        self.screen.blit(controls, (self.WIDTH // 2 - controls.get_width() // 2, self.HEIGHT - 40))
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        self.screen.blit(game_over_text, (self.WIDTH // 2 - game_over_text.get_width() // 2, 200))
        
        # Final stats
        final_gold = self.font_medium.render(f"Final Gold: {self.player.gold}", True, YELLOW)
        self.screen.blit(final_gold, (self.WIDTH // 2 - final_gold.get_width() // 2, 300))
        
        final_wave = self.font_medium.render(f"Waves Survived: {self.wave}", True, WHITE)
        self.screen.blit(final_wave, (self.WIDTH // 2 - final_wave.get_width() // 2, 360))
        
        # Restart instruction
        restart_text = self.font_small.render("Press R to restart or close window to quit", True, GREEN)
        self.screen.blit(restart_text, (self.WIDTH // 2 - restart_text.get_width() // 2, 450))
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = IslandAdventure()
    game.run()
