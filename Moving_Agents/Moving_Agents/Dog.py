import pygame
from Vector import Vector
import Constants
import random
from Agent import Agent


class Dog(Agent):
    def __init__(self, position, size, speed, img):
        super().__init__(position, size, speed, img)
        self.target = None
        self.behavior_weight = Constants.PLAYER_FORCE_WEIGHT
        self.img = img
        self.turn_speed = Constants.PLAYER_TURN_SPEED

    def __str__(self):
        return f"Player size: {self.size}, player position: {self.pos}, player center: {self.center}, player velocity: {self.vel}"

    def update(self, enemies, bounds, delta_time):
        target_vector = Vector.zero()
        if self.target == None:
            self.target = enemies[random.randint(0, len(enemies) - 1)]
        elif super().collision_detection(self.target.rect):
            self.target = enemies[random.randint(0, len(enemies) - 1)]

        target_vector = (self.target.pos - self.pos).normalize()

        self.boundary_force = super().check_boundaries()
        
        self.applied_force = target_vector.scale(self.behavior_weight)
        self.applied_force = self.applied_force.normalize().scale(delta_time * self.speed)

        self.applied_force += self.boundary_force

        super().update(bounds)

    # Tells the agent draw what color to make the debug line.
    def draw(self, screen):
        end_pos = (self.target.center.x, self.target.center.y)
        debug_line = pygame.draw.line(
            screen, (255, 0, 0), (self.center.x, self.center.y), end_pos, 3)
        super().draw(screen)
