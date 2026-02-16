from models import Trade, Direction
from indicators import ema, rsi, atr
from strategies.strategy_base import Strategy


class EMARSIATRStrategy(Strategy):
    def __init__(
        self,
        candles,
        context,
        ema_period=50,
        rsi_period=14,
        atr_period=14,
        atr_multiplier=1.5,
        risk_reward=2.0,
    ):
        super().__init__(candles)

        self.context = context

        self.ema_period = ema_period
        self.rsi_period = rsi_period
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.risk_reward = risk_reward

        self.ema = None
        self.rsi = None
        self.atr = None

        # Track breakout state
        self.active_break_level = None

    def precompute(self):
        self.ema = ema(self.candles, self.ema_period)
        self.rsi = rsi(self.candles, self.rsi_period)
        self.atr = atr(self.candles, self.atr_period)

    def generate_trade(self, index):
        if index == 0:
            return None

        if (
            self.ema[index] is None
            or self.rsi[index] is None
            or self.atr[index] is None
        ):
            return None

        curr = self.candles[index]
        prev = self.candles[index - 1]

        levels = self.context.levels

        # -----------------------------------
        # 1️⃣ Detect breakout
        # -----------------------------------
        broken_level = levels.broke_above(prev.close, curr.close)

        if broken_level:
            self.active_break_level = broken_level
            return None  # wait for retest

        # -----------------------------------
        # 2️⃣ Wait for retest holding
        # -----------------------------------
        if self.active_break_level:

            if levels.retest_holding(
                self.active_break_level,
                curr.low,
                curr.close
            ):
                # -----------------------------------
                # 3️⃣ Confirm structure + momentum
                # -----------------------------------

                if (
                    curr.close > self.ema[index]
                    and self.rsi[index] > 50
                    and self.context.momentum.is_bullish_momentum(index)
                ):
                    entry = curr.close
                    stop_loss = self.active_break_level
                    risk = entry - stop_loss
                    take_profit = entry + risk * self.risk_reward

                    self.active_break_level = None  # reset

                    trade = Trade(
                        direction=Direction.LONG,
                        entry_price=entry,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        entry_time=curr.close_time,
                        entry_index=index,
                    )

                    # ---- TAGGING ----S
                    trade.tags = {
                        "type": "breakout_retest",
                        "rsi": self.rsi[index],
                        "ema_distance": (curr.close - self.ema[index]) / self.ema[index],
                    }

                    return trade

            # Invalidate if price dumps below level
            if curr.close < self.active_break_level:
                self.active_break_level = None

        return None
