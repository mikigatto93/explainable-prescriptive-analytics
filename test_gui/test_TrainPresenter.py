from unittest.mock import MagicMock, PropertyMock, patch

import dash
import pytest
from freezegun import freeze_time

from gui.views import TrainView
from gui.views.TrainView import IDs as trainIDs
from test_gui import train_pres, CALLBACKS
from test_gui.tutils import PropertyMocker


# TEST CLASS METHODS
def test_validate_input():
    # {ex_name, kpi, id, timestamp, activity, act_to_opt}
    assert train_pres.validate_input({'ex_name': 'valid_name',
                                      'kpi': 'valid_kpi',
                                      'id': 'valid_id',
                                      'timestamp': 'valid_timestamp',
                                      'activity': 'valid_activity',
                                      'act_to_opt': 'valid_act_to_opt'}) == {}

    assert train_pres.validate_input({}) == {}

    assert train_pres.validate_input({'ex_name': None,
                                      'kpi': None,
                                      'id': None,
                                      'timestamp': None,
                                      'activity': None,
                                      'act_to_opt': None}) == {

               trainIDs.ACTIVITY_DROPDOWN: 'One ACTIVITY column must be selected',
               trainIDs.EXPERIMENT_NAME_TEXTBOX: 'Experiment name is empty',
               trainIDs.ID_DROPDOWN: 'One ID column must be selected',
               trainIDs.KPI_RADIO_ITEMS: 'One KPI must be selected',
               trainIDs.TIMESTAMP_DROPDOWN: 'One TIMESTAMP column must be selected'
           }

    assert train_pres.validate_input({'ex_name': 'invalid:_ex_name'}) == \
           {trainIDs.EXPERIMENT_NAME_TEXTBOX: 'Experiment name cannot contain the following characters: <, >, :, ", '
                                              '/, \\, |, ?, *'}

    assert train_pres.validate_input({'ex_name': '.invalid_ex_name'}) == \
           {trainIDs.EXPERIMENT_NAME_TEXTBOX: 'Experiment name cannot start with "."'}


# TEST CALLBACKS
def test_show_error_training():
    with pytest.raises(dash.exceptions.PreventUpdate):
        assert CALLBACKS['show_error_training'](None)

    assert CALLBACKS['show_error_training']({
        'id_not_in_errors_ids': 'ignored_message',
        'id_dropdown': 'message1',
        'experiment_name_textbox': 'message10'
    }) == ['message1', '', '', '', '', '', '', '', '', 'message10', '']

    assert CALLBACKS['show_error_training']({}) == ['', '', '', '', '', '', '', '', '', '', '']


def test_populate_experiment_selector_dropdown():
    assert CALLBACKS['populate_experiment_selector_dropdown']('other_path_name') == []

    with patch('gui.presenters.TrainPresenter.IOManager.get_experiment_folders_list') as mock_iomanagergetfoldderlist:
        mock_iomanagergetfoldderlist.return_value = []
        assert CALLBACKS['populate_experiment_selector_dropdown'](train_pres.views['train'].pathname) == []

    with patch('gui.presenters.TrainPresenter.IOManager.get_experiment_folders_list') as mock_iomanagergetfoldderlist:
        mock_iomanagergetfoldderlist.return_value = [
            {'ex_name': 'EX1', 'path': 'path/to/ex1'},
            {'ex_name': 'EX2', 'path': 'path/to/ex2'},
            {'ex_name': 'EX3', 'path': 'path/to/ex3'},
        ]

        assert CALLBACKS['populate_experiment_selector_dropdown'](train_pres.views['train'].pathname) == [
            {'label': 'EX1', 'value': 'path/to/ex1'},
            {'label': 'EX2', 'value': 'path/to/ex2'},
            {'label': 'EX3', 'value': 'path/to/ex3'}
        ]


def test_show_selected_experiment_creation_timestamp():
    with pytest.raises(dash.exceptions.PreventUpdate):
        assert CALLBACKS['show_selected_experiment_creation_timestamp']('')
        with patch('os.path.isdir') as mock_isdir:
            mock_isdir.return_value = False
            assert CALLBACKS['show_selected_experiment_creation_timestamp']('invalid_path')

    with patch('os.path.isdir') as mock_isdir, \
            patch('gui.presenters.TrainPresenter.IOManager.read') as mock_iomanagerread:
        mock_iomanagerread.return_value = {}
        mock_isdir.return_value = True
        assert CALLBACKS['show_selected_experiment_creation_timestamp']('valid_path') == ''

    with patch('os.path.isdir') as mock_isdir, \
            patch('gui.presenters.TrainPresenter.IOManager.read') as mock_iomanagerread:
        mock_iomanagerread.return_value = {'creation_timestamp': '31-01-2023_16-20-38_442591+0000'}
        mock_isdir.return_value = True
        assert CALLBACKS['show_selected_experiment_creation_timestamp']('valid_path') == \
               'Created: Tue Jan 31 16:20:38 2023'


def test_disable_load_model_btn():
    assert CALLBACKS['disable_load_model_btn']([], 'value')
    assert CALLBACKS['disable_load_model_btn'](['opt1', 'opt2'], '')
    assert not CALLBACKS['disable_load_model_btn'](['opt1', 'opt2'], 'value')
    assert CALLBACKS['disable_load_model_btn']([], '')


@freeze_time('2023-01-30')
def test_load_trained_model_data():
    test_ex_info_data = {"ex_name": "test1", "kpi": "Minimize activity occurrence", "id": "SR_Number",
                         "timestamp": "Change_Date+Time", "activity": "ACTIVITY",
                         "resource": None, "act_to_opt": "Involved_ST", "out_thrs": 0.03,
                         "pred_column": "remaining_time"}

    test_ex_info_data2 = {"ex_name": "test1", "kpi": "Total time", "id": "SR_Number",
                          "timestamp": "Change_Date+Time", "activity": "ACTIVITY",
                          "resource": "res", "act_to_opt": None, "out_thrs": 0.03,
                          "pred_column": "remaining_time"}

    assert CALLBACKS['load_trained_model_data']('folder_path', '1234', 0) == [dash.no_update] * 33

    with patch('gui.presenters.TrainPresenter.IOManager.read') as mock_iomanagerread, \
            patch('shutil.copytree') as mock_copytree, \
            patch('gui.presenters.TrainPresenter.Trainer') as mock_trainer:
        mock_iomanagerread.return_value = test_ex_info_data
        mock_trainer.return_value.create_model_archive.return_value = None

        assert CALLBACKS['load_trained_model_data']('folder_path', '1234', 1) == [
            '{"ex_name": "test1", "kpi": "Minimize activity occurrence", "id": "SR_Number", "timestamp": '
            '"Change_Date+Time", "activity": "ACTIVITY", "resource": null, "act_to_opt": '
            '"Involved_ST", "out_thrs": 0.03, "pred_column": "remaining_time", '
            '"creation_timestamp": "30-01-2023_00-00-00_000000+0000"}',
            'test1',
            'Minimize activity occurrence',
            'SR_Number',
            'Change_Date+Time',
            'ACTIVITY',
            None, 'Involved_ST', 0.03,
            [{'disabled': True, 'label': 'Total time', 'value': 'Total time'},
             {'disabled': True, 'label': 'Minimize activity occurrence', 'value': 'Minimize activity occurrence'}],
            ['SR_Number'],
            ['Change_Date+Time'],
            ['ACTIVITY'],
            [], ['Involved_ST'],
            True, True, True, True, True, True, True, True, True, False, True, True, True, True, False, True, True, True
        ]

        mock_iomanagerread.return_value = test_ex_info_data2

        assert CALLBACKS['load_trained_model_data']('folder_path', '1234', 1) == [
            '{"ex_name": "test1", "kpi": "Total time", "id": "SR_Number", "timestamp": '
            '"Change_Date+Time", "activity": "ACTIVITY", "resource": "res", "act_to_opt": '
            'null, "out_thrs": 0.03, "pred_column": "remaining_time", '
            '"creation_timestamp": "30-01-2023_00-00-00_000000+0000"}',
            'test1',
            'Total time',
            'SR_Number',
            'Change_Date+Time',
            'ACTIVITY',
            'res', dash.no_update, 0.03,
            [{'disabled': True, 'label': 'Total time', 'value': 'Total time'},
             {'disabled': True, 'label': 'Minimize activity occurrence', 'value': 'Minimize activity occurrence'}],
            ['SR_Number'],
            ['Change_Date+Time'],
            ['ACTIVITY'],
            ['res'], dash.no_update,
            True, True, True, True, True, True, True, True, False, False, True, True, True, True, False, True, True,
            True
        ]


def test_populate_dropdown_options():
    assert CALLBACKS['populate_dropdown_options']('train_file_path', '1234', 0) == [dash.no_update] * 21 + [False]

    with patch('gui.presenters.TrainPresenter.TrainDataSource.__init__') as mock_traindatasource_init:
        mock_traindatasource_init.side_effect = ValueError('test_exception')
        assert CALLBACKS['populate_dropdown_options']('train_file_path', '1234', 1) == \
               [{'load_train_file_btn': 'ValueError: test_exception'}] + [dash.no_update] * 20 + [False]

    with PropertyMocker(train_pres, 'data_sources', PropertyMock(return_value={})):
        with patch('gui.presenters.TrainPresenter.TrainDataSource') as mock_traindatasource:
            mock_traindatasource.to_dict.return_value = None
            mock_traindatasource.return_value.columns_list = ['COL1', 'COL2', 'COL3']
            mock_traindatasource.return_value.is_xes = False
            assert CALLBACKS['populate_dropdown_options']('train_file_path', '1234', 1) == \
                   [{}] + [['COL1', 'COL2', 'COL3']] * 4 + [dash.no_update, 0.02] + [dash.no_update] * 10 + \
                   [True, True, True, dash.no_update, True]

    with PropertyMocker(train_pres, 'data_sources', PropertyMock(return_value={})):
        with patch('gui.presenters.TrainPresenter.TrainDataSource') as mock_traindatasource:
            mock_traindatasource.to_dict.return_value = None
            mock_traindatasource.return_value.columns_list = ['COL1', 'COL2', 'COL3']
            mock_traindatasource.return_value.is_xes = True
            mock_traindatasource.return_value.xes_columns_names = {'id': 'id', 'timestamp': 'timestamp',
                                                                   'activity': 'activity', 'resource': 'resource'}

            mock_traindatasource.return_value.get_activity_list.return_value = ['ACTNAME1', 'ACTNAME2', 'ACTNAME3']

            assert CALLBACKS['populate_dropdown_options']('train_file_path', '1234', 1) == [{}] + \
                   [['COL1', 'COL2', 'COL3']] * 4 + \
                   [['ACTNAME1', 'ACTNAME2', 'ACTNAME3'], 0.02] + \
                   ['id', 'timestamp', 'activity', 'resource'] + [True] * 11


def test_show_choose_act_to_opt_dropdown():
    assert CALLBACKS['show_choose_act_to_opt_dropdown']('Maximize activity occurrence')
    assert CALLBACKS['show_choose_act_to_opt_dropdown']('Minimize activity occurrence')
    assert not CALLBACKS['show_choose_act_to_opt_dropdown']('other kpis')


def test_go_2nd_phase_train_option_selection():
    # _id, timestamp, activity, resource, user_id, n_clicks
    assert CALLBACKS['go_2nd_phase_train_option_selection']('test', 'test', 'test', 'test', '1234', 0) == \
           [dash.no_update] * 11

    with patch('gui.presenters.TrainPresenter.TrainPresenter.validate_input') as mock_validate:
        mock_validate.return_value = {'component_id': 'error_message'}
        assert CALLBACKS['go_2nd_phase_train_option_selection']('test', 'test', 'test', 'test', '1234', 1) == \
               [[], False, {'component_id': 'error_message'}] + \
               [False] * 4 + [TrainView.get_kpi_radio_items_options(True), True, False, False]

    mock_traindatasource = MagicMock()
    with PropertyMocker(train_pres, 'data_sources', PropertyMock(return_value={'1234': 'dummy'})):
        with patch('gui.presenters.TrainPresenter.build_TrainDataSource_from_dict') as mock_traindatasource_builder, \
                patch('gui.presenters.TrainPresenter.TrainPresenter.validate_input') as mock_validate:
            mock_validate.return_value = {}
            mock_traindatasource_builder.return_value = mock_traindatasource
            mock_traindatasource.get_activity_list.return_value = ['ACTIVITY1', 'ACTIVITY2', 'ACTIVITY3']
            assert CALLBACKS['go_2nd_phase_train_option_selection']('test', 'test', 'test', 'test', '1234', 1) == \
                   [['ACTIVITY1', 'ACTIVITY2', 'ACTIVITY3'], True, {}] + [True] * 4 + \
                   [TrainView.get_kpi_radio_items_options(False), False, True, False]


def test_return_1st_phase_train_option_selection():
    assert CALLBACKS['return_1st_phase_train_option_selection'](0) == [dash.no_update] * 8

    assert CALLBACKS['return_1st_phase_train_option_selection'](1) == [False] * 4 + \
           [TrainView.get_kpi_radio_items_options(True), True, False, True]


def test_collect_training_user_data():
    # ex_name, kpi, _id, timestamp, activity, resource, act_to_opt, out_thrs, user_id, n_clicks
    assert CALLBACKS['collect_training_user_data']('test', 'test', 'test', 'test',
                                                   'test', 'test', 'test', 'test', '1234', 0) == [dash.no_update] * 14

    with patch('gui.presenters.TrainPresenter.TrainPresenter.validate_input') as mock_validate:
        mock_validate.return_value = {'component_id': 'error_message'}
        assert CALLBACKS['collect_training_user_data'](
            'test', 'test', 'test', 'test', 'test', 'test', 'test', 'test', '1234', 1
        ) == [dash.no_update, dash.no_update, dash.no_update, {'component_id': 'error_message'}] + [dash.no_update] * 10

    with PropertyMocker(train_pres, 'data_sources', PropertyMock(return_value={'1234': 'dummy'})):
        with patch('gui.presenters.TrainPresenter.TrainPresenter.validate_input') as mock_validate, \
                patch('gui.presenters.TrainPresenter.Experiment') as mock_experiment, \
                patch('gui.presenters.TrainPresenter.Trainer') as mock_trainer, \
                patch('gui.presenters.TrainPresenter.build_TrainDataSource_from_dict') as mock_traindatasource_builder,\
                patch('gui.presenters.TrainPresenter.TrainProgLogger') as mock_trainproglogger:
            mock_validate.return_value = {}
            mock_traindatasource_builder.return_value = None
            mock_experiment.return_value.to_dict.return_value = None
            mock_trainer.return_value.to_dict.return_value = None
            mock_trainproglogger.return_value.to_dict.return_value = None

            assert CALLBACKS['collect_training_user_data'](
                'test', 'test', 'test', 'test', 'test', 'test', 'test', 'test', '1234', 1
            ) == [True, 'null', True, {}] + [True] * 9 + [TrainView.get_kpi_radio_items_options(disabled=True)]


def test_train_model():
    assert CALLBACKS['train_model'](False, '1234') == [dash.no_update] * 5

    mock_trainer = MagicMock()

    with PropertyMocker(train_pres, 'trainers', PropertyMock(return_value={'1234': 'dummy'})), \
            PropertyMocker(train_pres, 'progress_loggers', PropertyMock(return_value={'1234': 'dummy'})):
        with patch('gui.presenters.TrainPresenter.build_Trainer_from_dict') as mock_train_builder, \
                patch('gui.presenters.TrainPresenter.build_TrainProgLogger_from_dict') as mock_trainproglogger:
            mock_train_builder.return_value = mock_trainer
            mock_trainproglogger.return_value = MagicMock()

            mock_trainer.create_model_archive.return_value = None
            mock_trainer.prepare_dataset.side_effect = ValueError('test_exception')  # random exception
            assert CALLBACKS['train_model'](True, '1234') == \
                   ['An error occurred: ValueError: test_exception', {'display': 'none'}, False, False, True]

            mock_trainer.reset_mock(side_effect=True, return_value=True)
            mock_trainer.create_model_archive.return_value = None
            assert CALLBACKS['train_model'](True, '1234') == ['Training completed', {'display': 'none'},
                                                              True, True, False]


def test_download_train_files():
    with pytest.raises(dash.exceptions.PreventUpdate):
        assert CALLBACKS['download_train_files']('1234', 0)
        with PropertyMocker(train_pres, 'zip_files_paths', PropertyMock(return_value={'1234': None})):
            assert CALLBACKS['download_train_files']('1234', 1)

    with PropertyMocker(train_pres, 'zip_files_paths', PropertyMock(return_value={'1234': 'valid_path'})):
        with patch('gui.presenters.TrainPresenter.dash.dcc.send_file') as mock_dash_sendfile:
            mock_dash_sendfile.return_value = 'send_file'
            assert CALLBACKS['download_train_files']('1234', 1) == 'send_file'
            mock_dash_sendfile.assert_called_once_with('valid_path')


def test_update_training_progress():
    mock_trainproglogger_builder = MagicMock()

    with pytest.raises(dash.exceptions.PreventUpdate):
        assert CALLBACKS['update_training_progress']('1234', 0)

    with PropertyMocker(train_pres, 'progress_loggers', PropertyMock(return_value={'1234': 'dummy'})):
        with patch('gui.presenters.TrainPresenter.build_TrainProgLogger_from_dict', mock_trainproglogger_builder):
            mock_prog_logger = MagicMock()
            mock_prog_logger.get_from_stack.return_value = 'test'
            mock_trainproglogger_builder.return_value = mock_prog_logger
            assert CALLBACKS['update_training_progress']('1234', 1) == 'test'

    with PropertyMocker(train_pres, 'progress_loggers', PropertyMock(return_value={'1234': 'dummy'})):
        with patch('gui.presenters.TrainPresenter.build_TrainProgLogger_from_dict', mock_trainproglogger_builder):
            mock_trainproglogger_builder.side_effect = ValueError('test_exception')  # random exception
            with pytest.raises(dash.exceptions.PreventUpdate):
                assert CALLBACKS['update_training_progress']('1234', 1)
