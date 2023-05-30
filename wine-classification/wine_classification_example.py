import pandas as pd

from sklearn.datasets import load_wine
from sklearn.linear_model import LogisticRegression
from flytekit import task, workflow, ImageSpec

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
    image_name="flytekit",  # rename this to your docker image name
    base_image="ghcr.io/flyteorg/flytekit:py3.10-1.6.0",
    # this is the base image that flytekit will use to build your image
    registry="ghcr.io/unionai-oss",  # this is the registry where your image will be pushed to
    packages=["flytekit>=1.6.0", "pandas==1.5.3", "scikit-learn==1.2.2"],  # these are the packages that will be installed in your image
    python_version="3.10",  # this is the python version that will be used to build your image
)

@task
def get_data() -> pd.DataFrame:
    """Get the wine dataset."""
    return load_wine(as_frame=True).frame

@task
def process_data(data: pd.DataFrame) -> pd.DataFrame:
    """Simplify the task from a 3-class to a binary classification problem."""
    return data.assign(target=lambda x: x["target"].where(x["target"] == 0, 1))

@task
def train_model(data: pd.DataFrame, hyperparameters: dict) -> LogisticRegression:
    """Train a model on the wine dataset."""
    features = data.drop("target", axis="columns")
    target = data["target"]
    return LogisticRegression(max_iter=3000, **hyperparameters).fit(features, target)

@workflow
def training_workflow(hyperparameters: dict = {"C": 0.1}) -> LogisticRegression:
    """Put all of the steps together into a single workflow."""
    data = get_data()
    processed_data = process_data(data=data)
    return train_model(
        data=processed_data,
        hyperparameters=hyperparameters,
    )

if __name__ == "__main__":
    training_workflow(hyperparameters={"C": 0.1})
