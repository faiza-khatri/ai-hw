from search import SearchProblem
import csv

def _loadMatrix(path, parseCell):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = [row for row in csv.reader(f) if row and any(cell.strip() for cell in row)]
 
    if not rows:
        raise ValueError(f"{path} is empty")
 
    columnAreas = [name.strip() for name in rows[0][1:]]
 
    matrix = {}
    for row in rows[1:]:
        rowArea = row[0].strip()
        cells = row[1:]
 
        if len(cells) != len(columnAreas):
            raise ValueError(
                f"{path}: row '{rowArea}' has {len(cells)} values, "
                f"but the header has {len(columnAreas)} areas"
            )
 
        matrix[rowArea] = {
            colArea: parseCell(cell.strip())
            for colArea, cell in zip(columnAreas, cells)
        }
 
    return matrix
 


class courierDeliveryProblem(SearchProblem):
    def __init__(self, connectionsFile, heuristicsFile, trackTypesFile, start, goal):
        """
            start : string 
            goal : string
            connectionsFile : path to Connections.csv
            heuristicsFile  : path to heuristics.csv
            trackTypesFile  : path to TrackType.csv
        """


        # connections : dict[area][area] -> float (km) or None
        # heuristics : dict[area][area] -> float (km)
        # tracktypes : dict[area][area] -> 'M' 'S" or 'N' or None 

        self.connections = self._loadConnections(connectionsFile)
        self.heuristics = self._loadHeuristics(heuristicsFile)
        self.tracktypes = self._loadTrackTypes(trackTypesFile)

        self.start = start
        self.goal = goal
        self.penalty = {'M': 1.0, 'S': 2.0, 'N': 3.0}


    @staticmethod
    def _loadConnections(path):
        """Connections.csv -> dict[area][area] -> float km, or None for -1 (no direct connection)."""
        def parseCell(cell):
            value = float(cell)
            return None if (value == -1 or value == 0) else value
        return _loadMatrix(path, parseCell)
 
    @staticmethod
    def _loadHeuristics(path):
        """heuristics.csv -> dict[area][area] -> float km (defined for every pair)."""
        return _loadMatrix(path, lambda cell: float(cell))
 
    @staticmethod
    def _loadTrackTypes(path):
        """TrackType.csv -> dict[area][area] -> 'M' / 'S' / 'N', or None for -1 (no connection) or 0 (self)."""
        def parseCell(cell):
            if cell in ("-1", "0"):
                return None
            if cell not in ("M", "S", "N"):
                raise ValueError(f"Unexpected track type '{cell}' (expected M, S, N, -1, or 0)")
            return cell
        return _loadMatrix(path, parseCell)
 

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
