import os
import model.IO.write_functions as wf
import model.IO.read_functions as rf


class IOManager:
    model = {
        'data_info': 'data_info.json',
        'dfTrain': 'dfTrain.csv',
        'dfTrain_without_valid': 'dfTrain_without_valid.csv',
        'dfValid': 'dfValid.csv',
        'dfTest': 'dfTest.csv',
        'model': 'model.pkl',
        'params': 'model_configuration.json',
        'scores': 'models_scores.json',
        'validation_model_no_history': 'model_no_history.json',
        'validation_model_only_aggr_act_hist': 'model_aggr_hist.json',
        'validation_model_1_event_info': 'model_1_event_info.json',
        'validation_model_2_events_info': 'model_2_events_info.json',
        'validation_model_3_events_info': 'model_3_events_info.json',
        'validation_model_4_events_info': 'model_4_events_info.json',
        'validation_model_5_events_info': 'model_5_events_info.json',
        'validation_model_6_events_info': 'model_6_events_info.json',
        'validation_model_7_events_info': 'model_7_events_info.json',
        'validation_model_8_events_info': 'model_8_events_info.json'
    }

    results = {
        'running': 'results_running.csv',
        'results_completed': 'results_completed.csv',
        'completed': 'completed.csv',
        'explanations_completed': 'explanations_completed.json',
        'explanations_histogram': 'explanation_histogram.json',
        'explanations_running': 'explanations_running.json',
        'mean': 'completedMean.json',
        'scores': 'scores.json',
    }

    shap = {
        'background': 'background.npy',
        'shap_test': 'shapley_values_test_{}.npy',
        'timestep': 'timestep_histogram_{}.json',
        'heatmap': 'shap_heatmap_{}.json',
        'running': 'shapley_values_running.npy',
    }

    reader = {
        'json': rf.read_json,
        'pkl': rf.read_pickle,
        'pickle': rf.read_pickle,
        'npy': rf.read_numpy,
        'csv': rf.read_csv,
    }

    writer = {
        'json': wf.write_json,
        'pkl': wf.write_pickle,
        'pickle': wf.write_pickle,
        'npy': wf.write_numpy,
        'csv': wf.write_csv,
    }

    def __init__(self, ex_name, main_path=os.getcwd()):
        self.ex_name = ex_name  # TODO: VALIDATE NAME AS IT GOES ON A FILE PATH
        self.main_path = os.path.join(main_path, ex_name)
        self.folders = {
            'model': self.path_maker('model', IOManager.model),
            'results': self.path_maker('results', IOManager.results),
            'shap': self.path_maker('shap', IOManager.shap),
            'plots': {},
        }

    def path_maker(self, parent, d):
        return {k: os.path.join(self.main_path, parent, v) for k, v in d.items()}


def read(filename, readfn=None, **kwargs):
    """Generic read function, the normal usage is to pass the filename that we
    want to read and expect the result. This works based on files extensions,
    if the file we want to read doesn't have an extension or has a different one
    than the ones normally used we can pass a `readfn` that will be used to read
    that file.

    Args:
        filename (str): the path to the file that we want to read
        readfn (function, optional): a reading function if we want to
         control in which way to open and read the given file. Defaults to None.

    Returns:
        any: depends on the file read
    """
    if readfn:
        return readfn(filename, **kwargs)
    else:
        ext = filename.split('.')[-1]
        return IOManager.reader[ext](filename, **kwargs)


def write(data, filename, writefn=None):
    """Generic write function, the normal usage is to pass the data and the
     filename that we want to write. This works based on files extensions,
    if the file we want to write doesn't have an extension or has a different
     one than the ones normally used we can pass a `readfn` that will be used
     to write to that file.

    Args:
        data (any): any writable data structure
        filename (str): path to the file we want to write to
        writefn (function, optional): a writing function. Defaults to None.

    Returns:
        str: the passed filename
    """
    if writefn:
        writefn(data, filename)
        return filename
    else:
        ext = filename.split('.')[-1]
        IOManager.writer[ext](data, filename)
        return filename