"""Hello World"""

import flytekit as fl

image_spec = fl.ImageSpec(

    # The name of the image. This image will be used byt he say_hello task
    name="say-hello-image",

    # Lock file with dependencies to install in image
    requirements="uv.lock",
)

@fl.task(container_image=image_spec)
def say_hello(name: str) -> str:
    return f"Hello, {name}!"

@fl.workflow
def hello_world_wf(name: str = "world") -> str:
    greeting = say_hello(name=name)
    return greeting