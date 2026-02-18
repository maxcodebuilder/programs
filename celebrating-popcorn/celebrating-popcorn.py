import pygame
import random
import math

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 36)

# Level Definitions
LEVELS = {
    1: {
        'name': 'BUTTER',
        'spawn_chance': 0.05,
        'projectile_speed': 2,
        'color': (255, 200, 100),
        'time_limit': 60,
        'boss_hp': 1000,
        'damage_range': (1, 3)
    },
    2: {
        'name': 'SALT SHAKER',
        'spawn_chance': 0.10,
        'projectile_speed': 2,
        'color': (200, 200, 200),
        'time_limit': 60,
        'boss_hp': 5000,
        'damage_range': (4, 6)
    },
    3: {
        'name': 'FIRE',
        'spawn_chance': 0.50,
        'projectile_speed': 2,
        'color': (255, 100, 0),
        'time_limit': 60,
        'boss_hp': 10000,
        'damage_range': (7, 9),
        'heal_range': (10, 15)
    },
    4: {
        'name': 'MAGNETRON',
        'spawn_chance': 1.00,
        'projectile_speed': 2,
        'color': (255, 0, 100),
        'time_limit': 60,
        'boss_hp': 15000,
        'damage_range': (10, 15),
        'heal_range': (16, 30)
    }
}

# Game State
current_level = 1
level_data = LEVELS[current_level]
level_start_time = pygame.time.get_ticks()
level_survived = 0
lives = 2.0
MAX_HP = 2.0
in_self_destruct = False
self_destruct_start_time = 0
boss_health = 0
boss_pos = [400, 100]
boss_radius = 30
special_move_timer = 0
special_move_cooldown = 0
current_special_move = None
attack_cooldown = 180  # 3 seconds at 60 FPS
last_attack_time = 0
player_attack = None

# Kernel (Player) Properties
player_pos = [400, 300]
player_radius = 15
is_popped = False

# Projectile Properties
projectiles = []
lasers = []  # Lasers for Fire and Magnetron
laser_timer = 0  # Timer for laser shooting
mini_fires = []  # Mini fires spawned by Fire boss
mini_fire_timer = 0  # Timer for mini fire spawning
boss_shoot_timer = 0  # Timer for boss shooting bullets
# Player beam when attacking
player_beam = None
player_beam_timer = 0
# Eating mechanic cooldown
eat_cooldown = 15  # frames between eats
eat_timer = 0

def spawn_projectile():
    side = random.choice(['top', 'bottom', 'left', 'right'])
    speed = level_data['projectile_speed']
    if side == 'top': return [random.randint(0, 800), 0, 0, speed]
    if side == 'bottom': return [random.randint(0, 800), 600, 0, -speed]
    if side == 'left': return [0, random.randint(0, 600), speed, 0]
    if side == 'right': return [800, random.randint(0, 600), -speed, 0]

def advance_level():
    global current_level, level_data, level_start_time, projectiles, in_self_destruct, self_destruct_start_time, boss_health, special_move_cooldown, current_special_move, last_attack_time, player_attack, lasers, laser_timer, mini_fires, mini_fire_timer, boss_shoot_timer
    in_self_destruct = True
    self_destruct_start_time = pygame.time.get_ticks()
    projectiles = []
    lasers = []
    mini_fires = []
    laser_timer = 0
    mini_fire_timer = 0
    boss_shoot_timer = 0
    boss_health = level_data['boss_hp']
    special_move_cooldown = 0
    current_special_move = None
    last_attack_time = 0
    player_attack = None
    player_beam = None
    player_beam_timer = 0
    return True

def start_next_level():
    global current_level, level_data, level_start_time, in_self_destruct, lives, special_move_cooldown, current_special_move, last_attack_time, player_attack
    if current_level < 4:
        current_level += 1
        level_data = LEVELS[current_level]
        level_start_time = pygame.time.get_ticks()
        in_self_destruct = False
        projectiles.clear()
        lives = 2
        special_move_cooldown = 0
        current_special_move = None
        last_attack_time = 0
        player_attack = None
    else:
        return False
    return True

def draw_boss():
    """Draw boss based on current level"""
    if current_level == 1:  # BUTTER - stick of butter
        pygame.draw.rect(screen, (255, 220, 100), (boss_pos[0] - 20, boss_pos[1] - 30, 40, 60))
        pygame.draw.rect(screen, (255, 200, 50), (boss_pos[0] - 18, boss_pos[1] - 28, 36, 56))
    elif current_level == 2:  # SALT SHAKER
        # Salt shaker body
        pygame.draw.polygon(screen, (200, 200, 200), [
            (boss_pos[0] - 20, boss_pos[1]),
            (boss_pos[0] + 20, boss_pos[1]),
            (boss_pos[0] + 15, boss_pos[1] + 40),
            (boss_pos[0] - 15, boss_pos[1] + 40)
        ])
        # Top cap
        pygame.draw.rect(screen, (100, 100, 100), (boss_pos[0] - 18, boss_pos[1] - 15, 36, 15))
        # Holes
        pygame.draw.circle(screen, (50, 50, 50), (boss_pos[0] - 8, boss_pos[1] - 5), 2)
        pygame.draw.circle(screen, (50, 50, 50), (boss_pos[0] + 8, boss_pos[1] - 5), 2)
    elif current_level == 3:  # FIRE - flame
        # Flame shape
        points = [
            (boss_pos[0], boss_pos[1] - 35),
            (boss_pos[0] - 15, boss_pos[1] - 10),
            (boss_pos[0] - 10, boss_pos[1] + 20),
            (boss_pos[0], boss_pos[1] + 25),
            (boss_pos[0] + 10, boss_pos[1] + 20),
            (boss_pos[0] + 15, boss_pos[1] - 10)
        ]
        pygame.draw.polygon(screen, (255, 100, 0), points)
        pygame.draw.polygon(screen, (255, 200, 0), [(p[0], p[1] + 3) for p in points])
    elif current_level == 4:  # MAGNETRON - blue orb
        pygame.draw.circle(screen, (0, 100, 255), boss_pos, boss_radius)
        pygame.draw.circle(screen, (100, 150, 255), (boss_pos[0] - 8, boss_pos[1] - 8), 8)

def do_special_move():
    """Execute boss special move"""
    global current_special_move, special_move_timer
    
    if current_level == 1:  # BUTTER - 2 special moves
        if current_special_move == 1:
            # Rapid fire in all directions
            for i in range(8):
                angle = (i / 8) * 2 * math.pi
                speed = 6
                projectiles.append([boss_pos[0], boss_pos[1], speed * math.cos(angle), speed * math.sin(angle)])
        elif current_special_move == 2:
            # Spread shot
            for i in range(5):
                angle = (i - 2) * 0.3
                speed = 5
                projectiles.append([boss_pos[0], boss_pos[1], speed * math.cos(angle), speed * math.sin(angle)])
    
    elif current_level == 2:  # SALT SHAKER
        if current_special_move == 1:
            # Rain of salt - many projectiles falling
            for i in range(12):
                projectiles.append([random.randint(100, 700), boss_pos[1], random.uniform(-2, 2), 4])
        elif current_special_move == 2:
            # Two-way spread
            for i in range(6):
                angle = (i / 6) * math.pi + math.pi / 12
                speed = 5
                projectiles.append([boss_pos[0], boss_pos[1], speed * math.cos(angle), speed * math.sin(angle)])
    
    elif current_level == 3:  # FIRE
        if current_special_move == 1:
            # Inferno - many fast projectiles
            for i in range(16):
                angle = (i / 16) * 2 * math.pi
                speed = 7
                projectiles.append([boss_pos[0], boss_pos[1], speed * math.cos(angle), speed * math.sin(angle)])
        elif current_special_move == 2:
            # Fire wave - projectiles in expanding arcs
            for i in range(10):
                angle = (i / 10) * 2 * math.pi + (random.random() * 0.5)
                speed = 6
                projectiles.append([boss_pos[0], boss_pos[1], speed * math.cos(angle), speed * math.sin(angle)])
    
    elif current_level == 4:  # MAGNETRON
        if current_special_move == 1:
            # Magnetic pulse - spiraling projectiles
            for i in range(20):
                angle = (i / 20) * 2 * math.pi
                speed = 8
                projectiles.append([boss_pos[0], boss_pos[1], speed * math.cos(angle), speed * math.sin(angle)])
        elif current_special_move == 2:
            # Gravity well - projectiles converge from edges
            for i in range(15):
                if i < 8:
                    projectiles.append([random.choice([50, 750]), random.randint(100, 500), random.uniform(-2, 2), random.uniform(-2, 2)])
                else:
                    projectiles.append([random.randint(100, 700), random.choice([50, 550]), random.uniform(-2, 2), random.uniform(-2, 2)])

running = True
while running:
    screen.fill((255, 240, 200)) # Popcorn-themed background
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and lives <= 0:
                # Restart the game
                current_level = 1
                level_data = LEVELS[current_level]
                level_start_time = pygame.time.get_ticks()
                is_popped = False
                lives = MAX_HP
                projectiles = []
                lasers = []
                mini_fires = []
                boss_shoot_timer = 0
                player_beam = None
                player_beam_timer = 0
                player_pos = [400, 300]
                in_self_destruct = False
                last_attack_time = 0
                player_attack = None
            # space eating is handled per-frame to be more responsive
            # Attack selection during boss fight
            elif in_self_destruct and last_attack_time <= 0:
                if current_level == 1:  # BUTTER
                    if event.key == pygame.K_1:
                        player_attack = {'name': 'Kernel Poke', 'beam_type': 1}
                        last_attack_time = attack_cooldown
                    elif event.key == pygame.K_2:
                        player_attack = {'name': 'Butter Jab', 'beam_type': 2}
                        last_attack_time = attack_cooldown
                    elif event.key == pygame.K_3:
                        player_attack = {'name': 'Spread Strike', 'beam_type': 3}
                        last_attack_time = attack_cooldown
                elif current_level == 2:  # SALT SHAKER
                    if event.key == pygame.K_1:
                        player_attack = {'name': 'Salt Pinch', 'beam_type': 1}
                        last_attack_time = attack_cooldown
                    elif event.key == pygame.K_2:
                        player_attack = {'name': 'Grain Grind', 'beam_type': 2}
                        last_attack_time = attack_cooldown
                    elif event.key == pygame.K_3:
                        player_attack = {'name': 'Shaker Smash', 'beam_type': 3}
                        last_attack_time = attack_cooldown
                elif current_level == 3:  # FIRE
                    if event.key == pygame.K_1:
                        player_attack = {'name': 'Cool Splash', 'beam_type': 1}
                        last_attack_time = attack_cooldown
                    elif event.key == pygame.K_2:
                        player_attack = {'name': 'Heat Block', 'beam_type': 2}
                        last_attack_time = attack_cooldown
                    elif event.key == pygame.K_3:
                        player_attack = {'name': 'Flame Extinguish', 'beam_type': 3}
                        last_attack_time = attack_cooldown
                elif current_level == 4:  # MAGNETRON
                    if event.key == pygame.K_1:
                        player_attack = {'name': 'Magnetic Pulse', 'beam_type': 1}
                        last_attack_time = attack_cooldown
                    elif event.key == pygame.K_2:
                        player_attack = {'name': 'Repel Force', 'beam_type': 2}
                        last_attack_time = attack_cooldown
                    elif event.key == pygame.K_3:
                        player_attack = {'name': 'Overload Burst', 'beam_type': 3}
                        last_attack_time = attack_cooldown

    # Check if level time is complete (start self-destruct phase)
    if not in_self_destruct:
        elapsed = (pygame.time.get_ticks() - level_start_time) / 1000
        if elapsed > level_data['time_limit'] and not is_popped:
            advance_level()
    else:
        # Self-destruct phase - Boss shoots projectiles
        self_destruct_elapsed = (pygame.time.get_ticks() - self_destruct_start_time) / 1000
        
        # Update attack cooldown
        last_attack_time -= 1
        
        # Self-destruct difficulty based on level
        if current_level == 1:  # BUTTER
            spawn_rate = 0.03
        elif current_level == 2:  # SALT SHAKER
            spawn_rate = 0.06
        elif current_level == 3:  # FIRE
            spawn_rate = 0.10
        else:  # MAGNETRON
            spawn_rate = 0.15
        
        # Update special move timers
        special_move_cooldown -= 1
        special_move_timer -= 1
        
        # Check if it's time for a special move
        if special_move_cooldown <= 0 and random.random() < 0.02:
            current_special_move = random.randint(1, 2)
            special_move_timer = 20  # Warning duration
            special_move_cooldown = 180  # Cooldown between special moves
        
        # Execute special move if timer is up
        if special_move_timer == 0 and current_special_move is not None:
            do_special_move()
            # Boss heals after special attack if Fire or Magnetron
            if current_level == 3:  # FIRE
                heal_amount = random.randint(10, 15)
                boss_health = min(level_data['boss_hp'], boss_health + heal_amount)
            elif current_level == 4:  # MAGNETRON
                heal_amount = random.randint(16, 30)
                boss_health = min(level_data['boss_hp'], boss_health + heal_amount)
            current_special_move = None
        
        # Boss shoots projectiles outward (normal attacks) - timer based
        boss_shoot_timer -= 1
        if boss_shoot_timer <= 0:
            # Set shoot interval based on level
            if current_level == 1:  # BUTTER - 5 seconds
                shoot_interval = 300
            elif current_level == 2:  # SALT SHAKER - 3 seconds
                shoot_interval = 180
            elif current_level == 3:  # FIRE - 1.5 seconds
                shoot_interval = 90
            else:  # MAGNETRON - 1 second
                shoot_interval = 60
            
            # Use Butter (level 1) bullet speed for all levels
            speed = 2.5
            
            angle = random.uniform(0, 2 * math.pi)
            projectiles.append([boss_pos[0], boss_pos[1], speed * math.cos(angle), speed * math.sin(angle)])
            boss_shoot_timer = shoot_interval
        
        # Fire and Magnetron shoot lasers occasionally
        laser_timer -= 1
        if laser_timer <= 0:
            if current_level == 3:  # FIRE shoots laser
                if random.random() < 0.3:  # 30% chance per frame
                    angle = random.uniform(0, 2 * math.pi)
                    lasers.append([boss_pos[0], boss_pos[1], angle])
                    laser_timer = 30  # Cooldown between lasers
            elif current_level == 4:  # MAGNETRON shoots laser
                if random.random() < 0.25:  # 25% chance per frame
                    angle = random.uniform(0, 2 * math.pi)
                    lasers.append([boss_pos[0], boss_pos[1], angle])
                    laser_timer = 40  # Cooldown between lasers
        
        # Fire boss spawns mini fires
        if current_level == 3:
            mini_fire_timer -= 1
            if mini_fire_timer <= 0:
                if random.random() < 0.4:  # 40% chance per frame
                    angle = random.uniform(0, 2 * math.pi)
                    speed = 2  # Slow moving
                    mini_fires.append([boss_pos[0], boss_pos[1], speed * math.cos(angle), speed * math.sin(angle)])
                    mini_fire_timer = 60  # Cooldown between spawns
        
        # Process player attack: random damage between 1 and 999 and show a beam
        if player_attack is not None:
            damage = random.randint(1, 999)
            boss_health -= damage
            # create beam to display from player to boss
            player_beam = {
                'type': player_attack.get('beam_type', 1),
                'damage': damage,
                'start': (player_pos[0], player_pos[1]),
                'end': (boss_pos[0], boss_pos[1])
            }
            player_beam_timer = 15  # frames to show beam
            player_attack = None
        
        # Check if boss is defeated
        if boss_health <= 0:
            if not start_next_level():
                # Won all levels!
                print("YOU WON! Beat all 4 levels!")
                running = False

    # 1. Movement Logic
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: player_pos[0] -= 5
    if keys[pygame.K_RIGHT]: player_pos[0] += 5
    if keys[pygame.K_UP]: player_pos[1] -= 5
    if keys[pygame.K_DOWN]: player_pos[1] += 5

    # Keep player in bounds
    player_pos[0] = max(player_radius, min(800 - player_radius, player_pos[0]))
    player_pos[1] = max(player_radius, min(600 - player_radius, player_pos[1]))

    # Eating mechanic (hold SPACE to eat nearby projectile)
    if eat_timer <= 0 and lives > 0:
        if keys[pygame.K_SPACE]:
            for p in projectiles[:]:
                dist = ((p[0]-player_pos[0])**2 + (p[1]-player_pos[1])**2)**0.5
                if dist <= player_radius + 12:
                    projectiles.remove(p)
                    lives = min(MAX_HP, lives + 0.5)
                    eat_timer = eat_cooldown
                    break
    if eat_timer > 0:
        eat_timer -= 1

    # 2. Projectile Logic (normal or self-destruct)
    if not in_self_destruct:
        if random.random() < level_data['spawn_chance']:
            projectiles.append(spawn_projectile())

    for p in projectiles[:]:
        p[0] += p[2] # Move X
        p[1] += p[3] # Move Y
        pygame.draw.circle(screen, level_data['color'], (p[0], p[1]), 10)
        
        # 3. Collision
        if in_self_destruct:
            # In self-destruct, projectiles hit the boss but no damage
            dist = ((p[0]-boss_pos[0])**2 + (p[1]-boss_pos[1])**2)**0.5
            if dist < boss_radius + 10:
                if p in projectiles:
                    projectiles.remove(p)
                continue
        else:
            # Normal level - projectiles hit player
            dist = ((p[0]-player_pos[0])**2 + (p[1]-player_pos[1])**2)**0.5
            if dist < player_radius + 10:
                lives -= 1.0
                is_popped = True
                if lives > 0:
                    is_popped = False
                    player_pos = [400, 300]
        
        # Remove projectiles that go off screen
        if p[0] < -20 or p[0] > 820 or p[1] < -20 or p[1] > 620:
            projectiles.remove(p)

    # Process lasers (for Fire and Magnetron)
    for laser in lasers[:]:
        angle = laser[2]
        laser_start_x = laser[0]
        laser_start_y = laser[1]
        laser_length = 400
        laser_end_x = laser_start_x + laser_length * math.cos(angle)
        laser_end_y = laser_start_y + laser_length * math.sin(angle)
        
        # Draw laser
        pygame.draw.line(screen, (255, 100, 0) if current_level == 3 else (0, 150, 255), 
                        (laser_start_x, laser_start_y), (laser_end_x, laser_end_y), 3)
        
        # Check collision with player
        if not in_self_destruct:
            # Check if player is near the laser line
            px, py = player_pos
            # Simple distance to line calculation
            dx = laser_end_x - laser_start_x
            dy = laser_end_y - laser_start_y
            if dx != 0 or dy != 0:
                t = max(0, min(1, ((px - laser_start_x) * dx + (py - laser_start_y) * dy) / (dx*dx + dy*dy)))
                closest_x = laser_start_x + t * dx
                closest_y = laser_start_y + t * dy
                dist = ((px - closest_x)**2 + (py - closest_y)**2)**0.5
                if dist < player_radius + 5:
                    lives -= 1.0
                    is_popped = True
                    if lives > 0:
                        is_popped = False
                        player_pos = [400, 300]
        
        # Remove laser after it's done (just keep it for one frame for simplicity)
        lasers.remove(laser)

    # Process mini fires (for Fire boss)
    for mf in mini_fires[:]:
        mf[0] += mf[2]  # Move X
        mf[1] += mf[3]  # Move Y
        
        # Draw mini fire as a small orange circle
        pygame.draw.circle(screen, (255, 150, 50), (int(mf[0]), int(mf[1])), 8)
        
        # Check collision with player
        if not in_self_destruct:
            dist = ((mf[0] - player_pos[0])**2 + (mf[1] - player_pos[1])**2)**0.5
            if dist < player_radius + 8:
                lives -= 1.0
                is_popped = True
                if lives > 0:
                    is_popped = False
                    player_pos = [400, 300]
                mini_fires.remove(mf)
                continue
        
        # Remove mini fires that go off screen
        if mf[0] < -20 or mf[0] > 820 or mf[1] < -20 or mf[1] > 620:
            mini_fires.remove(mf)

    # 4. Draw Boss (if in self-destruct phase)
    if in_self_destruct:
        draw_boss()
        
        # Show special move warning
        if special_move_timer > 0:
            warning_text = font.render("SPECIAL MOVE!", True, (255, 0, 0))
            screen.blit(warning_text, (250, 140))
            # Flash effect
            if special_move_timer % 10 < 5:
                pygame.draw.circle(screen, (255, 0, 0), boss_pos, boss_radius + 5, 3)
        
        boss_health_text = small_font.render(f"Boss HP: {max(0, boss_health)}", True, (200, 0, 0))
        screen.blit(boss_health_text, (300, 50))

        # Draw player beam if active
        if player_beam_timer > 0 and player_beam is not None:
            bt = player_beam['type']
            # choose color per beam type
            if bt == 1:
                color = (255, 50, 50)
            elif bt == 2:
                color = (50, 255, 50)
            else:
                color = (50, 150, 255)
            pygame.draw.line(screen, color, player_beam['start'], player_beam['end'], 6)
            # decrement timer
            player_beam_timer -= 1
        
        # Show attack options if ready
        if last_attack_time <= 0:
            attack_text = font.render("ATTACK READY! Press:", True, (0, 200, 0))
            screen.blit(attack_text, (150, 250))
            
            if current_level == 1:  # BUTTER
                attack1_text = small_font.render(f"1: Kernel Poke (1-999 DMG)", True, (100, 255, 100))
                attack2_text = small_font.render(f"2: Butter Jab (1-999 DMG)", True, (100, 255, 100))
                attack3_text = small_font.render(f"3: Spread Strike (1-999 DMG)", True, (100, 255, 100))
            elif current_level == 2:  # SALT SHAKER
                attack1_text = small_font.render(f"1: Salt Pinch (1-999 DMG)", True, (100, 255, 100))
                attack2_text = small_font.render(f"2: Grain Grind (1-999 DMG)", True, (100, 255, 100))
                attack3_text = small_font.render(f"3: Shaker Smash (1-999 DMG)", True, (100, 255, 100))
            elif current_level == 3:  # FIRE
                attack1_text = small_font.render(f"1: Cool Splash (1-999 DMG)", True, (100, 255, 100))
                attack2_text = small_font.render(f"2: Heat Block (1-999 DMG)", True, (100, 255, 100))
                attack3_text = small_font.render(f"3: Flame Extinguish (1-999 DMG)", True, (100, 255, 100))
            elif current_level == 4:  # MAGNETRON
                attack1_text = small_font.render(f"1: Magnetic Pulse (1-999 DMG)", True, (100, 255, 100))
                attack2_text = small_font.render(f"2: Repel Force (1-999 DMG)", True, (100, 255, 100))
                attack3_text = small_font.render(f"3: Overload Burst (1-999 DMG)", True, (100, 255, 100))
            screen.blit(attack1_text, (200, 300))
            screen.blit(attack2_text, (200, 340))
            screen.blit(attack3_text, (200, 380))
        else:
            cooldown_secs = (last_attack_time + 59) // 60  # Round up for display
            cooldown_text = small_font.render(f"Next Attack In: {cooldown_secs}s", True, (200, 100, 0))
            screen.blit(cooldown_text, (250, 300))
    
    # 5. Draw Player (Popcorn Kernel)
    if not is_popped:
        # Draw popcorn kernel shape
        pygame.draw.circle(screen, (255, 255, 100), player_pos, player_radius)
        # Add bumps for popcorn texture
        pygame.draw.circle(screen, (255, 220, 0), (player_pos[0] - 8, player_pos[1] - 8), 6)
        pygame.draw.circle(screen, (255, 220, 0), (player_pos[0] + 8, player_pos[1] - 8), 6)
        pygame.draw.circle(screen, (255, 220, 0), (player_pos[0], player_pos[1] + 10), 7)
        pygame.draw.circle(screen, (255, 240, 150), (player_pos[0] - 5, player_pos[1] - 3), 3)
    else:
        # Popped/hit state - darker
        pygame.draw.circle(screen, (200, 150, 0), player_pos, player_radius)

    # 6. Draw Level Info
    if not in_self_destruct:
        level_text = font.render(f"LEVEL {current_level}: {level_data['name']}", True, (50, 50, 50))
        elapsed = (pygame.time.get_ticks() - level_start_time) / 1000
        time_remaining = max(0, level_data['time_limit'] - int(elapsed))
        time_text = small_font.render(f"Time: {time_remaining}s", True, (50, 50, 50))
        screen.blit(level_text, (20, 20))
        screen.blit(time_text, (20, 70))
    else:
        level_text = font.render(f"BOSS FIGHT!", True, (255, 0, 0))
        screen.blit(level_text, (200, 20))
    
    # Draw lives
    lives_text = small_font.render(f"HP: {lives:.1f}", True, (50, 50, 50))
    screen.blit(lives_text, (600, 20))

    if lives == 0:
        # Immediate auto-restart when player loses
        current_level = 1
        level_data = LEVELS[current_level]
        level_start_time = pygame.time.get_ticks()
        is_popped = False
        lives = 2
        projectiles = []
        lasers = []
        mini_fires = []
        boss_shoot_timer = 0
        player_pos = [400, 300]
        in_self_destruct = False
        last_attack_time = 0
        player_attack = None

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
