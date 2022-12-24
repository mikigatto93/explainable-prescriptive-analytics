import json
import uuid

import os
from abc import ABC, abstractmethod


class TimeLogger(ABC):
    def __init__(self, filename=str(uuid.uuid4())):
        self.file_name = filename
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

    def clear_stack(self):
        with open(self.file_path, 'w'):
            pass

    @abstractmethod
    def write(self, log_entry):
        pass
