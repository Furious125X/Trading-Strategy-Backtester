from models import Trade, Direction
from indicators import ema, rsi, atr


class EMARSIATRStrategy:
    def __init__(
        self,
        candles,
        ema_period=50,
        rsi_period=14,
        atr_period=14,
        atr_multiplier=1.5,
        risk_reward=2.0,
    ):
        self.candles = candles
        self.ema = ema(candles, ema_period)
        self.rsi = rsi(candles, rsi_period)
        self.atr = atr(candles, atr_period)

        self.atr_multiplier = atr_multiplier
        self.risk_reward = risk_reward

    def generate_trade(self, index):
        # Safety checks
        if (
            self.ema[index] is None
            or self.rsi[index] is None
            or self.atr[index] is None
        ):
            return None

        curr = self.candles[index]

        # LONG conditions
        if curr.close > self.ema[index] and self.rsi[index] > 50:
            entry = curr.close
            stop_loss = entry - self.atr[index] * self.atr_multiplier
            risk = entry - stop_loss
            take_profit = entry + risk * self.risk_reward

            return Trade(
                direction=Direction.LONG,
                entry_price=entry,
                stop_loss=stop_loss,
                take_profit=take_profit,
                entry_time=curr.close_time,
                entry_index=index,
            )

        return None
