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

WANDER_RING_DISTANCE = 50.0
WANDER_RADIUS = 50.0
class Enemy(Agent):
    def __init__(self, position, size, speed, img):
        super().__init__(position, size, speed, img)
        self.state = State.Wander
        # Calculated in wander and flee state, then used in force calculation
        self.wander_point = Vector.zero()
        self.state = State.Wander
        self.wander_point = None
        self.img = img
        self.turn_speed = Constants.ENEMY_TURN_SPEED

    def __str__(self):
        return f"Enemy size: {self.size}, enemy position: {self.pos}, Enemy Destination: {self.vel}, enemy center: {self.center}"

    def update(self, player, bounds, delta_time):
        player_vector = self.pos - player.pos
        player_distance = player_vector.length()

        if self.is_player_close(player_distance):
            self.change_state(State.Flee)
            self.vel = player_vector
            self.behavior_weight = Constants.ENEMY_FLEE_WEIGHT

        super().update(bounds, delta_time)

    # Tells the agent draw what color to make the debug line.
    def draw(self, screen):
        line_color = (0, 0, 255)
        if self.state == State.Flee:
            line_color = (255, 0, 0)
        else:
            line_color = (0, 0, 255)

        super().draw(screen, line_color)

    '''
    Return true if player agent is within range, otherwise false.
    '''
    def is_player_close(self, distance):
        if distance <= Constants.ENEMY_RANGE:
            return True
        else:
            return False

    '''
    Makes the agent state be the state it should be
    '''
    def change_state(self, desired_state):
        if self.state != desired_state:
            self.state = desired_state



