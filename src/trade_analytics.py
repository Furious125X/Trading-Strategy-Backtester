def compute_mfe_mae(trade, candles):

    entry = trade.entry_price
    stop = trade.stop_loss

    mfe = 0
    mae = 0

    start = trade.entry_index
    end = trade.exit_index if trade.exit_index else len(candles) - 1

    for i in range(start, end + 1):

        c = candles[i]

        favorable = c.high - entry
        adverse = entry - c.low

        if favorable > mfe:
            mfe = favorable

        if adverse > mae:
            mae = adverse

    risk = abs(entry - stop)

    if risk == 0:
        return 0, 0

    mfe_r = mfe / risk
    mae_r = mae / risk

    return mfe_r, mae_r

def trade_duration(trade):

    if trade.exit_index is None:
        return 0

    return trade.exit_index - trade.entry_index

def analyze_trades(trades, candles):

    results = []

    for t in trades:

        mfe, mae = compute_mfe_mae(t, candles)
        duration = trade_duration(t)

        results.append({
            "mfe_r": mfe,
            "mae_r": mae,
            "duration": duration,
            "result_r": t.r_multiple
        })

    return results

def summarize_trade_analytics(analytics):

    if not analytics:
        return {}

    avg_mfe = sum(a["mfe_r"] for a in analytics) / len(analytics)
    avg_mae = sum(a["mae_r"] for a in analytics) / len(analytics)
    avg_duration = sum(a["duration"] for a in analytics) / len(analytics)

    return {
        "avg_mfe_r": round(avg_mfe, 2),
        "avg_mae_r": round(avg_mae, 2),
        "avg_duration_bars": round(avg_duration, 2)
    }
