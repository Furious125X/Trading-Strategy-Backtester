from models import Direction


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
            losses.append(abs(pnl))  # store losses as positive numbers

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

    risk_reward = (
        avg_win / avg_loss
        if avg_loss > 0
        else float("inf")
    )

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
