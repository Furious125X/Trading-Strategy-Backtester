from models import Candle
from datetime import timedelta


def aggregate_candles(candles, factor):

    htf_candles = []

    for i in range(0, len(candles), factor):
        chunk = candles[i : i + factor]

        if len(chunk) < factor:
            break

        open_price = chunk[0].open
        close_price = chunk[-1].close
        high_price = max(c.high for c in chunk)
        low_price = min(c.low for c in chunk)
        volume = sum(c.volume for c in chunk)

        htf_candle = Candle(
            open_time=chunk[0].open_time,
            close_time=chunk[-1].close_time,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=volume,
        )


        htf_candle.lt_index = i

        htf_candles.append(htf_candle)

    return htf_candles


#Helper function to find corresponding HTF index
def find_htf_index(htf_candles, ltf_index):
    for i in range(len(htf_candles) - 1, -1, -1):
        if htf_candles[i].lt_index <= ltf_index:
            return i
    return None