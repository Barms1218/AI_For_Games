import pygame
import Constants
from Vector import Vector
from Agent import Agent


class Enemy(Agent):
    def __init__(self, position, size, speed):
        self.pos = position
        self.size = size
        self.speed = speed
        self.center = super().calc_center()
        super().__init__(position, size, speed, Constants.ENEMY_COLOR)

    def update(self, player):
        player_distance = self.pos.__sub__(player.pos).length()
        # print(player_distance)
        if player_distance < 50:
            super().update(self.pos.__add__(player.pos))

    def __str__(self):
        print(
            f"Enemy size: {self.size}, enemy position: {self.position}, enemy center: {self.center}")
