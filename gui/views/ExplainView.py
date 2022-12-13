from strenum import StrEnum
from dash_extensions.enrich import html, dcc
import dash_bootstrap_components as dbc

from gui.views.View import View


class _IDs(StrEnum):
    VISUALIZE_EXPL_BTN = 'visualize_explan_btn',
    GO_DOWN_PRED_GRAPH = 'go_down_btn_pred_graph',
    GO_UP_PRED_GRAPH = 'go_up_btn_preed_graph',
    VISUALIZE_EXPLANATION_GRAPH = 'visualize_explan_graph',
    EXPLANATION_QUANTITY_SLIDER = 'explan_quantity_number',
    PREDICTION_SEARCH_GRAPH = 'pred_search_graph',
    ACT_TO_EXPLAIN_DROPDOWN = 'ex_act_dropdown',
    PRED_TABLE_CAPTION = 'pred_table_caption',
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
            html.Caption('Prediction for', id=self.IDs.PRED_TABLE_CAPTION),
            html.Thead(html.Tr([html.Th('Activity'), html.Th('Actual'), html.Th('Predicted')])),
            html.Tbody([html.Tr(id=self.IDs.FIRST_ROW_PRED_TABLE),
                       html.Tr(id=self.IDs.SECOND_ROW_PRED_TABLE),
                       html.Tr(id=self.IDs.THIRD_ROW_PRED_TABLE)])
        ]

    def get_layout(self):
        return html.Div([
            html.H1('Explain'),
            html.Div([
                html.Span('Select the desired trace'),
                dcc.Graph(id=self.IDs.PREDICTION_SEARCH_GRAPH, figure={}),
                html.Button('∧', id=self.IDs.GO_UP_PRED_GRAPH, n_clicks=0),
                html.Button('∨', id=self.IDs.GO_DOWN_PRED_GRAPH, n_clicks=0)
            ]),
            html.Span('Search trace by id'),
            dcc.Input(id=self.IDs.SEARCH_TRACE_ID_INPUT),
            dbc.Table(self.create_table()),
            html.Span('Select the activity to explain'),
            dcc.Dropdown(id=self.IDs.ACT_TO_EXPLAIN_DROPDOWN),
            html.Span('Select how mant explanations to visualize'),
            dcc.Slider(id=self.IDs.EXPLANATION_QUANTITY_SLIDER, max=10, min=0, step=1, marks=None,
                       tooltip={"placement": "bottom", "always_visible": True}),
            html.Button('Visualize explanations', self.IDs.VISUALIZE_EXPL_BTN, n_clicks=0),
            dcc.Graph(id=self.IDs.VISUALIZE_EXPLANATION_GRAPH)
        ])
