import hash_maps
from gui.model.Experiment import Experiment
from gui.model.RunDataSource import RunDataSource
from load_dataset import prepare_dataset_for_gui
from utils import import_vars


class Recommender:
    def __init__(self, experiment_info: Experiment, data_source: RunDataSource):
        self.ex_info = experiment_info
        self.data_source = data_source
        # self.paths = paths

    def prepare_dataset(self):
        self.data_source.convert_datetime_to_seconds(self.ex_info.timestamp)

        self.data_source.remove_unnamed_columns()

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

        print('Creating hash-map of possible next activities')
        X_train, _, _, _ = import_vars(self.paths)
        X_train = X_train.iloc[:, 1:]
        traces_hash = hash_maps.fill_hashmap(X_train=X_train, case_id_name=self.ex_info.id,
                                             activity_name=self.ex_info.activity,
                                             thrs=self.ex_info.out_thrs)
        print('Hash-map created')

        train_info, prep_df = prepare_dataset_for_gui(self.data_source.data, self.ex_info,
                                                           self.paths, pred_column, mode)




        # df_rec = load_dataset.preprocess_df(df=df_rec, case_id_name=case_id_name, activity_column_name=activity_name,
        #                 start_date_name=start_date_name, date_format=date_format, end_date_name=end_date_name,
        #                 pred_column=pred_column, mode="train", experiment_name=experiment_name, override=override,
        #                 pred_attributes=pred_attributes, costs=costs, working_times=working_time,
        #                 resource_column_name=resource_column_name, role_column_name=role_column_name,
        #                 use_remaining_for_num_targets=use_remaining_for_num_targets,
        #                 predict_activities=predict_activities, lost_activities=lost_activities,
        #                 retained_activities=retained_activities,
        #                 custom_attribute_column_name=custom_attribute_column_name, shap=shap)
        # df_rec.to_csv('gui_backup/dfrun_preprocessed.csv')
        # print('Running Data Imported')
        # print(4*'\n')
        # print('Starting generating recommendations')
        #
        # pickle.dump(traces_hash, open('gui_backup/transition_system.pkl', 'wb'))
        #
        # idx_list = df_rec[case_id_name].unique()
        # results = list()
        # rec_dict = dict()
        # real_dict = dict()
        # if not os.path.exists('explanations'):
        #     os.mkdir('explanations')
        # if not os.path.exists(f'explanations/{experiment_name}'):
        #     os.mkdir(f'explanations/{experiment_name}')
        # if not os.path.exists(f'recommendations/{experiment_name}'):
        #     os.mkdir(f'recommendations/{experiment_name}')