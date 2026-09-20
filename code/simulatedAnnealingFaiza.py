import random
import math
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import os
 

def boothFunc(x, y):
    # -10 <= x, y <= 10
    if -10 <= x <= 10 and -10 <= y <= 10:
        return (x + 2 * y - 7) ** 2 + (2 * x + y - 5) ** 2
    raise ValueError(f"f(x,y) undefined for (x, y): ({x}, {y})")
 
 
def himmelblauFunc(x, y):
    # -5 <= x, y <= 5
    if -5 <= x <= 5 and -5 <= y <= 5:
        return (x ** 2 + y - 11) ** 2 + (x + y ** 2 - 7) ** 2
    raise ValueError(f"f(x,y) undefined for (x, y): ({x}, {y})")
 
 
def griewankFunc(x, y):
    # -30 < x, y < 30
    if -30 < x < 30 and -30 < y < 30:
        return 1 + (x ** 2 + y ** 2) / 4000 - math.cos(x) * math.cos(y / math.sqrt(2))
    raise ValueError(f"f(x,y) undefined for (x, y): ({x}, {y})")
 

def simAnnealing(
        f, 
        bounds, 
        x0, y0,
        inclusiveBounds = 1, 
        neighbourhoodSize = 0.5,
        K = 100,
        temperature = 1,
        decTemp = 0.1,
        best = "min"
        
    ):

    (minX, minY), (maxX, maxY) = bounds
 
    if not inclusiveBounds:
        minX = math.nextafter(minX, math.inf)
        minY = math.nextafter(minY, math.inf)
        maxX = math.nextafter(maxX, -math.inf)
        maxY = math.nextafter(maxY, -math.inf)
 


    x, y = x0, y0
    fxy = f(x, y)

    xHist, yHist, fHist, THist = [x], [y], [fxy], [temperature]

    while temperature > 0:
        for _ in range(K):
            candX = x + random.uniform(-neighbourhoodSize, neighbourhoodSize)
            candY = y + random.uniform(-neighbourhoodSize, neighbourhoodSize)
            
            candX = min(max(candX, minX), maxX)
            candY = min(max(candY, minY), maxY)

            candF = f(candX, candY)

            delta = candF - fxy

            if best=="min":
                accept = delta < 0 or random.random() < math.exp(-delta / temperature)
            else:
                accept = delta > 0 or random.random() < math.exp(delta / temperature)

            if accept:
                x, y, fxy = candX, candY, candF

            xHist.append(x)
            yHist.append(y)
            fHist.append(fxy)
            THist.append(temperature)


        temperature -= decTemp

    label = "minimum" if best == "min" else "maximum"
    print(f"The global {label} is at ({x:.4f}, {y:.4f}) for f(x,y) = {fxy:.4f}")
 
    return x, y, fxy, (xHist, yHist, fHist, THist)



def plot_run(history, f, best, out_dir="."):
    xHist, yHist, fHist, _THist = history
    iterations = range(len(fHist))
 
    fig, axes = plt.subplots(3, 1, figsize=(8, 9), sharex=True)
 
    axes[0].plot(iterations, xHist)
    axes[0].set_ylabel("x")
    axes[0].set_title(f"{f} function \u2014 Simulated Annealing ({best})")
 
    axes[1].plot(iterations, yHist, color="darkorange")
    axes[1].set_ylabel("y")
 
    axes[2].plot(iterations, fHist, color="seagreen")
    axes[2].set_ylabel("f(x, y)")
    axes[2].set_xlabel("Iteration")
 
    fig.tight_layout()
    fname = f"{out_dir}/{f.lower()}_{best}.png"
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    return fname
 


# testing

random.seed(45)  

OUT_DIR = "output"
os.makedirs(OUT_DIR, exist_ok=True)


problems = [
    # name,        func,             bounds,                inclusive, best   decTemp  K
    ("Booth",      boothFunc,       ((-10, -10), (10, 10)), True,      "min", 0.1,    100),
    ("Himmelblau", himmelblauFunc,  ((-5, -5), (5, 5)),     True,      "min", 0.1,    100),
    ("Griewank",   griewankFunc,    ((-30, -30), (30, 30)), False,     "min", 0.01,   300),
    ("Booth",      boothFunc,       ((-10, -10), (10, 10)), True,      "max", 0.1,    100),
    ("Himmelblau", himmelblauFunc,  ((-5, -5), (5, 5)),     True,      "max", 0.1,    100),
    ("Griewank",   griewankFunc,    ((-30, -30), (30, 30)), False,     "max", 0.01,   100),

]

for name, func, bounds, inclusive, best, decTemp, K in problems:
    (minX, minY), (maxX, maxY) = bounds
    x0 = random.uniform(minX, maxX)
    y0 = random.uniform(minY, maxY)

    print(f"\n=== {name} function ===")
    print(f"Start point: ({x0:.3f}, {y0:.3f})")

    x_opt, y_opt, f_opt, history = simAnnealing(
        func, bounds, x0, y0,
        inclusiveBounds=inclusive,
        neighbourhoodSize=0.5,
        K=K,
        temperature=1.0,
        decTemp=decTemp,
        best=best,
    )

    fname = plot_run(history, name, best, OUT_DIR)
    print(f"Saved plot to {fname}")
