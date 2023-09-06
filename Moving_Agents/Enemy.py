import pygame
import Constants
from Vector import Vector
from Agent import Agent
import math
import random


class Enemy(Agent):
    def __init__(self, position, size, speed):
        self.pos = position
        self.size = size
        self.speed = speed
        self.vel = Vector.one()
        self.center = super().calc_center()
        super().__init__(position, size, speed, Constants.ENEMY_COLOR)

    def __str__(self):
        print(
            f"Enemy size: {self.size}, enemy position: {self.position}, enemy center: {self.center}")

    def update(self, player):
        player_vector = self.pos.__sub__(player.pos)
        player_distance = self.pos.__sub__(player.pos).length()

        if player_distance < 50:
            super().update(player_vector)
        else:
            # get angle between -1 and 1
            theta = math.acos(random.randint(-1, 1))
            # create wander direction with cos and sin of angle
            wander_direction = Vector(math.cos(theta), math.sin(theta))
            # if random number > 50 add 180

            # wanderpoint = velocity + position
            wander_point = self.vel + self.pos
            # wanderpoint += wanderdirection
            wander_point += wander_direction
            super().update(wander_point)
