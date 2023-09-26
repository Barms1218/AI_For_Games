import math

from math import sqrt

class Vector:
	'''2D vector class'''

	def __init__(self, x, y):
		'''Construct the vector'''
		self.x = x
		self.y = y

	def __str__(self):
		'''Print the vector to the screen'''
		return 'Vector (%f, %f)' % (self.x, self.y)

	def __add__(self,other):
		'''Add two vectors together'''
		return Vector(self.x + other.x, self.y + other.y)

	def __sub__(self,other):
		'''Substract two vectors'''
		return Vector(self.x - other.x, self.y - other.y)

	def dot(self, other):
		'''Compute the dot product between two vectors'''
		return self.x * other.x + self.y * other.y

	def scale(self, scalar):
		'''Scale the vector'''
		return Vector(self.x * scalar, self.y * scalar)

	def length(self):
		'''Compute the length of the vector'''
		return math.sqrt(self.dot(self))

	def normalize(self):
		'''Normalize the vector'''
		len = self.length()

		# If the vector does not have length zero, normalize it
		if not len == 0:
			return Vector(self.x / len, self.y / len)
		else:
			return Vector(self.x, self.y)

	def lerp(self, end, percent):
		'''Linearly interpolate between two vectors'''
		return self + (end - self).scale(percent)

	def perpendicular(self):
		'''Compute the perpendicular vector'''
		return Vector(-self.y, self.x)