import pygame
from Vector import Vector
import Constants
import random
from Agent import Agent


class Player(Agent):
    def __init__(self, position, size, speed):
        super().__init__(position, size, speed, Constants.PLAYER_COLOR)
        self.target_vector = None
        self.target = None
        self.center = self.calc_center()


    def __str__(self):
        return f"Player size: {self.size}, player position: {self.pos}, player center: {self.center}, player velocity: {self.vel}"

    def update(self, enemies):
        if self.target_vector == None or super().collision_detection(self.target.rect):
            self.target = enemies[random.randint(0, len(enemies) - 1)]
        self.target_vector = self.target.pos
            
        super().update(self.target_vector)


    def draw(self, screen):
        end_pos = (self.center.x - self.target_vector.x * 10,
                   self.center.y - self.target_vector.y * 10)
        super().draw(screen, end_pos, (255, 0 , 0))
        # debug_line = pygame.draw.line(
        #     screen, (255, 0, 0), (self.center.x, self.center.y), (self.target.center.x, self.target.center.y), 3)
