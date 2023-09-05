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
        player_distance = self.pos.__sub__(player.pos).length()

        if player_distance < 50:
            super().update(self.pos.__add__(player.pos))
        else:
            # theta = math.acos(random.randint(-1, 1))
            # x_pos = math.cos(theta) - math.sin(theta)
            # y_pos = math.sin(theta) + math.cos(theta)
            wander_angle = random.uniform(0, 2 * math.pi)
            change = random.uniform(-0.5, 0.5)
            wander_angle += change

            # Calculate new velocity vector
            self.vel.x = self.speed * math.cos(wander_angle)
            self.vel.y = self.speed * math.sin(wander_angle)
            super().update(Vector(math.cos(wander_angle), math.sin(wander_angle)))
