import json
import os

import dash
from dash import ClientsideFunction

from app import app
from dash_extensions.enrich import Input, Output, State

from gui.model.Experiment import Experiment, build_experiment_from_dict
from gui.model.ProgressLogger.TrainProgLogger import TrainProgLogger
from gui.model.TrainDataSource import TrainDataSource
from gui.model.Trainer import Trainer
from gui.model.IO import IOManager
from gui.presenters.Presenter import Presenter
import dash_uploader as du

from gui.views import TrainView


class TrainPresenter(Presenter):
    def __init__(self, views):
        super().__init__(views)
        self.zip_file_path = None
        self.data_source = None
        self.file_path = None
        self.trainer = None
        self.progress_logger = TrainProgLogger('train_progress.tmp')

    def __validate_input(self, dict_values):
        # dict_values = { ex_name, kpi, id, timestamp, activity, act_to_opt }
        error_data = {}
        if 'ex_name' in dict_values and dict_values['ex_name'] is None:
            error_data[self.views['train'].IDs.EXPERIMENT_NAME_TEXTBOX] = 'Experiment name is empty'
        elif 'ex_name' in dict_values:
            if not Experiment.validate_forbidden_ex_names(dict_values['ex_name']):
                error_data[self.views['train'].IDs.EXPERIMENT_NAME_TEXTBOX] = \
                    'Experiment name cannot contain the following characters: <, >, :, ", /, \\, |, ?, *'

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
                      Input(self.views['base'].IDs.ERRORS_MANAGER_STORE, 'data'),
                      prevent_initial_call=True)
        def show_error_training(error_data):
            print(error_data)

            l = [Output(e.value, 'children') for e in self.views['train'].ERROR_IDs]
            print(l)
            if error_data is not None:
                output_values = []
                for e in self.views['train'].ERROR_IDs:
                    err_id = str(e.value)
                    elem_id = err_id.replace('_error', '')
                    print(elem_id)
                    if elem_id in error_data:
                        output_values.append(error_data[elem_id])
                    else:
                        output_values.append('')
                print(output_values)
                return output_values
            else:
                raise dash.exceptions.PreventUpdate

        @app.callback(Output(self.views['base'].IDs.ARROW_CONTROLLER_STORE, 'data'),
                      Input(self.views['base'].IDs.LOCATION_URL, 'pathname'))
        def disable_go_next_page_at_start(url):
            # print(url)
            if url == self.views['train'].pathname:
                return {'go_next_disabled_status': True,
                        'go_back_disabled_status': 'no_update'}
            else:
                raise dash.exceptions.PreventUpdate

        @app.callback(Output(self.views['train'].IDs.EXPERIMENT_SELECTOR_DROPDOWN, 'options'),
                      Input(self.views['base'].IDs.LOCATION_URL, 'pathname'))
        def populate_experiment_selector_dropdown(url):
            if url == self.views['train'].pathname:
                return IOManager.get_experiment_folders_list(IOManager.MAIN_EXPERIMENTS_PATH)
            else:
                return []

        @app.callback(Output(self.views['train'].IDs.LOAD_MODEL_BTN, 'disabled'),
                      [Input(self.views['train'].IDs.EXPERIMENT_SELECTOR_DROPDOWN, 'options'),
                       Input(self.views['train'].IDs.EXPERIMENT_SELECTOR_DROPDOWN, 'value')])
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
                       Output(self.views['train'].IDs.FADE_ALL_TRAIN_CONTROLS, 'is_in'),
                       Output(self.views['train'].IDs.FADE_ACT_TO_OPTIMIZE_DROPDOWN, 'is_in'),
                       Output(self.views['train'].IDs.FADE_START_TRAINING_BTN, 'is_in')],
                      State(self.views['train'].IDs.EXPERIMENT_SELECTOR_DROPDOWN, 'value'),
                      Input(self.views['train'].IDs.LOAD_MODEL_BTN, 'n_clicks'))
        def load_trained_model_data(ex_name_val, n_clicks):
            if n_clicks > 0:
                experiment_data_path = os.path.join(ex_name_val, IOManager.Paths.EXPERIMENT_DATA)
                ex_info_data = IOManager.read(os.path.join(IOManager.MAIN_EXPERIMENTS_PATH, experiment_data_path))
                ex_info = build_experiment_from_dict(ex_info_data)
                self.trainer = Trainer(ex_info, None)  # used only for generating the zip and download TODO: REFACTOR
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
                        act_to_opt_options, True, True, True, True, True, True, True, True, False,
                        show_act_to_opt_dropdown]
            else:
                return [dash.no_update] * 25

        @du.callback(
            output=Output(self.views['train'].IDs.LOAD_TRAIN_FILE_BTN, 'disabled'),
            id=self.views['train'].IDs.TRAIN_FILE_UPLOADER
        )
        def on_train_file_upload_complete(status):
            print(status)
            print('Upload train file completed')
            self.file_path = str(status.latest_file)
            return False

        @app.callback(Output(self.views['train'].IDs.FADE_ALL_TRAIN_CONTROLS, 'is_in'),
                      Input(self.views['train'].IDs.LOAD_TRAIN_FILE_BTN, 'n_clicks'),
                      prevent_initial_call=True)
        def show_all_controls(n_clicks):
            if n_clicks > 0:
                try:
                    self.data_source = TrainDataSource(self.file_path)
                except Exception as e:
                    print(e)
                    return False

                return True

        @app.callback([Output(self.views['train'].IDs.ID_DROPDOWN, 'options'),
                       Output(self.views['train'].IDs.TIMESTAMP_DROPDOWN, 'options'),
                       Output(self.views['train'].IDs.ACTIVITY_DROPDOWN, 'options'),
                       Output(self.views['train'].IDs.RESOURCE_NAME_DROPDOWN, 'options'),
                       Output(self.views['train'].IDs.OUTLIERS_THRS_SLIDER, 'value')],
                      Input(self.views['train'].IDs.FADE_ALL_TRAIN_CONTROLS, 'is_in'),
                      prevent_initial_call=True)
        def populate_dropdown_options(fade):
            DEFAULT_OUTLIER_THRS = 0.05
            if fade and self.data_source:
                options_group = self.data_source.columns_list
                return [options_group] * 4 + [DEFAULT_OUTLIER_THRS]
            else:
                raise dash.exceptions.PreventUpdate

        @app.callback(Output(self.views['train'].IDs.FADE_ACT_TO_OPTIMIZE_DROPDOWN, 'is_in'),
                      Input(self.views['train'].IDs.KPI_RADIO_ITEMS, 'value'),
                      prevent_initial_call=True)
        def show_choose_act_to_opt_dropdown(value):
            return value in ['Maximize activity occurrence', 'Minimize activity occurrence']

        @app.callback([Output(self.views['train'].IDs.ACT_TO_OPTIMIZE_DROPDOWN, 'options'),
                       Output(self.views['train'].IDs.FADE_KPI_RADIO_ITEMS, 'is_in'),
                       Output(self.views['base'].IDs.ERRORS_MANAGER_STORE, 'data'),
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
                       State(self.views['train'].IDs.RESOURCE_NAME_DROPDOWN, 'value')],
                      Input(self.views['train'].IDs.NEXT_SELECT_PHASE_TRAIN_BTN, 'n_clicks'),
                      prevent_initial_call=True)
        def go_2nd_phase_train_option_selection(_id, timestamp, activity, resource, n_clicks):
            if n_clicks > 0:
                error_data = self.__validate_input({'id': _id,
                                                    'timestamp': timestamp,
                                                    'activity': activity})
                if not error_data:
                    act_list = self.data_source.get_activity_list(activity)
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
                function_name='slider_value_display_csc'
            ),
            Output(self.views['train'].IDs.OUT_THRS_SLIDER_VALUE_LABEL, 'children'),
            Input(self.views['train'].IDs.OUTLIERS_THRS_SLIDER, 'value')
        )

        @app.callback([Output(self.views['base'].IDs.START_TRAINING_CONTROLLER, 'data'),
                       Output(self.views['base'].IDs.EXPERIMENT_DATA_STORE, 'data'),
                       Output(self.views['train'].IDs.PROC_TRAIN_OUT_FADE, 'is_in'),
                       Output(self.views['base'].IDs.ERRORS_MANAGER_STORE, 'data')],
                      [State(self.views['train'].IDs.EXPERIMENT_NAME_TEXTBOX, 'value'),
                       State(self.views['train'].IDs.KPI_RADIO_ITEMS, 'value'),
                       State(self.views['train'].IDs.ID_DROPDOWN, 'value'),
                       State(self.views['train'].IDs.TIMESTAMP_DROPDOWN, 'value'),
                       State(self.views['train'].IDs.ACTIVITY_DROPDOWN, 'value'),
                       State(self.views['train'].IDs.RESOURCE_NAME_DROPDOWN, 'value'),
                       State(self.views['train'].IDs.ACT_TO_OPTIMIZE_DROPDOWN, 'value'),
                       State(self.views['train'].IDs.OUTLIERS_THRS_SLIDER, 'value')],
                      Input(self.views['train'].IDs.START_TRAINING_BTN, 'n_clicks'),
                      prevent_initial_call=True)
        def collect_training_user_data(ex_name, kpi, _id, timestamp, activity, resource, act_to_opt, out_thrs,
                                       n_clicks):
            if n_clicks > 0:
                error_data = self.__validate_input({'ex_name': ex_name,
                                                    'kpi': kpi,
                                                    'id': _id,
                                                    'timestamp': timestamp,
                                                    'activity': activity,
                                                    'act_to_opt': act_to_opt})
                if not error_data:
                    experiment_info = Experiment(ex_name, kpi, _id, timestamp, activity, resource, act_to_opt, out_thrs)
                    print(experiment_info)
                    self.trainer = Trainer(experiment_info, self.data_source)
                    self.trainer.write_experiment_info()
                    self.progress_logger.clear_stack()
                    return [True, json.dumps(experiment_info.to_dict()), True, error_data]
                else:
                    return [dash.no_update, dash.no_update, dash.no_update, error_data]
            else:
                return [dash.no_update] * 4

        @app.callback(
            output=[Output(self.views['train'].IDs.TEMP_TRAINING_OUTPUT, 'children'),
                    Output(self.views['train'].IDs.SHOW_PROCESS_TRAINING_OUTPUT, 'style')],
            inputs=Input(self.views['base'].IDs.START_TRAINING_CONTROLLER, 'data'),
            background=True,
            prevent_initial_call=True,
            running=[
                (Output(self.views['train'].IDs.TRAIN_SPINNER, 'style'),
                 {'display': 'inline'}, {'display': 'none'}),
                (Output(self.views['train'].IDs.DOWNLOAD_TRAIN_BTN_FADE, 'is_in'), False, True),
                (Output(self.views['train'].IDs.PROGRESS_LOG_INTERVAL, 'max_intervals'), -1, 0),
            ]
        )
        def train_model(start_cont_store):
            if start_cont_store:
                self.progress_logger.clear_stack()
                self.progress_logger.add_to_stack('Preparing dataset...')
                self.trainer.prepare_dataset()

                self.progress_logger.add_to_stack('Starting training...')
                self.trainer.train(self.progress_logger)

                self.progress_logger.add_to_stack('Generating variables...')
                self.trainer.generate_variables()
                # self.zip_file_path = self.trainer.create_model_archive()
                self.progress_logger.clear_stack()
                return ['Training completed', {'display': 'none'}]
            else:
                raise dash.exceptions.PreventUpdate

        @app.callback(Output(self.views['base'].IDs.DOWNLOAD_TRAIN, 'data'),
                      Input(self.views['train'].IDs.DOWNLOAD_TRAIN_BTN, 'n_clicks'),
                      prevent_initial_call=True)
        def download_train_files(n_clicks):
            if n_clicks > 0:
                # TODO: MAYBE THIS CAN BE MOVED INSIDE THE TRAINIG PROCESS
                self.zip_file_path = self.trainer.create_model_archive()

                return dash.dcc.send_file(self.zip_file_path)
            else:
                raise dash.exceptions.PreventUpdate

        @app.callback(Output(self.views['train'].IDs.SHOW_PROCESS_TRAINING_OUTPUT, 'children'),
                      Input(self.views['train'].IDs.PROGRESS_LOG_INTERVAL, 'n_intervals'),
                      prevent_initial_call=True)
        def update_training_progress(n_intervals):
            if n_intervals > 0:
                t = self.progress_logger.get_from_stack()
                if t:
                    return t
                else:
                    raise dash.exceptions.PreventUpdate
            else:
                raise dash.exceptions.PreventUpdate
