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

    def update(self, enemies, delta_time):
        if self.target_vector == None or super().collision_detected(self.target.rect):
            self.target = enemies[random.randint(0, len(enemies) - 1)]
        self.target_vector = self.target.pos.__sub__(self.pos)
        super().update_velocity(self.target_vector)
        applied_force = self.normal_velocity.scale(
            Constants.PLAYER_FORCE_WEIGHT)
        applied_force = applied_force.normalize().scale(delta_time)
        self.target_vector = applied_force
        super().update(applied_force)

    def draw(self, screen):
        end_pos = (self.center.x + self.target_vector.x,
                   self.center.y + self.target_vector.y)
        super().draw(screen, end_pos, (255, 0, 0))
