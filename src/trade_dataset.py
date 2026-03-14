import csv
import os


def build_trade_dataset(trades, candles, context, filename="outputs/trade_dataset.csv"):

    os.makedirs("outputs", exist_ok=True)

    rows = []

    for trade in trades:

        entry_i = trade.entry_index
        exit_i = trade.exit_index if trade.exit_index is not None else entry_i

        entry_candle = candles[entry_i]
        exit_candle = candles[exit_i]

        duration = exit_i - entry_i

        r_multiple = getattr(trade, "r_multiple", None)

        row = {
            "entry_time": entry_candle.close_time,
            "exit_time": exit_candle.close_time,
            "direction": trade.direction.name,
            "entry_price": trade.entry_price,
            "stop_loss": trade.stop_loss,
            "take_profit": trade.take_profit,
            "exit_price": trade.exit_price,
            "duration_candles": duration,
            "R": r_multiple,
            "strategy": trade.tags.get("type") if trade.tags else None
        }

        # Indicators if available
        if hasattr(context, "rsi"):
            row["rsi"] = context.rsi[entry_i]

        if hasattr(context, "ema_fast"):
            ema_val = context.ema_fast[entry_i]
            if ema_val:
                row["ema_distance"] = (trade.entry_price - ema_val) / ema_val

        if hasattr(context, "atr"):
            row["atr"] = context.atr[entry_i]

        # Copy all trade tags
        if trade.tags:
            for k, v in trade.tags.items():
                row[f"tag_{k}"] = v

        rows.append(row)

    if not rows:
        print("No trades to export.")
        return

    keys = rows[0].keys()

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nTrade dataset exported → {filename}")