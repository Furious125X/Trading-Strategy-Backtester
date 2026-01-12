from loader import load_candles
from simulator import simulate_trade
from stats import basic_trade_stats, pnl_stats
from strategy import SimpleBreakoutStrategy


def main():
    candles = load_candles("data/xrp_15m.csv")
    strategy = SimpleBreakoutStrategy()

    trades = []

    for i in range(len(candles) - 1):
        trade = strategy.generate_trade(candles, i)

        if trade:
            result = simulate_trade(trade, candles[i + 1:])
            trades.append(result)

    print(basic_trade_stats(trades))
    print(pnl_stats(trades))


if __name__ == "__main__":
    main()
