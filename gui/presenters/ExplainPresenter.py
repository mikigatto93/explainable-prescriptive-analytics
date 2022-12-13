import json

import dash
import pandas as pd

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
        self.explainer = None
        self.kpis_df = None
        self.pred_graph_progression = 0

    def __create_pred_graph(self):
        df_slice = self.kpis_df[slice(15 * self.pred_graph_progression, 15 * (self.pred_graph_progression + 1))]
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
                name='Actual Value',
                y=df_slice.index,
                x=df_slice['Actual Value'],
                marker_color='darkred',
                orientation='h',
            )
        )

        fig.update_yaxes(tickmode='linear')
        return fig

    def register_callbacks(self):

        @app.callback(Output(self.views['explain'].IDs.PREDICTION_SEARCH_GRAPH, 'figure'),
                      State(self.views['base'].IDs.EXPERIMENT_DATA_STORE, 'data'),
                      Input(self.views['base'].IDs.LOCATION_URL, 'pathname'))
        def show_prediction_graph(ex_info_data, url):
            if url == self.views['explain'].pathname:
                print(url)
                ex_info_data = {"ex_name": "test1", "kpi": "Total time", "id": "SR_Number",
                                "timestamp": "Change_Date+Time", "activity": "ACTIVITY",
                                "resource": None, "act_to_opt": "Involved_ST", "out_thrs": 0.03,
                                "pred_column": "remaining_time"}
                if ex_info_data:
                    # self.explainer = Explainer(Experiment.build_experiment_from_dict(json.loads(ex_info_data)))
                    self.explainer = Explainer(Experiment.build_experiment_from_dict(ex_info_data))
                    kpis_dict = self.explainer.calculate_best_scores()
                    self.kpis_df = pd.DataFrame.from_dict(kpis_dict,
                                                          orient='index',
                                                          columns=['Following recommendation', 'Actual Value'])
                    # TODO: ORDERING FUNCTION
                    return self.__create_pred_graph()

                else:
                    # TODO: ERROR
                    raise dash.exceptions.PreventUpdate
            else:
                raise dash.exceptions.PreventUpdate

        @app.callback(Output(self.views['explain'].IDs.PREDICTION_SEARCH_GRAPH, 'figure'),
                      [Input(self.views['explain'].IDs.GO_UP_PRED_GRAPH, 'n_clicks'),
                       Input(self.views['explain'].IDs.GO_DOWN_PRED_GRAPH, 'n_clicks')],
                      prevent_initial_call=True)
        def scroll_graph(n_clicks_up, n_clicks_down):
            button_id = dash.ctx.triggered_id
            if button_id == self.views['explain'].IDs.GO_UP_PRED_GRAPH and n_clicks_up > 0:
                self.pred_graph_progression += 1
                return self.__create_pred_graph()
            elif button_id == self.views['explain'].IDs.GO_DOWN_PRED_GRAPH and n_clicks_down > 0:
                self.pred_graph_progression -= 1
                return self.__create_pred_graph()
            else:
                raise dash.exceptions.PreventUpdate

        @app.callback([Output(self.views['explain'].IDs.PRED_TABLE_CAPTION, 'children'),
                       Output(self.views['explain'].IDs.FIRST_ROW_PRED_TABLE, 'children'),
                       Output(self.views['explain'].IDs.SECOND_ROW_PRED_TABLE, 'children'),
                       Output(self.views['explain'].IDs.THIRD_ROW_PRED_TABLE, 'children'),
                       Output(self.views['explain'].IDs.ACT_TO_EXPLAIN_DROPDOWN, 'options')],
                      Input(self.views['explain'].IDs.PREDICTION_SEARCH_GRAPH, 'clickData'),
                      prevent_initial_call=True)
        def show_preds_text_format(click_data):
            trace_id = click_data['points'][0]['y']
            print(trace_id)
            pred_info = self.explainer.get_best_n_scores_by_trace(trace_id, 3)

            rec_act = [t[0] for t in pred_info['rec']]
            rec_values = [t[1] for t in pred_info['rec']]
            # real_act = pred_info['real'][0][0]
            real_val = pred_info['real'][0][1]

            print(pred_info)
            print(rec_act)
            print(rec_values)
            print(real_val)

            return [
                'Prediction for {}'.format(trace_id),
                [html.Td(rec_act[0]), html.Td(real_val), html.Td(rec_values[0])],
                [html.Td(rec_act[1]), html.Td('-'), html.Td(rec_values[1])] if len(rec_act) > 1 else [],
                [html.Td(rec_act[2]), html.Td('-'), html.Td(rec_values[2])] if len(rec_act) > 2 else [],
                rec_act
            ]