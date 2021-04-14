from flytekit import task, workflow


@task
def greet(first_name: str, last_name: str) -> str:
    return f"Hello, {first_name} {last_name}"


@workflow
def hello_world(first_name: str = "world", last_name: str = "earth") -> str:
    greeting = greet(first_name=first_name, last_name=last_name)
    return greeting
