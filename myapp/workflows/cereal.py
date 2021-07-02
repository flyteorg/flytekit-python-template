import csv
import requests
from typing import List, Dict, Any
from flytekit import conditional, task, workflow, dynamic

""" Sample workflow to test out Flyte functionality
    such as conditionals and @dynamic
"""


@task
def load_cereal(filepath: str) -> List[Dict[str, str]]:
    if not filepath:
        print("No cereal filepath found")
        return []

    response = requests.get(filepath)
    lines = response.text.split("\n")
    cereals = [row for row in csv.DictReader(lines)]

    # Unsure what the logging best practices are for flyte
    print(f"Found {len(cereals)} cereals")

    return cereals


@task
def is_list_empty(lst: List[Dict[str, str]]) -> bool:
    if lst:
        return False
    else:
        return True


@task
def name_length(cereal: Dict[str, str]) -> int:
    return len(cereal["Cereal Name"])


@task
def average(lst: List[int]) -> float:
    avg = sum(lst) / len(lst)
    print(f"Average cereal name length is {avg} characters")
    return avg


@dynamic
def cereal_name_avg(cereals: List[Dict[str, str]]) -> float:
    lengths = []
    for cereal in cereals:
        lengths.append(name_length(cereal=cereal))

    avg_name_length = average(lst=lengths)

    return avg_name_length


@workflow
def mycereal(cereal_path: str) -> float:
    ''' Cereal workflow reads CSV and determines average cereal name length
    '''
    cereals = load_cereal(filepath=cereal_path)
    empty = is_list_empty(lst=cereals)

    avg_length = (
        conditional("is_lst_empty")
        .if_(empty.is_false())
        .then(cereal_name_avg(cereals=cereals))
        .else_()
        .fail("Must specify cereals")
    )
    # avg_length = cereal_name_avg(cereals=cereals)
    return avg_length


if __name__ == "__main__":

    path = "https://gist.githubusercontent.com/lisawilliams/a91ffcea96ac3af9500bbf6b92f1408e/raw/728e9b2e4fb0da2baa34e2da2a9d732d74b484ab/cereal.csv"
    res = mycereal(cereal_path=path)
    print(f"Running mycereal(cereal_path={path}) = {res}")
