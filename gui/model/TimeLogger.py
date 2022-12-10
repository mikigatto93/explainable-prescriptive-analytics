import json
import uuid

import os
from parse import parse


def _validate_value(val):
    if val:
        return val[0]
    else:
        return 0


class TimeLogger:
    def __init__(self):
        self.file_name = '{}.tmp'.format(uuid.uuid4())
        self.file_path = os.path.join(os.getcwd(), self.file_name)

    def add_to_stack(self, data):
        with open(self.file_path, 'w') as pf:
            pf.write(data)

    def get_from_stack(self):
        try:
            with open(self.file_path, 'rb') as pf:
                try:  # catch OSError in case of a one line file
                    pf.seek(-2, os.SEEK_END)
                    while pf.read(1) != b'\n':
                        pf.seek(-2, os.SEEK_CUR)
                except OSError:
                    pf.seek(0)
                return pf.readline().decode()
        except FileNotFoundError:
            return None

    def write(self, log_entry):
        record = str(log_entry)
        tokens = record.split(":")
        if len(tokens) > 1:
            rem = tokens[3].replace("remaining", "").strip()
            tot = tokens[4].strip()

            # tot_min = parse("{:g}m", tot)
            # tot_sec = parse("{:g}s", tot)
            # tot_ms = parse("{:g}ms", tot)
            # tot_us = parse("{:g}us", tot)
            #
            # rem_min = parse("{:g}m", rem)
            # rem_sec = parse("{:g}s", rem)
            # rem_ms = parse("{:g}ms", rem)
            # rem_us = parse("{:g}us", rem)
            #
            # obj = {
            #     'min': _validate_value(rem_min),
            #     'sec': _validate_value(rem_sec),
            #     'ms': _validate_value(rem_ms),
            #     'us': _validate_value(rem_us)
            # }
            self.add_to_stack('elapsed: {}, remaining: {}'.format(rem, tot))
