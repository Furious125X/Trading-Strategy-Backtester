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

        # state
        self.break_confirm_index = None
        self.active_break_level = None

    def precompute(self):
        # indicators are computed in context (no-op)
        pass

    def should_enter(self, index):
        # basic guards
        if index <= 0:
            return False

        ctx = self.context

        # indicators must exist
        try:
            ema_fast = ctx.ema_fast[index]
            rsi_value = ctx.rsi[index]
            atr_value = ctx.atr[index]
        except Exception:
            return False

        if ema_fast is None or rsi_value is None or atr_value is None:
            return False

        candles = ctx.candles
        if index >= len(candles):
            return False

        curr = candles[index]
        prev = candles[index - 1]

        # HTF EMA confluence (safe compute)
        if not ctx.htf_candles or not getattr(ctx, "htf_ema_fast", None):
            return False

        htf_factor = max(1, len(ctx.candles) // len(ctx.htf_candles))
        htf_index = index // htf_factor
        if htf_index >= len(ctx.htf_ema_fast):
            return False

        htf_ema_fast = ctx.htf_ema_fast[htf_index]
        htf_ema_slow = ctx.htf_ema_slow[htf_index]

        # require HTF bullish
        if not (htf_ema_fast is not None and htf_ema_slow is not None and htf_ema_fast > htf_ema_slow):
            return False

        # price above HTF ema
        if curr.close < htf_ema_fast:
            return False

        # levels object
        levels = ctx.levels
        if not levels:
            return False

        # 1) detect new breakout (first close above level)
        broken_level = levels.broke_above(prev.close, curr.close)
        if broken_level:
            # start confirmation process
            self.active_break_level = broken_level
            self.break_confirm_index = index
            return False

        # 2) two-close confirmation: check the candle immediately after breakout
        if self.break_confirm_index is not None:
            if index == self.break_confirm_index + 1:
                # second close must remain above level
                if curr.close > (self.active_break_level or 0):
                    # confirmed breakout — keep active_break_level and wait for retest
                    # clear break_confirm_index to avoid re-checking
                    self.break_confirm_index = None
                else:
                    # failed confirmation — reset
                    self.active_break_level = None
                    self.break_confirm_index = None
                    return False

        # 3) retest logic: require price touches level + strong rejection
        if self.active_break_level is not None:
            level = self.active_break_level

            # ATR shield
            atr_value = ctx.atr[index]
            tolerance = atr_value * 0.2

            # condition 1: touched level (allow small buffer)
            touched_level = curr.low <= level + tolerance

            # condition 2: must close above level
            closed_above = curr.close > level

            # condition 3: avoid deep breakdown beyond safe ATR
            no_deep_break = curr.low > level - (atr_value * 0.5)

            # momentum/expansion candle checks
            body = abs(curr.close - curr.open)
            full_range = (curr.high - curr.low) if (curr.high - curr.low) != 0 else 1e-9
            prev_range = (prev.high - prev.low) if (prev.high - prev.low) != 0 else 1e-9

            # stronger composition checks
            strong_body = body > (full_range * 0.65)
            close_near_high = (curr.high - curr.close) < (full_range * 0.25)
            range_expansion = full_range > prev_range
            atr_expansion = full_range > (atr_value * 0.8)

            momentum_candle = (
                strong_body
                and close_near_high
                and range_expansion
                and atr_expansion
            )

            if touched_level and closed_above and momentum_candle and no_deep_break:
                # EMA (LTF) alignment check
                ema_fast = ctx.ema_fast[index]
                ema_slow = ctx.ema_slow[index]
                if not (ema_fast is not None and ema_slow is not None and ema_fast > ema_slow):
                    # LTF trend not aligned
                    return False

                # RSI confirmation optional (we require >50 here)
                if not (rsi_value > 50):
                    return False

                # momentum detector (one candle confirmation)
                if not ctx.momentum.is_bullish_momentum(index):
                    return False

                # all checks passed — entry allowed
                return True

            # if price closed below level, invalidate state
            if curr.close < level:
                self.active_break_level = None
                self.break_confirm_index = None

        return False

    def build_trade(self, index):
        ctx = self.context
        candles = ctx.candles
        if index >= len(candles):
            return None

        curr = candles[index]

        entry = curr.close
        stop_loss = self.active_break_level
        if stop_loss is None:
            return None

        risk = entry - stop_loss
        if risk <= 0:
            # invalid or negative risk
            self.active_break_level = None
            return None

        take_profit = entry + risk * self.risk_reward

        # reset internal state
        self.active_break_level = None
        self.break_confirm_index = None

        trade = Trade(
            direction=Direction.LONG,
            entry_price=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            entry_time=curr.close_time,
            entry_index=index,
        )

        # tags for analysis
        ema_value = ctx.ema_fast[index]
        trade.tags = {
            "type": "breakout_retest",
            "rsi": ctx.rsi[index],
            "ema_distance": (curr.close - ema_value) / ema_value if ema_value else 0.0,
        }

        return trade