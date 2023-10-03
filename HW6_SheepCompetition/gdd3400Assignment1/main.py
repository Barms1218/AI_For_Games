import pygame
import random
import Vector
import Agent
import Dog
import Sheep
import Constants
import Graph
import Node
import GameState

from Constants import *
from pygame import *
from random import *
from Vector import *
from Agent import *
from Sheep import *
from Dog import *
from Graph import *
from Node import *
from GameState import *

#################################################################################
# Helper Functions
#################################################################################

def buildGates(graph):
	'''Build the Pen that the sheep will be forced into'''
	X = 0
	Y = 1

	# Add the sheep pen to the game
	for gate in PEN:
		graph.placeObstacle(Vector(gate[0][X], gate[0][Y]), (0, 255, 0))
		graph.placeObstacle(Vector(gate[0][X] - Constants.GRID_SIZE, gate[0][Y]), (0, 255, 0))
		graph.placeObstacle(Vector(gate[0][X] - Constants.GRID_SIZE * 2, gate[0][Y]), (0, 255, 0))
		graph.placeObstacle(Vector(gate[1][X], gate[1][Y]), (255, 0, 0))
		graph.placeObstacle(Vector(gate[1][X] + Constants.GRID_SIZE, gate[1][Y]), (255, 0, 0))
		graph.placeObstacle(Vector(gate[1][X] + Constants.GRID_SIZE * 2, gate[1][Y]), (255, 0, 0))

	# Initialize Pen Collision Rectangles
	penBounds = []

	# Add the final pen based on the final gate
	finalGate = gate[-2:]
	# If the gate is horizontally arranged
	if finalGate[0][Y] == finalGate[1][Y]:
		# Create the gate's "entrance" collider
		penBounds.append(pygame.Rect(finalGate[0][X] + GRID_SIZE * 0.5, finalGate[1][Y] - GRID_SIZE * 0.5, \
										finalGate[1][X] - finalGate[0][X] - GRID_SIZE, GRID_SIZE))

		# Create the pen's "inside" collider
		penBounds.append(pygame.Rect(finalGate[0][X] + GRID_SIZE * 0.5, finalGate[0][Y] + GRID_SIZE * 0.5, \
										finalGate[1][X] - finalGate[0][X] - GRID_SIZE, PEN_DEPTH - GRID_SIZE * 2))

		# Draw the two sides of the pen
		for y in range(finalGate[0][Y] + GRID_SIZE, finalGate[0][Y] + PEN_DEPTH, GRID_SIZE):
			graph.placeObstacle(Vector(finalGate[0][X], y), (0, 0, 0))
			graph.placeObstacle(Vector(finalGate[1][X], y), (0, 0, 0))

		# Draw the far-end of the pen
		for x in range(finalGate[0][X] + GRID_SIZE, finalGate[1][X], GRID_SIZE):
			graph.placeObstacle(Vector(x, finalGate[0][Y] + (PEN_DEPTH - GRID_SIZE)), (0, 0, 0))

	# Build the left and right sides of the pen
	for y in range(gate[0][Y] + Constants.GRID_SIZE, \
					gate[0][Y] + Constants.GRID_SIZE * 9, \
					Constants.GRID_SIZE):
		# Place the left side of the pen
		graph.placeObstacle(Vector(gate[0][X], y), (0, 0, 0))
		graph.placeObstacle(Vector(gate[0][X] - Constants.GRID_SIZE, y), (0, 0, 0))
		graph.placeObstacle(Vector(gate[0][X] - Constants.GRID_SIZE * 2, y), (0, 0, 0))
		# Place the right side of the pen
		graph.placeObstacle(Vector(gate[1][X], y), (0, 0, 0))
		graph.placeObstacle(Vector(gate[1][X] + Constants.GRID_SIZE, y), (0, 0, 0))
		graph.placeObstacle(Vector(gate[1][X] + Constants.GRID_SIZE * 2, y), (0, 0, 0))

	# Build the bottom of the pen
	for x in range(gate[0][X] + Constants.GRID_SIZE - 3 * Constants.GRID_SIZE, \
					gate[1][X] + 3 * Constants.GRID_SIZE, \
					Constants.GRID_SIZE):
		graph.placeObstacle(Vector(x, gate[0][Y] + Constants.GRID_SIZE * 9), (0, 0, 0))
		graph.placeObstacle(Vector(x, gate[0][Y] + Constants.GRID_SIZE * 10), (0, 0, 0))
		graph.placeObstacle(Vector(x, gate[0][Y] + Constants.GRID_SIZE * 11), (0, 0, 0))

	# Return the two collision rectangles that represent the pen
	return penBounds

# Create all of the obstacles in the world and add them to the graph
def buildObstacles(graph, penBounds):

	# Define the area of the pen and "in front" of the pen to prevent obstacles
	pen = [ Vector(penBounds[0].x, penBounds[0].y - penBounds[1].height), 
			Vector(penBounds[1].x + penBounds[1].width, penBounds[1].y + penBounds[1].height) ]

	# Random Obstacles
	for i in range(Constants.NBR_RANDOM_OBSTACLES):

		# Select a random cell to use as the starting cell of an obstacle
		start = Vector(randrange(0, Constants.WORLD_WIDTH), randrange(0, Constants.WORLD_HEIGHT))
		while(pen[0].x <= start.x <= pen[1].x and pen[0].y <= start.y <= pen[1].y):
			start = Vector(randrange(0, Constants.WORLD_WIDTH), randrange(0, Constants.WORLD_HEIGHT))
		graph.placeObstacle(start, (0, 0, 0))

		# Grow a block of contiguous obstacles
		for j in range(randrange(Constants.MIN_NBR_CLUMPED_OBSTACLES, Constants.NBR_CLUMPED_OBSTACLES)):
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

def computeNeighbors(herd):
	'''Compute the neighbors for each sheep'''
	for i in range(0, len(herd)):
		herd[i].neighbors = []

	for i in range(0, len(herd)):
		for j in range(i + 1, len(herd)):
			if (herd[i].center - herd[j].center).length() < Constants.SHEEP_NEIGHBOR_RADIUS:
				herd[i].neighbors += [sheep]

#################################################################################
# Main Functionality
#################################################################################

# Comment-in this line if you want to test on the same exact configuration of
# objects as the last time.  Change the number to test out some variations
#random.seed(1005)

pygame.init();

# Set up the visual world
screen = pygame.display.set_mode((WORLD_WIDTH, WORLD_HEIGHT))
clock = pygame.time.Clock()
sheepImage = pygame.image.load('sheep.png')
dogImage = pygame.image.load('dog.png')
worldBounds = Vector(WORLD_WIDTH, WORLD_HEIGHT)

# Setup the graph
graph = Graph()

# Setup the gates and obstacles
penBounds = buildGates(graph)
buildObstacles(graph, penBounds)
atEntrance = []

# Setup the dog
dog = Dog(dogImage, 
		  Vector(WORLD_WIDTH * .5, WORLD_HEIGHT * .5), 
		  Vector(DOG_WIDTH, DOG_HEIGHT), 
		  (0, 255, 0), 
		  DOG_SPEED, 
		  DOG_ANGULAR_SPEED)

# Setup the sheep (only 1 for now...)
herd = []
while len(herd) < Constants.SHEEP_COUNT:
	# Randomly place the sheep in the world on a walkable cell
	center = Vector(randrange(int(worldBounds.x * .05), int(worldBounds.x * .95)), 
					randrange(int(worldBounds.y * .05), int(worldBounds.y * .95)))
	while (not graph.getNodeFromPoint(center).isWalkable):
		center = Vector(randrange(int(worldBounds.x * .05), int(worldBounds.x * .95)), 
						randrange(int(worldBounds.y * .05), int(worldBounds.y * .95)))

	# Create the sheep at the center point
	sheep = Sheep(sheepImage, center, Vector(SHEEP_WIDTH, SHEEP_HEIGHT), (0, 255, 0), 
					SHEEP_SPEED, SHEEP_ANGULAR_SPEED)

	# Make sure the sheep is not already in the pen
	if (not sheep.boundingRect.colliderect(penBounds[0]) and not sheep.boundingRect.colliderect(penBounds[1])):
		herd.append(sheep)

# Setup the "winning" message and time
font = pygame.font.SysFont('courier new', 32)

# While the user has not selected quit
gameState = GameState()
hasQuit = False
startTime = time.get_ticks()
while not hasQuit:
	# Clear the screen
	screen.fill(BACKGROUND_COLOR)

	# Process all in-game events
	for event in pygame.event.get():
		if event.type == pygame.QUIT \
			or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
			hasQuit = True

	deltaTime = clock.get_time() / 1000

	# Compute the neighbors of the herd
	computeNeighbors(herd)

	# Update the GameState Object
	gameState.update(deltaTime, worldBounds, graph, dog, herd, penBounds)

	# Update the agents onscreen
	dog.update(gameState)
	for sheep in herd:
		sheep.update(gameState)	

	# Draw the agents onscreen
	graph.draw(screen)
	dog.draw(screen)
	for sheep in herd:
		sheep.draw(screen)

	# Draw the Goal colliders
	pygame.draw.rect(screen, (255, 0, 25), penBounds[1], 6)
	pygame.draw.rect(screen, (0, 0, 255), penBounds[0], 6)

	# See if one of the sheep has arrived in the pen by going through the gate
	for sheep in herd:
		# If the sheep is not at the entrance
		if sheep not in atEntrance:
			# If the sheep is colliding with the entrance to the pen, mark that sheep
			if sheep.boundingRect.colliderect(penBounds[0]):
				atEntrance.append(sheep)
		# If the sheep is at the entrance
		else:
			# If the sheep is also in the pen, remove the sheep
			if sheep.boundingRect.colliderect(penBounds[1]):
				herd.remove(sheep)
			# If they're not longer colliding with the entrance,
			# assume they have moved away from the entrance
			elif not sheep.boundingRect.colliderect(penBounds[0]):
				atEntrance.remove(sheep)
					   
	# Display the time since the game started
	endTime = time.get_ticks()
	elapsedTime = (endTime - startTime) / 1000
	text = font.render('%13s' % (' Time: ' + str(elapsedTime)).ljust(13,' '), True, (0, 255, 0), (0, 0, 255)) 
	textRect = text.get_rect()  
	textRect.center = (WORLD_WIDTH // 2, 25) 
	screen.blit(text, textRect) 

	# If all the sheep have been captured, the player has won!
	if len(herd) == 0:
		hasQuit = True
		print('Final Time: ' + str(elapsedTime))

	# Double buffer
	pygame.display.flip()

	# Limit to 60 FPS
	clock.tick(FRAME_RATE)

# Quit
pygame.quit()