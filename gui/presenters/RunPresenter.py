import json

import dash

from app import app
from dash_extensions.enrich import Input, Output, State

from gui.model import Experiment
from gui.model.ProgressLogger.RunProgLogger import RunProgLogger
from gui.model.Recommender import Recommender
from gui.model.RunDataSource import RunDataSource
from gui.presenters.Presenter import Presenter
import dash_uploader as du


class RunPresenter(Presenter):
    def __init__(self, views, prog_logger_file_name='run_progress.tmp'):
        super().__init__(views)
        self.data_source = None
        self.file_path = None
        self.recommender = None
        self.progress_logger = RunProgLogger(prog_logger_file_name)

    def register_callbacks(self):

        @du.callback(
            output=Output(self.views['run'].IDs.LOAD_RUN_FILE_BTN, 'disabled'),
            id=self.views['run'].IDs.RUN_FILE_UPLOADER
        )
        def on_train_file_upload_complete(status):
            print(status)
            print('Upload run log file completed')
            if status.is_completed:
                self.file_path = str(status.latest_file)
                return False
            else:
                return True

        @app.callback([Output(self.views['run'].IDs.FADE_GENERATE_PREDS_BTN, 'is_in'),
                       Output(self.views['run'].IDs.PROC_RUN_OUT_FADE, 'is_in')],
                      Input(self.views['run'].IDs.LOAD_RUN_FILE_BTN, 'n_clicks'),
                      prevent_initial_call=True)
        def show_gen_pred_button(n_clicks):
            if n_clicks > 0:
                try:
                    self.data_source = RunDataSource(self.file_path)
                    self.progress_logger.clear_stack()
                except Exception as e:
                    print(e)
                    return [False, False]

                return [True, True]
            else:
                return [dash.no_update, dash.no_update]

        @app.callback(
            output=[Output(self.views['run'].IDs.TEMP_RUNNING_OUTPUT, 'children'),
                    Output(self.views['run'].IDs.SHOW_PROCESS_RUNNING_OUTPUT, 'style')],
            inputs=[State(self.views['base'].IDs.EXPERIMENT_DATA_STORE, 'data'),
                    Input(self.views['run'].IDs.GENERATE_PREDS_BTN, 'n_clicks')],
            background=True,
            prevent_initial_call=True,
            running=[
                (Output(self.views['run'].IDs.RUN_SPINNER, 'style'),
                 {'display': 'inline'}, {'display': 'none'}),
                (Output(self.views['run'].IDs.PROGRESS_LOG_INTERVAL_RUN, 'max_intervals'), -1, 0),
            ]
        )
        def generate_predictions(ex_info_data, n_clicks):
            if n_clicks > 0:
                # print(ex_info_data)
                ex_info = Experiment.build_experiment_from_dict(json.loads(ex_info_data))
                print(ex_info)
                # ex_info = Experiment.build_experiment_from_dict(
                #     {"ex_name": "test1", "kpi": "Total time", "id": "SR_Number",
                #      "timestamp": "Change_Date+Time", "activity": "ACTIVITY",
                #      "resource": None, "act_to_opt": "Involved_ST", "out_thrs": 0.03,
                #      "pred_column": "remaining_time"})

                self.recommender = Recommender(ex_info, self.data_source)

                self.progress_logger.add_to_stack('Preparing dataset...')
                self.recommender.prepare_dataset()

                self.progress_logger.add_to_stack('Starting recommendations generation...')
                self.recommender.generate_recommendations(self.progress_logger)
                self.progress_logger.clear_stack()

                return ['Recommendations generation completed', {'display': 'none'}]
            else:
                return [dash.no_update, dash.no_update, dash.no_update]

        @app.callback(Output(self.views['run'].IDs.SHOW_PROCESS_RUNNING_OUTPUT, 'children'),
                      Input(self.views['run'].IDs.PROGRESS_LOG_INTERVAL_RUN, 'n_intervals'),
                      prevent_initial_call=True)
        def update_running_progress(n_intervals):
            if n_intervals > 0:
                t = self.progress_logger.get_from_stack()
                if t:
                    return t
                else:
                    raise dash.exceptions.PreventUpdate
            else:
                raise dash.exceptions.PreventUpdate
