import json

import dash
import pytest

from gui.views.BaseView import IDs as baseIDs

from unittest.mock import patch, PropertyMock, MagicMock

from test_gui import run_pres, CALLBACKS

from test_gui.tutils import PropertyMocker, mock_dash_context


def test_show_gen_pred_button():
    assert CALLBACKS['show_gen_pred_button']('test_path', '1234', 0) == [dash.no_update, dash.no_update, dash.no_update]

    with patch('gui.model.RunDataSource.RunDataSource.__init__') as mock_init_exc:
        mock_init_exc.side_effect = ValueError('test_exception')
        assert CALLBACKS['show_gen_pred_button']('test_path', '1234', 1) == [False, False, 'ValueError: test_exception']

    with patch('gui.model.RunDataSource.RunDataSource.__init__') as mock_init_no_exc, \
            patch('gui.model.RunDataSource.RunDataSource.to_dict') as mock_to_dict:
        mock_init_no_exc.return_value = None  # a valid __init__ returns None
        mock_to_dict.return_value = None
        assert CALLBACKS['show_gen_pred_button']('test_path', '1234', 1) == [True, True, '']


def test_generate_predictions():
    assert CALLBACKS['generate_predictions']('arg1', 'arg2', 0) == [dash.no_update, dash.no_update, dash.no_update]

    test_experiments_data = json.dumps({"ex_name": "test1", "kpi": "Total time", "id": "SR_Number",
                                        "timestamp": "Change_Date+Time", "activity": "ACTIVITY",
                                        "resource": None, "act_to_opt": "Involved_ST", "out_thrs": 0.03,
                                        "pred_column": "remaining_time", "creation_timestamp": "2023-01-30"})

    assert CALLBACKS['generate_predictions'](test_experiments_data, 'arg2', 1)


def test_update_running_progress():
    mock_rundatasource_builder = MagicMock()

    with pytest.raises(dash.exceptions.PreventUpdate):
        assert CALLBACKS['update_running_progress']('1234', 0)

    with PropertyMocker(run_pres, 'progress_loggers', PropertyMock(return_value={'1234': 'dummy'})):
        with patch('gui.presenters.RunPresenter.build_RunProgLogger_from_dict', mock_rundatasource_builder):
            mock_prog_logger = MagicMock()
            mock_prog_logger.get_from_stack.return_value = 'test'
            mock_rundatasource_builder.return_value = mock_prog_logger
            assert CALLBACKS['update_running_progress']('1234', 1) == 'test'

    with PropertyMocker(run_pres, 'progress_loggers', PropertyMock(return_value={'1234': 'dummy'})):
        with patch('gui.presenters.RunPresenter.build_RunProgLogger_from_dict', mock_rundatasource_builder):
            mock_rundatasource_builder.side_effect = ValueError('test_exception')  # random exception
            with pytest.raises(dash.exceptions.PreventUpdate):
                assert CALLBACKS['update_running_progress']('1234', 1)
