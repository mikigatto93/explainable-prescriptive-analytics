import json
import uuid

import os
from abc import ABC, abstractmethod


class TimeLogger(ABC):
    def __init__(self, filename, base_path=os.getcwd()):
        self.file_name = '{}.prog'.format(filename)
        self.file_path = os.path.join(base_path, self.file_name)

    def free(self):
        try:
            os.remove(self.file_path)
        except OSError:
            print('OSError: File to delete does not exists')

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

    def clear_stack(self):
        with open(self.file_path, 'w'):
            pass

    def to_dict(self):
        return {
            'file_name': self.file_name,
            'file_path': self.file_path
        }

    @abstractmethod
    def write(self, log_entry):
        pass
