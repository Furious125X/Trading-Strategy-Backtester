from models import Direction

def simulate_trade(trade, candles):
    for candle in candles:
        if trade.direction == Direction.LONG:
            if candle.low <= trade.stop_loss:
                trade.exit_time = candle.close_time
                trade.exit_price = trade.stop_loss
                trade.result = "loss"
                return trade

            if candle.high >= trade.take_profit:
                trade.exit_time = candle.close_time
                trade.exit_price = trade.take_profit
                trade.result = "win"
                return trade

        else:  # SHORT
            if candle.high >= trade.stop_loss:
                trade.exit_time = candle.close_time
                trade.exit_price = trade.stop_loss
                trade.result = "loss"
                return trade

            if candle.low <= trade.take_profit:
                trade.exit_time = candle.close_time
                trade.exit_price = trade.take_profit
                trade.result = "win"
                return trade

    trade.result = "open"
    return trade
