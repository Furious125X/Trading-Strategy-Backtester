import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def plot_candles(candles, start=0, end=None, ax=None):
    """
    Simple, reliable candlestick renderer using Candle objects.
    - candles: list of Candle
    - start, end: integer indices (end exclusive)
    Returns (fig, ax)
    """
    if end is None:
        end = len(candles)

    # clamp
    start = max(0, start)
    end = min(len(candles), end)
    subset = candles[start:end]

    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))
    else:
        fig = ax.get_figure()

    xs = list(range(len(subset)))

    color_up = "#2ca02c"   # green
    color_down = "#d62728" # red
    width = 0.8

    ax.clear()

    for i, c in enumerate(subset):
        x = xs[i]
        openp = c.open
        highp = c.high
        lowp = c.low
        closep = c.close

        # wick
        ax.vlines(x, lowp, highp, linewidth=1, color="black", zorder=1)

        # body
        if closep >= openp:
            col = color_up
            bottom = openp
            height = closep - openp
        else:
            col = color_down
            bottom = closep
            height = openp - closep

        # avoid zero-height rectangles (visible tiny body)
        if height == 0:
            height = (highp - lowp) * 0.001 or 0.0001

        rect = Rectangle((x - width / 2, bottom), width, height, facecolor=col, edgecolor="black", linewidth=0.4, zorder=2)
        ax.add_patch(rect)

    ax.set_xlim(-1, len(subset) + 1)
    # auto-scale y with small margin
    all_prices = [p for c in subset for p in (c.high, c.low)]
    if all_prices:
        ymin = min(all_prices)
        ymax = max(all_prices)
        yrange = max(1e-9, ymax - ymin)
        ax.set_ylim(ymin - yrange * 0.05, ymax + yrange * 0.05)

    ax.set_title("Candlestick Chart")
    ax.set_xlabel("Candle Index (local slice)")
    ax.set_ylabel("Price")
    ax.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    return fig, ax


def plot_trade_overlay(ax, trade, candles, start=0, end=None):
    """
    Draw entry / stop / tp and annotate entry/exit candle on an existing axes.
    - ax: matplotlib axes
    - trade: Trade object (with entry_index, exit_index, entry_price, stop_loss, take_profit)
    - candles: full candles list
    - start/end: the slice used to render candles (same coordinates)
    """
    if end is None:
        end = len(candles)

    start = max(0, start)
    end = min(len(candles), end)

    # convert global index -> local x
    def idx_to_x(global_idx):
        return global_idx - start

    # entry marker
    entry_x = idx_to_x(trade.entry_index)
    ax.axvline(entry_x, color="blue", linestyle="--", linewidth=1, alpha=0.9, zorder=4)
    ax.hlines(trade.entry_price, entry_x - 0.5, entry_x + 0.5, color="blue", linewidth=1.2, zorder=5)
    ax.text(entry_x, trade.entry_price, " ENTRY", color="blue", va="bottom", fontsize=9, zorder=6)

    # stop loss
    ax.hlines(trade.stop_loss, -1, len(candles), color="red", linestyle=":", linewidth=1.0, zorder=3)
    ax.text(entry_x, trade.stop_loss, " SL", color="red", va="bottom", fontsize=9, zorder=6)

    # take profit
    ax.hlines(trade.take_profit, -1, len(candles), color="green", linestyle=":", linewidth=1.0, zorder=3)
    ax.text(entry_x, trade.take_profit, " TP", color="green", va="bottom", fontsize=9, zorder=6)

    # exit marker (if present)
    if getattr(trade, "exit_index", None) is not None:
        exit_x = idx_to_x(trade.exit_index)
        ax.axvline(exit_x, color="purple", linestyle="--", linewidth=1.0, alpha=0.9, zorder=4)
        ax.text(exit_x, trade.exit_price, " EXIT", color="purple", va="bottom", fontsize=9, zorder=6)

    return ax