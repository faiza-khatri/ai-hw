"""Question 2: optimize two-variable functions with simulated annealing."""

import argparse
import math
import os
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AnnealingResult:
    bestX: float
    bestY: float
    bestValue: float
    iterations: list
    xHistory: list
    yHistory: list
    valueHistory: list
    acceptedMoves: int


def boothFunction(x, y):
    return (x + 2 * y - 7) ** 2 + (2 * x + y - 5) ** 2


def himmelblauFunction(x, y):
    return (x**2 + y - 11) ** 2 + (x + y**2 - 7) ** 2


def griewankFunction(x, y):
    return 1 + (x**2 + y**2) / 4000 - math.cos(x) * math.cos(y / math.sqrt(2))


def simulatedAnnealing(
    function,
    bounds,
    objective="min",
    neighborhoodSize=0.5,
    startingTemperature=1.0,
    temperatureDecrease=0.1,
    iterationsPerTemperature=100,
    seed=None,
):
    """Optimize a bounded function and retain its full execution history."""
    if objective not in {"min", "max"}:
        raise ValueError("objective must be either 'min' or 'max'")
    if neighborhoodSize <= 0:
        raise ValueError("neighborhoodSize must be positive")
    if startingTemperature <= 0 or temperatureDecrease <= 0:
        raise ValueError("temperatures must be positive")
    if iterationsPerTemperature <= 0:
        raise ValueError("iterationsPerTemperature must be positive")

    (minimumX, maximumX), (minimumY, maximumY) = bounds
    randomGenerator = random.Random(seed)

    currentX = randomGenerator.uniform(minimumX, maximumX)
    currentY = randomGenerator.uniform(minimumY, maximumY)
    currentValue = function(currentX, currentY)

    bestX = currentX
    bestY = currentY
    bestValue = currentValue

    iterations = [0]
    xHistory = [currentX]
    yHistory = [currentY]
    valueHistory = [currentValue]
    acceptedMoves = 0
    iteration = 0
    temperature = startingTemperature

    while temperature > 1e-12:
        for _ in range(iterationsPerTemperature):
            candidateX = currentX + randomGenerator.uniform(
                -neighborhoodSize, neighborhoodSize
            )
            candidateY = currentY + randomGenerator.uniform(
                -neighborhoodSize, neighborhoodSize
            )

            # Keep every proposed neighbor within the function's domain.
            candidateX = min(max(candidateX, minimumX), maximumX)
            candidateY = min(max(candidateY, minimumY), maximumY)
            candidateValue = function(candidateX, candidateY)

            # A negative change is an improvement for the chosen objective.
            objectiveChange = candidateValue - currentValue
            if objective == "max":
                objectiveChange = -objectiveChange

            acceptMove = objectiveChange <= 0
            if not acceptMove:
                acceptanceProbability = math.exp(-objectiveChange / temperature)
                acceptMove = randomGenerator.random() < acceptanceProbability

            if acceptMove:
                currentX = candidateX
                currentY = candidateY
                currentValue = candidateValue
                acceptedMoves += 1

                isNewBest = (
                    currentValue < bestValue
                    if objective == "min"
                    else currentValue > bestValue
                )
                if isNewBest:
                    bestX = currentX
                    bestY = currentY
                    bestValue = currentValue

            iteration += 1
            iterations.append(iteration)
            xHistory.append(currentX)
            yHistory.append(currentY)
            valueHistory.append(currentValue)

        temperature -= temperatureDecrease

    return AnnealingResult(
        bestX,
        bestY,
        bestValue,
        iterations,
        xHistory,
        yHistory,
        valueHistory,
        acceptedMoves,
    )


def findBestRun(function, bounds, restarts, firstSeed, **annealingParameters):
    """Run independent trials and return the best result found."""
    if restarts <= 0:
        raise ValueError("restarts must be positive")

    results = [
        simulatedAnnealing(
            function,
            bounds,
            seed=firstSeed + restart,
            **annealingParameters,
        )
        for restart in range(restarts)
    ]
    return min(results, key=lambda result: result.bestValue)


def plotResult(functionName, result, outputDirectory, showPlot=False):
    matplotlibCache = Path(__file__).resolve().parent.parent / ".matplotlib-cache"
    matplotlibCache.mkdir(exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(matplotlibCache))

    try:
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise RuntimeError(
            "Plotting requires matplotlib. Install it with: python -m pip install matplotlib"
        ) from error

    figure, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    axes[0].plot(result.iterations, result.xHistory, color="tab:blue")
    axes[0].set_ylabel("x")
    axes[0].set_title(f"{functionName}: Simulated Annealing Execution")

    axes[1].plot(result.iterations, result.yHistory, color="tab:orange")
    axes[1].set_ylabel("y")

    axes[2].plot(result.iterations, result.valueHistory, color="tab:green")
    axes[2].set_ylabel("f(x, y)")
    axes[2].set_xlabel("Iteration")

    for axis in axes:
        axis.grid(alpha=0.25)

    figure.tight_layout()
    outputDirectory.mkdir(parents=True, exist_ok=True)
    outputPath = outputDirectory / f"{functionName.lower()}_execution.png"
    figure.savefig(outputPath, dpi=180)

    if showPlot:
        plt.show()
    plt.close(figure)
    return outputPath


def runRequiredFunctions(restarts=20, firstSeed=351, outputDirectory=None, show=False):
    """Minimize all three functions required by the assignment."""
    functions = [
        ("Booth", boothFunction, ((-10, 10), (-10, 10)), {}),
        ("Himmelblau", himmelblauFunction, ((-5, 5), (-5, 5)), {}),
        (
            "Griewank",
            griewankFunction,
            ((-30, 30), (-30, 30)),
            {
                # Its many local minima need slower cooling than the baseline.
                "temperatureDecrease": 0.01,
                "iterationsPerTemperature": 300,
            },
        ),
    ]
    results = []

    for index, (name, function, bounds, tunedParameters) in enumerate(functions):
        parameters = {
            "objective": "min",
            "neighborhoodSize": 0.5,
            "startingTemperature": 1.0,
            "temperatureDecrease": 0.1,
            "iterationsPerTemperature": 100,
        }
        parameters.update(tunedParameters)

        result = findBestRun(
            function,
            bounds,
            restarts,
            firstSeed + index * restarts,
            **parameters,
        )
        results.append((name, result, "Min"))

        if outputDirectory is not None:
            plotResult(name+"_min", result, outputDirectory, show)

    for index, (name, function, bounds, tunedParameters) in enumerate(functions):
            parameters = {
                "objective": "max",
                "neighborhoodSize": 0.5,
                "startingTemperature": 1.0,
                "temperatureDecrease": 0.1,
                "iterationsPerTemperature": 100,
            }
            parameters.update(tunedParameters)
    
            result = findBestRun(
                function,
                bounds,
                restarts,
                firstSeed + index * restarts,
                **parameters,
            )
            results.append((name, result, "Max"))
    
            if outputDirectory is not None:
                plotResult(name+"_max", result, outputDirectory, show)

    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restarts", type=int, default=20)
    parser.add_argument("--seed", type=int, default=351)
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "plots",
    )
    parser.add_argument("--show", action="store_true")
    arguments = parser.parse_args()

    results = runRequiredFunctions(
        arguments.restarts,
        arguments.seed,
        arguments.output_directory,
        arguments.show,
    )

    print("Function     Max/Min      Best x       Best y        Best f(x, y)   Accepted")
    print("-----------------------------------------------------------------")
    for name, result, obj in results:
        print(
            f"{name:<12} "
            f"{obj:<10}"
            f"{result.bestX:>11.6f} "
            f"{result.bestY:>12.6f} "
            f"{result.bestValue:>18.10f} "
            f"{result.acceptedMoves:>9}"
        )


if __name__ == "__main__":
    main()
