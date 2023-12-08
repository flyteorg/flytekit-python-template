import pandas as pd

from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from flytekit import task, workflow

@task
def get_data() -> pd.DataFrame:
    """Get the digts dataset."""
    return load_digits(as_frame=True).frame

@task
def process_data(data: pd.DataFrame) -> pd.DataFrame:
    # TODO update for digits dataset
    pass

@task
def train_model(data: pd.DataFrame) -> LogisticRegression:
    """Train a model on the digits dataset."""
    # TODO update for digits dataset
    return LogisticRegression()

@workflow
def training_workflow() -> LogisticRegression:
    """Put all of the tasks together into a single workflow."""
    data = get_data()
    processed_data = process_data(data=data)
    # TODO update for digits dataset
    return train_model()

if __name__ == "__main__":
    # TODO pdate for digits dataset
    training_workflow()

