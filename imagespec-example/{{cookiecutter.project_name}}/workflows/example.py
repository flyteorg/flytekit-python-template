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

import typing
from flytekit import task, workflow, ImageSpec


pandas_image_spec = ImageSpec(
    base_image="ghcr.io/flyteorg/flytekit:py3.8-1.6.0",
    packages=["pandas", "numpy"],
    python_version="3.9",
    apt_packages=["git"],
    env={"Debug": "True"},
)

sklearn_image_spec = ImageSpec(
    base_image="ghcr.io/flyteorg/flytekit:py3.8-1.6.0",
    packages=["tensorflow"],
)

@task
def say_hello(name: str) -> str:
    """A simple Flyte task to say "hello".

    The @task decorator allows Flyte to use this function as a Flyte task, which
    is executed as an isolated, containerized unit of compute.
    """
    return f"hello {name}!"


@task
def greeting_length(greeting: str) -> int:
    """A task the counts the length of a greeting."""
    return len(greeting)

@workflow
def wf(name: str = "union") -> typing.Tuple[str, int]:
    """Declare workflow called `wf`.

    The @workflow decorator defines an execution graph that is composed of tasks
    and potentially sub-workflows. In this simple example, the workflow is
    composed of just one task.

    There are a few important things to note about workflows:
    - Workflows are a domain-specific language (DSL) for creating execution
      graphs and therefore only support a subset of Python's behavior.
    - Tasks must be invoked with keyword arguments
    - The output variables of tasks are Promises, which are placeholders for
      values that are yet to be materialized, not the actual values.
    """
    greeting = say_hello(name=name)
    greeting_len = greeting_length(greeting=greeting)
    return greeting, greeting_len


if __name__ == "__main__":
    # Execute the workflow, simply by invoking it like a function and passing in
    # the necessary parameters
    print(f"Running wf() { wf(name='passengers') }")
