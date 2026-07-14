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
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
DARK_GREY = (70, 70, 70)

class Material:
    def __init__(self, x, y, material_type):
        self.x = x
        self.y = y
        self.radius = 8
        self.material_type = material_type  # "wood", "rope", "metal", "stone"
        self.collected = False
        
        # Material colors
        self.colors = {
            "wood": BROWN,
            "rope": ORANGE,
            "metal": GREY,
            "stone": DARK_GREY
        }
    
    def draw(self, surface):
        if not self.collected:
            color = self.colors.get(self.material_type, WHITE)
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 1)
    
    def check_collision(self, player):
        distance = math.dist((self.x, self.y), (player.x, player.y))
        return distance < self.radius + player.radius

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.speed = 4
        self.health = 100
        self.max_health = 100
        self.materials = {"wood": 0, "rope": 0, "metal": 0, "stone": 0}
        
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
        pygame.draw.circle(surface, PURPLE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 2)
        
        # Health bar
        health_bar_width = 30
        pygame.draw.rect(surface, GREY, (self.x - 15, self.y - 25, health_bar_width, 6))
        health_ratio = self.health / self.max_health
        pygame.draw.rect(surface, GREEN, (self.x - 15, self.y - 25, health_bar_width * health_ratio, 6))

class Island:
    def __init__(self, x, y, name, is_starting=False):
        self.x = x
        self.y = y
        self.name = name
        self.radius = 50
        self.is_starting = is_starting
        self.visited = is_starting
        self.materials = []
        self.generate_materials()
    
    def generate_materials(self):
        # Generate random materials on the island
        material_types = ["wood", "rope", "metal", "stone"]
        for _ in range(random.randint(8, 15)):
            offset_x = random.randint(-40, 40)
            offset_y = random.randint(-40, 40)
            material_type = random.choice(material_types)
            self.materials.append(Material(self.x + offset_x, self.y + offset_y, material_type))
    
    def draw(self, surface):
        if self.is_starting:
            color = GREEN
        elif self.visited:
            color = GREY
        else:
            color = YELLOW
        
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, DARK_GREEN, (int(self.x), int(self.y)), self.radius, 3)
        
        # Island name
        font = pygame.font.Font(None, 20)
        text = font.render(self.name, True, BLACK)
        surface.blit(text, (self.x - text.get_width() // 2, self.y - 8))
    
    def draw_materials(self, surface):
        for material in self.materials:
            material.draw(surface)
    
    def check_collision(self, player):
        distance = math.dist((self.x, self.y), (player.x, player.y))
        return distance < self.radius + player.radius

class EnemyEntity:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 8
        self.speed = 2
        self.angle = random.uniform(0, 2 * math.pi)
    
    def move(self):
        # Random patrol movement
        self.angle += random.uniform(-0.1, 0.1)
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # Keep in bounds
        if self.x < 0 or self.x > 1200:
            self.angle = math.pi - self.angle
        if self.y < 0 or self.y > 800:
            self.angle = -self.angle
        
        self.x = max(0, min(1200, self.x))
        self.y = max(0, min(800, self.y))
    
    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius, 1)
    
    def check_collision(self, player):
        distance = math.dist((self.x, self.y), (player.x, player.y))
        return distance < self.radius + player.radius

class IslandAdventure:
    def __init__(self):
        pygame.init()
        self.WIDTH = 1200
        self.HEIGHT = 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Island Adventure - Build & Sail!")
        self.clock = pygame.time.Clock()
        
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game state
        self.player = Player(self.WIDTH // 2, self.HEIGHT // 2)
        self.islands = self.generate_islands()
        self.current_island = self.islands[0]
        self.island_index = 0
        
        self.game_over = False
        self.message = ""
        self.message_timer = 0
        self.ship_requirements = {"wood": 20, "rope": 15, "metal": 10, "stone": 12}
        self.game_time = 0
        
        # Enemies on current island
        self.enemies = []
        self.spawn_enemies()
    
    def generate_islands(self):
        names = ["Starting Port", "Forest Island", "Rocky Peak", "Metal Mines", "Merchant Bay", "Storm Island"]
        islands = []
        
        positions = [
            (self.WIDTH // 2, self.HEIGHT // 2),
            (200, 150),
            (1000, 200),
            (150, 650),
            (1050, 650),
            (self.WIDTH // 2, self.HEIGHT - 150)
        ]
        
        for i, (x, y) in enumerate(positions):
            is_starting = (i == 0)
            islands.append(Island(x, y, names[i], is_starting))
        
        return islands
    
    def spawn_enemies(self):
        self.enemies = []
        for _ in range(2 + self.island_index):
            x = random.randint(100, self.WIDTH - 100)
            y = random.randint(100, self.HEIGHT - 100)
            self.enemies.append(EnemyEntity(x, y))
    
    def show_message(self, text):
        self.message = text
        self.message_timer = 180
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    self.try_build_ship()
                if event.key == pygame.K_r and self.game_over:
                    self.__init__()
        return True
    
    def try_build_ship(self):
        # Check if player has enough materials
        can_build = all(
            self.player.materials[mat] >= self.ship_requirements[mat]
            for mat in self.ship_requirements
        )
        
        if can_build:
            # Consume materials
            for mat in self.ship_requirements:
                self.player.materials[mat] -= self.ship_requirements[mat]
            
            # Move to next island
            if self.island_index + 1 < len(self.islands):
                self.island_index += 1
                self.current_island = self.islands[self.island_index]
                self.current_island.visited = True
                self.player.x = self.current_island.x
                self.player.y = self.current_island.y
                self.player.health = self.player.max_health
                self.spawn_enemies()
                self.show_message(f"Sailed to {self.current_island.name}!")
            else:
                self.game_over = True
                self.show_message("You've explored all islands! Victory!")
        else:
            self.show_message("Not enough materials to build a ship!")
    
    def update(self):
        if self.game_over:
            return
        
        self.game_time += 1
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.WIDTH, self.HEIGHT)
        
        # Collect materials
        for material in self.current_island.materials:
            if not material.collected and material.check_collision(self.player):
                self.player.materials[material.material_type] += 1
                material.collected = True
                self.show_message(f"Collected {material.material_type}!")
        
        # Move enemies (simple patrol)
        for enemy in self.enemies:
            enemy.move()
            
            # Combat
            if enemy.check_collision(self.player):
                self.player.health -= 0.5
                if self.player.health <= 0:
                    self.game_over = True
                    self.show_message("You were defeated!")
        
        if self.message_timer > 0:
            self.message_timer -= 1
    
    def draw(self):
        self.screen.fill(DARK_BLUE)
        
        # Animate water background
        wave_offset = (self.game_time // 5) % 20
        for x in range(0, self.WIDTH, 40):
            for y in range(0, self.HEIGHT, 40):
                offset = math.sin((x + y + self.game_time / 10) / 100) * 3
                pygame.draw.line(self.screen, LIGHT_BLUE, (x, y + offset), (x + 40, y + offset), 1)
        
        # Draw all islands
        for island in self.islands:
            island.draw(self.screen)
        
        # Draw materials on current island
        self.current_island.draw_materials(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
        
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_hud(self):
        # Island info
        island_text = self.font_medium.render(f"Island: {self.current_island.name}", True, CYAN)
        self.screen.blit(island_text, (20, 20))
        
        # Health
        health_text = self.font_small.render(f"Health: {int(self.player.health)}/100", True, GREEN)
        self.screen.blit(health_text, (20, 70))
        
        # Materials collected
        mat_y = 120
        mat_label = self.font_small.render("Materials:", True, WHITE)
        self.screen.blit(mat_label, (20, mat_y))
        
        mat_y += 30
        for mat_type, required in self.ship_requirements.items():
            current = self.player.materials[mat_type]
            color = GREEN if current >= required else RED
            text = self.font_small.render(f"{mat_type}: {current}/{required}", True, color)
            self.screen.blit(text, (20, mat_y))
            mat_y += 25
        
        # Instructions
        inst_y = self.HEIGHT - 100
        inst1 = self.font_small.render("Collect materials to build a ship", True, YELLOW)
        self.screen.blit(inst1, (20, inst_y))
        
        inst2 = self.font_small.render("Press B to build and sail to next island", True, YELLOW)
        self.screen.blit(inst2, (20, inst_y + 30))
        
        # Message
        if self.message_timer > 0:
            msg_text = self.font_small.render(self.message, True, YELLOW)
            self.screen.blit(msg_text, (self.WIDTH // 2 - msg_text.get_width() // 2, 30))
    
    def draw_game_over(self):
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font_large.render(self.message, True, YELLOW if "Victory" in self.message else RED)
        self.screen.blit(game_over_text, (self.WIDTH // 2 - game_over_text.get_width() // 2, 250))
        
        restart_text = self.font_small.render("Press R to restart or close window to quit", True, GREEN)
        self.screen.blit(restart_text, (self.WIDTH // 2 - restart_text.get_width() // 2, 400))
    
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