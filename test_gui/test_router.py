from gui.views.BaseView import IDs as baseIDs

from unittest.mock import patch, PropertyMock

from test_gui import router, CALLBACKS

from test_gui.test_utils import PropertyMocker, mock_dash_context


def test_update_links():
    pathname_list = ['', '/', '/run', '/explain']
    with PropertyMocker(router, 'pathname_list', PropertyMock(return_value=pathname_list)):
        assert mock_dash_context(CALLBACKS['update_links'],
                                 [''], ('/', 0, 0)) == ['/run', '']

    with PropertyMocker(router, 'pathname_list', PropertyMock(return_value=['/', '/run', '/explain'])):
        # test page changes (n_clicks values >1 have the same behaviour), click is simulated via dash context
        assert mock_dash_context(CALLBACKS['update_links'],
                                 [baseIDs.GO_NEXT_BTN + '.n_clicks'], ('/', 1, 1)) == ['/run', '/explain']

    with PropertyMocker(router, 'pathname_list', PropertyMock(return_value=pathname_list)):
        assert mock_dash_context(CALLBACKS['update_links'],
                                 [baseIDs.GO_NEXT_BTN + '.n_clicks'], ('/run', 1, 1)) == ['/explain', '/']

    with PropertyMocker(router, 'pathname_list', PropertyMock(return_value=pathname_list)):
        assert mock_dash_context(CALLBACKS['update_links'],
                                 [baseIDs.GO_NEXT_BTN + '.n_clicks'], ('/explain', 1, 1)) == ['', '/run']

    with PropertyMocker(router, 'pathname_list', PropertyMock(return_value=['/', '/run', '/explain'])):
        assert mock_dash_context(CALLBACKS['update_links'],
                                 [baseIDs.GO_BACK_BTN + '.n_clicks'], ('/', 1, 1)) == ['/run', '']

    with PropertyMocker(router, 'pathname_list', PropertyMock(return_value=pathname_list)):
        assert mock_dash_context(CALLBACKS['update_links'],
                                 [baseIDs.GO_BACK_BTN + '.n_clicks'], ('/run', 0, 1)) == ['/explain', '/']
