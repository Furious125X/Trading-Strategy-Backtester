from models import Direction
from collections import defaultdict


# -----------------------------
# BASIC STATS (unchanged)
# -----------------------------

def basic_trade_stats(trades):
    completed = [t for t in trades if t.result in ("win", "loss")]

    total = len(completed)
    wins = sum(1 for t in completed if t.result == "win")
    losses = sum(1 for t in completed if t.result == "loss")

    win_rate = wins / total if total > 0 else 0
    loss_rate = losses / total if total > 0 else 0

    return {
        "total_trades": total,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "loss_rate": loss_rate,
    }


def trade_pnl(trade):
    if trade.result not in ("win", "loss"):
        return None, None

    if trade.direction == Direction.LONG:
        pnl = trade.exit_price - trade.entry_price
    else:  # SHORT
        pnl = trade.entry_price - trade.exit_price

    return_pct = pnl / trade.entry_price
    return pnl, return_pct


def pnl_stats(trades):
    wins = []
    losses = []
    returns = []

    for trade in trades:
        pnl, ret = trade_pnl(trade)
        if pnl is None:
            continue

        returns.append(ret)

        if pnl > 0:
            wins.append(pnl)
        else:
            losses.append(abs(pnl))

    total_trades = len(wins) + len(losses)

    total_pnl = sum(wins) - sum(losses)
    avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
    avg_return = sum(returns) / len(returns) if returns else 0

    avg_win = sum(wins) / len(wins) if wins else 0
    avg_loss = sum(losses) / len(losses) if losses else 0

    win_rate = len(wins) / total_trades if total_trades > 0 else 0
    loss_rate = len(losses) / total_trades if total_trades > 0 else 0

    expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)

    profit_factor = (
        sum(wins) / sum(losses)
        if losses and sum(losses) > 0
        else float("inf")
    )

    risk_reward = avg_win / avg_loss if avg_loss > 0 else float("inf")

    return {
        "total_pnl": total_pnl,
        "average_pnl": avg_pnl,
        "average_return": avg_return,
        "average_win": avg_win,
        "average_loss": avg_loss,
        "expectancy": expectancy,
        "profit_factor": profit_factor,
        "risk_reward": risk_reward,
    }


def r_multiple_stats(trades):
    rs = [t.r_multiple for t in trades if t.r_multiple is not None]

    if not rs:
        return {}

    return {
        "total_R": sum(rs),
        "average_R": sum(rs) / len(rs),
        "max_R": max(rs),
        "min_R": min(rs),
    }


# -----------------------------
# REGIME ANALYSIS (FIXED)
# -----------------------------

def group_trades_by_regime(trades):
    groups = defaultdict(list)
    for t in trades:
        if t.regime is not None and t.r_multiple is not None:
            groups[t.regime].append(t)
    return groups


def regime_expectancy(trades):
    grouped = group_trades_by_regime(trades)
    results = {}

    for regime, regime_trades in grouped.items():
        total_r = sum(t.r_multiple for t in regime_trades)
        avg_r = total_r / len(regime_trades) if regime_trades else 0

        results[regime] = {
            "trades": len(regime_trades),
            "total_R": total_r,
            "expectancy_R": avg_r,
        }

    return results

def tag_expectancy(trades, tag_key):
    results = {}

    for t in trades:
        if not hasattr(t, "tags"):
            continue

        if tag_key not in t.tags:
            continue

        key = t.tags[tag_key]

        if key not in results:
            results[key] = []

        results[key].append(t.r_multiple)

    expectancy = {}
    for k, values in results.items():
        if values:
            expectancy[k] = sum(values) / len(values)

    return expectancy


import random


def monte_carlo_simulation(trades, runs=1000):
    r_values = [t.r_multiple for t in trades if t.r_multiple is not None]

    if not r_values:
        return None

    results = []

    for _ in range(runs):
        shuffled = random.sample(r_values, len(r_values))

        equity = 0
        peak = 0
        max_dd = 0

        for r in shuffled:
            equity += r
            peak = max(peak, equity)
            dd = peak - equity
            max_dd = max(max_dd, dd)

        results.append({
            "final_r": equity,
            "max_dd_r": max_dd
        })

    return results


def summarize_monte_carlo(results):
    if not results:
        return None

    finals = [r["final_r"] for r in results]
    drawdowns = [r["max_dd_r"] for r in results]

    finals.sort()
    drawdowns.sort()

    return {
        "median_final_r": finals[len(finals)//2],
        "worst_5pct_final_r": finals[int(len(finals)*0.05)],
        "median_max_dd_r": drawdowns[len(drawdowns)//2],
        "worst_5pct_dd_r": drawdowns[int(len(drawdowns)*0.95)],
    }
