import pygame
import Constants
from Vector import Vector


class Enemy:
    def __init__(self, position, size, speed):
        self.pos = position
        self.size = size
        self.speed = speed
        self.vel = Vector.zero()
        # self.center = Calc_Center()

    def __str__(self):
        print(
            f"Enemy size: {self.size}, enemy position: {self.position}, enemy center: {self.center}")

    def draw(self, screen):
        body = pygame.draw.rect(screen, Constants.PLAYER_COLOR, pygame.Rect(
            self.pos.x, self.pos.y, self.size, self.size))
