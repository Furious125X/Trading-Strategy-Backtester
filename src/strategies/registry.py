from strategies.ema_rsi_atr_strategy import EMARSIATRStrategy


STRATEGY_REGISTRY = {
    "ema_rsi_atr": EMARSIATRStrategy,
}


def get_strategy(name):
    if name not in STRATEGY_REGISTRY:
        raise ValueError(f"Strategy '{name}' not found in registry")
    return STRATEGY_REGISTRY[name]
