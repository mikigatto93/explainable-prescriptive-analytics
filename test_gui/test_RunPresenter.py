import dash
import pytest

from gui.views.BaseView import IDs as baseIDs

from unittest.mock import patch, PropertyMock, MagicMock

from test_gui import run_pres, CALLBACKS

from test_gui.tutils import PropertyMocker, mock_dash_context


def test_show_gen_pred_button():
    assert CALLBACKS['show_gen_pred_button'](0) == [dash.no_update, dash.no_update]

    with patch('gui.model.RunDataSource.RunDataSource.__init__', ) as mock_init_exc:
        mock_init_exc.side_effect = ValueError('test_exception')
        assert CALLBACKS['show_gen_pred_button'](1) == [False, False]

    with patch('gui.model.RunDataSource.RunDataSource.__init__', ) as mock_init_no_exc:
        mock_init_no_exc.return_value = None  # a valid __init__ returns None
        assert CALLBACKS['show_gen_pred_button'](1) == [True, True]


def test_update_running_progress():
    mock_prog_logger = MagicMock()

    with pytest.raises(dash.exceptions.PreventUpdate):
        assert CALLBACKS['update_running_progress'](0)

    with PropertyMocker(run_pres, 'progress_logger', PropertyMock(return_value=mock_prog_logger)):
        mock_prog_logger.get_from_stack.return_value = 'test'
        assert CALLBACKS['update_running_progress'](1) == 'test'

    with PropertyMocker(run_pres, 'progress_logger', PropertyMock(return_value=mock_prog_logger)):
        mock_prog_logger.get_from_stack.return_value = None
        with pytest.raises(dash.exceptions.PreventUpdate):
            assert CALLBACKS['update_running_progress'](1)


