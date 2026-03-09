from optimizer import parameter_sweep, rank_results
from simulator import simulate_trade
from strategies.registry import get_strategy


def run_backtest_window(candles, context, strategy_name, params):

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

def walk_forward_test(
    candles,
    context,
    strategy_name,
    param_grid,
    train_size,
    test_size
):

    results = []

    start = 0

    while start + train_size + test_size < len(candles):

        train_data = candles[start:start+train_size]
        test_data = candles[start+train_size:start+train_size+test_size]

        # optimize on training data
        sweep = parameter_sweep(
            train_data,
            context,
            strategy_name,
            param_grid
        )

        best = rank_results(sweep, top_n=1)[0]

        best_params = best["params"]

        # test on unseen data
        trades = run_backtest_window(
            test_data,
            context,
            strategy_name,
            best_params
        )

        total_r = sum(t.r_multiple for t in trades)

        results.append({
            "params": best_params,
            "test_trades": len(trades),
            "test_total_r": total_r
        })

        start += test_size

    return results

