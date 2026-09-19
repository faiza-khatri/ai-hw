from search import SearchProblem


class courierDeliveryProblem(SearchProblem):
    def __init__(self, connections, heuristics, tracktypes, start, goal):
        """
            start : string 
            goal : string
            connections : dict[area][area] -> float (km) or None
            heuristics : dict[area][area] -> float (km)
            tracktypes : dict[area][area] -> 'M' 'S" or 'N' or None 
        """
        self.connections = connections
        self.tracktypes = tracktypes
        self.heuristics = heuristics
        self.start = start
        self.goal = goal
        self.currentState = start
        self.penalty = {'M': 1.0, 'S': 2.0, 'N': 3.0}

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        """
            state : string
        """
        return state == self.goal

    def getSuccessors(self, state):
        successors = []
        for neighbor, dist in self.connections[state].items():
            if dist is None or dist <= 0:
                continue
            track = self.tracktypes[state][neighbor]
            cost = dist * self.penalty[track]
            action = f"{state} -> {neighbor}"
            successors.append((neighbor, action, cost))
        return successors

    def getCostOfActions(self, actions):
        if actions is None:
            return float('inf')

        total = 0
        for action in actions:
            src, dest = action.split(" -> ")
            dist = self.connections[src][dest]
            track = self.tracktypes[src][dest]
            cost = dist * self.penalty[track]
            total += cost

        return total

    def getHeuristic(self, state):
        return self.heuristics[state][self.goal]
