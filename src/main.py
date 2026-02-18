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
from levels import Levels
from stats import tag_expectancy

from strategies.registry import get_strategy
from strategies.config import CONFIG

from context import BacktestContext
from momentum import MomentumDetector

from stats import monte_carlo_simulation, summarize_monte_carlo

from indicators import ema, rsi, atr

def main():
    # ---- LOAD CONFIG ----
    data_cfg = CONFIG["data"]
    strat_cfg = CONFIG["strategy"]
    risk_cfg = CONFIG["risk"]

    # ---- LOAD DATA ----
    candles = load_candles(data_cfg["path"])

    # ---- CONTEXT ----
    context = BacktestContext()
    context.momentum = MomentumDetector(candles)
    context.levels = Levels(candles)


    # ---- LTF INDICATORS ----
    context.candles = candles

    context.ema_fast = ema(candles, 20)
    context.ema_slow = ema(candles, 50)
    context.rsi = rsi(candles, 14)
    context.atr = atr(candles, 14)


    # ---- HTF ----
    HTF_FACTOR = data_cfg["htf_factor"]
    context.htf_candles = aggregate_candles(candles, HTF_FACTOR)
    context.htf_ema_fast = ema(context.htf_candles, 20)
    context.htf_ema_slow = ema(context.htf_candles, 50)


    # ---- STRATEGY ----
    StrategyClass = get_strategy(strat_cfg["name"])
    strategy = StrategyClass(context, **strat_cfg["params"])

    trades = []
    i = 0

    # ---- ENGINE ----
    while i < len(candles):

        context.regime = detect_regime(
            context.ema_fast,
            context.ema_slow,
            i
        )

        htf_i = i // HTF_FACTOR
        if htf_i >= len(context.htf_candles):
            i += 1
            continue

        context.htf_bias = htf_trend_bias(
            context.htf_candles,
            context.htf_ema_fast,
            context.htf_ema_slow,
            htf_i
        )

        if context.htf_bias != "bullish":
            i += 1
            continue


        trade = None

        if strategy.should_enter(i):
            trade = strategy.build_trade(i)

        if trade:
            trade.regime = context.regime
            trade.htf_bias = context.htf_bias

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
        starting_balance=risk_cfg["starting_balance"],
        risk_per_trade=risk_cfg["risk_per_trade"],
    )

    if equity_curve:
        print(f"Final equity: {equity_curve[-1]:.2f}")
        print(f"Max drawdown: {max(drawdowns) * 100:.2f}%")
        plot_equity_curve(equity_curve, drawdowns)
    else:
        print("No trades taken — equity curve empty.")

    print("\nExpectancy by Trade Type:")
    print(tag_expectancy(trades, "type"))


    print("\nRunning Monte Carlo...")

    mc_results = monte_carlo_simulation(trades, runs=1000)
    mc_summary = summarize_monte_carlo(mc_results)

    if mc_summary:
        print("\nMonte Carlo Summary:")
        for k, v in mc_summary.items():
            print(k, round(v, 2))



if __name__ == "__main__":
    main()
