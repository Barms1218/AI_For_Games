import Constants
import Node
import pygame
import Vector
from pygame import *
from Vector import *
from Node import *
from enum import Enum

class SearchType(Enum):
	DJIKSTRA = 1
	A_STAR = 2
	BEST_FIRST = 3

class Graph():
	def __init__(self):
		""" Initialize the Graph """
		self.nodes = []			# Set of nodes
		self.obstacles = []		# Set of obstacles - used for collision detection

		# Initialize the size of the graph based on the world size
		self.gridWidth = int(Constants.WORLD_WIDTH / Constants.GRID_SIZE)
		self.gridHeight = int(Constants.WORLD_HEIGHT / Constants.GRID_SIZE)

		# Create grid of nodes
		for i in range(self.gridHeight):
			row = []
			for j in range(self.gridWidth):
				node = Node(i, j, Vector(Constants.GRID_SIZE * j, Constants.GRID_SIZE * i), Vector(Constants.GRID_SIZE, Constants.GRID_SIZE))
				row.append(node)
			self.nodes.append(row)

		## Connect to Neighbors
		for i in range(self.gridHeight):
			for j in range(self.gridWidth):
				# Add the top row of neighbors
				if i - 1 >= 0:
					# Add the upper left
					if j - 1 >= 0:		
						self.nodes[i][j].neighbors += [self.nodes[i - 1][j - 1]]
					# Add the upper center
					self.nodes[i][j].neighbors += [self.nodes[i - 1][j]]
					# Add the upper right
					if j + 1 < self.gridWidth:
						self.nodes[i][j].neighbors += [self.nodes[i - 1][j + 1]]

				# Add the center row of neighbors
				# Add the left center
				if j - 1 >= 0:
					self.nodes[i][j].neighbors += [self.nodes[i][j - 1]]
				# Add the right center
				if j + 1 < self.gridWidth:
					self.nodes[i][j].neighbors += [self.nodes[i][j + 1]]
				
				# Add the bottom row of neighbors
				if i + 1 < self.gridHeight:
					# Add the lower left
					if j - 1 >= 0:
						self.nodes[i][j].neighbors += [self.nodes[i + 1][j - 1]]
					# Add the lower center
					self.nodes[i][j].neighbors += [self.nodes[i + 1][j]]
					# Add the lower right
					if j + 1 < self.gridWidth:
						self.nodes[i][j].neighbors += [self.nodes[i + 1][j + 1]]

	def getNodeFromPoint(self, point):
		""" Get the node in the graph that corresponds to a point in the world """
		return self.nodes[int(point.y/Constants.GRID_SIZE)][int(point.x/Constants.GRID_SIZE)]

	def placeObstacle(self, point, color):
		""" Place an obstacle on the graph """
		node = self.getNodeFromPoint(point)

		# If the node is not already an obstacle, make it one
		if node.isWalkable:
			# Indicate that this node cannot be traversed
			node.isWalkable = False		

			# Set a specific color for this obstacle
			node.color = color
			for neighbor in node.neighbors:
				neighbor.neighbors.remove(node)
			node.neighbors = []
			self.obstacles += [node]

	def reset(self):
		""" Reset all the nodes for another search """
		for i in range(self.gridHeight):
			for j in range(self.gridWidth):
				self.nodes[i][j].reset()

	def buildPath(self, endNode):
		""" Go backwards through the graph reconstructing the path """
		path = []
		node = endNode
		while node is not 0:
			node.isPath = True
			path = [node] + path
			node = node.backNode

		# If there are nodes in the path, reset the colors of start/end
		if len(path) > 0:
			path[0].isPath = False
			path[0].isStart = True
			path[-1].isPath = False
			path[-1].isEnd = True
		return path

	def findPath_Breadth(self, start, end):
		""" Breadth-first Search """
		print("BREADTH")
		self.reset()

		# Initialize a queue for BFS
		startNode = (self.getNodeFromPoint(start))
		startNode.isStart = True
		queue = [startNode]
		visited = {startNode}
		endNode = self.getNodeFromPoint(end)
		endNode.isEnd = True
		start.isVisited = True

		if startNode == endNode:
			return self.buildPath(startNode)
		

		# Continue BFS until the queue is empty
		while queue:
			currentNode = queue.pop(0)
			currentNode.isExplored = True

			if currentNode == endNode:
				# Path found, reconstruct and return it
				return self.buildPath(endNode)

			# Explore neighbors
			for neighbor in currentNode.neighbors:
				if neighbor not in visited:
					visited.add(neighbor)
					queue.append(neighbor)
					neighbor.isVisited = True
					neighbor.backNode = currentNode


			if currentNode.neighbors == endNode:
				return self.buildPath(endNode)
			
		# No path found
		return []

	def findPath_Djikstra(self, start, end):
		""" Djikstra's Search """
		# Reset the graph and initialize the starting node
		print("DJIKSTRA")
		self.reset()
		start_node = self.getNodeFromPoint(start)
		end_node = self.getNodeFromPoint(end)

		start_node.cost = 0
		start_node.costFromStart = 0
		priority_queue = [start_node]

		visited = {start_node}

		while priority_queue:
			priority_queue.sort(key=lambda node: node.cost)
			currNode = priority_queue.pop(0)
			currNode.isExplored = True

			if currNode == end_node:
				return self.buildPath(end_node)
			
			for neighbor in currNode.neighbors:
				neighbor.costFromStart = currNode.costFromStart + self.calculate_cost(currNode, neighbor)
				neighbor.costToEnd = 0
				new_cost = neighbor.costFromStart + neighbor.costToEnd
				if neighbor not in visited:
					neighbor.isVisited = True
					visited.add(neighbor)
					neighbor.cost = new_cost

					neighbor.backNode = currNode
					priority_queue.append(neighbor)
				elif neighbor in visited:
					if new_cost < neighbor.cost:
						neighbor.cost = new_cost
						neighbor.backNode = currNode

				
		# No path found
		return []

	def findPath_AStar(self, start, end):
		""" A Star Search """
		print("A_STAR")
		self.reset()
		start_node = self.getNodeFromPoint(start)
		end_node = self.getNodeFromPoint(end)

		start_node.cost = 0
		start_node.costFromStart = 0
		priority_queue = [start_node]
		visited = {start_node}

		while priority_queue:
			priority_queue.sort(key=lambda node:node.cost)
			currNode = priority_queue.pop(0)
			currNode.isExplored = True

			if currNode == end_node:
				return self.buildPath(end_node)

			for neighbor in currNode.neighbors:
				neighbor.costFromStart = self.calculate_cost(currNode, neighbor) + currNode.costFromStart
				neighbor.costToEnd = self.calculateHeuristic(neighbor, end_node)
				new_cost = neighbor.costFromStart + neighbor.costToEnd
				if neighbor not in visited or new_cost < neighbor.cost:
					
					neighbor.cost = new_cost
					neighbor.backNode = currNode
					
					if not neighbor.isVisited:
						neighbor.isVisited = True
						visited.add(neighbor)
						priority_queue.append(neighbor)

		# Return empty path indicating no path was found
		return []

	def findPath_BestFirst(self, start, end):
		"""Best First Search"""
		print("BEST_FIRST")
		self.reset()
		start_node = self.getNodeFromPoint(start)
		end_node = self.getNodeFromPoint(end)

		start_node.cost = 0
		priority_queue = [start_node]
		visited = {start_node}

		while priority_queue:
			priority_queue.sort(key=lambda node:node.cost)
			currNode = priority_queue.pop(0)
			currNode.isExplored = True

			if currNode == end_node:
				return self.buildPath(end_node)

			for neighbor in currNode.neighbors:
				neighbor.costFromStart = 0
				neighbor.costToEnd = self.calculateHeuristic(neighbor, end_node)
				new_cost = neighbor.costFromStart + neighbor.costToEnd
				if neighbor not in visited or new_cost < neighbor.cost:
					
					neighbor.cost = new_cost
					neighbor.backNode = currNode
					
					if not neighbor.isVisited:
						neighbor.isVisited = True
						visited.add(neighbor)
						priority_queue.append(neighbor)

        # No path found
		return []


	def draw(self, screen):
		""" Draw the graph """
		for i in range(self.gridHeight):
			for j in range(self.gridWidth):
				self.nodes[i][j].draw(screen)

	# Calculcate the cost to move cardinally vs diagonally
	def calculate_cost(self, current_node, next_node):
		target_x = abs(current_node.x - next_node.x)
		target_y = abs(current_node.y - next_node.y)

		# Node is in a diagonal direction from current node
		if target_x == 1 and target_y == 1:
			return 2
		
		# node is in a cardinal direction
		return 1

	def calculateHeuristic(self, node, goal):
        # Implement your heuristic function here, e.g., Manhattan distance
		return Vector(node.x - goal.x, node.y - goal.y).length()