import os.path

import pandas as pd

import explain_recsys
from gui.model.Experiment import Experiment, build_experiment_from_dict
from gui.model.IO.IOManager import Paths, read, write
import gui.model.IO.IOManager as gui_io


class Explainer:
    def __init__(self, experiment_info: Experiment):
        self.ex_info = experiment_info
        self.paths = Paths(self.ex_info.ex_name)
        self.df_run = pd.read_csv(self.paths.folders['recommendations']['df_run'])
        self.quantitative_vars = read(self.paths.folders['variables']['qnt'])
        self.qualitative_vars = read(self.paths.folders['variables']['qlt'])
        self.model = read(self.paths.folders['model']['model'])
        self.rec_dict = gui_io.read(self.paths.folders['recommendations']['rec_dict'])
        self.real_dict = gui_io.read(self.paths.folders['recommendations']['real_dict'])

    def calculate_best_scores(self):
        pred_column = self.ex_info.pred_column
        if pred_column in ['Minimize the activity occurrence', 'independent_activity']:
            res_val = 1
        else:
            res_val = 60

        # Read the variables' types
        # quantitative_vars = pickle.load(open(f'explanations/{experiment_name}/quantitative_vars.pkl', 'rb'))
        # qualitative_vars = pickle.load(open(f'explanations/{experiment_name}/qualitative_vars.pkl', 'rb'))

        # Make a dictionary with only the best scores
        best_scores = dict()
        for key in self.rec_dict.keys():
            best_scores[key] = {min(self.rec_dict[key], key=self.rec_dict[key].get): min(self.rec_dict[key].values())}

        # Make a dictionary with only the 3-best activities
        # best_3_dict = dict()
        # for key in rec_dict.keys():
        #     best_3_dict[key] = dict(sorted(rec_dict[key].items(), key=lambda item: item[1], reverse=False))
        #     best_3_dict[key] = {k: best_3_dict[key][k] for k in list(best_3_dict[key])[:3]}

        kpis_dict = dict()
        real_dict = dict(sorted(self.real_dict.items(), key=lambda x: list(x[1].values())[0]))
        # Added (list(real_dict[key].values())[0]*.1) for showing also not so good cases
        for key in real_dict.keys():
            if list(best_scores[key].values())[0] <= list(real_dict[key].values())[0] + (
                    list(real_dict[key].values())[0] * .05):
                kpis_dict[key] = [list(best_scores[key].values())[0], list(real_dict[key].values())[0]]

        kpis_dict = {str(A): N for (A, N) in [x for x in kpis_dict.items()]}
        kpis_dict = dict(sorted(kpis_dict.items(), key=lambda item: item[1][1]))
        return kpis_dict

    def get_best_n_scores_by_trace(self, trace_id, n):
        trace_pred = self.rec_dict[trace_id]

        # create list of tuples (activity_name, value) ordered by value (ascending)
        trace_pred_ord = [(k, v) for k, v in sorted(trace_pred.items(), key=lambda item: item[1])]

        real_pred = self.real_dict[trace_id]
        trace_real_pred = [(k, v) for k, v in real_pred.items()]

        return {
            'rec': trace_pred_ord[0:n],
            'real': trace_real_pred
        }

    def calculate_explanation(self, trace_idx, value):
        self.df_run[self.ex_info.id] = [str(i) for i in self.df_run[self.ex_info.id]]

        if value in set(self.df_run[self.ex_info.activity]):
            act = value

            for i in self.df_run.columns:
                if 'Unnamed' in i:
                    del self.df_run[i]
            # self.ex_info.id = pickle.load(open('gui_backup/self.ex_info.id.pkl', 'rb'))
            # experiment_name = 'Gui_experiment'
            X_test = self.df_run.copy()
            # traces_hash = pickle.load(open('gui_backup/transition_system.pkl', 'rb'))

            trace_exp = self.df_run[self.df_run[self.ex_info.id] == trace_idx].copy()
            trace = self.df_run[self.df_run[self.ex_info.id] == trace_idx].iloc[:, 1:].copy()
            trace_exp.rename(columns={'time_from_midnight': 'daytime'}, inplace=True)
            trace.rename(columns={'time_from_midnight': 'daytime'}, inplace=True)

            # start = time.time()
            # quantitative_vars = pickle.load(open(f'explanations/{experiment_name}/quantitative_vars.pkl', 'rb'))
            # qualitative_vars = pickle.load(open(f'explanations/{experiment_name}/qualitative_vars.pkl', 'rb'))
            # pred_column = pickle.load(open('gui_backup/pred_column.pkl', 'rb'))

            # model = utils.import_predictor(experiment_name=experiment_name, pred_column=pred_column)
            # rec_dict = pickle.load(open(f'recommendations/{experiment_name}/rec_dict.pkl', 'rb'))[trace_idx]
            rec_dict = read(self.paths.folders['recommendations']['rec_dict'])[trace_idx]
            rec_dict = dict(sorted(rec_dict.items(), key=lambda x: x[1]))
            rec_dict = {A: N for (A, N) in [x for x in rec_dict.items()][:3]}

            for var in (set(self.quantitative_vars).union(self.qualitative_vars)):
                trace_exp[var] = "none"
            groundtruth_explanation = explain_recsys.evaluate_shap_vals(trace_exp, self.model, self.df_run,
                                                                        self.ex_info.id)
            groundtruth_explanation = [a for a in groundtruth_explanation]
            groundtruth_explanation = [trace_idx] + groundtruth_explanation
            groundtruth_explanation = pd.Series(groundtruth_explanation,
                                                index=[i for i in self.df_run.columns if i != 'y'])

            # Save also groundtruth explanations
            # write(groundtruth_explanation, self.paths.get_explanation_path(trace_idx, 'groundtruth'))
            write(groundtruth_explanation.to_dict(), self.paths.get_gt_explanation_path(trace_idx))
            # print('____________')
            # print(groundtruth_explanation)
            # print('____________')
            # groundtruth_explanation.drop([self.ex_info.id] + [i for i in (set(quantitative_vars).union(qualitative_vars))],
            #                              inplace=True)
            # print(groundtruth_explanation)

            # # stampa l'ultima riga di trace normale
            # trace_exp.iloc[-1].to_csv(f'explanations/{experiment_name}/{trace_idx}_expl_df_values.csv')
            # last = trace_exp.iloc[-1].copy().drop(
            #     [self.ex_info.id] + [i for i in (set(quantitative_vars).union(qualitative_vars))])
            # next_activities = list(rec_dict.keys())  # TODO: Note that is only optimized for minimizing a KPI

            trace_exp.reset_index(drop=True, inplace=True)
            trace_exp.loc[len(trace_exp) - 1, self.ex_info.activity] = act
            for i in trace_exp.columns:
                if 'Unnamed' in i:
                    del self.df_run[i]
            explanations = explain_recsys.evaluate_shap_vals(trace_exp, self.model, X_test, self.ex_info.id)
            explanations = [a for a in explanations]
            explanations = [trace_idx] + explanations
            explanations = pd.Series(explanations, index=[i for i in trace_exp.columns if i != 'y'])
            write(explanations.to_dict(), self.paths.get_explanation_path(trace_idx, act))

    def generate_explanations_dataframe(self, trace_id, value):
        try:
            groundtruth_explanation = pd.read_json(self.paths.get_gt_explanation_path(trace_id), typ='series')
            explanations = pd.read_json(self.paths.get_explanation_path(trace_id, value), typ='series')
        except Exception as e:
            return None, None

        explanations.drop(
            [self.ex_info.id] + [i for i in (set(self.quantitative_vars).union(self.qualitative_vars))],
            inplace=True)

        groundtruth_explanation = groundtruth_explanation[list(explanations.index)]
        deltas_expls = groundtruth_explanation - explanations

        deltas_expls.sort_values(ascending=False, inplace=True)

        return (groundtruth_explanation.reindex(index=deltas_expls.keys()),
                explanations.reindex(index=deltas_expls.keys()))

    def check_if_explanations_exists(self, trace_id, value):
        return (os.path.isfile(self.paths.get_gt_explanation_path(trace_id)) and
                os.path.isfile(self.paths.get_explanation_path(trace_id, value)))

    def check_if_trace_is_valid(self, trace_id):
        return trace_id in self.rec_dict

    def to_dict(self):
        # def __init__(self, experiment_info: Experiment):
        #     self.real_dict = None
        #     self.rec_dict = None
        #     self.ex_info = experiment_info
        #     self.paths = Paths(self.ex_info.ex_name)
        #     self.df_run = pd.read_csv(self.paths.folders['recommendations']['df_run'])
        #     self.quantitative_vars = read(self.paths.folders['variables']['qnt'])
        #     self.qualitative_vars = read(self.paths.folders['variables']['qlt'])
        #     self.model = read(self.paths.folders['model']['model'])

        return {
            'ex_info': self.ex_info.to_dict(),
        }


def build_Explainer_from_dict(dict_obj):
    return Explainer(build_experiment_from_dict(dict_obj['ex_info']))