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


class StateMachine:
    """ Machine that manages the set of states and their transitions """

    def __init__(self, startState):
        """ Initialize the state machine and its start state"""
        self.__currentState = startState
        self.__currentState.enter()

    def getCurrentState(self):
        """ Get the current state """
        return self.__currentState

    def update(self, gameState):
        """ Run the update on the current state and determine if we should transition """
        nextState = self.__currentState.update(gameState)

        # If the nextState that is returned by current state's update is not the same
        # state, then transition to that new state
        if nextState != None and type(nextState) != type(self.__currentState):
            self.transitionTo(nextState)

    def transitionTo(self, nextState):
        """ Transition to the next state """
        self.__currentState.exit()
        self.__currentState = nextState
        self.__currentState.enter()

    def draw(self, screen):
        """ Draw any debugging information associated with the states """
        self.__currentState.draw(screen)


class State:
    def enter(self):
        """ Enter this state, perform any setup required """
        print("Entering " + self.__class__.__name__)

    def exit(self):
        """ Exit this state, perform any shutdown or cleanup required """
        print("Exiting " + self.__class__.__name__)

    def update(self, gameState):
        """ Update this state, before leaving update, return the next state """
        print("Updating " + self.__class__.__name__)

    def draw(self, screen):
        """ Draw any debugging info required by this state """
        pass


class FindSheepState(State):
    """ This is an example state that simply picks the first sheep to target """

    def update(self, gameState):
        """ Update this state using the current gameState """
        super().update(gameState)
        dog = gameState.getDog()
        if len(gameState.getHerd()) <= 0:
            return Idle()

        sheep_distance = (dog.center - gameState.getHerd()[0].center).length()
        if dog.getTargetSheep() == None:
            sheep = None
            for sheep in gameState.getHerd():
                if (dog.center - sheep.center).length() < sheep_distance:
                    sheep = sheep

        dog.setTargetSheep(sheep)
        return Chase()
        # You could add some logic here to pick which state to go to next
        # depending on the gameState


class Idle(State):
    """ This is an idle state where the dog does nothing """

    def update(self, gameState):
        super().update(gameState)

        # Do nothing
        if len(gameState.getHerd()) > 0:
            return FindSheepState()
        else:
            return Idle()


class Chase(State):
    """ This is the state the dog will be in to chase a sheep """

    def update(self, gameState):
        super().update(gameState)
        dog = gameState.getDog()
        penBounds = gameState.getPenBounds()[0]

        if dog.targetSheep == None:
            return FindSheepState()

        sheepToPen = Vector(penBounds[0] - dog.targetSheep.center.x,
                            penBounds[1] - dog.targetSheep.center.y).normalize()
        dogToSheep = Vector(dog.center.x - dog.targetSheep.center.x,
                            dog.center.y - dog.targetSheep.center.y).normalize()

        cross_product = sheepToPen.x * dogToSheep.y - sheepToPen.y * dogToSheep.x

        if cross_product > 0:
            desired_position = dog.targetSheep.center - \
                dog.targetSheep.velocity.scale(
                    dog.targetSheep.maxSpeed) - sheepToPen.rotateRight().scale(30)
        else:
            desired_position = dog.targetSheep.center + \
                dog.targetSheep.velocity.scale(
                    dog.targetSheep.maxSpeed) - sheepToPen.rotateLeft().scale(30)

        if dog.getPathLength() <= 0:
            dog.calculatePathToNewTarget(desired_position)

        # if dog.getPathLength() <= 0:
        #     dog.calculatePathToNewTarget(desired_position)
