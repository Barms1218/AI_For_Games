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
        normalized_velocity = self.vel.normalize()
        desired_velocity = normalized_velocity.scale(self.speed)
        self.pos += desired_velocity
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
        self.center = self.calc_center()


    def draw(self, screen):
        body = pygame.draw.rect(screen, self.color, self.rect)
        end_pos = (self.center.x + self.vel.x * 50.0,
                   self.center.y + self.vel.y * 50.0)
        debug_line = pygame.draw.line(
            screen, (0, 0, 255), (self.center.x, self.center.y), end_pos, 3)

    def calc_center(self):
        return self.pos + (Vector.one().scale(self.size / 2))
    
    def collision_detection(rect):
        collision = pygame.Rect.colliderect(self.rect, rect)
