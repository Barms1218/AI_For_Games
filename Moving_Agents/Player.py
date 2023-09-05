import pygame
from Vector import Vector
import Constants
import random
import math
from Agent import Agent


class Player(Agent):
    def __init__(self, position, size, speed):
        self.pos = position
        self.size = size
        self.speed = speed
        self.enemy_positions = list()
        self.enemy_distances = list()
        self.center = super().calc_center()
        super().__init__(position, size, speed, Constants.PLAYER_COLOR)

    def __str__(self):
        return f"Player size: {self.size}, player position: {self.pos}, player center: "

    def update(self, enemies):
        target_vector = None
        for enemy in enemies:
            distance = self.pos.__sub__(enemy.pos).length()
            self.enemy_distances.append(distance)
            self.enemy_positions.append(enemy.pos)
        if target_vector == None:
            target_vector = self.choose_target()

        # seek_force = self.vel.__sub__(desired_velocity)

        super().update(target_vector)

    def choose_target(self):
        self.enemy_distances.sort()
        target = random.choice(self.enemy_positions)
        target_vector = self.pos.__sub__(target)
        return target_vector
