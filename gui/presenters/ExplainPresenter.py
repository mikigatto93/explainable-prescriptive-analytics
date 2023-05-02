import json
import math
import os
import time

import dash
import diskcache
import pandas as pd
from dash import ClientsideFunction

from app import app
from dash_extensions.enrich import Input, Output, State
from dash_extensions.enrich import html
import plotly.graph_objects as go
import plotly.express as px

from gui.model import Experiment
import gui.model.DiskDict as diskdict
from gui.model.Explainer import Explainer, build_Explainer_from_dict, order_by_delta_max, \
    order_by_delta_min, order_by_max_value, order_by_min_value
from gui.presenters.Presenter import Presenter


class ExplainPresenter(Presenter):
    def __init__(self, views):
        super().__init__(views)
        self.REC_PER_PAGE = 15
        self.DEFAULT_EXPL_QNT = 4
        self.explainers = diskdict.DiskDict(os.path.join(os.getcwd(), 'gui_data', 'explain'), 'explainers')
        self.kpis_dfs = diskdict.DiskDict(os.path.join(os.getcwd(), 'gui_data', 'explain'), 'kpis_dfs')
        self.kpis_dfs_lengths = diskdict.DiskDict(os.path.join(os.getcwd(), 'gui_data', 'explain'), 'kpis_dfs_lengths')
        self.pred_graph_progression_data = diskdict.DiskDict(os.path.join(os.getcwd(), 'gui_data', 'explain'),
                                                             'pred_graph_progression_data')

    def clear_user_data(self, user_id):
        if self.explainers.exists(user_id):
            self.explainers.delete(user_id)
            print('deleted explainer')

        if self.kpis_dfs_lengths.exists(user_id):
            self.kpis_dfs_lengths.delete(user_id)
            print('deleted kpi_df length')

        if self.pred_graph_progression_data.exists(user_id):
            self.pred_graph_progression_data.delete(user_id)
            print('deleted pred_graph_progression data')

        if self.kpis_dfs.exists(user_id):
            path = self.kpis_dfs[user_id]
            try:
                os.remove(path)
            except:
                print('An error occurred during file deletion: ({})'.format(path))
            self.kpis_dfs.delete(user_id)
            print('deleted kpis df')

    def create_pred_graph(self, user_id):
        pred_graph_progression_data = self.pred_graph_progression_data[user_id]
        kpis_df = pd.read_parquet(self.kpis_dfs[user_id])

        df_slice = kpis_df[
            slice(max(self.REC_PER_PAGE * pred_graph_progression_data, 0),
                  min(self.REC_PER_PAGE * (pred_graph_progression_data + 1),
                      self.kpis_dfs_lengths[user_id]))]
        df_slice = df_slice.iloc[::-1]  # reverse dataframe so it can be watched from top to bottom

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                name='Following recommendation',
                y=df_slice.index,
                x=df_slice['Following recommendation'],
                marker_color='darkgreen',
                orientation='h',
            )
        )

        fig.add_trace(
            go.Bar(
                name='Current Value',
                y=df_slice.index,
                x=df_slice['Current Value'],
                marker_color='darkred',
                orientation='h',
            )
        )

        fig.update_yaxes(tickmode='linear')

        fig.update_layout(
            # yaxis=dict(
            #     tickmode='array', tickvals=list(df_slice.index),
            #     ticktext=['{}'.format(i)
            #               for i in list(df_slice.index)]
            # ),
            title='Select the desired trace',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(
                r=10,
            ),
            height=450,
        )

        return fig

    def create_explanation_graph(self, expl_df, qnt, order=None):

        if order == 'Delta from maximum':
            expl_df = order_by_delta_max(expl_df, 'explanations', 'groundtruth')
        elif order == 'Delta from minimum':
            expl_df = order_by_delta_min(expl_df, 'explanations', 'groundtruth')

        expl_slice = expl_df[slice(0, qnt)]
        expl_slice = expl_slice.iloc[::-1]  # reverse dataframe so it can be watched from top to bottom

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                name='Following recommendation',
                y=list(expl_slice.index),
                x=list(expl_slice['explanations']),
                marker_color='darkgreen',
                orientation='h',
            )
        )

        fig.add_trace(
            go.Bar(
                name='Current Value',
                y=list(expl_slice.index),
                x=list(expl_slice['groundtruth']),
                marker_color='darkred',
                orientation='h',
            )
        )
        return fig

    def register_callbacks(self):

        @app.callback([Output(e.value, 'children') for e in self.views['explain'].ERROR_IDs],
                      Input(self.views['base'].IDs.ERRORS_MANAGER_STORE_EXPLAIN, 'data'),
                      prevent_initial_call=True)
        def show_error_explain(error_data):
            # l = [Output(e.value, 'children') for e in self.views['train'].ERROR_IDs]
            # print(l)
            if error_data is not None:
                output_values = []
                for e in self.views['explain'].ERROR_IDs:
                    err_id = str(e.value)
                    elem_id = err_id.replace('_error', '')
                    if elem_id in error_data:
                        output_values.append(error_data[elem_id])
                    else:
                        output_values.append('')
                return output_values
            else:
                raise dash.exceptions.PreventUpdate

        @app.callback([Output(self.views['explain'].IDs.PREDICTION_SEARCH_GRAPH, 'figure'),
                       Output(self.views['explain'].IDs.RECOMMENDATION_GRAPH_PAGING_INFO, 'children'),
                       Output(self.views['explain'].IDs.CHANGE_ORDER_EXPL_DROPDOWN, 'value')],
                      [State(self.views['base'].IDs.EXPERIMENT_DATA_STORE, 'data'),
                       State(self.views['base'].IDs.USER_ID, 'data'),
                       State(self.views['base'].IDs.EXPL_SORT_METHOD, 'data')],
                      Input(self.views['base'].IDs.LOCATION_URL, 'pathname'))
        def show_prediction_graph(ex_info_data, user_id, expl_sort_method, url):
            if url == self.views['explain'].pathname:

                # ex_info_data = {"ex_name": "test_xes_fin", "kpi": "Total time", "id": "case:concept:name",
                #                 "timestamp": "time:timestamp", "activity": "concept:name", "resource": "org:resource",
                #                 "act_to_opt": None, "out_thrs": 0.02,
                #                 "creation_timestamp": "15-02-2023_20-28-46_433853+0000",
                #                 "pred_column": "remaining_time"}

                # ex_info_data = {"ex_name": "vinst_test_time1", "kpi": "Total time", "id": "SR_Number",
                #                 "timestamp": "Change_Date+Time",
                #                 "activity": "ACTIVITY", "resource": None, "act_to_opt": None, "out_thrs": 0.02,
                #                 "creation_timestamp": "21-02-2023_16-36-56_524573+0000",
                #                 "pred_column": "remaining_time"}

                ex_info_data = {"ex_name": "test-exp3", "kpi": "Total time", "id": "SR_Number",
                                "timestamp": "Change_Date+Time", "activity": "ACTIVITY", "resource": None,
                                "act_to_opt": None, "out_thrs": 0,
                                "creation_timestamp": "15-04-2023_08-34-13_272399+0000",
                                "pred_column": "remaining_time"}

                # ex_info_data = {"ex_name": "test_bac5", "kpi": "Minimize activity occurrence", "id": "REQUEST_ID",
                #  "timestamp": "START_DATE", "activity": "ACTIVITY", "resource": "CE_UO",
                #  "act_to_opt": "Pending Liquidation Request", "out_thrs": 0.02,
                #  "creation_timestamp": "20-02-2023_20-13-27_362264+0000", "pred_column": "independent_activity"}

                if ex_info_data:
                    # explainer = Explainer(Experiment.build_experiment_from_dict(json.loads(ex_info_data)))
                    explainer = Explainer(Experiment.build_experiment_from_dict(ex_info_data))
                    print(user_id)
                    self.explainers[user_id] = explainer.to_dict()

                    kpis_dict = explainer.calculate_best_scores()
                    kpis_df_temp = pd.DataFrame.from_dict(kpis_dict,
                                                          orient='index',
                                                          columns=['Following recommendation', 'Current Value'])
                    kpi_df_length = len(kpis_df_temp.index)
                    self.kpis_dfs_lengths[user_id] = kpi_df_length

                    kpi_df_path = diskdict.get_df_path('kpi_df', user_id, ext='pqt')
                    kpis_df_temp.to_parquet(kpi_df_path)
                    self.kpis_dfs[user_id] = kpi_df_path

                    # mask = kpis_df_temp['Current Value'] > kpis_df_temp['Following recommendation']
                    # kpis_df1 = kpis_df_temp[mask]  # current > following
                    # kpis_df2 = kpis_df_temp[~mask]  # current <= following
                    #
                    # new_df = pd.concat([kpis_df1, kpis_df2])
                    # self.kpis_dfs[user_id] = {'df': new_df,
                    #                           'length': len(new_df.index)}

                    # self.kpis_dfs[user_id] = {'df': kpis_df_temp,
                    #                           'length': len(kpis_df_temp.index)}

                    # self.kpis_df_len = len(self.kpis_df.index)

                    # print('Good traces / Total traces ratio: {}'.format(len(kpis_df1.index) / self.kpis_df_len))

                    self.pred_graph_progression_data[user_id] = 0

                    return [self.create_pred_graph(user_id),
                            '{}/{}'.format(1, math.ceil(kpi_df_length / self.REC_PER_PAGE)), expl_sort_method]

                else:
                    # TODO: ERROR
                    return [dash.no_update] * 3
            else:
                return [dash.no_update] * 3

        @app.callback(Output(self.views['explain'].IDs.PREDICTION_SEARCH_GRAPH, 'figure'),
                      [State(self.views['base'].IDs.USER_ID, 'data'),
                       State(self.views['explain'].IDs.CHANGE_ORDER_PRED_DROPDOWN, 'value')],
                      Input(self.views['explain'].IDs.CHANGE_ORDER_PRED_BTN, 'n_clicks'),
                      prevent_initial_call=True)
        def change_pred_graph_order(user_id, pred_sort_method, n_clicks):
            if n_clicks > 0 and pred_sort_method is not None:
                kpis_df = pd.read_parquet(self.kpis_dfs[user_id])

                if pred_sort_method == 'Minimize':
                    kpis_df = order_by_min_value(kpis_df, 'Following recommendation')
                elif pred_sort_method == 'Maximize':
                    kpis_df = order_by_max_value(kpis_df, 'Following recommendation')
                elif pred_sort_method == 'Delta from maximum':
                    kpis_df = order_by_delta_max(kpis_df, 'Following recommendation', 'Current Value')
                elif pred_sort_method == 'Delta from minimum':
                    kpis_df = order_by_delta_min(kpis_df, 'Following recommendation', 'Current Value')

                kpi_df_path = diskdict.get_df_path('kpi_df', user_id, ext='pqt')
                kpis_df.to_parquet(kpi_df_path)
                self.kpis_dfs[user_id] = kpi_df_path

                return self.create_pred_graph(user_id)
            else:
                raise dash.exceptions.PreventUpdate

        @app.callback([Output(self.views['explain'].IDs.PREDICTION_SEARCH_GRAPH, 'figure'),
                       Output(self.views['explain'].IDs.RECOMMENDATION_GRAPH_PAGING_INFO, 'children'),
                       Output(self.views['explain'].IDs.GO_UP_PRED_GRAPH, 'disabled'),
                       Output(self.views['explain'].IDs.GO_DOWN_PRED_GRAPH, 'disabled'),
                       Output(self.views['explain'].IDs.SELECT_PAGE_PRED_GRAPH_INPUT, 'value')],
                      [State(self.views['explain'].IDs.SELECT_PAGE_PRED_GRAPH_INPUT, 'value'),
                       State(self.views['base'].IDs.USER_ID, 'data')],
                      [Input(self.views['explain'].IDs.GO_UP_PRED_GRAPH, 'n_clicks'),
                       Input(self.views['explain'].IDs.GO_DOWN_PRED_GRAPH, 'n_clicks'),
                       Input(self.views['explain'].IDs.SELECT_PAGE_PRED_GRAPH_BTN, 'n_clicks')],
                      prevent_initial_call=True)
        def scroll_graph(page_value_sel, user_id, n_clicks_up, n_clicks_down, n_clicks_sel_page):
            button_id = dash.ctx.triggered_id
            # print(self.pred_graph_progression)
            if button_id == self.views['explain'].IDs.GO_UP_PRED_GRAPH and n_clicks_up > 0:
                new_pred_graph_progression_data = self.pred_graph_progression_data[user_id]
                new_pred_graph_progression_data += 1
                self.pred_graph_progression_data[user_id] = new_pred_graph_progression_data
                max_page = math.ceil(self.kpis_dfs_lengths[user_id] / self.REC_PER_PAGE)
                return [
                    self.create_pred_graph(user_id),
                    '{}/{}'.format(new_pred_graph_progression_data + 1, max_page),
                    new_pred_graph_progression_data == (max_page - 1),
                    False,
                    ''
                ]

            elif button_id == self.views['explain'].IDs.GO_DOWN_PRED_GRAPH and n_clicks_down > 0:
                new_pred_graph_progression_data = self.pred_graph_progression_data[user_id]
                new_pred_graph_progression_data -= 1
                self.pred_graph_progression_data[user_id] = new_pred_graph_progression_data
                return [
                    self.create_pred_graph(user_id),
                    '{}/{}'.format(new_pred_graph_progression_data + 1,
                                   math.ceil(self.kpis_dfs_lengths[user_id] / self.REC_PER_PAGE)),
                    False,
                    new_pred_graph_progression_data == 0,
                    ''
                ]

            elif button_id == self.views['explain'].IDs.SELECT_PAGE_PRED_GRAPH_BTN and n_clicks_sel_page > 0:
                if page_value_sel:
                    max_page = math.ceil(self.kpis_dfs_lengths[user_id] / self.REC_PER_PAGE)
                    page_value_sel = int(max(1, min(page_value_sel, max_page)))
                    self.pred_graph_progression_data[user_id] = page_value_sel - 1
                    return [
                        self.create_pred_graph(user_id),
                        '{}/{}'.format(page_value_sel,
                                       math.ceil(self.kpis_dfs_lengths[user_id] / self.REC_PER_PAGE)),
                        (page_value_sel - 1) == (max_page - 1),
                        (page_value_sel - 1) == 0,
                        ''
                    ]
                else:
                    return [dash.no_update] * 5

            else:
                return [dash.no_update] * 5

        @app.callback([Output(self.views['explain'].IDs.CURRENT_TRACE_ID, 'children'),
                       Output(self.views['explain'].IDs.CURRENT_ACTIVITY, 'children'),
                       Output(self.views['explain'].IDs.CURRENT_EXPECTED_KPI, 'children'),
                       Output(self.views['explain'].IDs.FIRST_ROW_PRED_TABLE, 'children'),
                       Output(self.views['explain'].IDs.SECOND_ROW_PRED_TABLE, 'children'),
                       Output(self.views['explain'].IDs.THIRD_ROW_PRED_TABLE, 'children'),
                       Output(self.views['explain'].IDs.FIRST_ROW_PRED_TABLE, 'className'),
                       Output(self.views['explain'].IDs.SECOND_ROW_PRED_TABLE, 'className'),
                       Output(self.views['explain'].IDs.THIRD_ROW_PRED_TABLE, 'className'),
                       Output(self.views['base'].IDs.TRACE_ID_TO_EXPLAIN_STORE, 'data'),
                       Output(self.views['explain'].IDs.VISUALIZE_EXPL_FADE, 'is_in'),
                       Output(self.views['explain'].IDs.EXPLANATION_QUANTITY_SLIDER, 'value'),
                       Output(self.views['explain'].IDs.GENERATE_EXPL_BTN_FADE, 'is_in'),
                       Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_GRAPH_FADE, 'is_in'),
                       Output(self.views['base'].IDs.ERRORS_MANAGER_STORE_EXPLAIN, 'data')],
                      [State(self.views['explain'].IDs.SEARCH_TRACE_ID_INPUT, 'value'),
                       State(self.views['base'].IDs.USER_ID, 'data')],
                      [Input(self.views['explain'].IDs.PREDICTION_SEARCH_GRAPH, 'clickData'),
                       Input(self.views['explain'].IDs.SEARCH_TRACE_ID_INPUT_BTN, 'n_clicks')],
                      prevent_initial_call=True)
        def show_preds_text_format(input_value, user_id, click_data, n_clicks):
            CSS_BASE_ROW_CLASS_NAME = 'expl_table_selectable_row'
            graph_clicked = dash.ctx.triggered_id == self.views['explain'].IDs.PREDICTION_SEARCH_GRAPH
            search_btn_clicked = dash.ctx.triggered_id == self.views['explain'].IDs.SEARCH_TRACE_ID_INPUT_BTN
            error_data = {}

            if (graph_clicked and click_data) or (search_btn_clicked and n_clicks > 0):
                explainer = build_Explainer_from_dict(self.explainers[user_id])
                if graph_clicked:
                    trace_id = click_data['points'][0]['y']
                elif search_btn_clicked and input_value != '':
                    if explainer.check_if_trace_is_valid(input_value):
                        trace_id = input_value
                    else:
                        error_data[self.views['explain'].IDs.SEARCH_TRACE_ID_INPUT] = \
                            'The trace inserted does not exists'
                elif search_btn_clicked and input_value == '':
                    error_data[self.views['explain'].IDs.SEARCH_TRACE_ID_INPUT] = \
                        'No trace inserted'

                if not error_data:
                    pred_info = explainer.get_best_n_scores_by_trace(trace_id, 3)

                    rec_act = [t[0] for t in pred_info['rec']]
                    rec_values = [t[1] for t in pred_info['rec']]
                    real_act = pred_info['real'][0][0]
                    real_val = pred_info['real'][0][1]

                    return [
                        'Recommendations for {}'.format(trace_id),
                        'Current activity: {}'.format(real_act),
                        'Expected KPI: {}'.format(real_val),
                        [html.Td(rec_act[0]), html.Td(rec_values[0])],
                        [html.Td(rec_act[1]), html.Td(rec_values[1])] if len(rec_act) > 1 else [],
                        [html.Td(rec_act[2]), html.Td(rec_values[2])] if len(rec_act) > 2 else [],
                        CSS_BASE_ROW_CLASS_NAME,
                        CSS_BASE_ROW_CLASS_NAME,
                        CSS_BASE_ROW_CLASS_NAME,
                        trace_id,
                        True,
                        self.DEFAULT_EXPL_QNT,
                        False,
                        False,
                        error_data
                    ]
                else:
                    return [dash.no_update] * 14 + [error_data]
            else:
                return [dash.no_update] * 15

        app.clientside_callback(
            ClientsideFunction(
                namespace='clientside',
                function_name='slider_value_display_csc'
            ),
            Output(self.views['explain'].IDs.QNT_EXPL_SLIDER_VALUE_LABEL, 'children'),
            Input(self.views['explain'].IDs.EXPLANATION_QUANTITY_SLIDER, 'value')
        )

        @app.callback([Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_GRAPH, 'figure'),
                       Output(self.views['base'].IDs.EXPL_SORT_METHOD, 'data')],
                      [State(self.views['base'].IDs.TRACE_ID_TO_EXPLAIN_STORE, 'data'),
                       State(self.views['base'].IDs.ACT_TO_EXPLAIN_STORE, 'data'),
                       State(self.views['base'].IDs.USER_ID, 'data'),
                       State(self.views['base'].IDs.EXPLANATION_QUANTITY_STORE, 'data'),
                       State(self.views['explain'].IDs.CHANGE_ORDER_EXPL_DROPDOWN, 'value')],
                      Input(self.views['explain'].IDs.CHANGE_ORDER_EXPL_BTN, 'n_clicks'),
                      prevent_initial_call=True)
        def change_expl_graph_order(trace_id, act_to_explain, user_id, expl_qnt, expl_sort_method, n_clicks):
            if n_clicks > 0 and expl_sort_method is not None:

                if expl_qnt is None:
                    expl_qnt = self.DEFAULT_EXPL_QNT
                else:
                    expl_qnt = int(expl_qnt)

                expl_df = build_Explainer_from_dict(
                    self.explainers[user_id]
                ).generate_explanations_dataframe(trace_id, act_to_explain)
                if expl_df is not None:
                    return [self.create_explanation_graph(expl_df, expl_qnt, order=expl_sort_method), expl_sort_method]
                else:
                    return [dash.no_update] * 2
            else:
                return [dash.no_update] * 2

        @app.callback([Output(self.views['base'].IDs.ACT_TO_EXPLAIN_STORE, 'data'),
                       Output(self.views['explain'].IDs.FIRST_ROW_PRED_TABLE, 'className'),
                       Output(self.views['explain'].IDs.SECOND_ROW_PRED_TABLE, 'className'),
                       Output(self.views['explain'].IDs.THIRD_ROW_PRED_TABLE, 'className'),
                       Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_GRAPH, 'figure'),
                       Output(self.views['explain'].IDs.GENERATE_EXPL_BTN_FADE, 'is_in'),
                       Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_GRAPH_FADE, 'is_in'),
                       Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_DETAILS, 'children')],
                      [Input(self.views['explain'].IDs.FIRST_ROW_PRED_TABLE, 'n_clicks'),
                       Input(self.views['explain'].IDs.SECOND_ROW_PRED_TABLE, 'n_clicks'),
                       Input(self.views['explain'].IDs.THIRD_ROW_PRED_TABLE, 'n_clicks')],
                      [State(self.views['explain'].IDs.FIRST_ROW_PRED_TABLE, 'children'),
                       State(self.views['explain'].IDs.SECOND_ROW_PRED_TABLE, 'children'),
                       State(self.views['explain'].IDs.THIRD_ROW_PRED_TABLE, 'children'),
                       State(self.views['base'].IDs.TRACE_ID_TO_EXPLAIN_STORE, 'data'),
                       State(self.views['base'].IDs.USER_ID, 'data')],
                      prevent_initial_call=True)
        def select_trace_activity_to_explain(n_clicks1, n_clicks2, n_clicks3, ch1, ch2, ch3, trace_id, user_id):
            CSS_SELECTED_ROW_CLASS_NAME = 'selected_expl_table_row'
            CSS_BASE_ROW_CLASS_NAME = 'expl_table_selectable_row'
            row1_clicked = dash.ctx.triggered_id == self.views['explain'].IDs.FIRST_ROW_PRED_TABLE and n_clicks1 > 0
            row2_clicked = dash.ctx.triggered_id == self.views['explain'].IDs.SECOND_ROW_PRED_TABLE and n_clicks2 > 0
            row3_clicked = dash.ctx.triggered_id == self.views['explain'].IDs.THIRD_ROW_PRED_TABLE and n_clicks3 > 0

            if row1_clicked:
                act_to_explain = (ch1[0]['props']['children'])
                class_list_to_return = [act_to_explain,
                                        CSS_SELECTED_ROW_CLASS_NAME, CSS_BASE_ROW_CLASS_NAME, CSS_BASE_ROW_CLASS_NAME]
            elif row2_clicked:
                act_to_explain = (ch2[0]['props']['children'])
                class_list_to_return = [act_to_explain,
                                        CSS_BASE_ROW_CLASS_NAME, CSS_SELECTED_ROW_CLASS_NAME, CSS_BASE_ROW_CLASS_NAME]
            elif row3_clicked:
                act_to_explain = (ch3[0]['props']['children'])
                class_list_to_return = [act_to_explain,
                                        CSS_BASE_ROW_CLASS_NAME, CSS_BASE_ROW_CLASS_NAME, CSS_SELECTED_ROW_CLASS_NAME]
            else:
                return [dash.no_update] * 8
            explainer = build_Explainer_from_dict(self.explainers[user_id])

            if explainer.check_if_groundtruth_exists(trace_id) and \
                    explainer.check_if_explanations_exists(trace_id, act_to_explain):
                print('Explanations found, visualizing shap values for '
                      'trace: {}, activity: {}'.format(trace_id, act_to_explain))

                expl_df = explainer.generate_explanations_dataframe(trace_id, act_to_explain)
                print(expl_df)
                return class_list_to_return + [self.create_explanation_graph(expl_df, self.DEFAULT_EXPL_QNT),
                                               False, True, []]
            else:
                print('Not found shap values for trace: {}, activity: {}'.format(trace_id, act_to_explain))
                return class_list_to_return + [dash.no_update, True, False, []]

        @app.callback([Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_GRAPH, 'figure'),
                       Output(self.views['base'].IDs.EXPLANATION_QUANTITY_STORE, 'data')],
                      [State(self.views['base'].IDs.TRACE_ID_TO_EXPLAIN_STORE, 'data'),
                       State(self.views['base'].IDs.ACT_TO_EXPLAIN_STORE, 'data'),
                       State(self.views['base'].IDs.USER_ID, 'data'),
                       State(self.views['base'].IDs.EXPL_SORT_METHOD, 'data')],
                      Input(self.views['explain'].IDs.EXPLANATION_QUANTITY_SLIDER, 'value'),
                      prevent_initial_call=True)
        def change_quantity_explanations(trace_id, act_to_explain, user_id, expl_sort_method, value):
            if value:
                expl_df = build_Explainer_from_dict(
                    self.explainers[user_id]
                ).generate_explanations_dataframe(trace_id, act_to_explain)
                if expl_df is not None:
                    return [self.create_explanation_graph(expl_df, int(value), order=expl_sort_method), int(value)]
                else:
                    return [dash.no_update] * 2
            else:
                return [dash.no_update] * 2

        @app.callback(
            output=[Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_GRAPH, 'figure'),
                    Output(self.views['explain'].IDs.GENERATE_EXPL_BTN_FADE, 'is_in'),
                    Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_GRAPH_FADE, 'is_in'),
                    Output(self.views['explain'].IDs.CHANGE_ORDER_EXPL_DROPDOWN, 'value'),
                    Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_DETAILS, 'children')],
            inputs=[State(self.views['base'].IDs.ACT_TO_EXPLAIN_STORE, 'data'),
                    State(self.views['base'].IDs.TRACE_ID_TO_EXPLAIN_STORE, 'data'),
                    State(self.views['explain'].IDs.EXPLANATION_QUANTITY_SLIDER, 'value'),
                    State(self.views['base'].IDs.USER_ID, 'data'),
                    State(self.views['base'].IDs.EXPL_SORT_METHOD, 'data'),
                    Input(self.views['explain'].IDs.GENERATE_EXPL_BTN, 'n_clicks')],
            background=True,
            prevent_initial_call=True,
            running=[
                # (Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_GRAPH_FADE, 'is_in'), False, True),
                (Output(self.views['explain'].IDs.GENERATE_EXPL_SPINNER, 'style'),
                 {'display': 'inline'}, {'display': 'none'}),
                (Output(self.views['explain'].IDs.GENERATE_EXPL_BTN, 'disabled'), True, False),
            ]
        )
        def calculate_and_visualize_shap_by_trace(act_to_explain, trace_id, expl_qnt, user_id,
                                                  expl_sort_method, n_clicks):
            if n_clicks > 0:
                explainer = build_Explainer_from_dict(self.explainers[user_id])
                if not explainer.check_if_explanations_exists(trace_id, act_to_explain):
                    print('Calculating shap values for trace: {}, activity: {}'.format(trace_id, act_to_explain))
                    explainer.calculate_explanation(trace_id,
                                                    act_to_explain,
                                                    generate_gt=not explainer.check_if_groundtruth_exists(trace_id))

                    expl_df = explainer.generate_explanations_dataframe(trace_id, act_to_explain)
                    print(expl_df)
                    return [self.create_explanation_graph(expl_df, expl_qnt if expl_qnt else self.DEFAULT_EXPL_QNT,
                                                          order=expl_sort_method),
                            False, True, expl_sort_method, []]
                else:
                    return [dash.no_update] * 5
            else:
                return [dash.no_update] * 5

        @app.callback(Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_DETAILS, 'children'),
                      [State(self.views['base'].IDs.ACT_TO_EXPLAIN_STORE, 'data'),
                       State(self.views['base'].IDs.TRACE_ID_TO_EXPLAIN_STORE, 'data'),
                       State(self.views['base'].IDs.USER_ID, 'data')],
                      Input(self.views['explain'].IDs.VISUALIZE_EXPLANATION_GRAPH, 'clickData'))
        def show_explanation_details_on_click(act_to_explain, trace_id, user_id, click_data):
            print(click_data)

            explainer = build_Explainer_from_dict(self.explainers[user_id])
            expl_df = explainer.generate_explanations_dataframe(trace_id, act_to_explain)
            if expl_df is not None:
                expl_var = click_data['points'][0]['y']
                return explainer.generate_explanation_details(trace_id, act_to_explain, expl_df, expl_var)
            else:
                raise dash.exceptions.PreventUpdate
