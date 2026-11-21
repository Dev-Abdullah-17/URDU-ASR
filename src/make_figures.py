"""Figures for the WER We Stand re-evaluation (from committed aggregate tables only).

Inputs (committed, no reference text):
    results/reeval_table.csv          (reeval_wws.py)
    results/reeval_length_buckets.csv (reeval_analysis.py)
Outputs:
    results/figures/rank_slope_utt_vs_corpus.png
    results/figures/wer_by_length_top5.png

    python src/make_figures.py --results-dir results

Static PNGs for the README/paper. Identity is never colour-only: every line is
directly labelled (slope chart) or carries a distinct marker shape plus a
legend (length chart). The underlying numbers are in the CSVs above (table
view). `as_released~` is our reproduction of the published scoring (WWS
chars.json is unavailable), so its values differ from the paper by <= 0.20.
"""

from __future__ import annotations

import argparse
import csv
import os

import matplotlib
from scipy.stats import kendalltau

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

# Validated default palette (light mode), see the dataviz palette reference.
SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e4e3df"
NEUTRAL = "#b5b3ad"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]  # fixed order
UP, DOWN = SERIES[0], SERIES[1]   # rank improves / worsens under corpus WER
MARKERS = ["o", "s", "D", "^", "v"]
DODGE = 0.07  # x offset between series on categorical axes
DPI = 150
CONDITIONS = ("as_released~", "N7_numwords")   # both tables carry these


def condition_label(condition: str) -> str:
    if condition == "as_released~":
        return "as released~ (reproduction of the published scoring)"
    return f"{condition} (our normalizer, both sides)"

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": NEUTRAL, "axes.labelcolor": TEXT_2,
    "xtick.color": TEXT_2, "ytick.color": TEXT_2, "text.color": TEXT,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})


def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def slope_chart(table, condition, out):
    """Rank by utterance-averaged vs corpus WER for one condition; tau is
    computed from the two plotted rankings."""
    sel = [r for r in table if r["subset"] == "overall" and r["condition"] == condition]
    left = {r["model"]: (int(r["rank"]), float(r["value"])) for r in sel if r["metric"] == "utt_wer"}
    right = {r["model"]: (int(r["rank"]), float(r["value"])) for r in sel if r["metric"] == "corpus_wer"}
    models = sorted(left)
    tau = kendalltau([left[m][0] for m in models], [right[m][0] for m in models]).statistic
    n = len(left)

    fig, ax = plt.subplots(figsize=(7.2, 6.4))
    for m in left:
        (rl, vl), (rr, vr) = left[m], right[m]
        color = NEUTRAL if rl == rr else (UP if rr < rl else DOWN)
        lw, z = (1.2, 1) if rl == rr else (2.0, 3)
        ax.plot([0, 1], [rl, rr], color=color, lw=lw, zorder=z, solid_capstyle="round")
        ax.scatter([0, 1], [rl, rr], s=36, color=color, zorder=z + 1,
                   edgecolor=SURFACE, linewidth=1.5)
        ink = TEXT if rl != rr else TEXT_2
        ax.text(-0.04, rl, f"{m}  {vl:.2f}", ha="right", va="center", fontsize=8, color=ink)
        ax.text(1.04, rr, f"{vr:.2f}  {m}", ha="left", va="center", fontsize=8, color=ink)
    ax.set_ylim(n + 0.7, 0.3)
    ax.set_xlim(-0.9, 1.9)
    ax.set_yticks([])
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["rank by utterance-averaged WER\n(the paper's metric)",
                        "rank by corpus WER"], fontsize=9, color=TEXT)
    ax.tick_params(axis="x", length=0, pad=8)
    ax.xaxis.set_ticks_position("top")
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(f"Model ranking, utterance-averaged vs corpus WER (Kendall's τ = {tau:.3f})\n"
                 f"{condition_label(condition)}", fontsize=10, color=TEXT, loc="left", pad=36)
    ax.text(0.5, n + 0.55,
            "blue = better rank under corpus WER · orange = worse · grey = unchanged; values are WER (%)",
            ha="center", va="top", fontsize=7.5, color=TEXT_2)
    fig.tight_layout()
    fig.savefig(out, dpi=DPI)
    plt.close(fig)


def length_chart(table, buckets, condition, out, top_k=5):
    """Corpus WER per reference-length bucket for the top_k models (ranked by
    utterance-averaged WER under `condition`), requested and finer buckets."""
    sel = [r for r in table if r["subset"] == "overall" and r["condition"] == condition
           and r["metric"] == "utt_wer"]
    top = [r["model"] for r in sorted(sel, key=lambda r: int(r["rank"]))[:top_k]]
    schemes = [("spec", "requested buckets"), ("fine", "finer split")]
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.2), sharey=True,
                             gridspec_kw={"width_ratios": [3, 4]})
    ymax = 0
    for ax, (scheme, title) in zip(axes, schemes):
        rows = [r for r in buckets if r["scheme"] == scheme and r["condition"] == condition]
        order = []
        for r in rows:
            if r["bucket"] not in order:
                order.append(r["bucket"])
        n_utts = {r["bucket"]: r["n_utts"] for r in rows}
        x = list(range(len(order)))
        for i, m in enumerate(top):
            by_b = {r["bucket"]: float(r["corpus_wer"]) for r in rows if r["model"] == m}
            y = [by_b[b] for b in order]
            ymax = max(ymax, max(y))
            # small horizontal dodge so converging markers stay visible
            xd = [v + (i - (top_k - 1) / 2) * DODGE for v in x]
            # lines in one layer, all markers in a higher layer, so no line
            # can cover another series' marker
            ax.plot(xd, y, color=SERIES[i], lw=2, zorder=3)
            ax.plot(xd, y, ls="none", color=SERIES[i], marker=MARKERS[i], ms=6,
                    markeredgecolor=SURFACE, markeredgewidth=1.2, zorder=10 + i)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{b.replace('<=', '≤')} words\nn = {n_utts[b]}" for b in order],
                           fontsize=8)
        ax.set_title(title, fontsize=9, color=TEXT_2, loc="left")
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.set_xlim(-0.3, len(order) - 0.7)
    axes[0].set_ylabel("corpus WER within bucket (%)")
    axes[0].set_ylim(0, ymax * 1.08)
    handles = [Line2D([0], [0], color=SERIES[i], lw=2, marker=MARKERS[i], ms=6,
                      markeredgewidth=0) for i in range(len(top))]
    axes[0].legend(handles, top, frameon=False, fontsize=7.5, loc="upper right")
    fig.suptitle(f"WER by reference length, top {top_k} models by utterance-averaged WER — "
                 f"{condition_label(condition)}", fontsize=10, color=TEXT, x=0.01, ha="left")
    smallest = min((r for r in buckets if r["scheme"] == "spec" and r["condition"] == condition),
                   key=lambda r: int(r["n_utts"]))
    fig.text(0.01, 0.02, f"Length = raw reference word count. The {smallest['bucket'].replace('<=', '≤')} "
             f"bucket has only {smallest['n_utts']} utterances "
             f"({float(smallest['word_share']) * 100:.1f}% of words); its values are noisy. "
             "Series are offset slightly along x so overlapping points stay visible.",
             fontsize=7, color=TEXT_2)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(out, dpi=DPI)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--results-dir", default="results")
    p.add_argument("--condition", default="as_released~", choices=CONDITIONS)
    a = p.parse_args()
    table = read_csv(os.path.join(a.results_dir, "reeval_table.csv"))
    buckets = read_csv(os.path.join(a.results_dir, "reeval_length_buckets.csv"))
    out_dir = os.path.join(a.results_dir, "figures")
    os.makedirs(out_dir, exist_ok=True)
    f1 = os.path.join(out_dir, "rank_slope_utt_vs_corpus.png")
    f2 = os.path.join(out_dir, "wer_by_length_top5.png")
    slope_chart(table, a.condition, f1)
    length_chart(table, buckets, a.condition, f2)
    print(f"wrote {f1}\nwrote {f2}")


if __name__ == "__main__":
    main()
