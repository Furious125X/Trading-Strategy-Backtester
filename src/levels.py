from collections import defaultdict


class Levels:
    def __init__(
        self,
        candles,
        lookback=3,
        merge_distance=0.002,  # 0.2%
    ):
        """
        candles: list[Candle]
        lookback: swing detection window
        merge_distance: how close levels must be to merge (percentage)
        """

        self.candles = candles
        self.lookback = lookback
        self.merge_distance = merge_distance

        self.raw_levels = []
        self.levels = []

        self._detect_swings()
        self._merge_levels()

    # -----------------------------
    # Swing detection
    # -----------------------------
    def _detect_swings(self):
        for i in range(self.lookback, len(self.candles) - self.lookback):
            candle = self.candles[i]

            highs = [c.high for c in self.candles[i - self.lookback : i + self.lookback + 1]]
            lows = [c.low for c in self.candles[i - self.lookback : i + self.lookback + 1]]

            if candle.high == max(highs):
                self.raw_levels.append(candle.high)

            if candle.low == min(lows):
                self.raw_levels.append(candle.low)

    # -----------------------------
    # Merge nearby levels
    # -----------------------------
    def _merge_levels(self):
        if not self.raw_levels:
            return

        self.raw_levels.sort()
        merged = [self.raw_levels[0]]

        for level in self.raw_levels[1:]:
            last = merged[-1]
            if abs(level - last) / last <= self.merge_distance:
                merged[-1] = (level + last) / 2
            else:
                merged.append(level)

        self.levels = merged

    # -----------------------------
    # Query helpers (USED BY STRATEGIES)
    # -----------------------------
    def nearest_level(self, price):
        if not self.levels:
            return None
        return min(self.levels, key=lambda l: abs(l - price))

    def is_near_level(self, price, tolerance=0.002):
        """
        tolerance: percentage distance
        """
        level = self.nearest_level(price)
        if level is None:
            return False
        return abs(price - level) / level <= tolerance

    def broke_above(self, prev_close, close):
        """
        Returns the level broken, or None
        """
        for level in self.levels:
            if prev_close <= level and close > level:
                return level
        return None

    def broke_below(self, prev_close, close):
        for level in self.levels:
            if prev_close >= level and close < level:
                return level
        return None

    def retest_holding(self, level, low, close, tolerance=0.002):
        """
        Price dipped into level and closed back above
        """
        if abs(low - level) / level <= tolerance and close > level:
            return True
        return False
