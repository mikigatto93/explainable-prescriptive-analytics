from strenum import StrEnum
from dash_extensions.enrich import html, dcc
import dash_bootstrap_components as dbc

from gui.views.View import View


class _IDs(StrEnum):
    VISUALIZE_EXPLANATION_GRAPH_1 = 'visualize_explan_graph_1',
    VISUALIZE_EXPLANATION_GRAPH_FADE = 'expl_graph_fade',
    QNT_EXPL_SLIDER_VALUE_LABEL = 'explain_qnt_slider_value_label',
    CURRENT_ACTIVITY = 'curretn_activity',
    VISUALIZE_EXPL_FADE = 'visualize_explan_fade',
    RECOMMANDATION_GRAPH_PAGING_INFO = 'recomm_graph_paging_info',
    SEARCH_TRACE_ID_INPUT_BTN = 'search_trace_id_input_btn',
    CURRENT_TRACE_ID = 'current_trace_id_selected'
    CURRENT_EXPECTED_KPI = 'current_expected_kpi',
    VISUALIZE_EXPL_BTN = 'visualize_explan_btn',
    GO_DOWN_PRED_GRAPH = 'go_down_btn_pred_graph',
    GO_UP_PRED_GRAPH = 'go_up_btn_pred_graph',
    VISUALIZE_EXPLANATION_GRAPH = 'visualize_explan_graph',
    EXPLANATION_QUANTITY_SLIDER = 'explan_quantity_number',
    PREDICTION_SEARCH_GRAPH = 'pred_search_graph',
    FIRST_ROW_PRED_TABLE = 'row1_pred_table',
    SECOND_ROW_PRED_TABLE = 'row2_pred_table',
    THIRD_ROW_PRED_TABLE = 'row3_pred_table',
    SEARCH_TRACE_ID_INPUT = 'search_trace_id_input',


class ExplainView(View):
    def __init__(self, pathname='', order=-1):
        super().__init__(pathname, order)
        self.IDs = _IDs

    def create_table(self):
        return [
            html.Caption('Proposed next activities:'),
            html.Thead(html.Tr([html.Th('Activity'), html.Th('Expected KPI')])),
            html.Tbody([html.Tr(id=self.IDs.FIRST_ROW_PRED_TABLE, n_clicks=0),
                        html.Tr(id=self.IDs.SECOND_ROW_PRED_TABLE, n_clicks=0),
                        html.Tr(id=self.IDs.THIRD_ROW_PRED_TABLE, n_clicks=0)])
        ]

    # def get_blank_figure():
    #     fig = go.Figure(go.Scatter(x=[], y=[]))
    #     fig.update_layout(template=None)
    #     fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    #     fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    #     return fig

    def get_layout(self):
        return html.Div([
            html.H1('Explain'),
            html.Div([
                html.Div([
                    dcc.Loading([dcc.Graph(id=self.IDs.PREDICTION_SEARCH_GRAPH, figure={})], type='circle'),
                ], className='search_trace_graph_cont'),

                html.Div([
                    html.Button('∧', id=self.IDs.GO_UP_PRED_GRAPH, n_clicks=0),
                    html.Button('∨', id=self.IDs.GO_DOWN_PRED_GRAPH, n_clicks=0, disabled=True),
                    html.Span(id=self.IDs.RECOMMANDATION_GRAPH_PAGING_INFO),
                ], className='paging_controls_cont'),

                html.Div([
                    html.Span('Search trace by id'),
                    dcc.Input(id=self.IDs.SEARCH_TRACE_ID_INPUT),
                    html.Button('Search', id=self.IDs.SEARCH_TRACE_ID_INPUT_BTN, n_clicks=0)
                ], className='search_trace_by_id_cont')
            ], className='trace_expl_selectors_cont'),

            dbc.Fade([
                html.P(id=self.IDs.CURRENT_TRACE_ID),
                html.Div(id=self.IDs.CURRENT_ACTIVITY),
                html.Div(id=self.IDs.CURRENT_EXPECTED_KPI),
                dbc.Table(self.create_table(), className='explanation_table'),
                html.Span('Select how many explanations to visualize'),
                html.Div([
                    dcc.Slider(id=self.IDs.EXPLANATION_QUANTITY_SLIDER, max=10, min=0, step=1, marks=None),
                    html.Span(id=self.IDs.QNT_EXPL_SLIDER_VALUE_LABEL),
                ], className='slider_cont'),
                html.Button('Visualize explanations', self.IDs.VISUALIZE_EXPL_BTN, n_clicks=0,
                            className='general_btn_layout'),
                dcc.Loading([dcc.Graph(id=self.IDs.VISUALIZE_EXPLANATION_GRAPH)], type='circle'),
                dcc.Graph(id=self.IDs.VISUALIZE_EXPLANATION_GRAPH_1),

            ], is_in=False, appear=False, id=self.IDs.VISUALIZE_EXPL_FADE, className='visualize_expl_cont')
        ], className='explain_container')
