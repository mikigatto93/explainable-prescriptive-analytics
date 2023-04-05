import json
import os
import pathlib
import shutil
import tarfile
import tempfile

import pytest

from gui.model.Experiment import Experiment
from gui.model.IO.IOManager import Paths
from gui.model.TrainDataSource import TrainDataSource
from gui.model.Trainer import Trainer, build_Trainer_from_dict

ex = Experiment(
    ex_name='test',
    kpi='Total time',
    id='ID',
    timestamp='TIMESTAMP',
    activity='ACTIVITY',
    resource=None,
    act_to_opt=None,
    out_thrs=0.02,
    creation_timestamp='10-02-2023_21-48-26_541142+0000'
)

ds = TrainDataSource(path='test_datasets/bac_train_red.csv')


@pytest.fixture
def trainer():
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = pathlib.Path(temp_dir.name)
    yield Trainer(ex, ds, main_path=temp_path), temp_path
    temp_dir.cleanup()


def test_trainer_init(trainer):
    assert trainer[0].ex_info.__dict__ == ex.__dict__
    assert trainer[0].data_source.__dict__ == ds.__dict__
    assert trainer[0].train_info is None
    assert trainer[0].paths.main_path == os.path.join(trainer[1], 'test--10-02-2023_21-48-26_541142+0000')
    assert trainer[0].paths.folders == Paths(ex.ex_name, main_path=trainer[1],
                                             creation_timestamp='10-02-2023_21-48-26_541142+0000').folders


def test_write_experiment_info(trainer):
    trainer[0].write_experiment_info()
    assert os.path.exists(trainer[0].paths.folders['experiment'])

    with open(trainer[0].paths.folders['experiment'], 'r') as f:
        content = f.read()

    assert json.loads(content) == ex.to_dict()


def test_to_dict(trainer):
    assert trainer[0].to_dict('1234', save_df_data=False) == \
           {'data_source': {'columns_list': ['Unnamed: 0',
                                             'REQUEST_ID',
                                             'CLOSURE_TYPE',
                                             'CLOSURE_REASON',
                                             'ACTIVITY',
                                             'END_DATE',
                                             'START_DATE',
                                             'CE_UO',
                                             'ROLE'],
                            'data': os.path.join(os.getcwd(), 'datasets_for_gui'
                                                              '\\train_df_1234.csv'),
                            'file_path': 'test_datasets/bac_train_red.csv',
                            'is_xes': False,
                            'xes_columns_names': {}},
            'ex_info': {'act_to_opt': None,
                        'activity': 'ACTIVITY',
                        'creation_timestamp': '10-02-2023_21-48-26_541142+0000',
                        'ex_name': 'test',
                        'id': 'ID',
                        'kpi': 'Total time',
                        'out_thrs': 0.02,
                        'pred_column': 'remaining_time',
                        'resource': None,
                        'timestamp': 'TIMESTAMP'}}


def test_create_model_archive(trainer):
    shutil.copytree('test_experiments_dir/test--10-02-2023_21-48-26_541142+0000', trainer[0].paths.main_path)
    archive_path = trainer[0].create_model_archive()
    assert os.path.exists(archive_path)

    expected_file_list = ['model.pkl', 'dfTrain.csv', 'dfTest.csv', 'dfValid.csv', 'dfTrain_without_valid.csv',
                          'model_configuration.json', 'data_info.json', 'experiment_info.json']
    with tarfile.open(archive_path, 'r:xz') as tar:
        assert set(tar.getnames()) == set(expected_file_list)


def test_build_Trainer_from_dict(trainer):
    dict_obj = {'data_source': {'columns_list': ['Unnamed: 0',
                                                 'REQUEST_ID',
                                                 'CLOSURE_TYPE',
                                                 'CLOSURE_REASON',
                                                 'ACTIVITY',
                                                 'END_DATE',
                                                 'START_DATE',
                                                 'CE_UO',
                                                 'ROLE'],
                                'data': 'F:\\STAGE\\explainable-prescriptive-analytics\\test_gui\\datasets_for_gui'
                                        '\\train_df_1234.csv',
                                'file_path': 'test_datasets/bac_train_red.csv',
                                'is_xes': False,
                                'xes_columns_names': {}},
                'ex_info': {'act_to_opt': None,
                            'activity': 'ACTIVITY',
                            'creation_timestamp': '10-02-2023_21-48-26_541142+0000',
                            'ex_name': 'test',
                            'id': 'ID',
                            'kpi': 'Total time',
                            'out_thrs': 0.02,
                            'pred_column': 'remaining_time',
                            'resource': None,
                            'timestamp': 'TIMESTAMP'}}

    built_trainer = build_Trainer_from_dict(dict_obj, load_data_source=False, main_path=trainer[1])
    assert built_trainer.data_source.file_path == trainer[0].data_source.file_path
    assert built_trainer.data_source.xes_columns_names == trainer[0].data_source.xes_columns_names
    assert built_trainer.data_source.columns_list == trainer[0].data_source.columns_list
    assert built_trainer.data_source.is_xes == trainer[0].data_source.is_xes
    assert built_trainer.data_source.file_path == trainer[0].data_source.file_path
    assert built_trainer.ex_info.__dict__ == trainer[0].ex_info.__dict__
    assert built_trainer.paths.folders == trainer[0].paths.folders
    assert built_trainer.train_info == trainer[0].train_info
