from typing import Any, Dict, List
import pandas as pd
from pyspark.ml.param import Param
from pyspark.ml.tuning import TrainValidationSplitModel


def extract_validation_metrics(
    tvs_model: TrainValidationSplitModel, paramGrid: List[Dict[Param, Any]]
) -> pd.DataFrame:
    """Extracts validation metrics from a pyspark train-validation
    grid search model.

    Args:
        tvs_model (TrainValidationSplitModel): a grid search model
        paramGrid (List[Dict[Param, Any]]): a parameter grid

    Returns:
        pd.DataFrame: a dataframe of validation metrics and corresponding parameters
    """
    # Extract evaluation metrics and corresponding parameters
    metrics = tvs_model.validationMetrics
    params = tvs_model.getEstimatorParamMaps()

    param_names = [p.name for p in paramGrid[0]]
    param_values = [[param_dict[p] for p in paramGrid[0]] for param_dict in params]

    results_df = pd.DataFrame(param_values, columns=param_names)
    results_df["metric"] = metrics

    return results_df
