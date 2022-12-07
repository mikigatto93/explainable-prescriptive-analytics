from typing import Optional

from gui.model.Experiment import Experiment, TrainInfo
from gui.model.IO.IOManager import Paths, write
from gui.model.TrainDataSource import TrainDataSource
from load_dataset import prepare_dataset_for_gui
from ml import generate_train_and_test_sets, fit_model, predict, write_results
from utils import import_vars, variable_type_analysis


class Trainer:
    def __init__(self, experiment_info: Experiment, data_source: TrainDataSource):
        self.train_info: Optional[TrainInfo] = None
        self.ex_info = experiment_info
        self.paths = Paths(self.ex_info.ex_name)
        self.data_source = data_source

    def prepare_dataset(self):
        self.data_source.convert_datetime_to_seconds(self.ex_info.timestamp)

        if self.ex_info.kpi == 'Total time':
            pred_column = 'remaining_time'
        elif self.ex_info.kpi == 'Minimize activity occurrence':
            pred_column = 'independent_activity'
        else:
            # TODO: ERROR
            return

        use_remaining_for_num_targets = None
        custom_attribute_column_name = None
        end_date_name = None
        role_column_name = None  # TODO: implement a function which maps the possibility of having the variable
        override = True
        pred_attributes = None
        costs = None
        working_times = None
        retained_activities = None
        grid = False  # default
        mode = 'train'
        # TODO: SEE IF THIS CAN BE REFACTORED

        self.train_info, prep_df = prepare_dataset_for_gui(self.data_source.data, self.ex_info,
                                                           self.paths, pred_column, mode)

        generate_train_and_test_sets(
            prep_df, self.train_info.target_column, self.train_info.target_column_name, self.train_info.event_level,
            self.train_info.column_type, override, self.ex_info.id, self.train_info.df_completed_cases,
            self.ex_info.activity, self.paths)

    def train(self):
        fit_model(self.train_info.column_type, self.train_info.history, self.ex_info.id,
                  activity_name=self.ex_info.activity, experiment_name=self.ex_info.ex_name, paths=self.paths)

        y_pred = predict(self.train_info.column_type, self.train_info.target_column_name,
                         activity_name=self.ex_info.activity, paths=self.paths)

        mode = 'train'
        write_results(y_pred, self.ex_info.activity, self.train_info.target_column_name,
                      self.train_info.pred_attributes, self.train_info.pred_column, mode, self.train_info.column_type,
                      self.ex_info.ex_name, self.ex_info.id, self.paths)

    def generate_variables(self):
        X_train, X_test, y_train, y_test = import_vars(self.paths)
        quantitative_vars, \
        qualitative_trace_vars, \
        qualitative_vars = variable_type_analysis(X_train, self.ex_info.id, self.ex_info.activity)

        write(quantitative_vars, self.paths.folders['variables']['qnt'])
        write(qualitative_vars, self.paths.folders['variables']['qlt'])
        write(qualitative_trace_vars, self.paths.folders['variables']['qlt_trc'])
