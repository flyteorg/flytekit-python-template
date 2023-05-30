from typing import Dict, List

from flytekit import task, workflow, dynamic, ImageSpec
from bayes_opt import BayesianOptimization, UtilityFunction

"""
Image Spec is a way to specify how to build a container image without a Dockerfile. The image spec by default will be
converted to an `Envd <https://envd.tensorchord.ai/>`__ config, and the `Envd builder
<https://github.com/flyteorg/flytekit/blob/master/plugins/flytekit-envd/flytekitplugins/envd
/image_builder.py#L12-L34>`__ will build the image for you. However, you can also register your own builder to build
the image using other tools.
For every :py:class:`flytekit.PythonFunctionTask` task or a task decorated with the ``@task`` decorator,
you can specify rules for binding container images. By default, flytekit binds a single container image, i.e.,
the `default Docker image <https://ghcr.io/flyteorg/flytekit>`__, to all tasks. To modify this behavior,
use the ``container_image`` parameter available in the :py:func:`flytekit.task` decorator, and pass an
``ImageSpec``.
Before building the image, Flytekit checks the container registry first to see if the image already exists. By doing
so, it avoids having to rebuild the image over and over again. If the image does not exist, flytekit will build the
image before registering the workflow, and replace the image name in the task template with the newly built image name.
"""
image_definition = ImageSpec(
    name="flytekit",  # rename this to your docker image name
    base_image="ghcr.io/flyteorg/flytekit:py3.10-1.6.0",  # this is the base image that flytekit will use to build your image
    registry="ghcr.io/unionai-oss",  # this is the registry where your image will be pushed to
    packages=["flytekit>=1.6.0", "bayesian-optimization==1.4.3"],  # these are the packages that will be installed in your image
    python_version="3.10",  # this is the python version that will be used to build your image
)

Point = Dict[str, float]


@task(container_image=image_definition)
def black_box_function(point: Point) -> float:
    # implement your function to optimize here!
    x, y = point["x"], point["y"]
    return -x ** 2 - (y - 1) ** 2 + 1


@task(container_image=image_definition)
def suggest_points(
        optimizer: BayesianOptimization,
        utility: UtilityFunction,
        concurrency: int,
) -> List[Point]:
    points = set()
    # make sure that points are unique
    while len(points) < concurrency:
        points.add(tuple([(k, float(v)) for k, v in optimizer.suggest(utility).items()]))
    return [dict(x) for x in points]


@task(container_image=image_definition)
def register_targets(
        optimizer: BayesianOptimization,
        points: List[Point],
        targets: List[float],
) -> BayesianOptimization:
    for point, target in zip(points, targets):
        optimizer.register(params=point, target=target)
    return optimizer


@task(container_image=image_definition)
def log_iteration(
        optimizer: BayesianOptimization,
        points: List[Point],
        targets: List[float],
):
    print(f"{points=}\n{targets=}\n{optimizer.max=}\n")


@task(container_image=image_definition)
def return_max(optimizer: BayesianOptimization) -> Dict:
    return optimizer.max


@dynamic(container_image=image_definition)
def concurrent_trials(points: List[Point]) -> List[float]:
    return [black_box_function(point=point) for point in points]


@dynamic(container_image=image_definition)
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
