def aggregate_candles(candles, factor):
    """
    Aggregates lower timeframe candles into higher timeframe.
    factor = number of LTF candles per HTF candle
    """
    htf = []

    for i in range(0, len(candles), factor):
        chunk = candles[i:i + factor]
        if len(chunk) < factor:
            break

        htf.append({
            "open": chunk[0]["open"],
            "high": max(c["high"] for c in chunk),
            "low": min(c["low"] for c in chunk),
            "close": chunk[-1]["close"],
            "volume": sum(c["volume"] for c in chunk),
            "lt_index": i  # maps back to LTF
        })

    return htf
