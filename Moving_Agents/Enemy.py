import pygame
import Constants
from Vector import Vector
from Agent import Agent
import math
import random
from enum import Enum


class State(Enum):
    Wander = 1
    Flee = 2


class Enemy(Agent):
    def __init__(self, position, size, speed):
        super().__init__(position, size, speed, Constants.ENEMY_COLOR)
        self.state = State.Wander
        self.target_vector = None
        self.color = Constants.ENEMY_COLOR
        self.wander_point = None
        self.center = self.calc_center()

    def __str__(self):
        return f"Enemy size: {self.size}, enemy position: {self.pos}, Enemy Velocity: {self.vel}, enemy center: {self.center}"

    def update(self, player):
        behavior_weight = 0
        player_distance = self.pos.__sub__(player.pos).length()

        if self.is_player_close(player_distance) and self.state == State.Wander:
            self.change_state()
            if self.state == State.Flee:
                behavior_weight = Constants.ENEMY_FLEE_WEIGHT
                self.target_vector = self.pos.__sub__(player.pos)
        else:
            theta = math.acos(random.randint(-1, 1))

            wander_direction = Vector(math.cos(theta), math.sin(theta))

            self.target_vector = self.vel + self.pos

            self.target_vector += wander_direction
            if self.state == State.Flee:
                behavior_weight = Constants.ENEMY_WANDER_WEIGHT
                self.change_state()
        super().update_velocity(self.target_vector)
        applied_force = self.normal_velocity.scale(behavior_weight)
        applied_force = applied_force.normalize().scale(Constants.DELTA_TIME)
        self.target_vector = applied_force
        super().update(applied_force)

    def draw(self, screen):
        end_pos = (self.center.x - self.target_vector.x * 1000,
                   self.center.y - self.target_vector.y * 1000)
        if self.state == State.Flee:
            line_color = (255, 0, 0)
        else:
            line_color = (0, 0, 255)

        super().draw(screen, end_pos, line_color)

    def change_state(self):
        if self.state == State.Wander:
            self.state = State.Flee
        else:
            self.state = State.Wander

    def is_player_close(self, player_distance):
        if player_distance < 200 and not self.state == State.Flee:
            return True
        else:
            return False
