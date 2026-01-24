import matplotlib.pyplot as plt


def plot_equity_curve(equity_curve, drawdowns):
    plt.figure(figsize=(10, 6))

    plt.plot(equity_curve, label="Equity Curve")
    plt.title("Equity Curve (R-Multiple Based)")
    plt.xlabel("Trade Number")
    plt.ylabel("Account Balance")

    plt.legend()
    plt.grid(True)

    # 🔥 SAVE instead of show
    plt.savefig("equity_curve.png")
    plt.close()
