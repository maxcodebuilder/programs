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
	'soldier': {'hp':100, 'xp':10, 'gold':100, 'color':(200,50,50), 'damage':10},
	'general': {'hp':1000, 'xp':30, 'gold':500, 'color':(50,50,200), 'damage':40},
	'mercenary': {'hp':3000, 'xp':500, 'gold':1500, 'color':(50,200,50), 'damage':80},
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

	def update(self, dt, player):
		# move towards player
		dx = player.x - self.x
		dy = player.y - self.y
		dist = math.hypot(dx,dy) + 1e-6
		speed = 40 if self.type=='soldier' else (25 if self.type=='general' else 15)
		self.x += dx/dist * speed * dt
		self.y += dy/dist * speed * dt

	def draw(self, surf):
		pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)
		# hp bar
		bar_w = self.radius*2
		hp_ratio = max(0, self.hp/self.max_hp)
		pygame.draw.rect(surf, (50,50,50), (self.x-self.radius, self.y-self.radius-8, bar_w, 5))
		pygame.draw.rect(surf, (0,200,0), (self.x-self.radius, self.y-self.radius-8, int(bar_w*hp_ratio), 5))


def draw_hud(surf, player):
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


def main():
	player = Player(WIDTH//2, HEIGHT//2)
	bullets = pygame.sprite.Group()
	enemies = pygame.sprite.Group()

	fire_rate = 0.25  # seconds
	spawn_timer = 0.0
	spawn_cooldown = 1.0
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
			b = Bullet(player.x + dx/dist*(player.radius+6), player.y + dy/dist*(player.radius+6), vx, vy, dmg)
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
			# choose type weights
			if player.level < 3:
				choices = ['soldier']*85 + ['general']*12 + ['mercenary']*3
			elif player.level < 5:
				choices = ['soldier']*70 + ['general']*20 + ['mercenary']*10
			else:
				choices = ['soldier']*55 + ['general']*30 + ['mercenary']*15
			etype = random.choice(choices)
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
			enemies.add(Enemy(etype, x, y))

		# update bullets
		for b in list(bullets):
			b.update(dt)

		# update enemies
		for e in list(enemies):
			e.update(dt, player)
			# collision with player
			if math.hypot(e.x-player.x, e.y-player.y) < e.radius + player.radius:
				# damage player
				dmg = ENEMY_TYPES[e.type]['damage']
				player.health -= dmg
				# knockback enemy a bit
				ang = math.atan2(e.y-player.y, e.x-player.x)
				e.x += math.cos(ang)*10
				e.y += math.sin(ang)*10
				if player.health <= 0:
					running = False

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
		pygame.draw.circle(SCREEN, player.color, (int(player.x), int(player.y)), player.radius)
		# draw bullets
		for b in bullets:
			b.draw(SCREEN)
		# draw enemies
		for e in enemies:
			e.draw(SCREEN)

		draw_hud(SCREEN, player)

		if win:
			txt = BIGFONT.render('You beat the war! Congratulations!', True, (240,240,200))
			SCREEN.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - txt.get_height()//2))

		pygame.display.flip()

	pygame.quit()


if __name__ == '__main__':
	main()

