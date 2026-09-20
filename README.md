# Artificial Intelligence Assignment 1

> **AI-assisted README:** This README was created with AI assistance purely to
> help the checker navigate the codebase, locate the work for each question,
> and reproduce the submitted results.

This repository contains the implementation, experiments, and analysis for two
problems:

1. **Question 1 — Search:** A* and Dijkstra search for robot navigation and
   courier delivery, followed by multi-stop route planning.
2. **Question 2 — Optimization:** Simulated annealing for minimizing and
   maximizing the Booth, Himmelblau, and Griewank functions.

The source files remain together in `code/` so their imports and the assignment
interface continue to work. The sections below identify exactly which files and
outputs belong to each question.

## Setup

Run all commands from the `ai-hw` directory.

```powershell
python -m pip install -r requirements.txt
```

The project uses Python, Matplotlib, and Pillow. Input data is already included
in `csv/`.

## Question 1 — Search and Route Planning

Question 1 implements two generic graph-search algorithms and applies them to
two different problems. A* uses a problem-specific heuristic, while Dijkstra
uses only the accumulated route cost. Both return the selected path, its cost,
and the number of nodes expanded.

### Question 1 files

| File | Purpose |
|---|---|
| [`code/search.py`](code/search.py) | Generic A*, Dijkstra, and multi-stop search algorithms |
| [`code/robotNavigation.py`](code/robotNavigation.py) | Grid navigation problem with obstacles and Manhattan-distance heuristic |
| [`code/courierDelivery.py`](code/courierDelivery.py) | Karachi delivery graph, track penalties, and aerial-distance heuristic |
| [`code/comparativeAnalysis.py`](code/comparativeAnalysis.py) | Reproducible A* versus Dijkstra experiments and comparison charts |
| [`code/stopoverDelivery.py`](code/stopoverDelivery.py) | Runnable Question 1(d) multi-stop delivery example |
| [`code/robotSimulation.py`](code/robotSimulation.py) | Optional animated robot-navigation demonstrations |
| [`code/util.py`](code/util.py) | Shared priority queue and distance utility functions |
| [`csv/`](csv/) | Connections, track types, and heuristic values for courier delivery |
| [`comparative_analysis.md`](comparative_analysis.md) | Complete Question 1 results, discussion, pseudocode, and complexity analysis |

### Run the A* and Dijkstra comparison

```powershell
python .\code\comparativeAnalysis.py
```

This prints the results for all robot and courier test cases and regenerates:

- `comparisonOutput/robot_nodes_expanded.png`
- `comparisonOutput/courier_nodes_expanded.png`

The experiments confirm that A* and Dijkstra find routes with the same optimal
cost. A* usually expands fewer nodes when its heuristic closely represents the
remaining route cost.

### Run the multi-stop delivery example

```powershell
python .\code\stopoverDelivery.py
```

The default example begins at `Saddar (Hub)`, visits Korangi,
Gulistan-e-Johar, and Clifton, and returns to the hub. The program uses A* to
precompute each ordered pair of locations, tests every stopover permutation,
and joins the segments belonging to the cheapest reachable order.

Expected optimized order and cost:

```text
Gulistan-e-Johar -> Korangi -> Clifton
Total route cost: 75.0
```

A custom run can be supplied from the command line:

```powershell
python .\code\stopoverDelivery.py --hub "Saddar (Hub)" --stopovers Clifton Korangi
```

The implementation also handles repeated stopovers, a redundant hub entry, an
empty stopover list, and unreachable complete routes.

### Generate robot simulations

```powershell
python .\code\robotSimulation.py
```

This regenerates the side-by-side A* and Dijkstra GIFs in
`robotSimulations/`. In each animation, yellow cells show expanded states and
the red robot follows the final cyan route from the blue start to the green
goal.

To generate both the comparison animations and the earlier A*-only versions:

```powershell
python .\code\robotSimulation.py --mode all
```

## Question 2 — Simulated Annealing

Question 2 uses simulated annealing to minimize and maximize three continuous
functions. Better moves are always accepted, while worse moves may be accepted
according to the current temperature. This probabilistic behavior helps the
search escape local optima.

### Question 2 files

| File | Purpose |
|---|---|
| [`code/simulatedAnnealing.py`](code/simulatedAnnealing.py) | Simulated annealing, benchmark functions, seeded restarts, and plot generation |
| [`optimization_analysis.md`](optimization_analysis.md) | Complete formulation, pseudocode, tuning discussion, results, and final figures |
| [`newPlots/`](newPlots/) | Final minimum and maximum execution plots used in the report |
| [`plots/`](plots/) and `OLD plots (rough work)/` | Earlier experimental plots retained as rough-work evidence |

### Run the optimization experiments

```powershell
python .\code\simulatedAnnealing.py
```

The default run performs 20 reproducible seeded restarts for each function and
objective, prints the best result, and regenerates all six figures in
`newPlots/`.

Booth and Himmelblau use the assignment's baseline cooling schedule. Griewank
uses slower cooling and more iterations because its oscillating surface has
many local minima. Full parameter values and the resulting optima are recorded
in [`optimization_analysis.md`](optimization_analysis.md).

Alternative values can be supplied when experimenting:

```powershell
python .\code\simulatedAnnealing.py --restarts 20 --seed 351 --output-directory newPlots
```

## Repository Map

```text
ai-hw/
|-- README.md                    Project guide and reproduction commands
|-- comparative_analysis.md     Question 1 report
|-- optimization_analysis.md    Question 2 report
|-- requirements.txt            Python dependencies
|-- code/                       Implementations and runnable experiments
|-- csv/                        Question 1 courier data
|-- comparisonOutput/           Question 1 comparison charts
|-- robotSimulations/           Question 1 optional GIF demonstrations
|-- newPlots/                   Question 2 final figures
|-- plots/                      Question 2 earlier plots
|-- OLD plots (rough work)/     Question 2 rough-work plots
`-- roughWork/                  Planning sketches and development evidence
```

## Suggested Reading Order

1. Read [`comparative_analysis.md`](comparative_analysis.md) alongside the
   Question 1 source files.
2. Run the comparison and stopover examples to reproduce the reported search
   results.
3. Read [`optimization_analysis.md`](optimization_analysis.md) alongside
   `simulatedAnnealing.py`.
4. Run the optimization program to reproduce the final plots and seeded
   results.

The committed charts, GIFs, and reports allow the results to be inspected
without rerunning the programs, while the commands above make every final
experiment reproducible.
