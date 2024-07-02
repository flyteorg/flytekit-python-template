from unionai import task, workflow, ImageSpec

image_spec = ImageSpec(
    name="basic-union-serverless-image",
    base_image="ghcr.io/flyteorg/flytekit:py3.11-latest",
    requirements="requirements.txt"
)

@task(container_image=image_spec)
def say_hello(name: str) -> str:
    return f"Hello, {name}!"


@workflow
def wf(name: str = "world") -> str:
    greeting = say_hello(name=name)
    return greeting
