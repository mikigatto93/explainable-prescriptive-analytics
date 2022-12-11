import json

import dash

from app import app
from dash_extensions.enrich import Input, Output, State
import plotly.graph_objects as go

from gui.model import Experiment
from gui.model.Explainer import Explainer
from gui.presenters.Presenter import Presenter


class ExplainPresenter(Presenter):
    def __init__(self, views):
        super().__init__(views)
        self.explainer = None

    def register_callbacks(self):

        @app.callback(Output(self.views['explain'].IDs.PREDICTION_SEARCH_GRAPH, 'figure'),
                      State(self.views['base'].IDs.EXPERIMENT_DATA_STORE, 'data'),
                      Input(self.views['base'].IDs.LOCATION_URL, 'pathname'))
        def generate_prediction_graph(ex_info_data, url):
            if url == self.views['explain'].pathname:
                print(url)
                if ex_info_data:
                    self.explainer = Explainer(Experiment.build_experiment_from_dict(json.loads(ex_info_data)))
                    kpis_dict = self.explainer.calculate_best_scores()

                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=list([kpis_dict[k][0] for k in kpis_dict.keys()]),
                        y=list(kpis_dict.keys()),
                        name='Following recommendation',
                        orientation='h',
                        marker_color='darkgreen',
                    ))
                    fig.add_trace(go.Bar(
                        x=[kpis_dict[k][1] for k in kpis_dict.keys()],
                        y=list(kpis_dict.keys()),
                        name='Actual Value',
                        orientation='h',
                        marker_color='darkred',
                    ))
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                                      plot_bgcolor='rgba(0,0,0,0)',
                                      xaxis=dict(range=[0, max([kpis_dict[k][1] for k in kpis_dict.keys()])]),
                                      yaxis=dict(range=[len(kpis_dict) - 10, len(kpis_dict)]))
                    # fig.update_style(width='60%')
                    return fig
                else:
                    # TODO: ERROR
                    raise dash.exceptions.PreventUpdate
            else:
                raise dash.exceptions.PreventUpdate
