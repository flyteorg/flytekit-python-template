import pandas as pd
from sklearn.datasets import load_wine
from sklearn.linear_model import LogisticRegression

from flytekit import task, workflow
from flytekit.types.pickle import FlytePickle


@task
def get_data() -> pd.DataFrame:
    return load_wine(as_frame=True).frame


@task
def process_data(data: pd.DataFrame) -> pd.DataFrame:
    return data.assign(target=lambda x: x["target"].where(x["target"] == 0, 1))


@task
def train_model(data: pd.DataFrame) -> FlytePickle:
    features = data.drop("target", axis="columns")
    target = data["target"]
    return LogisticRegression().fit(features, target)


@workflow
def training_workflow() -> FlytePickle:
    data = get_data()
    processed_data = process_data(data=data)
    return train_model(data=processed_data)


if __name__ == "__main__":
    print(f"Running training_workflow() {training_workflow()}")
