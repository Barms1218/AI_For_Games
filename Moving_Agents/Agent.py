import Constants
import pygame
import math
from Vector import Vector
from enum import Enum


class Agent:
    def __init__(self, position, size, speed, img):
        self.pos = position
        self.size = size
        self.speed = speed
        self.vel = Vector.one()
        self.behavior_weight = 0
        self.turn_speed = 0
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)
        self.img = img
        self.angle = 0
        self.surf = pygame.transform.rotate(self.img, self.angle)
        self.upper_left = Vector.zero()
        self.center = self.calc_center()
        self.applied_force = Vector.zero()
        self.boundary_force = Vector.zero()

    def update(self, bounds):

        self.vel = self.update_direction(self.vel, self.applied_force, self.turn_speed)

        self.pos += self.vel

        self.clamp(bounds)

        self.update_rect()

        self.center = self.calc_center()
        
        self.upper_left.x = self.center.x - self.surf.get_width() / 2
        self.upper_left.y = self.center.y - self.surf.get_height() / 2


    # Compares agent position with boundaries of the screen and creates a vector
    # That increases in strength as the agent gets closer and/or gets near more than
    # One boundary
    def check_boundaries(self):
        boundaries = Vector.zero()
        x, y = self.pos.x, self.pos.y
        r = Constants.BOUNDARY_RADIUS
        w, h = Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT
        size = self.size
        
        if x <= r:
            boundaries.x += (r - x)
        elif x >= w - r - size:
            boundaries.x += (w - r - size - x)
        else:
            boundaries.x = 0
            
        if y <= r:
            boundaries.y += (r - y)
        elif y >= h - r - size:
            boundaries.y += (h - r - size - y)
        else:
            boundaries.y = 0
        
        return boundaries
        
    # Makes the agent stay within the borders of the screen
    def clamp(self, bounds):
        self.pos.x = max(0, min(self.pos.x, bounds.x - self.size))

        self.pos.y = max(0, min(self.pos.y, bounds.y - self.size))

    # Calculates the center of the agent
    def calc_center(self):
        return self.pos + (Vector.one().scale(self.size / 2))

    # Draws the agent, its debug line, and its image
    def draw(self, screen):
        # Draws the agent image at the appropriate rotation
        self.angle = math.atan2(self.vel.y, self.vel.x) 
        self.angle = math.degrees(self.angle) + 90
        self.surf = pygame.transform.rotate(self.img, -self.angle)
        screen.blit(self.surf, [self.upper_left.x, self.upper_left.y])

        bound_rect = self.surf.get_bounding_rect()
        bound_rect.move_ip(self.upper_left.x, self.upper_left.y)
        if Constants.DEBUG_BOUNDING_RECTS:
            body = pygame.draw.rect(screen, (0, 0, 0), bound_rect, 1)

        # Velocity line for all agents
        end_pos = (self.center.x + self.vel.x * 25,
                   self.center.y + self.vel.y * 25)
        if Constants.DEBUG_VELOCITY:
            debug_line = pygame.draw.line(
            screen, (0, 255, 0), (self.center.x, self.center.y), end_pos, 3)


    # Checks for a collision between the agent and another rectangle
    def collision_detection(self, rect):
        return pygame.Rect.colliderect(self.rect, rect)

    # Returns the velocity, but normalized
    def update_velocity(self, velocity):
        return velocity.normalize()

    # Updates the rectangle so it is drawn at the proper point
    def update_rect(self):
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size, self.size)

    # Takes the current velocity, target velocity, and turning speed to 
    # create a smoothing effect and make a more realistic turn.
    def update_direction(self, current_direction, target_direction, turning_speed):
        # Calculate the difference vector
        diff_vector = target_direction - current_direction

        # Check if the length of the difference vector is smaller than the turning speed
        if diff_vector.length() < turning_speed:
            current_direction = target_direction
        else:
            # Normalize the difference vector
            diff_vector = diff_vector.normalize()

            # Scale it by the turning speed
            diff_vector = diff_vector.scale(turning_speed)

            # Add it to the current direction
            current_direction += diff_vector

            # Normalize the current direction
            current_direction = current_direction.normalize()

        return current_direction
