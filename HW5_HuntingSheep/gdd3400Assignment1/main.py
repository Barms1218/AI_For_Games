import pygame
import random
import Vector
import Agent
import Player
import Sheep
import Constants
import Graph
import Node

from pygame import *
from random import *
from Vector import *
from Agent import *
from Sheep import *
from Player import *
from Graph import *
from Node import *

#################################################################################
# Helper Functions
#################################################################################

def buildPen(graph):
	'''Build the Pen that the sheep will be forced into'''
	X = 0
	Y = 1

	# Add the final pen based on the final gate
	finalGate = Constants.FINAL_GATE

	# Add the final gate to the game
	graph.placeObstacle(Vector(finalGate[0][X], finalGate[0][Y]), (0, 255, 0))
	graph.placeObstacle(Vector(finalGate[0][X] - Constants.GRID_SIZE, finalGate[0][Y]), (0, 255, 0))
	graph.placeObstacle(Vector(finalGate[0][X] - Constants.GRID_SIZE * 2, finalGate[0][Y]), (0, 255, 0))
	graph.placeObstacle(Vector(finalGate[1][X], finalGate[1][Y]), (255, 0, 0))
	graph.placeObstacle(Vector(finalGate[1][X] + Constants.GRID_SIZE, finalGate[1][Y]), (255, 0, 0))
	graph.placeObstacle(Vector(finalGate[1][X] + Constants.GRID_SIZE * 2, finalGate[1][Y]), (255, 0, 0))

	# If the green gate (the first gate) is on the right, paddock goes "up"
	direction = 1

	# Build the left and right sides of the pen
	for y in range(finalGate[0][Y] + direction * Constants.GRID_SIZE, \
					finalGate[0][Y] + direction * Constants.GRID_SIZE * 7, \
					direction * Constants.GRID_SIZE):
		# Place the left side of the pen
		graph.placeObstacle(Vector(finalGate[0][X], y), (0, 0, 0))
		graph.placeObstacle(Vector(finalGate[0][X] - Constants.GRID_SIZE, y), (0, 0, 0))
		graph.placeObstacle(Vector(finalGate[0][X] - Constants.GRID_SIZE * 2, y), (0, 0, 0))
		# Place the right side of the pen
		graph.placeObstacle(Vector(finalGate[1][X], y), (0, 0, 0))
		graph.placeObstacle(Vector(finalGate[1][X] + Constants.GRID_SIZE, y), (0, 0, 0))
		graph.placeObstacle(Vector(finalGate[1][X] + Constants.GRID_SIZE * 2, y), (0, 0, 0))

	# Build the bottom of the pen
	for x in range(finalGate[0][X] + direction * Constants.GRID_SIZE - 3 * Constants.GRID_SIZE, \
					finalGate[1][X] + 3 * Constants.GRID_SIZE, \
					direction * Constants.GRID_SIZE):
		graph.placeObstacle(Vector(x, finalGate[0][Y] + direction * Constants.GRID_SIZE * 6), (0, 0, 0))
		graph.placeObstacle(Vector(x, finalGate[0][Y] + direction * Constants.GRID_SIZE * 7), (0, 0, 0))
		graph.placeObstacle(Vector(x, finalGate[0][Y] + direction * Constants.GRID_SIZE * 8), (0, 0, 0))

	# Return the pen bounds and an "empty" area near the opening to allow the dog space to maneuver the sheep
	return [ Vector(finalGate[0][X] - Constants.GRID_SIZE * 2, \
					finalGate[0][Y] - direction * Constants.GRID_SIZE * 8), \
			 Vector(finalGate[1][X] + Constants.GRID_SIZE * 2, \
					finalGate[0][Y] + direction * Constants.GRID_SIZE * 8) ]

def buildObstacles(graph, pen):
	# Random Obstacles
	for i in range(Constants.NBR_RANDOM_OBSTACLES):

		# Select a random cell to use as the starting cell of an obstacle
		start = Vector(randrange(0, Constants.WORLD_WIDTH), randrange(0, Constants.WORLD_HEIGHT))
		while(pen[0].x <= start.x <= pen[1].x and pen[0].y <= start.y <= pen[1].y):
			start = Vector(randrange(0, Constants.WORLD_WIDTH), randrange(0, Constants.WORLD_HEIGHT))
		graph.placeObstacle(start, (0, 0, 0))

		# Grow a block of contiguous obstacles
		for j in range(randrange(Constants.NBR_RANDOM_OBSTACLES)):
			offset = Vector(randrange(-1, 2, 2) * Constants.GRID_SIZE, 0) if randrange(0, 2) == 1 \
							else Vector(0, (randrange(-1, 2, 2)) * Constants.GRID_SIZE)
			offset = start + offset
			while(offset.x < 0 or offset.y < 0
					or offset.x >= Constants.WORLD_WIDTH - Constants.GRID_SIZE 
					or offset.y >= Constants.WORLD_HEIGHT - Constants.GRID_SIZE
					or (pen[0].x <= offset.x <= pen[1].x and pen[0].y <= offset.y <= pen[1].y)):
				offset = start + Vector(randrange(-1, 2, 2) * Constants.GRID_SIZE, 0) if randrange(0,1) \
							else Vector(0, randrange(-1, 2, 2) * Constants.GRID_SIZE)
			start = offset
			graph.placeObstacle(start, (0, 0, 0))

	# Go through the whole map and place an obstacle in any cell that has 6 or more neighbors
	for i in range(0, Constants.WORLD_WIDTH, Constants.GRID_SIZE):
		for j in range(0, Constants.WORLD_HEIGHT, Constants.GRID_SIZE):
			cell = Vector(i, j)
			node = graph.getNodeFromPoint(cell)
			if len(node.neighbors) <= 2:
				graph.placeObstacle(cell, (0, 0, 0))

def handleEvents():		
	'''Handle the Debugging for Forces and lines'''
	events = pygame.event.get()
	for event in events:
		# Handle the quit event
		if event.type == pygame.QUIT \
			or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
			hasQuit = True

		# Toggle forces and lines on and off
		if event.type == pygame.KEYUP:
			# Toggle Dog Influence
			if event.key == pygame.K_1:
				Constants.ENABLE_DOG = not Constants.ENABLE_DOG
				print("Toggle Dog Influence", Constants.ENABLE_DOG)

			# Toggle Obstacle Influence
			if event.key == pygame.K_2:
				Constants.ENABLE_OBSTACLES = not Constants.ENABLE_OBSTACLES
				print("Toggle Obstacle Influence", Constants.ENABLE_OBSTACLES)

			# Toggle Boundary Influence
			if event.key == pygame.K_3: 
				Constants.ENABLE_BOUNDARIES = not Constants.ENABLE_BOUNDARIES
				print("Toggle Boundary Influence", Constants.ENABLE_BOUNDARIES)

			# Toggle Velocity Lines
			if event.key == pygame.K_7: 
				Constants.DEBUG_VELOCITY = not Constants.DEBUG_VELOCITY
				print("Toggle Velocity Lines", Constants.DEBUG_VELOCITY)

			# Toggle Dog Influence Lines
			if event.key == pygame.K_8: 
				Constants.DEBUG_DOG_INFLUENCE = not Constants.DEBUG_DOG_INFLUENCE
				print("Toggle Dog Influence Lines", Constants.DEBUG_DOG_INFLUENCE)

			# Toggle Obstacle Force Lines
			if event.key == pygame.K_9: 
				Constants.DEBUG_OBSTACLES = not Constants.DEBUG_OBSTACLES
				print("Toggle Obstacle Force Lines", Constants.DEBUG_OBSTACLES)
				
			# Toggle Boundary Force Lines
			if event.key == pygame.K_0: 
				Constants.DEBUG_BOUNDARIES = not Constants.DEBUG_BOUNDARIES
				print("Toggle Boundary Force Lines", Constants.DEBUG_BOUNDARIES)


#################################################################################
# Main Functionality
#################################################################################

# Initialize the game
pygame.init();
screen = pygame.display.set_mode((Constants.WORLD_WIDTH, Constants.WORLD_HEIGHT))
clock = pygame.time.Clock()
sheepImage = pygame.image.load('sheep.png')
dogImage = pygame.image.load('dog.png')
bounds = Vector(Constants.WORLD_WIDTH, Constants.WORLD_HEIGHT)

# Setup the graph
graph = Graph()

# Setup the dog
dog = Player(dogImage, Vector(Constants.WORLD_WIDTH * .5, Constants.WORLD_HEIGHT * .5), 
			 Vector(Constants.DOG_WIDTH, Constants.DOG_HEIGHT), (0, 255, 0), 
			 Constants.DOG_SPEED, Constants.DOG_ANGULAR_SPEED)

# Setup the sheep (only 1 for now...)
herd = []
sheep = Sheep(sheepImage, Vector(randrange(int(bounds.x * .4), int(bounds.x * .6)),
								  randrange(int(bounds.y * .6), int(bounds.y * .8))), 
			   Vector(Constants.DOG_WIDTH, Constants.DOG_HEIGHT), (0, 255, 0), Constants.SHEEP_SPEED, Constants.SHEEP_ANGULAR_SPEED)
herd.append(sheep)

# Setup the gates and obstacles
pen = buildPen(graph)
buildObstacles(graph, pen)

# While the user has not selected quit
hasQuit = False
while not hasQuit:
	# Clear the screen
	screen.fill(Constants.BACKGROUND_COLOR)

	handleEvents()

	# Update the agents onscreen
	dog.update(bounds, graph, herd, Constants.GATES)
	for sheep in herd:
		sheep.update(bounds, graph, dog, herd, Constants.GATES)	

	# Draw the agents onscreen
	graph.draw(screen)
	dog.draw(screen)
	for sheep in herd:
		sheep.draw(screen)

	# Double buffer
	pygame.display.flip()

	# Limit to 60 FPS
	clock.tick(Constants.FRAME_RATE)

# Quit
pygame.quit()