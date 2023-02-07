import os

from gui.model.ProgressLogger.TimeLogger import TimeLogger


class RunProgLogger(TimeLogger):
    def write(self, log_entry):
        try:
            prog_perc = log_entry.split('%')[0].strip()
            prog_nums = log_entry.split('/')
            to_do = prog_nums[0].split(' ')[-1]
            done = prog_nums[1].split(' ')[0]
            self.add_to_stack('Traces analyzed: {}/{}, ({}%)'.format(to_do, done, prog_perc))
        except Exception as e:
            pass


def build_RunProgLogger_from_dict(dict_obj):
    head, _ = os.path.split(dict_obj['file_path'])
    return RunProgLogger(os.path.splitext(dict_obj['file_name'])[0], base_path=head)
