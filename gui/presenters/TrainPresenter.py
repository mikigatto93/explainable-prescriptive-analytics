import json
import os

import dash

from gui.app import app
from dash_extensions.enrich import Input, Output, State

from gui.model.Experiment import Experiment
from gui.model.TrainDataSource import TrainDataSource
from gui.model.Trainer import Trainer
from gui.presenters.Presenter import Presenter

import tkinter as tk
from tkinter import filedialog


class TrainPresenter(Presenter):
    def __init__(self, views, trainer: Trainer):
        super().__init__(views)
        self.data_source = None
        self.file_path = None
        self.experiment_info = None
        self.trainer = trainer

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
                       Output(self.views['train'].IDs.ACT_TO_OPTIMIZE_DROPDOWN, 'options')],
                      Input(self.views['train'].IDs.FADE_ALL_TRAIN_CONTROLS, 'is_in'),
                      prevent_initial_call=True)
        def populate_dropdown_options(fade):
            if fade:
                options_group = self.data_source.columns_list
                return [options_group] * 4  # generate a list of 4 option_group for the dropdowns
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
        def collect_training_user_data(ex_name, kpi, _id, timestamp, activity, act_to_opt, resource, out_thrs, n_clicks):
            if n_clicks > 0:
                # TODO: validate data
                self.experiment_info = Experiment(ex_name, kpi, _id, timestamp, activity, resource, act_to_opt, out_thrs)
                print(self.experiment_info)
                self.trainer.set_experiment_info(self.experiment_info)
                self.data_source.set_experiment_info(self.experiment_info)
                return json.dumps({'validated': True}, indent=2)
            else:
                # TODO: invalida data
                raise dash.exceptions.PreventUpdate

        # @app.callback(Output(),
        #               Input(self.views['base'].IDS.EXPERIMENT_DATA_STORE, 'data'))
        # def start_training(validation_res):
        #     if validation_res['validated']:
        #         self.data_source.prepare_dataset()

