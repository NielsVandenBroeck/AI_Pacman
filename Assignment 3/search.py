# search.py
# ---------
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


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""
import copy

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()

def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem: SearchProblem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    """

    """
    branches = [] #keeps track where the path branches
    path = [] #final solution
    closed = {} #set of states that are already visited
    fringe = util.Stack() #process these states next
    fringe.push((problem.getStartState(),None,None)) #startstate
    while True:
        #no solution found
        if fringe.isEmpty():
            return False
        node = fringe.pop()
        #exception for startstate
        if len(closed) != 0:
            path.append(node[1])
        #if goal is reached, exit loop
        if problem.isGoalState(node[0]):
            break
        successors = problem.getSuccessors(node[0])
        SuccessorsAmount = len(successors)
        #put node in already visited
        closed[node[0]] = set()
        #loop over successors
        for child in successors:
            #only add if state is not visited yet
            if child[0] not in closed:
                fringe.push(child)
            else:
                SuccessorsAmount -= 1
        #add position of branch in path and amount of branches
        #so that we later know until where to delete states in path if this branch reaches dead end
        if SuccessorsAmount > 1:
            branches.append([len(path),SuccessorsAmount])
        #delete all states of branch with dead end
        if SuccessorsAmount == 0:
            currentBranch = branches.pop()
            if currentBranch[1] > 2:
                currentBranch[1] -= 1
                branches.append(currentBranch)
            path = path[:currentBranch[0]]
    return path
    """
    closed = set() #set of states that are already visited
    fringe = util.Stack() #process these states next
    fringe.push(((problem.getStartState()),[])) #startstate

    while True:
        if fringe.isEmpty(): #if fringe is empty, no solution found
            return False
        node = fringe.pop() #get next node in fringe
        if problem.isGoalState(node[0]): #check if node is goal
            return node[1] #return the path to get to this node
        if node[0] not in closed: #if it is visited yet, skip and go to next node
            closed.add(node[0])
            for child in problem.getSuccessors(node[0]): #add all the successors of this node
                newpath = copy.deepcopy(node[1]) #copy the path to get to this node
                newpath.append(child[1])
                fringe.push((child[0],newpath)) #add next node to fringe to visit next

def breadthFirstSearch(problem: SearchProblem):
    """Search the shallowest nodes in the search tree first."""
    closed = set() #set of states that are already visited
    fringe = util.Queue() #process these states next
    fringe.push(((problem.getStartState()),[])) #startstate

    while True:
        if fringe.isEmpty(): #if fringe is empty, no solution found
            return False
        node = fringe.pop() #get next node in fringe
        if problem.isGoalState(node[0]): #check if node is goal
            return node[1] #return the path to get to this node
        if node[0] not in closed: #if it is visited yet, skip and go to next node
            closed.add(node[0])
            for child in problem.getSuccessors(node[0]): #add all the successors of this node
                newpath = copy.deepcopy(node[1]) #copy the path to get to this node
                newpath.append(child[1])
                fringe.push((child[0],newpath)) #add next node to fringe to visit next

def uniformCostSearch(problem: SearchProblem):
    """Search the node of least total cost first."""
    closed = set()  # set of states that are already visited
    fringe = util.PriorityQueue()  # process these states next
    fringe.push((problem.getStartState(), [], 0),0)  # startstate

    while True:
        if fringe.isEmpty(): #if fringe is empty, no solution found
            return False
        node = fringe.pop() #get next node in fringe
        if problem.isGoalState(node[0]): #check if node is goal
            return node[1] #return the path to get to this node
        if node[0] not in closed: #if it is visited yet, skip and go to next node
            closed.add(node[0])
            for child in problem.getSuccessors(node[0]): #add all the successors of this node
                newpath = copy.deepcopy(node[1])  #copy the path to get to this node
                newpath.append(child[1])
                totalcost = node[2]+child[2] #calculate the cost to go to new node
                fringe.push((child[0],newpath,totalcost),totalcost) #add next node to fringe to visit next

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    closed = set()  # set of states that are already visited
    fringe = util.PriorityQueue()  # process these states next
    fringe.push((problem.getStartState(), [], 0),0)  # startstate

    while True:
        if fringe.isEmpty(): #if fringe is empty, no solution found
            return False
        node = fringe.pop() #get next node in fringe
        if problem.isGoalState(node[0]): #check if node is goal
            return node[1] #return the path to get to this node
        if node[0] not in closed: #if it is visited yet, skip and go to next node
            closed.add(node[0])
            for child in problem.getSuccessors(node[0]): #add all the successors of this node
                newpath = copy.deepcopy(node[1])  #copy the path to get to this node
                newpath.append(child[1])
                totalcost = node[2]+child[2] #calculate the cost to go to new node
                fringe.push((child[0],newpath,totalcost),totalcost+heuristic(child[0],problem))#add next node to fringe to visit next

# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
