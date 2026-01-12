from models import Trade, Direction


class SimpleBreakoutStrategy:
    def __init__(self, stop_pct=0.01, take_pct=0.04):
        self.stop_pct = stop_pct
        self.take_pct = take_pct

    def generate_trade(self, candles, index):
        if index < 20:
            return None

        prev = candles[index - 1]
        curr = candles[index]

        # Simple momentum rule
        if curr.close > prev.high:
            entry = curr.close
            return Trade(
                direction=Direction.LONG,
                entry_price=entry,
                stop_loss=entry * (1 - self.stop_pct),
                take_profit=entry * (1 + self.take_pct),
                entry_time=curr.close_time,
            )

        return None
