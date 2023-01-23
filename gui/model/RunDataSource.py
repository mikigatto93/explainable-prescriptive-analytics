import os

import numpy as np
import pandas as pd
import pm4py

from pm4py.objects.conversion.log import converter as log_converter

from gui.model import DiskDict
from gui.model.DataSource import DataSource


class RunDataSource(DataSource):
    def __init__(self, path, read_data=True):
        super().__init__(path, read_data)
        if read_data:
            self.columns_list = list(self.data.columns)

    def read_data(self, path):
        dataframe = None
        filename, file_extension = os.path.splitext(path)
        try:
            if file_extension == '.csv':
                dataframe = pd.read_csv(path)
            elif file_extension == '.xes':
                # pm4py.convert_to_dataframe(pm4py.read_xes(io.BytesIO(decoded))).to_csv(path_or_buf=(filename[:-4] +
                # '.csv'),index=None)
                log = pm4py.read_xes(path)
                dataframe = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)
            elif file_extension == '.xls':
                dataframe = pd.read_excel(path)
        except Exception as e:
            print(e)
            raise e
        return dataframe

    def convert_datetime_to_seconds(self, start_time_col, date_format='%Y-%m-%d %H:%M:%S'):
        if not np.issubdtype(self.data[start_time_col], np.number):
            self.data[start_time_col] = pd.to_datetime(self.data[start_time_col], format=date_format)
            self.data[start_time_col] = self.data[start_time_col].view(np.int64) / int(1e9)

    def remove_unnamed_columns(self):
        for i in self.columns_list:
            if 'Unnamed' in i:
                del self.data[i]

    def to_dict(self, key, save_df_data=True):
        if save_df_data:
            self.data.to_csv(DiskDict.get_df_path('run_df', key))
        return {
            'file_path': self.file_path,
            'is_xes': self.is_xes,
            'xes_columns_names': self.xes_columns_names,
            'columns_list': self.columns_list,
            'data': DiskDict.get_df_path('run_df', key)
        }

    def free_df(self, key):
        path = DiskDict.get_df_path('run_df', key)
        try:
            os.remove(path)
        except OSError:
            print('An error occurred during df file deletion: ({})'.format(path))



def build_RunDataSource_from_dict(dict_obj, load_df=False):
    obj = RunDataSource(dict_obj['file_path'], False)

    obj.is_xes = dict_obj['is_xes']
    obj.xes_columns_names = dict_obj['xes_columns_names']
    obj.columns_list = dict_obj['columns_list']
    if load_df:
        obj.data = pd.read_csv(dict_obj['data'])
    return obj
