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
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
        self.color = color

    def update(self, bounds):
        self.update_velocity()

        self.vel = self.vel.scale(self.speed)

        self.pos += self.vel

        self.pos.x = max(0, min(self.pos.x, bounds.x - self.size))

        self.pos.y = max(0, min(self.pos.y, bounds.y - self.size))

        self.update_rect()

        self.center = self.calc_center()

    def draw(self, screen, line_color):
        end_pos = (self.center.x + self.vel.x * 25,
                   self.center.y + self.vel.y * 25)
        body = pygame.draw.rect(screen, self.color, self.rect)
        debug_line = pygame.draw.line(
            screen, line_color, (self.center.x, self.center.y), end_pos, 3)

    def calc_center(self):
        return self.pos + (Vector.one().scale(self.size / 2))

    def collision_detection(self, rect):
        return pygame.Rect.colliderect(self.rect, rect)
    
    def update_velocity(self):
        self.vel = self.vel.normalize()
    
    def update_rect(self):
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
