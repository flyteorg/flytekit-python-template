# Hello World

import flytekit as fl
import os

image_spec = fl.ImageSpec(
    # The name of the image. This image will be used by the `say_hello`` task.
    name="say-hello-image",

    # Lock file with dependencies to be installed in the image.
    requirements="uv.lock",

    # Image registry to to which this image will be pushed.
    # Set the Environment variable FLYTE_IMAGE_REGISTRY to the URL of your registry.
    # The image will be built on your local machine, so enure that your Docker is running.
    # Ensure that pushed image is accessible to your Flyte cluster, so that it can pull the image
    # when it spins up the task container.
    registry=os.environ['FLYTE_IMAGE_REGISTRY']
)


@fl.task(container_image=image_spec)
def say_hello(name: str) -> str:
    return f"Hello, {name}!"

@fl.workflow
def hello_world_wf(name: str = "world") -> str:
    greeting = say_hello(name=name)
    return greeting