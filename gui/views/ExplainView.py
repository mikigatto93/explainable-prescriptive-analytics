from strenum import StrEnum
from dash_extensions.enrich import html, dcc
import dash_bootstrap_components as dbc

import plotly.graph_objects as go

from app import app
from gui.views.View import View


class IDs(StrEnum):
    VISUALIZE_EXPLANATION_DETAILS = 'visualize_explainations_details'
    CHANGE_ORDER_EXPL_DROPDOWN = 'change_order_expl_dropdown',
    CHANGE_ORDER_EXPL_BTN = 'change_order_expl_btn',
    CHANGE_ORDER_PRED_DROPDOWN = 'change_order_pred_dropdown',
    CHANGE_ORDER_PRED_BTN = 'change_order_pred_btn',
    SELECT_PAGE_PRED_GRAPH_BTN = 'sel_page_pred_graph_btn',
    SELECT_PAGE_PRED_GRAPH_INPUT = 'sel_page_pred_graph_input',
    GENERATE_EXPL_SPINNER = 'generate_expl_spinner',
    GENERATE_EXPL_BTN_FADE = 'generate_expl_btn_fade',
    VISUALIZE_EXPLANATION_GRAPH_1 = 'visualize_explan_graph_1',
    VISUALIZE_EXPLANATION_GRAPH_FADE = 'expl_graph_fade',
    QNT_EXPL_SLIDER_VALUE_LABEL = 'explain_qnt_slider_value_label',
    CURRENT_ACTIVITY = 'curretn_activity',
    VISUALIZE_EXPL_FADE = 'visualize_explan_fade',
    RECOMMENDATION_GRAPH_PAGING_INFO = 'recomm_graph_paging_info',
    SEARCH_TRACE_ID_INPUT_BTN = 'search_trace_id_input_btn',
    CURRENT_TRACE_ID = 'current_trace_id_selected'
    CURRENT_EXPECTED_KPI = 'current_expected_kpi',
    GENERATE_EXPL_BTN = 'generate_explan_btn',
    GO_DOWN_PRED_GRAPH = 'go_down_btn_pred_graph',
    GO_UP_PRED_GRAPH = 'go_up_btn_pred_graph',
    VISUALIZE_EXPLANATION_GRAPH = 'visualize_explan_graph',
    EXPLANATION_QUANTITY_SLIDER = 'explan_quantity_number',
    PREDICTION_SEARCH_GRAPH = 'pred_search_graph',
    FIRST_ROW_PRED_TABLE = 'row1_pred_table',
    SECOND_ROW_PRED_TABLE = 'row2_pred_table',
    THIRD_ROW_PRED_TABLE = 'row3_pred_table',
    SEARCH_TRACE_ID_INPUT = 'search_trace_id_input',


class _ERROR_IDs(StrEnum):
    SEARCH_TRACE_ID_INPUT = 'search_trace_id_input_error'


def _get_blank_figure():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    return fig


class ExplainView(View):
    def __init__(self, pathname='', order=-1):
        super().__init__(pathname, order)
        self.IDs = IDs
        self.ERROR_IDs = _ERROR_IDs

    def create_table(self):
        return [
            html.Caption('Proposed next activities:'),
            html.Thead(html.Tr([html.Th('Activity'), html.Th('Expected KPI')])),
            html.Tbody([html.Tr(id=self.IDs.FIRST_ROW_PRED_TABLE, n_clicks=0, className='expl_table_selectable_row'),
                        html.Tr(id=self.IDs.SECOND_ROW_PRED_TABLE, n_clicks=0, className='expl_table_selectable_row'),
                        html.Tr(id=self.IDs.THIRD_ROW_PRED_TABLE, n_clicks=0, className='expl_table_selectable_row')])
        ]

    def get_layout(self):
        return html.Div([
            html.H1('Explain'),
            html.Div([
                html.Div([
                    dcc.Loading([dcc.Graph(id=self.IDs.PREDICTION_SEARCH_GRAPH, figure={})], type='circle'),
                    html.Div([
                        html.Span('Change order of recommendations'),
                        html.Div([
                            dcc.Dropdown(['Maximize', 'Minimize', 'Delta from maximum', 'Delta from minimum'],
                                         className='order_options_dropdown', id=self.IDs.CHANGE_ORDER_PRED_DROPDOWN),
                            html.Button('Change order', id=self.IDs.CHANGE_ORDER_PRED_BTN, n_clicks=0)
                        ], className='order_changer_controls_container')
                    ]),
                ], className='search_trace_graph_cont'),

                html.Div([
                    html.Button('∧', id=self.IDs.GO_UP_PRED_GRAPH, n_clicks=0),
                    html.Button('∨', id=self.IDs.GO_DOWN_PRED_GRAPH, n_clicks=0, disabled=True),

                    html.Div([
                        html.Span('Select page'),
                        dcc.Input(id=self.IDs.SELECT_PAGE_PRED_GRAPH_INPUT, type='number'),
                        html.Button('Go', id=self.IDs.SELECT_PAGE_PRED_GRAPH_BTN, n_clicks=0),
                    ], className='select_page_paging_controls_cont'),

                    html.Span(id=self.IDs.RECOMMENDATION_GRAPH_PAGING_INFO),
                ], className='paging_controls_cont'),

                html.Div([
                    html.Span('Search trace by id'),
                    dcc.Input(id=self.IDs.SEARCH_TRACE_ID_INPUT),
                    html.Button('Search', id=self.IDs.SEARCH_TRACE_ID_INPUT_BTN, n_clicks=0),
                    html.Div(className='error_box', id=self.ERROR_IDs.SEARCH_TRACE_ID_INPUT),
                ], className='search_trace_by_id_cont')
            ], className='trace_expl_selectors_cont'),

            dbc.Fade([
                html.P(id=self.IDs.CURRENT_TRACE_ID),
                html.Div(id=self.IDs.CURRENT_ACTIVITY),
                html.Div(id=self.IDs.CURRENT_EXPECTED_KPI),
                dbc.Table(self.create_table(), className='explanation_table'),

                dbc.Fade([html.Button(
                    html.Div([html.Img(src=app.get_asset_url('spinner-white.gif'), id=self.IDs.GENERATE_EXPL_SPINNER,
                                       style={'display': 'inline'}, width=18, height=18, className='spinner_img'),
                              html.Span('Generate explanations')], className='button_spinner_cont'),
                    n_clicks=0, id=self.IDs.GENERATE_EXPL_BTN,
                    className='general_btn_layout')], id=self.IDs.GENERATE_EXPL_BTN_FADE,
                    is_in=False, appear=False),

                dbc.Fade([
                    html.Div('Select how many explanations to visualize'),
                    html.Div([
                        dcc.Slider(id=self.IDs.EXPLANATION_QUANTITY_SLIDER, max=10, min=0, step=1, marks=None,
                                   updatemode='drag'),
                        html.Span(id=self.IDs.QNT_EXPL_SLIDER_VALUE_LABEL),
                    ], className='slider_cont'),

                    html.Div([
                        html.Span('Change order of explanations'),
                        html.Div([
                            dcc.Dropdown(['Delta from maximum', 'Delta from minimum'],
                                         className='order_options_dropdown', id=self.IDs.CHANGE_ORDER_EXPL_DROPDOWN),
                            html.Button('Change order', id=self.IDs.CHANGE_ORDER_EXPL_BTN, n_clicks=0)
                        ], className='order_changer_controls_container')
                    ]),

                    html.P(id=self.IDs.VISUALIZE_EXPLANATION_DETAILS),

                    dcc.Graph(id=self.IDs.VISUALIZE_EXPLANATION_GRAPH, figure={}),

                ], is_in=False, appear=False, id=self.IDs.VISUALIZE_EXPLANATION_GRAPH_FADE),

            ], is_in=False, appear=False, id=self.IDs.VISUALIZE_EXPL_FADE, className='visualize_expl_cont')
        ], className='explain_container')
