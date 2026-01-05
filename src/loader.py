import csv
from datetime import datetime, timedelta
from models import Candle

TIMEFRAME_MINUTES = 15

def load_candles(file_path):
    candles = []

    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            open_time = datetime.fromtimestamp(
                int(row["Open time"])
            )

            close_time = open_time + timedelta(minutes=TIMEFRAME_MINUTES)

            candles.append(
                Candle(
                    open_time=open_time,
                    close_time=close_time,
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=float(row["Volume"]),
                )
            )

    return candles
