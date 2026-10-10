"""Generate animated visualizations of the A* robot-navigation routes."""

import argparse
import io
import os
import re
from contextlib import redirect_stdout
from pathlib import Path


PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
MATPLOTLIB_CACHE = PROJECT_DIRECTORY / ".matplotlib-cache"
MATPLOTLIB_CACHE.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MATPLOTLIB_CACHE))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import ListedColormap

from comparativeAnalysis import buildRobotCases
from robotNavigation import RobotNavigationProblem
from search import aStarSearch, dijkstraSearch


ACTION_CHANGES = {
    "Up": (-1, 0),
    "Down": (1, 0),
    "Left": (0, -1),
    "Right": (0, 1),
}


def traceRoute(start, actions):
    """Convert an action list into every grid position visited by the robot."""
    positions = [start]
    row, column = start

    for action in actions:
        rowChange, columnChange = ACTION_CHANGES[action]
        row += rowChange
        column += columnChange
        positions.append((row, column))

    return positions


def makeFilename(caseName):
    """Turn a display name into a portable lowercase filename."""
    return re.sub(r"[^a-z0-9]+", "_", caseName.lower()).strip("_") + ".gif"


def solveWithTrace(searchFunction, problem):
    """Run a search quietly and retain the order in which states expand."""
    expandedStates = []
    with redirect_stdout(io.StringIO()):
        actions, cost, nodesExpanded = searchFunction(
            problem,
            onExpand=expandedStates.append,
        )
    return actions, cost, nodesExpanded, expandedStates


def animateRoute(caseName, grid, start, goal, outputDirectory, framesPerSecond=5):
    """Solve one grid with A* and save an animation of its resulting route."""
    problem = RobotNavigationProblem(grid, start, goal)
    actions, cost, nodesExpanded, _ = solveWithTrace(aStarSearch, problem)

    if actions is None:
        raise ValueError(f"No route found for {caseName}")

    positions = traceRoute(start, actions)
    # Hold the completed route briefly so the destination is easy to inspect.
    animationPositions = positions + [positions[-1]] * (2 * framesPerSecond)

    obstacleMap = [
        [1 if cell == "#" else 0 for cell in row]
        for row in grid
    ]

    figure, axis = plt.subplots(figsize=(9, 6))
    axis.imshow(
        obstacleMap,
        cmap=ListedColormap(["#f8fafc", "#334155"]),
        origin="upper",
        vmin=0,
        vmax=1,
    )

    startRow, startColumn = start
    goalRow, goalColumn = goal
    axis.scatter(startColumn, startRow, marker="s", s=130, color="#2563eb", label="Start")
    axis.scatter(goalColumn, goalRow, marker="*", s=210, color="#16a34a", label="Goal")

    trail, = axis.plot([], [], color="#38bdf8", linewidth=3, label="A* route")
    robot = axis.scatter([], [], s=150, color="#dc2626", edgecolor="white", zorder=5, label="Robot")

    rowCount = len(grid)
    columnCount = len(grid[0])
    axis.set_xticks(range(columnCount))
    axis.set_yticks(range(rowCount))
    axis.set_xticks([value - 0.5 for value in range(1, columnCount)], minor=True)
    axis.set_yticks([value - 0.5 for value in range(1, rowCount)], minor=True)
    axis.grid(which="minor", color="#cbd5e1", linewidth=0.5)
    axis.tick_params(which="minor", bottom=False, left=False)
    axis.set_xlabel("Column")
    axis.set_ylabel("Row")
    axis.legend(loc="upper left", bbox_to_anchor=(1.01, 1))

    def update(frameIndex):
        visibleIndex = min(frameIndex, len(positions) - 1)
        visited = positions[: visibleIndex + 1]
        rows = [position[0] for position in visited]
        columns = [position[1] for position in visited]

        trail.set_data(columns, rows)
        robot.set_offsets([[columns[-1], rows[-1]]])
        axis.set_title(
            f"{caseName}: A* Robot Navigation\n"
            f"Step {visibleIndex}/{len(actions)} | Cost {cost} | "
            f"Nodes expanded {nodesExpanded}"
        )
        return trail, robot

    animation = FuncAnimation(
        figure,
        update,
        frames=len(animationPositions),
        interval=1000 / framesPerSecond,
        repeat=True,
    )

    outputDirectory.mkdir(parents=True, exist_ok=True)
    outputPath = outputDirectory / makeFilename(caseName)
    animation.save(outputPath, writer=PillowWriter(fps=framesPerSecond), dpi=110)
    plt.close(figure)
    return outputPath, cost, nodesExpanded


def preparePanel(axis, grid, start, goal, algorithmName):
    """Draw the fixed grid elements for one algorithm panel."""
    obstacleMap = [
        [1 if cell == "#" else 0 for cell in row]
        for row in grid
    ]
    axis.imshow(
        obstacleMap,
        cmap=ListedColormap(["#f8fafc", "#334155"]),
        origin="upper",
        vmin=0,
        vmax=1,
    )

    startRow, startColumn = start
    goalRow, goalColumn = goal
    axis.scatter(startColumn, startRow, marker="s", s=100, color="#2563eb", label="Start")
    axis.scatter(goalColumn, goalRow, marker="*", s=170, color="#16a34a", label="Goal")

    expanded = axis.scatter(
        [],
        [],
        marker="s",
        s=70,
        color="#facc15",
        alpha=0.55,
        label="Expanded",
    )
    trail, = axis.plot([], [], color="#38bdf8", linewidth=3, label="Final route")
    robot = axis.scatter(
        [startColumn],
        [startRow],
        s=130,
        color="#dc2626",
        edgecolor="white",
        zorder=5,
        label="Robot",
    )

    rowCount = len(grid)
    columnCount = len(grid[0])
    axis.set_xticks(range(columnCount))
    axis.set_yticks(range(rowCount))
    axis.set_xticks([value - 0.5 for value in range(1, columnCount)], minor=True)
    axis.set_yticks([value - 0.5 for value in range(1, rowCount)], minor=True)
    axis.grid(which="minor", color="#cbd5e1", linewidth=0.45)
    axis.tick_params(which="minor", bottom=False, left=False)
    axis.set_xlabel("Column")
    axis.set_ylabel("Row")
    axis.set_title(algorithmName)
    return expanded, trail, robot


def animateComparison(
    caseName,
    grid,
    start,
    goal,
    outputDirectory,
    framesPerSecond=5,
):
    """Animate A* and Dijkstra exploration and final routes side by side."""
    algorithmData = []
    for algorithmName, searchFunction in (
        ("A*", aStarSearch),
        ("Dijkstra", dijkstraSearch),
    ):
        problem = RobotNavigationProblem(grid, start, goal)
        actions, cost, nodesExpanded, expandedStates = solveWithTrace(
            searchFunction,
            problem,
        )
        if actions is None:
            raise ValueError(f"{algorithmName} found no route for {caseName}")
        algorithmData.append(
            {
                "name": algorithmName,
                "positions": traceRoute(start, actions),
                "cost": cost,
                "expanded": expandedStates,
                "nodesExpanded": nodesExpanded,
            }
        )

    largestExpansionCount = max(
        len(data["expanded"])
        for data in algorithmData
    )
    # Show the exploration in at most about 35 frames, even on large grids.
    nodesPerFrame = max(1, (largestExpansionCount + 34) // 35)
    explorationFrames = (largestExpansionCount + nodesPerFrame - 1) // nodesPerFrame
    routeFrames = max(len(data["positions"]) for data in algorithmData)
    pauseFrames = 2 * framesPerSecond
    totalFrames = explorationFrames + routeFrames + pauseFrames

    figure, axes = plt.subplots(1, 2, figsize=(15, 7), constrained_layout=True)
    artists = [
        preparePanel(axis, grid, start, goal, data["name"])
        for axis, data in zip(axes, algorithmData)
    ]
    axes[0].legend(loc="upper center", bbox_to_anchor=(1.05, -0.10), ncol=5)
    figure.suptitle(f"{caseName}: A* vs Dijkstra", fontsize=16)

    def update(frameIndex):
        updatedArtists = []
        exploring = frameIndex < explorationFrames

        for axis, data, panelArtists in zip(axes, algorithmData, artists):
            expandedArtist, trail, robot = panelArtists

            if exploring:
                expandedCount = min(
                    (frameIndex + 1) * nodesPerFrame,
                    len(data["expanded"]),
                )
                visibleExpanded = data["expanded"][:expandedCount]
                routeStep = 0
                phase = f"Exploring: {expandedCount}/{data['nodesExpanded']} nodes"
            else:
                visibleExpanded = data["expanded"]
                routeStep = min(
                    frameIndex - explorationFrames,
                    len(data["positions"]) - 1,
                )
                phase = f"Route: {routeStep}/{len(data['positions']) - 1} steps"

            expandedOffsets = [
                [column, row]
                for row, column in visibleExpanded
            ]
            expandedArtist.set_offsets(expandedOffsets)

            visitedRoute = data["positions"][: routeStep + 1]
            routeRows = [position[0] for position in visitedRoute]
            routeColumns = [position[1] for position in visitedRoute]
            trail.set_data(routeColumns, routeRows)
            robot.set_offsets([[routeColumns[-1], routeRows[-1]]])

            axis.set_title(
                f"{data['name']}\n{phase} | Cost {data['cost']}"
            )
            updatedArtists.extend(panelArtists)

        return updatedArtists

    animation = FuncAnimation(
        figure,
        update,
        frames=totalFrames,
        interval=1000 / framesPerSecond,
        repeat=True,
    )

    outputDirectory.mkdir(parents=True, exist_ok=True)
    baseName = makeFilename(caseName).removesuffix(".gif")
    outputPath = outputDirectory / f"{baseName}_astar_vs_dijkstra.gif"
    animation.save(outputPath, writer=PillowWriter(fps=framesPerSecond), dpi=90)
    plt.close(figure)
    return outputPath, algorithmData


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=PROJECT_DIRECTORY / "robotSimulations",
    )
    parser.add_argument("--fps", type=int, default=5)
    parser.add_argument(
        "--mode",
        choices=("comparison", "solo", "all"),
        default="comparison",
        help="Generate side-by-side comparisons, A*-only routes, or both.",
    )
    arguments = parser.parse_args()

    if arguments.fps <= 0:
        parser.error("--fps must be positive")

    for caseName, grid, start, goal in buildRobotCases():
        if arguments.mode in {"solo", "all"}:
            outputPath, cost, nodesExpanded = animateRoute(
                caseName,
                grid,
                start,
                goal,
                arguments.output_directory,
                arguments.fps,
            )
            print(
                f"Saved {outputPath} "
                f"(A* cost={cost}, nodes expanded={nodesExpanded})"
            )

        if arguments.mode in {"comparison", "all"}:
            outputPath, algorithmData = animateComparison(
                caseName,
                grid,
                start,
                goal,
                arguments.output_directory,
                arguments.fps,
            )
            summary = ", ".join(
                f"{data['name']} expanded {data['nodesExpanded']}"
                for data in algorithmData
            )
            print(f"Saved {outputPath} ({summary})")


if __name__ == "__main__":
    main()
