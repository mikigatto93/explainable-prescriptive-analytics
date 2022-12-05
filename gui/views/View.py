from abc import ABC, abstractmethod


class View(ABC):
    def __init__(self, pathname='', order=-1):
        self.pathname = pathname
        self.order = order

    @abstractmethod
    def get_layout(self):
        pass

