from loader import load_candles
from models import Trade, Direction
from simulator import simulate_trade

def main():
    candles = load_candles("data/xrp_15m.csv")

    entry_index = 100
    entry_candle = candles[entry_index]

    trade = Trade(
        direction=Direction.LONG,
        entry_price=entry_candle.close,
        stop_loss=entry_candle.close * 0.96,
        take_profit=entry_candle.close * 1.04,
        entry_time=entry_candle.close_time,
    )

    result = simulate_trade(trade, candles[entry_index + 1:])

    print(result)

if __name__ == "__main__":
    main()
