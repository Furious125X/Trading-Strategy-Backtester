def htf_trend_bias(htf_candles, ema_fast, ema_slow, i):
    if i < ema_slow:
        return None

    if ema_fast[i] > ema_slow[i]:
        return "bullish"
    elif ema_fast[i] < ema_slow[i]:
        return "bearish"

    return None

#Helper function to find corresponding HTF index
def find_htf_index(htf_candles, ltf_index):
    for i in range(len(htf_candles) - 1, -1, -1):
        if htf_candles[i]["lt_index"] <= ltf_index:
            return i
    return None
