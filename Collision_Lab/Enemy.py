import pygame
import Constants
from Vector import Vector
from Agent import Agent
import math
import random


class Enemy(Agent):
    def __init__(self, position, size, speed):
        super().__init__(position, size, speed, Constants.ENEMY_COLOR)
        self.fleeing = False
        self.target_vector = None
        self.color = Constants.ENEMY_COLOR
        self.wander_point = None
        self.center = self.calc_center()

    def __str__(self):
        return f"Enemy size: {self.size}, enemy position: {self.pos}, Enemy Velocity: {self.vel}, enemy center: {self.center}"

    def update(self, player):
        self.target_vector = self.pos.__sub__(player.pos)
        player_distance = self.pos.__sub__(player.pos).length()

        if player_distance < 200:
            self.fleeing = True
            super().update(self.target_vector)
        else:
            # get angle between -1 and 1
            theta = math.acos(random.randint(-1, 1))
            # create wander direction with cos and sin of angle
            wander_direction = Vector(math.cos(theta), math.sin(theta))
            # if random number > 50 add 180

            # wanderpoint = velocity + position
            self.target_vector = self.vel + self.pos
            # wanderpoint += wanderdirection
            self.target_vector += wander_direction
            self.fleeing = False
            self.center = self.calc_center()
            super().update(self.target_vector)

    def draw(self, screen):
        line_color = (0, 0, 255)
        end_pos = (self.center.x - self.target_vector.x,
                   self.center.y - self.target_vector.y)
        if self.fleeing:
            line_color = (255, 0, 0)

        super().draw(screen, end_pos, line_color)
