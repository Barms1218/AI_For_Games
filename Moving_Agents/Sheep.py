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
class Sheep(Agent):
    def __init__(self, position, size, speed, img):
        super().__init__(position, size, speed, img)
        self.state = State.Wander
        # Calculated in wander and flee state, then used in force calculation
        self.wander_point = Vector.zero()
        self.state = State.Wander
        self.wander_point = None
        self.img = img
        self.turn_speed = Constants.ENEMY_TURN_SPEED
        self.player_vector = Vector.zero()
        self.neighbors = list()
        self.neighbor_count = 0
        self.player = None

    def __str__(self):
        return f"Enemy size: {self.size}, enemy position: {self.pos}, Enemy Destination: {self.vel}, enemy center: {self.center}"

    def update(self, flock, player, bounds, delta_time):
        self.player = player
        for sheep in flock:
            if sheep is not self and self.sheep_is_neighbor(sheep, Constants.NEIGHBOR_RADIUS):
                self.neighbors.append(sheep)
                self.neighbor_count += 1
            elif sheep in self.neighbors and not self.sheep_is_neighbor(sheep, Constants.NEIGHBOR_RADIUS):
                    self.neighbors.remove(sheep)
                    self.neighbor_count -= 1
        
        # Reset force vector every frame
        dog_force = Vector.zero()
        self.applied_force = Vector.zero()

        # Know where the player is
        self.player_vector = self.pos - player.pos
        player_distance = self.player_vector.length()

        alignment = self.compute_alignment(self.neighbors)
        cohesion = self.compute_cohesion(self.neighbors)
        separation = self.compute_separation(self.neighbors)

        if self.is_player_close(player_distance):
            self.change_state(State.Flee)
            self.player_vector = self.player_vector.normalize()
            dog_force = self.player_vector
        else:
            self.change_state(State.Wander)
        
        self.boundary_force = super().check_boundaries()
        
        self.applied_force += (alignment.scale(Constants.ALIGNMENT_WEIGHT)) + \
            cohesion.scale(Constants.COHESION_WEIGHT) + \
                separation.scale(Constants.SEPARATION_WEIGHT) + \
                    dog_force.scale(Constants.DOG_WEIGHT) + \
                        self.boundary_force.scale(Constants.BOUNDARY_WEIGHT)
        self.applied_force = self.applied_force.normalize().scale(delta_time * self.speed)
        
        super().update(bounds)

    # Tells the agent draw what color to make the debug line.
    def draw(self, screen):
        if self.state == State.Flee:
            pygame.draw.line(screen, (255, 0, 0), (self.center.x, self.center.y),
                             (self.player.center.x, self.player.center.y), 1)
        for sheep in self.neighbors:
            pygame.draw.line(screen, (0, 0, 255), (self.center.x, self.center.y), 
                             (sheep.center.x, sheep.center.y), 1)
        super().draw(screen)


    #region Flocking Methods
    def compute_alignment(self, flock):
        neighbor_count = 0
        alignment_vector = Vector.zero()

        for sheep in flock:
            alignment_vector += sheep.vel

        if self.neighbor_count == 0:
            return alignment_vector
        
        alignment_vector.x /= self.neighbor_count
        alignment_vector.y /= self.neighbor_count

        return alignment_vector.normalize()
    
    def compute_cohesion(self, flock):
        neighbor_count = 0
        cohesion_vector = Vector.zero()

        for sheep in flock:
            cohesion_vector += sheep.pos

        if self.neighbor_count == 0:
            return cohesion_vector
        
        cohesion_vector.x /= self.neighbor_count
        cohesion_vector.y /= self.neighbor_count

        cohesion_vector.x -= self.pos.x
        cohesion_vector.y -= self.pos.y

        return cohesion_vector.normalize()
    
    def compute_separation(self, flock):
        neighbor_count = 0
        separation_vector = Vector.zero()

        for sheep in flock:
            separation_vector += (sheep.pos - self.pos)

        if self.neighbor_count == 0:
            return separation_vector
        
        separation_vector.x /= self.neighbor_count
        separation_vector.y /= self.neighbor_count

        separation_vector = separation_vector.scale(-1)

        return separation_vector.normalize()  

    #endregion


    #region Detection Methods
    '''
    Return true if player agent is within range, otherwise false.
    '''
    def is_player_close(self, distance):
        if distance <= Constants.ENEMY_RANGE:
            return True
        else:
            return False
        
    def sheep_is_neighbor(self, sheep, range):
        if (self.pos - sheep.pos).length() < range:
            return True
        else:
            return False
    #endregion


    '''
    Makes the agent state be the state it should be
    '''
    def change_state(self, desired_state):
        if self.state != desired_state:
            self.state = desired_state
        
        


        




