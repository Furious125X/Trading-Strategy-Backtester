from loader import load_candles
from simulator import simulate_trade
from stats import (
    basic_trade_stats,
    pnl_stats,
    r_multiple_stats,
    regime_expectancy,
)
from equity import build_equity_curve
from equity_plot import plot_equity_curve
from timeframe import aggregate_candles
from htf_bias import htf_trend_bias
from indicators import ema
from regime import detect_regime

from strategies.ema_rsi_atr_strategy import EMARSIATRStrategy


def main():
    candles = load_candles("data/ETHUSD_15.csv")

    # ---- PRECOMPUTE LTF INDICATORS ----
    ema_fast = ema(candles, 20)
    ema_slow = ema(candles, 50)

    # ---- HTF ----
    HTF_FACTOR = 4
    htf_candles = aggregate_candles(candles, HTF_FACTOR)

    htf_ema_fast = ema(htf_candles, 20)
    htf_ema_slow = ema(htf_candles, 50)

    # ---- STRATEGY ----
    strategy = EMARSIATRStrategy(candles)
    strategy.precompute()

    trades = []
    i = 0

    while i < len(candles):

        # ---- REGIME ----
        regime = detect_regime(
            ema_fast,
            ema_slow,
            i
        )

        # ---- HTF INDEX ----
        htf_i = i // HTF_FACTOR
        if htf_i >= len(htf_candles):
            i += 1
            continue

        # ---- HTF BIAS ----
        bias = htf_trend_bias(
            htf_candles,
            htf_ema_fast,
            htf_ema_slow,
            htf_i
        )

        if bias != "bullish":
            i += 1
            continue

        # ---- STRATEGY SIGNAL ----
        trade = strategy.generate_trade(i)

        if trade:
            trade.regime = regime
            trade.htf_bias = bias

            result = simulate_trade(trade, candles[i + 1:])
            trades.append(result)

            if result.exit_index is not None:
                i = result.exit_index + 1
                continue

        i += 1

    # ---- STATS ----
    print(basic_trade_stats(trades))
    print(pnl_stats(trades))
    print(r_multiple_stats(trades))

    print("\nRegime Expectancy:")
    for k, v in regime_expectancy(trades).items():
        print(k, v)

    # ---- EQUITY ----
    equity_curve, drawdowns = build_equity_curve(
        trades,
        starting_balance=10_000,
        risk_per_trade=0.01,
    )

    if equity_curve:
        print(f"Final equity: {equity_curve[-1]:.2f}")
        print(f"Max drawdown: {max(drawdowns) * 100:.2f}%")
        plot_equity_curve(equity_curve, drawdowns)
    else:
        print("No trades taken — equity curve empty.")


if __name__ == "__main__":
    main()
