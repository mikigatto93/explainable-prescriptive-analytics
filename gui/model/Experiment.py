import typing
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class Experiment:
    ex_name: str
    kpi: str
    id: str
    timestamp: str
    activity: str
    resource: str
    act_to_opt: str
    out_thrs: float

@dataclass
class TrainInfo:
    model_type: str
    mean_events: Optional[np.array]
    column_type: str
    df_completed_cases: pd.DataFrame
    history: list[str]
    target_column: pd.DataFrame
    target_column_name: str
    pred_column: str
    pred_attributes: typing.Any
    event_level: int
