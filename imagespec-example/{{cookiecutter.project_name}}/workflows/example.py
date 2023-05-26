"""
Building Docker Images without a Dockerfile
-------------------------------------------

.. tags:: Containerization, Intermediate

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

import pandas as pd

from flytekit import task, workflow, ImageSpec, Resources

pandas_image_spec = ImageSpec(
    base_image="ghcr.io/flyteorg/flytekit:py3.8-1.6.0",
    registry="docker",
    packages=["pandas", "numpy"],
    python_version="3.9",
    apt_packages=["git"],
    env={"Debug": "True"},
)

sklearn_image_spec = ImageSpec(
    base_image="ghcr.io/flyteorg/flytekit:py3.8-1.6.0",
    registry="docker",
    packages=["tensorflow"],
)

# ``is_container`` is used to determine whether the task is utilizing the image constructed from the ``ImageSpec``.
# If the task is indeed using the image built from the ``ImageSpec``, it will then import Tensorflow.
# This approach helps minimize module loading time and prevents unnecessary dependency installation within a single image.
if sklearn_image_spec.is_container():
    from sklearn.linear_model import LogisticRegression


# To enable tasks to utilize the images built with ``ImageSpec``, you can specify the ``container_image`` parameter
# for those tasks.
# @task(container_image=pandas_image_spec)
@task
def get_pandas_dataframe() -> (pd.DataFrame, pd.Series):
    df = pd.read_csv("https://storage.googleapis.com/download.tensorflow.org/data/heart.csv")
    print(df.head())
    return df[['age', 'thalach', 'trestbps', 'chol', 'oldpeak']], df.pop('target')


@task(container_image=sklearn_image_spec, requests=Resources(cpu="1", mem="1Gi"))
# @task
def get_model(max_iter: int, multi_class: str) -> LogisticRegression:
    return LogisticRegression(max_iter=max_iter, multi_class=multi_class)


# Get a basic model to train.
@task(container_image=sklearn_image_spec, requests=Resources(cpu="1", mem="1Gi"))
# @task
def train_model(model: LogisticRegression, feature: pd.DataFrame, target: pd.Series) -> LogisticRegression:
    model.fit(feature, target)
    return model
#
#
# # Lastly, let's define a workflow to capture the dependencies between the tasks.
@workflow()
def imagespec_workflow() -> LogisticRegression:
    feature, target = get_pandas_dataframe()
    model = get_model(max_iter=3000, multi_class="auto")
    return train_model(model=model, feature=feature, target=target)
