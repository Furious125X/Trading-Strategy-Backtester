import csv
import os

from equity import build_equity_curve


def compute_strategy_stats(trades, risk_cfg):

    if not trades:
        return {
            "trades": 0,
            "win_rate": 0,
            "expectancy": 0,
            "profit": 0,
            "max_dd": 0
        }

    wins = [t for t in trades if getattr(t, "r_multiple", 0) > 0]
    losses = [t for t in trades if getattr(t, "r_multiple", 0) <= 0]

    win_rate = len(wins) / len(trades)

    r_values = [getattr(t, "r_multiple", 0) for t in trades]
    expectancy = sum(r_values) / len(r_values)

    equity, drawdowns = build_equity_curve(
        trades,
        starting_balance=risk_cfg["starting_balance"],
        risk_per_trade=risk_cfg["risk_per_trade"],
    )

    profit = equity[-1] - risk_cfg["starting_balance"] if equity else 0
    max_dd = max(drawdowns) * 100 if drawdowns else 0

    return {
        "trades": len(trades),
        "win_rate": round(win_rate * 100, 2),
        "expectancy": round(expectancy, 3),
        "profit": round(profit, 2),
        "max_dd": round(max_dd, 2)
    }


def compare_strategies(strategy_trades, risk_cfg):

    results = {}

    for name, trades in strategy_trades.items():

        stats = compute_strategy_stats(trades, risk_cfg)

        results[name] = stats

    return results


def print_strategy_comparison(results):

    print("\nStrategy Comparison")
    print("-" * 60)

    header = f"{'Strategy':20} {'Trades':7} {'Win%':7} {'Expectancy':10} {'Profit':10} {'MaxDD':8}"
    print(header)

    for name, stats in results.items():

        row = f"{name:20} {stats['trades']:7} {stats['win_rate']:7} {stats['expectancy']:10} {stats['profit']:10} {stats['max_dd']:8}"
        print(row)


def export_strategy_comparison(results):

    os.makedirs("outputs", exist_ok=True)

    filename = "outputs/strategy_comparison.csv"

    rows = []

    for name, stats in results.items():

        row = {"strategy": name}
        row.update(stats)

        rows.append(row)

    if not rows:
        return

    keys = rows[0].keys()

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nStrategy comparison exported → {filename}")