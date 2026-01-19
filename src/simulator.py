from models import Direction


def simulate_trade(trade, candles):
    """
    Simulates a single trade forward in time.
    candles MUST be candles AFTER entry_index.
    """

    for i, candle in enumerate(candles):
        # LONG trades
        if trade.direction == Direction.LONG:
            # Stop loss hit first
            if candle.low <= trade.stop_loss:
                trade.exit_time = candle.close_time
                trade.exit_price = trade.stop_loss
                trade.exit_index = trade.entry_index + i + 1
                trade.result = "loss"
                return trade

            # Take profit hit
            if candle.high >= trade.take_profit:
                trade.exit_time = candle.close_time
                trade.exit_price = trade.take_profit
                trade.exit_index = trade.entry_index + i + 1
                trade.result = "win"
                return trade

        # SHORT trades
        else:
            if candle.high >= trade.stop_loss:
                trade.exit_time = candle.close_time
                trade.exit_price = trade.stop_loss
                trade.exit_index = trade.entry_index + i + 1
                trade.result = "loss"
                return trade

            if candle.low <= trade.take_profit:
                trade.exit_time = candle.close_time
                trade.exit_price = trade.take_profit
                trade.exit_index = trade.entry_index + i + 1
                trade.result = "win"
                return trade

        # 🔒 HARD SAFETY CAP (prevents infinite runtime)
        if i > 500:  # trade expires after 500 candles (~5 days on 15m)
            trade.exit_time = candle.close_time
            trade.exit_price = candle.close
            trade.exit_index = trade.entry_index + i + 1
            trade.result = "timeout"
            return trade

    # If data ends before TP/SL
    trade.result = "open"
    return trade
