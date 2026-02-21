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
        self.break_confirm_index = None
        # Track breakout state
        self.active_break_level = None

    def precompute(self):
        # Indicators already computed in context
        pass

    def should_enter(self, index):
        if index == 0:
            return False

        if (
            self.context.ema_fast[index] is None
            or self.context.rsi[index] is None
            or self.context.atr[index] is None
        ):
            return False

        curr = self.context.candles[index]
        prev = self.context.candles[index - 1]
        levels = self.context.levels

        # 1️⃣ Detect breakout
        broken_level = levels.broke_above(prev.close, curr.close)

        if broken_level:
            self.active_break_level = broken_level
            self.break_confirm_index = index
            return False

        # 2️⃣ Confirm second close above level
        if hasattr(self, "break_confirm_index"):

            if index == self.break_confirm_index + 1:

                if curr.close > self.active_break_level:
                    # confirmed breakout
                    pass
                else:
                    # failed confirmation
                    self.active_break_level = None
                    del self.break_confirm_index
                    return False

        # 2️⃣ Retest confirmation
        if self.active_break_level:

            ema_value = self.context.ema_fast[index]
            rsi_value = self.context.rsi[index]
            atr_value = self.context.atr[index]

            level = self.active_break_level

            # ---- Retest Conditions ----

            # 1️⃣ Must dip into level area (allow small ATR buffer)
            tolerance = atr_value * 0.2
            touched_level = curr.low <= level + tolerance

            # 2️⃣ Must NOT close below level
            closed_above = curr.close > level

            # 3️⃣ Strong bullish rejection candle
            body_size = abs(curr.close - curr.open)
            full_range = curr.high - curr.low
            strong_body = body_size > (full_range * 0.6)

            # 4️⃣ Avoid deep breakdown
            no_deep_break = curr.low > level - (atr_value * 0.5)

            if touched_level and closed_above and strong_body and no_deep_break:

                ema_value = self.context.ema_fast[index]
                rsi_value = self.context.rsi[index]

                if (
                    curr.close > ema_value
                    and rsi_value > 50
                    and self.context.momentum.is_bullish_momentum(index)
                ):
                    return True

            # Invalidate if lost level
            if curr.close < self.active_break_level:
                self.active_break_level = None

        return False

    def build_trade(self, index):

        curr = self.context.candles[index]

        entry = curr.close
        stop_loss = self.active_break_level
        risk = entry - stop_loss

        if risk <= 0:
            self.active_break_level = None
            return None

        take_profit = entry + risk * self.risk_reward

        self.active_break_level = None  # reset after building

        trade = Trade(
            direction=Direction.LONG,
            entry_price=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            entry_time=curr.close_time,
            entry_index=index,
        )

        trade.tags = {
            "type": "breakout_retest",
            "rsi": self.context.rsi[index],
            "ema_distance": (
                curr.close - self.context.ema_fast[index]
            ) / self.context.ema_fast[index],
        }

        return trade


        return None
