from unittest.mock import patch

from contextvars import copy_context
from dash._callback_context import context_value
from dash._utils import AttributeDict


class PropertyMocker:
    def __init__(self, obj, prop_name, mock_instance):
        self.obj = obj
        self.prop_name = prop_name
        self.mock_instance = mock_instance

    def __enter__(self):
        with patch.object(self.obj, self.prop_name):
            setattr(type(self.obj), self.prop_name, self.mock_instance)

    def __exit__(self, type, value, traceback):
        pass


def mock_dash_context(fun, triggered_id, tuple_args):
    def run_callback():
        triggered_id_dict = {'triggered_inputs': [{'prop_id': _id} for _id in triggered_id]}
        context_value.set(AttributeDict(**triggered_id_dict))
        return fun(*tuple_args)

    ctx = copy_context()
    output = ctx.run(run_callback)
    return output
