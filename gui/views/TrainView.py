from strenum import StrEnum
from dash_extensions.enrich import html, dcc, Output, Input, dcc
import dash_bootstrap_components as dbc

from gui.views.View import View
import dash_uploader as du


class _IDs(StrEnum):
    PROC_TRAIN_OUT_FADE = 'proc_train_output_fade',
    OUT_THRS_SLIDER_VALUE_LABEL = 'out_thrs_slidier_value_label'
    SLIDER_VALUE_TEXTBOX = 'slider_value_textbox',
    TRAIN_FILE_UPLOADER = 'train_file_uploader',
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
    KPI_RADIO_ITEMS = 'kpi_radio_items',
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
            # html.Div('Click to select the training file', n_clicks=0, id=self.IDs.LOAD_FILE_AREA),
            html.Div([
                html.Div([
                    du.Upload(id=self.IDs.TRAIN_FILE_UPLOADER),
                    html.Button('Load file', id=self.IDs.LOAD_TRAIN_FILE_BTN, n_clicks=0, disabled=True,
                                className='general_btn_layout'),
                ], className='load_train_file_cont'),
                html.Div([
                    html.Button('Load model', id=self.IDs.LOAD_MODEL_BTN, n_clicks=0,
                                className='general_btn_layout'),
                ], className='load_model_cont'),
            ], className='train_load_area'),
            dbc.Fade([
                html.Div([
                    html.Span('Experiment name'),
                    dcc.Input(id=self.IDs.EXPERIMENT_NAME_TEXTBOX),
                ], className='experiment_name_cont'),
                html.Div([
                    html.Div([
                        html.P('Select KPI'),
                        dcc.RadioItems([
                            'Total time',
                            # 'Maximize activity occurrence',
                            'Minimize activity occurrence'
                        ], id=self.IDs.KPI_RADIO_ITEMS),
                    ], className='kpi_radio_cont'),
                    html.Div([
                        html.P('Select columns:'),
                        html.Span('ID'),
                        dcc.Dropdown(id=self.IDs.ID_DROPDOWN, className='dropdown_select_column'),
                        html.Span('Timestamp'),
                        dcc.Dropdown(id=self.IDs.TIMESTAMP_DROPDOWN, className='dropdown_select_column'),
                        html.Span('Activity'),
                        dcc.Dropdown(id=self.IDs.ACTIVITY_DROPDOWN, className='dropdown_select_column'),
                        html.Span('Resource name'),
                        dcc.Dropdown(id=self.IDs.RESOURCE_NAME_DROPDOWN, className='dropdown_select_column'),
                        dbc.Fade([
                            html.Span('Activity to optimize'),
                            dcc.Dropdown(id=self.IDs.ACT_TO_OPTIMIZE_DROPDOWN, className='dropdown_select_column')
                        ], is_in=False, appear=False, id=self.IDs.FADE_ACT_TO_OPTIMIZE_DROPDOWN),
                    ], className='columns_dropdown_cont'),
                ], className='kpi_and_columns_cont'),
                html.Span('Select outliers threshold'),
                html.Div([
                    dcc.Slider(id=self.IDs.OUTLIERS_THRS_SLIDER, min=0, max=1, step=0.01, marks=None),
                    # dcc.Input(id=self.IDs.SLIDER_VALUE_TEXTBOX, maxLength=4, max=1, min=0, step=0.01),
                    html.Span(id=self.IDs.OUT_THRS_SLIDER_VALUE_LABEL)
                ], className='slider_cont'),
                html.Button('Train', id=self.IDs.START_TRAINING_BTN, n_clicks=0, className='general_btn_layout')
            ], is_in=False, appear=False, id=self.IDs.FADE_ALL_TRAIN_CONTROLS, className='all_controls_container'),
            dbc.Fade([html.Div(id=self.IDs.TEMP_TRAINING_OUTPUT),
                      html.Div(id=self.IDs.SHOW_PROCESS_TRAINING_OUTPUT)], is_in=False, appear=False,
                     id=self.IDs.PROC_TRAIN_OUT_FADE, className='process_display_out_cont'),
            dcc.Interval(id=self.IDs.PROGRESS_LOG_INTERVAL, n_intervals=0, interval=1000, max_intervals=-1)
        ], className='view_container')
