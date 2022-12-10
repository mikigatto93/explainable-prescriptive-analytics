import json
import os
from abc import ABC

import dash

from app import app
from dash_extensions.enrich import Input, Output, State

from gui.model import Experiment
from gui.model.Recommender import Recommender
from gui.model.RunDataSource import RunDataSource
from gui.presenters.Presenter import Presenter

import tkinter as tk
from tkinter import filedialog


class RunPresenter(Presenter, ABC):
    def __init__(self, views):
        super().__init__(views)
        self.data_source = None
        self.file_path = None
        self.recommender = None

    def register_callbacks(self):

        @app.callback(Output(self.views['run'].IDs.LOAD_FILE_AREA, 'children'),
                      Input(self.views['run'].IDs.LOAD_FILE_AREA, 'n_clicks'),
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

        @app.callback(Output(self.views['run'].IDs.FADE_GENERATE_PREDS_BTN, 'is_in'),
                      Input(self.views['run'].IDs.LOAD_RUN_FILE_BTN, 'n_clicks'),
                      prevent_initial_call=True)
        def show_gen_pred_button(n_clicks):
            if n_clicks > 0:
                try:
                    self.data_source = RunDataSource(self.file_path)
                except Exception as e:
                    print(e)
                    return False

                return True

        @app.callback(State(self.views['base'].IDs.EXPERIMENT_DATA_STORE, 'data'),
                      Input(self.views['run'].IDs.GENERATE_PREDS_BTN, 'n_clicks'),
                      prevent_initial_call=True)
        def generate_predictions(ex_info_data, n_clicks):
            if n_clicks > 0:
                print(ex_info_data)
                ex_info = Experiment.build_experiment_from_dict(json.loads(ex_info_data))
                print(ex_info)
                self.recommender = Recommender(ex_info, self.data_source)
                self.recommender.prepare_dataset()
                self.recommender.generate_recommendations()
            else:
                raise dash.exceptions.PreventUpdate


