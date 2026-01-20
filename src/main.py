from loader import load_candles
from simulator import simulate_trade
from stats import basic_trade_stats, pnl_stats, r_multiple_stats
from strategy import EMARSIATRStrategy


def main():
    candles = load_candles("data/xrp_15m.csv")
    strategy = EMARSIATRStrategy(candles)

    trades = []
    i = 0

    while i < len(candles):
        trade = strategy.generate_trade(i)

        if trade:
            trade.entry_index = i

            result = simulate_trade(trade, candles[i + 1 :])
            trades.append(result)

            if result.exit_index is not None:
                i = result.exit_index + 1
                continue

        i += 1

    print(basic_trade_stats(trades))
    print(pnl_stats(trades))
    print(r_multiple_stats(trades))

if __name__ == "__main__":
    main()
