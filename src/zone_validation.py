import pandas as pd

def has_displacement(df, zone_index, direction, lookahead=5):
    """
    Confirms strong impulsive move away from zone
    """
    candles = df.iloc[zone_index+1 : zone_index+1+lookahead]

    if len(candles) < lookahead:
        return False

    bodies = abs(candles["close"] - candles["open"])
    ranges = candles["high"] - candles["low"]

    body_ratio = (bodies / ranges).mean()

    if direction == "bullish":
        return (
            body_ratio > 0.6 and
            candles["close"].iloc[-1] > candles["high"].iloc[0]
        )

    if direction == "bearish":
        return (
            body_ratio > 0.6 and
            candles["close"].iloc[-1] < candles["low"].iloc[0]
        )

    return False

def valid_retest(candle, zone, direction):
    """
    Ensures price respects zone on pullback
    """
    zone_high = zone["high"]
    zone_low = zone["low"]

    # candle info
    wick_low = candle["low"]
    wick_high = candle["high"]
    close = candle["close"]

    if direction == "bullish":
        # must tap zone, not close below it
        return (
            wick_low <= zone_high and
            close > zone_low
        )

    if direction == "bearish":
        return (
            wick_high >= zone_low and
            close < zone_high
        )

    return False

def zone_invalidated(candle, zone, direction):
    if direction == "bullish":
        return candle["close"] < zone["low"]

    if direction == "bearish":
        return candle["close"] > zone["high"]

    return True
