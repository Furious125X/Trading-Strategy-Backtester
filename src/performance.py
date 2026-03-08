from stats import (
    basic_trade_stats,
    pnl_stats,
    r_multiple_stats,
    regime_expectancy,
    tag_expectancy
)


def compute_performance(trades, equity_curve=None, drawdowns=None):

    report = {}

    report["basic"] = basic_trade_stats(trades)
    report["pnl"] = pnl_stats(trades)
    report["r_multiple"] = r_multiple_stats(trades)

    report["regime_expectancy"] = regime_expectancy(trades)
    report["type_expectancy"] = tag_expectancy(trades, "type")

    if equity_curve:
        report["final_equity"] = equity_curve[-1]

    if drawdowns:
        report["max_drawdown"] = max(drawdowns)

    return report