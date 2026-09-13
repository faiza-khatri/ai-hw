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


def aStarSearch(problem):
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
    "*** YOUR A* CODE HERE ***"
    queue = util.PriorityQueue()

    state = problem.getStartState()
    
    gn = 0
    hn = problem.getHeuristic(state)
    fn = gn + hn

    currentState = (state, [], gn) # current node, actions, cost 

    queue.push(currentState, fn)

    visited = {}
    nodesExpanded = 0

    print("Beginning A* search:\n")

    while not queue.isEmpty():
        state, path, gn = queue.pop()
        print("Node Expanded: ", state)


        if state in visited and visited[state] <= gn:
            continue

        visited[state] = gn
        nodesExpanded += 1

        if problem.isGoalState(state):
            print("Goal state reached. Path observed:")
            for action in path:
                print(action)

            print("Number of nodes expanded", nodesExpanded)
            print("Total cost: ", gn)
            return path, gn, nodesExpanded

        for successor, action, stepCost in state.getSuccessors():
            gnSucessor = gn + stepCost
            if successor not in visited or newCost < visited[successor]:
                hnSuccessor = problem.getHeuristic(successor)
                fnSuccessor = gnSucessor + hnSuccessor

                newPath = path + [action]

                queue.update((successor, path, gnSucessor), fnSuccessor)


    return None, float('inf'), nodesExpanded



def dijkstraSearch(problem):
    """
    Uniform-cost search: expand the node with the lowest cumulative path
    cost (g) first, ignoring the heuristic entirely (equivalent to A* with
    h(state) = 0 for every state).

    Like aStarSearch, this must work generically on any SearchProblem.
    You may reuse/adapt your CS 102 - DSA implementation here.
    """
    "*** YOUR DIJKSTRA CODE HERE ***"
    util.raiseNotDefined()


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
    util.raiseNotDefined()
