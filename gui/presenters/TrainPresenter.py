import json
import os
import time

import dash

from app import app
from dash_extensions.enrich import Input, Output, State

from gui.model.Experiment import Experiment
from gui.model.TimeLogger import TimeLogger
from gui.model.TrainDataSource import TrainDataSource
from gui.model.Trainer import Trainer
from gui.presenters.Presenter import Presenter

import tkinter as tk
from tkinter import filedialog


class TrainPresenter(Presenter):
    def __init__(self, views):
        super().__init__(views)
        self.data_source = None
        self.file_path = None
        self.trainer = None
        self.progress_logger = TimeLogger()

    def register_callbacks(self):
        @app.callback(Output(self.views['train'].IDs.LOAD_FILE_AREA, 'children'),
                      Input(self.views['train'].IDs.LOAD_FILE_AREA, 'n_clicks'),
                      prevent_initial_call=True)
        def open_file(n_clicks):
            if n_clicks > 0:
                root = tk.Tk()
                root.attributes("-topmost", True)
                root.withdraw()
                file_path = filedialog.askopenfilename(parent=root)
                root.destroy()
                self.file_path = file_path
                filename = os.sep.join(os.path.normpath(file_path).split(os.sep)[-1:])
                return filename
            else:
                raise dash.exceptions.PreventUpdate

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
                       Output(self.views['train'].IDs.ACT_TO_OPTIMIZE_DROPDOWN, 'options')],
                      Input(self.views['train'].IDs.FADE_ALL_TRAIN_CONTROLS, 'is_in'),
                      prevent_initial_call=True)
        def populate_dropdown_options(fade):
            if fade:
                options_group = self.data_source.columns_list
                return [options_group] * 5  # generate a list of 5 option_group for the dropdowns
            else:
                raise dash.exceptions.PreventUpdate

        @app.callback(Output(self.views['train'].IDs.FADE_ACT_TO_OPTIMIZE_DROPDOWN, 'is_in'),
                      Input(self.views['train'].IDs.KPI_RADIO_ITEMS, 'value'),
                      prevent_initial_call=True)
        def show_choose_act_to_opt_dropdown(value):
            return value in ['Maximize activity occurrence', 'Minimize activity occurrence']

        @app.callback(Output(self.views['base'].IDs.EXPERIMENT_DATA_STORE, 'data'),
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
                # TODO: validate data
                experiment_info = Experiment(ex_name, kpi, _id, timestamp, activity, resource, act_to_opt, out_thrs)
                print(experiment_info)
                self.trainer = Trainer(experiment_info, self.data_source)
                return json.dumps(experiment_info.to_dict())
            else:
                # TODO: invalida data
                raise dash.exceptions.PreventUpdate

        @app.callback(
            output=[Output(self.views['train'].IDs.TEMP_TRAINING_OUTPUT, 'children'),
                    Output(self.views['train'].IDs.PROGRESS_LOG_INTERVAL, 'max_intervals')],
            inputs=Input(self.views['base'].IDs.EXPERIMENT_DATA_STORE, 'data'),
            background=True,
            prevent_initial_call=True
        )
        def train_model(ex_store_data):
            if ex_store_data is not None and json.loads(ex_store_data):
                self.trainer.prepare_dataset()
                self.trainer.train(self.progress_logger)
                self.trainer.generate_variables()
                return ['Training finished', 0]  # stops the interval
            elif ex_store_data is None:
                raise dash.exceptions.PreventUpdate
            else:
                return ['Error', 0]  # stops the interval

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

