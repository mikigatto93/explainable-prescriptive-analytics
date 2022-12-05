import os
import traceback
from datetime import datetime

import numpy as np
import pandas as pd
import pm4py
from pm4py.objects.conversion.log import converter as log_converter

from model.DataSource import DataSource
import model.IO.IOManager as IOManager


class TrainDataSource(DataSource):
    def __init__(self, path):
        super().__init__(path)
        self.columns_list = list(self.data.columns)
        self.ex_info = None
        self.paths = None

    def read_data(self, path):
        dataframe = None
        filename, file_extension = os.path.splitext(path)
        try:
            if file_extension == '.csv':
                dataframe = pd.read_csv(path)
            elif file_extension == '.xes':
                # pm4py.convert_to_dataframe(pm4py.read_xes(io.BytesIO(decoded))).to_csv(path_or_buf=(filename[:-4] +
                # '.csv'),index=None)
                log = pm4py.read_xes(path)
                dataframe = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)
            elif file_extension == '.xls':
                dataframe = pd.read_excel(path)
        except Exception as e:
            print(e)
            raise e
        return dataframe

    def set_experiment_info(self, ex_info):
        self.ex_info = ex_info

    def set_paths(self, paths):
        self.paths = paths

    def prepare_dataset(self, ex_info):
        self.convert_datetime_to_sec()
        use_remaining_for_num_targets = None
        custom_attribute_column_name = None
        if self.ex_info.kpi == 'Total time':
            pred_column = 'remaining_time'
        elif self.ex_info.kpi == 'Minimize activity occurrence':
            pred_column = 'independent_activity'
        else:
            # TODO: ERROR
            pass

        end_date_name = None
        role_column_name = None  # TODO: implement a function which maps the possibility of having the variable
        override = True
        pred_attributes = None
        costs = None
        working_times = None
        lost_activities = None
        retained_activities = None
        mean_reference_target = None
        grid = False  # default
        predict_activities = [self.ex_info.act_to_opt]  # require being a list (than only takes first argument??)
        # TODO: SEE IF THIS CAN BE REFACTORED

        # If there are not a folder for contain indexes, create it
        # if not os.path.os.path.exists('indexes'):
        #     os.mkdir('indexes')
        #
        # if not (os.path.os.path.exists(f'indexes/test_idx_{case_id_name}.pkl') and os.path.os.path.exists(
        #         f'indexes/train_idx_{case_id_name}.pkl')):
        #     get_split_indexes(df, case_id_name, start_date_name, train_size=.65)
        # else:
        #     print('reading indexes')

        if pred_column == "remaining_time":
            mean_reference_target = self.write_leadtime_reference_mean(self.data,
                                                                       self.ex_info.id,
                                                                       self.ex_info.timestamp,
                                                                       end_date_name)
            # histogram_median_events_per_dataset(df, case_id_name, activity_column_name, start_date_name,
            #                                     end_date_name)

            date_format = "%Y-%m-%d %H:%M:%S"
            df = self.prepare_data_and_add_features(self.data, self.ex_info.id, self.ex_info.timestamp,
                                                    date_format, end_date_name)

            if "activity_duration" in df.columns:
                df_completed_cases = df.groupby(self.ex_info.id).agg("last")[
                    [self.ex_info.activity, "time_from_start", "activity_duration"]].reset_index()
                df_completed_cases["current"] = df_completed_cases["time_from_start"] + df_completed_cases[
                    "activity_duration"]
                df_completed_cases.drop(["time_from_start", "activity_duration"], axis=1, inplace=True)
            else:
                df_completed_cases = df.groupby(self.ex_info.id).agg("last")[
                    [self.ex_info.activity, "time_from_start"]].reset_index()
                df_completed_cases["current"] = df_completed_cases["time_from_start"]
                df_completed_cases.drop(["time_from_start"], axis=1, inplace=True)
            df_completed_cases.rename(columns={self.ex_info.id: "CASE ID", self.ex_info.activity: "Activity"},
                                      inplace=True)
            if costs is not None:
                try:
                    df = self.calculate_costs(df, costs, working_times, self.ex_info.activity, self.ex_info.resource,
                                              role_column_name, self.ex_info.id)
                    if pred_column == "case_cost":
                        mean_reference_target = self.write_costs_reference_mean(df, self.ex_info.id)
                except Exception as e:
                    print(traceback.format_exc(), '\nContinuing')
                    pass
            # if mode == "train":
            mean_events = np.round(
                np.mean(df.groupby(self.ex_info.id).count()[self.ex_info.activity]))  # TODO:? ARRAY ROUNDED?
            if grid is True:
                history = ["no history", "aggr hist"]
                for i in range(1, mean_events + 1):
                    history.append(i)
                # end is needed if we try all models and validation curve is still decreasing (edge case)
                history.append("end")
            else:
                history = ["aggr hist"]

            df_original = df.copy()
            end = False
            # else: (mode != 'train')
            # history = [IOManager.read(self.paths.folders['model']['params'])["history"]]

            case_level_attributes = self.new_case_level_attribute_detection(df, self.ex_info.id, 'train')
            for model_type in history:
                # if mode == "train":
                if os.path.exists(self.paths.folders['model']['params']):
                    if "history" in IOManager.read(self.paths.folders['model']['params']) or model_type == "end":
                        model_type = IOManager.read(self.paths.folders['model']['params'])["history"]
                        # end = True
                df = df_original.copy()
                df = self.apply_history_to_df(df, self.ex_info.id, self.ex_info.activity, model_type,
                                              case_level_attributes)
                # if target column != remaining time exclude target column
                if pred_column != 'remaining_time':
                    if pred_column == "independent_activity":
                        event_level = 1
                        pred_attributes = predict_activities[0]
                        pred_column = self.ex_info.activity
                    elif pred_column == "churn_activity":
                        event_level = 1
                        pred_attributes = retained_activities
                        pred_column = self.ex_info.activity
                    elif pred_column == "custom_attribute":
                        # this follows the same path as independent_activity
                        event_level = 1
                        pred_attributes = pred_attributes[0]
                        pred_column = custom_attribute_column_name
                    else:
                        event_level = self.detect_case_level_attribute(df, pred_column)
                    if event_level == 0:
                        # case level - test column as is
                        if np.issubdtype(df[pred_column], np.number):
                            # take target numeric column as is
                            column_type = 'Numeric'
                            target_column = df[pred_column].reset_index(drop=True)
                            target_column_name = pred_column
                            # add temporary column to know which rows delete later (remaining_time=0)
                            target_column = pd.concat([target_column, df['remaining_time']], axis=1)
                            del df[pred_column]
                        else:
                            # case level string (you want to discover if a client recess will be performed)
                            column_type = 'Categorical'
                            # add one more test column for every value to be predicted
                            for value in pred_attributes:
                                df[value] = 0
                            # assign 1 to the column corresponding to that value
                            for value in pred_attributes:
                                df.loc[df[pred_column] == value, value] = 1
                            # eliminate old test column and take columns that are one-hot encoded test
                            del df[pred_column]
                            target_column = df[pred_attributes]
                            target_column_name = pred_attributes
                            df.drop(pred_attributes, axis=1, inplace=True)
                            target_column = target_column.join(df['remaining_time'])
                    else:
                        # event level attribute prediction
                        if np.issubdtype(df[pred_column], np.number):
                            column_type = 'Numeric'
                            # if a number you want to discover the final value of the attribute (ex invoice amount)
                            df_last_attribute = df.groupby(self.ex_info.id)[pred_column].agg(['last']).reset_index()
                            target_column = df[self.ex_info.id].map(
                                df_last_attribute.set_index(self.ex_info.id)['last'])
                            if use_remaining_for_num_targets:
                                # now we predict remaining attribute (e.g. remaining cost)
                                target_column = target_column - df[pred_column]
                            # if you don't add y to the name you already have the same column in x, when you add the y-column
                            # after normalizing
                            target_column_name = 'Y_COLUMN_' + pred_column
                            target_column = pd.concat([target_column, df['remaining_time']], axis=1)
                        else:
                            # TODO: target column could be calculated only once for all history models when using grid
                            # you want to discover if a certain activity will be performed
                            # set 1 for each case until that activity happens, the rest 0
                            if pred_column == self.ex_info.activity and not type(pred_attributes) == np.str:
                                target_column_name = "retained_activity"
                                df[target_column_name] = 0
                            else:
                                # this is the case for single independent activity or custom attribute
                                df[pred_attributes] = 0
                            # multiple end activities (churn) are monitored together
                            if not type(pred_attributes) == np.str:
                                case_ids = []
                                for pred_attribute in pred_attributes:
                                    case_ids.extend(
                                        df.loc[df[self.ex_info.activity] == pred_attribute][
                                            self.ex_info.id].unique().tolist())
                            else:
                                case_ids = df.loc[df[pred_column] == pred_attributes][self.ex_info.id].unique()
                            if type(pred_attributes) == np.str:
                                df.reset_index(inplace=True)
                                # take start indexes of cases that contain that activity
                                # and the index where there is the last target activity for that case
                                start_case_indexes = \
                                    df.loc[df[self.ex_info.id].isin(case_ids)].groupby(self.ex_info.id,
                                                                                       as_index=False).agg(
                                        'first')[
                                        'index']
                                last_observed_activity_indexes = \
                                    df.loc[(df[self.ex_info.id].isin(case_ids)) & (
                                            df[self.ex_info.activity] == pred_attributes)].groupby(
                                        self.ex_info.id).agg('last')['index']
                                df_indexes = pd.concat([start_case_indexes.reset_index(drop=True),
                                                        last_observed_activity_indexes.reset_index(drop=True).rename(
                                                            "index_1")],
                                                       axis=1)
                                index_list = []
                                for x, y in zip(df_indexes['index'], df_indexes['index_1']):
                                    for index in range(x, y):
                                        index_list.append(index)
                                del df["index"]
                                df.loc[df.index.isin(index_list), pred_attributes] = 1
                            else:
                                # TODO: make this more efficient also for churn prediction
                                for case_id in case_ids:
                                    for pred_attribute in pred_attributes:
                                        index = df.loc[
                                            (df[self.ex_info.id] == case_id) & (
                                                    df[self.ex_info.activity] == pred_attribute)].index
                                        # each case id corresponds to one end activity only
                                        if len(index) != 0:
                                            break
                                if len(index) == 1:
                                    index = index[0]
                                else:
                                    # if activity is performed more than once, take only the last
                                    index = index[-1]
                                # put 1 to all y_targets before that activity in the case
                                df.loc[(df[self.ex_info.id] == case_id) & (df.index < index), target_column_name] = 1
                            column_type = 'Categorical'

                            # we take only the columns we are interested in
                            if not type(pred_attributes) == np.str:
                                target_column = df[target_column_name]
                                df.drop(target_column_name, axis=1, inplace=True)
                            else:
                                target_column = df[pred_attributes]
                                target_column_name = pred_attributes
                                df.drop(pred_attributes, axis=1, inplace=True)
                            target_column = pd.concat([target_column, df["remaining_time"]], axis=1)
                    print("Calculated target column")
                elif pred_column == 'remaining_time':
                    column_type = 'Numeric'
                    if use_remaining_for_num_targets:
                        event_level = 1
                        target_column_name = 'remaining_time'
                    else:
                        event_level = 0
                        if end_date_name is not None:
                            leadtime_per_case = df.groupby(self.ex_info.id).agg("first")["activity_duration"] \
                                                + df.groupby(self.ex_info.id).agg("first")["remaining_time"]
                        else:
                            leadtime_per_case = df.groupby(self.ex_info.id).agg("first")["remaining_time"]
                        df["lead_time"] = df[self.ex_info.id].map(leadtime_per_case)
                        target_column_name = 'lead_time'

                    # remove rows where remaining_time=0
                    df = df[df.loc[:, 'remaining_time'] != 0].reset_index(drop=True)

                    if use_remaining_for_num_targets:
                        target_column = df.loc[:, 'remaining_time'].reset_index(drop=True)
                    else:
                        target_column = df.loc[:, 'lead_time'].reset_index(drop=True)
                        del df["remaining_time"]
                    del df[target_column_name]
                    print("Calculated target column")

                # eliminate rows where remaining time = 0 (nothing to predict) - only in train
                if pred_column != 'remaining_time':
                    df = df[df.loc[:, 'remaining_time'] != 0].reset_index(drop=True)
                    target_column = target_column[target_column.loc[:, 'remaining_time'] != 0].reset_index(drop=True)
                    del df['remaining_time']
                    del target_column['remaining_time']

                # convert case id series to string and cut spaces if we have dirty data (both int and string)
                df.iloc[:, 0] = df.iloc[:, 0].apply(str)
                df.iloc[:, 0] = df.iloc[:, 0].apply(lambda x: x.strip())
                test_case_ids = df.iloc[:, 0]
                # convert back to int in order to use median (if it is a string convert to categoric int values)
                try:
                    df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0])
                except ValueError:
                    pass
                    # df.iloc[:, 0] = pd.Series(df.iloc[:, 0]).astype('category').cat.codes.values

                self.generate_train_and_test_sets(df, target_column, target_column_name, event_level, column_type,
                                                  override,
                                                  self.ex_info.id, df_completed_cases,
                                                  activity_name=self.ex_info.activity)

                # if grid is True:
                #     if not os.path.exists(self.paths.folders['model']['params']):
                #         grid_search(model_type, mean_events, column_type)
                #         return
                #     elif "history" not in IOManager.read(self.paths.folders['model']['params']):
                #         grid_search(model_type, mean_events, column_type)
                #         if "history" in IOManager.read(self.paths.folders['model']['params']) or model_type == "end":
                #             compare_best_validation_curves(pred_column, mean_reference_target)
                #         return
            # prepare_data_for_ml_model_and_predict(df, target_column, target_column_name, event_level, column_type,
            #                                       mode,
            #                                       experiment_name, override, activity_column_name, pred_column,
            #                                       pred_attributes, model_type, mean_events, mean_reference_target,
            #                                       history, df_completed_cases, case_id_name, grid, shap)
            # if end is True:
            #     break

        # create_folders(folders, safe=override)
        # shap = False
        # prepare_dataset(df=df, case_id_name=case_id_name, activity_column_name=activity_name,
        #                 start_date_name=start_date_name, date_format=date_format, end_date_name=end_date_name,
        #                 pred_column=pred_column, mode="train", experiment_name=experiment_name, override=override,
        #                 pred_attributes=pred_attributes, costs=costs, working_times=working_time,
        #                 resource_column_name=resource_column_name, role_column_name=role_column_name,
        #                 use_remaining_for_num_targets=use_remaining_for_num_targets,
        #                 predict_activities=predict_activities,
        #                 lost_activities=lost_activities, retained_activities=retained_activities,
        #                 custom_attribute_column_name=custom_attribute_column_name, shap=shap)

        # fromDirectory = os.path.join(os.getcwd(), 'experiment_files')
        # toDirectory = os.path.join(os.getcwd(), 'experiments', experiment_name)
        #
        # # copy results as a backup
        # if os.path.os.path.exists(toDirectory):
        #     shutil.rmtree(toDirectory)
        #     shutil.copytree(fromDirectory, toDirectory)
        # else:
        #     shutil.copytree(fromDirectory, toDirectory)
        #     print('Data and results saved')
        #
        # print('Starting import model and data..')
        # if not os.path.os.path.exists(f'expls_{experiment_name}'):
        #     os.mkdir(f'expls_{experiment_name}')
        #     print('explanation folder created')
        #
        # if not os.path.os.path.exists(f'explanations/{experiment_name}'):
        #     os.mkdir(f'explanations/{experiment_name}')
        #     print('other explanation folder created')
        #
        # info = IOManager.read(self.paths.folders['model']['data_info'])
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
        # return 'Training_finished'

    def convert_datetime_to_sec(self, date_format="%Y-%m-%d %H:%M:%S"):
        if not np.issubdtype(self.data[self.ex_info.timestamp], np.number):
            self.data[self.ex_info.timestamp] = pd.to_datetime(self.data[self.ex_info.timestamp], format=date_format)
            self.data[self.ex_info.timestamp] = self.data[self.ex_info.timestamp].astype(np.int64) / int(1e9)
        return date_format

    def write_costs_reference_mean(self, df, case_id_name):
        avg_cost = (df.groupby(case_id_name)["case_cost"].max() -
                    df.groupby(case_id_name)["case_cost"].min()).mean()
        mean = {'completedMean': round(avg_cost, 2)}
        print(f"Average completed cost: {mean}")
        write(mean, self.paths.folders["results"]["mean"])
        return round(avg_cost, 2)

    def write_leadtime_reference_mean(self, df, case_id_name, start_date_name, end_date_name):
        # avg of all the completed cases to be passed as a reference value
        if end_date_name is not None:
            avg_duration_days = (df.groupby(case_id_name)[end_date_name].max() -
                                 df.groupby(case_id_name)[start_date_name].min()).mean()
        else:
            avg_duration_days = (df.groupby(case_id_name)[start_date_name].max() -
                                 df.groupby(case_id_name)[start_date_name].min()).mean()
        mean = {'completedMean': round(avg_duration_days, 2)}
        print(f'"Average completed lead time (days): {mean["completedMean"] / (3600 * 24 * 1000)}"')
        write(mean, self.paths.folders["results"]["mean"])
        return round(avg_duration_days, 2)

    def prepare_data_and_add_features(self, df, case_id_name, start_date_name, date_format, end_date_name):
        # df = fillna(df, date_format)
        if end_date_name is not None:
            df[end_date_name] = df[end_date_name].fillna(df[start_date_name])
            # df = fill_missing_end_dates(df, start_date_position, end_date_position)
        # df = convert_strings_to_datetime(df, date_format)
        df = self.fillna(df)
        df = self.move_essential_columns(df, case_id_name, start_date_name)
        df = self.sort_df(df, case_id_name, start_date_name)
        df = self.add_features(df, end_date_name)
        df["weekday"].replace({0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
                               4: "Friday", 5: "Saturday", 6: "Sunday"}, inplace=True)
        return df

    def fillna(self, df):
        for i, column in enumerate(df.columns):
            if df[column].dtype == 'object':
                df[column] = df[column].fillna("missing")
        return df

    def move_essential_columns(self, df, case_id_name, start_date_name):
        columns = df.columns.to_list()
        # move case_id column and start_date column to always know their position
        columns.pop(columns.index(case_id_name))
        columns.pop(columns.index(start_date_name))
        df = df[[case_id_name, start_date_name] + columns]
        return df

    def sort_df(self, df, case_id_name, start_date_name):
        df.sort_values([case_id_name, start_date_name], axis=0, ascending=True, inplace=True, kind='quicksort',
                       na_position='last')
        return df

    def calculate_costs(self, df, costs, working_times, activity_column_name, resource_column_name, role_column_name,
                        case_id_name):
        """
        cost is activity cost + resource or role cost(hour)*working time

        resource is present:
        activity_cost + resource_cost (if present) * working_time
        only role cost:
        activity_cost + role_cost (if present) * working_time
        no specific resource or role cost:
        activity_cost + default_resource (if present, otherwise default_role) * working_time

        Note that in MyInvenio, costs can vary for different periods of time, but this is not currently implemented here.

        """

        # preallocate case cost column
        import ipdb;
        ipdb.set_trace()
        df["case_cost"] = 0
        activities = df[activity_column_name].unique()
        roles = df[role_column_name].unique()
        resources = df[resource_column_name].unique()
        # assign role cost* working time since we don't have resource cost
        for resource in costs["resourceCost"].keys():
            if resource != "__DEFAULT__":
                df.loc[df[resource_column_name] == resource, "case_cost"] = costs["resourceCost"][resource]
        for role in costs["roleCost"].keys():
            if role != "__DEFAULT__":
                df.loc[(df[role_column_name] == role) & (df["case_cost"] == 0), "case_cost"] = costs["roleCost"][role]
        if "__DEFAULT__" in costs["resourceCost"]:
            df.loc[df["case_cost"] == 0, "case_cost"] = costs["resourceCost"]["__DEFAULT__"]
        elif "__DEFAULT__" in costs["roleCost"]:
            df.loc[df["case_cost"] == 0, "case_cost"] = costs["roleCost"]["__DEFAULT__"]

        # multiply by working time and then sum the cost for the activity
        for activity in activities:
            if activity in working_times:
                df.loc[df[activity_column_name] == activity, "case_cost"] *= working_times[activity]
            elif "__DEFAULT__" in working_times:
                df.loc[df[activity_column_name] == activity, "case_cost"] *= working_times["__DEFAULT__"]

            if activity in costs["activityCost"]:
                df.loc[df[activity_column_name] == activity, "case_cost"] += costs["activityCost"][activity]
            elif "__DEFAULT__" in costs["activityCost"]:
                df.loc[df[activity_column_name] == activity, "case_cost"] += costs["activityCost"]["__DEFAULT__"]

        # at this point you sum the cost for previous events of the case (is a case cost, not event cost)
        df["case_cost"] = df.groupby(case_id_name)["case_cost"].cumsum()
        import ipdb;
        ipdb.set_trace()
        return df

    def add_features(self, df, end_date_name):
        dataset = df.values
        if end_date_name is not None:
            end_date_position = df.columns.to_list().index(end_date_name)
        else:
            end_date_position = None
        traces = []
        # analyze first dataset line
        caseID = dataset[0][0]
        activityTimestamp = dataset[0][1]
        starttime = activityTimestamp
        lastevtime = activityTimestamp
        current_activity_end_date = None
        line = dataset[0]
        if end_date_position is not None:
            # at the begin previous and current end time are the same
            current_activity_end_date = dataset[0][end_date_position]
            line = np.delete(line, end_date_position)
        num_activities = 1
        activity = self.create_activity_features(line, starttime, lastevtime, caseID, current_activity_end_date)
        traces.append(activity)
        for line in dataset[1:, :]:
            case = line[0]
            if case == caseID:
                # continues the current case
                activityTimestamp = line[1]
                if end_date_position is not None:
                    current_activity_end_date = line[end_date_position]
                    line = np.delete(line, end_date_position)
                activity = self.create_activity_features(line, starttime, lastevtime, caseID, current_activity_end_date)

                # lasteventtimes become the actual
                lastevtime = activityTimestamp
                traces.append(activity)
                num_activities += 1
            else:
                caseID = case
                traces = self.calculate_remaining_time_for_actual_case(traces, num_activities)

                activityTimestamp = line[1]
                starttime = activityTimestamp
                lastevtime = activityTimestamp
                if end_date_position is not None:
                    current_activity_end_date = line[end_date_position]
                    line = np.delete(line, end_date_position)
                activity = self.create_activity_features(line, starttime, lastevtime, caseID, current_activity_end_date)
                traces.append(activity)
                num_activities = 1

        # last case
        traces = self.calculate_remaining_time_for_actual_case(traces, num_activities)
        # construct df again with new features
        columns = df.columns
        if end_date_position is not None:
            columns = columns.delete(end_date_position)
        columns = columns.delete(1)
        columns = columns.to_list()
        if end_date_position is not None:
            # columns.extend(["time_from_previous_event(start)", "time_from_midnight",
            #                 "weekday", "activity_duration", "remaining_time"])
            columns.extend(["time_from_start", "time_from_previous_event(start)", "time_from_midnight",
                            "weekday", "activity_duration", "remaining_time"])
        else:
            # columns.extend(["time_from_previous_event(start)", "time_from_midnight",
            #                 "weekday", "remaining_time"])
            columns.extend(["time_from_start", "time_from_previous_event(start)", "time_from_midnight",
                            "weekday", "remaining_time"])
        df = pd.DataFrame(traces, columns=columns)
        print("Features added")
        return df

    def calculate_remaining_time_for_actual_case(self, traces, num_activities):
        finishtime = self.find_case_finish_time(traces, num_activities)
        for i in range(num_activities):
            # calculate remaining time to finish the case for every activity in the actual case
            traces[-(i + 1)][-1] = (finishtime - traces[-(i + 1)][-1]).total_seconds()
        return traces

    def calculate_time_from_midnight(self, actual_datetime):
        midnight = actual_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        timesincemidnight = (actual_datetime - midnight).total_seconds()
        return timesincemidnight

    def create_activity_features(self, line, starttime, lastevtime, caseID, current_activity_end_date):
        activityTimestamp = line[1]
        activity = []
        activity.append(caseID)
        for feature in line[2:]:
            activity.append(feature)

        # We get timestamps in ms
        activityTimestamp = datetime.fromtimestamp(int(activityTimestamp) / 1_000)
        starttime = datetime.fromtimestamp(int(starttime) / 1_000)
        lastevtime = datetime.fromtimestamp(int(lastevtime) / 1_000)

        # add features: time from trace start, time from last_startdate_event, time from midnight, weekday
        activity.append((activityTimestamp - starttime).total_seconds())
        activity.append((activityTimestamp - lastevtime).total_seconds())
        activity.append(self.calculate_time_from_midnight(activityTimestamp))
        activity.append(activityTimestamp.weekday())
        # if there is also end_date add features time from last_enddate_event and activity_duration.
        # hotfix: sometimes "missing" comes from myinvenio
        if current_activity_end_date is not None:
            current_activity_end_date = datetime.fromtimestamp(int(current_activity_end_date) / 1_000)
            activity.append((current_activity_end_date - activityTimestamp).total_seconds())
            # add timestamp end or start to calculate remaining time later
            activity.append(current_activity_end_date)
        else:
            activity.append(activityTimestamp)
        return activity

    def find_case_finish_time(self, trace, num_activities):
        # we find the max finishtime for the actual case
        for i in range(num_activities):
            if i == 0:
                finishtime = trace[-i - 1][-1]
            else:
                if trace[-i - 1][-1] > finishtime:
                    finishtime = trace[-i - 1][-1]
        return finishtime

    def new_case_level_attribute_detection(self, df, case_id_name, mode):
        # needed for explanations later
        if mode == "train":
            if os.path.exists(self.paths.folders['model']['data_info']):
                info = IOManager.read(self.paths.folders['model']['data_info'])
                info["case_level_attributes"] = []
            else:
                info = {"case_level_attributes": []}
            case_level_attributes = []
            for column in df.columns[1:]:
                # if there is at least 1 False in the series it is an event-level attribute
                if False not in df.groupby(case_id_name)[column].nunique().eq(1).values:
                    case_level_attributes.append(column)
                    info["case_level_attributes"].append(column)
            # write(info, self.paths.folders['model']['data_info'])
        else:
            case_level_attributes = IOManager.read(self.paths.folders['model']['data_info'])["case_level_attributes"]
        return case_level_attributes

    def apply_history_to_df(self, df, case_id_name, activity_column_name, timestep, case_level_attributes):
        remaining_time = df["remaining_time"]
        if timestep == "no history":
            return df
        elif timestep == "aggr hist":
            df = self.add_aggregated_history(df, case_id_name, activity_column_name)
            print("Added history")
            return df
        # we delete remaining_time and later we reapply it in order to not duplicate it
        del df["remaining_time"]
        df_original = df.copy()
        float_columns = df.select_dtypes(include=['float64']).columns
        int_columns = df.select_dtypes(include=['int']).columns
        int_columns = [x for x in int_columns if (x != case_id_name) and (x not in case_level_attributes)]
        float_columns = [x for x in float_columns if (x != case_id_name) and (x not in case_level_attributes)]

        # at step 2 you need to append also step 1
        for i in range(1, int(timestep) + 1):
            df_shifted = df_original.copy()
            # don't shift case_level columns
            df_shifted.drop(case_level_attributes, axis=1, inplace=True)
            df_shifted = df_shifted.groupby(case_id_name).shift(i, fill_value="No previous activity").drop(
                [case_id_name],
                axis=1)
            # keep numerical columns as numbers for history
            df_shifted.loc[df_shifted[activity_column_name] == "No previous activity", float_columns] = -1
            df_shifted.loc[df_shifted[activity_column_name] == "No previous activity", int_columns] = -1
            df_shifted[float_columns] = df_shifted[float_columns].astype("float64")
            df_shifted[int_columns] = df_shifted[int_columns].astype("float64")
            df_shifted.columns = df_shifted.columns + f' (-{i})'
            df = df.merge(df_shifted, left_index=True, right_index=True)

        # put to missing categorical nan columns
        for i, column in enumerate(df.columns):
            if df[column].dtype == 'object':
                df[column] = df[column].fillna("missing")
        # df = add_aggregated_history(df, case_id_name, activity_column_name)
        df["remaining_time"] = remaining_time
        print("Added history")
        return df

    def add_aggregated_history(self, df, case_id_name, activity_column_name):
        for activity in df[activity_column_name].unique():
            df[f"# {activity_column_name}={activity}"] = 0
            # first put 1 in correspondence to each activity
            df.loc[df[activity_column_name] == activity, f"# {activity_column_name}={activity}"] = 1
            # sum the count from the previous events
            df[f"# {activity_column_name}={activity}"] = \
                df.groupby(case_id_name)[f"# {activity_column_name}={activity}"].cumsum()
        return df

    def detect_case_level_attribute(self, df, pred_column):
        # take some sample cases and understand if the attribute to be predicted is event-level or case-level
        # we assume that the column is numeric or a string
        event_level = 0
        case_ids = df[df.columns[0]].unique()
        case_ids = case_ids[:int((len(case_ids) / 100))]
        for case in case_ids:
            df_reduced = df[df[df.columns[0]] == case]
            if len(df_reduced[pred_column].unique()) == 1:
                continue
            else:
                event_level = 1
                break
        return event_level

    def generate_train_and_test_sets(self, df, target_column, target_column_name, event_level, column_type, override,
                                     case_id_name, df_completed_cases, activity_name):
        # reattach predict column before splitting
        df[target_column_name] = target_column
        df.columns = df.columns.str.replace('time_from_midnight', 'daytime')
        # around 2/3 cases are the training set, 1/3 is the test set
        second_quartile = len(np.unique(df.iloc[:, 0])) / 2
        third_quartile = len(np.unique(df.iloc[:, 0])) / 4 * 3

        categorical_features = df.iloc[:, 1:-1].select_dtypes(exclude=np.number).columns
        df[categorical_features] = df[categorical_features].astype(str)

        if (column_type == "Categorical") and ((len(df[df[target_column_name] == 0][case_id_name].unique()) /
                                                len(df[df[target_column_name] == 1][case_id_name].unique())) > 10):
            unbalanced = True
        else:
            unbalanced = False

        # DO NOT REMOVE CASE, IT IS NEEDED IF WE WANT TO COMPARE DIFFERENT ALGORITHMS ON THE TEST SET
        # if trained model os.path.exists just pick the previously chosen case indexes
        if ("train_cases" in IOManager.read(self.paths.folders['model']['data_info'])) or (os.path.exists(self.paths.folders['model']['model'])
                                                                      and override is False):
            train_cases = IOManager.read(self.paths.folders['model']['data_info'])["train_cases"]
            print("Reloaded train cases")
            # dfTrain = df[df[case_id_name].isin(train_cases)]
            dfTest = df[~df[case_id_name].isin(train_cases)]
        else:
            # we consider the class unbalanced when the class is 1/10 or lower (equally distribute the 1 targets)
            if unbalanced:
                number_train_cases = round((third_quartile + second_quartile) / 2)
                # 50% of cases_1 go in train, 50% in test
                cases_0 = df[df[target_column_name] == 0][case_id_name].unique()
                cases_1 = df[df[target_column_name] == 1][case_id_name].unique()
                # if there is at least a 1 in the case (cases_1) then do not include it in cases_0
                cases_0 = cases_0[~np.isin(cases_0, cases_1)]
                number_train_cases_1 = round(len(cases_1) / 2)
                number_train_cases_0 = number_train_cases - number_train_cases_1
                train_cases_0 = np.random.choice(cases_0, size=number_train_cases_0, replace=False)
                train_cases_1 = np.random.choice(cases_1, size=number_train_cases_1, replace=False)
                train_cases = np.append(train_cases_0, train_cases_1)
                dfTest = df[~df[case_id_name].isin(train_cases)]

            else:
                # take cases for training in random order (the seed is fixed for replicability)
                cases = df[case_id_name].unique()
                number_train_cases = round((third_quartile + second_quartile) / 2)
                train_cases = np.random.choice(cases, size=number_train_cases, replace=False)
                # dfTrain = df[df[case_id_name].isin(train_cases)]
                dfTest = df[~df[case_id_name].isin(train_cases)]
        df_completed_cases = df_completed_cases.loc[df_completed_cases['CASE ID'].isin(dfTest[case_id_name].unique()),
                             :]
        df_completed_cases.to_csv(self.paths.folders['results']['completed'], index=False)

        # TODO: investigate reducing number of 0 examples. Investigate reducing 1 and using fraud detection algo
        # Investigate 3 models in parallel trained on balanced datasets
        # in that case how do we cope with the parameters and the grid_search?

        if unbalanced:
            # The 1 targets should be distributed proportionally also between validation and train
            if ("train_cases" in IOManager.read(self.paths.folders['model']['data_info'])):
                dfTrain = df[df[case_id_name].isin(train_cases)]
                train_cases_0 = dfTrain.loc[dfTrain[target_column_name] == 0, case_id_name].unique()
                train_cases_1 = dfTrain.loc[dfTrain[target_column_name] == 1, case_id_name].unique()
                train_cases_0 = train_cases_0[~np.isin(train_cases_0, train_cases_1)]
            valid_cases_0 = np.random.choice(train_cases_0, size=int(len(train_cases_0) / 100 * 20), replace=False)
            valid_cases_1 = np.random.choice(train_cases_1, size=int(len(train_cases_1) / 100 * 20), replace=False)
            valid_cases = np.append(valid_cases_0, valid_cases_1)
        else:
            valid_cases = np.random.choice(train_cases, size=int(len(train_cases) / 100 * 20), replace=False)
        dfValid = df[df[case_id_name].isin(valid_cases)]
        dfTrain_without_valid = df[df[case_id_name].isin(train_cases) & ~df[case_id_name].isin(valid_cases)]
        dfTrain = dfTrain_without_valid.append(dfValid, ignore_index=True)

        # if unbalanced: #leave this if you want to balance the num of the targets
        #     #at this point you can balance the number of the targets
        #     dfTrain, dfTrain_without_valid, dfValid = balance_examples_target_column(df, case_id_name, train_cases_0, train_cases_1)

        if not os.path.exists(self.paths.folders['model']['model']) or override:
            save_column_information_for_real_predictions(dfTrain, dfTrain_without_valid, dfTest, dfValid, train_cases,
                                                         event_level, target_column_name, column_type,
                                                         categorical_features,
                                                         activity_name)
