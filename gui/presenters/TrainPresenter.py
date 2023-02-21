import datetime
import json
import os
import shelve
import shutil
import traceback
import uuid
import diskcache

import dash
import pandas as pd
from dash import ClientsideFunction

from app import app
from dash_extensions.enrich import Input, Output, State

from gui.model.DiskDict import DiskDict
from gui.model.Experiment import Experiment, build_experiment_from_dict
from gui.model.ProgressLogger.TrainProgLogger import TrainProgLogger, build_TrainProgLogger_from_dict
from gui.model.TrainDataSource import TrainDataSource, build_TrainDataSource_from_dict
from gui.model.Trainer import Trainer, build_Trainer_from_dict
from gui.model.IO import IOManager
from gui.presenters.Presenter import Presenter
import dash_uploader as du

from gui.views import TrainView


class TrainPresenter(Presenter):
    def __init__(self, views):
        super().__init__(views)
        self.zip_files_paths = DiskDict(os.path.join(os.getcwd(), 'gui_data', 'train'), 'zip_files_paths')
        self.data_sources = DiskDict(os.path.join(os.getcwd(), 'gui_data', 'train'), 'data_sources')
        self.trainers = DiskDict(os.path.join(os.getcwd(), 'gui_data', 'train'), 'trainers')
        self.progress_loggers = DiskDict(os.path.join(os.getcwd(), 'gui_data', 'train'), 'progress_loggers')

    def clear_user_data(self, user_id):
        if self.data_sources.exists(user_id):
            data_source = build_TrainDataSource_from_dict(self.data_sources[user_id])
            data_source.free()
            data_source.free_df(user_id)
            self.data_sources.delete(user_id)
            print('deleted data source')

        if self.trainers.exists(user_id):
            self.trainers.delete(user_id)
            print('deleted trainer')

        if self.zip_files_paths.exists(user_id):
            self.zip_files_paths.delete(user_id)
            print('deleted zip file path')

        if self.progress_loggers.exists(user_id):
            build_TrainProgLogger_from_dict(self.progress_loggers[user_id]).free()  # delete file
            self.progress_loggers.delete(user_id)
            print('deleted prog logger')

    def validate_input(self, dict_values):
        # dict_values = { ex_name, kpi, id, timestamp, activity, act_to_opt }
        error_data = {}
        if 'ex_name' in dict_values and dict_values['ex_name'] is None:
            error_data[self.views['train'].IDs.EXPERIMENT_NAME_TEXTBOX] = 'Experiment name is empty'
        elif 'ex_name' in dict_values:
            if not Experiment.validate_forbidden_ex_names(dict_values['ex_name']):
                error_data[self.views['train'].IDs.EXPERIMENT_NAME_TEXTBOX] = \
                    'Experiment name cannot contain the following characters: <, >, :, ", /, \\, |, ?, *'
            elif dict_values['ex_name'].startswith('.'):
                error_data[self.views['train'].IDs.EXPERIMENT_NAME_TEXTBOX] = 'Experiment name cannot start with "."'

        if 'kpi' in dict_values and dict_values['kpi'] is None:
            error_data[self.views['train'].IDs.KPI_RADIO_ITEMS] = 'One KPI must be selected'
        if 'id' in dict_values and dict_values['id'] is None:
            error_data[self.views['train'].IDs.ID_DROPDOWN] = 'One ID column must be selected'
        if 'timestamp' in dict_values and dict_values['timestamp'] is None:
            error_data[self.views['train'].IDs.TIMESTAMP_DROPDOWN] = 'One TIMESTAMP column must be selected'
        if 'activity' in dict_values and dict_values['activity'] is None:
            error_data[self.views['train'].IDs.ACTIVITY_DROPDOWN] = 'One ACTIVITY column must be selected'
        if 'act_to_opt' in dict_values \
                and dict_values['act_to_opt'] is None \
                and dict_values['kpi'] == 'Minimize activity occurrence':
            error_data[self.views['train'].IDs.ACT_TO_OPTIMIZE_DROPDOWN] = \
                'If KPI "Minimize activity occurrence" is chosen then one ACTIVITY column to minimize must be selected'
        return error_data

    def register_callbacks(self):

        @app.callback([Output(e.value, 'children') for e in self.views['train'].ERROR_IDs],
                      Input(self.views['base'].IDs.ERRORS_MANAGER_STORE_TRAIN, 'data'),
                      prevent_initial_call=True)
        def show_error_training(error_data):
            if error_data is not None:
                # print('errors: {}'.format(error_data))
                error_data = {str(k): v for k, v in error_data.items()}
                output_values = []
                for e in self.views['train'].ERROR_IDs:
                    err_id = str(e.value)
                    elem_id = err_id.replace('_error', '')
                    if elem_id in error_data:
                        output_values.append(error_data[elem_id])
                    else:
                        output_values.append('')
                return output_values
            else:
                raise dash.exceptions.PreventUpdate

        @app.callback(Output(self.views['train'].IDs.EXPERIMENT_SELECTOR_DROPDOWN, 'options'),
                      Input(self.views['base'].IDs.LOCATION_URL, 'pathname'))
        def populate_experiment_selector_dropdown(url):
            if url == self.views['train'].pathname:
                folders_data_list = IOManager.get_experiment_folders_list(IOManager.MAIN_EXPERIMENTS_PATH)
                if folders_data_list:
                    return [{'label': d['ex_name'], 'value': d['path']} for d in folders_data_list]
                else:
                    return []
            else:
                return []

        @app.callback(Output(self.views['train'].IDs.EXPERIMENT_SELECTOR_TIME_DISPLAYER, 'children'),
                      Input(self.views['train'].IDs.EXPERIMENT_SELECTOR_DROPDOWN, 'value'))
        def show_selected_experiment_creation_timestamp(value):
            if value and os.path.isdir(value):
                ex_info_data = IOManager.read(os.path.join(value, 'experiment_info.json'))
                if 'creation_timestamp' in ex_info_data:
                    creation_timestamp = datetime.datetime.strptime(ex_info_data['creation_timestamp'],
                                                                    '%d-%m-%Y_%H-%M-%S_%f%z')
                    return 'Created: {}'.format(str(creation_timestamp.strftime('%c')))
                else:
                    return ''
            else:
                raise dash.exceptions.PreventUpdate

        @app.callback(Output(self.views['train'].IDs.LOAD_MODEL_BTN, 'disabled'),
                      State(self.views['train'].IDs.EXPERIMENT_SELECTOR_DROPDOWN, 'options'),
                      Input(self.views['train'].IDs.EXPERIMENT_SELECTOR_DROPDOWN, 'value'))
        def disable_load_model_btn(options, value):
            return not options or not value  # disable if options == [] or value == '', else enable it

        @app.callback([Output(self.views['base'].IDs.EXPERIMENT_DATA_STORE, 'data'),
                       Output(self.views['train'].IDs.EXPERIMENT_NAME_TEXTBOX, 'value'),
                       Output(self.views['train'].IDs.KPI_RADIO_ITEMS, 'value'),
                       Output(self.views['train'].IDs.ID_DROPDOWN, 'value'),
                       Output(self.views['train'].IDs.TIMESTAMP_DROPDOWN, 'value'),
                       Output(self.views['train'].IDs.ACTIVITY_DROPDOWN, 'value'),
                       Output(self.views['train'].IDs.RESOURCE_NAME_DROPDOWN, 'value'),
                       Output(self.views['train'].IDs.ACT_TO_OPTIMIZE_DROPDOWN, 'value'),
                       Output(self.views['train'].IDs.OUTLIERS_THRS_SLIDER, 'value'),
                       # populate options
                       Output(self.views['train'].IDs.KPI_RADIO_ITEMS, 'options'),
                       Output(self.views['train'].IDs.ID_DROPDOWN, 'options'),
                       Output(self.views['train'].IDs.TIMESTAMP_DROPDOWN, 'options'),
                       Output(self.views['train'].IDs.ACTIVITY_DROPDOWN, 'options'),
                       Output(self.views['train'].IDs.RESOURCE_NAME_DROPDOWN, 'options'),
                       Output(self.views['train'].IDs.ACT_TO_OPTIMIZE_DROPDOWN, 'options'),
                       # READ-ONLY props
                       Output(self.views['train'].IDs.EXPERIMENT_NAME_TEXTBOX, 'readOnly'),
                       Output(self.views['train'].IDs.ID_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.TIMESTAMP_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.ACTIVITY_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.RESOURCE_NAME_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.ACT_TO_OPTIMIZE_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.OUTLIERS_THRS_SLIDER, 'disabled'),
                       # FADEs
                       Output(self.views['train'].IDs.FADE_ALL_TRAIN_CONTROLS, 'is_in'),
                       Output(self.views['train'].IDs.FADE_ACT_TO_OPTIMIZE_DROPDOWN, 'is_in'),
                       Output(self.views['train'].IDs.FADE_START_TRAINING_BTN, 'is_in'),
                       Output(self.views['train'].IDs.FADE_KPI_RADIO_ITEMS, 'is_in'),
                       Output(self.views['train'].IDs.DOWNLOAD_TRAIN_BTN_FADE, 'is_in'),
                       # btns
                       Output(self.views['train'].IDs.NEXT_SELECT_PHASE_TRAIN_BTN, 'disabled'),
                       Output(self.views['train'].IDs.PREV_SELECT_PHASE_TRAIN_BTN, 'disabled'),
                       # GO NEXT BTN
                       Output(self.views['base'].IDs.GO_NEXT_BTN, 'disabled'),
                       # CONTROLS DISABLED
                       Output(self.views['train'].IDs.TRAIN_FILE_UPLOADER, 'disabled'),
                       Output(self.views['train'].IDs.LOAD_MODEL_BTN, 'disabled'),
                       Output(self.views['train'].IDs.EXPERIMENT_SELECTOR_DROPDOWN, 'disabled')],
                      [State(self.views['train'].IDs.EXPERIMENT_SELECTOR_DROPDOWN, 'value'),
                       State(self.views['base'].IDs.USER_ID, 'data')],
                      Input(self.views['train'].IDs.LOAD_MODEL_BTN, 'n_clicks'),
                      prevent_initial_call=True)
        def load_trained_model_data(ex_folder_path, user_id, n_clicks):
            if n_clicks > 0:
                ex_info_data = IOManager.read(os.path.join(ex_folder_path, 'experiment_info.json'))
                creation_timestamp = datetime.datetime.now(datetime.timezone.utc).strftime('%d-%m-%Y_%H-%M-%S_%f%z')
                ex_info_data['creation_timestamp'] = str(creation_timestamp)
                ex_info = build_experiment_from_dict(ex_info_data)
                dest_path = os.path.join(os.path.split(ex_folder_path)[0],
                                         '{}--{}'.format(ex_info.ex_name, ex_info.creation_timestamp))
                shutil.copytree(ex_folder_path, dest_path)

                trainer = Trainer(ex_info, None)  # used only for generating archive TODO: REFACTOR
                self.zip_files_paths[user_id] = trainer.create_model_archive()
                trainer.write_experiment_info()
                print(ex_info)
                kpi_options = TrainView.get_kpi_radio_items_options(True)

                if ex_info.act_to_opt is None:
                    act_to_opt_data = dash.no_update
                    act_to_opt_options = dash.no_update
                    show_act_to_opt_dropdown = False
                else:
                    act_to_opt_data = ex_info.act_to_opt
                    act_to_opt_options = [ex_info.act_to_opt]
                    show_act_to_opt_dropdown = True

                if ex_info.resource is None:
                    resource_dropdown_options = []
                else:
                    resource_dropdown_options = [ex_info.resource]

                return [json.dumps(ex_info_data), ex_info.ex_name, ex_info.kpi, ex_info.id, ex_info.timestamp,
                        ex_info.activity, ex_info.resource, act_to_opt_data, ex_info.out_thrs] + \
                       [kpi_options, [ex_info.id], [ex_info.timestamp], [ex_info.activity], resource_dropdown_options,
                        act_to_opt_options, True, True, True, True, True, True, True, True, show_act_to_opt_dropdown,
                        False, True, True, True, True, False, True, True, True]
            else:
                return [dash.no_update] * 33

        @du.callback(
            output=[Output(self.views['train'].IDs.LOAD_TRAIN_FILE_BTN_FADE, 'is_in'),
                    Output(self.views['base'].IDs.TRAIN_FILE_PATH_STORE, 'data'),
                    Output(self.views['train'].IDs.LOAD_MODEL_BTN, 'disabled')],
            id=self.views['train'].IDs.TRAIN_FILE_UPLOADER
        )
        def on_train_file_upload_complete(status):
            print(status)
            print('Upload train file completed')
            if status.is_completed:
                return [True, str(status.latest_file), True]
            else:
                return [False, dash.no_update, dash.no_update]

        @app.callback(
            output=[Output(self.views['base'].IDs.ERRORS_MANAGER_STORE_TRAIN, 'data'),
                    # options
                    Output(self.views['train'].IDs.ID_DROPDOWN, 'options'),
                    Output(self.views['train'].IDs.TIMESTAMP_DROPDOWN, 'options'),
                    Output(self.views['train'].IDs.ACTIVITY_DROPDOWN, 'options'),
                    Output(self.views['train'].IDs.RESOURCE_NAME_DROPDOWN, 'options'),
                    Output(self.views['train'].IDs.ACT_TO_OPTIMIZE_DROPDOWN, 'options'),
                    # values
                    Output(self.views['train'].IDs.OUTLIERS_THRS_SLIDER, 'value'),
                    Output(self.views['train'].IDs.ID_DROPDOWN, 'value'),
                    Output(self.views['train'].IDs.TIMESTAMP_DROPDOWN, 'value'),
                    Output(self.views['train'].IDs.ACTIVITY_DROPDOWN, 'value'),
                    Output(self.views['train'].IDs.RESOURCE_NAME_DROPDOWN, 'value'),
                    # disable
                    Output(self.views['train'].IDs.ID_DROPDOWN, 'disabled'),
                    Output(self.views['train'].IDs.TIMESTAMP_DROPDOWN, 'disabled'),
                    Output(self.views['train'].IDs.ACTIVITY_DROPDOWN, 'disabled'),
                    Output(self.views['train'].IDs.RESOURCE_NAME_DROPDOWN, 'disabled'),
                    Output(self.views['train'].IDs.NEXT_SELECT_PHASE_TRAIN_BTN, 'disabled'),
                    Output(self.views['train'].IDs.PREV_SELECT_PHASE_TRAIN_BTN, 'disabled'),
                    Output(self.views['train'].IDs.LOAD_TRAIN_FILE_BTN, 'disabled'),
                    Output(self.views['train'].IDs.LOAD_MODEL_BTN, 'disabled'),
                    Output(self.views['train'].IDs.EXPERIMENT_SELECTOR_DROPDOWN, 'disabled'),

                    Output(self.views['train'].IDs.FADE_KPI_RADIO_ITEMS, 'is_in'),
                    Output(self.views['train'].IDs.FADE_ALL_TRAIN_CONTROLS, 'is_in')],

            inputs=[State(self.views['base'].IDs.TRAIN_FILE_PATH_STORE, 'data'),
                    State(self.views['base'].IDs.USER_ID, 'data'),
                    Input(self.views['train'].IDs.LOAD_TRAIN_FILE_BTN, 'n_clicks')],
            running=[
                (Output(self.views['train'].IDs.LOAD_TRAIN_SPINNER, 'style'),
                 {'display': 'inline'}, {'display': 'none'}),
                (Output(self.views['train'].IDs.LOAD_TRAIN_FILE_BTN, 'disabled'), True, False),
            ],
            background=True,
            prevent_initial_call=True
        )
        def populate_dropdown_options(train_file_path, user_id, n_clicks):
            DEFAULT_OUTLIER_THRS = 0.02
            if n_clicks > 0:
                error_data = {}
                try:
                    train_data_source = TrainDataSource(train_file_path)
                except (pd.errors.ParserError, pd.errors.EmptyDataError, ValueError) as e:
                    print(traceback.format_exc())
                    error_data[self.views['train'].IDs.LOAD_TRAIN_FILE_BTN] = '{}: {}'.format(type(e).__name__, e)
                    return [error_data] + [dash.no_update] * 20 + [False]

                self.data_sources[user_id] = train_data_source.to_dict(user_id)
                options_group = train_data_source.columns_list

                if train_data_source.is_xes:
                    xes_cols_data = train_data_source.xes_columns_names
                    return [error_data] + [options_group] * 4 + \
                           [train_data_source.get_activity_list(xes_cols_data['activity']),
                            DEFAULT_OUTLIER_THRS] + [xes_cols_data['id'],
                                                     xes_cols_data['timestamp'],
                                                     xes_cols_data['activity'],
                                                     xes_cols_data['resource'], ] + [True] * 11
                else:
                    return [error_data] + [options_group] * 4 + \
                           [dash.no_update, DEFAULT_OUTLIER_THRS] + [dash.no_update] * 10 + \
                           [True, True, True, dash.no_update, True]

            else:
                return [dash.no_update] * 21 + [False]

        @app.callback(Output(self.views['train'].IDs.FADE_ACT_TO_OPTIMIZE_DROPDOWN, 'is_in'),
                      Input(self.views['train'].IDs.KPI_RADIO_ITEMS, 'value'),
                      prevent_initial_call=True)
        def show_choose_act_to_opt_dropdown(value):
            return value in ['Maximize activity occurrence', 'Minimize activity occurrence']

        @app.callback([Output(self.views['train'].IDs.ACT_TO_OPTIMIZE_DROPDOWN, 'options'),
                       Output(self.views['train'].IDs.FADE_KPI_RADIO_ITEMS, 'is_in'),
                       Output(self.views['base'].IDs.ERRORS_MANAGER_STORE_TRAIN, 'data'),
                       Output(self.views['train'].IDs.ID_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.TIMESTAMP_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.ACTIVITY_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.RESOURCE_NAME_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.KPI_RADIO_ITEMS, 'options'),
                       Output(self.views['train'].IDs.ACT_TO_OPTIMIZE_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.NEXT_SELECT_PHASE_TRAIN_BTN, 'disabled'),
                       Output(self.views['train'].IDs.PREV_SELECT_PHASE_TRAIN_BTN, 'disabled')],
                      [State(self.views['train'].IDs.ID_DROPDOWN, 'value'),
                       State(self.views['train'].IDs.TIMESTAMP_DROPDOWN, 'value'),
                       State(self.views['train'].IDs.ACTIVITY_DROPDOWN, 'value'),
                       State(self.views['train'].IDs.RESOURCE_NAME_DROPDOWN, 'value'),
                       State(self.views['base'].IDs.USER_ID, 'data')],
                      Input(self.views['train'].IDs.NEXT_SELECT_PHASE_TRAIN_BTN, 'n_clicks'),
                      prevent_initial_call=True)
        def go_2nd_phase_train_option_selection(_id, timestamp, activity, resource, user_id, n_clicks):
            if n_clicks > 0:
                error_data = self.validate_input({'id': _id,
                                                  'timestamp': timestamp,
                                                  'activity': activity})
                if not error_data:
                    act_list = build_TrainDataSource_from_dict(
                        self.data_sources[user_id], load_df=True
                    ).get_activity_list(activity)
                    return [act_list, True, error_data] + [True] * 4 + \
                           [TrainView.get_kpi_radio_items_options(False), False, True, False]
                else:
                    return [[], False, error_data] + [False] * 4 + \
                           [TrainView.get_kpi_radio_items_options(True), True, False, False]
            else:
                return [dash.no_update] * 11

        @app.callback([Output(self.views['train'].IDs.ID_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.TIMESTAMP_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.ACTIVITY_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.RESOURCE_NAME_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.KPI_RADIO_ITEMS, 'options'),
                       Output(self.views['train'].IDs.ACT_TO_OPTIMIZE_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.NEXT_SELECT_PHASE_TRAIN_BTN, 'disabled'),
                       Output(self.views['train'].IDs.PREV_SELECT_PHASE_TRAIN_BTN, 'disabled')],
                      Input(self.views['train'].IDs.PREV_SELECT_PHASE_TRAIN_BTN, 'n_clicks'),
                      prevent_initial_call=True)
        def return_1st_phase_train_option_selection(n_clicks):
            if n_clicks > 0:
                return [False] * 4 + [TrainView.get_kpi_radio_items_options(True), True, False, True]
            else:
                return [dash.no_update] * 8

        app.clientside_callback(
            ClientsideFunction(
                namespace='clientside',
                function_name='slider_value_display_csc_percent'
            ),
            Output(self.views['train'].IDs.OUT_THRS_SLIDER_VALUE_LABEL, 'children'),
            Input(self.views['train'].IDs.OUTLIERS_THRS_SLIDER, 'value')
        )

        @app.callback([Output(self.views['base'].IDs.START_TRAINING_CONTROLLER, 'data'),
                       Output(self.views['base'].IDs.EXPERIMENT_DATA_STORE, 'data'),
                       Output(self.views['train'].IDs.PROC_TRAIN_OUT_FADE, 'is_in'),
                       Output(self.views['base'].IDs.ERRORS_MANAGER_STORE_TRAIN, 'data'),
                       # READ-ONLY props
                       Output(self.views['train'].IDs.EXPERIMENT_NAME_TEXTBOX, 'readOnly'),
                       Output(self.views['train'].IDs.ID_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.TIMESTAMP_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.ACTIVITY_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.RESOURCE_NAME_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.ACT_TO_OPTIMIZE_DROPDOWN, 'disabled'),
                       Output(self.views['train'].IDs.OUTLIERS_THRS_SLIDER, 'disabled'),
                       # btns
                       Output(self.views['train'].IDs.NEXT_SELECT_PHASE_TRAIN_BTN, 'disabled'),
                       Output(self.views['train'].IDs.PREV_SELECT_PHASE_TRAIN_BTN, 'disabled'),

                       Output(self.views['train'].IDs.KPI_RADIO_ITEMS, 'options')],
                      [State(self.views['train'].IDs.EXPERIMENT_NAME_TEXTBOX, 'value'),
                       State(self.views['train'].IDs.KPI_RADIO_ITEMS, 'value'),
                       State(self.views['train'].IDs.ID_DROPDOWN, 'value'),
                       State(self.views['train'].IDs.TIMESTAMP_DROPDOWN, 'value'),
                       State(self.views['train'].IDs.ACTIVITY_DROPDOWN, 'value'),
                       State(self.views['train'].IDs.RESOURCE_NAME_DROPDOWN, 'value'),
                       State(self.views['train'].IDs.ACT_TO_OPTIMIZE_DROPDOWN, 'value'),
                       State(self.views['train'].IDs.OUTLIERS_THRS_SLIDER, 'value'),
                       State(self.views['base'].IDs.USER_ID, 'data')],
                      Input(self.views['train'].IDs.START_TRAINING_BTN, 'n_clicks'),
                      prevent_initial_call=True)
        def collect_training_user_data(ex_name, kpi, _id, timestamp, activity, resource, act_to_opt, out_thrs, user_id,
                                       n_clicks):
            if n_clicks > 0:
                error_data = self.validate_input({'ex_name': ex_name,
                                                  'kpi': kpi,
                                                  'id': _id,
                                                  'timestamp': timestamp,
                                                  'activity': activity,
                                                  'act_to_opt': act_to_opt})
                if not error_data:
                    experiment_info = Experiment(ex_name, kpi, _id, timestamp, activity, resource, act_to_opt, out_thrs,
                                                 datetime.datetime.now(
                                                     datetime.timezone.utc
                                                 ).strftime('%d-%m-%Y_%H-%M-%S_%f%z'))
                    print(experiment_info)
                    trainer = Trainer(experiment_info, build_TrainDataSource_from_dict(self.data_sources[user_id]))
                    self.trainers[user_id] = trainer.to_dict(user_id)
                    trainer.write_experiment_info()

                    self.progress_loggers[user_id] = TrainProgLogger(str(uuid.uuid4())).to_dict()
                    kpi_options = TrainView.get_kpi_radio_items_options(disabled=True)
                    return [True, json.dumps(experiment_info.to_dict()), True, error_data] + [True] * 9 + [kpi_options]
                else:
                    return [dash.no_update, dash.no_update, dash.no_update, error_data] + [dash.no_update] * 10
            else:
                return [dash.no_update] * 14

        @app.callback(
            output=[Output(self.views['train'].IDs.TEMP_TRAINING_OUTPUT, 'children'),
                    Output(self.views['train'].IDs.SHOW_PROCESS_TRAINING_OUTPUT, 'style'),
                    Output(self.views['train'].IDs.DOWNLOAD_TRAIN_BTN_FADE, 'is_in'),
                    Output(self.views['train'].IDs.START_TRAINING_BTN, 'disabled'),
                    Output(self.views['base'].IDs.GO_NEXT_BTN, 'disabled')],
            inputs=[Input(self.views['base'].IDs.START_TRAINING_CONTROLLER, 'data'),
                    State(self.views['base'].IDs.USER_ID, 'data')],
            background=True,
            prevent_initial_call=True,
            running=[
                (Output(self.views['train'].IDs.TRAIN_SPINNER, 'style'),
                 {'display': 'inline'}, {'display': 'none'}),
                # (Output(self.views['train'].IDs.DOWNLOAD_TRAIN_BTN_FADE, 'is_in'), False, True),
                (Output(self.views['train'].IDs.PROGRESS_LOG_INTERVAL_TRAIN, 'max_intervals'), -1, 0),
                (Output(self.views['train'].IDs.START_TRAINING_BTN, 'disabled'), True, False)
            ],
            cancel=[Input(self.views['base'].IDs.LOCATION_URL, 'pathname')]
        )
        def train_model(start_cont_store, user_id):
            if start_cont_store:
                trainer = build_Trainer_from_dict(self.trainers[user_id], load_data_source=True)
                progress_logger = build_TrainProgLogger_from_dict(self.progress_loggers[user_id])

                progress_logger.clear_stack()
                progress_logger.add_to_stack('Preparing dataset...')

                try:
                    trainer.prepare_dataset()
                except (pd.errors.ParserError, ValueError) as e:
                    return ['An error occurred: {}: {}'.format(type(e).__name__, e), {'display': 'none'}, False, False,
                            True]

                progress_logger.add_to_stack('Starting training...')
                trainer.train(progress_logger)

                progress_logger.add_to_stack('Generating variables...')
                trainer.generate_variables()

                progress_logger.add_to_stack('Generating archives...')
                self.zip_files_paths[user_id] = trainer.create_model_archive()

                progress_logger.clear_stack()

                return ['Training completed', {'display': 'none'}, True, True, False]
            else:
                return [dash.no_update] * 5

        @app.callback(Output(self.views['base'].IDs.DOWNLOAD_TRAIN, 'data'),
                      State(self.views['base'].IDs.USER_ID, 'data'),
                      Input(self.views['train'].IDs.DOWNLOAD_TRAIN_BTN, 'n_clicks'),
                      prevent_initial_call=True)
        def download_train_files(user_id, n_clicks):
            if n_clicks > 0:
                if self.zip_files_paths[user_id]:
                    return dash.dcc.send_file(self.zip_files_paths[user_id])
                else:
                    raise dash.exceptions.PreventUpdate
            else:
                raise dash.exceptions.PreventUpdate

        @app.callback(Output(self.views['train'].IDs.SHOW_PROCESS_TRAINING_OUTPUT, 'children'),
                      State(self.views['base'].IDs.USER_ID, 'data'),
                      Input(self.views['train'].IDs.PROGRESS_LOG_INTERVAL_TRAIN, 'n_intervals'),
                      prevent_initial_call=True)
        def update_training_progress(user_id, n_intervals):
            if n_intervals > 0:
                t = None
                try:
                    t = build_TrainProgLogger_from_dict(self.progress_loggers[user_id]).get_from_stack()
                except:
                    pass

                if t:
                    return t
                else:
                    raise dash.exceptions.PreventUpdate
            else:
                raise dash.exceptions.PreventUpdate
