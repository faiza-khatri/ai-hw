# search.py


"""
In search.py, you will implement generic search algorithms (A* and Dijkstra)
that operate on any problem implementing the SearchProblem interface below.

For this assignment you will formulate TWO problems against this interface:
    1. Robot Navigation with Obstacles 
    2. Courier Delivery Route Planning 

You will implement a SearchProblem subclass for each (in separate files,
e.g. robotNavigation.py and courierDelivery.py), then write generic
aStarSearch and dijkstraSearch functions here that work on either subclass
purely through this interface.
"""

import util
import itertools


class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't
    implement any of the methods (in object-oriented terminology: an
    abstract class).

    You do not need to change anything in this class, ever. Instead, you
    will write problem-specific subclasses (for Robot Navigation and for
    Courier Delivery) that implement each of these methods.
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

        For a given state, this should return a list of triples,
        (successor, action, stepCost), where 'successor' is a successor to
        the current state, 'action' is the action required to get there,
        and 'stepCost' is the incremental cost of expanding to that
        successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of
        actions. The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()

    def getHeuristic(self, state):
        """
         state: the current state of the agent

        This function returns the heuristic value of the current state,
        i.e. the estimated remaining cost/distance to the goal. Used by
        A* Search. Should return 0 for Dijkstra-equivalent behaviour.
        """
        util.raiseNotDefined()


def aStarSearch(problem, startState=None, goalState=None):
    """
    Search the node that has the lowest combined cost (g) and heuristic (h)
    first, i.e. lowest f = g + h.

    This must work generically on ANY SearchProblem passed in - it should
    not know anything about grids, CSV files, robots, or couriers. All of
    that logic belongs inside the SearchProblem subclasses.

    Should return the list of actions from start to goal. Consider also
    tracking/returning the total cost and number of nodes expanded, since
    the assignment asks you to report these for the comparative analysis.
    """
    queue = util.PriorityQueue()
    start = problem.getStartState() if startState is None else startState

    if goalState is not None:
        isGoal = lambda s: s == goalState
        heuristic = lambda s: problem.getHeuristic(s, goalState)
    else:
        isGoal = problem.isGoalState
        heuristic = problem.getHeuristic


    gValues = {start: 0}        # state -> cheapest gn found so far
    parent = {}                 # state -> (previous state, action taken)
    visited = set()             # states whose optimal gn is finalized


    startHn = problem.getHeuristic(start)
    startFn = 0 + startHn
    queue.push(start, startFn)

    nodesExpanded = 0

    print("Beginning A* search:\n")

    while not queue.isEmpty():
        state = queue.pop() # get cheapest fn state

        if state in visited:
            continue # if optimal path to state alr present, skip

        visited.add(state)
        nodesExpanded += 1
        print("Node Expanded: ", state)

        gn = gValues[state]
 
        if isGoal(state):
            return _reconstructPath(parent, state), gn, nodesExpanded

        for successor, action, stepCost in problem.getSuccessors(state):
            if stepCost < 0:
                raise ValueError("A* Search requires non-negative costs")

            gnSuccessor = gn + stepCost

            if successor not in gValues or gnSuccessor < gValues[successor]:
                gValues[successor] = gnSuccessor
                parent[successor] = (state, action)

                hnSuccessor = heuristic(successor)
                fnSuccessor = hnSuccessor + gnSuccessor

                queue.update(successor, fnSuccessor)

    return None, float('inf'), nodesExpanded

def _reconstructPath(parent, goal):
    path = []
    state = goal
    while state in parent:
        previousState, action = parent[state]
        path.append(action)
        state = previousState
    path.reverse()
    return path




def dijkstraSearch(problem):
    """
    Uniform-cost search: expand the node with the lowest cumulative path
    cost (g) first, ignoring the heuristic entirely (equivalent to A* with
    h(state) = 0 for every state).

    Like aStarSearch, this must work generically on any SearchProblem.
    You may reuse/adapt your CS 102 - DSA implementation here.
    """
    frontier = util.PriorityQueue()
    start = problem.getStartState()

    # Each queue item stores: (current state, actions taken, path cost).
    frontier.push((start, [], 0), 0)

    # Cheapest path discovered to each state. This also prevents cycles
    # from making us repeatedly explore the same states.
    bestCost = {start: 0}
    nodesExpanded = 0

    while not frontier.isEmpty():
        state, path, pathCost = frontier.pop()

        # A cheaper route may have been added after this entry. In that
        # case, this older queue entry should be ignored.
        if pathCost > bestCost.get(state, float('inf')):
            continue

        nodesExpanded += 1

        if problem.isGoalState(state):
            return path, pathCost, nodesExpanded

        for successor, action, stepCost in problem.getSuccessors(state):
            if stepCost < 0:
                raise ValueError("Dijkstra Search requires non-negative costs")

            newCost = pathCost + stepCost

            if newCost < bestCost.get(successor, float('inf')):
                bestCost[successor] = newCost
                newPath = path + [action]
                frontier.push((successor, newPath, newCost), newCost)

    return None, float('inf'), nodesExpanded


def searchWithStopovers(problem, stopovers):
    """
    Part (d): Route with Stopovers.

    Adapts A* Search so that the resulting route starts at the hub, visits
    every location in `stopovers` (in some order you determine), and
    returns to the hub - using A* Search to find the route between each
    consecutive pair of locations.

    This is the function you should pseudocode/implement for Question 1(d).
    stopovers: a list of states/locations that must all be visited before
               returning to the start state.

    Should return the complete route, its total cost, and the order in
    which stopovers were visited (see assignment spec for exact output
    requirements).
    """
    "*** YOUR STOPOVER-ROUTING CODE HERE ***"

    hub = problem.getStartState()
    points = [hub] + list(stopovers)

    # pairwise A* between every ordered pair of points
    pairResults = {}
    totalNodesExpanded = 0

    for a, b in itertools.permutations(points, 2):
        # here, we assume that we have means to get heuristics btw an arbitary start and goal 
        # instead of just problems
        path, cost, nodes = aStarSearch(problem, startState=a, goalState=b)
        pairResults[(a, b)] = (path, cost)  # path/cost may be None/inf
        totalNodesExpanded += nodes

    # brute-force best order of stopovers (hub -> ... -> hub)
    # implicitly skips any order that relies on an unreachable path btw stopovers

    bestOrder, bestCost = None, float('inf')

    for perm in itertools.permutations(stopovers):
        order = [hub] + list(perm) + [hub]
        cost = sum(pairResults[(order[i], order[i + 1])][1]
                   for i in range(len(order) - 1))
        if cost < bestCost:
            bestCost, bestOrder = cost, order

    if bestOrder is None:
        raise ValueError("No valid route visits all stopovers and returns to the hub")

    # stitch full path from the winning order.
    totalPath = []
    for i in range(len(bestOrder) - 1):
        totalPath += pairResults[(bestOrder[i], bestOrder[i + 1])][0]

    return totalPath, bestCost, totalNodesExpanded, bestOrder[1:-1]