from models import Direction


def simulate_trade(trade, candles):
    entry = trade.entry_price
    stop = trade.stop_loss
    tp = trade.take_profit

    partial_taken = False

    if trade.direction == Direction.LONG:
        initial_risk = entry - stop
        partial_target = entry + initial_risk  # 1R

    else:  # SHORT
        initial_risk = stop - entry
        partial_target = entry - initial_risk  # 1R

    for i, candle in enumerate(candles):

        # =========================
        # ===== LONG TRADES =======
        # =========================
        if trade.direction == Direction.LONG:

            # ---- PARTIAL TP (1R) ----
            if (
                not partial_taken
                and candle.high >= partial_target
            ):
                partial_taken = True
                stop = entry  # move to break-even
            
            # ---- STRUCTURAL TRAILING ----
            if partial_taken:
                # trail to previous candle low (structure)
                prev_index = i - 1
                if prev_index >= 0:
                    prev_low = candles[prev_index].low
                    if prev_low > stop:
                        stop = prev_low

            # ---- STOP LOSS ----
            if candle.low <= stop:
                trade.exit_time = candle.close_time
                trade.exit_price = stop
                trade.exit_index = trade.entry_index + i + 1

                if partial_taken:
                    # locked 1R on half, BE on rest
                    trade.r_multiple = 0.5 * 1
                    trade.result = "partial_win"
                else:
                    trade.r_multiple = -1
                    trade.result = "loss"

                return trade

            # ---- FINAL TAKE PROFIT ----
            if candle.high >= tp:
                trade.exit_time = candle.close_time
                trade.exit_price = tp
                trade.exit_index = trade.entry_index + i + 1
                trade.result = "win"

                if partial_taken:
                    full_r = (tp - entry) / initial_risk
                    trade.r_multiple = 0.5 * 1 + 0.5 * full_r
                else:
                    trade.r_multiple = (tp - entry) / initial_risk

                return trade

        # =========================
        # ===== SHORT TRADES ======
        # =========================
        else:

            # ---- PARTIAL TP (1R) ----
            if (
                not partial_taken
                and candle.low <= partial_target
            ):
                partial_taken = True
                stop = entry  # move to break-even
            
            # ---- STRUCTURAL TRAILING ----
            if partial_taken:
                prev_index = i - 1
                if prev_index >= 0:
                    prev_high = candles[prev_index].high
                    if prev_high < stop:
                        stop = prev_high

            # ---- STOP LOSS ----
            if candle.high >= stop:
                trade.exit_time = candle.close_time
                trade.exit_price = stop
                trade.exit_index = trade.entry_index + i + 1

                if partial_taken:
                    trade.r_multiple = 0.5 * 1
                    trade.result = "partial_win"
                else:
                    trade.r_multiple = -1
                    trade.result = "loss"

                return trade

            # ---- FINAL TAKE PROFIT ----
            if candle.low <= tp:
                trade.exit_time = candle.close_time
                trade.exit_price = tp
                trade.exit_index = trade.entry_index + i + 1
                trade.result = "win"

                if partial_taken:
                    full_r = (entry - tp) / initial_risk
                    trade.r_multiple = 0.5 * 1 + 0.5 * full_r
                else:
                    trade.r_multiple = (entry - tp) / initial_risk

                return trade

    # Trade still open
    trade.result = "open"
    return trade