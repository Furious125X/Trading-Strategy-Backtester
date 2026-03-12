def combine_trades(strategy_trades):
    """
    strategy_trades = {
        "strategy_name": [trade1, trade2, ...]
    }
    """

    combined = []

    for name, trades in strategy_trades.items():
        for t in trades:
            t.strategy = name
            combined.append(t)

    # sort trades by entry time
    combined.sort(key=lambda x: x.entry_index)

    return combined

from strategies.registry import get_strategy
from simulator import simulate_trade


def run_strategy(candles, context, strategy_name, params):

    StrategyClass = get_strategy(strategy_name)
    strategy = StrategyClass(context, **params)

    trades = []

    i = 0

    while i < len(candles):

        if strategy.should_enter(i):

            trade = strategy.build_trade(i)

            result = simulate_trade(trade, candles[i+1:])

            trades.append(result)

            if result.exit_index:
                i = result.exit_index + 1
                continue

        i += 1

    return trades

def run_portfolio(candles, context, strategies):

    strategy_trades = {}

    for name, params in strategies.items():

        trades = run_strategy(
            candles,
            context,
            name,
            params
        )

        strategy_trades[name] = trades

    combined = combine_trades(strategy_trades)

    return combined, strategy_trades

