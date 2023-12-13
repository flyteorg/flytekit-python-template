"""A basic Flyte example"""

from flytekit import task, workflow


@task
def say_hello(name: str) -> str:
    return f"Hello, {name}!"


@workflow
def hello_world_wf(name: str = 'world') -> str:
    res = say_hello(name=name)
    return res


if __name__ == "__main__":
    # Execute the workflow by invoking it like a function and passing in
    # the necessary parameters
    print(f"Running wf() {hello_world_wf(name='passengers')}")
