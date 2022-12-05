from abc import ABC, abstractmethod


class Presenter(ABC):
    def __init__(self, views):
        self.views = views

    @abstractmethod
    def register_callbacks(self):
        pass
