import json
import math
import time

import dash
import pandas as pd
from dash import ClientsideFunction

from app import app
from dash_extensions.enrich import Input, Output, State
from dash_extensions.enrich import html
import plotly.graph_objects as go
import plotly.express as px

from gui.model import Experiment
from gui.model.Explainer import Explainer
from gui.presenters.Presenter import Presenter


class ExplainPresenter(Presenter):
    def __init__(self, views):
        super().__init__(views)
        self.REC_PER_PAGE = 15
        self.DEFAULT_EXPL_QNT = 4
        self.explainer = None
        self.kpis_df = None
        self.kpis_df_len = None
        self.pred_graph_progression = 0

    def __create_pred_graph(self):
        # print(max(self.REC_PER_PAGE * self.pred_graph_progression, 0))
        # print('__')
        # print(min(self.REC_PER_PAGE * (self.pred_graph_progression + 1), self.kpis_df_len))
        df_slice = self.kpis_df[slice(max(self.REC_PER_PAGE * self.pred_graph_progression, 0),
                                      min(self.REC_PER_PAGE * (self.pred_graph_progression + 1), self.kpis_df_len))]

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

    def __create_explanation_graph(self, gt, expl, qnt):
        gt_slice = gt[slice(0, qnt)]
        expl_slice = expl[slice(0, qnt)]
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                name='Following recommendation',
                y=list(expl_slice.index),
                x=list(expl_slice.array),
                marker_color='darkgreen',
                orientation='h',
            )
        )

        fig.add_trace(
            go.Bar(
                name='Current Value',
                y=list(gt_slice.index),
                x=list(gt_slice.array),
                marker_color='darkred',
                orientation='h',
            )
        )

        # fig.update_yaxes(tickmode='linear')
        return fig

    def register_callbacks(self):

        @app.callback([Output(self.views['explain'].IDs.PREDICTION_SEARCH_GRAPH, 'figure'),
                       Output(self.views['explain'].IDs.RECOMMANDATION_GRAPH_PAGING_INFO, 'children')],
                      State(self.views['base'].IDs.EXPERIMENT_DATA_STORE, 'data'),
                      Input(self.views['base'].IDs.LOCATION_URL, 'pathname'))
        def show_prediction_graph(ex_info_data, url):
            if url == self.views['explain'].pathname:

                # ex_info_data = {"ex_name": "test1", "kpi": "Total time", "id": "SR_Number",
                #                 "timestamp": "Change_Date+Time", "activity": "ACTIVITY",
                #                 "resource": None, "act_to_opt": "Involved_ST", "out_thrs": 0.03,
                #                 "pred_column": "remaining_time"}

                if ex_info_data:
                    self.explainer = Explainer(Experiment.build_experiment_from_dict(json.loads(ex_info_data)))
                    # self.explainer = Explainer(Experiment.build_experiment_from_dict(ex_info_data))
                    kpis_dict = self.explainer.calculate_best_scores()
                    kpis_df_temp = pd.DataFrame.from_dict(kpis_dict,
                                                          orient='index',
                                                          columns=['Following recommendation', 'Current Value'])
                    # TODO: TEST THIS "ORDERING" FUNCTION
                    mask = kpis_df_temp['Current Value'] > kpis_df_temp['Following recommendation']
                    kpis_df1 = kpis_df_temp[mask]  # current > following
                    kpis_df2 = kpis_df_temp[~mask]  # current <= following
                    self.kpis_df = pd.concat([kpis_df1, kpis_df2])
                    self.kpis_df_len = len(self.kpis_df.index)

                    return [self.__create_pred_graph(),
                            '{}/{}'.format(self.pred_graph_progression + 1,
                                           math.ceil(self.kpis_df_len / self.REC_PER_PAGE))]

                else:
                    # TODO: ERROR
                    return [dash.no_update] * 2
            else:
                return [dash.no_update] * 2

        @app.callback([Output(self.views['explain'].IDs.PREDICTION_SEARCH_GRAPH, 'figure'),
                       Output(self.views['explain'].IDs.RECOMMANDATION_GRAPH_PAGING_INFO, 'children'),
                       Output(self.views['explain'].IDs.GO_UP_PRED_GRAPH, 'disabled'),
                       Output(self.views['explain'].IDs.GO_DOWN_PRED_GRAPH, 'disabled'),
                       Output(self.views['explain'].IDs.SELECT_PAGE_PRED_GRAPH_INPUT, 'value')],
                      State(self.views['explain'].IDs.SELECT_PAGE_PRED_GRAPH_INPUT, 'value'),
                      [Input(self.views['explain'].IDs.GO_UP_PRED_GRAPH, 'n_clicks'),
                       Input(self.views['explain'].IDs.GO_DOWN_PRED_GRAPH, 'n_clicks'),
                       Input(self.views['explain'].IDs.SELECT_PAGE_PRED_GRAPH_BTN, 'n_clicks')],
                      prevent_initial_call=True)
        def scroll_graph(page_value_sel, n_clicks_up, n_clicks_down, n_clicks_sel_page):
            button_id = dash.ctx.triggered_id
            # print(self.pred_graph_progression)
            max_page = math.ceil(self.kpis_df_len / self.REC_PER_PAGE)
            if button_id == self.views['explain'].IDs.GO_UP_PRED_GRAPH and n_clicks_up > 0:
                self.pred_graph_progression += 1
                return [
                    self.__create_pred_graph(),
                    '{}/{}'.format(self.pred_graph_progression + 1, max_page),
                    self.pred_graph_progression == (max_page - 1),
                    False,
                    ''
                ]

            elif button_id == self.views['explain'].IDs.GO_DOWN_PRED_GRAPH and n_clicks_down > 0:
                self.pred_graph_progression -= 1
                return [
                    self.__create_pred_graph(),
                    '{}/{}'.format(self.pred_graph_progression + 1, math.ceil(self.kpis_df_len / self.REC_PER_PAGE)),
                    False,
                    self.pred_graph_progression == 0,
                    ''
                ]

            elif button_id == self.views['explain'].IDs.SELECT_PAGE_PRED_GRAPH_BTN and n_clicks_sel_page > 0:
                if page_value_sel:
                    page_value_sel = int(max(1, min(page_value_sel, max_page)))
                    self.pred_graph_progression = page_value_sel - 1
                    return [
                        self.__create_pred_graph(),
                        '{}/{}'.format(self.pred_graph_progression + 1,
                                       math.ceil(self.kpis_df_len / self.REC_PER_PAGE)),
                        self.pred_graph_progression == (max_page - 1),
                        self.pred_graph_progression == 0,
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
                       Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_GRAPH_FADE, 'is_in')],
                      State(self.views['explain'].IDs.SEARCH_TRACE_ID_INPUT, 'value'),
                      [Input(self.views['explain'].IDs.PREDICTION_SEARCH_GRAPH, 'clickData'),
                       Input(self.views['explain'].IDs.SEARCH_TRACE_ID_INPUT_BTN, 'n_clicks')],
                      prevent_initial_call=True)
        def show_preds_text_format(input_value, click_data, n_clicks):
            DEFAULT_EXPL_QNT = 4
            CSS_BASE_ROW_CLASS_NAME = 'expl_table_selectable_row'
            graph_clicked = dash.ctx.triggered_id == self.views['explain'].IDs.PREDICTION_SEARCH_GRAPH
            search_btn_clicked = dash.ctx.triggered_id == self.views['explain'].IDs.SEARCH_TRACE_ID_INPUT_BTN
            if (graph_clicked and click_data) or (search_btn_clicked and n_clicks > 0):
                if graph_clicked:
                    trace_id = click_data['points'][0]['y']
                elif search_btn_clicked and input_value != '':
                    trace_id = input_value
                # print(trace_id)
                pred_info = self.explainer.get_best_n_scores_by_trace(trace_id, 3)

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
                    DEFAULT_EXPL_QNT,
                    False,
                    False
                ]
            else:
                return [dash.no_update] * 14

        app.clientside_callback(
            ClientsideFunction(
                namespace='clientside',
                function_name='slider_value_display_csc'
            ),
            Output(self.views['explain'].IDs.QNT_EXPL_SLIDER_VALUE_LABEL, 'children'),
            Input(self.views['explain'].IDs.EXPLANATION_QUANTITY_SLIDER, 'value')
        )

        @app.callback([Output(self.views['base'].IDs.ACT_TO_EXPLAIN_STORE, 'data'),
                       Output(self.views['explain'].IDs.FIRST_ROW_PRED_TABLE, 'className'),
                       Output(self.views['explain'].IDs.SECOND_ROW_PRED_TABLE, 'className'),
                       Output(self.views['explain'].IDs.THIRD_ROW_PRED_TABLE, 'className'),
                       Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_GRAPH, 'figure'),
                       Output(self.views['explain'].IDs.GENERATE_EXPL_BTN_FADE, 'is_in'),
                       Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_GRAPH_FADE, 'is_in')],
                      [Input(self.views['explain'].IDs.FIRST_ROW_PRED_TABLE, 'n_clicks'),
                       Input(self.views['explain'].IDs.SECOND_ROW_PRED_TABLE, 'n_clicks'),
                       Input(self.views['explain'].IDs.THIRD_ROW_PRED_TABLE, 'n_clicks')],
                      [State(self.views['explain'].IDs.FIRST_ROW_PRED_TABLE, 'children'),
                       State(self.views['explain'].IDs.SECOND_ROW_PRED_TABLE, 'children'),
                       State(self.views['explain'].IDs.THIRD_ROW_PRED_TABLE, 'children'),
                       State(self.views['base'].IDs.TRACE_ID_TO_EXPLAIN_STORE, 'data')],
                      prevent_initial_call=True)
        def select_trace_activity_to_explain(n_clicks1, n_clicks2, n_clicks3, ch1, ch2, ch3, trace_id):
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
                return [dash.no_update] * 7

            if self.explainer.check_if_explanations_exists(trace_id, act_to_explain):
                print('Explanations found, visualizing shap values for '
                      'trace: {}, activity: {}'.format(trace_id, act_to_explain))

                gt, expl = self.explainer.generate_explanations_dataframe(trace_id, act_to_explain)
                return class_list_to_return + [self.__create_explanation_graph(gt, expl, self.DEFAULT_EXPL_QNT),
                                               False, True]
            else:
                print('Not found shap values for trace: {}, activity: {}'.format(trace_id, act_to_explain))
                return class_list_to_return + [dash.no_update, True, False]

        @app.callback(Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_GRAPH, 'figure'),
                      [State(self.views['base'].IDs.TRACE_ID_TO_EXPLAIN_STORE, 'data'),
                       State(self.views['base'].IDs.ACT_TO_EXPLAIN_STORE, 'data')],
                      Input(self.views['explain'].IDs.EXPLANATION_QUANTITY_SLIDER, 'value'),
                      prevent_initial_call=True)
        def change_quantity_explanations(trace_id, act_to_explain, value):
            if value:
                gt, expl = self.explainer.generate_explanations_dataframe(trace_id, act_to_explain)
                if gt is not None and expl is not None:
                    return self.__create_explanation_graph(gt, expl, int(value))
                else:
                    raise dash.exceptions.PreventUpdate
            else:
                raise dash.exceptions.PreventUpdate

        @app.callback(
            output=[Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_GRAPH, 'figure'),
                    Output(self.views['explain'].IDs.GENERATE_EXPL_BTN_FADE, 'is_in'),
                    Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_GRAPH_FADE, 'is_in')],
            inputs=[State(self.views['base'].IDs.ACT_TO_EXPLAIN_STORE, 'data'),
                    State(self.views['base'].IDs.TRACE_ID_TO_EXPLAIN_STORE, 'data'),
                    State(self.views['explain'].IDs.EXPLANATION_QUANTITY_SLIDER, 'value'),
                    Input(self.views['explain'].IDs.GENERATE_EXPL_BTN, 'n_clicks')],
            background=True,
            prevent_initial_call=True,
            running=[
                # (Output(self.views['explain'].IDs.VISUALIZE_EXPLANATION_GRAPH_FADE, 'is_in'), False, True),
                (Output(self.views['explain'].IDs.GENERATE_EXPL_SPINNER, 'style'),
                 {'display': 'inline'}, {'display': 'none'})
            ]
        )
        def calculate_and_visualize_shap_by_trace(act_to_explain, trace_id, expl_qnt, n_clicks):
            if n_clicks > 0:
                if not self.explainer.check_if_explanations_exists(trace_id, act_to_explain):
                    print('Calculating shap values for trace: {}, activity: {}'.format(trace_id, act_to_explain))
                    self.explainer.calculate_explanation(trace_id, act_to_explain)
                    # trace_id = '1-739610172'
                    # act_to_explain = 'Resolved'
                    # time.sleep(5)
                    gt, expl = self.explainer.generate_explanations_dataframe(trace_id, act_to_explain)
                    return [self.__create_explanation_graph(gt, expl, expl_qnt if expl_qnt else self.DEFAULT_EXPL_QNT),
                            False, True]
                else:
                    # print('Explanations found, visualizing shap values for '
                    #       'trace: {}, activity: {}'.format(trace_id, act_to_explain))
                    #
                    # gt, expl = self.explainer.generate_explanations_dataframe(trace_id, act_to_explain)
                    # return self.__create_explanation_graph(gt, expl, expl_qnt if expl_qnt else self.DEFAULT_EXPL_QNT)
                    return [dash.no_update] * 3
            else:
                return [dash.no_update] * 3
