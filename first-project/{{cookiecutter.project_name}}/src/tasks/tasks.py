"""Tasks"""

import union

image_spec = union.ImageSpec(
    name="standard-union-template-image",
    requirements="uv.lock",
)

@union.task(container_image=image_spec)
def task_1(name: str) -> str:
    return f"Hello, {name}!"
