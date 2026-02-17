from abc import ABC, abstractmethod


class Strategy(ABC):
    def __init__(self, context):
        self.context = context

    @abstractmethod
    def precompute(self):
        pass

    @abstractmethod
    def generate_trade(self, index):
        pass
