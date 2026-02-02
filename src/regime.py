TREND_UP = "trend_up"
TREND_DOWN = "trend_down"
RANGE = "range"


def detect_regime(
    ema_fast,
    ema_slow,
    i,
    slope_lookback=5,
    slope_threshold=1e-6,
):
    """
    Regime detection using precomputed EMAs (O(1))

    Returns:
        'trend_up'
        'trend_down'
        'range'
        None if insufficient data
    """

    # ---- SAFETY: ensure EMAs exist ----
    if (
        i < slope_lookback
        or ema_fast[i] is None
        or ema_slow[i] is None
        or ema_slow[i - slope_lookback] is None
    ):
        return None

    # ---- Direction ----
    if ema_fast[i] > ema_slow[i]:
        direction = TREND_UP
    elif ema_fast[i] < ema_slow[i]:
        direction = TREND_DOWN
    else:
        return RANGE

    # ---- Slope confirmation ----
    slope = ema_slow[i] - ema_slow[i - slope_lookback]

    if abs(slope) < slope_threshold:
        return RANGE

    return direction
