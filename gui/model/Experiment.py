from dataclasses import dataclass


@dataclass
class Experiment:
    ex_name: str
    kpi: str
    _id: str
    timestamp: str
    activity: str
    resource: str
    act_to_opt: str
    out_thrs: float


