import pygame
import Vector
import Agent

from Vector import Vector
from Agent import *
from enum import Enum
from pygame import *

class SearchType(Enum):
	BREADTH = 1
	DJIKSTRA = 2
	BEST = 3
	A_STAR = 4

class Player(Agent):

	def __init__(self, image, position, size, color, speed, angularSpeed):
		'''Initialize the player'''
		super().__init__(image, position, size, color, speed, angularSpeed)
		self.searchType = SearchType.A_STAR
		self.gateNumber = 0
		self.isFollowingPath = False
		self.path = []

	def calculateHerdPosition(self, herd):
		'''Calculate the center of the herd'''
		position = Vector(0, 0)
		for sheep in herd:
			position += sheep.center

		return position.scale(1 / len(herd))

	def update(self, bounds, graph, herd, gates):
		'''Update the player'''

		# Allow the user to select a search type
		if pygame.key.get_pressed()[K_f]:
			self.searchType = SearchType.BREADTH
		elif pygame.key.get_pressed()[K_d]:
			self.searchType = SearchType.DJIKSTRA
		elif pygame.key.get_pressed()[K_s]:
			self.searchType = SearchType.BEST
		elif pygame.key.get_pressed()[K_a]:
			self.searchType = SearchType.A_STAR

		# If we are not following the path, find the sheep
		if not self.isFollowingPath:
			# Find the sheep and head toward the sheep
			herdPosition = self.calculateHerdPosition(herd)

			# If the herdPosition is walkable, find a path
			herdPosNode = graph.getNodeFromPoint(herdPosition)
			if herdPosNode.isWalkable:

				# Select the appropriate search algorithm based on user input
				if self.searchType == SearchType.BREADTH:
					self.path = graph.findPath_Breadth(self.center, herdPosition)
				elif self.searchType == SearchType.DJIKSTRA:
					self.path = graph.findPath_Djikstra(self.center, herdPosition)
				elif self.searchType == SearchType.BEST:
					self.path = graph.findPath_BestFirst(self.center, herdPosition)
				elif self.searchType == SearchType.A_STAR:
					self.path = graph.findPath_AStar(self.center, herdPosition)

				# If there is a path, start following it
				if len(self.path) > 0:
					self.isFollowingPath = True
					self.target = self.path.pop(0).center
					self.speed = self.maxSpeed

		# If we are following the path
		else:
			vectorToTarget = self.target - self.center
			# If we've arrived at the first location in the path
			if (vectorToTarget).length() <= Constants.GRID_SIZE * .5:
				# Go to next position in path, if there is one
				if len(self.path) > 0:
					self.target = self.path.pop(0).center
				# Stop following the path if it is empty
				else:
					self.isFollowingPath = False
					self.speed = 0
			else:
				self.setVelocity(vectorToTarget)

		super().update(bounds, graph, [self] + [herd])