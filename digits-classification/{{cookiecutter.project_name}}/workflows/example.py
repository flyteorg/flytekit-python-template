import pandas as pd

from sklearn.datasets import load_digits
from flytekit import task, workflow

@task
def get_data() -> pd.DataFrame:
    """Get the digts dataset."""
    return load_digits(as_frame=True).frame

@task
def process_data(data: pd.DataFrame) -> pd.DataFrame:
    # TODO
    pass

@workflow
def wf():
    # TODO
    pass

if __name__ == "__main__":
    wf()

