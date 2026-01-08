from loader import load_candles
from models import Trade, Direction
from simulator import simulate_trade
from stats import basic_trade_stats, pnl_stats

def main():
    candles = load_candles("data/xrp_15m.csv")

    trades = []

    for i in range(50, 200, 10):
        entry = candles[i]

        trade = Trade(
            direction=Direction.LONG,
            entry_price=entry.close,
            stop_loss=entry.close * 0.18,
            take_profit=entry.close * 1.04,
            entry_time=entry.close_time,
        )

        result = simulate_trade(trade, candles[i + 1:])
        trades.append(result)

    basic = basic_trade_stats(trades)
    pnl = pnl_stats(trades)

    print(basic)
    print(pnl)


if __name__ == "__main__":
    main()
