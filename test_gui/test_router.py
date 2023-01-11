import pytest
from index import startup_gui
from unittest.mock import patch, PropertyMock, MagicMock

from contextvars import copy_context
from dash._callback_context import context_value
from dash._utils import AttributeDict

from gui.views.BaseView import IDs as baseIDs


from unittest.mock import patch, PropertyMock

from test_gui import router, CALLBACKS


def test_update_links():
    with patch.object(router, 'pathname_list') as mock:
        p_m = PropertyMock(return_value='test')
        type(router).pathname_list = p_m
        assert CALLBACKS['update_links']('/', 0, 0) == 'test'


    # def run_callback():
    #     context_value.set(AttributeDict(**{'triggered_inputs': [{'prop_id': baseIDs.GO_BACK_BTN}]}))
    #     return CALLBACKS['update_links']('/', 0, 0)
    #
    # ctx = copy_context()
    # output = ctx.run(run_callback)
    # print(output)


# def test_change_page():
#     print(Router.__dict__)
#     assert CALLBACKS['change_page']('test') == '404: Not Found'
