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
        self.wander_point = None
        self.center = self.calc_center()

    def __str__(self):
        return f"Enemy size: {self.size}, enemy position: {self.pos}, Enemy Velocity: {self.vel}, enemy center: {self.center}"

    def update(self, player, bounds):
        player_vector = self.pos - player.pos
        player_distance = player_vector.length()

        if self.is_player_close(player_distance):   
            self.fleeing = True
            self.vel = player_vector
        else:
            self.fleeing = False
            # get angle between -1 and 1
            angle = random.uniform(-1, 1)

            angle = math.acos(angle)

            if random.randint(0, 100) > 50:
                angle += math.pi
                
            # create wander direction with cos and sin of angle
            wander_direction = Vector(math.cos(angle), math.sin(angle))

            wander_point = self.pos + self.vel

            wander_point += wander_direction

            self.vel = wander_point - self.pos
            # wanderpoint += wanderdirection

        super().update(bounds)

    def draw(self, screen):
        line_color = (0, 0, 255)
        if self.fleeing:
            line_color = (255, 0, 0)

        super().draw(screen, line_color)

    def is_player_close(self, distance):
        if distance < Constants.ENEMY_RANGE:
            return True
        else:
            return False


