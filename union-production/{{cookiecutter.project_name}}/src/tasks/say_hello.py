"""Say Hello"""

import union

image_spec = union.ImageSpec(

    # Build the image using Union's built-in cloud builder (not locally on your machine)
    builder="union",

    # The name of the image. This image will be used by the say_hello task
    name="say-hello-image",

    # List of packages to install on the image
    packages=["union"],
)

@union.task(container_image=image_spec)
def say_hello(name: str) -> str:
    return f"Hello, {name}!"
