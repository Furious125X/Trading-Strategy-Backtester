from abc import ABC, abstractmethod


class Strategy(ABC):
    def __init__(self, candles):
        self.candles = candles

    @abstractmethod
    def precompute(self):
        pass

    @abstractmethod
    def generate_trade(self, index):
        pass
