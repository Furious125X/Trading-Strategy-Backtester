from itertools import product
from strategies.registry import get_strategy
from simulator import simulate_trade


def run_single_backtest(candles, context, strategy_name, params):

    StrategyClass = get_strategy(strategy_name)
    strategy = StrategyClass(context, **params)

    trades = []

    i = 0
    while i < len(candles):

        if strategy.should_enter(i):

            trade = strategy.build_trade(i)

            result = simulate_trade(trade, candles[i + 1:])
            trades.append(result)

            if result.exit_index:
                i = result.exit_index + 1
                continue

        i += 1

    return trades

def parameter_sweep(candles, context, strategy_name, param_grid):

    keys = list(param_grid.keys())
    values = list(param_grid.values())

    results = []

    for combo in product(*values):

        params = dict(zip(keys, combo))

        trades = run_single_backtest(
            candles,
            context,
            strategy_name,
            params
        )

        total_r = sum(t.r_multiple for t in trades)

        results.append({
            "params": params,
            "trades": len(trades),
            "total_r": total_r
        })

    return results

def rank_results(results, top_n=10):

    results.sort(
        key=lambda x: x["total_r"],
        reverse=True
    )

    return results[:top_n]