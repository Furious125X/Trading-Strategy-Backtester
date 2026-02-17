class BacktestContext:
    def __init__(self):
        # Core data
        self.candles = None

        # Indicators
        self.ema_fast = None
        self.ema_slow = None
        self.rsi = None
        self.atr = None

        # Structure
        self.levels = None
        self.momentum = None

        # Higher timeframe
        self.htf_candles = None
        self.htf_ema_fast = None
        self.htf_ema_slow = None

        # State (updated per candle)
        self.regime = None
        self.htf_bias = None
