from strategies.breakout_retest import breakout_retest_strategy
from strategies.ema_pullback_test import ema_pullback_test

STRATEGY_REGISTRY = {
    "breakout_retest": breakout_retest_strategy,
    "ema_pullback_test": ema_pullback_test
}


def get_strategy(name):
    if name not in STRATEGY_REGISTRY:
        raise ValueError(f"Strategy '{name}' not found in registry")
    return STRATEGY_REGISTRY[name]
