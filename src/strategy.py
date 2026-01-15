from models import Trade, Direction
from indicators import ema, rsi, atr


class EMARSIATRStrategy:
    def __init__(
        self,
        ema_period=50,
        rsi_period=14,
        atr_period=14,
        atr_multiplier=1.5,
        risk_reward=2.0,
    ):
        self.ema_period = ema_period
        self.rsi_period = rsi_period
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.risk_reward = risk_reward

    def generate_trade(self, candles, index):
        # Pre-calculate indicators once
        ema_values = ema(candles, self.ema_period)
        rsi_values = rsi(candles, self.rsi_period)
        atr_values = atr(candles, self.atr_period)

        # Safety checks
        if (
            ema_values[index] is None
            or rsi_values[index] is None
            or atr_values[index] is None
        ):
            return None

        curr = candles[index]

        # LONG conditions
        if (
            curr.close > ema_values[index]
            and rsi_values[index] > 50
        ):
            entry = curr.close
            stop_loss = entry - atr_values[index] * self.atr_multiplier
            risk = entry - stop_loss
            take_profit = entry + risk * self.risk_reward

            return Trade(
                direction=Direction.LONG,
                entry_price=entry,
                stop_loss=stop_loss,
                take_profit=take_profit,
                entry_time=curr.close_time,
            )

        return None
