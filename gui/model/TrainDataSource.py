import os
import traceback

import numpy as np
import pandas as pd
import pm4py
from pandas.errors import ParserError
from pm4py.objects.conversion.log import converter as log_converter

from gui.model import DiskDict
from gui.model.DataSource import DataSource


class TrainDataSource(DataSource):
    XES_RELEVANT_COLS_NAMES = {'id': 'case:concept:name', 'timestamp': 'time:timestamp',
                               'activity': 'concept:name', 'resource': 'org:resource'}

    def __init__(self, path, read_data=True):
        super().__init__(path, read_data)
        if read_data:
            self.columns_list = list(self.data.columns)

    def read_data(self, path, datetime=None):
        dataframe = None
        filename, file_extension = os.path.splitext(path)
        try:
            if file_extension == '.csv':
                dataframe = pd.read_csv(path)
                self.is_xes = False

                # import datetime
                # t1 = datetime.datetime.now()
                #
                # dataframe.to_parquet('test.prq')
                # t2 = datetime.datetime.now()
                #
                # t1 = datetime.datetime.now()
                #
                # dataframe.read_parquet('test.prq')
                # t2 = datetime.datetime.now()

            elif file_extension == '.xes':
                log = pm4py.read_xes(path)
                dataframe = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)

                self.is_xes = True
                for k, v in TrainDataSource.XES_RELEVANT_COLS_NAMES.items():
                    if v in dataframe.columns:
                        self.xes_columns_names[k] = v
                    else:
                        self.xes_columns_names[k] = None

                # start_time_col = 'time:timestamp'
                # self.data = dataframe
                # if not np.issubdtype(self.data[start_time_col], np.number):
                #     try:
                #         self.data[start_time_col] = pd.to_datetime(self.data[start_time_col],
                #                                                    format='%Y-%m-%d %H:%M:%S',
                #                                                    utc=True)
                #         self.data[start_time_col] = self.data[start_time_col].view(np.int64) / int(1e9)
                #     except ParserError as pe:
                #         raise pe
                #     except ValueError as ve:
                #         raise ve
                # import datetime

                # import datetime
                # t1 = datetime.datetime.now()
                # dataframe.to_csv('test_to_csv.csv')
                # t2 = datetime.datetime.now()
                # print('p w time: {}'.format(t2-t1))
                #
                # t3 = datetime.datetime.now()
                # pd.read_csv('test_to_csv.csv')
                # t4 = datetime.datetime.now()
                # print('pkl w time: {}'.format(t4 - t3))
                #
                # t1 = datetime.datetime.now()
                # dataframe.to_parquet('test1.prq')
                # t2 = datetime.datetime.now()
                # print('p r time: {}'.format(t2 - t1))
                #
                # t3 = datetime.datetime.now()
                #
                # t4 = datetime.datetime.now()
                # print('pkl r time: {}'.format(t4 - t3))

            elif file_extension == '.xls':
                dataframe = pd.read_excel(path)
                self.is_xes = False
        except Exception as e:
            print(traceback.format_exc())
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

    def to_dict(self, key, save_df_data=True):
        # self.file_path = path
        # self.is_xes = None
        # self.xes_columns_names = {}
        # self.data = self.read_data(self.file_path)
        if save_df_data:
            self.data.to_csv(DiskDict.get_df_path('train_df', key))
        return {
            'file_path': self.file_path,
            'is_xes': self.is_xes,
            'xes_columns_names': self.xes_columns_names,
            'columns_list': self.columns_list,
            'data': DiskDict.get_df_path('train_df', key)
        }

    def free_df(self, key):
        path = DiskDict.get_df_path('train_df', key)
        try:
            os.remove(path)
        except OSError:
            print('An error occurred during df file deletion: ({})'.format(path))


def build_TrainDataSource_from_dict(dict_obj, load_df=False):
    obj = TrainDataSource(dict_obj['file_path'], False)

    obj.is_xes = dict_obj['is_xes']
    obj.xes_columns_names = dict_obj['xes_columns_names']
    obj.columns_list = dict_obj['columns_list']
    if load_df:
        obj.data = pd.read_csv(dict_obj['data'])
    return obj

