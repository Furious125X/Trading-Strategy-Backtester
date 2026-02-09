class MomentumDetector:
    def __init__(
        self,
        candles,
        body_ratio_threshold=0.6,
        expansion_multiplier=1.3,
    ):
        """
        candles: list[Candle]
        body_ratio_threshold: how much of candle range must be body
        expansion_multiplier: range vs previous candle
        """
        self.candles = candles
        self.body_ratio_threshold = body_ratio_threshold
        self.expansion_multiplier = expansion_multiplier

    def is_bullish_momentum(self, i):
        if i == 0:
            return False

        curr = self.candles[i]
        prev = self.candles[i - 1]

        body = abs(curr.close - curr.open)
        range_ = curr.high - curr.low
        prev_range = prev.high - prev.low

        if range_ == 0:
            return False

        body_ratio = body / range_

        # Conditions
        strong_body = body_ratio >= self.body_ratio_threshold
        range_expansion = range_ >= prev_range * self.expansion_multiplier
        bullish_close = curr.close > curr.open

        return strong_body and range_expansion and bullish_close

    def is_bearish_momentum(self, i):
        if i == 0:
            return False

        curr = self.candles[i]
        prev = self.candles[i - 1]

        body = abs(curr.close - curr.open)
        range_ = curr.high - curr.low
        prev_range = prev.high - prev.low

        if range_ == 0:
            return False

        body_ratio = body / range_

        strong_body = body_ratio >= self.body_ratio_threshold
        range_expansion = range_ >= prev_range * self.expansion_multiplier
        bearish_close = curr.close < curr.open

        return strong_body and range_expansion and bearish_close
