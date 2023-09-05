import pygame
from Vector import Vector
import Constants
import random
import math


class Player:
    def __init__(self, position, size, speed):
        self.pos = position
        self.size = size
        self.speed = speed
        self.vel = Vector.zero()
        self.center = self.calc_center()
        self.enemy_positions = list()
        self.enemy_distances = list()

    def __str__(self):
        return f"Player size: {self.size}, player position: {self.pos}, player center: "

    def update(self, enemies):
        for enemy in enemies:
            distance = self.pos.__sub__(enemy.pos).length
            self.enemy_distances.append(distance)
            self.enemy_positions.append(enemy.pos)
            
        target = random.choice(self.enemy_positions)
        target_vector = self.pos.__sub__(target)
        print(distance)
        desired_velocity = target_vector.scale(self.speed)
        seek_force = self.vel.__sub__(desired_velocity)
        self.pos -= desired_velocity.normalize()
        self.center = self.calc_center()

    def draw(self, screen):
        player_square = pygame.draw.rect(screen, Constants.PLAYER_COLOR, pygame.Rect(
            self.pos.x, self.pos.y, self.size, self.size))
        end_pos = (self.center.x + self.vel.x * 125, self.center.y + self.vel.y * 125)
        debug_line = pygame.draw.line(screen, (0, 0, 255), (self.center.x, self.center.y), end_pos, 3)

    def calc_center(self):
        return self.pos + (Vector.one().scale(self.size / 2))
