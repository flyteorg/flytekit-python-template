# Hello World

import flytekit as fl
from tasks.say_hello import say_hello


@fl.workflow
def hello_world_wf(name: str = "world") -> str:
    greeting = say_hello(name=name)
    return greeting
