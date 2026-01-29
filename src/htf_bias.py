def htf_trend_bias(htf_candles, ema_fast, ema_slow, i):
    """
    Determines higher-timeframe trend bias.

    Returns:
        "bullish", "bearish", or None
    """

    # Safety: indicators not ready
    if i is None:
        return None

    if ema_fast[i] is None or ema_slow[i] is None:
        return None

    # Bullish HTF trend
    if ema_fast[i] > ema_slow[i]:
        return "bullish"

    # Bearish HTF trend
    if ema_fast[i] < ema_slow[i]:
        return "bearish"

    return None
