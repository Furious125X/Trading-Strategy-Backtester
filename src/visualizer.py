# src/visualizer.py
import matplotlib
matplotlib.use("Agg")   # headless backend for Codespaces / CI

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from typing import Optional
import os
import math


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def plot_candles(candles, start: int = 0, end: Optional[int] = None, ax=None):
    """
    Deterministic candlestick renderer for headless environments.
    Returns (fig, ax, start, end).
    - uses integer x positions (0..n-1) to avoid time-based gaps.
    """
    if end is None:
        end = len(candles)

    # clamp
    start = max(0, start)
    end = min(len(candles), end)
    if start >= end:
        raise ValueError("start must be < end and within candle range")

    subset = candles[start:end]
    n = len(subset)

    created_fig = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))
        created_fig = True
    else:
        fig = ax.get_figure()
        ax.clear()

    xs = list(range(n))
    width = 0.7

    color_up = "#2ca02c"
    color_down = "#d62728"

    # compute visible y-limits from subset
    highs = [c.high for c in subset]
    lows = [c.low for c in subset]
    ymin = min(lows)
    ymax = max(highs)

    # avoid zero-range
    yrange = max(1e-9, ymax - ymin)

    # Ensure axis limits set before drawing to allow clamping
    ax.set_xlim(-1, n + 1)
    ax.set_ylim(ymin - yrange * 0.06, ymax + yrange * 0.06)

    # Draw candles deterministically
    for i, c in enumerate(subset):
        x = xs[i]
        openp = float(c.open)
        closep = float(c.close)
        highp = float(c.high)
        lowp = float(c.low)

        # Clamp extreme outliers to plotting range to avoid absurd artefacts
        # (we still show true values in diagnostics; this only affects rendering)
        lowp = _clamp(lowp, ymin - yrange * 0.2, ymax + yrange * 0.2)
        highp = _clamp(highp, ymin - yrange * 0.2, ymax + yrange * 0.2)
        openp = _clamp(openp, ymin - yrange * 0.2, ymax + yrange * 0.2)
        closep = _clamp(closep, ymin - yrange * 0.2, ymax + yrange * 0.2)

        # Wick (vertical line)
        ax.vlines(x, lowp, highp, linewidth=0.8, color="black", zorder=2)

        # Body
        if closep >= openp:
            col = color_up
            bottom = openp
            height = closep - openp
        else:
            col = color_down
            bottom = closep
            height = openp - closep

        # Prevent invisible bodies or bodies plotted far from their true position:
        # use minimum visible height relative to current visible yrange.
        min_height = yrange * 0.005  # 0.5% of visible range
        if height < min_height:
            # create a centered small rectangle at the correct mid-price
            mid = (openp + closep) / 2.0
            bottom = mid - (min_height / 2.0)
            height = min_height

            # ensure body remains within y-bounds
            bottom = _clamp(bottom, ymin - yrange * 0.05, ymax + yrange * 0.05)
            height = _clamp(height, 1e-6, (ymax - bottom) + yrange * 0.05)

        rect = Rectangle((x - width / 2, bottom), width, height,
                         facecolor=col, edgecolor="black", linewidth=0.25, zorder=3)
        ax.add_patch(rect)

    ax.set_title("Candlestick Chart")
    ax.set_xlabel("Candle Index (slice)")
    ax.set_ylabel("Price")
    ax.grid(True, linestyle="--", alpha=0.35)
    plt.tight_layout()
    return fig, ax, start, end


def plot_trade_overlay(
    ax,
    trade,
    candles,
    start: int = 0,
    end: Optional[int] = None,
    context=None,
    current_index: Optional[int] = None):
    """
    Plot entry / stop / tp and annotate entry/exit candle on an existing axes.
    Draw only *relevant* levels: breakout level and nearest N levels (to avoid clutter).
    """
    # If replay mode, do not draw trade before it exists
    if current_index is not None:
        if current_index < trade.entry_index:
            return ax

    # ---- Risk / Reward Shading ----
    if start <= trade.entry_index < end:
        entry = trade.entry_price
        stop = trade.stop_loss
        target = trade.take_profit

        # Risk zone (red)
        ax.axhspan(
            min(entry, stop),
            max(entry, stop),
            color="red",
            alpha=0.08,
            zorder=0,
        )

        # Reward zone (green)
        ax.axhspan(
            min(entry, target),
            max(entry, target),
            color="green",
            alpha=0.08,
            zorder=0,
        )

    if end is None:
        end = len(candles)

    start = max(0, start)
    end = min(len(candles), end)
    n = end - start

    def idx_to_x(gidx):
        return gidx - start

    # draw ENTRY / SL / TP across visible range only
    # Entry line
    ax.hlines(
        trade.entry_price,
        -1,
        n + 1,
        color="blue",
        linestyle="--",
        linewidth=1.0,
        zorder=1,
    )

    # Stop loss
    ax.hlines(
        trade.stop_loss,
        -1,
        n + 1,
        color="red",
        linestyle=":",
        linewidth=1.0,
        zorder=1,
    )

    # Take profit
    ax.hlines(
        trade.take_profit,
        -1,
        n + 1,
        color="green",
        linestyle=":",
        linewidth=1.0,
        zorder=1,
    )

    # entry marker (if visible)
    if (
    start <= trade.entry_index < end
    and current_index is not None
    and current_index >= trade.entry_index):
    
        entry_x = idx_to_x(trade.entry_index)
        ax.axvline(entry_x, color="blue", linestyle="--", linewidth=1.0, alpha=0.9, zorder=6)
        ax.hlines(trade.entry_price, entry_x - 0.6, entry_x + 0.6, color="blue", linewidth=1.2, zorder=7)
        ax.text(entry_x, trade.entry_price, " ENTRY", color="blue", va="bottom", fontsize=9, zorder=8)

    # ---- Confirmation Candle Highlight ----
    if (
        trade.confirmation_index is not None
        and current_index is not None
        and current_index >= trade.confirmation_index
        and start <= trade.confirmation_index < end):
        
            conf_x = trade.confirmation_index - start

            # Vertical highlight
            ax.axvline(
                conf_x,
                color="orange",
                linestyle="-",
                linewidth=2.0,
                alpha=0.6,
                zorder=5,
            )

            # Label
            ax.text(
                conf_x,
                candles[trade.confirmation_index].high,
                " CONFIRM",
                color="orange",
                fontsize=8,
                ha="center",
                va="bottom",
                zorder=9,
            )

    # exit marker
    if (
    trade.exit_index is not None
    and current_index is not None
    and current_index >= trade.exit_index
    and start <= trade.exit_index < end):

        exit_x = idx_to_x(trade.exit_index)
        ax.axvline(exit_x, color="purple", linestyle="--", linewidth=1.0, alpha=0.9, zorder=6)
        ax.hlines(trade.exit_price, exit_x - 0.6, exit_x + 0.6, color="purple", linewidth=1.2, zorder=7)
        ax.text(exit_x, trade.exit_price, " EXIT", color="purple", va="bottom", fontsize=9, zorder=8)

    # draw relevant levels (only a few)
    if context is not None and getattr(context, "levels", None):
        levels_list = context.levels.levels or []

        # Prefer: 1) breakout level used by trade (if present), 2) nearest N levels to entry price
        relevant = []

        # breakout level if present and within slice price range
        tags = trade.trade_tags or {}
        bl = tags.get("breakout_level", None)
        if bl is not None:
            relevant.append(("breakout", bl))

        # compute center price (entry price if visible else mid price of slice)
        if start <= trade.entry_index < end:
            center_price = trade.entry_price
        else:
            # approximate using visible candle mid
            subset = candles[start:end]
            center_price = sum((c.close + c.open) / 2.0 for c in subset) / max(1, len(subset))

        # find levels nearest to center_price
        def dist(tup):
            return abs(tup - center_price)

        nearest = sorted(levels_list, key=dist)
        # pick top N but ensure they are not too many
        N = 8
        for lvl in nearest[:N]:
            relevant.append(("near", lvl))

        # Deduplicate preserve order
        seen = set()
        filtered = []
        for tag, lvl in relevant:
            if lvl in seen:
                continue
            seen.add(lvl)
            filtered.append((tag, lvl))

        # Draw the filtered levels
        for tag, lvl in filtered:
            color = "#b35900" if tag == "near" else "#ff7f0e"
            alpha = 0.55 if tag == "near" else 0.85
            ax.hlines(lvl, -1, n + 1, color=color, linestyle="--", linewidth=0.9, alpha=alpha, zorder=1)

            if tag == "breakout":
                # label breakout
                x_label = (trade.entry_index - start) if (start <= trade.entry_index < end) else 0
                ax.text(x_label, lvl, " BREAK", color=color, fontsize=8, zorder=9)

    # ---- Trade Info Panel ----
    if (
        current_index is not None
        and current_index >= trade.entry_index
    ):
        info_lines = []

        info_lines.append(f"Direction: {trade.direction.value.upper()}")
        info_lines.append(f"Entry: {trade.entry_price:.2f}")
        info_lines.append(f"Stop: {trade.stop_loss:.2f}")
        info_lines.append(f"Target: {trade.take_profit:.2f}")

        # Live R multiple calculation
        if current_index < len(candles):
            price = candles[current_index].close
            risk = abs(trade.entry_price - trade.stop_loss)

            if risk > 0:
                if trade.direction.value == "long":
                    r_live = (price - trade.entry_price) / risk
                else:
                    r_live = (trade.entry_price - price) / risk

                info_lines.append(f"Live R: {r_live:.2f}")

        # Include tags if present
        if getattr(trade, "tags", None):
            for k, v in trade.tags.items():
                try:
                    info_lines.append(f"{k}: {v:.2f}")
                except Exception:
                    info_lines.append(f"{k}: {v}")

        text = "\n".join(info_lines)

        ax.text(
            0.01,
            0.99,
            text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            bbox=dict(
                boxstyle="round",
                facecolor="black",
                alpha=0.6,
            ),
            color="white",
            zorder=20,
        )

    return ax


def save_trade_chart(trade, candles, filename, context=None, window=60):
    """
    Save a PNG for a single trade in headless mode.
    - draws only nearest levels and breakout level to avoid clutter
    """
    start = max(0, trade.entry_index - window)
    end = min(len(candles), trade.entry_index + window)

    fig, ax, s, e = plot_candles(candles, start=start, end=end)
    ax = plot_trade_overlay(
    ax,
    trade,
    candles,
    start=s,
    end=e,
    context=context,
    current_index=trade.exit_index or trade.entry_index)

    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    fig.savefig(filename, dpi=200, bbox_inches="tight")
    plt.close(fig)