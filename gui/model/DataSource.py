from abc import ABC, abstractmethod


class DataSource(ABC):
    def __init__(self, path):
        self.file_path = path
        self.is_xes = None
        self.xes_columns_names = {}
        self.data = self.read_data(self.file_path)

    @abstractmethod
    def read_data(self, path):
        pass
