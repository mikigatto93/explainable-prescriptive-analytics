import os

from gui.model.ProgressLogger.TimeLogger import TimeLogger


class TrainProgLogger(TimeLogger):
    def write(self, log_entry):
        record = str(log_entry)
        tokens = record.split(":")
        if len(tokens) > 1:
            rem = tokens[3].replace("remaining", "").strip()
            tot = tokens[4].strip()
            self.add_to_stack('elapsed: {}, remaining: {}'.format(rem, tot))


def build_TrainProgLogger_from_dict(dict_obj):
    head, _ = os.path.split(dict_obj['file_path'])
    return TrainProgLogger(os.path.splitext(dict_obj['file_name'])[0], base_path=head)
