import pandas as pd

import explain_recsys
from gui.model.Experiment import Experiment
from gui.model.IO.IOManager import Paths, read, write
import gui.model.IO.IOManager as gui_io


class Explainer:
    def __init__(self, experiment_info: Experiment):
        self.real_dict = None
        self.rec_dict = None
        self.ex_info = experiment_info
        self.paths = Paths(self.ex_info.ex_name)
        self.df_run = pd.read_csv(self.paths.folders['recommendations']['df_run'])

    def calculate_best_scores(self):
        # Read the dictionaries with the scores
        self.rec_dict = gui_io.read(self.paths.folders['recommendations']['rec_dict'])
        self.real_dict = gui_io.read(self.paths.folders['recommendations']['real_dict'])
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

    def calculate_trace_groundtruth(self, trace_idx, value):
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
            quantitative_vars = read(self.paths.folders['variables']['qnt'])
            qualitative_vars = read(self.paths.folders['variables']['qlt'])
            model = read(self.paths.folders['model']['model'])
            # quantitative_vars = pickle.load(open(f'explanations/{experiment_name}/quantitative_vars.pkl', 'rb'))
            # qualitative_vars = pickle.load(open(f'explanations/{experiment_name}/qualitative_vars.pkl', 'rb'))
            # pred_column = pickle.load(open('gui_backup/pred_column.pkl', 'rb'))

            # model = utils.import_predictor(experiment_name=experiment_name, pred_column=pred_column)
            # rec_dict = pickle.load(open(f'recommendations/{experiment_name}/rec_dict.pkl', 'rb'))[trace_idx]
            rec_dict = read(self.paths.folders['recommendations']['rec_dict'])[trace_idx]
            rec_dict = dict(sorted(rec_dict.items(), key=lambda x: x[1]))
            rec_dict = {A: N for (A, N) in [x for x in rec_dict.items()][:3]}

            for var in (set(quantitative_vars).union(qualitative_vars)):
                trace_exp[var] = "none"
            groundtruth_explanation = explain_recsys.evaluate_shap_vals(trace_exp, model, self.df_run, self.ex_info.id)
            groundtruth_explanation = [a for a in groundtruth_explanation]
            groundtruth_explanation = [trace_idx] + groundtruth_explanation
            groundtruth_explanation = pd.Series(groundtruth_explanation,
                                                index=[i for i in self.df_run.columns if i != 'y'])

            # Save also groundtruth explanations
            # write(groundtruth_explanation, self.paths.get_explanation_path(trace_idx, 'groundtruth'))
            groundtruth_explanation.to_csv(self.paths.get_gt_explanation_path(trace_idx))
            # groundtruth_explanation.drop([self.ex_info.id] + [i for i in (set(quantitative_vars).union(qualitative_vars))],
            #                              inplace=True)



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
            explanations = explain_recsys.evaluate_shap_vals(trace_exp, model, X_test, self.ex_info.id)
            explanations = [a for a in explanations]
            explanations = [trace_idx] + explanations
            explanations = pd.Series(explanations, index=[i for i in trace_exp.columns if i != 'y'])
            explanations.to_csv(self.paths.get_explanation_path(trace_idx, act))
            #
            # # Take the best-4 deltas
            # explanations.drop([self.ex_info.id] + [i for i in (set(quantitative_vars).union(qualitative_vars))],
            #                   inplace=True)
            # groundtruth_explanation = groundtruth_explanation[list(explanations.index)]
            # deltas_expls = groundtruth_explanation - explanations
            # deltas_expls.sort_values(ascending=False, inplace=True)
            # idxs_chosen = deltas_expls.index[:4]
            #
            # pickle.dump(idxs_chosen, open(f'explanations/{experiment_name}/{trace_idx}_{act}_idx_chosen.pkl', 'wb'))
            # pickle.dump(last, open(f'explanations/{experiment_name}/{trace_idx}_last.pkl', 'wb'))
            # explain_recsys.plot_explanations_recs(groundtruth_explanation, explanations, idxs_chosen, last,
            #                                       experiment_name, trace_idx, act)
            #
            # trace_idx = pickle.load(open('gui_backup/chosen_trace.pkl', 'rb'))
            # act = value
            # experiment_name = 'Gui_experiment'
            #
            # print('Generating explanations..')
            #
            # explanations = pd.read_csv(f'explanations/{experiment_name}/{trace_idx}_{act}_expl_df.csv', index_col=0)
            # idxs_chosen = pickle.load(open(f'explanations/{experiment_name}/{trace_idx}_{act}_idx_chosen.pkl', 'rb'))
            # groundtruth_explanation = pd.read_csv(f'explanations/{experiment_name}/{trace_idx}_expl_df_gt.csv',
            #                                       index_col=0)
            # last = pickle.load(open(f'explanations/{experiment_name}/{trace_idx}_last.pkl', 'rb'))
            #
            # expl_df = {"Following Recommendation": [float(i) / 60 for i in
            #                                         explanations['0'][idxs_chosen].sort_values(ascending=False).values],
            #            "Actual Value": [float(i) / 60 for i in
            #                             groundtruth_explanation['0'][idxs_chosen].sort_values(ascending=False).values]}
            #
            # last = last[idxs_chosen]
            # feature_names = [str(i) for i in last.index]
            # feature_values = [str(i) for i in last.values]
            #
            # index = [feature_names[i] + '=' + feature_values[i] for i in range(len(feature_values))]
            # plot_df = pd.DataFrame(data=expl_df)
            # plot_df.index = index
