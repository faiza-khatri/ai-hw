"""Run the experiments used for Question 1(c)."""

import csv
import io
from contextlib import redirect_stdout
from itertools import groupby
from pathlib import Path
import matplotlib.pyplot as plt
import os

from courierDelivery import courierDeliveryProblem
from robotNavigation import RobotNavigationProblem
from search import aStarSearch, dijkstraSearch


CSV_DIRECTORY = Path(__file__).resolve().parent.parent / "csv"


def runQuietly(searchFunction, problem):
    """Run a search without A*'s step-by-step console messages."""
    with redirect_stdout(io.StringIO()):
        return searchFunction(problem)


def compressRobotRoute(actions):
    """Turn repeated actions into a compact but complete route description."""
    parts = []
    for action, group in groupby(actions):
        count = len(list(group))
        parts.append(f"{action} x{count}")
    return ", ".join(parts)


def formatCourierRoute(start, actions):
    locations = [start]
    for action in actions:
        _, destination = action.split(" -> ")
        locations.append(destination)
    return " -> ".join(locations)


def buildRobotCases():
    openGrid = ["." * 15 for _ in range(15)]

    wallCells = [["."] * 17 for _ in range(12)]
    for row in range(11):
        wallCells[row][8] = "#"
    wallGrid = ["".join(row) for row in wallCells]

    zigzagCells = [["."] * 21 for _ in range(15)]
    barriers = [(4, 13), (8, 1), (12, 13), (16, 1)]
    for column, gapRow in barriers:
        for row in range(15):
            if row != gapRow:
                zigzagCells[row][column] = "#"
    zigzagGrid = ["".join(row) for row in zigzagCells]

    return [
        ("Open 15x15", openGrid, (7, 1), (7, 13)),
        ("Single-wall detour", wallGrid, (2, 2), (2, 14)),
        ("Alternating barriers", zigzagGrid, (7, 1), (7, 19)),
    ]


def compareRobotNavigation():
    results = []
    algorithms = [("A*", aStarSearch), ("Dijkstra", dijkstraSearch)]

    for caseName, grid, start, goal in buildRobotCases():
        for algorithmName, searchFunction in algorithms:
            problem = RobotNavigationProblem(grid, start, goal)
            path, cost, expanded = runQuietly(searchFunction, problem)
            results.append(
                (caseName, algorithmName, cost, expanded, compressRobotRoute(path))
            )

    return results


def compareCourierDelivery():
    cases = [
        ("Saddar to Korangi", "Saddar (Hub)", "Korangi"),
        ("Lyari to Johar", "Lyari", "Gulistan-e-Johar"),
        ("Orangi to DHA", "Orangi Town", "DHA"),
        ("North Nazimabad to Malir", "North Nazimabad", "Malir"),
    ]
    algorithms = [("A*", aStarSearch), ("Dijkstra", dijkstraSearch)]
    results = []

    for caseName, start, goal in cases:
        for algorithmName, searchFunction in algorithms:
            problem = courierDeliveryProblem(
                "csv/Connections.csv", "csv/heuristics.csv", "csv/TrackType.csv", start, goal
            )
            path, cost, expanded = runQuietly(searchFunction, problem)
            results.append(
                (
                    caseName,
                    algorithmName,
                    cost,
                    expanded,
                    formatCourierRoute(start, path),
                )
            )

    return results


def printMarkdownTable(title, results):
    print(f"## {title}")
    print()
    print("| Configuration | Algorithm | Cost | Nodes expanded | Route |")
    print("|---|---:|---:|---:|---|")
    for caseName, algorithm, cost, expanded, route in results:
        print(f"| {caseName} | {algorithm} | {cost} | {expanded} | {route} |")
    print()

def _groupByCase(results):
    """
    Turns the flat (case, algorithm, cost, expanded, route) results list into
    caseNames (in first-seen order) plus, per algorithm, a list of
    nodes-expanded counts aligned to those caseNames -- ready to hand
    straight to a grouped bar chart.
    """
    caseNames = []
    expandedByAlgorithm = {}
 
    for caseName, algorithm, _cost, expanded, _route in results:
        if caseName not in caseNames:
            caseNames.append(caseName)
        expandedByAlgorithm.setdefault(algorithm, {})[caseName] = expanded
 
    algorithms = list(expandedByAlgorithm.keys())
    series = {
        algorithm: [expandedByAlgorithm[algorithm][case] for case in caseNames]
        for algorithm in algorithms
    }
    return caseNames, series
 
 
def plotNodesExpanded(results, title, outputPath):
    """Grouped bar chart: nodes expanded per configuration, one bar per algorithm."""
    caseNames, series = _groupByCase(results)
    algorithms = list(series.keys())
 
    x = range(len(caseNames))
    barWidth = 0.8 / len(algorithms)
 
    fig, ax = plt.subplots(figsize=(max(7, len(caseNames) * 2.2), 5))
    for i, algorithm in enumerate(algorithms):
        offset = (i - (len(algorithms) - 1) / 2) * barWidth
        positions = [xi + offset for xi in x]
        ax.bar(positions, series[algorithm], barWidth, label=algorithm)
 
    ax.set_ylabel("Nodes expanded")
    ax.set_title(title)
    ax.set_xticks(list(x))
    ax.set_xticklabels(caseNames, rotation=15, ha="right", fontsize=9)
    ax.legend()
 
    fig.tight_layout()
    fig.savefig(outputPath, dpi=150)
    plt.close(fig)
    return outputPath
 
 
if __name__ == "__main__":
    os.makedirs("comparisonOutput", exist_ok=True)

    robotResults = compareRobotNavigation()
    courierResults = compareCourierDelivery()
 
    printMarkdownTable("Robot Navigation", robotResults)
    printMarkdownTable("Courier Delivery", courierResults)
 
    robotChart = plotNodesExpanded(
        robotResults, "Robot Navigation: nodes expanded (A* vs Dijkstra)", "comparisonOutput/robot_nodes_expanded.png"
    )
    courierChart = plotNodesExpanded(
        courierResults, "Courier Delivery: nodes expanded (A* vs Dijkstra)", "comparisonOutput/courier_nodes_expanded.png"
    )
 
    print(f"Saved {robotChart}")
    print(f"Saved {courierChart}")
 
