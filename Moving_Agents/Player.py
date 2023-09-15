import pygame
from Vector import Vector
import Constants
import random
from Agent import Agent


class Player(Agent):
    def __init__(self, position, size, speed, img):
        super().__init__(position, size, speed, img)
        self.target = None
        self.behavior_weight = Constants.PLAYER_FORCE_WEIGHT
        self.img = img

    def __str__(self):
        return f"Player size: {self.size}, player position: {self.pos}, player center: {self.center}, player velocity: {self.vel}"

    def update(self, enemies, bounds, delta_time):
        if self.vel.x == 0 or super().collision_detection(self.target.rect):
            self.target = enemies[random.randint(0, len(enemies) - 1)]
        self.vel = self.target.pos - self.pos
        print(self.pos)
        super().update(bounds, delta_time)

    def draw(self, screen):
        super().draw(screen, (255, 0, 0))
