import os

import pandas as pd
import pm4py

import pytest

from gui.model.TrainDataSource import TrainDataSource, build_TrainDataSource_from_dict
from pm4py.objects.conversion.log import converter as log_converter


@pytest.fixture
def datasource():
    yield {'csv': TrainDataSource('test_datasets/bac_train_red.csv', read_data=True),
           'xls': TrainDataSource('test_datasets/VINST_train_red.xls', read_data=True),
           'xes': TrainDataSource('test_datasets/test_file_xes.xes', read_data=True)}


def test_read(datasource):
    ds = datasource['csv']
    assert not ds.is_xes
    assert ds.xes_columns_names == {}
    assert ds.columns_list == ['Unnamed: 0',
                               'REQUEST_ID',
                               'CLOSURE_TYPE',
                               'CLOSURE_REASON',
                               'ACTIVITY',
                               'END_DATE',
                               'START_DATE',
                               'CE_UO',
                               'ROLE']

    assert len(ds.data.index) == len(pd.read_csv('test_datasets/bac_train_red.csv').index)

    ds = datasource['xls']
    assert not ds.is_xes
    assert ds.xes_columns_names == {}
    assert ds.columns_list == ['Unnamed: 0',
                               'SR_Number',
                               'Change_Date+Time',
                               'Status',
                               'ACTIVITY',
                               'Involved_ST_Function_Div',
                               'Involved_Org_line_3',
                               'Involved_ST',
                               'SR_Latest_Impact',
                               'Product',
                               'Country',
                               'Owner_Country']
    assert len(ds.data.index) == len(pd.read_excel('test_datasets/VINST_train_red.xls').index)

    ds = datasource['xes']
    assert ds.is_xes
    assert ds.xes_columns_names == {'activity': 'concept:name',
                                    'id': 'case:concept:name',
                                    'resource': 'org:resource',
                                    'timestamp': 'time:timestamp'}
    assert ds.columns_list == ['org:resource',
                               'time:timestamp',
                               'concept:name',
                               'lifecycle:transition',
                               'case:concept:name']

    log = pm4py.read_xes('test_datasets/test_file_xes.xes')
    dataframe = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)

    assert len(ds.data.index) == len(dataframe.index)


def test_get_activity_list(datasource):
    assert datasource['csv'].get_activity_list('ACTIVITY') == ['Service closure Request with network responsibility',
                                                               'Service closure Request with BO responsibility',
                                                               'Pending Request for Reservation Closure',
                                                               'Pending Liquidation Request',
                                                               'Request created',
                                                               'Authorization Requested',
                                                               'Evaluating Request (NO registered letter)',
                                                               'Network Adjustment Requested']

    assert datasource['xls'].get_activity_list('ACTIVITY') == ['In Progress',
                                                               'Awaiting Assignment',
                                                               'Resolved',
                                                               'Assigned',
                                                               'Closed',
                                                               'Wait - User',
                                                               'Wait - Implementation',
                                                               'Wait',
                                                               'Wait - Vendor']

    assert datasource['xes'].get_activity_list('concept:name') == ['A', 'E', 'D', 'C', 'B']


def test_to_dict(datasource):
    assert datasource['csv'].to_dict('1234', save_df_data=False) == \
           {'columns_list': ['Unnamed: 0',
                             'REQUEST_ID',
                             'CLOSURE_TYPE',
                             'CLOSURE_REASON',
                             'ACTIVITY',
                             'END_DATE',
                             'START_DATE',
                             'CE_UO',
                             'ROLE'],
            'data': os.path.join(os.getcwd(),'datasets_for_gui\\train_df_1234.csv'),
            'file_path': 'test_datasets/bac_train_red.csv',
            'is_xes': False,
            'xes_columns_names': {}}

    assert datasource['xls'].to_dict('1234', save_df_data=False) == \
           {'columns_list': ['Unnamed: 0',
                             'SR_Number',
                             'Change_Date+Time',
                             'Status',
                             'ACTIVITY',
                             'Involved_ST_Function_Div',
                             'Involved_Org_line_3',
                             'Involved_ST',
                             'SR_Latest_Impact',
                             'Product',
                             'Country',
                             'Owner_Country'],
            'data': os.path.join(os.getcwd(),'datasets_for_gui\\train_df_1234.csv'),
            'file_path': 'test_datasets/VINST_train_red.xls',
            'is_xes': False,
            'xes_columns_names': {}}

    assert datasource['xes'].to_dict('1234', save_df_data=False) == \
           {'columns_list': ['org:resource',
                             'time:timestamp',
                             'concept:name',
                             'lifecycle:transition',
                             'case:concept:name'],
            'data': os.path.join(os.getcwd(),'datasets_for_gui\\train_df_1234.csv'),
            'file_path': 'test_datasets/test_file_xes.xes',
            'is_xes': True,
            'xes_columns_names': {'activity': 'concept:name',
                                  'id': 'case:concept:name',
                                  'resource': 'org:resource',
                                  'timestamp': 'time:timestamp'}}


def test_convert_datetime_to_seconds(datasource):
    datasource['csv'].convert_datetime_to_seconds('START_DATE')
    assert datasource['csv'].data.dtypes['START_DATE'] == 'int64'

    datasource['xls'].convert_datetime_to_seconds('Change_Date+Time')
    assert datasource['xls'].data.dtypes['Change_Date+Time'] == 'float64'

    datasource['xes'].convert_datetime_to_seconds('time:timestamp')
    assert datasource['xes'].data.dtypes['time:timestamp'] == 'float64'

def test_build_TrainDataSource_from_dict():
    dict_obj = {'columns_list': ['Unnamed: 0',
                                 'REQUEST_ID',
                                 'CLOSURE_TYPE',
                                 'CLOSURE_REASON',
                                 'ACTIVITY',
                                 'END_DATE',
                                 'START_DATE',
                                 'CE_UO',
                                 'ROLE'],
                'data': os.path.join(os.getcwd(), 'datasets_for_gui\\train_df_1234.csv'),
                'file_path': 'test_datasets/bac_train_red.csv',
                'is_xes': False,
                'xes_columns_names': {}}

    obj = build_TrainDataSource_from_dict(dict_obj, load_df=False)
    expected = TrainDataSource('test_datasets/bac_train_red.csv')
    assert obj.columns_list == expected.columns_list
    assert obj.is_xes == expected.is_xes
    assert obj.xes_columns_names == expected.xes_columns_names
    assert obj.file_path == expected.file_path
