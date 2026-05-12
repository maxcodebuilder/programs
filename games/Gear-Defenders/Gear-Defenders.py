import pygame
import math

class Enemy(pygame.sprite.Sprite):
    def __init__(self, waypoints):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 0, 0)) # Red square for enemy
        self.rect = self.image.get_rect()
        self.waypoints = waypoints
        self.target_waypoint = 0
        self.pos = pygame.Vector2(waypoints[0])
        self.rect.center = self.pos
        self.speed = 2

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
            self.kill() # Reached the end
