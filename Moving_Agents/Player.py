import pygame
from Vector import Vector
import Constants


class Player:
    def __init__(self, position, size, speed):
        self.pos = position
        self.size = size
        self.speed = speed
        self.vel = Vector.zero()
        self.center = self.calc_center()

    def __str__(self):
        return f"Player size: {self.size}, player position: {self.pos}, player center: "

    def update(self):
        keys = pygame.key.get_pressed()
        up = keys[pygame.K_w]
        down = keys[pygame.K_s]
        left = keys[pygame.K_a]
        right = keys[pygame.K_d]
        movement = Vector.zero()
        if up:
            movement.y = movement.y - 1
        if down:
            movement.y = movement.y + 1
        if left:
            movement.x = movement.x - 1
        if right:
            movement.x = movement.x + 1

        self.vel = movement.normalize()
        self.pos += movement
        self.center = self.calc_center()

    def draw(self, screen):
        player_square = pygame.draw.rect(screen, Constants.PLAYER_COLOR, pygame.Rect(
            self.pos.x, self.pos.y, self.size, self.size))
        end_pos = (self.center.x + self.vel.x * 125, self.center.y + self.vel.y * 125)
        debug_line = pygame.draw.line(screen, (0, 0, 255), (self.center.x, self.center.y), end_pos, 3)

    def calc_center(self):
        return self.pos + (Vector.one().scale(self.size / 2))
