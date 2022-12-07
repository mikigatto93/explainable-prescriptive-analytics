from strenum import StrEnum
from dash_extensions.enrich import html, dcc
import dash_bootstrap_components as dbc

from gui.views.View import View


class _IDs(StrEnum):
    FADE_GENERATE_PREDS_BTN = 'fade_gen_preds_btn',
    GENERATE_PREDS_BTN = 'gen_preds_btn',
    LOAD_FILE_AREA = 'load_file_area_run',
    LOAD_RUN_FILE_BTN = 'load_run_btn',


class RunView(View):
    def __init__(self, pathname='', order=-1):
        super().__init__(pathname, order)
        self.IDs = _IDs

    def get_layout(self):
        return html.Div([
            html.H1('Run'),
            html.Div('Click to select the training file', n_clicks=0, id=self.IDs.LOAD_FILE_AREA),
            html.Button('Load file', id=self.IDs.LOAD_RUN_FILE_BTN, n_clicks=0),
            dbc.Fade([
                html.Button('Generate Predictions', id=self.IDs.GENERATE_PREDS_BTN, n_clicks=0)
            ], is_in=False, appear=False, id=self.IDs.FADE_GENERATE_PREDS_BTN)
        ])
