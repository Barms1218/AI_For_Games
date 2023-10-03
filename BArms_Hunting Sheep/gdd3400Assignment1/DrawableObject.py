import pygame
import random
import Constants

from Vector import *

class DrawableObject(object):
	"""Uses images to draw an object on the screen"""
	def __init__(self, image, position, size, color):
		self.upperLeft = position
		self.center = position + size.scale(0.5)
		self.size = size
		self.image = image
		self.angle = 0
		self.calcSurface()
		self.color = color

	def __str__(self):
		'''Print the object'''
		return 'DrawableObject (%s, %s)' % (self.center, self.angle)

	def calcSurface(self):
		'''Calculate the drawable surface and bounding rectangle for collisions'''
		self.surf = pygame.transform.rotate(self.image, self.angle)
		self.upperLeft = self.center - Vector(self.surf.get_width(), self.surf.get_height()).scale(0.5)
		self.boundingRect = self.surf.get_bounding_rect().move(self.upperLeft.x, self.upperLeft.y)

	def isInCollision(self, agent):
		'''Determine if this object is in collision with the agent'''
		return self.boundingRect.colliderect(agent.boundingRect)

	def draw(self, screen):
		'''Draw the object'''
		
		# Draw the image to the surface
		screen.blit(self.surf, [self.upperLeft.x, self.upperLeft.y])