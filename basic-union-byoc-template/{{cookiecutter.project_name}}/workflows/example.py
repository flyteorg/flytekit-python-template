from unionai import task, workflow, ImageSpec

image_spec = ImageSpec(
    name="basic-union-byoc-image",
    base_image="ghcr.io/flyteorg/flytekit:py3.11-latest",
    requirements="requirements.txt",
    registry="ghcr.io/<my-github-org>"
)

@task(container_image=image_spec)
def say_hello(name: str) -> str:
    return f"Hello, {name}!"


@workflow
def wf(name: str = "world") -> str:
    greeting = say_hello(name=name)
    return greeting
