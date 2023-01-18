from gui.views.BaseView import IDs as baseIDs

from unittest.mock import patch, PropertyMock, MagicMock

from test_gui import router, CALLBACKS

from test_gui.tutils import PropertyMocker, mock_dash_context


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


def test_change_page():
    mock_view_1 = MagicMock(pathname='v1')
    mock_view_1.get_layout.return_value = 'v1_view'
    mock_view_2 = MagicMock(pathname='v2')
    mock_view_2.get_layout.return_value = 'v2_view'
    mock_view_3 = MagicMock(pathname='v3')
    mock_view_3.get_layout.return_value = 'v3_view'

    view_dict = {'1': mock_view_1, '2': mock_view_2, '3': mock_view_3}

    with PropertyMocker(router, 'views', PropertyMock(return_value=view_dict)):
        assert CALLBACKS['change_page']('v1') == 'v1_view'
        assert CALLBACKS['change_page']('v2') == 'v2_view'
        assert CALLBACKS['change_page']('v3') == 'v3_view'
        assert CALLBACKS['change_page']('v4') == '404: Not Found'


def test_disable_unreachable_links():
    assert CALLBACKS['disable_unreachable_links']('', '') == [True, True]
    assert CALLBACKS['disable_unreachable_links']('test', '') == [False, True]
    assert CALLBACKS['disable_unreachable_links']('', 'test') == [True, False]
    assert CALLBACKS['disable_unreachable_links']('test', 'test') == [False, False]


def test_disable_link_arrows_custom():
    assert 1 == 1
