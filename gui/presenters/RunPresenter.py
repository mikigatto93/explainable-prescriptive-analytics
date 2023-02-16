import json
import os
import traceback
import uuid
import diskcache
import dash
import pandas as pd
from dash import ClientsideFunction

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

        # @app.callback(Output(self.views['base'].IDs.GO_NEXT_BTN, 'disabled'),
        #               Input(self.views['base'].IDs.LOCATION_URL, 'pathname'))
        # def disable_go_next_page_at_start_run(url):
        #     if url == self.views['run'].pathname:
        #         print('ok')
        #         return True
        #     else:
        #         raise dash.exceptions.PreventUpdate

        @app.callback(
            output=[Output(self.views['run'].IDs.FADE_GENERATE_PREDS_BTN, 'is_in'),
                    Output(self.views['run'].IDs.PROC_RUN_OUT_FADE, 'is_in'),
                    Output(self.views['run'].ERROR_IDs.LOAD_RUN_FILE_BTN, 'children'),
                    Output(self.views['run'].IDs.LOAD_RUN_FILE_BTN, 'disabled')],
            inputs=[State(self.views['base'].IDs.RUN_FILE_PATH_STORE, 'data'),
                    State(self.views['base'].IDs.USER_ID, 'data'),
                    Input(self.views['run'].IDs.LOAD_RUN_FILE_BTN, 'n_clicks')],
            running=[
                (Output(self.views['run'].IDs.LOAD_RUN_SPINNER, 'style'),
                 {'display': 'inline'}, {'display': 'none'}),
                (Output(self.views['run'].IDs.LOAD_RUN_FILE_BTN, 'disabled'), True, False),
                (Output(self.views['base'].IDs.GO_BACK_BTN, 'disabled'), True, False),
            ],
            background=True,
            prevent_initial_call=True
        )
        def show_gen_pred_button(run_file_path, user_id, n_clicks):
            if n_clicks > 0:
                try:
                    self.data_sources[user_id] = RunDataSource(run_file_path).to_dict(user_id)
                except (pd.errors.ParserError, pd.errors.EmptyDataError, ValueError) as e:
                    print(traceback.format_exc())
                    return [False, False, '{}: {}'.format(type(e).__name__, e), False]

                return [True, True, '', True]
            else:
                return [dash.no_update] * 4

        @app.callback(
            output=[Output(self.views['run'].IDs.TEMP_RUNNING_OUTPUT, 'children'),
                    Output(self.views['run'].IDs.SHOW_PROCESS_RUNNING_OUTPUT, 'style'),
                    Output(self.views['run'].IDs.GENERATE_PREDS_BTN, 'disabled')],
            inputs=[State(self.views['base'].IDs.EXPERIMENT_DATA_STORE, 'data'),
                    State(self.views['base'].IDs.USER_ID, 'data'),
                    Input(self.views['run'].IDs.GENERATE_PREDS_BTN, 'n_clicks')],
            background=True,
            prevent_initial_call=True,
            running=[
                (Output(self.views['run'].IDs.RUN_SPINNER, 'style'),
                 {'display': 'inline'}, {'display': 'none'}),
                (Output(self.views['run'].IDs.PROGRESS_LOG_INTERVAL_RUN, 'max_intervals'), -1, 0),
                (Output(self.views['run'].IDs.GENERATE_PREDS_BTN, 'disabled'), True, False),
                (Output(self.views['base'].IDs.GO_BACK_BTN, 'disabled'), True, False),
            ],
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

                recommender = Recommender(ex_info,
                                          build_RunDataSource_from_dict(self.data_sources[user_id], load_df=True))
                progress_logger = RunProgLogger(str(uuid.uuid4()))
                self.progress_loggers[user_id] = progress_logger.to_dict()

                progress_logger.add_to_stack('Preparing dataset...')
                try:
                    recommender.prepare_dataset()
                except (pd.errors.ParserError, pd.errors.EmptyDataError, ValueError) as e:
                    print(traceback.format_exc())
                    return ['An error occurred: {}: {}'.format(type(e).__name__, e), {'display': 'none'}, False]

                progress_logger.add_to_stack('Starting recommendations generation...')
                recommender.generate_recommendations(progress_logger)
                progress_logger.clear_stack()

                return ['Recommendations generation completed', {'display': 'none'}, True]
            else:
                return [dash.no_update] * 3

        @app.callback(Output(self.views['base'].IDs.GO_NEXT_BTN, 'disabled'),
                      Output(self.views['base'].IDs.GO_BACK_BTN, 'disabled'),
                      Input(self.views['run'].IDs.TEMP_RUNNING_OUTPUT, 'children'),
                      prevent_initial_call=True)
        def activate_go_next_arrow_run(children):
            if children == 'Recommendations generation completed':
                return [False, False]
            else:
                raise dash.exceptions.PreventUpdate

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
