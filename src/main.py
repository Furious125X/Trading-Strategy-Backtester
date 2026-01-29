from loader import load_candles
from simulator import simulate_trade
from stats import basic_trade_stats, pnl_stats, r_multiple_stats
from strategy import EMARSIATRStrategy
from equity import build_equity_curve
from equity_plot import plot_equity_curve
from timeframe import aggregate_candles
from htf_bias import htf_trend_bias




def main():
    candles = load_candles("data/ETHUSD_15.csv")
    htf_candles = load_candles("data/xrp_1h.csv")
    strategy = EMARSIATRStrategy(candles)
    HTF_FACTOR = 4  # 15m → 1H
    htf_candles = aggregate_candles(candles, HTF_FACTOR)
    htf_closes = [c["close"] for c in htf_candles]
    htf_ema_fast = ema(htf_closes, 20)
    htf_ema_slow = ema(htf_closes, 50)


    htf_i = find_htf_index(htf_candles, i)

    if htf_i is None:
        i += 1
        continue

    bias = htf_trend_bias(
        htf_candles,
        htf_ema_fast,
        htf_ema_slow,
        htf_i
    )

    if bias != "bullish":
        i += 1
        continue

    trades = []
    i = 0
    while i < len(candles):
        trade = strategy.generate_trade(i)

        if trade:
            trade.entry_index = i

            result = simulate_trade(trade, candles[i + 1:])
            trades.append(result)

            if result.exit_index is not None:
                i = result.exit_index + 1
                continue

        i += 1

    print(basic_trade_stats(trades))
    print(pnl_stats(trades))
    print(r_multiple_stats(trades))

    equity_curve, drawdowns = build_equity_curve(
        trades,
        starting_balance=10_000,
        risk_per_trade=0.01,
    )

    print(f"Final equity: {equity_curve[-1]:.2f}")
    print(f"Max drawdown: {max(drawdowns) * 100:.2f}%")


    plot_equity_curve(equity_curve, drawdowns)


if __name__ == "__main__":
    main()
