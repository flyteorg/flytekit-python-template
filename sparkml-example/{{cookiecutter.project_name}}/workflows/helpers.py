from typing import Any, Dict, List
import pandas as pd
from pyspark.ml.param import Param
from pyspark.ml.tuning import TrainValidationSplitModel


def extract_validation_metrics(
    tvs_model: TrainValidationSplitModel, paramGrid: List[Dict[Param, Any]]
) -> pd.DataFrame:
    """_summary_

    Args:
        tvs_model (TrainValidationSplitModel): _description_
        paramGrid (List[Dict[Param, Any]]): _description_

    Returns:
        pd.DataFrame: _description_
    """
    # Extract evaluation metrics and corresponding parameters
    metrics = tvs_model.validationMetrics
    params = tvs_model.getEstimatorParamMaps()

    param_names = [p.name for p in paramGrid[0]]
    param_values = [[param_dict[p] for p in paramGrid[0]] for param_dict in params]

    results_df = pd.DataFrame(param_values, columns=param_names)
    results_df["metric"] = metrics

    return results_df
