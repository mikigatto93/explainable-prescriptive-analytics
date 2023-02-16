from abc import ABC, abstractmethod
import shutil
import os


class DataSource(ABC):
    def __init__(self, path, read_data):
        self.file_path = path
        self.is_xes = None
        self.xes_columns_names = {}
        if read_data:
            self.data = self.read_data(self.file_path)
        else:
            self.data = None

    def free(self):
        head, _ = os.path.split(self.file_path)
        print(head)
        try:
            shutil.rmtree(head)  # remove folder
        except OSError:
            print('OSError: Folder to delete does not exists')

    @abstractmethod
    def read_data(self, path):
        pass
