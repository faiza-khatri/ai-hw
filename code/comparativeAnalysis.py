"""Run the experiments used for Question 1(c)."""

import csv
import io
from contextlib import redirect_stdout
from itertools import groupby
from pathlib import Path

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


def loadMatrix(filename, convertValue):
    with (CSV_DIRECTORY / filename).open(
        newline="", encoding="utf-8-sig"
    ) as csvFile:
        rows = list(csv.reader(csvFile))

    columnNames = rows[0][1:]
    matrix = {
        row[0]: {
            column: convertValue(value)
            for column, value in zip(columnNames, row[1:])
        }
        for row in rows[1:]
    }
    return matrix


def loadCourierData():
    connections = loadMatrix("Connections.csv", float)
    heuristics = loadMatrix("heuristics.csv", float)
    trackTypes = loadMatrix(
        "TrackType.csv", lambda value: None if value == "-1" else value
    )
    return connections, heuristics, trackTypes


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
    connections, heuristics, trackTypes = loadCourierData()
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
                connections, heuristics, trackTypes, start, goal
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


if __name__ == "__main__":
    printMarkdownTable("Robot Navigation", compareRobotNavigation())
    printMarkdownTable("Courier Delivery", compareCourierDelivery())