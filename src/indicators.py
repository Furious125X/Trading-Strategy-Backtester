# indicators.py

def ema(candles, period):
    if period <= 0:
        raise ValueError("EMA period must be > 0")

    closes = [c.close for c in candles]
    ema_values = [None] * len(closes)

    k = 2 / (period + 1)

    if len(closes) < period:
        return ema_values

    sma = sum(closes[:period]) / period
    ema_values[period - 1] = sma

    for i in range(period, len(closes)):
        ema_values[i] = (closes[i] * k) + (ema_values[i - 1] * (1 - k))

    return ema_values


def rsi(candles, period=14):
    if period <= 0:
        raise ValueError("RSI period must be > 0")

    closes = [c.close for c in candles]
    rsi_values = [None] * len(closes)

    if len(closes) < period + 1:
        return rsi_values

    gains = []
    losses = []

    for i in range(1, period + 1):
        change = closes[i] - closes[i - 1]
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    if avg_loss == 0:
        rsi_values[period] = 100
    else:
        rs = avg_gain / avg_loss
        rsi_values[period] = 100 - (100 / (1 + rs))

    for i in range(period + 1, len(closes)):
        change = closes[i] - closes[i - 1]
        gain = max(change, 0)
        loss = abs(min(change, 0))

        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

        if avg_loss == 0:
            rsi_values[i] = 100
        else:
            rs = avg_gain / avg_loss
            rsi_values[i] = 100 - (100 / (1 + rs))

    return rsi_values


def atr(candles, period=14):
    if period <= 0:
        raise ValueError("ATR period must be > 0")

    atr_values = [None] * len(candles)

    if len(candles) < period + 1:
        return atr_values

    true_ranges = []

    for i in range(1, period + 1):
        high = candles[i].high
        low = candles[i].low
        prev_close = candles[i - 1].close

        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )

        true_ranges.append(tr)

    atr_current = sum(true_ranges) / period
    atr_values[period] = atr_current

    for i in range(period + 1, len(candles)):
        high = candles[i].high
        low = candles[i].low
        prev_close = candles[i - 1].close

        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )

        atr_current = (atr_current * (period - 1) + tr) / period
        atr_values[i] = atr_current

    return atr_values
