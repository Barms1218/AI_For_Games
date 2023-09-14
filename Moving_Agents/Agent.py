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

    def update(self, bounds, delta_time):
        boundary_vector = Vector.zero()
        num_boundaries = 0

        boundaries = list()

        if self.pos.x <= Constants.BOUNDARY_RADIUS:
            distance = Constants.BOUNDARY_RADIUS - self.pos.x
            boundaries.append(Vector(0, self.pos.y))
            num_boundaries += 1
        elif self.pos.x >= Constants.SCREEN_WIDTH - Constants.BOUNDARY_RADIUS - self.size:
            distance = Constants.BOUNDARY_RADIUS - self.pos.x
            boundaries.append(Vector(Constants.SCREEN_WIDTH, self.pos.y))
            num_boundaries += 1
        if self.pos.y <= Constants.BOUNDARY_RADIUS:
            distance = Constants.BOUNDARY_RADIUS - self.pos.x
            boundaries.append(Vector(self.pos.x, 0))
            num_boundaries += 1
        elif self.pos.y >= Constants.SCREEN_HEIGHT - Constants.BOUNDARY_RADIUS - self.size:
            distance = self.pos.y + self.size - \
                (Constants.SCREEN_HEIGHT - Constants.BOUNDARY_RADIUS)
            boundaries.append(Vector(self.pos.x, Constants.SCREEN_HEIGHT))
            num_boundaries += 1

        boundary_force = Vector.zero()
        for i in range(len(boundaries)):
            boundary_force += boundaries[i].normalize()

        boundary_force = self.pos - boundary_force
        boundary_force.scale(boundary_force.length())
        # self.vel += boundary_force

        applied_force = self.vel.scale(
            Constants.PLAYER_FORCE_WEIGHT)
        applied_force = applied_force.normalize().scale(delta_time * self.speed)

        self.vel = applied_force
        self.vel += boundary_force
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

    def update_velocity(self, velocity):
        return velocity.normalize()

    def update_rect(self):
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
