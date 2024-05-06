# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from pacman import GameState

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"
        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        score = 0

        #check best way to the nearest food
        if len(newFood.asList()) == 0:
            score += 100
        else:
            #getting closer to the nearest food gives a higher score
            nearestFood = min([util.manhattanDistance(newPos, foodPos) for foodPos in newFood.asList()])
            score += 1 / float(nearestFood)

        #watch out for ghost, don't go if ghost is 1 step away from you
        ghostsPos = successorGameState.getGhostPositions()
        if min([util.manhattanDistance(newPos, ghostPos) for ghostPos in ghostsPos]) < 2:
            score -= 100

        return successorGameState.getScore() + score

def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        return self.minimax(gameState, 0, self.depth)[1]

    def minimax(self, gameState: GameState, agentIndex, depth):
        if depth == 0 or gameState.isWin() or gameState.isLose():
            return (self.evaluationFunction(gameState), Directions.STOP)
        if agentIndex == 0:
            return self.maximum(gameState, agentIndex, depth)
        else:
            return self.minimum(gameState, agentIndex, depth)

    def maximum(self, gameState: GameState, agentIndex, depth):
        v = (float('-inf'), Directions.STOP)
        nextAgent = (agentIndex + 1) % gameState.getNumAgents()
        if nextAgent == 0:
            depth -= 1
        for action in gameState.getLegalActions(agentIndex):
            successor = gameState.generateSuccessor(agentIndex, action)
            newv = self.minimax(successor, nextAgent, depth)[0]
            if newv > v[0]:
                v = (newv, action)
        return v

    def minimum(self, gameState: GameState, agentIndex, depth):
        v = (float('inf'), Directions.STOP)
        nextAgent = (agentIndex+1)%gameState.getNumAgents()
        if nextAgent == 0:
            depth -= 1
        for action in gameState.getLegalActions(agentIndex):
            successor = gameState.generateSuccessor(agentIndex,action)
            newv = self.minimax(successor,nextAgent,depth)[0]
            if newv < v[0]:
                v = (newv, action)
        return v

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        return self.minimax(gameState, 0, self.depth, float('-inf'), float('inf'))[1]

    def minimax(self, gameState: GameState, agentIndex, depth, alpha, beta):
        if depth == 0 or gameState.isWin() or gameState.isLose():
            return (self.evaluationFunction(gameState), Directions.STOP)
        if agentIndex == 0:
            return self.maximum(gameState, agentIndex, depth, alpha, beta)
        else:
            return self.minimum(gameState, agentIndex, depth, alpha, beta)

    def maximum(self, gameState: GameState, agentIndex, depth, alpha, beta):
        v = (float('-inf'), Directions.STOP)
        nextAgent = (agentIndex + 1) % gameState.getNumAgents()
        if nextAgent == 0:
            depth -= 1
        for action in gameState.getLegalActions(agentIndex):
            successor = gameState.generateSuccessor(agentIndex, action)
            newv = self.minimax(successor, nextAgent, depth, alpha, beta)[0]
            if newv > v[0]:
                v = (newv, action)
            if v[0] > beta:
                return v
            alpha = max(alpha, v[0])
        return v

    def minimum(self, gameState: GameState, agentIndex, depth, alpha, beta):
        v = (float('inf'), Directions.STOP)
        nextAgent = (agentIndex+1)%gameState.getNumAgents()
        if nextAgent == 0:
            depth -= 1
        for action in gameState.getLegalActions(agentIndex):
            successor = gameState.generateSuccessor(agentIndex,action)
            newv = self.minimax(successor,nextAgent,depth, alpha, beta)[0]
            if newv < v[0]:
                v = (newv, action)
            if v[0] < alpha:
                return v
            beta = min(beta, v[0])
        return v

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        return self.minimax(gameState, 0, self.depth)[1]

    def minimax(self, gameState: GameState, agentIndex, depth):
        if depth == 0 or gameState.isWin() or gameState.isLose():
            return (self.evaluationFunction(gameState), Directions.STOP)
        if agentIndex == 0:
            return self.maximum(gameState, agentIndex, depth)
        else:
            return self.expected(gameState, agentIndex, depth)

    def maximum(self, gameState: GameState, agentIndex, depth):
        v = (float('-inf'), Directions.STOP)
        nextAgent = (agentIndex + 1) % gameState.getNumAgents()
        if nextAgent == 0:
            depth -= 1
        for action in gameState.getLegalActions(agentIndex):
            successor = gameState.generateSuccessor(agentIndex, action)
            newv = self.minimax(successor, nextAgent, depth)[0]
            if newv > v[0]:
                v = (newv, action)
        return v

    def expected(self, gameState: GameState, agentIndex, depth):
        v = 0.0
        nextAgent = (agentIndex+1)%gameState.getNumAgents()
        p = 1.0/len(gameState.getLegalActions(agentIndex))
        if nextAgent == 0:
            depth -= 1
        for action in gameState.getLegalActions(agentIndex):
            successor = gameState.generateSuccessor(agentIndex,action)
            v += p * self.minimax(successor,nextAgent,depth)[0]
        return (v,Directions.STOP)

def betterEvaluationFunction(currentGameState: GameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    pacmanPos = currentGameState.getPacmanPosition()
    foods = currentGameState.getFood().asList()
    ghosts = currentGameState.getGhostStates()
    #this makes sure that the pacman doesnt just stay where he is
    score = currentGameState.getScore()

    if currentGameState.isWin():
        return float('inf')

    if currentGameState.isLose():
        return float('-inf')

    #The more food there is left, the worse the score
    score += 25.0 / len(foods)

    for ghost in ghosts:
        distance = manhattanDistance(pacmanPos, ghost.configuration.pos)
        score += 50.0 / distance if ghost.scaredTimer > 0 else -10.0 / distance

    score += 10.0 / min(util.manhattanDistance(pacmanPos, nextFood) for nextFood in foods)
    return score

# Abbreviation
better = betterEvaluationFunction
