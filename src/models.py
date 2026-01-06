from dataclasses import dataclass
from datetime import datetime

@dataclass
class Candle :
    open_time: datetime
    close_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

from enum import Enum

class Direction(Enum):
    LONG = "long"
    SHORT = "short"

@dataclass
class Trade:
    direction: Direction
    entry_price: float
    stop_loss: float
    take_profit: float
    entry_time: datetime
    exit_time: datetime | None = None
    result: str | None = None
