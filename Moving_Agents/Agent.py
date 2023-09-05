import Constants
import pygame
import math
from Vector import Vector


class Agent:
    def __init__(self, position, size, speed, color):
        self.pos = position
        self.size = size
        self.speed = speed
        self.vel = Vector.zero()
        self.center = self.calc_center()
        self.color = color

    def update(self, target_vector):
        desired_velocity = target_vector.scale(self.speed)
        self.pos -= desired_velocity.normalize()
        self.center = self.calc_center()

        if self.pos.__sub__(target_vector).length() < 100:
            desired_velocity = target_vector.scale(3)

    def draw(self, screen):
        body = pygame.draw.rect(screen, self.color, pygame.Rect(
            self.pos.x, self.pos.y, self.size, self.size))
        end_pos = (self.center.x + self.vel.x * 125,
                   self.center.y + self.vel.y * 125)
        debug_line = pygame.draw.line(
            screen, (0, 0, 255), (self.center.x, self.center.y), end_pos, 3)

    def calc_center(self):
        return self.pos + (Vector.one().scale(self.size / 2))
