import pygame
from Vector import Vector
import Constants


class Player:
    def __init__(self, position, size, speed):
        self.pos = position
        self.size = size
        self.speed = speed
        self.vel = Vector.zero()
        # self.center = Calc_Center()

    def __str__(self):
        return f"Player size: {self.size}, player position: {self.pos}, player center: "

    def draw(self, screen):
        body = pygame.draw.rect(screen, Constants.PLAYER_COLOR, pygame.Rect(
            self.pos.x, self.pos.y, self.size, self.size))

    def Calc_Center(self):
        return Vector(self.position.x + self.size.x, self.position.y - self.size.y)
