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
from regime import detect_regime
from levels import Levels
from stats import tag_expectancy

from strategies.registry import get_strategy
from strategies.config import CONFIG

from context import BacktestContext
from momentum import MomentumDetector

from stats import monte_carlo_simulation, summarize_monte_carlo

from indicators import ema, rsi, atr

from visualizer import save_trade_chart
import matplotlib.pyplot as plt
import os

from performance import compute_performance

from trade_analytics import analyze_trades, summarize_trade_analytics

from analytic_plots import plot_mfe_mae, plot_duration, plot_r_distribution

from optimizer import parameter_sweep, rank_results

from walk_forward import walk_forward_test
from exporter import export_summary, export_optimizer_results, export_walkforward

import os
os.makedirs("analytic_outputs", exist_ok=True)
from portfolio import run_portfolio


def main():
    # ---- LOAD CONFIG ----
    data_cfg = CONFIG["data"]
    strat_cfg = CONFIG["strategy"]
    risk_cfg = CONFIG["risk"]

    # ---- LOAD DATA ----
    candles = load_candles(data_cfg["path"])

    #-----SET PARAMETTERS FOR OPTIMIZATION----
    param_grid = {
    "risk_reward": [1.5, 2.0, 2.5, 3.0],
    "rsi_threshold": [45, 50, 55],
    }
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


   # ---- PORTFOLIO STRATEGIES ----
    portfolio_strategies = {
        "breakout_retest": {
            "risk_reward": 2.0,
            "rsi_threshold": 50
        }
    }

    print("\nRunning Portfolio Strategies...")

    portfolio_trades, strategy_trades = run_portfolio(
        candles,
        context,
        portfolio_strategies
    )

    trades = portfolio_trades

    # optional strategy breakdown
    for name, t in strategy_trades.items():
        print(f"{name} trades:", len(t))

    # ---- EQUITY ----
    equity_curve, drawdowns = build_equity_curve(
        trades,
        starting_balance=risk_cfg["starting_balance"],
        risk_per_trade=risk_cfg["risk_per_trade"],
    )

    performance = compute_performance(trades, equity_curve, drawdowns)

    print("\nPerformance Summary")
    for section, data in performance.items():
        print(section, data)

    if equity_curve:
        print(f"Final equity: {equity_curve[-1]:.2f}")
        print(f"Max drawdown: {max(drawdowns) * 100:.2f}%")
        plot_equity_curve(equity_curve, drawdowns)
    else:
        print("No trades taken — equity curve empty.")

    print("\nExpectancy by Trade Type:")
    print(tag_expectancy(trades, "type"))

    analytics = analyze_trades(trades, candles)
    summary = summarize_trade_analytics(analytics)

    print("\nTrade Analytics:")
    print(summary)
    export_summary(summary)

    plot_mfe_mae(analytics)
    plot_duration(analytics)
    plot_r_distribution(analytics)

    print("\nRunning Monte Carlo...")

    mc_results = monte_carlo_simulation(trades, runs=1000)
    mc_summary = summarize_monte_carlo(mc_results)

    if mc_summary:
        print("\nMonte Carlo Summary:")
        for k, v in mc_summary.items():
            print(k, round(v, 2))

    # choose a trade to inspect
    for i, t in enumerate(trades):
        save_trade_chart(t, candles, f"outputs/trade_{i}_entry{t.entry_index}.png", context=context, window=60)

    
    print("\nRunning Parameter Sweep...")

    results = parameter_sweep(
        candles,
        context,
        strat_cfg["name"],
        param_grid
    )

    top = rank_results(results)
    export_optimizer_results(results)

    print("\nTop Strategy Variants:")

    for r in top:
        print(r)

    print("\nRunning Walk-Forward Test...")

    wf_results = walk_forward_test(
        candles,
        context,
        strat_cfg["name"],
        param_grid,
        train_size=5000,
        test_size=1000
    )

    print("\nWalk-Forward Results:")

    for r in wf_results:
        print(r)

    export_walkforward(wf_results)


if __name__ == "__main__":
    main()
