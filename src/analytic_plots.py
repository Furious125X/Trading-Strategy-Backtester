import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


def plot_mfe_mae(analytics, path="analytic_outputs/mfe_mae.png"):

    mfe = [a["mfe_r"] for a in analytics]
    mae = [a["mae_r"] for a in analytics]

    plt.figure()

    plt.scatter(mae, mfe)

    plt.xlabel("MAE (R)")
    plt.ylabel("MFE (R)")
    plt.title("Trade Excursions")

    plt.savefig(path)
    plt.close()


def plot_duration(analytics, path="analytic_outputs/trade_duration.png"):

    durations = [a["duration"] for a in analytics]

    plt.figure()

    plt.hist(durations, bins=30)

    plt.xlabel("Trade Duration (bars)")
    plt.ylabel("Count")
    plt.title("Trade Duration Distribution")

    plt.savefig(path)
    plt.close()

def plot_r_distribution(analytics, path="analytic_outputs/r_distribution.png"):

    results = [a["result_r"] for a in analytics]

    plt.figure()

    plt.hist(results, bins=30)

    plt.xlabel("R Multiple")
    plt.ylabel("Count")
    plt.title("Trade Result Distribution")

    plt.savefig(path)
    plt.close()

