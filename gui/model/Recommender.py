import tqdm

import hash_maps
import next_act
import utils
from gui.model.Experiment import Experiment, build_experiment_from_dict
from gui.model.RunDataSource import RunDataSource, build_RunDataSource_from_dict
from gui.model.IO.IOManager import Paths, read, write
from load_dataset import prepare_dataset_for_gui
from utils import import_vars


class Recommender:
    def __init__(self, experiment_info: Experiment, data_source: RunDataSource):
        self.prep_df = None
        self.ex_info = experiment_info
        self.data_source = data_source
        self.traces_hash = None
        self.paths = Paths(self.ex_info.ex_name, creation_timestamp=self.ex_info.creation_timestamp)

    def prepare_dataset(self):
        self.data_source.convert_datetime_to_seconds(self.ex_info.timestamp)

        self.data_source.remove_unnamed_columns()

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

        # print('Creating hash-map of possible next activities')
        X_train, _, _, _ = import_vars(self.paths)
        # print(X_train)
        # print('_____')
        # print(X_train.iloc[:, 1:])
        # TODO: VEDERE SE LASCIARE O NO ILOC PERCHè TOGLIE LA PRIMA COLONNA CON L'ID E DOPO DA ERRORE CHE NON LA TROVA
        self.traces_hash = hash_maps.fill_hashmap(X_train=X_train, case_id_name=self.ex_info.id,
                                                  activity_name=self.ex_info.activity, thrs=self.ex_info.out_thrs)
        # print('Hash-map created')

        train_info, self.prep_df = prepare_dataset_for_gui(self.data_source.data, self.ex_info,
                                                           self.paths, self.ex_info.pred_column, mode)
        write(self.prep_df, self.paths.folders['recommendations']['df_run'])

    def generate_recommendations(self, progress_logger):
        idx_list = self.prep_df[self.ex_info.id].unique()
        results = list()
        rec_dict = dict()
        real_dict = dict()

        model = read(self.paths.folders['model']['model'])
        quantitative_vars = read(self.paths.folders['variables']['qnt'])
        qualitative_vars = read(self.paths.folders['variables']['qlt'])

        print('start')
        with tqdm.tqdm(idx_list, file=progress_logger) as idx_list_iter:
            for trace_idx in idx_list_iter:

                trace = self.prep_df[self.prep_df[self.ex_info.id] == trace_idx].reset_index(drop=True)
                trace = trace.reset_index(drop=True)  # trace.iloc[:, :-1].reset_index(drop=True)
                trace.rename(columns={'time_from_midnight': 'daytime'}, inplace=True)
                # trace = trace[list(model.feature_names_)]
                try:
                    # take activity list
                    acts = list(self.prep_df[self.prep_df[self.ex_info.id] == trace_idx].reset_index(drop=True)[
                                    self.ex_info.activity])

                    # Remove the last (it has been added because of the evaluation)
                    # trace = trace.iloc[:-1].reset_index(drop=True)
                except:
                    import ipdb;
                    ipdb.set_trace()

                try:
                    next_activities, actual_prediciton = next_act.next_act_kpis(trace, self.traces_hash, model,
                                                                                self.ex_info.pred_column,
                                                                                self.ex_info.id, self.ex_info.activity,
                                                                                quantitative_vars, qualitative_vars,
                                                                                encoding='aggr-hist')
                    next_activities['kpi_rel'] = next_activities['kpi_rel'].abs()
                except:
                    # print('Next activity not found in transition system')
                    continue

                try:
                    rec_act = \
                        next_activities[next_activities['kpi_rel'] == min(next_activities['kpi_rel'])][
                            'Next_act'].values
                    other_traces = [
                        next_activities[next_activities['kpi_rel'] != min(next_activities['kpi_rel'])][
                            'Next_act'].values]
                except:
                    try:
                        if len(next_activities) == 1:
                            print('No other traces to analyze')
                    except:
                        print(trace_idx, 'check it')

                rec_dict[trace_idx] = {i: j for i, j in zip(next_activities['Next_act'], next_activities['kpi_rel'])}
                real_dict[trace_idx] = {acts[-1]: actual_prediciton}
        rec_dict = {str(A): N for (A, N) in [x for x in rec_dict.items()]}
        real_dict = {str(A): N for (A, N) in [x for x in real_dict.items()]}
        write(rec_dict, self.paths.folders['recommendations']['rec_dict'])
        write(real_dict, self.paths.folders['recommendations']['real_dict'])
        print('done')

#     def to_dict(self, key, save_df_data=False):
#         return {
#             'ex_info': self.ex_info.to_dict(),
#             'data_source': self.data_source.to_dict(key, save_df_data)
#         }
#
#
# def build_Recommender_from_dict(dict_obj, load_data_source=False):
#     obj = Recommender(build_experiment_from_dict(dict_obj['ex_info']),
#                       build_RunDataSource_from_dict(dict_obj['data_source'], load_data_source))
#     # self.paths is build on demand
#     return obj
