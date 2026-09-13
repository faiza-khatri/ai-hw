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


    def getSuccessors(self, state):
        row, col = state
        successors = []

        directions = [
            ("Up", -1, 0),
            ("Down", 1, 0),
            ("Left", 0, -1),
            ("Right", 0, 1),
        ]

        for action, row_change, col_change in directions:

            new_row = row + row_change
            new_col = col + col_change

            if not (0 <= new_row < len(self.grid)):
                continue

            if not (0 <= new_col < len(self.grid[new_row])):
                continue

            if self.grid[new_row][new_col] == "#":
                continue

            new_state = (new_row, new_col)
            successors.append((new_state, action, 1))

        return successors    

    def getCostOfActions(self, actions):
        if actions is None:
            return float("inf")

        return len(actions)

    def getHeuristic(self, state):
        return manhattanDistance(state, self.goal)


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

    # print(problem.getStartState())
    # print(problem.isGoalState((0,0)))
    # print(problem.isGoalState((2,2)))
    # print(problem.getSuccessors((0,0)))
    print(problem.getCostOfActions(["Right", "Right", "Down", "Down"]))
    print(problem.getHeuristic((0, 0)))
    print(problem.getHeuristic((2, 2)))