from strenum import StrEnum
from dash_extensions.enrich import html, dcc, Output, Input, dcc
import dash_bootstrap_components as dbc

from gui.views.View import View


class _IDs(StrEnum):
    PROGRESS_LOG_INTERVAL = 'logging_prpg_interval',
    LOAD_TRAIN_FILE_BTN = 'load_train_btn',
    LOAD_FILE_AREA = 'load_file_div_train',
    LOAD_MODEL_BTN = 'load_model_btn',
    EXPERIMENT_NAME_TEXTBOX = 'experiment_name_textbox',
    ID_DROPDOWN = 'id_dropdown',
    TIMESTAMP_DROPDOWN = 'timestamp_dropdown',
    ACTIVITY_DROPDOWN = 'activity_dropdown',
    ACT_TO_OPTIMIZE_DROPDOWN = 'act_to_opt_dropdown',
    OUTLIERS_THRS_SLIDER = 'outliers_slider',
    FADE_ACT_TO_OPTIMIZE_DROPDOWN = 'fade_act_opt_dropdown',
    START_TRAINING_BTN = 'start_training_btn',
    FADE_ALL_TRAIN_CONTROLS = 'fade_all_controls_train',
    KPI_RADIO_ITEMS = 'kpi_radio_item',
    RESOURCE_NAME_DROPDOWN = 're_name_dropdown',
    TEMP_TRAINING_OUTPUT = 'temp_out_train',
    SHOW_PROCESS_TRAINING_OUTPUT = 'show_proc_train_out',


class TrainView(View):
    def __init__(self, pathname='', order=-1):
        super().__init__(pathname, order)
        self.IDs = _IDs

    def get_layout(self):
        return html.Div([
            html.H1('Train'),
            html.Div('Click to select the training file', n_clicks=0, id=self.IDs.LOAD_FILE_AREA),
            html.Button('Load file', id=self.IDs.LOAD_TRAIN_FILE_BTN, n_clicks=0),
            html.Button('Load model', id=self.IDs.LOAD_MODEL_BTN, n_clicks=0),
            dbc.Fade([
                html.Span('Experiment name:'),
                dcc.Input(id=self.IDs.EXPERIMENT_NAME_TEXTBOX),
                html.P('Select KPI'),
                dcc.RadioItems([
                    'Total time',
                    'Maximize activity occurrence',
                    'Minimize activity occurrence'
                ], id=self.IDs.KPI_RADIO_ITEMS),
                html.P('Select columns:'),
                html.Span('ID'),
                dcc.Dropdown(id=self.IDs.ID_DROPDOWN),
                html.Span('Timestamp'),
                dcc.Dropdown(id=self.IDs.TIMESTAMP_DROPDOWN),
                html.Span('Activity'),
                dcc.Dropdown(id=self.IDs.ACTIVITY_DROPDOWN),
                html.Span('Resource name'),
                dcc.Dropdown(id=self.IDs.RESOURCE_NAME_DROPDOWN),
                dbc.Fade([
                    html.Span('Activity to optimize'),
                    dcc.Dropdown(id=self.IDs.ACT_TO_OPTIMIZE_DROPDOWN)
                ], is_in=False, appear=False, id=self.IDs.FADE_ACT_TO_OPTIMIZE_DROPDOWN),
                html.Span('Select outliers threshold'),
                dcc.Slider(id=self.IDs.OUTLIERS_THRS_SLIDER, min=0, max=1, step=0.01, marks=None,
                           tooltip={"placement": "bottom", "always_visible": True}),
                html.Button('Train', id=self.IDs.START_TRAINING_BTN, n_clicks=0)
            ], is_in=False, appear=False, id=self.IDs.FADE_ALL_TRAIN_CONTROLS),
            html.Div(id=self.IDs.TEMP_TRAINING_OUTPUT),
            html.Div(id=self.IDs.SHOW_PROCESS_TRAINING_OUTPUT),
            dcc.Interval(id=self.IDs.PROGRESS_LOG_INTERVAL, n_intervals=0, interval=1000)
        ])
