"""A basic Flyte project template that uses ImageSpec"""

import typing
from flytekit import task, workflow


"""
ImageSpec is a way to specify a container image configuration without a
Dockerfile. To use ImageSpec:
1. Add ImageSpec to the flytekit import line.
2. Uncomment the ImageSpec definition below and modify as needed.
3. If needed, create additional image definitions.
4. Set the container_image parameter on tasks that need a specific image, e.g.
`@task(container_image=basic_image)`. If no container_image is specified,
flytekit will use the default Docker image at
https://github.com/flyteorg/flytekit/pkgs/container/flytekit.

For more information, see the
`ImageSpec documentation <https://docs.flyte.org/projects/cookbook/en/latest/auto_examples/customizing_dependencies/image_spec.html#image-spec-example>`__.
"""

# image_definition = ImageSpec(
#    name="flytekit",  # default docker image name.
#    base_image="ghcr.io/flyteorg/flytekit:py3.11-1.10.2",  # the base image that flytekit will use to build your image.
#    packages=["pandas"],  # python packages to install.
#    registry="ghcr.io/unionai-oss", # the registry your image will be pushed to.
#    python_version="3.11"  # Optional if python is installed in the base image.
# )


@task()
def say_hello(name: str) -> str:
    """A simple Flyte task to say "Hello".

    The @task decorator allows Flyte to use this function as a Flyte task,
    which is executed as an isolated, containerized unit of compute.
    """
    return f"Hello, {name}!"


@task()
def greeting_length(greeting: str) -> int:
    """A task the counts the length of a greeting."""
    return len(greeting)


@workflow
def wf(name: str = "world") -> typing.Tuple[str, int]:
    """Declare workflow called `wf`.

    The @workflow decorator defines an execution graph that is composed of
    tasks and potentially sub-workflows. In this simple example, the workflow
    is composed of just one task.

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
    # Execute the workflow by invoking it like a function and passing in
    # the necessary parameters
    print(f"Running wf() {wf(name='passengers')}")
