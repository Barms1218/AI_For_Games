import pygame

# screen values

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_COLOR = (100, 149, 237)
FRAME_RATE = 60

# player values
PLAYER_COLOR = (255, 255, 0)
PLAYER_SPEED = 5.5
PLAYER_SIZE = 10
PLAYER_FORCE_WEIGHT = 0.5
PLAYER_TURN_SPEED = 0.4

# enemy values
ENEMY_START = 100
ENEMY_SIZE = 10
ENEMY_SPEED = 5.0
ENEMY_COLOR = (0, 255, 0)
ENEMY_RANGE = 200
ENEMY_WANDER_WEIGHT = 0.5
ENEMY_FLEE_WEIGHT = 0.5
ENEMY_TURN_SPEED = 0.1

# Agent values
BOUNDARY_WEIGHT = 1
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
