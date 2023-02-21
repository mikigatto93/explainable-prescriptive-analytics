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
    resource: Optional[str]
    act_to_opt: Optional[str]
    out_thrs: float
    creation_timestamp: str
    pred_column: str = ''

    def __post_init__(self):
        if self.kpi == 'Total time':
            self.pred_column = 'remaining_time'
            self.act_to_opt = None
        elif self.kpi == 'Minimize activity occurrence':
            self.pred_column = 'independent_activity'

    @staticmethod
    def validate_forbidden_ex_names(ex_name):
        # < (less than)
        # > (greater than)
        # : (colon - sometimes works, but is actually NTFS Alternate Data Streams)
        # " (double quote)
        # / (forward slash)
        # \ (backslash)
        # | (vertical bar or pipe)
        # ? (question mark)
        # * (asterisk)
        # \n (not necessary, remove it for convenience)

        forbidden_chars = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*", "\n"]
        flag = True
        for i, _ in enumerate(forbidden_chars):
            flag = flag and (forbidden_chars[i] not in ex_name)
        return flag

    def to_dict(self):
        return {
            'ex_name': self.ex_name,
            'kpi': self.kpi,
            'id': self.id,
            'timestamp': self.timestamp,
            'activity': self.activity,
            'resource': self.resource,
            'act_to_opt': self.act_to_opt,
            'out_thrs': self.out_thrs,
            'creation_timestamp': str(self.creation_timestamp),
            'pred_column': self.pred_column,
        }


@dataclass
class TrainInfo:
    model_type: str
    mean_events: Optional[np.array]
    column_type: str
    df_completed_cases: pd.DataFrame
    history: list[str]
    target_column: pd.DataFrame
    target_column_name: str
    pred_attributes: typing.Any
    event_level: int

#     def to_dict(self, key):
#         self.df_completed_cases.to_csv(DiskDict.get_df_path('df_completed_cases', key))
#         self.target_column.to_csv(DiskDict.get_df_path('target_column', key))
#         return {
#             'model_type': self.model_type,
#             'mean_events': self.mean_events,
#             'column_type': self.column_type,
#             'df_completed_cases': DiskDict.get_df_path('df_completed_cases', key),
#             'history': self.history,
#             'target_column': DiskDict.get_df_path('target_column', key),
#             'target_column_name': self.target_column_name,
#             'pred_attributes': self.pred_attributes,
#             'event_level': self.event_level,
#         }
#
#
# def build_TrainInfo_from_dict(dict_obj):
#     return TrainInfo(
#         model_type=dict_obj['model_type'],
#         mean_events=dict_obj['mean_events'],
#         column_type=dict_obj['event_level'],
#         df_completed_cases=pd.read_csv(dict_obj['df_completed_cases']),
#         history=dict_obj['history'],
#         target_column=pd.read_csv(dict_obj['target_column']),
#         target_column_name=dict_obj['target_column_name'],
#         pred_attributes=dict_obj['pred_attributes'],
#         event_level=dict_obj['event_level']
#     )


def build_experiment_from_dict(dict_obj: dict) -> Experiment:
    return Experiment(
        ex_name=dict_obj['ex_name'],
        kpi=dict_obj['kpi'],
        id=dict_obj['id'],
        timestamp=dict_obj['timestamp'],
        activity=dict_obj['activity'],
        resource=dict_obj['resource'],
        act_to_opt=dict_obj['act_to_opt'],
        out_thrs=dict_obj['out_thrs'],
        creation_timestamp=dict_obj['creation_timestamp'],
        pred_column=dict_obj['pred_column']
    )
