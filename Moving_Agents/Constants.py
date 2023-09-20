import pygame

# screen values

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_COLOR = (100, 149, 237)
FRAME_RATE = 60

# Dog values
PLAYER_SPEED = 10.5
PLAYER_SIZE = 10
PLAYER_FORCE_WEIGHT = 0.5
PLAYER_TURN_SPEED = 0.4

# Sheep values
ENEMY_START = 100
ENEMY_SIZE = 10
ENEMY_SPEED = 5.0
ENEMY_RANGE = 200
ENEMY_FLEE_WEIGHT = 0.5
ENEMY_TURN_SPEED = 0.1
NEIGHBOR_RADIUS = 50

# Agent values
BOUNDARY_RADIUS = 50
DELTA_TIME = 60 / 1000
BODY_WIDTH = 16
BODY_HEIGHT = 32

# Debugging
ENABLE_DOG = True
ENABLE_ALIGNMENT = True
ENABLE_COHESION = True
ENABLE_SEPARATION = True
ENABLE_BOUNDARIES = True

DEBUGGING = True
DEBUG_LINE_WIDTH = 1
DEBUG_VELOCITY = DEBUGGING
DEBUG_BOUNDARIES = DEBUGGING
DEBUG_NEIGHBORS = DEBUGGING
DEBUG_DOG_INFLUENCE = DEBUGGING
DEBUG_BOUNDING_RECTS = DEBUGGING

# Flocking Force Weights
BOUNDARY_WEIGHT = 1
DOG_WEIGHT = 0.2
ALIGNMENT_WEIGHT = 0.3
SEPARATION_WEIGHT = 0.325
COHESION_WEIGHT = 0.3
