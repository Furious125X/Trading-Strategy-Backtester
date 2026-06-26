CONFIG = {
    "data": {
        "path": "data/ETHUSD_15.csv",
        "timeframe" : 15,
        "htf_factor": 4,
    },

    "strategy": {
        "name": "breakout_retest",
        "params": {
            "ema_period": 50,
            "rsi_period": 14,
            "atr_period": 14,
            "atr_multiplier": 1.5,
            "risk_reward": 2.0,
        },
    },

    "strategy": {
        "name": "ema_pullback_test",
        "params": {
            "risk_reward": 2.0,
            "rsi_threshold": 50,
        },
    },

    "risk": {
        "starting_balance": 10_000,
        "risk_per_trade": 0.01,
    },


}
