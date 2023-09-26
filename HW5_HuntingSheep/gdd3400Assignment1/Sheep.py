import pygame
import Vector
import Agent
import Constants

from Vector import Vector
from Agent import *

class Sheep(Agent):
	"""Sheep class avoid boundaries and flee from the dog"""
	
	def computeDogInfluence(self, dog):
		'''Compute the Force exerted by the dog'''
		vectToDog = self.center - dog.center
		self.target = dog

		# If the dog is close enough, flee from him
		if vectToDog.length() < Constants.MIN_ATTACK_DIST:
			self.drawDogInfluence = True
			return vectToDog
		else:
			self.drawDogInfluence = False
			return Vector(0, 0)

	def computeBoundaryInfluence(self, bounds):
		'''Compute the Forces exerted by the boundaries'''
		boundsInfluence = Vector(0, 0)
		self.boundaries = []

		# Compute forces from the left and right boundaries
		if self.center.x < Constants.SHEEP_BOUNDARY_RADIUS:
			boundsInfluence -= Vector(0 - self.center.x, 0)
			self.boundaries += [Vector(0, self.center.y)]
		elif self.center.x > bounds.x - Constants.SHEEP_BOUNDARY_RADIUS:
			boundsInfluence -= Vector(bounds.x - self.center.x, 0)
			self.boundaries += [Vector(bounds.x, self.center.y)]

		# Compute forces from the top and bottom boundaries
		if self.center.y < Constants.SHEEP_BOUNDARY_RADIUS:
			boundsInfluence -= Vector(0, 0 - self.center.y)
			self.boundaries += [Vector(self.center.x, 0)]
		elif self.center.y > bounds.y - Constants.SHEEP_BOUNDARY_RADIUS:
			boundsInfluence -= Vector(0, bounds.y - self.center.y)
			self.boundaries += [Vector(self.center.x, bounds.y)]

		return boundsInfluence

	def computeObstacleInfluence(self, obstacles):
		'''Compute the forces exerted by the closest obstacles'''
		obstacleInfluence = Vector(0, 0)
		obstacleCount = 0
		self.obstacles = []
		self.obstacleForces = []

		# For each obstacle, determine if it is "close" to the sheep
		for obstacle in obstacles:
			vectToObstacle =  self.center - obstacle.center

			# If the obstacle is close enough, run away from it
			if vectToObstacle.length() < Constants.SHEEP_OBSTACLE_RADIUS:
				self.obstacles += [obstacle]
				self.obstacleForces += [vectToObstacle]
				obstacleInfluence += vectToObstacle.normalize().scale(Constants.SHEEP_OBSTACLE_RADIUS - vectToObstacle.length())
			obstacleInfluence = obstacleInfluence.normalize().scale(len(self.obstacles))
		return obstacleInfluence			

	def update(self, bounds, graph, dog, herd, gates):
		'''Update the sheep this frame'''

		# Compute all of the forces on the sheep
		dogInfluence = self.computeDogInfluence(dog).normalize()
		boundsInfluence = self.computeBoundaryInfluence(bounds).normalize()
		obstacleInfluence = self.computeObstacleInfluence(graph.obstacles).normalize()

		# Sum all of the forces and scale them appropriately
		direction = dogInfluence.scale(Constants.SHEEP_DOG_INFLUENCE_WEIGHT * int(Constants.ENABLE_DOG)) \
					+ boundsInfluence.scale(Constants.SHEEP_BOUNDARY_INFLUENCE_WEIGHT * int(Constants.ENABLE_BOUNDARIES)) \
					+ obstacleInfluence.scale(Constants.SHEEP_OBSTACLE_INFLUENCE_WEIGHT * int(Constants.ENABLE_OBSTACLES))

		# If velocity is zero, keep the old velocity but set the speed to zero
		if abs(direction.x) < 0.000001 and abs(direction.y) < 0.000001:
			self.speed = 0
		else:
			self.setVelocity(direction)
			self.speed = self.maxSpeed
		super().update(bounds, graph, [dog] + [herd])


	def draw(self, screen):
		'''Draw the sheep'''
		super().draw(screen)

		# Draw a line from the dog to the sheep if the sheep is fleeing
		if self.drawDogInfluence and Constants.DEBUG_DOG_INFLUENCE:
			pygame.draw.line(screen, (255, 0, 0), (self.center.x, self.center.y), 
				(self.target.center.x, self.target.center.y), Constants.DEBUG_LINE_WIDTH)
		
		# Draw the boundary forces
		if Constants.DEBUG_BOUNDARIES:
			for boundary in self.boundaries:
				pygame.draw.line(screen, (255, 0, 255), (self.center.x, self.center.y), 
								 (boundary.x, boundary.y), Constants.DEBUG_LINE_WIDTH)

		# Draw the obstacle forces
		if Constants.DEBUG_OBSTACLES:
			for obstacle in self.obstacles:
				pygame.draw.line(screen, (0, 255, 255), (self.center.x, self.center.y),
								 (obstacle.center.x, obstacle.center.y), Constants.DEBUG_LINE_WIDTH)
