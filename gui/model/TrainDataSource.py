import os

import numpy as np
import pandas as pd
import pm4py
from pandas.errors import ParserError
from pm4py.objects.conversion.log import converter as log_converter

from gui.model.DataSource import DataSource


class TrainDataSource(DataSource):
    XES_RELEVANT_COLS_NAMES = {'id': 'case:concept:name', 'timestamp': 'time:timestamp',
                               'activity': 'concept:name', 'resource': 'org:resource'}

    def __init__(self, path):
        super().__init__(path)
        self.columns_list = list(self.data.columns)

    def read_data(self, path):
        dataframe = None
        filename, file_extension = os.path.splitext(path)
        try:
            if file_extension == '.csv':
                dataframe = pd.read_csv(path)
                self.is_xes = False

            elif file_extension == '.xes':
                log = pm4py.read_xes(path)
                dataframe = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)

                self.is_xes = True
                for k, v in TrainDataSource.XES_RELEVANT_COLS_NAMES.items():
                    if v in dataframe.columns:
                        self.xes_columns_names[k] = v
                    else:
                        self.xes_columns_names[k] = None

            elif file_extension == '.xls':
                dataframe = pd.read_excel(path)
                self.is_xes = False
        except Exception as e:
            print(e)
            raise e
        return dataframe

    def convert_datetime_to_seconds(self, start_time_col, date_format='%Y-%m-%d %H:%M:%S'):
        if not np.issubdtype(self.data[start_time_col], np.number):
            try:
                self.data[start_time_col] = pd.to_datetime(self.data[start_time_col], format=date_format, utc=True)
                self.data[start_time_col] = self.data[start_time_col].view(np.int64) / int(1e9)
            except ParserError as pe:
                raise pe
            except ValueError as ve:
                raise ve

    def get_activity_list(self, act_name):
        return list(self.data[act_name].unique())
