import json
from unittest.mock import MagicMock, PropertyMock, patch

import dash
import pytest

from gui.views import ExplainView
from gui.views.ExplainView import IDs as explainIDs
from test_gui import explain_pres, CALLBACKS
from test_gui.tutils import PropertyMocker, mock_dash_context


def test_show_error_explain():
    with pytest.raises(dash.exceptions.PreventUpdate):
        assert CALLBACKS['show_error_explain'](None)

    assert CALLBACKS['show_error_explain']({
        'id_not_in_errors_ids': 'ignored_message',
        'search_trace_id_input': 'message1',
    }) == ['message1']

    assert CALLBACKS['show_error_explain']({}) == ['']


def test_show_prediction_graph():
    # ex_info_data, user_id, url
    valid_pathname = explain_pres.views['explain'].pathname
    assert CALLBACKS['show_prediction_graph']({}, '123', 'EXPL_SORT_METHOD', valid_pathname) == [dash.no_update] * 3
    assert CALLBACKS['show_prediction_graph']({}, '123', 'EXPL_SORT_METHOD', 'invalid_pathname') == [dash.no_update] * 3

    with patch('gui.presenters.ExplainPresenter.Explainer') as mock_explainer, \
         patch('gui.presenters.ExplainPresenter.Experiment.build_experiment_from_dict') as mock_experiment_builder, \
         patch('gui.presenters.ExplainPresenter.ExplainPresenter.create_pred_graph') as mock_createpredgraph:
        mock_experiment_builder.return_value = None
        mock_explainer.return_value.to_dict.return_value = None
        mock_explainer.return_value.calculate_best_scores.return_value = {
            'trace0': [1234, 3456],
            'trace1': [12345, 34567],
            'trace2': [12347, 34568],
        }
        mock_createpredgraph.return_value = 'pred_graph_data'
        assert CALLBACKS['show_prediction_graph'](json.dumps({'experiment': 'data'}), '123',
                                                  'EXPL_SORT_METHOD', valid_pathname) == \
               ['pred_graph_data', '1/1', 'EXPL_SORT_METHOD']

        with PropertyMocker(explain_pres, 'REC_PER_PAGE', PropertyMock(return_value=2)):
            assert CALLBACKS['show_prediction_graph'](json.dumps({'experiment': 'data'}), '123',
                                                      'EXPL_SORT_METHOD', valid_pathname) == \
                   ['pred_graph_data', '1/2', 'EXPL_SORT_METHOD']


def test_scroll_graph():
    # page_value_sel, user_id, n_clicks_up, n_clicks_down, n_clicks_sel_page
    assert mock_dash_context(CALLBACKS['scroll_graph'],
                             [explainIDs.GO_UP_PRED_GRAPH + '.n_clicks'],
                             ('', '1234', 0, 0, 0)) == [dash.no_update] * 5

    assert mock_dash_context(CALLBACKS['scroll_graph'],
                             [explainIDs.SELECT_PAGE_PRED_GRAPH_BTN + '.n_clicks'],
                             ('', '1234', 0, 0, 1)) == [dash.no_update] * 5

    with PropertyMocker(explain_pres, 'pred_graph_progression_data', PropertyMock(return_value={'1234': 0})), \
         PropertyMocker(explain_pres, 'kpis_dfs_lengths', PropertyMock(return_value={'1234': 3})), \
         PropertyMocker(explain_pres, 'REC_PER_PAGE', PropertyMock(return_value=1)), \
         patch('gui.presenters.ExplainPresenter.ExplainPresenter.create_pred_graph') as mock_createpredgraph:
        mock_createpredgraph.return_value = 'pred_graph_data'

        assert mock_dash_context(CALLBACKS['scroll_graph'],
                                 [explainIDs.SELECT_PAGE_PRED_GRAPH_BTN + '.n_clicks'],
                                 (2, '1234', 0, 0, 1)) == ['pred_graph_data', '2/3', False, False, '']
        assert mock_dash_context(CALLBACKS['scroll_graph'],
                                 [explainIDs.SELECT_PAGE_PRED_GRAPH_BTN + '.n_clicks'],
                                 (1, '1234', 0, 0, 1)) == ['pred_graph_data', '1/3', False, True, '']
        assert mock_dash_context(CALLBACKS['scroll_graph'],
                                 [explainIDs.SELECT_PAGE_PRED_GRAPH_BTN + '.n_clicks'],
                                 (3, '1234', 0, 0, 1)) == ['pred_graph_data', '3/3', True, False, '']

    with PropertyMocker(explain_pres, 'pred_graph_progression_data', PropertyMock(return_value={'1234': 0})), \
         PropertyMocker(explain_pres, 'kpis_dfs_lengths', PropertyMock(return_value={'1234': 3})), \
         PropertyMocker(explain_pres, 'REC_PER_PAGE', PropertyMock(return_value=1)), \
         patch('gui.presenters.ExplainPresenter.ExplainPresenter.create_pred_graph') as mock_createpredgraph:
        mock_createpredgraph.return_value = 'pred_graph_data'
        assert mock_dash_context(CALLBACKS['scroll_graph'],
                                 [explainIDs.GO_UP_PRED_GRAPH + '.n_clicks'],
                                 ('', '1234', 1, 0, 0)) == ['pred_graph_data', '2/3', False, False, '']
        assert mock_dash_context(CALLBACKS['scroll_graph'],
                                 [explainIDs.GO_DOWN_PRED_GRAPH + '.n_clicks'],
                                 ('', '1234', 0, 1, 0)) == ['pred_graph_data', '1/3', False, True, '']

    with PropertyMocker(explain_pres, 'pred_graph_progression_data', PropertyMock(return_value={'1234': 1})), \
         PropertyMocker(explain_pres, 'kpis_dfs_lengths', PropertyMock(return_value={'1234': 3})), \
         PropertyMocker(explain_pres, 'REC_PER_PAGE', PropertyMock(return_value=1)), \
         patch('gui.presenters.ExplainPresenter.ExplainPresenter.create_pred_graph') as mock_createpredgraph:
        mock_createpredgraph.return_value = 'pred_graph_data'
        assert mock_dash_context(CALLBACKS['scroll_graph'],
                                 [explainIDs.GO_UP_PRED_GRAPH + '.n_clicks'],
                                 ('', '1234', 1, 0, 0)) == ['pred_graph_data', '3/3', True, False, '']
        assert mock_dash_context(CALLBACKS['scroll_graph'],
                                 [explainIDs.GO_DOWN_PRED_GRAPH + '.n_clicks'],
                                 ('', '1234', 0, 1, 0)) == ['pred_graph_data', '2/3', False, False, '']




def test_show_preds_text_format():
    # input_value, user_id, click_data, n_clicks
    assert mock_dash_context(CALLBACKS['show_preds_text_format'],
                             [explainIDs.PREDICTION_SEARCH_GRAPH + '.n_clicks'],
                             ('', '1234', {}, 0)) == [dash.no_update] * 15

    assert mock_dash_context(CALLBACKS['show_preds_text_format'],
                             [explainIDs.PREDICTION_SEARCH_GRAPH + '.n_clicks'],
                             ('', '1234', {}, 1)) == [dash.no_update] * 15

    assert mock_dash_context(CALLBACKS['show_preds_text_format'],
                             [explainIDs.SEARCH_TRACE_ID_INPUT_BTN + '.n_clicks'],
                             ('', '1234', {}, 0)) == [dash.no_update] * 15

    assert mock_dash_context(CALLBACKS['show_preds_text_format'],
                             [explainIDs.SEARCH_TRACE_ID_INPUT_BTN + '.n_clicks'],
                             ('', '1234', {'test': 'test'}, 0)) == [dash.no_update] * 15

    with PropertyMocker(explain_pres, 'explainers', PropertyMock(return_value={'1234': 'test'})):
        with patch('gui.presenters.ExplainPresenter.build_Explainer_from_dict') as mock_build_explainer:
            mock_build_explainer.return_value.check_if_trace_is_valid.return_value = False

            assert mock_dash_context(CALLBACKS['show_preds_text_format'],
                                     [explainIDs.SEARCH_TRACE_ID_INPUT_BTN + '.n_clicks'],
                                     ('input', '1234', {}, 1)) == \
                   [dash.no_update] * 14 + [{explainIDs.SEARCH_TRACE_ID_INPUT: 'The trace inserted does not exists'}]

            assert mock_dash_context(CALLBACKS['show_preds_text_format'],
                                     [explainIDs.SEARCH_TRACE_ID_INPUT_BTN + '.n_clicks'],
                                     ('', '1234', {}, 1)) == \
                   [dash.no_update] * 14 + [{explainIDs.SEARCH_TRACE_ID_INPUT: 'No trace inserted'}]

            mock_build_explainer.return_value.check_if_trace_is_valid.return_value = True
            mock_build_explainer.return_value.get_best_n_scores_by_trace.return_value = {
                'rec': [('act1', 123456), ('act2', 234567), ('act3', 345678)],
                'real': [('act', 123)]
            }
            out = mock_dash_context(CALLBACKS['show_preds_text_format'],
                                    [explainIDs.SEARCH_TRACE_ID_INPUT_BTN + '.n_clicks'],
                                    ('valid_input', '1234', {}, 1))
            expected = ['Recommendations for valid_input',
                        'Current activity: act',
                        'Expected KPI: 123',
                        [dash.html.Td('act1'), dash.html.Td(123456)],
                        [dash.html.Td('act2'), dash.html.Td(234567)],
                        [dash.html.Td('act3'), dash.html.Td(345678)],
                        'expl_table_selectable_row',
                        'expl_table_selectable_row',
                        'expl_table_selectable_row',
                        'valid_input',
                        True,
                        explain_pres.DEFAULT_EXPL_QNT,
                        False,
                        False,
                        {}]

            # object assert == fails if the objects are not the same instance (dash.html.Td()), so I split the list and
            # compare separately

            # comparing the singular values for every object
            for out_val, exp_val in zip(out[3:5], expected[3:5]):
                assert out_val[0].__dict__ == out_val[0].__dict__
                assert out_val[1].__dict__ == out_val[1].__dict__

            assert out[0:2] + out[6:] == expected[0:2] + expected[6:]


def test_select_trace_activity_to_explain():
    assert mock_dash_context(CALLBACKS['select_trace_activity_to_explain'],
                             [explainIDs.FIRST_ROW_PRED_TABLE + '.n_clicks'],
                             (0, 1, 1, [], [], [], 'trace', '1234')) == [dash.no_update] * 8
    assert mock_dash_context(CALLBACKS['select_trace_activity_to_explain'],
                             [explainIDs.SECOND_ROW_PRED_TABLE + '.n_clicks'],
                             (1, 0, 1, [], [], [], 'trace', '1234')) == [dash.no_update] * 8
    assert mock_dash_context(CALLBACKS['select_trace_activity_to_explain'],
                             [explainIDs.THIRD_ROW_PRED_TABLE + '.n_clicks'],
                             (1, 1, 0, [], [], [], 'trace', '1234')) == [dash.no_update] * 8

    with PropertyMocker(explain_pres, 'explainers', PropertyMock(return_value={'1234': 'test'})):
        with patch('gui.presenters.ExplainPresenter.build_Explainer_from_dict') as mock_build_explainer, \
                patch(
                    'gui.presenters.ExplainPresenter.ExplainPresenter.create_explanation_graph'
                ) as mock_createexplgraph:
            mock_build_explainer.return_value.check_if_explanations_exists.return_value = False
            assert mock_dash_context(CALLBACKS['select_trace_activity_to_explain'],
                                     [explainIDs.FIRST_ROW_PRED_TABLE + '.n_clicks'],
                                     (1, 0, 0, [{'props': {'children': 'ACT1'}}], [], [], 'trace', '1234')) == \
                   ['ACT1', 'selected_expl_table_row', 'expl_table_selectable_row', 'expl_table_selectable_row',
                    dash.no_update, True, False, []]

            mock_build_explainer.return_value.check_if_explanations_exists.return_value = True
            mock_build_explainer.return_value.generate_explanations_dataframe.return_value = [1, 2, 3], [4, 5, 6]
            mock_createexplgraph.return_value = 'graph_result'
            assert mock_dash_context(CALLBACKS['select_trace_activity_to_explain'],
                                     [explainIDs.FIRST_ROW_PRED_TABLE + '.n_clicks'],
                                     (1, 0, 0, [{'props': {'children': 'ACT1'}}], [], [], 'trace', '1234')) == \
                   ['ACT1', 'selected_expl_table_row', 'expl_table_selectable_row', 'expl_table_selectable_row',
                    'graph_result', False, True, []]
            mock_createexplgraph.assert_called_with(([1, 2, 3], [4, 5, 6]), explain_pres.DEFAULT_EXPL_QNT)


def test_change_quantity_explanations():
    with pytest.raises(dash.exceptions.PreventUpdate):
        assert CALLBACKS['change_quantity_explanations']('trace', 'act_to_explain', '1234', None, 0)

        with PropertyMocker(explain_pres, 'explainers', PropertyMock(return_value={'1234': 'test'})):
            with patch('gui.presenters.ExplainPresenter.build_Explainer_from_dict') as mock_build_explainer:
                mock_build_explainer.return_value.generate_explanations_dataframe.return_value = None, None
                assert CALLBACKS['change_quantity_explanations']('trace', 'act_to_explain', '1234', None, 5)
                mock_build_explainer.return_value.generate_explanations_dataframe.return_value = 'NotNone', None
                assert CALLBACKS['change_quantity_explanations']('trace', 'act_to_explain', '1234', None, 5)
                mock_build_explainer.return_value.generate_explanations_dataframe.return_value = None, 'NotNone'
                assert CALLBACKS['change_quantity_explanations']('trace', 'act_to_explain', '1234', None, 5)

    with PropertyMocker(explain_pres, 'explainers', PropertyMock(return_value={'1234': 'test'})):
        with patch('gui.presenters.ExplainPresenter.build_Explainer_from_dict') as mock_build_explainer, \
             patch(
                 'gui.presenters.ExplainPresenter.ExplainPresenter.create_explanation_graph'
             ) as mock_createexplgraph:
            mock_createexplgraph.return_value = 'graph_result'
            mock_build_explainer.return_value.generate_explanations_dataframe.return_value = [1, 2, 3], [4, 5, 6]
            assert CALLBACKS['change_quantity_explanations']('trace', 'act_to_explain', '1234',
                                                             'EXPL_SORT_METHOD', 5) == 'graph_result'
            mock_createexplgraph.assert_called_with([1, 2, 3], [4, 5, 6], 5)
            with pytest.raises(dash.exceptions.PreventUpdate):
                CALLBACKS['change_quantity_explanations']('trace',
                                                          'act_to_explain', '1234', explain_pres.DEFAULT_EXPL_QNT)



def test_calculate_and_visualize_shap_by_trace():
    # act_to_explain, trace_id, expl_qnt, user_id, n_clicks

    assert CALLBACKS['calculate_and_visualize_shap_by_trace']('ACT', 'trace', 'expl_qnt', '1234', 0) == \
           [dash.no_update] * 3

    with PropertyMocker(explain_pres, 'explainers', PropertyMock(return_value={'1234': 'test'})):
        with patch('gui.presenters.ExplainPresenter.build_Explainer_from_dict') as mock_build_explainer, \
             patch(
                 'gui.presenters.ExplainPresenter.ExplainPresenter.create_explanation_graph'
             ) as mock_createexplgraph:
            mock_createexplgraph.return_value = 'graph_result'
            mock_build_explainer.return_value.check_if_explanations_exists.return_value = True
            assert CALLBACKS['calculate_and_visualize_shap_by_trace']('ACT', 'trace', 'expl_qnt', '1234', 1) == \
                   [dash.no_update] * 3

            mock_build_explainer.return_value.check_if_explanations_exists.return_value = False
            mock_build_explainer.return_value.generate_explanations_dataframe.return_value = [1, 2, 3], [4, 5, 6]
            assert CALLBACKS['calculate_and_visualize_shap_by_trace']('ACT', 'trace', 5, '1234', 1) == \
                ['graph_result', False, True]



