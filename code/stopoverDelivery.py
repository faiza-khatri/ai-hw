"""Plan a Karachi delivery run with multiple stopovers and a hub return."""

import argparse
import io
from contextlib import redirect_stdout
from pathlib import Path

from courierDelivery import courierDeliveryProblem
from search import searchWithStopovers


PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
CSV_DIRECTORY = PROJECT_DIRECTORY / "csv"


def locationsFromActions(hub, actions):
    """Convert courier edge actions into the complete sequence of locations."""
    locations = [hub]
    for action in actions:
        _source, destination = action.split(" -> ")
        locations.append(destination)
    return locations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hub", default="Saddar (Hub)")
    parser.add_argument(
        "--stopovers",
        nargs="*",
        default=["Korangi", "Gulistan-e-Johar", "Clifton"],
        help="Area names to visit before returning to the hub.",
    )
    arguments = parser.parse_args()

    problem = courierDeliveryProblem(
        CSV_DIRECTORY / "Connections.csv",
        CSV_DIRECTORY / "heuristics.csv",
        CSV_DIRECTORY / "TrackType.csv",
        arguments.hub,
        arguments.hub,
    )

    # A* normally prints every expanded state. Keep this report focused on the
    # final multi-stop route while searchWithStopovers still returns the count.
    with redirect_stdout(io.StringIO()):
        actions, totalCost, nodesExpanded, stopoverOrder = searchWithStopovers(
            problem,
            arguments.stopovers,
        )

    completeRoute = locationsFromActions(arguments.hub, actions)

    print("Requested stopovers:", " -> ".join(arguments.stopovers) or "None")
    print("Optimized stopover order:", " -> ".join(stopoverOrder) or "None")
    print("Complete route:", " -> ".join(completeRoute))
    print("Total route cost:", totalCost)
    print("Nodes expanded during pairwise A* searches:", nodesExpanded)


if __name__ == "__main__":
    main()
