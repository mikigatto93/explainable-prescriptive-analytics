import uuid

from strenum import StrEnum
from dash_extensions.enrich import html, dcc, Output, Input, dcc
import dash_bootstrap_components as dbc

from app import app

from gui.views.View import View
import dash_uploader as du


class _IDs(StrEnum):
    FADE_START_TRAINING_BTN = 'fade_start_train_btn',
    EXPERIMENT_SELECTOR_DROPDOWN = 'exp_selector_dropdown',
    DOWNLOAD_TRAIN_BTN = 'download_train_btn',
    DOWNLOAD_TRAIN_BTN_FADE = 'download_train_btn_fade',
    TRAIN_SPINNER = 'train_spinner',
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


class TrainView(View):
    def __init__(self, pathname='', order=-1):
        super().__init__(pathname, order)
        self.IDs = _IDs
        self.ERROR_IDs = _ERROR_IDs
        self.error_IDs = []
        # gen_id =
        # print(gen_id)
        self.upload_id = str(uuid.uuid4())

    def get_err_id(self, elem_id):
        if elem_id in self.IDs:
            _id = '{}_error_box'.format(elem_id)
            self.error_IDs.append(_id)
            return _id
        else:
            raise KeyError('No id found')

    def get_layout(self):
        return html.Div([
            html.H1('Train'),
            # html.Div('Click to select the training file', n_clicks=0, id=self.IDs.LOAD_FILE_AREA),
            html.Div([
                html.Div([
                    du.Upload(id=self.IDs.TRAIN_FILE_UPLOADER, upload_id=self.upload_id, filetypes=['csv', 'xes']),
                    html.Button('Load file', id=self.IDs.LOAD_TRAIN_FILE_BTN, n_clicks=0, disabled=True,
                                className='general_btn_layout'),
                    html.Div(className='error_box', id=self.ERROR_IDs.LOAD_TRAIN_FILE_BTN),
                ], className='load_train_file_cont'),
                html.Div([
                    html.Span('Select one experiment:'),
                    dcc.Dropdown(id=self.IDs.EXPERIMENT_SELECTOR_DROPDOWN, className='dropdown_select_column'),
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
                        html.P('Select KPI'),
                        dcc.RadioItems([
                            'Total time',
                            # 'Maximize activity occurrence',
                            'Minimize activity occurrence'
                        ], id=self.IDs.KPI_RADIO_ITEMS),
                        html.Div(className='error_box', id=self.ERROR_IDs.KPI_RADIO_ITEMS),
                    ], className='kpi_radio_cont'),
                    html.Div([
                        html.P('Select columns:'),
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
                        dbc.Fade([
                            html.Span('Activity to optimize'),
                            dcc.Dropdown(id=self.IDs.ACT_TO_OPTIMIZE_DROPDOWN, className='dropdown_select_column'),
                            html.Div(className='error_box', id=self.ERROR_IDs.ACT_TO_OPTIMIZE_DROPDOWN),
                        ], is_in=False, appear=False, id=self.IDs.FADE_ACT_TO_OPTIMIZE_DROPDOWN),
                    ], className='columns_dropdown_cont'),
                ], className='kpi_and_columns_cont'),
                html.Span('Select outliers threshold'),
                html.Div([
                    dcc.Slider(id=self.IDs.OUTLIERS_THRS_SLIDER, min=0, max=1, step=0.01, marks=None),
                    # dcc.Input(id=self.IDs.SLIDER_VALUE_TEXTBOX, maxLength=4, max=1, min=0, step=0.01),
                    html.Span(id=self.IDs.OUT_THRS_SLIDER_VALUE_LABEL),
                    html.Div(className='error_box', id=self.ERROR_IDs.OUTLIERS_THRS_SLIDER),
                ], className='slider_cont'),
                
                dbc.Fade([
                    html.Button(
                        html.Div([html.Img(src=app.get_asset_url('spinner-white.gif'), id=self.IDs.TRAIN_SPINNER,
                                           style={'display': 'inline'}, width=18, height=18, className='spinner_img'),
                                  html.Span('Train')], className='button_spinner_cont'),
                        n_clicks=0, id=self.IDs.START_TRAINING_BTN,
                        className='general_btn_layout'),
                    html.Div(className='error_box', id=self.ERROR_IDs.START_TRAINING_BTN),
                ], is_in=True, appear=False, id=self.IDs.FADE_START_TRAINING_BTN),
            ], is_in=False, appear=False, id=self.IDs.FADE_ALL_TRAIN_CONTROLS, className='all_controls_container'),
            dbc.Fade([html.Button(['Download training files'], n_clicks=0, id=self.IDs.DOWNLOAD_TRAIN_BTN,
                                  className='general_btn_layout')],
                     id=self.IDs.DOWNLOAD_TRAIN_BTN_FADE, is_in=True, appear=False),
            dbc.Fade([html.Div(id=self.IDs.TEMP_TRAINING_OUTPUT),
                      html.Div(id=self.IDs.SHOW_PROCESS_TRAINING_OUTPUT)], is_in=False, appear=False,
                     id=self.IDs.PROC_TRAIN_OUT_FADE, className='process_display_out_cont'),
            dcc.Interval(id=self.IDs.PROGRESS_LOG_INTERVAL, n_intervals=0, interval=1000),
        ], className='view_container')
