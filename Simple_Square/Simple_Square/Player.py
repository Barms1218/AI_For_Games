import pygame
from Vector import Vector
import Game_Numbers


class Player:
    def __init__(self, position, size, color):
        self.position = position
        self.velocity = Vector(0, 0)
        self.size = size
        self.color = color
        self.center = position + (Vector.one().scale(self.size / 2))

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

        self.velocity = movement.normalize()
        # self.position += self.velocity + Vector(1.0, 1.0)
        self.position += movement
        self.center = self.position + (Vector.one().scale(self.size / 2))

    def draw(self, screen):
        player_square = pygame.draw.rect(screen, self.color, pygame.Rect(
            self.position.x, self.position.y, self.size, self.size))
        center = Vector(player_square.centerx, player_square.centery)
        end_pos = (self.center.x + self.velocity.x * 50,
                   self.center.y + self.velocity.y * 50)
        debug_line = pygame.draw.line(
            screen, (0, 0, 255), (self.center.x, self.center.y), end_pos, 3)
