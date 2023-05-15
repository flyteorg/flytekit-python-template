from dataclasses import asdict, dataclass, field
from typing import Dict, List, NamedTuple, Optional

import pandas as pd
from dataclasses_json import dataclass_json
from flytekit import StructuredDataset
from pyspark.ml.pipeline import PipelineModel
from pyspark.ml.tuning import ParamGridBuilder


@dataclass_json
@dataclass
class Dataset:
    data: StructuredDataset
    features: List[str]
    target: str


@dataclass_json
@dataclass
class ParamGrid:
    n_estimators: Optional[List[int]] = field(default_factory=list)
    max_depth: Optional[List[int]] = field(default_factory=list)
    learning_rate: Optional[List[float]] = field(default_factory=list)
    tree_method: Optional[List[str]] = field(default_factory=list)
    gamma: Optional[List[float]] = field(default_factory=list)
    min_child_weight: Optional[List[float]] = field(default_factory=list)
    subsample: Optional[List[float]] = field(default_factory=list)
    colsample_bytree: Optional[List[float]] = field(default_factory=list)
    reg_alpha: Optional[List[float]] = field(default_factory=list)
    reg_lambda: Optional[List[float]] = field(default_factory=list)

    def build_params_grid(self, model):
        param_grid_builder = ParamGridBuilder()
        for param, values in asdict(self).items():
            if values:
                param_grid_builder.addGrid(getattr(model, param), values)

        return param_grid_builder.build()


class TrainXGBoostSparkOutput(NamedTuple):
    best_pipeline: PipelineModel
    results_df: pd.DataFrame
    feature_importance: Dict[str, float]
