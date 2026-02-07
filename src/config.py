CONFIG = {
    "data": {
        "path": "data/ETHUSD_15.csv",
        "htf_factor": 4,
    },

    "strategy": {
        "name": "ema_rsi_atr",
        "params": {
            "ema_period": 50,
            "rsi_period": 14,
            "atr_period": 14,
            "atr_multiplier": 1.5,
            "risk_reward": 2.0,
        },
    },

    "risk": {
        "starting_balance": 10_000,
        "risk_per_trade": 0.01,
    },
}
