import pygame
import Vector
import random
import Constants

from Vector import Vector
from DrawableObject import *

class Agent(DrawableObject):
	'''Agent class inherits from DrawableObject'''

	def __init__(self, image, position, size, color, speed, angularSpeed):
		'''Agent Constructor - initialize the agent'''
		super().__init__(image, position, size, color)
		self.maxSpeed = speed
		self.speed = 0
		self.angularSpeed = angularSpeed
		self.velocity = Vector(random.random() - 0.5, random.random() - 0.5).normalize()
		self.target = Vector(0, 0)
		self.targetVelocity = self.velocity

	def __str__(self):
		'''Convert the agent to a string'''
		return 'Agent (%s, %s, %s)' % (self.size, self.center, self.velocity)

	def setVelocity(self, velocity):
		'''Set the velocity and normalize it'''
		self.targetVelocity = velocity.normalize()

	def moveTowardTargetVelocity(self):
		'''Using rotational velocity, move toward the target velocity'''
		velocityDiff = self.targetVelocity - self.velocity
		if (velocityDiff.length() < self.angularSpeed):
			self.velocity = self.targetVelocity
		else:
			velPerp = self.velocity.perpendicular()
			# If the perpendicular velocity is in the same direction 
			# as the velocity difference, use it, otherwise, reverse it
			if velPerp.dot(velocityDiff) < 0:
				velPerp = velPerp.scale(-1)
			
			# Add the perpendicular velocity to the current velocity and scale it
			self.velocity += velPerp.normalize().scale(self.angularSpeed)
		self.velocity = self.velocity.normalize()

	def update(self, bounds, graph, agents):
		'''Update the agent'''
		self.moveTowardTargetVelocity()
		self.center = self.center + self.velocity.scale(self.speed)

		# Check to make sure the object is still in the bounds of the world
		self.center.x = max(self.boundingRect.width * 0.5, min(self.center.x, bounds.x - self.boundingRect.width * 0.5))
		self.center.y = max(self.boundingRect.height * 0.5, min(self.center.y, bounds.y - self.boundingRect.height * 0.5))
		self.calcSurface()

	def draw(self, screen):
		'''Draw the agent using its orientation'''
		self.angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x)) - 90
		super().draw(screen)

		# If we want to draw the agent's velocity line, draw it
		if Constants.DEBUG_VELOCITY:
			pygame.draw.line(screen, self.color, (self.center.x, self.center.y), 
					   (self.center.x + (self.velocity.x * self.boundingRect.width * 2), 
						self.center.y + (self.velocity.y * self.boundingRect.height * 2)), 
						Constants.DEBUG_LINE_WIDTH)

