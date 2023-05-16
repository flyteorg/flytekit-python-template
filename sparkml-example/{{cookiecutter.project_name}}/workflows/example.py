import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import flytekit
import pandas as pd
import sklearn.datasets
from flytekit import StructuredDataset, kwtypes, task, workflow
from flytekitplugins.deck.renderer import MarkdownRenderer
from flytekitplugins.papermill import NotebookTask
from flytekitplugins.spark import Spark
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.param import Param
from pyspark.ml.pipeline import Pipeline, PipelineModel
from pyspark.ml.tuning import TrainValidationSplit
from pyspark.sql import DataFrame
from sklearn.model_selection import train_test_split
from xgboost.spark import SparkXGBRegressor

from .charts import plot_subgroup_performance
from .types import Dataset, ParamGrid, TrainXGBoostSparkOutput
from .helpers import extract_validation_metrics

SPARK_CONFIG = {
    "spark.driver.memory": "4g",
    "spark.executor.memory": "2g",
    "spark.executor.instances": "3",
    "spark.driver.cores": "3",
    "spark.executor.cores": "1",
    "spark.eventLog.enabled": "false",
}

DEFAULT_PARAM_GRID = ParamGrid(
    max_depth=[3, 6], n_estimators=[30, 75, 150], learning_rate=[0.2, 0.5]
)


@task(cache=True, cache_version="v3")
def load_data() -> Tuple[Dataset, Dataset]:
    """Loads the California housing dataset and splits it into train and test sets.

    Returns:
        Tuple[Dataset, Dataset]: _description_
    """
    dataset = sklearn.datasets.fetch_california_housing(
        as_frame=True, download_if_missing=True
    )
    features_names = dataset["feature_names"]

    df = dataset["data"]
    df = df[features_names]
    df["target"] = dataset["target"]

    train_df, test_df = train_test_split(df, test_size=0.01)
    return (
        Dataset(
            data=StructuredDataset(dataframe=train_df),
            features=features_names,
            target="target",
        ),
        Dataset(
            data=StructuredDataset(dataframe=test_df),
            features=features_names,
            target="target",
        ),
    )


@task(
    task_config=Spark(spark_conf=SPARK_CONFIG),
    disable_deck=False,
    cache=True,
    cache_version="v1",
)
def xgboost_gridsearch_spark(
    dataset: Dataset, param_grid: ParamGrid
) -> TrainXGBoostSparkOutput:
    """
    Performs a grid search over the XGBoost hyperparameters using Spark
    to distribute the training across multiple nodes.

    Args:
        dataset (Dataset): A dataclass containing the training dataset
        param_grid (ParamGrid): A grid of xgboost parameters to search over

    Returns:
        TrainXGBoostSparkOutput: A dataclass containing the best model, validation results, and feature importance
    """
    df = dataset.data.open(DataFrame).all()

    va = VectorAssembler(inputCols=dataset.features, outputCol="features")
    model = SparkXGBRegressor(features_col="features", label_col="target")

    param_grid = param_grid.build_params_grid(model)

    # combine the above two steps into a single pipeline
    pipeline = Pipeline(stages=[va, model])

    tvs = TrainValidationSplit(
        estimator=pipeline,
        estimatorParamMaps=param_grid,
        evaluator=RegressionEvaluator(labelCol="target"),
        trainRatio=0.8,
    )

    # fit tvs and get the metrics
    tvs_model = tvs.fit(df)

    # Training Outputs
    best_pipeline = tvs_model.bestModel
    results_df = extract_validation_metrics(tvs_model, param_grid)
    feature_importance = dict(
        zip(
            dataset.features,
            best_pipeline.stages[-1].get_feature_importances().values(),
        )
    )

    return TrainXGBoostSparkOutput(
        best_pipeline=best_pipeline,
        results_df=results_df,
        feature_importance=feature_importance,
    )


@task(
    task_config=Spark(spark_conf=SPARK_CONFIG),
    disable_deck=False,
    cache=True,
    cache_version="v2",
)
def score_test_dataset(model: PipelineModel, test_ds: Dataset) -> StructuredDataset:
    """Score the test dataset using a trained spark xgboost model

    Args:
        model (PipelineModel): A trained xgboost model
        test_ds (Dataset): A dataclass containing the test dataset

    Returns:
        StructuredDataset: the test dataset with predictions added
    """
    test_df = test_ds.data.open(DataFrame).all()
    scores_df = model.transform(test_df).drop("features")
    return StructuredDataset(dataframe=scores_df)


@task(disable_deck=False)
def training_report(
    results_df: pd.DataFrame,
    scores_df: pd.DataFrame,
    feature_importance: Dict[str, float],
):
    """Generate a report of the training results using FlyteDecks

    Args:
        results_df (pd.DataFrame): the grid search results
        scores_df (pd.DataFrame): the test dataset with predictions added
        feature_importance (Dict[str, float]): a dictionary of feature importances from the best model
    """
    flytekit.Deck(
        "Grid Search", results_df.sort_values(by="metric", ascending=True).to_html()
    )

    fe_df = pd.DataFrame(feature_importance, index=[0]).T.sort_values(
        by=0, ascending=False
    )
    flytekit.Deck("Feature Importance", fe_df.to_html())
    flytekit.Deck("Subgroup Performance", plot_subgroup_performance(scores_df))

    mse = ((scores_df["target"] - scores_df["prediction"]) ** 2).mean()
    flytekit.Deck("MSE", MarkdownRenderer().to_html(f"# MSE\n{mse}"))


notebook_training_report = NotebookTask(
    name="notebook_training_report",
    notebook_path=os.path.join(Path(__file__).parent.absolute(), "notebook.ipynb"),
    render_deck=True,
    disable_deck=False,
    inputs=kwtypes(sd=StructuredDataset),
)


@workflow
def wf(param_grid: ParamGrid = DEFAULT_PARAM_GRID):
    """Performs a grid search of an xgboost model on the California housing dataset
        from sklearn.datasets. Displays the results in both a FlyteDeck and Papermill
        notebook.

    Args:
        param_grid (ParamGrid, optional): _description_. Defaults to DEFAULT_PARAM_GRID.
    """
    train_ds, test_ds = load_data()
    train_outputs = xgboost_gridsearch_spark(dataset=train_ds, param_grid=param_grid)
    scores_df = score_test_dataset(model=train_outputs.best_pipeline, test_ds=test_ds)

    training_report(
        results_df=train_outputs.results_df,
        scores_df=scores_df,
        feature_importance=train_outputs.feature_importance,
    )

    notebook_training_report(sd=train_outputs.results_df)
