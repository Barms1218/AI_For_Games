import pygame
import Constants
from Vector import Vector


class Enemy:
    def __init__(self, position, size, speed):
        self.pos = position
        self.size = size
        self.speed = speed
        self.vel = Vector.zero()
        self.center = self.calc_center()

    def __str__(self):
        print(
            f"Enemy size: {self.size}, enemy position: {self.position}, enemy center: {self.center}")

    def draw(self, screen):
        body = pygame.draw.rect(screen, Constants.ENEMY_COLOR, pygame.Rect(
            self.pos.x, self.pos.y, self.size, self.size))
        end_pos = (self.center.x + self.vel.x * 125, self.center.y + self.vel.y * 125)
        debug_line = pygame.draw.line(screen, (0, 0, 255), (self.center.x, self.center.y), end_pos, 3)
        
    def calc_center(self):
        return self.pos + (Vector.one().scale(self.size / 2))
