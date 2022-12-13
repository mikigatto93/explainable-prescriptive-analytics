from gui.model.Experiment import Experiment
from gui.model.IO.IOManager import Paths
import gui.model.IO.IOManager as gui_io


class Explainer:
    def __init__(self, experiment_info: Experiment):
        self.real_dict = None
        self.rec_dict = None
        self.ex_info = experiment_info
        self.paths = Paths(self.ex_info.ex_name)

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

