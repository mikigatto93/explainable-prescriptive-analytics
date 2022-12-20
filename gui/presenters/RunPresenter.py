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
    def __init__(self, views):
        super().__init__(views)
        self.data_source = None
        self.file_path = None
        self.recommender = None
        self.progress_logger = RunProgLogger('run_progress.tmp')

    def register_callbacks(self):

        # @app.callback(Output(self.views['run'].IDs.LOAD_FILE_AREA, 'children'),
        #               Input(self.views['run'].IDs.LOAD_FILE_AREA, 'n_clicks'),
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

        @du.callback(
            output=Output(self.views['run'].IDs.LOAD_RUN_FILE_BTN, 'disabled'),
            id=self.views['run'].IDs.RUN_FILE_UPLOADER
        )
        def on_train_file_upload_complete(status):
            print(status)
            print('Upload run log file completed')
            self.file_path = str(status.latest_file)
            return False

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

        @app.callback([Output(self.views['run'].IDs.TEMP_RUNNING_OUTPUT, 'children'),
                       Output(self.views['run'].IDs.PROGRESS_LOG_INTERVAL_RUN, 'max_intervals')],
                      State(self.views['base'].IDs.EXPERIMENT_DATA_STORE, 'data'),
                      Input(self.views['run'].IDs.GENERATE_PREDS_BTN, 'n_clicks'),
                      prevent_initial_call=True)
        def generate_predictions(ex_info_data, n_clicks):
            if n_clicks > 0:
                # print(ex_info_data)
                # ex_info = Experiment.build_experiment_from_dict(json.loads(ex_info_data))
                # print(ex_info)
                ex_info = Experiment.build_experiment_from_dict({"ex_name": "test1", "kpi": "Total time", "id": "SR_Number",
                                                 "timestamp": "Change_Date+Time", "activity": "ACTIVITY",
                                                 "resource": None, "act_to_opt": "Involved_ST", "out_thrs": 0.03,
                                                 "pred_column": "remaining_time"})

                self.recommender = Recommender(ex_info, self.data_source)
                self.recommender.prepare_dataset()
                self.recommender.generate_recommendations(self.progress_logger)
                return ['Recommendations generation completed', 0]  # stops the interval
            else:
                return [dash.no_update, dash.no_update]

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
