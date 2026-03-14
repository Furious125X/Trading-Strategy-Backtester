from models import Trade, Direction
from strategies.strategy_base import Strategy


class ema_pullback_test(Strategy):

    def __init__(
        self,
        context,
        risk_reward=2.0,
        rsi_threshold=50,
        pullback_lookback=5
    ):
        super().__init__(context)

        self.risk_reward = risk_reward
        self.rsi_threshold = rsi_threshold
        self.pullback_lookback = pullback_lookback

    def precompute(self):
        pass

    def should_enter(self, index):

        ctx = self.context
        candles = ctx.candles

        if index <= self.pullback_lookback:
            return False

        if index >= len(candles):
            return False

        try:
            ema_fast = ctx.ema_fast[index]
            ema_slow = ctx.ema_slow[index]
            rsi_value = ctx.rsi[index]
        except Exception:
            return False

        if ema_fast is None or ema_slow is None or rsi_value is None:
            return False

        curr = candles[index]

        # Trend condition
        if ema_fast <= ema_slow:
            return False

        # Pullback condition
        if curr.close >= ema_fast:
            return False

        # RSI filter
        if rsi_value <= self.rsi_threshold:
            return False

        return True

    def build_trade(self, index):

        ctx = self.context
        candles = ctx.candles

        if index >= len(candles):
            return None

        curr = candles[index]

        entry = curr.close

        # stop at recent swing low
        lookback = self.pullback_lookback
        swing_low = min(c.low for c in candles[index-lookback:index])

        stop_loss = swing_low

        risk = entry - stop_loss

        if risk <= 0:
            return None

        take_profit = entry + risk * self.risk_reward

        trade = Trade(
            direction=Direction.LONG,
            entry_price=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            entry_time=curr.close_time,
            entry_index=index
        )

        ema_value = ctx.ema_fast[index]

        trade.tags = {
            "type": "ema_pullback_test",
            "rsi": ctx.rsi[index],
            "ema_distance": (curr.close - ema_value) / ema_value if ema_value else 0.0
        }

        return trade