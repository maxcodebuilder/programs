import pygame
import os
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

        # If this is the starting island, ensure there are enough
        # materials to build a ship locally.
        if self.is_starting:
            # Ship requirements (match IslandAdventure.ship_requirements)
            reqs = {"wood": 20, "rope": 15, "metal": 10, "stone": 12}
            # Place required materials
            for mat_type, count in reqs.items():
                for _ in range(count):
                    # place within island bounds
                    angle = random.uniform(0, 2 * math.pi)
                    r = random.uniform(5, max(5, self.radius - 20))
                    mx = int(self.x + math.cos(angle) * r)
                    my = int(self.y + math.sin(angle) * r)
                    self.materials.append(Material(mx, my, mat_type))
            # Add a few extras for variety
            for _ in range(10):
                angle = random.uniform(0, 2 * math.pi)
                r = random.uniform(5, max(5, self.radius - 20))
                mx = int(self.x + math.cos(angle) * r)
                my = int(self.y + math.sin(angle) * r)
                self.materials.append(Material(mx, my, random.choice(material_types)))
        else:
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
    def __init__(self, x, y, held_material=None):
        self.x = x
        self.y = y
        self.radius = 8
        self.speed = 2
        self.angle = random.uniform(0, 2 * math.pi)
        self.health = 30
        self.max_health = 30
        self.held_material = held_material
    
    def move(self):
        # Random patrol movement
        self.angle += random.uniform(-0.1, 0.1)
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # Keep roughly inside island area (clamp later in update)
        if self.x < 0 or self.x > 1200:
            self.angle = math.pi - self.angle
        if self.y < 0 or self.y > 800:
            self.angle = -self.angle
        
        self.x = max(0, min(1200, self.x))
        self.y = max(0, min(800, self.y))
    
    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius, 1)
        # small health indicator
        hbw = 16
        pygame.draw.rect(surface, GREY, (self.x - hbw/2, self.y - 14, hbw, 3))
        pygame.draw.rect(surface, GREEN, (self.x - hbw/2, self.y - 14, hbw * (self.health/self.max_health), 3))
    
    def check_collision(self, player):
        distance = math.hypot(self.x - player.x, self.y - player.y)
        return distance < self.radius + player.radius


class Arrow:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 4
        self.damage = 20
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
    
    def draw(self, surface):
        # draw as small line with head
        end_x = int(self.x - self.vx * 0.2)
        end_y = int(self.y - self.vy * 0.2)
        pygame.draw.line(surface, BLACK, (int(self.x), int(self.y)), (end_x, end_y), 2)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius)

class IslandAdventure:
    def __init__(self):
        pygame.init()
        # try to init mixer for sound (optional)
        try:
            pygame.mixer.init()
        except Exception:
            pass
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
        # Ship requirements must be set before ensuring island materials
        self.ship_requirements = {"wood": 20, "rope": 15, "metal": 10, "stone": 12}
        # Ensure islands (except final) contain enough materials to build the
        # ship to reach the next island. This guarantees progression isn't
        # blocked when moving from one island to the next.
        self.ensure_materials_on_islands()
        self.current_island = self.islands[0]
        self.island_index = 0
        
        self.game_over = False
        self.message = ""
        self.message_timer = 0
        self.game_time = 0
        
        # Enemies on current island
        self.enemies = []
        # Projectiles (arrows)
        self.arrows = []
        self.spawn_enemies()

        # Phase can be: 'island', 'sailing', 'maze', 'riddle', 'victory'
        self.phase = 'island'
        # Sailing/cutscene timer (frames)
        self.sailing_timer = 0

        # Maze related
        self.maze = None
        # Make the maze much larger and more complex
        self.maze_cell_size = 20
        self.maze_cols = 41
        self.maze_rows = 25
        self.maze_player_cell = (0, 0)
        self.maze_goal_cell = (0, 0)
        self.maze_moving = False

        # Create ship sprite surface (used in sailing cutscene)
        self.ship_sprite = self.create_ship_sprite()
        # Try to load optional ship sound (place a WAV at sprites/ship_horn.wav)
        self.ship_sound = None
        try:
            snd_path = os.path.join(os.path.dirname(__file__), 'sprites', 'ship_horn.wav')
            if os.path.exists(snd_path):
                self.ship_sound = pygame.mixer.Sound(snd_path)
        except Exception:
            self.ship_sound = None
    
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

    def ensure_materials_on_islands(self):
        """
        For every island except the final one, guarantee that the island has
        at least the counts required by `self.ship_requirements` so the player
        can build a ship to the next island.
        """
        # Include the final island as well so the player can build
        # a ship there (e.g., to trigger end-game/victory) if desired.
        for i in range(len(self.islands)):
            island = self.islands[i]
            # Count existing (uncollected) materials
            counts = {k: 0 for k in self.ship_requirements}
            for m in island.materials:
                if not getattr(m, "collected", False):
                    if m.material_type in counts:
                        counts[m.material_type] += 1

            # Add missing materials inside the island circle
            for mat, req in self.ship_requirements.items():
                missing = req - counts.get(mat, 0)
                for _ in range(max(0, missing)):
                    angle = random.uniform(0, 2 * math.pi)
                    r = random.uniform(5, max(5, island.radius - 20))
                    mx = int(island.x + math.cos(angle) * r)
                    my = int(island.y + math.sin(angle) * r)
                    island.materials.append(Material(mx, my, mat))
    
    def spawn_enemies(self):
        self.enemies = []
        for _ in range(2 + self.island_index):
            # spawn enemies within the current island circle
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(0, self.current_island.radius - 20)
            x = int(self.current_island.x + math.cos(angle) * r)
            y = int(self.current_island.y + math.sin(angle) * r)
            # give some enemies a held special material
            held = None
            if random.random() < 0.35:
                held = random.choice(["metal", "rope", "wood", "stone"])
            self.enemies.append(EnemyEntity(x, y, held_material=held))
    
    def show_message(self, text):
        self.message = text
        self.message_timer = 180

    def start_final_sequence(self):
        # Begin sailing cutscene then drop player at maze start
        self.phase = 'sailing'
        self.sailing_timer = 240  # 4 seconds at 60fps
        # optional: reset player position to center
        self.player.x = self.WIDTH // 2
        self.player.y = self.HEIGHT - 80
        self.show_message("A pirate ship approaches...")
        # play ship sound if available
        try:
            if self.ship_sound:
                self.ship_sound.play()
        except Exception:
            pass

    def begin_maze(self):
        # generate maze and place player at start
        self.phase = 'maze'
        self.maze = self.generate_maze(self.maze_cols, self.maze_rows)
        # place player at top-left open cell
        self.maze_player_cell = (1, 1)
        self.maze_goal_cell = (self.maze_cols - 2, self.maze_rows - 2)
        # convert to screen coords
        sx = (self.WIDTH - self.maze_cols * self.maze_cell_size) // 2
        sy = (self.HEIGHT - self.maze_rows * self.maze_cell_size) // 2
        px = sx + self.maze_player_cell[0] * self.maze_cell_size + self.maze_cell_size // 2
        py = sy + self.maze_player_cell[1] * self.maze_cell_size + self.maze_cell_size // 2
        self.player.x = px
        self.player.y = py
        self.player.radius = max(6, self.maze_cell_size // 3)
        self.show_message("You disembark onto a huge island. Find the portal!")

    def start_riddle(self):
        # Place player near the shore so they can walk to the spider
        self.phase = 'riddle'
        self.player.x = self.WIDTH // 2
        self.player.y = self.HEIGHT - 120
        # ensure player can move during riddle approach
        self.player.radius = 12
        self.show_message("A giant spider blocks your path and speaks...")

    def create_ship_sprite(self):
        # create a Surface for the ship sprite and draw a nicer ship there
        surf_w = 320
        surf_h = 200
        surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        cx = surf_w // 2
        hull_top = surf_h // 2
        # hull
        hull_points = [
            (cx - 120, hull_top + 30),
            (cx - 80, hull_top + 10),
            (cx + 80, hull_top + 10),
            (cx + 120, hull_top + 30),
            (cx + 60, hull_top + 50),
            (cx - 60, hull_top + 50),
        ]
        pygame.draw.polygon(surf, BROWN, hull_points)
        pygame.draw.polygon(surf, BLACK, hull_points, 2)
        # deck
        pygame.draw.rect(surf, (120, 70, 30), (cx - 70, hull_top - 4, 140, 14))
        # mast
        mast_x = cx
        mast_top = hull_top - 120
        pygame.draw.line(surf, DARK_GREY, (mast_x, hull_top - 6), (mast_x, mast_top), 6)
        # sails
        sail1 = [(mast_x + 6, mast_top + 20), (mast_x + 6 + 70, mast_top + 50), (mast_x + 6, mast_top + 80)]
        sail2 = [(mast_x - 4, mast_top + 60), (mast_x - 4 + 90, mast_top + 95), (mast_x - 4, mast_top + 130)]
        pygame.draw.polygon(surf, WHITE, sail1)
        pygame.draw.polygon(surf, BLACK, sail1, 2)
        pygame.draw.polygon(surf, WHITE, sail2)
        pygame.draw.polygon(surf, BLACK, sail2, 2)
        # jib
        jib = [(cx + 80, hull_top + 10), (cx + 140, hull_top - 10), (mast_x + 6, mast_top + 30)]
        pygame.draw.polygon(surf, WHITE, jib)
        pygame.draw.polygon(surf, BLACK, jib, 2)
        # flag
        flag_pts = [(mast_x, mast_top - 8), (mast_x + 34, mast_top - 4), (mast_x, mast_top + 4)]
        pygame.draw.polygon(surf, PURPLE, flag_pts)
        return surf

    def generate_maze(self, cols, rows):
        # Create a grid initialized as walls, carve passages with recursive backtracker
        grid = [[{'open': False} for _ in range(cols)] for _ in range(rows)]

        def carve(cx, cy):
            grid[cy][cx]['open'] = True
            dirs = [(2, 0), (-2, 0), (0, 2), (0, -2)]
            random.shuffle(dirs)
            for dx, dy in dirs:
                nx, ny = cx + dx, cy + dy
                if 1 <= nx < cols - 1 and 1 <= ny < rows - 1 and not grid[ny][nx]['open']:
                    # knock down wall between
                    wx, wy = cx + dx // 2, cy + dy // 2
                    grid[wy][wx]['open'] = True
                    grid[ny][nx]['open'] = True
                    carve(nx, ny)

        # Start at (1,1)
        carve(1, 1)
        # ensure goal is open
        gx, gy = cols - 2, rows - 2
        grid[gy][gx]['open'] = True
        return grid
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                # Phase-specific key handling
                if self.phase == 'maze' and self.maze is not None:
                    # tile movement: WASD or arrow keys
                    sx = (self.WIDTH - self.maze_cols * self.maze_cell_size) // 2
                    sy = (self.HEIGHT - self.maze_rows * self.maze_cell_size) // 2
                    cx = int((self.player.x - sx) // self.maze_cell_size)
                    cy = int((self.player.y - sy) // self.maze_cell_size)
                    nx, ny = cx, cy
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        nx = cx - 1
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        nx = cx + 1
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        ny = cy - 1
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        ny = cy + 1
                    # move if destination open
                    if 0 <= nx < self.maze_cols and 0 <= ny < self.maze_rows and self.maze[ny][nx]['open']:
                        self.maze_player_cell = (nx, ny)
                        self.player.x = sx + nx * self.maze_cell_size + self.maze_cell_size // 2
                        self.player.y = sy + ny * self.maze_cell_size + self.maze_cell_size // 2
                else:
                    if event.key == pygame.K_b:
                        self.try_build_ship()
                    elif event.key == pygame.K_SPACE:
                        # Attack nearby enemies
                        self.player_attack()
                    if event.key == pygame.K_r and self.game_over:
                        self.__init__()
                # Riddle keyboard shortcuts (only when near spider)
                if self.phase == 'riddle':
                    cx = self.WIDTH // 2
                    cy = self.HEIGHT // 2 - 40
                    dist_to_spider = math.hypot(self.player.x - cx, self.player.y - cy)
                    if dist_to_spider <= 140:
                        if event.key == pygame.K_h:
                            self.handle_riddle_choice('Human')
                        elif event.key == pygame.K_a:
                            self.handle_riddle_choice('Alien')
                        elif event.key == pygame.K_d:
                            self.handle_riddle_choice('Dog')
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click
                    mx, my = event.pos
                    if self.phase == 'island':
                        # fire arrow toward click
                        self.fire_arrow(mx, my)
                    elif self.phase == 'riddle':
                        # check buttons only if near spider
                        cx = self.WIDTH // 2
                        cy = self.HEIGHT // 2 - 40
                        dist_to_spider = math.hypot(self.player.x - cx, self.player.y - cy)
                        if dist_to_spider <= 140:
                            choices = ['Human', 'Alien', 'Dog']
                            for i, choice in enumerate(choices):
                                bx = self.WIDTH//2 - 220 + i * 220
                                by = cy + 140
                                rect = pygame.Rect(bx, by, 180, 50)
                                if rect.collidepoint(mx, my):
                                    self.handle_riddle_choice(choice)
        return True

    def handle_riddle_choice(self, choice):
        if choice == 'Human':
            self.game_over = True
            self.show_message('You answered Human. The spider bows. Victory!')
        else:
            # Wrong answer -> restart entire game
            self.show_message('Wrong! The world collapses... Restarting.')
            pygame.time.delay(800)
            self.__init__()
    
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
                # Start final sailing sequence toward the huge island
                self.start_final_sequence()
        else:
            self.show_message("Not enough materials to build a ship!")
    
    def update(self):
        if self.game_over:
            return

        self.game_time += 1

        # Phase updates
        if self.phase == 'sailing':
            # cutscene countdown
            if self.sailing_timer > 0:
                self.sailing_timer -= 1
                if self.sailing_timer == 0:
                    self.begin_maze()

        # Input handling for movement: island/sailing/riddle use free movement; maze uses tile movement handled in events
        keys = pygame.key.get_pressed()
        if self.phase in ('island', 'sailing', 'riddle'):
            self.player.move(keys, self.WIDTH, self.HEIGHT)
            # Prevent leaving the island: clamp player inside island circle
            dx = self.player.x - self.current_island.x
            dy = self.player.y - self.current_island.y
            dist = math.hypot(dx, dy)
            max_dist = self.current_island.radius - self.player.radius - 2
            if dist > max_dist:
                ang = math.atan2(dy, dx)
                self.player.x = self.current_island.x + math.cos(ang) * max_dist
                self.player.y = self.current_island.y + math.sin(ang) * max_dist
            elif self.phase == 'maze':
                # handle maze-specific updates (portal collision by distance)
                sx = (self.WIDTH - self.maze_cols * self.maze_cell_size) // 2
                sy = (self.HEIGHT - self.maze_rows * self.maze_cell_size) // 2
                gx, gy = self.maze_goal_cell
                portal_x = sx + gx * self.maze_cell_size + self.maze_cell_size / 2
                portal_y = sy + gy * self.maze_cell_size + self.maze_cell_size / 2
                if math.hypot(self.player.x - portal_x, self.player.y - portal_y) <= (self.maze_cell_size * 0.6):
                    # touched portal -> riddle sequence
                    self.start_riddle()

        # Collect materials only when on islands
        if self.phase == 'island':
            for material in self.current_island.materials:
                if not material.collected and material.check_collision(self.player):
                    self.player.materials[material.material_type] += 1
                    material.collected = True
                    self.show_message(f"Collected {material.material_type}!")

        # Move enemies only during island phase
        if self.phase == 'island':
            for enemy in self.enemies:
                enemy.move()
                if enemy.check_collision(self.player):
                    self.player.health -= 0.5
                    if self.player.health <= 0:
                        self.game_over = True
                        self.show_message("You were defeated!")

        # Update arrows and check collisions with enemies (only on islands)
        if self.phase == 'island':
            for arrow in self.arrows[:]:
                arrow.update()
                # remove if out of island bounds
                dx = arrow.x - self.current_island.x
                dy = arrow.y - self.current_island.y
                if math.hypot(dx, dy) > self.current_island.radius + 30:
                    try:
                        self.arrows.remove(arrow)
                    except ValueError:
                        pass
                    continue

                # Arrow hits enemy
                for enemy in self.enemies[:]:
                    if math.hypot(enemy.x - arrow.x, enemy.y - arrow.y) <= enemy.radius + arrow.radius:
                        enemy.health -= arrow.damage
                        try:
                            self.arrows.remove(arrow)
                        except ValueError:
                            pass
                        if enemy.health <= 0:
                            self.enemy_killed(enemy)
                        break

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

        if self.phase == 'island':
            # Draw only the current island (player view)
            self.current_island.draw(self.screen)
            # Draw materials on current island
            self.current_island.draw_materials(self.screen)
            # Draw enemies
            for enemy in self.enemies:
                enemy.draw(self.screen)
            # Draw player
            self.player.draw(self.screen)
            # Draw HUD
            self.draw_hud()

        elif self.phase == 'sailing':
            # Show a pirate ship cutscene: centered ship moving toward a huge island silhouette
            ship_x = self.WIDTH // 2
            ship_y = int(self.HEIGHT * (0.6 + 0.18 * (self.sailing_timer / 240)))
            # simple sway/animation for sails
            sway = math.sin(self.game_time / 8.0) * 6

            # distant huge island silhouette (back)
            pygame.draw.ellipse(self.screen, DARK_GREEN, (self.WIDTH//2 - 300, 20, 600, 220))
            pygame.draw.ellipse(self.screen, DARK_BLUE, (self.WIDTH//2 - 300, 40, 600, 220), 6)

            # hull (shaded)
            hull_top = ship_y
            hull_points = [
                (ship_x - 120, hull_top + 30),
                (ship_x - 80, hull_top + 10),
                (ship_x + 80, hull_top + 10),
                (ship_x + 120, hull_top + 30),
                (ship_x + 60, hull_top + 50),
                (ship_x - 60, hull_top + 50),
            ]
            pygame.draw.polygon(self.screen, BROWN, hull_points)
            pygame.draw.polygon(self.screen, BLACK, hull_points, 2)

            # deck
            pygame.draw.rect(self.screen, (120, 70, 30), (ship_x - 70, hull_top - 4, 140, 14))

            # mast
            mast_x = ship_x
            mast_top = hull_top - 120
            pygame.draw.line(self.screen, DARK_GREY, (mast_x, hull_top - 6), (mast_x, mast_top), 6)

            # sails (two square sails + jib) with slight sway
            sail1 = [(mast_x + 6, mast_top + 20 + sway), (mast_x + 6 + 70, mast_top + 50 + sway), (mast_x + 6, mast_top + 80 + sway)]
            sail2 = [(mast_x - 4, mast_top + 60 - sway), (mast_x - 4 + 90, mast_top + 95 - sway), (mast_x - 4, mast_top + 130 - sway)]
            pygame.draw.polygon(self.screen, WHITE, sail1)
            pygame.draw.polygon(self.screen, BLACK, sail1, 2)
            pygame.draw.polygon(self.screen, WHITE, sail2)
            pygame.draw.polygon(self.screen, BLACK, sail2, 2)

            # jib (small triangular sail at bow)
            jib = [(ship_x + 80, hull_top + 10), (ship_x + 140, hull_top - 10), (mast_x + 6, mast_top + 30 + sway)]
            pygame.draw.polygon(self.screen, WHITE, jib)
            pygame.draw.polygon(self.screen, BLACK, jib, 2)

            # flag at top
            flag_pts = [(mast_x, mast_top - 8), (mast_x + 34, mast_top - 4 + sway * 0.2), (mast_x, mast_top + 4)]
            pygame.draw.polygon(self.screen, PURPLE, flag_pts)

            # small wake under hull
            for i in range(-3, 4):
                wx = ship_x + i * 30
                wy = hull_top + 70 + (i % 2) * 6
                pygame.draw.ellipse(self.screen, LIGHT_BLUE, (wx - 18, wy + (i % 2) * 2, 36, 10))

            # Message (cutscene text)
            if self.message_timer > 0:
                msg_text = self.font_medium.render(self.message, True, YELLOW)
                self.screen.blit(msg_text, (self.WIDTH // 2 - msg_text.get_width() // 2, 20))

        elif self.phase == 'maze' and self.maze is not None:
            # Draw top-down maze centered on screen
            sx = (self.WIDTH - self.maze_cols * self.maze_cell_size) // 2
            sy = (self.HEIGHT - self.maze_rows * self.maze_cell_size) // 2
            # draw cells
            for y in range(self.maze_rows):
                for x in range(self.maze_cols):
                    cell = self.maze[y][x]
                    cx = sx + x * self.maze_cell_size
                    cy = sy + y * self.maze_cell_size
                    # floor
                    pygame.draw.rect(self.screen, SAND if cell['open'] else DARK_GREY, (cx, cy, self.maze_cell_size, self.maze_cell_size))
                    # walls
                    if not cell['open']:
                        pygame.draw.rect(self.screen, BLACK, (cx, cy, self.maze_cell_size, self.maze_cell_size), 2)
            # draw portal at goal
            gx, gy = self.maze_goal_cell
            px = sx + gx * self.maze_cell_size + self.maze_cell_size // 4
            py = sy + gy * self.maze_cell_size + self.maze_cell_size // 4
            pygame.draw.ellipse(self.screen, PURPLE, (px, py, self.maze_cell_size//2, self.maze_cell_size//2))
            # draw player (already positioned)
            self.player.draw(self.screen)

        elif self.phase == 'riddle':
            # draw spider and choices
            # spider body
            cx = self.WIDTH // 2
            cy = self.HEIGHT // 2 - 40
            pygame.draw.circle(self.screen, DARK_GREY, (cx, cy), 60)
            pygame.draw.circle(self.screen, BLACK, (cx, cy), 60, 3)
            # eyes
            pygame.draw.circle(self.screen, YELLOW, (cx - 18, cy - 8), 8)
            pygame.draw.circle(self.screen, YELLOW, (cx + 18, cy - 8), 8)
            # legs (simple lines)
            for i in range(8):
                ang = math.pi * (i / 8.0) - 0.5
                ex = cx + int(math.cos(ang) * 110)
                ey = cy + int(math.sin(ang) * 60)
                pygame.draw.line(self.screen, BLACK, (cx + int(math.cos(ang) * 40), cy + int(math.sin(ang) * 40)), (ex, ey), 4)
            # draw player so they can walk up to the spider
            self.player.draw(self.screen)

            # only present riddle and choices when player is near the spider
            dist_to_spider = math.hypot(self.player.x - cx, self.player.y - cy)
            approach_dist = 140
            if dist_to_spider <= approach_dist:
                # riddle text
                rtext = self.font_medium.render('"What has 4 legs in the morning, 2 legs in the afternoon, and 3 legs at night?"', True, WHITE)
                self.screen.blit(rtext, (self.WIDTH//2 - rtext.get_width()//2, cy + 80))
                # choices
                choices = ['Human', 'Alien', 'Dog']
                for i, choice in enumerate(choices):
                    bx = self.WIDTH//2 - 220 + i * 220
                    by = cy + 140
                    rect = pygame.Rect(bx, by, 180, 50)
                    pygame.draw.rect(self.screen, GREY, rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 2)
                    t = self.font_medium.render(choice, True, BLACK)
                    self.screen.blit(t, (bx + rect.width//2 - t.get_width()//2, by + rect.height//2 - t.get_height()//2))
            else:
                hint = self.font_small.render("Approach the spider to hear its riddle (use arrow keys)", True, YELLOW)
                self.screen.blit(hint, (self.WIDTH//2 - hint.get_width()//2, cy + 100))

        # Draw game over overlay if needed or HUD when in island
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

    def player_attack(self):
        # simple melee attack around player
        attack_range = 30
        attack_damage = 15
        for enemy in self.enemies[:]:
            if math.hypot(enemy.x - self.player.x, enemy.y - self.player.y) <= attack_range:
                enemy.health -= attack_damage
                if enemy.health <= 0:
                    self.enemy_killed(enemy)

    def enemy_killed(self, enemy):
        # enemy may hold a material; drop that preferentially
        if getattr(enemy, "held_material", None):
            drop = enemy.held_material
        else:
            drop = random.choice(["metal", "rope", "wood", "stone", "metal"])
        self.player.materials[drop] = self.player.materials.get(drop, 0) + 1
        try:
            self.enemies.remove(enemy)
        except ValueError:
            pass
        self.show_message(f"Defeated enemy and gained {drop}!")

    def fire_arrow(self, target_x, target_y):
        # create an arrow from player toward target
        dx = target_x - self.player.x
        dy = target_y - self.player.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        vx = (dx / dist) * 12
        vy = (dy / dist) * 12
        self.arrows.append(Arrow(self.player.x + vx*2, self.player.y + vy*2, vx, vy))

if __name__ == "__main__":
    game = IslandAdventure()
    game.run()