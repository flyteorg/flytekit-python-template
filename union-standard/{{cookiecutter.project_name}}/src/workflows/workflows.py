"""Workflows"""

import union

@union.workflow
def wf_1(name: str = "world") -> str:
    greeting = say_hello(name=name)
    return greeting
