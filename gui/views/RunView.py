from strenum import StrEnum
from dash_extensions.enrich import html, dcc
import dash_bootstrap_components as dbc

from gui.views.View import View
import dash_uploader as du


class _IDs(StrEnum):
    PROC_RUN_OUT_FADE = 'proc_run_output_fade',
    PROGRESS_LOG_INTERVAL_RUN = 'interval_log_prog_run',
    SHOW_PROCESS_RUNNING_OUTPUT = 'show_proc_run_out',
    TEMP_RUNNING_OUTPUT = 'temp_run_out',
    RUN_FILE_UPLOADER = 'run_file_uploader',
    FADE_GENERATE_PREDS_BTN = 'fade_gen_preds_btn',
    GENERATE_PREDS_BTN = 'gen_preds_btn',
    LOAD_RUN_FILE_BTN = 'load_run_btn',


class RunView(View):
    def __init__(self, pathname='', order=-1):
        super().__init__(pathname, order)
        self.IDs = _IDs

    def get_layout(self):
        return html.Div([
            html.H1('Run'),
            du.Upload(id=self.IDs.RUN_FILE_UPLOADER),
            html.Div([
                html.Button('Load file', id=self.IDs.LOAD_RUN_FILE_BTN, n_clicks=0, disabled=True,
                            className='general_btn_layout'),
                dbc.Fade([
                    html.Button('Generate Predictions', id=self.IDs.GENERATE_PREDS_BTN, n_clicks=0,
                                className='general_btn_layout')
                ], is_in=False, appear=False, id=self.IDs.FADE_GENERATE_PREDS_BTN),
            ], className='run_btns_cont'),
            dbc.Fade([html.Div(id=self.IDs.TEMP_RUNNING_OUTPUT),
                      html.Div(id=self.IDs.SHOW_PROCESS_RUNNING_OUTPUT)], is_in=False, appear=False,
                     id=self.IDs.PROC_RUN_OUT_FADE, className='process_display_out_cont'),
            dcc.Interval(id=self.IDs.PROGRESS_LOG_INTERVAL_RUN, n_intervals=0, interval=1000, max_intervals=-1)
        ], className='run_container')
