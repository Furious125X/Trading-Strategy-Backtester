from abc import ABC, abstractmethod


class Strategy(ABC):
    def __init__(self, context):
        self.context = context

    def precompute(self):
        pass

    @abstractmethod
    def should_enter(self, index):
        pass

    @abstractmethod
    def build_trade(self, index):
        pass
