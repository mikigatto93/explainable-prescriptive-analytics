from unittest.mock import MagicMock, PropertyMock, patch

import dash
import pytest

from gui.views import ExplainView
from test_gui import explain_pres, CALLBACKS
from test_gui.tutils import PropertyMocker


def show_error_explain():
    # error_data
    pass


def show_prediction_graph():
    # ex_info_data, user_id, url
    pass


def scroll_graph():
    # page_value_sel, user_id, n_clicks_up, n_clicks_down, n_clicks_sel_page
    pass


def show_preds_text_format():
    # input_value, user_id, click_data, n_clicks
    pass


def select_trace_activity_to_explain():
    # n_clicks1, n_clicks2, n_clicks3, ch1, ch2, ch3, trace_id, user_id
    pass


def change_quantity_explanations():
    # trace_id, act_to_explain, user_id, value
    pass


def calculate_and_visualize_shap_by_trace():
    # act_to_explain, trace_id, expl_qnt, user_id, n_clicks
    pass
