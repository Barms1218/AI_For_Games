import Constants
import pygame
import math
from Vector import Vector
from enum import Enum

class Boundaries(Enum):
    left = 0
    top = 0
    right = Constants.SCREEN_WIDTH
    bottom = Constants.SCREEN_HEIGHT


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
        boundary_vector = Vector.zero()
        num_boundaries = 0
        boundaries = list()
        if self.pos.x - Constants.BOUNDARY_RADIUS <= 0:
            boundaries.append(0)
            num_boundaries += 1
        elif self.pos.x + Constants.BOUNDARY_RADIUS >= Constants.SCREEN_WIDTH:
            boundaries.append(Constants.SCREEN_WIDTH)
            num_boundaries += 1
        if self.pos.y - Constants.BOUNDARY_RADIUS <= 0:
            boundaries.append(0) 
            num_boundaries += 1
        elif self.pos.y + Constants.BOUNDARY_RADIUS >= Constants.SCREEN_HEIGHT:
            boundaries.append(Constants.SCREEN_HEIGHT) 
            num_boundaries += 1

        for i in range(len(boundaries)):
            if i == 0 or i == Constants.SCREEN_WIDTH:
                boundary_vector.x = i
            if i == 0 or i == Constants.SCREEN_HEIGHT:
                boundary_vector.y = i
        
        print(boundary_vector)

        self.vel = self.vel.scale(self.speed)

        self.pos += self.vel

        self.clamp(bounds)

        self.update_rect()

        self.center = self.calc_center()

    def clamp(self, bounds):
        self.pos.x = max(0, min(self.pos.x, bounds.x - self.size))

        self.pos.y = max(0, min(self.pos.y, bounds.y - self.size))

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
        return self.vel.normalize()
    
    def update_rect(self):
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
