import json
import os
import uuid
import diskcache
import dash

from app import app
from dash_extensions.enrich import Input, Output, State

from gui.model import Experiment
from gui.model.DiskDict import DiskDict
from gui.model.ProgressLogger.RunProgLogger import RunProgLogger, build_RunProgLogger_from_dict
from gui.model.Recommender import Recommender
from gui.model.RunDataSource import RunDataSource, build_RunDataSource_from_dict
from gui.presenters.Presenter import Presenter
import dash_uploader as du


class RunPresenter(Presenter):
    def __init__(self, views):
        super().__init__(views)
        self.data_sources = DiskDict(os.path.join(os.getcwd(), 'gui_data', 'run'), 'data_sources')
        # self.file_paths =
        self.recommenders = DiskDict(os.path.join(os.getcwd(), 'gui_data', 'run'), 'recommenders')
        self.progress_loggers = DiskDict(os.path.join(os.getcwd(), 'gui_data', 'run'), 'progress_loggers')

    def clear_user_data(self, user_id):
        if self.data_sources.exists(user_id):
            data_source = build_RunDataSource_from_dict(self.data_sources[user_id])
            data_source.free()
            data_source.free_df(user_id)
            self.data_sources.delete(user_id)
            print('deleted data source')

        if self.progress_loggers.exists(user_id):
            build_RunProgLogger_from_dict(self.progress_loggers[user_id]).free()
            self.progress_loggers.delete(user_id)
            print('deleted prog logger')

    def register_callbacks(self):

        @du.callback(
            output=[Output(self.views['run'].IDs.LOAD_RUN_FILE_BTN_FADE, 'is_in'),
                    Output(self.views['base'].IDs.RUN_FILE_PATH_STORE, 'data')],
            id=self.views['run'].IDs.RUN_FILE_UPLOADER
        )
        def on_train_file_upload_complete(status):
            print(status)
            print('Upload run log file completed')
            if status.is_completed:
                return [True, str(status.latest_file)]
            else:
                return [False, dash.no_update]

        @app.callback(
            output=[Output(self.views['run'].IDs.FADE_GENERATE_PREDS_BTN, 'is_in'),
                    Output(self.views['run'].IDs.PROC_RUN_OUT_FADE, 'is_in')],
            inputs=[State(self.views['base'].IDs.RUN_FILE_PATH_STORE, 'data'),
                    State(self.views['base'].IDs.USER_ID, 'data'),
                    Input(self.views['run'].IDs.LOAD_RUN_FILE_BTN, 'n_clicks')],
            running=[
                (Output(self.views['run'].IDs.LOAD_RUN_SPINNER, 'style'),
                 {'display': 'inline'}, {'display': 'none'}),
            ],
            background=True,
            prevent_initial_call=True
        )
        def show_gen_pred_button(run_file_path, user_id, n_clicks):
            if n_clicks > 0:
                try:
                    self.data_sources[user_id] = RunDataSource(run_file_path).to_dict(user_id)
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
                    State(self.views['base'].IDs.USER_ID, 'data'),
                    Input(self.views['run'].IDs.GENERATE_PREDS_BTN, 'n_clicks')],
            background=True,
            prevent_initial_call=True,
            running=[
                (Output(self.views['run'].IDs.RUN_SPINNER, 'style'),
                 {'display': 'inline'}, {'display': 'none'}),
                (Output(self.views['run'].IDs.PROGRESS_LOG_INTERVAL_RUN, 'max_intervals'), -1, 0),
            ]
        )
        def generate_predictions(ex_info_data, user_id, n_clicks):
            if n_clicks > 0:
                # print(ex_info_data)
                ex_info = Experiment.build_experiment_from_dict(json.loads(ex_info_data))
                print(ex_info)
                # ex_info = Experiment.build_experiment_from_dict(
                #     {"ex_name": "test1", "kpi": "Total time", "id": "SR_Number",
                #      "timestamp": "Change_Date+Time", "activity": "ACTIVITY",
                #      "resource": None, "act_to_opt": "Involved_ST", "out_thrs": 0.03,
                #      "pred_column": "remaining_time"})

                # self.recommenders[user_id] = Recommender(ex_info, self.data_sources[user_id])
                recommender = Recommender(ex_info,
                                          build_RunDataSource_from_dict(self.data_sources[user_id], load_df=True))
                progress_logger = RunProgLogger(str(uuid.uuid4()))
                self.progress_loggers[user_id] = progress_logger.to_dict()

                progress_logger.add_to_stack('Preparing dataset...')
                recommender.prepare_dataset()

                progress_logger.add_to_stack('Starting recommendations generation...')
                recommender.generate_recommendations(progress_logger)
                progress_logger.clear_stack()

                return ['Recommendations generation completed', {'display': 'none'}]
            else:
                return [dash.no_update, dash.no_update, dash.no_update]

        @app.callback(Output(self.views['run'].IDs.SHOW_PROCESS_RUNNING_OUTPUT, 'children'),
                      State(self.views['base'].IDs.USER_ID, 'data'),
                      Input(self.views['run'].IDs.PROGRESS_LOG_INTERVAL_RUN, 'n_intervals'),
                      prevent_initial_call=True)
        def update_running_progress(user_id, n_intervals):
            if n_intervals > 0:
                t = None
                try:
                    t = build_RunProgLogger_from_dict(self.progress_loggers[user_id]).get_from_stack()
                except:
                    pass

                if t:
                    return t
                else:
                    raise dash.exceptions.PreventUpdate
            else:
                raise dash.exceptions.PreventUpdate

