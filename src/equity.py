def build_equity_curve(
    trades,
    starting_balance=10_000,
    risk_per_trade=0.01,
):
    """
    Builds equity curve using R-multiples

    Returns:
        equity_curve: list[float]
        drawdowns: list[float]
    """

    equity = starting_balance
    peak = starting_balance

    equity_curve = []
    drawdowns = []

    for trade in trades:
        if trade.r_multiple is None:
            continue

        # Position sizing via R
        pct_change = trade.r_multiple * risk_per_trade
        equity *= (1 + pct_change)

        equity_curve.append(equity)

        # Drawdown calculation
        if equity > peak:
            peak = equity

        drawdown = (peak - equity) / peak
        drawdowns.append(drawdown)

    return equity_curve, drawdowns
