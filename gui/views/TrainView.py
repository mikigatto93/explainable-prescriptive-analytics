import uuid

from strenum import StrEnum
from dash_extensions.enrich import html, dcc, Output, Input, dcc
import dash_bootstrap_components as dbc

from app import app, CONFIG

from gui.views.View import View
import dash_uploader as du


class IDs(StrEnum):
    EXPERIMENT_SELECTOR_TIME_DISPLAYER = 'experiment_selector_time_displayer',
    LOAD_TRAIN_FILE_BTN_FADE = 'load_train_file_btn_fade',
    LOAD_TRAIN_SPINNER = 'load_train_spinner',
    PREV_SELECT_PHASE_TRAIN_BTN = 'prev_select_phase_train_btn',
    NEXT_SELECT_PHASE_TRAIN_BTN = 'next_select_phase_train_btn',
    FADE_KPI_RADIO_ITEMS = 'fade_kpi_radio_items',
    FADE_START_TRAINING_BTN = 'fade_start_train_btn',
    EXPERIMENT_SELECTOR_DROPDOWN = 'exp_selector_dropdown',
    DOWNLOAD_TRAIN_BTN = 'download_train_btn',
    DOWNLOAD_TRAIN_BTN_FADE = 'download_train_btn_fade',
    TRAIN_SPINNER = 'train_spinner',
    PROC_TRAIN_OUT_FADE = 'proc_train_output_fade',
    OUT_THRS_SLIDER_VALUE_LABEL = 'out_thrs_slidier_value_label'
    SLIDER_VALUE_TEXTBOX = 'slider_value_textbox',
    TRAIN_FILE_UPLOADER = 'train_file_uploader',
    PROGRESS_LOG_INTERVAL_TRAIN = 'logging_prog_interval_train',
    LOAD_TRAIN_FILE_BTN = 'load_train_file_btn',
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
    RESOURCE_NAME_DROPDOWN = 'res_name_dropdown',
    TEMP_TRAINING_OUTPUT = 'temp_out_train',
    SHOW_PROCESS_TRAINING_OUTPUT = 'show_proc_train_out',


class _ERROR_IDs(StrEnum):
    ID_DROPDOWN = 'id_dropdown_error',
    TIMESTAMP_DROPDOWN = 'timestamp_dropdown_error',
    ACTIVITY_DROPDOWN = 'activity_dropdown_error',
    ACT_TO_OPTIMIZE_DROPDOWN = 'act_to_opt_dropdown_error',
    OUTLIERS_THRS_SLIDER = 'outliers_slider_error',
    RESOURCE_NAME_DROPDOWN = 'res_name_dropdown_error',
    KPI_RADIO_ITEMS = 'kpi_radio_items_error',
    LOAD_MODEL_BTN = 'load_model_btn_error',
    START_TRAINING_BTN = 'start_training_btn_error',
    EXPERIMENT_NAME_TEXTBOX = 'experiment_name_textbox_error',
    LOAD_TRAIN_FILE_BTN = 'load_train_file_btn_error',


def get_kpi_radio_items_options(disabled=False):
    return [{'label': 'Total time', 'value': 'Total time', 'disabled': disabled},
            {'label': 'Minimize activity occurrence', 'value': 'Minimize activity occurrence',
             'disabled': disabled}]


class TrainView(View):
    def __init__(self, pathname='', order=-1):
        super().__init__(pathname, order)
        self.IDs = IDs
        self.ERROR_IDs = _ERROR_IDs
        # self.upload_id = str(uuid.uuid4())

    def get_layout(self):
        return html.Div([
            html.H1('Train'),
            html.Div([
                html.Div([
                    du.Upload(id=self.IDs.TRAIN_FILE_UPLOADER, filetypes=['csv', 'xes', 'xls'],
                              max_file_size=CONFIG['UPLOAD_BYTE_SIZE']),
                    dbc.Fade([
                        html.Button(
                            html.Div(
                                [html.Img(src=app.get_asset_url('spinner-white.gif'), id=self.IDs.LOAD_TRAIN_SPINNER,
                                          style={'display': 'none'}, width=18, height=18, className='spinner_img'),
                                 html.Span('Process file')], className='button_spinner_cont'),
                            n_clicks=0, id=self.IDs.LOAD_TRAIN_FILE_BTN, className='general_btn_layout'),
                        html.Div(className='error_box', id=self.ERROR_IDs.LOAD_TRAIN_FILE_BTN)
                    ], is_in=False, appear=False, id=self.IDs.LOAD_TRAIN_FILE_BTN_FADE)
                ], className='load_train_file_cont'),
                html.Div([
                    html.Div('Select one experiment:'),
                    html.Div('A new experiment with the same data as the one selected will be created',
                             className='select_experiment_warning'),
                    dcc.Dropdown(id=self.IDs.EXPERIMENT_SELECTOR_DROPDOWN, className='dropdown_select_column'),
                    html.P(id=self.IDs.EXPERIMENT_SELECTOR_TIME_DISPLAYER),
                    html.Button('Load model', id=self.IDs.LOAD_MODEL_BTN, n_clicks=0,
                                className='general_btn_layout', disabled=True),
                    html.Div(className='error_box', id=self.ERROR_IDs.LOAD_MODEL_BTN),
                ], className='load_model_cont'),
            ], className='train_load_area'),

            dbc.Fade([
                html.Div([
                    html.Div([html.Span('Experiment name'),
                              dcc.Input(id=self.IDs.EXPERIMENT_NAME_TEXTBOX),
                              html.Div(className='error_box', id=self.ERROR_IDs.EXPERIMENT_NAME_TEXTBOX)
                              ]),
                ], className='experiment_name_cont'),

                html.Div([
                    html.Div([
                        html.P('Select columns'),
                        html.Span('ID'),
                        dcc.Dropdown(id=self.IDs.ID_DROPDOWN, className='dropdown_select_column'),
                        html.Div(className='error_box', id=self.ERROR_IDs.ID_DROPDOWN),
                        html.Span('Timestamp'),
                        dcc.Dropdown(id=self.IDs.TIMESTAMP_DROPDOWN, className='dropdown_select_column'),
                        html.Div(className='error_box', id=self.ERROR_IDs.TIMESTAMP_DROPDOWN),
                        html.Span('Activity'),
                        dcc.Dropdown(id=self.IDs.ACTIVITY_DROPDOWN, className='dropdown_select_column'),
                        html.Div(className='error_box', id=self.ERROR_IDs.ACTIVITY_DROPDOWN),
                        html.Span('Resource name'),
                        dcc.Dropdown(id=self.IDs.RESOURCE_NAME_DROPDOWN, className='dropdown_select_column'),
                        html.Div(className='error_box', id=self.ERROR_IDs.RESOURCE_NAME_DROPDOWN),
                        html.Button('Next >>', id=self.IDs.NEXT_SELECT_PHASE_TRAIN_BTN,
                                    className='general_btn_layout', n_clicks=0)
                    ], className='columns_dropdown_cont'),

                    html.Div([
                        dbc.Fade([
                            html.P('Select KPI'),
                            dcc.RadioItems(options=get_kpi_radio_items_options(), id=self.IDs.KPI_RADIO_ITEMS),
                            html.Div(className='error_box', id=self.ERROR_IDs.KPI_RADIO_ITEMS),

                            dbc.Fade([
                                html.Div('Since the chosen KPI is to minimize activity occurrence, the system will be '
                                         'trained several times for reaching higher accuracy.',
                                         className='double_training_warning'),
                                html.Span('Activity to optimize'),
                                dcc.Dropdown(id=self.IDs.ACT_TO_OPTIMIZE_DROPDOWN, className='dropdown_select_column'),
                                html.Div(className='error_box', id=self.ERROR_IDs.ACT_TO_OPTIMIZE_DROPDOWN),
                            ], is_in=False, appear=False, id=self.IDs.FADE_ACT_TO_OPTIMIZE_DROPDOWN),

                            html.Button('<< Previous', id=self.IDs.PREV_SELECT_PHASE_TRAIN_BTN,
                                        className='general_btn_layout', n_clicks=0)

                        ], is_in=False, appear=False, id=self.IDs.FADE_KPI_RADIO_ITEMS),

                    ], className='kpi_radio_cont'),

                ], className='kpi_and_columns_cont'),

                html.Span('Select outliers threshold for transition system building'),
                html.Div([
                    dcc.Slider(id=self.IDs.OUTLIERS_THRS_SLIDER, min=0, max=1, step=0.01, marks=None,
                               updatemode='drag'),
                    # dcc.Input(id=self.IDs.SLIDER_VALUE_TEXTBOX, maxLength=4, max=1, min=0, step=0.01),
                    html.Span(id=self.IDs.OUT_THRS_SLIDER_VALUE_LABEL),
                    html.Div(className='error_box', id=self.ERROR_IDs.OUTLIERS_THRS_SLIDER),
                ], className='slider_cont'),

                dbc.Fade([
                    html.Button(
                        html.Div([html.Img(src=app.get_asset_url('spinner-white.gif'), id=self.IDs.TRAIN_SPINNER,
                                           style={'display': 'none'}, width=18, height=18, className='spinner_img'),
                                  html.Span('Train')], className='button_spinner_cont'),
                        n_clicks=0, id=self.IDs.START_TRAINING_BTN,
                        className='general_btn_layout'),

                    dbc.Fade([html.Div(id=self.IDs.TEMP_TRAINING_OUTPUT),
                              html.Div(id=self.IDs.SHOW_PROCESS_TRAINING_OUTPUT)], is_in=False, appear=False,
                             id=self.IDs.PROC_TRAIN_OUT_FADE, className='process_display_out_cont'),

                ], is_in=True, appear=False, id=self.IDs.FADE_START_TRAINING_BTN,
                    className='train_btn_proc_display_cont'),

                html.Div(className='error_box', id=self.ERROR_IDs.START_TRAINING_BTN),

            ], is_in=False, appear=False, id=self.IDs.FADE_ALL_TRAIN_CONTROLS, className='all_controls_container'),

            dbc.Fade([html.Button(['Download training files'], n_clicks=0, id=self.IDs.DOWNLOAD_TRAIN_BTN,
                                  className='general_btn_layout')],
                     id=self.IDs.DOWNLOAD_TRAIN_BTN_FADE, is_in=False, appear=False),

            dcc.Interval(id=self.IDs.PROGRESS_LOG_INTERVAL_TRAIN, n_intervals=0, interval=3000, max_intervals=-1),
        ], className='train_container')
