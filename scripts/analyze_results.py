#!/usr/bin/env python3
"""
analyze_results.py — Statistical analysis of experiment results.

Computes success rates, runs McNemar's test for pairwise comparisons,
calculates effect sizes (Cohen's h), and generates summary tables.

Usage:
    python scripts/analyze_results.py \
        --results-dir data/results/ \
        --output analysis/
"""

import argparse
import json
import logging
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Data Loading
# ──────────────────────────────────────────────


def load_all_results(results_dir: Path) -> list[dict]:
    """Load all experiment result JSON files from the results directory."""
    results = []
    for json_file in results_dir.rglob("*.json"):
        if json_file.name.startswith("."):
            continue
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
                results.append(data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Skipping {json_file}: {e}")
    logger.info(f"Loaded {len(results)} result files")
    return results


# ──────────────────────────────────────────────
# Success Rate Computation
# ──────────────────────────────────────────────


def compute_success_rates(results: list[dict]) -> dict:
    """
    Compute success rates per (model, strategy) condition.
    
    Uses "any of N reps succeeds" as primary metric (matches paper).
    Also computes "strict" (all reps succeed) and "mean" rates.
    """
    # Group by (model, strategy, task_id)
    groups = defaultdict(list)
    for r in results:
        key = (r["model"], r["strategy"], r["task_id"])
        groups[key].append(r["success"])

    # Aggregate per (model, strategy)
    condition_results = defaultdict(lambda: {"any": [], "strict": [], "mean": []})
    
    for (model, strategy, task_id), successes in groups.items():
        cond_key = (model, strategy)
        any_success = any(successes)
        all_success = all(successes) if successes else False
        mean_success = sum(successes) / len(successes) if successes else 0

        condition_results[cond_key]["any"].append(any_success)
        condition_results[cond_key]["strict"].append(all_success)
        condition_results[cond_key]["mean"].append(mean_success)

    # Compute rates
    rates = {}
    for (model, strategy), data in condition_results.items():
        n = len(data["any"])
        rates[(model, strategy)] = {
            "model": model,
            "strategy": strategy,
            "n_tasks": n,
            "success_rate_any": sum(data["any"]) / n if n > 0 else 0,
            "success_rate_strict": sum(data["strict"]) / n if n > 0 else 0,
            "success_rate_mean": np.mean(data["mean"]) if n > 0 else 0,
            "successes_any": sum(data["any"]),
            "successes_strict": sum(data["strict"]),
            "per_task_any": data["any"],  # Keep for statistical tests
        }

    return rates


# ──────────────────────────────────────────────
# Statistical Tests
# ──────────────────────────────────────────────


def mcnemar_test(outcomes_a: list[bool], outcomes_b: list[bool]) -> dict:
    """
    McNemar's test for paired binary outcomes.
    
    Tests whether the marginal proportions differ between two conditions
    tested on the same instances.
    
    Returns dict with test statistic, p-value, and contingency table.
    """
    assert len(outcomes_a) == len(outcomes_b), "Must have same number of instances"

    # Build 2x2 contingency table
    # b = A succeeds, B fails
    # c = A fails, B succeeds
    b = sum(1 for a, bv in zip(outcomes_a, outcomes_b) if a and not bv)
    c = sum(1 for a, bv in zip(outcomes_a, outcomes_b) if not a and bv)

    # Both succeed / both fail (for reference)
    a_val = sum(1 for a, bv in zip(outcomes_a, outcomes_b) if a and bv)
    d = sum(1 for a, bv in zip(outcomes_a, outcomes_b) if not a and not bv)

    # McNemar's test statistic (with continuity correction)
    if b + c == 0:
        return {
            "statistic": 0.0,
            "p_value": 1.0,
            "b": b,
            "c": c,
            "a": a_val,
            "d": d,
            "significant": False,
        }

    # Chi-squared with continuity correction
    chi2 = (abs(b - c) - 1) ** 2 / (b + c)

    # p-value from chi-squared distribution with 1 df
    # Using scipy-free approximation
    p_value = _chi2_sf(chi2, df=1)

    return {
        "statistic": round(chi2, 4),
        "p_value": round(p_value, 6),
        "b": b,
        "c": c,
        "a": a_val,
        "d": d,
        "significant": p_value < 0.004,  # Bonferroni: 0.05/12
    }


def _chi2_sf(x: float, df: int = 1) -> float:
    """Survival function for chi-squared distribution (scipy-free)."""
    if x <= 0:
        return 1.0
    # Use the complementary error function approximation for df=1
    # P(X > x) = erfc(sqrt(x/2)) for chi2 with df=1
    return math.erfc(math.sqrt(x / 2))


def cohens_h(p1: float, p2: float) -> float:
    """
    Cohen's h effect size for comparing two proportions.
    
    h = 2 * arcsin(sqrt(p1)) - 2 * arcsin(sqrt(p2))
    
    Interpretation:
    |h| = 0.2: small effect
    |h| = 0.5: medium effect
    |h| = 0.8: large effect
    """
    h = 2 * math.asin(math.sqrt(p1)) - 2 * math.asin(math.sqrt(p2))
    return round(h, 4)


def bootstrap_ci(successes: list[bool], n_resamples: int = 1000, ci: float = 0.95) -> tuple:
    """Bootstrap confidence interval for a proportion."""
    if not successes:
        return (0.0, 0.0)

    rng = np.random.default_rng(seed=42)
    arr = np.array(successes, dtype=float)
    boot_means = []

    for _ in range(n_resamples):
        sample = rng.choice(arr, size=len(arr), replace=True)
        boot_means.append(sample.mean())

    alpha = (1 - ci) / 2
    lower = np.percentile(boot_means, 100 * alpha)
    upper = np.percentile(boot_means, 100 * (1 - alpha))

    return (round(float(lower), 4), round(float(upper), 4))


# ──────────────────────────────────────────────
# Pairwise Comparisons
# ──────────────────────────────────────────────


def run_pairwise_tests(rates: dict) -> list[dict]:
    """
    Run McNemar's test comparing each strategy to baseline, per model.
    
    Applies Bonferroni correction for multiple comparisons.
    """
    comparisons = []

    # Get unique models and strategies
    models = sorted(set(k[0] for k in rates.keys()))
    strategies = sorted(set(k[1] for k in rates.keys()))

    for model in models:
        baseline_key = (model, "baseline")
        if baseline_key not in rates:
            logger.warning(f"No baseline found for model: {model}")
            continue

        baseline_outcomes = rates[baseline_key]["per_task_any"]

        for strategy in strategies:
            if strategy == "baseline":
                continue

            strat_key = (model, strategy)
            if strat_key not in rates:
                continue

            strat_outcomes = rates[strat_key]["per_task_any"]

            # Ensure alignment (same tasks in same order)
            if len(baseline_outcomes) != len(strat_outcomes):
                logger.warning(
                    f"Mismatched task counts for {model}: "
                    f"baseline={len(baseline_outcomes)}, {strategy}={len(strat_outcomes)}"
                )
                continue

            # McNemar's test
            test_result = mcnemar_test(strat_outcomes, baseline_outcomes)

            # Effect size
            p_baseline = rates[baseline_key]["success_rate_any"]
            p_strategy = rates[strat_key]["success_rate_any"]
            h = cohens_h(p_strategy, p_baseline)

            # Bootstrap CIs
            ci_baseline = bootstrap_ci(baseline_outcomes)
            ci_strategy = bootstrap_ci(strat_outcomes)

            comparisons.append({
                "model": model,
                "strategy": strategy,
                "baseline_rate": round(p_baseline, 4),
                "strategy_rate": round(p_strategy, 4),
                "improvement_pp": round(p_strategy - p_baseline, 4),
                "cohens_h": h,
                "effect_size": (
                    "large" if abs(h) >= 0.8 else
                    "medium" if abs(h) >= 0.5 else
                    "small" if abs(h) >= 0.2 else
                    "negligible"
                ),
                "mcnemar_chi2": test_result["statistic"],
                "p_value": test_result["p_value"],
                "significant_bonferroni": test_result["significant"],
                "ci_baseline": ci_baseline,
                "ci_strategy": ci_strategy,
            })

    return comparisons


# ──────────────────────────────────────────────
# Report Generation
# ──────────────────────────────────────────────


def generate_report(rates: dict, comparisons: list[dict], output_dir: Path) -> None:
    """Generate summary tables and statistical test results."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Summary CSV
    csv_lines = ["model,strategy,n_tasks,success_rate_any,successes,ci_lower,ci_upper"]
    for (model, strategy), data in sorted(rates.items()):
        ci = bootstrap_ci(data["per_task_any"])
        csv_lines.append(
            f"{model},{strategy},{data['n_tasks']},"
            f"{data['success_rate_any']:.4f},{data['successes_any']},"
            f"{ci[0]:.4f},{ci[1]:.4f}"
        )
    csv_path = output_dir / "results_summary.csv"
    csv_path.write_text("\n".join(csv_lines), encoding="utf-8")
    logger.info(f"Saved: {csv_path}")

    # 2. Statistical tests markdown
    md_lines = [
        "# Statistical Test Results\n",
        f"**Generated:** {__import__('datetime').datetime.now().isoformat()}\n",
        "## Pairwise Comparisons (Strategy vs. Baseline)\n",
        "| Model | Strategy | Baseline | Strategy Rate | Δ (pp) | Cohen's h | Effect | χ² | p-value | Sig.* |",
        "|-------|----------|----------|--------------|--------|-----------|--------|-----|---------|-------|",
    ]
    for c in comparisons:
        sig = "✓" if c["significant_bonferroni"] else ""
        md_lines.append(
            f"| {c['model']} | {c['strategy']} | "
            f"{c['baseline_rate']:.1%} | {c['strategy_rate']:.1%} | "
            f"{c['improvement_pp']:+.1%} | {c['cohens_h']:.3f} | "
            f"{c['effect_size']} | {c['mcnemar_chi2']:.2f} | "
            f"{c['p_value']:.4f} | {sig} |"
        )
    md_lines.append("\n*Bonferroni-corrected threshold: α = 0.004 (0.05/12)\n")

    # Key findings
    md_lines.append("## Key Findings\n")
    if comparisons:
        best = max(comparisons, key=lambda c: c["improvement_pp"])
        md_lines.append(
            f"- **Best improvement:** {best['strategy']} on {best['model']} "
            f"({best['improvement_pp']:+.1%} pp, Cohen's h = {best['cohens_h']:.3f})\n"
        )
        sig_results = [c for c in comparisons if c["significant_bonferroni"]]
        md_lines.append(
            f"- **Statistically significant results:** {len(sig_results)} / {len(comparisons)}\n"
        )

    stats_path = output_dir / "statistical_tests.md"
    stats_path.write_text("\n".join(md_lines), encoding="utf-8")
    logger.info(f"Saved: {stats_path}")

    # 3. Raw comparisons JSON
    json_path = output_dir / "comparisons.json"
    with open(json_path, "w") as f:
        json.dump(comparisons, f, indent=2)
    logger.info(f"Saved: {json_path}")


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Analyze CyberGym experiment results"
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("data/results"),
        help="Directory containing result JSON files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis"),
        help="Output directory for analysis results",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Load results
    results = load_all_results(args.results_dir)
    if not results:
        logger.error("No results found. Run experiments first.")
        return

    # Compute success rates
    rates = compute_success_rates(results)
    logger.info(f"\nSuccess rates per condition:")
    for (model, strategy), data in sorted(rates.items()):
        logger.info(
            f"  {model:>20s} × {strategy:<25s}: "
            f"{data['success_rate_any']:.1%} "
            f"({data['successes_any']}/{data['n_tasks']})"
        )

    # Run statistical tests
    comparisons = run_pairwise_tests(rates)

    # Generate report
    generate_report(rates, comparisons, args.output)

    logger.info("\nAnalysis complete!")


if __name__ == "__main__":
    main()
