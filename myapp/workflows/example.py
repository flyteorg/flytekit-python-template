from flytekit import task, workflow


@task
def greet(name: str) -> str:
    return f"Hello, {name}"


@workflow
def hello_world(name: str = "world") -> str:
    edges = greet(name=name)
    return edges
