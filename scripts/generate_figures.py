#!/usr/bin/env python3
"""
generate_figures.py — Publication-quality figure generation for experiment results.

Generates:
1. Bar chart: Success rate by strategy (grouped by model)
2. Heatmap: Model × Strategy interaction matrix
3. Improvement waterfall chart
4. Cost-effectiveness plot

Usage:
    python scripts/generate_figures.py \
        --results-dir data/results/ \
        --output analysis/figures/
"""

import argparse
import json
import logging
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    logger.warning("matplotlib not installed. Install with: pip install matplotlib")


# ──────────────────────────────────────────────
# Style Configuration (Publication Quality)
# ──────────────────────────────────────────────

STYLE_CONFIG = {
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
}

# Color palette (colorblind-friendly)
STRATEGY_COLORS = {
    "baseline": "#4C72B0",
    "chain_of_thought": "#DD8452",
    "few_shot": "#55A868",
    "persona": "#C44E52",
    "structured_decomposition": "#8172B3",
}

MODEL_MARKERS = {
    "deepseek-v3": "o",
    "llama-3.3-70b": "s",
    "qwen2.5-coder-32b": "^",
}

STRATEGY_LABELS = {
    "baseline": "Baseline",
    "chain_of_thought": "Chain-of-Thought",
    "few_shot": "Few-Shot",
    "persona": "Persona",
    "structured_decomposition": "Structured Decomp.",
}

MODEL_LABELS = {
    "deepseek-v3": "DeepSeek-V3",
    "llama-3.3-70b": "Llama-3.3-70B",
    "qwen2.5-coder-32b": "Qwen2.5-Coder-32B",
}


def load_summary(analysis_dir: Path) -> dict:
    """Load results summary CSV and comparisons JSON."""
    csv_path = analysis_dir / "results_summary.csv"
    json_path = analysis_dir / "comparisons.json"

    data = {"rates": {}, "comparisons": []}

    if csv_path.exists():
        with open(csv_path) as f:
            lines = f.readlines()
        for line in lines[1:]:  # Skip header
            parts = line.strip().split(",")
            if len(parts) >= 5:
                model, strategy = parts[0], parts[1]
                data["rates"][(model, strategy)] = {
                    "n_tasks": int(parts[2]),
                    "success_rate": float(parts[3]),
                    "successes": int(parts[4]),
                    "ci_lower": float(parts[5]) if len(parts) > 5 else 0,
                    "ci_upper": float(parts[6]) if len(parts) > 6 else 0,
                }

    if json_path.exists():
        with open(json_path) as f:
            data["comparisons"] = json.load(f)

    return data


# ──────────────────────────────────────────────
# Figure 1: Grouped Bar Chart
# ──────────────────────────────────────────────


def plot_success_rates(data: dict, output_dir: Path) -> None:
    """Bar chart of success rates grouped by model, colored by strategy."""
    if not HAS_MATPLOTLIB:
        return

    plt.rcParams.update(STYLE_CONFIG)

    rates = data["rates"]
    models = sorted(set(k[0] for k in rates.keys()))
    strategies = sorted(set(k[1] for k in rates.keys()))

    fig, ax = plt.subplots(figsize=(10, 5))

    n_strategies = len(strategies)
    n_models = len(models)
    bar_width = 0.15
    x = np.arange(n_models)

    for i, strategy in enumerate(strategies):
        values = []
        ci_lower = []
        ci_upper = []
        for model in models:
            r = rates.get((model, strategy), {})
            val = r.get("success_rate", 0) * 100
            values.append(val)
            ci_lower.append(val - r.get("ci_lower", 0) * 100)
            ci_upper.append(r.get("ci_upper", 0) * 100 - val)

        offset = (i - n_strategies / 2 + 0.5) * bar_width
        bars = ax.bar(
            x + offset,
            values,
            bar_width,
            label=STRATEGY_LABELS.get(strategy, strategy),
            color=STRATEGY_COLORS.get(strategy, "#999999"),
            yerr=[ci_lower, ci_upper] if any(ci_lower) else None,
            capsize=3,
            edgecolor="white",
            linewidth=0.5,
        )

    ax.set_xlabel("Model")
    ax.set_ylabel("Success Rate (%)")
    ax.set_title("Vulnerability Reproduction Success Rate by Model and Prompt Strategy")
    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_LABELS.get(m, m) for m in models])
    ax.legend(loc="upper left", framealpha=0.9)
    ax.set_ylim(bottom=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    path = output_dir / "fig1_success_rates.pdf"
    fig.savefig(path)
    fig.savefig(path.with_suffix(".png"))
    plt.close(fig)
    logger.info(f"Saved: {path}")


# ──────────────────────────────────────────────
# Figure 2: Heatmap
# ──────────────────────────────────────────────


def plot_heatmap(data: dict, output_dir: Path) -> None:
    """Model × Strategy heatmap of success rates."""
    if not HAS_MATPLOTLIB:
        return

    plt.rcParams.update(STYLE_CONFIG)

    rates = data["rates"]
    models = sorted(set(k[0] for k in rates.keys()))
    strategies = sorted(set(k[1] for k in rates.keys()))

    matrix = np.zeros((len(models), len(strategies)))
    for i, model in enumerate(models):
        for j, strategy in enumerate(strategies):
            r = rates.get((model, strategy), {})
            matrix[i, j] = r.get("success_rate", 0) * 100

    fig, ax = plt.subplots(figsize=(8, 4))
    im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto")

    ax.set_xticks(range(len(strategies)))
    ax.set_xticklabels(
        [STRATEGY_LABELS.get(s, s) for s in strategies], rotation=45, ha="right"
    )
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels([MODEL_LABELS.get(m, m) for m in models])

    # Add value annotations
    for i in range(len(models)):
        for j in range(len(strategies)):
            val = matrix[i, j]
            color = "white" if val > matrix.max() * 0.6 else "black"
            ax.text(j, i, f"{val:.1f}%", ha="center", va="center", color=color, fontsize=9)

    ax.set_title("Success Rate (%) — Model × Strategy")
    fig.colorbar(im, ax=ax, label="Success Rate (%)", shrink=0.8)

    fig.tight_layout()
    path = output_dir / "fig2_heatmap.pdf"
    fig.savefig(path)
    fig.savefig(path.with_suffix(".png"))
    plt.close(fig)
    logger.info(f"Saved: {path}")


# ──────────────────────────────────────────────
# Figure 3: Improvement Waterfall
# ──────────────────────────────────────────────


def plot_improvement(data: dict, output_dir: Path) -> None:
    """Waterfall chart showing improvement over baseline per strategy."""
    if not HAS_MATPLOTLIB or not data["comparisons"]:
        return

    plt.rcParams.update(STYLE_CONFIG)

    # Aggregate improvement across models
    strategy_improvements = defaultdict(list)
    for c in data["comparisons"]:
        strategy_improvements[c["strategy"]].append(c["improvement_pp"] * 100)

    strategies = sorted(strategy_improvements.keys())
    means = [np.mean(strategy_improvements[s]) for s in strategies]
    stds = [np.std(strategy_improvements[s]) for s in strategies]

    fig, ax = plt.subplots(figsize=(8, 4))

    colors = ["#55A868" if m >= 0 else "#C44E52" for m in means]
    bars = ax.bar(
        range(len(strategies)),
        means,
        yerr=stds,
        capsize=4,
        color=colors,
        edgecolor="white",
        linewidth=0.5,
    )

    ax.axhline(y=0, color="black", linewidth=0.5, linestyle="-")
    ax.set_xticks(range(len(strategies)))
    ax.set_xticklabels(
        [STRATEGY_LABELS.get(s, s) for s in strategies], rotation=30, ha="right"
    )
    ax.set_ylabel("Improvement over Baseline (pp)")
    ax.set_title("Average Improvement by Prompt Strategy (across all models)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    path = output_dir / "fig3_improvement.pdf"
    fig.savefig(path)
    fig.savefig(path.with_suffix(".png"))
    plt.close(fig)
    logger.info(f"Saved: {path}")


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Generate publication-quality figures from experiment results"
    )
    parser.add_argument(
        "--analysis-dir",
        type=Path,
        default=Path("analysis"),
        help="Directory containing analysis results (CSV, JSON)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis/figures"),
        help="Output directory for figures",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not HAS_MATPLOTLIB:
        logger.error("matplotlib is required. Install: pip install matplotlib numpy")
        return

    args.output.mkdir(parents=True, exist_ok=True)

    data = load_summary(args.analysis_dir)
    if not data["rates"]:
        logger.error("No data found. Run analyze_results.py first.")
        return

    plot_success_rates(data, args.output)
    plot_heatmap(data, args.output)
    plot_improvement(data, args.output)

    logger.info(f"\nAll figures saved to: {args.output}")


if __name__ == "__main__":
    main()
