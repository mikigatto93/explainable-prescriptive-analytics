import os

import pandas as pd
import pm4py

import pytest

from gui.model.RunDataSource import RunDataSource, build_RunDataSource_from_dict
from pm4py.objects.conversion.log import converter as log_converter


@pytest.fixture
def datasource():
    yield {'csv': RunDataSource('test_datasets/bac_train_red.csv', read_data=True),
           'xls': RunDataSource('test_datasets/VINST_train_red.xls', read_data=True),
           'xes': RunDataSource('test_datasets/test_file_xes.xes', read_data=True)}


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
    # assert ds.xes_columns_names == {'activity': 'concept:name',
    #                                 'id': 'case:concept:name',
    #                                 'resource': 'org:resource',
    #                                 'timestamp': 'time:timestamp'}

    assert ds.xes_columns_names == {}
    assert ds.columns_list == ['org:resource',
                               'time:timestamp',
                               'concept:name',
                               'lifecycle:transition',
                               'case:concept:name']

    log = pm4py.read_xes('test_datasets/test_file_xes.xes')
    dataframe = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)

    assert len(ds.data.index) == len(dataframe.index)


def test_remove_unnamed_columns(datasource):
    datasource['csv'].remove_unnamed_columns()
    assert 'Unnamed: 0' not in datasource['csv'].data.columns
    assert 'Unnamed: 0' not in datasource['csv'].columns_list

    datasource['xls'].remove_unnamed_columns()
    assert 'Unnamed: 0' not in datasource['xls'].data.columns
    assert 'Unnamed: 0' not in datasource['xls'].columns_list

    datasource['xes'].remove_unnamed_columns()
    assert 'Unnamed: 0' not in datasource['xes'].data.columns
    assert 'Unnamed: 0' not in datasource['xes'].columns_list


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
            'data': os.path.join(os.getcwd(), 'datasets_for_gui\\run_df_1234.csv'),
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
            'data': os.path.join(os.getcwd(), 'datasets_for_gui\\run_df_1234.csv'),
            'file_path': 'test_datasets/VINST_train_red.xls',
            'is_xes': False,
            'xes_columns_names': {}}

    assert datasource['xes'].to_dict('1234', save_df_data=False) == \
           {'columns_list': ['org:resource',
                             'time:timestamp',
                             'concept:name',
                             'lifecycle:transition',
                             'case:concept:name'],
            'data': os.path.join(os.getcwd(), 'datasets_for_gui\\run_df_1234.csv'),
            'file_path': 'test_datasets/test_file_xes.xes',
            'is_xes': True,
            'xes_columns_names': {}}


def test_convert_datetime_to_seconds(datasource):
    datasource['csv'].convert_datetime_to_seconds('START_DATE')
    assert datasource['csv'].data.dtypes['START_DATE'] == 'int64'

    datasource['xls'].convert_datetime_to_seconds('Change_Date+Time')
    assert datasource['xls'].data.dtypes['Change_Date+Time'] == 'float64'

    datasource['xes'].convert_datetime_to_seconds('time:timestamp')
    assert datasource['xes'].data.dtypes['time:timestamp'] == 'float64'


def test_build_RunDataSource_from_dict():
    dict_obj = {'columns_list': ['Unnamed: 0',
                                 'REQUEST_ID',
                                 'CLOSURE_TYPE',
                                 'CLOSURE_REASON',
                                 'ACTIVITY',
                                 'END_DATE',
                                 'START_DATE',
                                 'CE_UO',
                                 'ROLE'],
                'data': os.path.join(os.getcwd(), 'datasets_for_gui\\run_df_1234.csv'),
                'file_path': 'test_datasets/bac_train_red.csv',
                'is_xes': False,
                'xes_columns_names': {}}

    obj = build_RunDataSource_from_dict(dict_obj, load_df=False)
    expected = RunDataSource('test_datasets/bac_train_red.csv')
    assert obj.columns_list == expected.columns_list
    assert obj.is_xes == expected.is_xes
    assert obj.xes_columns_names == expected.xes_columns_names
    assert obj.file_path == expected.file_path
