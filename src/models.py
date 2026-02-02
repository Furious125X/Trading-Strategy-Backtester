from dataclasses import dataclass
from datetime import datetime
from enum import Enum


@dataclass
class Candle:
    open_time: datetime
    close_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


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
    entry_index: int

    exit_time: datetime | None = None
    exit_index: int | None = None
    exit_price: float | None = None

    result: str | None = None

    r_multiple: float | None = None

     # ---- CONTEXT METADATA (NEW) ----
    regime: str | None = None
    htf_bias: str | None = None
