from models import Trade, Direction
from strategies.strategy_base import Strategy


class EMARSIATRStrategy(Strategy):
    def __init__(
        self,
        context,
        ema_period=50,
        rsi_period=14,
        atr_period=14,
        atr_multiplier=1.5,
        risk_reward=2.0,
    ):
        super().__init__(context)

        self.ema_period = ema_period
        self.rsi_period = rsi_period
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.risk_reward = risk_reward

        # Track breakout state
        self.active_break_level = None

    def precompute(self):
        # Indicators already computed in context
        pass

    def generate_trade(self, index):
        if index == 0:
            return None

        # Ensure indicators exist
        if (
            self.context.ema_fast[index] is None
            or self.context.rsi[index] is None
            or self.context.atr[index] is None
        ):
            return None

        curr = self.context.candles[index]
        prev = self.context.candles[index - 1]

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
                curr.close,
            ):

                # -----------------------------------
                # 3️⃣ Confirm structure + momentum
                # -----------------------------------

                ema_value = self.context.ema_fast[index]
                rsi_value = self.context.rsi[index]

                if (
                    curr.close > ema_value
                    and rsi_value > 50
                    and self.context.momentum.is_bullish_momentum(index)
                ):

                    entry = curr.close
                    stop_loss = self.active_break_level
                    risk = entry - stop_loss

                    if risk <= 0:
                        self.active_break_level = None
                        return None

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

                    # ---- TAGGING ----
                    trade.tags = {
                        "type": "breakout_retest",
                        "rsi": rsi_value,
                        "ema_distance": (curr.close - ema_value) / ema_value,
                    }

                    return trade

            # Invalidate if price closes below level
            if curr.close < self.active_break_level:
                self.active_break_level = None

        return None
