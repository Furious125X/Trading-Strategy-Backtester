from strategies.breakout_retest import breakout_retest_strategy


STRATEGY_REGISTRY = {
    "breakout_retest": breakout_retest_strategy,
}


def get_strategy(name):
    if name not in STRATEGY_REGISTRY:
        raise ValueError(f"Strategy '{name}' not found in registry")
    return STRATEGY_REGISTRY[name]
