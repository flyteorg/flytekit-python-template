"""Tasks"""

import union

image_spec = union.ImageSpec(

    # Build the image using Union's built-in cloud builder (not locally on your machine)
    builder="union",

    # The name of the image.
    name="union-standard-image",

    # List of packages to install on the image
    packages=-["union"],
)

@union.task(container_image=image_spec)
def task_1(name: str) -> str:
    return f"Hello, {name}!"
