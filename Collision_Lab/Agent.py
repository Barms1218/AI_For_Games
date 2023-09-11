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

    def update(self, target_vector):
        self.vel = target_vector - self.pos
        normalized_velocity = self.update_velocity(self.vel)
        self.pos += normalized_velocity.scale(self.speed)
        self.pos.x = max(0, min(self.pos.x, Constants.SCREEN_WIDTH))
        self.pos.y = max(0, min(self.pos.y, Constants.SCREEN_HEIGHT))
        self.update_rect()
        self.center = self.calc_center()

    def draw(self, screen, end_pos, line_color):
        body = pygame.draw.rect(screen, self.color, self.rect)
        debug_line = pygame.draw.line(
            screen, line_color, (self.center.x, self.center.y), end_pos, 3)

    def calc_center(self):
        return self.pos + (Vector.one().scale(self.size / 2))

    def collision_detected(self, rect):
        return pygame.Rect.colliderect(self.rect, rect)

    def update_rect(self):
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)

    def update_velocity(self, velocity):
        return velocity.normalize()
