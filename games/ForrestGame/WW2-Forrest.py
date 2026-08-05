# Simple WW2-style top-down shooter
# Controls:
# - WASD to move
# - Mouse to aim
# - Left click or Space to shoot
# - Number keys 1-5: buy and equip weapon if unlocked and you have gold
# - U: upgrade current weapon
# - Esc or Q: quit

import math
import random
import pygame

pygame.init()

WIDTH, HEIGHT = 900, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WW2 Forrest - Simple Prototype")
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 20)
BIGFONT = pygame.font.SysFont(None, 40)

# Enemy definitions (health, xp, gold)
ENEMY_TYPES = {
	'soldier': {'hp':100, 'xp':10, 'gold':100, 'color':(200,50,50), 'damage':0.1},
	'general': {'hp':1000, 'xp':30, 'gold':500, 'color':(50,50,200), 'damage':0.5},
	'mercenary': {'hp':3000, 'xp':500, 'gold':1500, 'color':(50,200,50), 'damage':1.0},
}

# Weapons: name, cost, base_damage, unlock_level
WEAPONS = [
	{'name':'Pistol','cost':0,'damage':10,'unlock_level':1},
	{'name':'Rifle','cost':5000,'damage':50,'unlock_level':2},
	{'name':'SMG','cost':20000,'damage':150,'unlock_level':3},
	{'name':'Bazooka','cost':50000,'damage':450,'unlock_level':4},
	{'name':'Nuke','cost':200000,'damage':1000,'unlock_level':5},
]

BASE_XP_FOR_LEVEL = 100000
def xp_required_for(level):
	# xp required to go from level -> level+1
	return BASE_XP_FOR_LEVEL * (2 ** (level-1))


class Player(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		self.x = x
		self.y = y
		self.radius = 14
		self.color = (220,220,100)
		self.health = 1000
		self.max_health = 1000
		self.gold = 0
		self.xp = 0
		self.level = 1
		self.weapon_index = 0
		self.weapon_upgrades = {i:0 for i in range(len(WEAPONS))}
		self.fire_cooldown = 0

	def rect(self):
		return pygame.Rect(self.x-self.radius, self.y-self.radius, self.radius*2, self.radius*2)

	def update_level(self):
		# Level up while xp reaches threshold
		while self.xp >= xp_required_for(self.level):
			req = xp_required_for(self.level)
			self.xp -= req
			self.level += 1

	def current_weapon_damage(self):
		base = WEAPONS[self.weapon_index]['damage']
		up = self.weapon_upgrades[self.weapon_index]
		# triple base damage, each upgrade increases damage by 20%
		return int(base * 3 * (1.2 ** up))


class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, vx, vy, damage):
		super().__init__()
		self.x = x
		self.y = y
		self.vx = vx
		self.vy = vy
		self.damage = damage
		self.radius = 4

	def update(self, dt):
		self.x += self.vx * dt
		self.y += self.vy * dt
		if self.x < -50 or self.y < -50 or self.x > WIDTH+50 or self.y > HEIGHT+50:
			self.kill()

	def draw(self, surf):
		pygame.draw.circle(surf, (255,220,0), (int(self.x), int(self.y)), self.radius)


class Enemy(pygame.sprite.Sprite):
	def __init__(self, etype, x, y):
		super().__init__()
		self.type = etype
		data = ENEMY_TYPES[etype]
		self.hp = data['hp']
		self.max_hp = data['hp']
		self.color = data['color']
		self.x = x
		self.y = y
		self.radius = 12 if etype=='soldier' else (20 if etype=='general' else 28)

	def rect(self):
		return pygame.Rect(self.x-self.radius, self.y-self.radius, self.radius*2, self.radius*2)

	def update(self, dt, castle):
		# move towards castle
		dx = castle['x'] - self.x
		dy = castle['y'] - self.y
		dist = math.hypot(dx,dy) + 1e-6
		speed = 40 if self.type=='soldier' else (25 if self.type=='general' else 15)
		self.x += dx/dist * speed * dt
		self.y += dy/dist * speed * dt

	def draw(self, surf):
		# draw humanoid enemy: head and body
		head_r = max(5, self.radius//2)
		head_x = int(self.x)
		head_y = int(self.y - self.radius//1.5)
		body_w = int(self.radius * 1.2)
		body_h = int(self.radius * 1.3)
		body_rect = pygame.Rect(int(self.x - body_w/2), int(self.y - body_h/2), body_w, body_h)
		pygame.draw.rect(surf, self.color, body_rect)
		pygame.draw.circle(surf, (220,200,170), (head_x, head_y), head_r)
		# hp bar
		bar_w = self.radius*2
		hp_ratio = max(0, self.hp/self.max_hp)
		pygame.draw.rect(surf, (50,50,50), (self.x-self.radius, self.y-self.radius-8, bar_w, 5))
		pygame.draw.rect(surf, (0,200,0), (self.x-self.radius, self.y-self.radius-8, int(bar_w*hp_ratio), 5))


class Missile(pygame.sprite.Sprite):
	def __init__(self, x, y, vx, vy, owner=None):
		super().__init__()
		self.x = x
		self.y = y
		self.vx = vx
		self.vy = vy
		self.owner = owner
		self.radius = 6

	def update(self, dt):
		self.x += self.vx * dt
		self.y += self.vy * dt
		# off-screen
		if self.x < -100 or self.y < -100 or self.x > WIDTH+100 or self.y > HEIGHT+100:
			self.kill()

	def draw(self, surf):
		pygame.draw.circle(surf, (200,120,50), (int(self.x), int(self.y)), self.radius)


class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, radius=60, life=0.6):
		super().__init__()
		self.x = x
		self.y = y
		self.radius = radius
		self.life = life

	def update(self, dt):
		self.life -= dt
		if self.life <= 0:
			self.kill()

	def draw(self, surf):
		alpha = max(0, min(255, int(255 * (self.life / 0.6))))
		s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
		pygame.draw.circle(s, (255,140,0, alpha), (self.radius, self.radius), self.radius)
		surf.blit(s, (int(self.x-self.radius), int(self.y-self.radius)))


class Boss(Enemy):
	def __init__(self, x, y):
		super().__init__('mercenary', x, y)
		self.radius = 60
		self.hp = 5000000
		self.max_hp = 5000000
		self.color = (120,20,160)
		self.shoot_timer = 0.0
		self.speed = 8.0  # advance much slower

	def update(self, dt, castle):
		# slow advance to castle
		dx = castle['x'] - self.x
		dy = castle['y'] - self.y
		dist = math.hypot(dx,dy) + 1e-6
		self.x += dx/dist * self.speed * dt
		self.y += dy/dist * self.speed * dt
		# shooting handled externally via spawn in main loop

	def draw(self, surf):
		# big boss
		pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)
		# hp bar above
		bar_w = 200
		hp_ratio = max(0, self.hp/self.max_hp)
		pygame.draw.rect(surf, (50,50,50), (int(self.x-bar_w/2), int(self.y-self.radius-18), bar_w, 8))
		pygame.draw.rect(surf, (200,30,30), (int(self.x-bar_w/2), int(self.y-self.radius-18), int(bar_w*hp_ratio), 8))


class Ally(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		self.x = x
		self.y = y
		self.hp = 1000
		self.max_hp = 1000
		self.radius = 10
		self.color = (180,180,240)
		self.shoot_cooldown = random.uniform(0.3, 0.9)

	def update(self, dt, player):
		# follow player loosely
		# allies will orbit / hold position near the castle; player passed but we ignore it here
		# keep as-is for compatibility (no movement) unless far from spawn point
		pass

	def try_shoot(self, dt, mx, my, bullets, firing):
		# Allies shoot toward the mouse when the player is firing.
		self.shoot_cooldown -= dt
		if not firing:
			return
		if self.shoot_cooldown > 0:
			return
		self.shoot_cooldown = random.uniform(0.12, 0.4)
		# aim at mouse position
		dx = mx - self.x
		dy = my - self.y
		dist = math.hypot(dx, dy) + 1e-6
		speed_b = 700
		vx = dx/dist*speed_b
		vy = dy/dist*speed_b
		dmg = 50
		spawn_x = self.x + dx/dist * (self.radius + 6)
		spawn_y = self.y + dy/dist * (self.radius + 6)
		bullets.add(Bullet(spawn_x, spawn_y, vx, vy, dmg))

	def draw(self, surf):
		# small humanoid
		pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)
		# hp bar
		bar_w = self.radius*2
		hp_ratio = max(0, self.hp/self.max_hp)
		pygame.draw.rect(surf, (50,50,50), (self.x-self.radius, self.y-self.radius-8, bar_w, 4))
		pygame.draw.rect(surf, (100,200,100), (self.x-self.radius, self.y-self.radius-8, int(bar_w*hp_ratio), 4))


def draw_hud(surf, player, allies_count=0):
	# top-left: health, gold, xp, level
	hx = 8
	hy = 8
	# health
	pygame.draw.rect(surf, (50,50,50), (hx, hy, 220, 24))
	health_w = int(220 * (player.health/player.max_health))
	pygame.draw.rect(surf, (200,50,50), (hx, hy, health_w, 24))
	surf.blit(FONT.render(f'HP: {player.health}/{player.max_health}', True, (255,255,255)), (hx+6, hy+3))

	surf.blit(FONT.render(f'Gold: {player.gold}', True, (255,215,0)), (hx, hy+34))
	surf.blit(FONT.render(f'XP: {player.xp}', True, (180,180,255)), (hx, hy+54))
	surf.blit(FONT.render(f'Level: {player.level}', True, (200,200,200)), (hx+140, hy+34))

	# XP progress to next level
	req = xp_required_for(player.level)
	prog = 0 if req==0 else min(1.0, player.xp/req)
	pygame.draw.rect(surf, (60,60,60), (hx, hy+74, 220, 14))
	pygame.draw.rect(surf, (100,100,255), (hx, hy+74, int(220*prog), 14))
	surf.blit(FONT.render(f'Next: {req} XP', True, (220,220,220)), (hx+6, hy+92))

	# current weapon info
	w = WEAPONS[player.weapon_index]
	surf.blit(FONT.render(f'Weapon: {w["name"]} (Damage: {player.current_weapon_damage()})', True, (255,255,255)), (WIDTH-320, 8))
	surf.blit(FONT.render('Press 1-5 to buy/equip weapon (if unlocked). U to upgrade.', True, (200,200,200)), (WIDTH-420, 30))

	# weapons list
	base_x = WIDTH-420
	base_y = 60
	for i, wep in enumerate(WEAPONS):
		unlocked = (player.level >= wep['unlock_level'])
		owned = (player.weapon_index == i or player.weapon_upgrades.get(i,0) > 0 or wep['cost']==0)
		text = f'{i+1}. {wep["name"]} - Cost: {wep["cost"]} - Dmg: {wep["damage"]} - Unlock L{wep["unlock_level"]}'
		col = (255,255,255) if unlocked else (120,120,120)
		surf.blit(FONT.render(text, True, col), (base_x, base_y + i*22))
		if owned:
			surf.blit(FONT.render('(Owned/Upgradable)', True, (180,240,180)), (base_x+320, base_y + i*22))

	# show allies count
	surf.blit(FONT.render(f'Allies: {allies_count}', True, (200,200,255)), (hx+6, hy+112))


def draw_player(surf, player, mx, my):
	# draw a simple humanoid: head + body and a gun pointing toward mouse
	angle = math.atan2(my - player.y, mx - player.x)
	# body
	body_radius = player.radius
	head_radius = max(6, player.radius // 2)
	body_color = player.color
	head_color = (220, 200, 170)
	# body circle
	pygame.draw.circle(surf, body_color, (int(player.x), int(player.y)), body_radius)
	# head above body
	head_x = int(player.x)
	head_y = int(player.y - body_radius - head_radius//2)
	pygame.draw.circle(surf, head_color, (head_x, head_y), head_radius)
	# gun
	gun_length = body_radius + 12
	gun_width = 6
	gun_end_x = int(player.x + math.cos(angle) * gun_length)
	gun_end_y = int(player.y + math.sin(angle) * gun_length)
	pygame.draw.line(surf, (40,40,40), (int(player.x), int(player.y)), (gun_end_x, gun_end_y), gun_width)
	# muzzle
	pygame.draw.circle(surf, (255,200,0), (gun_end_x, gun_end_y), 3)


def main():
	# castle placed near center; allies will protect it
	castle = {'x': WIDTH//2, 'y': HEIGHT//2, 'hp': 10000, 'max_hp': 10000, 'radius': 60}

	player = Player(WIDTH//2 + 150, HEIGHT//2 + 150)
	bullets = pygame.sprite.Group()
	enemies = pygame.sprite.Group()
	allies = []
	missiles = pygame.sprite.Group()
	explosions = pygame.sprite.Group()
	boss = None
	boss_spawned = False

	# spawn 500 allied soldiers arranged in concentric rings around the castle
	for i in range(500):
		angle = (i / 500.0) * (2 * math.pi)
		radius_ring = 90 + (i % 5) * 6
		rx = castle['x'] + math.cos(angle) * radius_ring
		ry = castle['y'] + math.sin(angle) * radius_ring
		allies.append(Ally(rx, ry))

	fire_rate = 0.25  # seconds
	spawn_timer = 0.0
	spawn_cooldown = 1.0
	explosion_damage = 300
	running = True
	win = False

	while running:
		dt = CLOCK.tick(60) / 1000.0
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
					running = False
				if event.key == pygame.K_u:
					# upgrade current weapon
					idx = player.weapon_index
					wep = WEAPONS[idx]
					upgrade_level = player.weapon_upgrades.get(idx,0)
					cost = wep['cost'] + 1000*(upgrade_level+1)
					if player.gold >= cost:
						player.gold -= cost
						player.weapon_upgrades[idx] = upgrade_level + 1
				if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
					idx = event.key - pygame.K_1
					if idx < len(WEAPONS):
						wep = WEAPONS[idx]
						if player.level >= wep['unlock_level']:
							# if not owned, attempt buy
							if player.gold >= wep['cost'] and wep['cost']>0 and player.weapon_index!=idx:
								player.gold -= wep['cost']
								player.weapon_index = idx
							else:
								# if cost == 0 or already affordable, equip if already bought or free
								if wep['cost']==0 or player.weapon_index==idx or player.weapon_upgrades.get(idx,0)>0:
									player.weapon_index = idx

		keys = pygame.key.get_pressed()
		mx, my = pygame.mouse.get_pos()
		# movement
		speed = 200
		if keys[pygame.K_a]:
			player.x -= speed*dt
		if keys[pygame.K_d]:
			player.x += speed*dt
		if keys[pygame.K_w]:
			player.y -= speed*dt
		if keys[pygame.K_s]:
			player.y += speed*dt

		# shooting
		mouse_pressed = pygame.mouse.get_pressed()[0]
		if (mouse_pressed or keys[pygame.K_SPACE]) and player.fire_cooldown <= 0:
			# fire a bullet towards mouse
			dx = mx - player.x
			dy = my - player.y
			dist = math.hypot(dx,dy) + 1e-6
			speed_b = 600
			vx = dx/dist*speed_b
			vy = dy/dist*speed_b
			dmg = player.current_weapon_damage()
			# spawn at gun tip so bullets don't appear from the body
			gun_length = player.radius + 12
			spawn_x = player.x + dx/dist * gun_length
			spawn_y = player.y + dy/dist * gun_length
			b = Bullet(spawn_x, spawn_y, vx, vy, dmg)
			bullets.add(b)
			player.fire_cooldown = fire_rate

		if player.fire_cooldown > 0:
			player.fire_cooldown -= dt

		# spawn enemies
		spawn_timer -= dt
		# decrease cooldown with player.level
		level_factor = max(1, player.level)
		cur_cd = max(0.15, spawn_cooldown / (1 + (level_factor-1)*0.2))
		if spawn_timer <= 0 and not win:
			spawn_timer = cur_cd
			# spawn logic: ring formations often, boss on level 5
			if player.level >= 5 and not boss_spawned:
				# spawn boss once at a random edge
				side = random.choice(['top','bottom','left','right'])
				if side == 'top':
					bx, by = WIDTH//2, -200
				elif side == 'bottom':
					bx, by = WIDTH//2, HEIGHT+200
				elif side == 'left':
					bx, by = -200, HEIGHT//2
				else:
					bx, by = WIDTH+200, HEIGHT//2
				boss = Boss(bx, by)
				enemies.add(boss)
				boss_spawned = True
				# also spawn some heavy waves around outer ring
				for i in range(500):
					a = random.random() * 2 * math.pi
					r = 420 + random.randint(-40, 80)
					x = castle['x'] + math.cos(a) * r
					y = castle['y'] + math.sin(a) * r
					enemies.add(Enemy('soldier', x, y))
				continue
			# otherwise, sometimes spawn a large ring
			if random.random() < 0.35:
				count = 500
				radius_ring = 300 + player.level * 40
				for i in range(count):
					a = (i / count) * (2 * math.pi)
					x = castle['x'] + math.cos(a) * (radius_ring + random.uniform(-20,20))
					y = castle['y'] + math.sin(a) * (radius_ring + random.uniform(-20,20))
					enemies.add(Enemy('soldier', x, y))
				continue
			# single spawn fallback
			if player.level < 3:
				type_choices = ['soldier']
			elif player.level < 5:
				type_choices = ['soldier']*70 + ['general']*20 + ['mercenary']*10
			else:
				type_choices = ['soldier']*55 + ['general']*30 + ['mercenary']*15
			type_choice = random.choice(type_choices)
			# spawn at random edge
			side = random.choice(['top','bottom','left','right'])
			if side == 'top':
				x = random.randint(0, WIDTH)
				y = -30
			elif side == 'bottom':
				x = random.randint(0, WIDTH)
				y = HEIGHT + 30
			elif side == 'left':
				x = -30
				y = random.randint(0, HEIGHT)
			else:
				x = WIDTH + 30
				y = random.randint(0, HEIGHT)
			enemies.add(Enemy(type_choice, x, y))

		# update bullets
		for b in list(bullets):
			b.update(dt)

		# update missiles
		for m in list(missiles):
			m.update(dt)
			# missile collision with castle/player/allies/enemies -> explode
			# castle
			if math.hypot(m.x-castle['x'], m.y-castle['y']) < m.radius + castle['radius']:
				explosions.add(Explosion(m.x, m.y, radius=80))
				m.kill()
				# apply explosion damage below when explosion created
				continue
			# player
			if math.hypot(m.x-player.x, m.y-player.y) < m.radius + player.radius:
				explosions.add(Explosion(m.x, m.y, radius=80))
				m.kill()
				continue
			# allies
			for a in list(allies):
				if math.hypot(m.x-a.x, m.y-a.y) < m.radius + a.radius:
					explosions.add(Explosion(m.x, m.y, radius=80))
					m.kill()
					break
			# enemies (missile hitting an enemy also explodes)
			for e2 in list(enemies):
				if math.hypot(m.x-e2.x, m.y-e2.y) < m.radius + e2.radius:
					explosions.add(Explosion(m.x, m.y, radius=80))
					m.kill()
					break

		# update explosions and apply damage once on creation
		for ex in list(explosions):
			ex.update(dt)
			# apply damage immediately (only once) by checking a flag
			if getattr(ex, 'applied', False):
				continue
			# apply to castle
			for ent in []:
				pass
			# damage castle
			if math.hypot(ex.x-castle['x'], ex.y-castle['y']) <= ex.radius:
				castle['hp'] -= explosion_damage
			# damage player
			if math.hypot(ex.x-player.x, ex.y-player.y) <= ex.radius:
				player.health -= explosion_damage
			# damage allies
			for a in list(allies):
				if math.hypot(ex.x-a.x, ex.y-a.y) <= ex.radius:
					a.hp -= explosion_damage
					if a.hp <= 0:
						try:
							allies.remove(a)
						except ValueError:
							pass
			# damage enemies
			for e3 in list(enemies):
				if math.hypot(ex.x-e3.x, ex.y-e3.y) <= ex.radius:
					e3.hp -= explosion_damage
					if e3.hp <= 0:
						r = ENEMY_TYPES[e3.type]
						player.gold += r['gold']
						player.xp += r['xp']
						enemies.remove(e3)
			# mark applied
			ex.applied = True

		# update allies (they shoot toward mouse when player fires and die when hp <= 0)
		for a in list(allies):
			a.update(dt, player)
			# allies follow the player's firing direction: pass mx,my and mouse state
			a.try_shoot(dt, mx, my, bullets, mouse_pressed)
			if a.hp <= 0:
				try:
					allies.remove(a)
				except ValueError:
					pass

		# update enemies
		for e in list(enemies):
			e.update(dt, castle)
			# collision with castle
			if math.hypot(e.x-castle['x'], e.y-castle['y']) < e.radius + castle['radius']:
				dmg = ENEMY_TYPES[e.type]['damage']
				castle['hp'] -= dmg
				# knockback enemy a bit
				ang = math.atan2(e.y-castle['y'], e.x-castle['x'])
				e.x += math.cos(ang)*10
				e.y += math.sin(ang)*10
				# if castle falls, game over
				if castle['hp'] <= 0:
					running = False

			# collision with allies
			for a in list(allies):
				if math.hypot(e.x-a.x, e.y-a.y) < e.radius + a.radius:
					# enemy and ally trade damage
					# ally takes enemy damage
					a.hp -= ENEMY_TYPES[e.type]['damage']
					# ally deals damage to enemy
					e.hp -= 50
					# knockback
					ang2 = math.atan2(e.y-a.y, e.x-a.x)
					e.x += math.cos(ang2)*8
					e.y += math.sin(ang2)*8
					if a.hp <= 0:
						try:
							allies.remove(a)
						except ValueError:
							pass


		# bullets -> enemies
		for b in list(bullets):
			for e in list(enemies):
				if math.hypot(b.x-e.x, b.y-e.y) < b.radius + e.radius:
					e.hp -= b.damage
					b.kill()
					if e.hp <= 0:
						# reward
						r = ENEMY_TYPES[e.type]
						player.gold += r['gold']
						player.xp += r['xp']
						enemies.remove(e)
					break

		# update player level based on xp
		prev_level = player.level
		player.update_level()
		if player.level != prev_level:
			# leveling may unlock weapons
			pass

		# check win: if player has passed level 5 requirement
		if player.level > 5:
			win = True

		# draw
		SCREEN.fill((34,34,34))
		# draw player
		draw_player(SCREEN, player, mx, my)
		# draw castle
		castle_rect = pygame.Rect(int(castle['x']-castle['radius']), int(castle['y']-castle['radius']), castle['radius']*2, castle['radius']*2)
		pygame.draw.rect(SCREEN, (120,80,40), castle_rect)
		# castle hp bar
		hp_w = 240
		hp_ratio = max(0, castle['hp']/castle['max_hp'])
		pygame.draw.rect(SCREEN, (40,40,40), (WIDTH//2 - hp_w//2, 12, hp_w, 18))
		pygame.draw.rect(SCREEN, (200,50,50), (WIDTH//2 - hp_w//2, 12, int(hp_w*hp_ratio), 18))
		# draw bullets
		for b in bullets:
			b.draw(SCREEN)
		# draw allies
		for a in allies:
			a.draw(SCREEN)
		# draw enemies
		for e in enemies:
			e.draw(SCREEN)

		draw_hud(SCREEN, player, len(allies))

		if win:
			txt = BIGFONT.render('You beat the war! Congratulations!', True, (240,240,200))
			SCREEN.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - txt.get_height()//2))

		pygame.display.flip()

	pygame.quit()


if __name__ == '__main__':
	main()

