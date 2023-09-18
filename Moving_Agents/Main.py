import pygame
from Vector import Vector
import Constants
from Dog import Dog
from Sheep import Sheep
import random

pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode(
    (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT))

flock = list()

sheep_img = pygame.image.load('sheep.png')
dog_img = pygame.image.load('dog.png')

world_bounds = Vector(Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT)
first_tick = pygame.time.get_ticks()
dog = Dog(Vector(Constants.SCREEN_WIDTH * 0.5, Constants.SCREEN_HEIGHT * 0.5),
                Constants.PLAYER_SIZE, Constants.PLAYER_SPEED, dog_img)
for i in range(100):
    sheep = Sheep(Vector(random.uniform(100, Constants.SCREEN_WIDTH), random.uniform(100, Constants.SCREEN_HEIGHT)),
                  Constants.ENEMY_SIZE, Constants.ENEMY_SPEED, sheep_img)
    flock.append(sheep)


def handleDebugging():        
    # Handle the Debugging for Forces
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.KEYUP:

            # Toggle Dog Influence
            if event.key == pygame.K_1:
                Constants.ENABLE_DOG = not Constants.ENABLE_DOG
                print("Toggle Dog Influence", Constants.ENABLE_DOG)

            # Toggle Alignment Influence
            if event.key == pygame.K_2: 
                Constants.ENABLE_ALIGNMENT = not Constants.ENABLE_ALIGNMENT
                print("Toggle Alignment Influence", Constants.ENABLE_ALIGNMENT)

            # Toggle Separation Influence
            if event.key == pygame.K_3: 
                Constants.ENABLE_SEPARATION = not Constants.ENABLE_SEPARATION
                print("Toggle Separation Influence", Constants.ENABLE_SEPARATION)

            # Toggle Cohesion Influence
            if event.key == pygame.K_4: 
                Constants.ENABLE_COHESION = not Constants.ENABLE_COHESION
                print("Toggle Cohesion Influence", Constants.ENABLE_COHESION)

            # Toggle Boundary Influence
            if event.key == pygame.K_5: 
                Constants.ENABLE_BOUNDARIES = not Constants.ENABLE_BOUNDARIES
                print("Toggle Boundary Influence", Constants.ENABLE_BOUNDARIES)

            # Toggle Dog Influence Lines
            if event.key == pygame.K_6: 
                Constants.DEBUG_DOG_INFLUENCE = not Constants.DEBUG_DOG_INFLUENCE
                print("Toggle Dog Influence Lines", Constants.DEBUG_DOG_INFLUENCE)
    
            # Toggle Velocity Lines
            if event.key == pygame.K_7: 
                Constants.DEBUG_VELOCITY = not Constants.DEBUG_VELOCITY
                print("Toggle Velocity Lines", Constants.DEBUG_VELOCITY)

            # Toggle Neighbor Lines
            if event.key == pygame.K_8: 
                Constants.DEBUG_NEIGHBORS = not Constants.DEBUG_NEIGHBORS
                print("Toggle Neighbor Lines", Constants.DEBUG_NEIGHBORS)

            # Toggle Boundary Force Lines
            if event.key == pygame.K_9: 
                Constants.DEBUG_BOUNDARIES = not Constants.DEBUG_BOUNDARIES
                print("Toggle Boundary Force Lines", Constants.DEBUG_BOUNDARIES)

            # Toggle Bounding Box Lines
            if event.key == pygame.K_0: 
                Constants.DEBUG_BOUNDING_RECTS = not Constants.DEBUG_BOUNDING_RECTS
                print("Toggle Bounding Box Lines", Constants.DEBUG_BOUNDING_RECTS)

        if event.type == pygame.QUIT:
            pygame.quit
            quit()

while True:
    handleDebugging()
    tick = pygame.time.get_ticks()
    delta_time = (tick - first_tick) / 1000
    first_tick = tick
    dog.update(flock, world_bounds, delta_time)
    dog.draw(screen)
    for sheep in flock:
        sheep.update(flock, dog, world_bounds, delta_time)
        sheep.draw(screen)

    pygame.display.flip()
    clock.tick(Constants.FRAME_RATE)
    screen.fill(Constants.SCREEN_COLOR)

