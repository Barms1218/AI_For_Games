class GameState:
	'''Manages the game state'''

	def getDeltaTime(self):
		return self.__deltaTime

	def getWorldBounds(self):
		return self.__worldBounds

	def getGraph(self):
		return self.__graph

	def getDog(self):
		return self.__dog

	def getHerd(self):
		return self.__herd

	def getPenBounds(self):
		return self.__penBounds

	def setDeltaTime(self, deltaTime):
		self.__deltaTime = deltaTime

	def setBounds(self, worldBounds):
		self.__worldBounds = worldBounds

	def setGraph(self, graph):
		self.__graph = graph

	def setDog(self, dog):
		self.__dog = dog

	def setHerd(self, herd):
		self.__herd = herd

	def setPen(self, pen):
		self.__pen = pen

	def update(self, deltaTime, worldBounds, graph, dog, herd, penBounds):
		self.__deltaTime = deltaTime
		self.__worldBounds = worldBounds
		self.__graph = graph
		self.__dog = dog
		self.__herd = herd
		self.__penBounds = penBounds
