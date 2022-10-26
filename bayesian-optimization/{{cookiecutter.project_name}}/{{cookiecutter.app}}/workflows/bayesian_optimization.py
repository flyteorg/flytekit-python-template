from typing import Dict, List

from flytekit import task, workflow, dynamic
from bayes_opt import BayesianOptimization, UtilityFunction


Point = Dict[str, float]


@task
def black_box_function(point: Point) -> float:
    # implement your function to optimize here!
    x, y = point["x"], point["y"]
    return -x ** 2 - (y - 1) ** 2 + 1

@task
def suggest_points(
    optimizer: BayesianOptimization,
    utility: UtilityFunction,
    concurrency: int,
) -> List[Point]:
    points = set()
    # make sure that points are unique
    while len(points) < concurrency:
        points.add({k: float(v) for k, v in optimizer.suggest(utility).items()})
    return points

@task
def register_targets(
    optimizer: BayesianOptimization,
    points: List[Point],
    targets: List[float],
) -> BayesianOptimization:
    for point, target in zip(points, targets):
        optimizer.register(params=point, target=target)
    return optimizer

@task
def log_iteration(
    optimizer: BayesianOptimization,
    points: List[Point],
    targets: List[float],
):
    print(f"{points=}\n{targets=}\n{optimizer.max=}\n")

@task
def return_max(optimizer: BayesianOptimization) -> Dict:
    return optimizer.max

@dynamic
def concurrent_trials(points: List[Point]) -> List[float]:
    return [black_box_function(point=point) for point in points]

@dynamic
def bayesopt(n_iter: int, concurrency: int) -> Dict:
    optimizer = BayesianOptimization(
        f=None,
        pbounds={"x": (-2, 2), "y": (-3, 3)},
        verbose=2,
        random_state=1,
    )
    utility = UtilityFunction(kind="ucb", kappa=2.5, xi=0.0)
    for _ in range(n_iter):
        points = suggest_points(optimizer=optimizer, utility=utility, concurrency=concurrency)
        targets = concurrent_trials(points=points)
        optimizer = register_targets(optimizer=optimizer, points=points, targets=targets)
        log_iteration(optimizer=optimizer, points=points, targets=targets)
    # return point that maximized the target
    return return_max(optimizer=optimizer)

@workflow
def wf(n_iter: int = 10, concurrency: int = 10) -> Dict:
    return bayesopt(n_iter=n_iter, concurrency=concurrency)


if __name__ == "__main__":
    print(wf())
