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

    def update(self, bounds, delta_time):
        distance = 0
        boundaries = self.check_boundaries()
        #self.vel = self.update_velocity(self.vel)
        applied_force = self.vel.scale(self.behavior_weight)
        applied_force = applied_force.normalize().scale(delta_time * self.speed)

        applied_force += boundaries
        self.vel = self.update_direction(self.vel, applied_force, self.turn_speed)
        #self.vel = applied_force
        self.vel = self.vel.scale(self.speed)

        
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
            
        if y <= r:
            boundaries.y += (r - y)
        elif y >= h - r - size:
            boundaries.y += (h - r - size - y)
        
        return boundaries.scale(Constants.BOUNDARY_WEIGHT)
        
    # Makes the agent stay within the borders of the screen
    def clamp(self, bounds):
        self.pos.x = max(0, min(self.pos.x, bounds.x - self.size))

        self.pos.y = max(0, min(self.pos.y, bounds.y - self.size))

    # Calculates the center of the agent
    def calc_center(self):
        return self.pos + (Vector.one().scale(self.size / 2))

    # Draws the agent, its debug line, and its image
    def draw(self, screen, line_color):
        self.angle = math.atan2(self.vel.y, self.vel.x) 

        self.angle = math.degrees(self.angle) + 90
        self.surf = pygame.transform.rotate(self.img, -self.angle)
        end_pos = (self.center.x + self.vel.x * 10,
                   self.center.y + self.vel.y * 10)
        screen.blit(self.surf, [self.upper_left.x, self.upper_left.y])

        bound_rect = self.surf.get_bounding_rect()
        bound_rect.move_ip(self.upper_left.x, self.upper_left.y)
        body = pygame.draw.rect(screen, (0, 0, 0), bound_rect, 1)
        debug_line = pygame.draw.line(
            screen, line_color, (self.center.x, self.center.y), end_pos, 3)


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
            diff_vector.normalize_ip()

            # Scale it by the turning speed
            diff_vector.scale(turning_speed)

            # Add it to the current direction
            current_direction += diff_vector

            # Normalize the current direction
            current_direction.normalize_ip()

        return current_direction
