from search import SearchProblem
from util import manhattanDistance

class RobotNavigationProblem(SearchProblem):
    def __init__(self, grid, start, goal):
        self.grid = grid
        self.start = start
        self.goal = goal

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state == self.goal


#rough tesing 

if __name__ == "__main__":
    grid = [
        "...",
        ".#.",
        "...",
    ]

    problem = RobotNavigationProblem(
        grid = grid, 
        start=(0,0),
        goal=(2,2),
        )      

    print(problem.getStartState())
    print(problem.isGoalState((0,0)))
    print(problem.isGoalState((2, 2)))