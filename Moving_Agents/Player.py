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
        self.vel = Vector.one()
        self.target_vector = None
        self.center = super().calc_center()
        super().__init__(position, size, speed, Constants.PLAYER_COLOR)

    def __str__(self):
        return f"Player size: {self.size}, player position: {self.pos}, player center: {self.center}, player velocity: {self.vel}"

    def update(self, enemies):
        for enemy in enemies:
            self.enemy_positions.append(enemy.pos)
        if self.target_vector == None:
            self.target_vector = self.choose_target()

        # seek_force = self.vel.__sub__(desired_velocity)
        #if pygame.Rect.collidelist(self.rect, target.rect)
        super().update(self.target_vector)

    def choose_target(self):
        target = random.choice(self.enemy_positions)
        return target
