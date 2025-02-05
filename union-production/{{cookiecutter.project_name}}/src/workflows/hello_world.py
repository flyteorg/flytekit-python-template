"""Hello World"""

import union
from ..tasks.say_hello import say_hello

@union.workflow
def hello_world_wf(name: str = "world") -> str:
    greeting = say_hello(name=name)
    return greeting
