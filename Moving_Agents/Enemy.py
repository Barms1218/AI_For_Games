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
        # Calculated in wander and flee state, then used in force calculation
        self.target_vector = Vector.zero()
        self.color = Constants.ENEMY_COLOR
        self.wander_point = Vector.zero()
        self.state = State.Wander
        self.wander_point = None
        self.center = self.calc_center()

    def __str__(self):
        return f"Enemy size: {self.size}, enemy position: {self.pos}, Enemy Destination: {self.vel}, enemy center: {self.center}"

    def update(self, player, bounds, delta_time):
        behavior_weight = 0
        player_vector = self.pos - player.pos
        player_distance = player_vector.length()

        if self.is_player_close(player_distance):   
            self.change_state(State.Flee)
            self.vel = player_vector
            behavior_weight = Constants.ENEMY_FLEE_WEIGHT
        else:
            self.change_state(State.Wander)

            behavior_weight = Constants.ENEMY_WANDER_WEIGHT

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
        #normal_velocity = super().update_velocity()
        applied_force = self.vel.scale(behavior_weight)
        normalized_force = applied_force.normalize().scale(self.speed)
        self.vel = normalized_force
        super().update(bounds)

    def draw(self, screen):
        line_color = (0, 0, 255)
        if self.state == State.Flee:
            line_color = (255, 0, 0)
        else:
            line_color = (0, 0, 255)

        super().draw(screen, line_color)

    def is_player_close(self, distance):
        if distance <= Constants.ENEMY_RANGE:
            return True
        else:
            return False
    def change_state(self, desired_state):
        if self.state != desired_state:
            self.state = desired_state


