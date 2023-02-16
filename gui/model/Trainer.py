import os
import tarfile
from typing import Optional

from gui.model.Experiment import Experiment, TrainInfo, build_experiment_from_dict
from gui.model.IO.IOManager import Paths, write, create_missing_folders
from gui.model.TrainDataSource import TrainDataSource, build_TrainDataSource_from_dict
from load_dataset import prepare_dataset_for_gui
from ml import generate_train_and_test_sets, fit_model, predict, write_results
from utils import import_vars, variable_type_analysis

import zipfile


class Trainer:
    def __init__(self, experiment_info: Experiment, data_source: TrainDataSource, main_path=None):
        self.train_info: Optional[TrainInfo] = None
        self.ex_info = experiment_info
        if main_path is not None:
            self.paths = Paths(self.ex_info.ex_name, creation_timestamp=self.ex_info.creation_timestamp,
                               main_path=main_path)
        else:
            self.paths = Paths(self.ex_info.ex_name, creation_timestamp=self.ex_info.creation_timestamp)
        self.data_source = data_source

    def write_experiment_info(self):
        write(self.ex_info.to_dict(), self.paths.folders['experiment'])

    def prepare_dataset(self):
        self.data_source.convert_datetime_to_seconds(self.ex_info.timestamp)

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
                                                           self.paths, self.ex_info.pred_column, mode)
        generate_train_and_test_sets(
            prep_df, self.train_info.target_column, self.train_info.target_column_name, self.train_info.event_level,
            self.train_info.column_type, override, self.ex_info.id, self.train_info.df_completed_cases,
            self.ex_info.activity, self.paths)

    def train(self, progress_logger):
        fit_model(self.train_info.column_type, self.train_info.history, self.ex_info.id,
                  activity_name=self.ex_info.activity, experiment_name=self.ex_info.ex_name, paths=self.paths,
                  progress_logger=progress_logger)

        y_pred = predict(self.train_info.column_type, self.train_info.target_column_name,
                         activity_name=self.ex_info.activity, paths=self.paths)

        mode = 'train'
        write_results(y_pred, self.ex_info.activity, self.train_info.target_column_name,
                      self.train_info.pred_attributes, self.ex_info.pred_column, mode, self.train_info.column_type,
                      self.ex_info.ex_name, self.ex_info.id, self.paths)

    def generate_variables(self):
        X_train, X_test, y_train, y_test = import_vars(self.paths)

        quantitative_vars, \
        qualitative_trace_vars, \
        qualitative_vars = variable_type_analysis(X_train, self.ex_info.id, self.ex_info.activity)

        write(quantitative_vars, self.paths.folders['variables']['qnt'])
        write(qualitative_vars, self.paths.folders['variables']['qlt'])
        write(qualitative_trace_vars, self.paths.folders['variables']['qlt_trc'])

        return quantitative_vars, qualitative_vars, qualitative_trace_vars

    def create_model_archive(self):
        create_missing_folders(self.paths.folders['archives']['train'])
        if not os.path.isfile(self.paths.folders['archives']['train']):
            # TODO: TEST OTHER COMPRESSION METHODS
            with tarfile.open(self.paths.folders['archives']['train'], 'w:xz') as tar_f:

                files = [self.paths.folders['model']['model'], self.paths.folders['model']['dfTrain'],
                         self.paths.folders['model']['dfTest'], self.paths.folders['model']['dfValid'],
                         self.paths.folders['model']['dfTrain_without_valid'], self.paths.folders['model']['params'],
                         self.paths.folders['model']['data_info'], self.paths.folders['experiment']]
                for f in files:
                    tar_f.add(f, arcname=os.path.basename(f))

            print('Archive created')

        return self.paths.folders['archives']['train']

    def to_dict(self, key, save_df_data=False):
        return {
            # 'train_info': self.train_info.to_dict(key),
            'ex_info': self.ex_info.to_dict(),
            # self.paths is build on demand
            'data_source': self.data_source.to_dict(key, save_df_data)
        }


def build_Trainer_from_dict(dict_obj, load_data_source=False, main_path=None):
    obj = Trainer(build_experiment_from_dict(dict_obj['ex_info']),
                  build_TrainDataSource_from_dict(dict_obj['data_source'], load_data_source), main_path=main_path)

    # self.paths is build on demand

    return obj

