from typing import Optional

from gui.model.Experiment import Experiment, TrainInfo
from gui.model.IO.IOManager import Paths
from gui.model.TrainDataSource import TrainDataSource
from load_dataset import prepare_dataset_for_gui
from ml import generate_train_and_test_sets, fit_model, predict, write_results


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

        # # copy results as a backup
        # fromDirectory = os.path.join(os.getcwd(), 'experiment_files')
        # toDirectory = os.path.join(os.getcwd(), 'experiments', experiment_name)
        #
        # # copy results as a backup
        # if os.path.exists(toDirectory):
        #     shutil.rmtree(toDirectory)
        #     shutil.copytree(fromDirectory, toDirectory)
        # else:
        #     shutil.copytree(fromDirectory, toDirectory)
        #     print('Data and results saved')
        #
        # print('Starting import model and data..')
        # if not os.path.exists(f'expls_{experiment_name}'):
        #     os.mkdir(f'expls_{experiment_name}')
        #     print('explanation folder created')
        #
        # if not os.path.exists(f'explanations/{experiment_name}'):
        #     os.mkdir(f'explanations/{experiment_name}')
        #     print('other explanation folder created')
        #
        # info = read(folders['model']['data_info'])
        # X_train, X_test, y_train, y_test = utils.import_vars(experiment_name=experiment_name, case_id_name=case_id_name)
        # model = utils.import_predictor(experiment_name=experiment_name, pred_column=pred_column)
        # print('Importing completed...')
        #
        # X_train.to_csv('gui_backup/X_train.csv')
        # print('Analyze variables...')
        # quantitative_vars, qualitative_trace_vars, qualitative_vars = utils.variable_type_analysis(X_train,
        #                                                                                            case_id_name,
        #                                                                                            activity_name)
        # pickle.dump(quantitative_vars, open(f'explanations/{experiment_name}/quantitative_vars.pkl', 'wb'))
        # pickle.dump(qualitative_vars, open(f'explanations/{experiment_name}/qualitative_vars.pkl', 'wb'))
        # pickle.dump(qualitative_trace_vars, open(f'explanations/{experiment_name}/qualitative_trace_vars.pkl', 'wb'))
        #
        # print('Variable analysis done')
        # print(f'{time.time()}')
        # return 'Training finished'