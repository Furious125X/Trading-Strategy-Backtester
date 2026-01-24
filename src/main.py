from loader import load_candles
from simulator import simulate_trade
from stats import basic_trade_stats, pnl_stats, r_multiple_stats
from strategy import EMARSIATRStrategy
from equity import build_equity_curve
from equity_plot import plot_equity_curve



def main():
    candles = load_candles("data/xrp_15m.csv")
    strategy = EMARSIATRStrategy(candles)

    trades = []
    i = 0

    # ---- SINGLE-PASS ENGINE (NO O(N²)) ----
    while i < len(candles):
        trade = strategy.generate_trade(i)

        if trade:
            trade.entry_index = i

            result = simulate_trade(trade, candles[i + 1:])
            trades.append(result)

            # 🚀 Skip candles inside the trade
            if result.exit_index is not None:
                i = result.exit_index + 1
                continue

        i += 1

    # ---- STATS ----
    print(basic_trade_stats(trades))
    print(pnl_stats(trades))
    print(r_multiple_stats(trades))

    # ---- EQUITY & DRAWDOWN (R-MULTIPLE BASED) ----
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
