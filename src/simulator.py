from models import Direction


def simulate_trade(trade, candles):
    for i, candle in enumerate(candles):
        if trade.direction == Direction.LONG:
            # STOP LOSS
            if candle.low <= trade.stop_loss:
                trade.exit_time = candle.close_time
                trade.exit_price = trade.stop_loss
                trade.exit_index = trade.entry_index + i + 1
                trade.result = "loss"

                trade.r_multiple = (
                    (trade.exit_price - trade.entry_price)
                    / (trade.entry_price - trade.stop_loss)
                )

                return trade

            # TAKE PROFIT
            if candle.high >= trade.take_profit:
                trade.exit_time = candle.close_time
                trade.exit_price = trade.take_profit
                trade.exit_index = trade.entry_index + i + 1
                trade.result = "win"

                trade.r_multiple = (
                    (trade.exit_price - trade.entry_price)
                    / (trade.entry_price - trade.stop_loss)
                )

                return trade

        else:  # SHORT
            # STOP LOSS
            if candle.high >= trade.stop_loss:
                trade.exit_time = candle.close_time
                trade.exit_price = trade.stop_loss
                trade.exit_index = trade.entry_index + i + 1
                trade.result = "loss"

                trade.r_multiple = (
                    (trade.entry_price - trade.exit_price)
                    / (trade.stop_loss - trade.entry_price)
                )

                return trade

            # TAKE PROFIT
            if candle.low <= trade.take_profit:
                trade.exit_time = candle.close_time
                trade.exit_price = trade.take_profit
                trade.exit_index = trade.entry_index + i + 1
                trade.result = "win"

                trade.r_multiple = (
                    (trade.entry_price - trade.exit_price)
                    / (trade.stop_loss - trade.entry_price)
                )

                return trade

    # Trade still open
    trade.result = "open"
    return trade
