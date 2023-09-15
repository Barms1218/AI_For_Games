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
    def __init__(self, position, size, speed, img):
        self.pos = position
        self.size = size
        self.speed = speed
        self.vel = Vector.zero()
        self.behavior_weight = 0
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
        self.img = img
        self.angle = 0
        self.surf = pygame.transform.rotate(self.img, self.angle)
        self.upper_left = Vector.zero()
        self.center = self.calc_center()

    def update(self, bounds, delta_time):
        boundary_vector = Vector.zero()
        distance = 0
        boundaries = Vector.zero()

        if self.pos.x <= Constants.BOUNDARY_RADIUS:
            distance = Constants.BOUNDARY_RADIUS - self.pos.x
            boundaries += Vector(self.pos.x, distance).normalize()
        elif self.pos.x >= Constants.SCREEN_WIDTH - Constants.BOUNDARY_RADIUS - self.size:
            distance = abs(Constants.SCREEN_WIDTH - (self.pos.x + Constants.BOUNDARY_RADIUS))
            boundaries += Vector(-self.pos.x, distance).normalize()
        if self.pos.y <= Constants.BOUNDARY_RADIUS:
            distance = Constants.BOUNDARY_RADIUS - self.pos.y
            boundaries += Vector(distance, self.pos.y).normalize()
        elif self.pos.y >= Constants.SCREEN_HEIGHT - Constants.BOUNDARY_RADIUS - self.size:
            distance = abs(Constants.SCREEN_HEIGHT - (self.pos.y + Constants.BOUNDARY_RADIUS))
            boundaries += Vector(distance, -self.pos.y).normalize()

        boundaries = boundaries.scale(Constants.BOUNDARY_WEIGHT)

        applied_force = self.vel.scale(self.behavior_weight)
        applied_force = applied_force.normalize().scale(delta_time * self.speed)

        applied_force += boundaries

        self.vel = applied_force
        self.vel = self.vel.scale(self.speed)

        self.pos += self.vel

        self.clamp(bounds)

        self.update_rect()

        self.center = self.calc_center()
        self.upper_left.x = self.center.x - self.surf.get_width() / 2
        self.upper_left.y = self.center.y - self.surf.get_height() / 2
        

    def clamp(self, bounds):
        self.pos.x = max(0, min(self.pos.x, bounds.x - self.size))

        self.pos.y = max(0, min(self.pos.y, bounds.y - self.size))

    def calc_center(self):
        return self.pos + (Vector.one().scale(self.size / 2))

    def draw(self, screen, line_color):
        self.angle = math.atan2(self.vel.y, self.vel.x) 

        self.angle = math.degrees(self.angle) - 45
        self.surf = pygame.transform.rotate(self.img, self.angle)
        end_pos = (self.center.x + self.vel.x * 25,
                   self.center.y + self.vel.y * 25)
        screen.blit(self.surf, [self.upper_left.x, self.upper_left.y])
        #body = pygame.draw.rect(screen, self.color, self.rect)
        debug_line = pygame.draw.line(
            screen, line_color, (self.center.x, self.center.y), end_pos, 3)



    def collision_detection(self, rect):
        return pygame.Rect.colliderect(self.rect, rect)

    def update_velocity(self, velocity):
        return velocity.normalize()

    def update_rect(self):
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
