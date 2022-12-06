from abc import ABC, abstractmethod


class DataSource(ABC):
    def __init__(self, path):
        self.file_path = path
        self.data = self.read_data(self.file_path)

    @abstractmethod
    def read_data(self, path):
        pass
