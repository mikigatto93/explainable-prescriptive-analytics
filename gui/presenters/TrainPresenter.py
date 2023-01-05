import json

import dash
from dash import ClientsideFunction

from app import app
from dash_extensions.enrich import Input, Output, State

from gui.model.Experiment import Experiment
from gui.model.ProgressLogger.TrainProgLogger import TrainProgLogger
from gui.model.TrainDataSource import TrainDataSource
from gui.model.Trainer import Trainer
from gui.presenters.Presenter import Presenter
import dash_uploader as du


class TrainPresenter(Presenter):
    def __init__(self, views):
        super().__init__(views)
        self.data_source = None
        self.file_path = None
        self.trainer = None
        self.progress_logger = TrainProgLogger('train_progress.tmp')

    def __validate_input(self, ex_name, kpi, _id, timestamp, activity, act_to_opt):
        error_data = {}
        if ex_name is None:
            error_data[self.views['train'].IDs.EXPERIMENT_NAME_TEXTBOX] = 'Experiment name is empty'
        if kpi is None:
            error_data[self.views['train'].IDs.KPI_RADIO_ITEMS] = 'One KPI must be selected'
        if _id is None:
            error_data[self.views['train'].IDs.ID_DROPDOWN] = 'One ID column must be selected'
        if timestamp is None:
            error_data[self.views['train'].IDs.TIMESTAMP_DROPDOWN] = 'One TIMESTAMP column must be selected'
        if activity is None:
            error_data[self.views['train'].IDs.ACTIVITY_DROPDOWN] = 'One ACTIVITY column must be selected'
        if act_to_opt is None and kpi == 'Minimize activity occurrence':
            error_data[self.views['train'].IDs.ACT_TO_OPTIMIZE_DROPDOWN] = \
                'If KPI "Minimize activity occurrence" is chosen then one ACTIVITY column to minimize must be selected'
        return error_data

    def register_callbacks(self):
        # @app.callback(Output(self.views['train'].IDs.LOAD_FILE_AREA, 'children'),
        #               Input(self.views['train'].IDs.LOAD_FILE_AREA, 'n_clicks'),
        #               prevent_initial_call=True)
        # def open_file(n_clicks):
        #     if n_clicks > 0:
        #         root = tk.Tk()
        #         root.attributes("-topmost", True)
        #         root.withdraw()
        #         file_path = filedialog.askopenfilename(parent=root)
        #         root.destroy()
        #         self.file_path = file_path
        #         filename = os.sep.join(os.path.normpath(file_path).split(os.sep)[-1:])
        #         return filename
        #     else:
        #         raise dash.exceptions.PreventUpdate

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
                       Output(self.views['train'].IDs.ACT_TO_OPTIMIZE_DROPDOWN, 'options'),
                       Output(self.views['train'].IDs.OUTLIERS_THRS_SLIDER, 'value')],
                      Input(self.views['train'].IDs.FADE_ALL_TRAIN_CONTROLS, 'is_in'),
                      prevent_initial_call=True)
        def populate_dropdown_options(fade):
            DEFAULT_OUTLIER_THRS = 0.3
            if fade:
                options_group = self.data_source.columns_list

                # generate a list of 5 option_group for the dropdowns
                return [options_group] * 5 + [DEFAULT_OUTLIER_THRS]
            else:
                raise dash.exceptions.PreventUpdate

        @app.callback(Output(self.views['train'].IDs.FADE_ACT_TO_OPTIMIZE_DROPDOWN, 'is_in'),
                      Input(self.views['train'].IDs.KPI_RADIO_ITEMS, 'value'),
                      prevent_initial_call=True)
        def show_choose_act_to_opt_dropdown(value):
            return value in ['Maximize activity occurrence', 'Minimize activity occurrence']

        # @app.callback([Output(self.views['train'].IDs.OUTLIERS_THRS_SLIDER, 'value'),
        #               Output(self.views['train'].IDs.SLIDER_VALUE_TEXTBOX, 'value')],
        #               [Input(self.views['train'].IDs.OUTLIERS_THRS_SLIDER, 'value'),
        #                Input(self.views['train'].IDs.SLIDER_VALUE_TEXTBOX, 'value')])
        # def slider_value_selector(slider_val, textbox_val):
        #     triggered_id = dash.ctx.triggered_id
        #     if triggered_id == self.views['train'].IDs.OUTLIERS_THRS_SLIDER:
        #         return [dash.no_update, slider_val]
        #     elif triggered_id == self.views['train'].IDs.SLIDER_VALUE_TEXTBOX:
        #         new_val = textbox_val if textbox_val else 0
        #         return [float(new_val), dash.no_update]
        #     else:
        #         return [dash.no_update, dash.no_update]

        # @app.callback(Output(self.views['train'].IDs.OUT_THRS_SLIDER_VALUE_LABEL, 'children'),
        #               Input(self.views['train'].IDs.OUTLIERS_THRS_SLIDER, 'value'))
        # def slider_value_selector(slider_val):
        #     if slider_val:
        #         return slider_val
        #     else:
        #         raise dash.exceptions.PreventUpdate

        app.clientside_callback(
            ClientsideFunction(
                namespace='clientside',
                function_name='slider_value_display_csc'
            ),
            Output(self.views['train'].IDs.OUT_THRS_SLIDER_VALUE_LABEL, 'children'),
            Input(self.views['train'].IDs.OUTLIERS_THRS_SLIDER, 'value')
        )

        @app.callback([Output(self.views['base'].IDs.EXPERIMENT_DATA_STORE, 'data'),
                       Output(self.views['train'].IDs.PROC_TRAIN_OUT_FADE, 'is_in'),
                       Output(self.views['train'].IDs.PROGRESS_LOG_INTERVAL, 'max_intervals'),
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
        def collect_training_user_data(ex_name, kpi, _id, timestamp, activity, resource, act_to_opt, out_thrs, n_clicks):
            if n_clicks > 0:
                error_data = self.__validate_input(ex_name, kpi, _id, timestamp, activity, act_to_opt)
                if not error_data:
                    experiment_info = Experiment(ex_name, kpi, _id, timestamp, activity, resource, act_to_opt, out_thrs)
                    print(experiment_info)
                    self.trainer = Trainer(experiment_info, self.data_source)
                    self.progress_logger.clear_stack()
                    return [json.dumps(experiment_info.to_dict()), True, -1, error_data]  # -1 starts interval
                else:
                    return [dash.no_update] * 3 + [error_data]
            else:
                return [dash.no_update] * 4

        @app.callback(
            output=[Output(self.views['train'].IDs.TEMP_TRAINING_OUTPUT, 'children'),
                    Output(self.views['train'].IDs.PROGRESS_LOG_INTERVAL, 'max_intervals'),
                    Output(self.views['train'].IDs.SHOW_PROCESS_TRAINING_OUTPUT, 'children')],
            inputs=Input(self.views['base'].IDs.EXPERIMENT_DATA_STORE, 'data'),
            background=True,
            prevent_initial_call=True,
            running=[
                (Output(self.views['train'].IDs.TRAIN_SPINNER, 'style'),
                 {'display': 'inline'}, {'display': 'none'})
            ]
        )
        def train_model(ex_store_data):
            if ex_store_data is not None and json.loads(ex_store_data):
                self.progress_logger.add_to_stack('Preparing dataset...')
                self.trainer.prepare_dataset()

                self.progress_logger.add_to_stack('Starting training...')
                self.trainer.train(self.progress_logger)

                self.progress_logger.add_to_stack('Generating variables...')
                self.trainer.generate_variables()

                return ['Training completed', 0, '']  # 0 stops the interval
            elif ex_store_data is None:
                return [dash.no_update, dash.no_update, dash.no_update]
            else:
                return ['An error occurred during training', 0, '']  # 0 stops the interval

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


