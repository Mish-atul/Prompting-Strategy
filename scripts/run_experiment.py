#!/usr/bin/env python3
"""
run_experiment.py — Batch experiment orchestrator for CyberGym prompt engineering study.

Runs the OpenHands agent with a specified prompt strategy and model backend
across all tasks in the filtered subset, with configurable repetitions.

This script modifies only the prompt.txt file passed to the OpenHands agent —
no changes are made to the agent framework itself.

Usage:
    # Run baseline with DeepSeek-V3 on all tasks, 3 repetitions
    python scripts/run_experiment.py \
        --strategy baseline \
        --model deepseek-v3 \
        --task-subset data/task_subset.json \
        --reps 3 \
        --cybergym-dir ./cybergym \
        --data-dir ./cybergym_data/data \
        --server http://localhost:8666

    # Run all strategies with a specific model
    python scripts/run_experiment.py \
        --strategy all \
        --model deepseek-v3 \
        --task-subset data/task_subset.json \
        --reps 3
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add parent to path for utils import
sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    STRATEGY_NAMES,
    ExperimentResult,
    get_model_config,
    load_prompt,
    load_task_subset,
    get_result_path,
    save_json,
    setup_logging,
)

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Core Experiment Runner
# ──────────────────────────────────────────────


def run_single_task(
    task_id: str,
    strategy: str,
    model_name: str,
    rep: int,
    cybergym_dir: Path,
    data_dir: Path,
    server: str,
    results_dir: Path,
    timeout: int = 1200,
    max_iter: int = 100,
    difficulty: str = "level1",
    dry_run: bool = False,
) -> ExperimentResult:
    """
    Run a single CyberGym task with a specific prompt strategy and model.
    
    This function:
    1. Generates the CyberGym task directory
    2. Replaces the prompt.txt with the selected strategy's prompt
    3. Invokes the OpenHands agent via the CyberGym runner
    4. Records the outcome
    """
    model_config = get_model_config(model_name)
    prompt_text = load_prompt(strategy)

    logger.info(
        f"[{task_id}] strategy={strategy} model={model_name} rep={rep}"
    )

    # Check if result already exists (resume support)
    result_path = get_result_path(results_dir, strategy, task_id, model_name, rep)
    if result_path.exists():
        logger.info(f"  → Result already exists, skipping: {result_path}")
        with open(result_path) as f:
            return ExperimentResult.from_dict(json.load(f))

    if dry_run:
        logger.info(f"  → DRY RUN: would run {task_id} with {strategy}/{model_name}")
        return ExperimentResult(
            task_id=task_id,
            strategy=strategy,
            model=model_name,
            repetition=rep,
            success=False,
            error="dry_run",
        )

    start_time = time.time()

    try:
        # Build the command to invoke the OpenHands agent
        # This follows the pattern from cybergym-agent-examples/openhands/run.py
        cmd = [
            sys.executable,
            str(cybergym_dir / "examples" / "agents" / "openhands" / "run.py"),
            "--task_id", task_id,
            "--data_dir", str(data_dir),
            "--server", server,
            "--difficulty", difficulty,
            "--llm.model", _map_model_id(model_name, model_config),
            "--llm.api_key", _get_api_key_safe(model_config),
            "--llm.base_url", model_config.api_base,
            "--llm.temperature", str(model_config.temperature),
            "--llm.top_p", str(model_config.top_p),
            "--llm.max_output_tokens", str(model_config.max_output_tokens),
            "--log_dir", str(results_dir / strategy / "logs"),
            "--tmp_dir", str(results_dir / strategy / "tmp"),
            "--timeout", str(timeout),
            "--max_iter", str(max_iter),
            "--silent", "true",
        ]

        # Set up environment with API key
        env = os.environ.copy()
        if model_config.env_key and os.getenv(model_config.env_key):
            env["LLM_API_KEY"] = os.getenv(model_config.env_key)

        # Inject custom prompt: we modify the template prompt.txt
        # The OpenHands runner reads from template/prompt.txt
        template_dir = cybergym_dir / "examples" / "agents" / "openhands" / "template"
        prompt_file = template_dir / "prompt.txt"

        # Backup original prompt
        backup_path = template_dir / "prompt.txt.backup"
        if not backup_path.exists() and prompt_file.exists():
            shutil.copy2(prompt_file, backup_path)

        # Write our strategy prompt
        prompt_file.write_text(prompt_text, encoding="utf-8")

        logger.info(f"  → Injected {strategy} prompt ({len(prompt_text)} chars)")
        logger.info(f"  → Running agent (timeout={timeout}s, max_iter={max_iter})")

        # Execute
        proc = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout + 60,  # Extra buffer beyond agent timeout
        )

        elapsed = time.time() - start_time

        # Parse result
        success = _check_success(proc, results_dir / strategy / "logs", task_id)

        result = ExperimentResult(
            task_id=task_id,
            strategy=strategy,
            model=model_name,
            repetition=rep,
            success=success,
            runtime_seconds=round(elapsed, 2),
            error=proc.stderr[:500] if proc.returncode != 0 else None,
        )

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        result = ExperimentResult(
            task_id=task_id,
            strategy=strategy,
            model=model_name,
            repetition=rep,
            success=False,
            runtime_seconds=round(elapsed, 2),
            error="timeout",
        )
        logger.warning(f"  → TIMEOUT after {elapsed:.0f}s")

    except Exception as e:
        elapsed = time.time() - start_time
        result = ExperimentResult(
            task_id=task_id,
            strategy=strategy,
            model=model_name,
            repetition=rep,
            success=False,
            runtime_seconds=round(elapsed, 2),
            error=str(e)[:500],
        )
        logger.error(f"  → ERROR: {e}")

    finally:
        # Restore original prompt
        if backup_path.exists():
            shutil.copy2(backup_path, prompt_file)

    # Save result
    save_json(result.to_dict(), result_path)
    status = "✓ SUCCESS" if result.success else "✗ FAIL"
    logger.info(f"  → {status} ({result.runtime_seconds:.0f}s)")

    return result


def _map_model_id(model_name: str, config) -> str:
    """Map our model name to OpenHands-compatible model identifier."""
    mapping = {
        "deepseek-v3": "deepseek/deepseek-chat",
        "llama-3.3-70b": "groq/llama-3.3-70b-versatile",
        "qwen2.5-coder-32b": "ollama/qwen2.5-coder:32b",
    }
    return mapping.get(model_name, config.model_id)


def _get_api_key_safe(config) -> str:
    """Get API key, returning 'EMPTY' for local models."""
    if config.env_key is None:
        return "EMPTY"
    return os.getenv(config.env_key, "EMPTY")


def _check_success(proc, log_dir: Path, task_id: str) -> bool:
    """
    Determine if the agent successfully triggered the vulnerability.
    
    Success = PoC caused crash in pre-patch (exit_code != 0) 
              AND no crash in post-patch (exit_code == 0).
    
    This is checked by the CyberGym submission server.
    """
    # Look for success indicators in output
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    combined = stdout + stderr

    # The CyberGym server returns JSON with exit codes
    # A successful submission shows exit_code != 0 for pre-patch
    if '"exit_code": 1' in combined or "exit_code" not in combined:
        # Also check log files if available
        pass

    # Conservative: check if any "pass" or "success" indicators exist
    success_indicators = [
        "crash triggered",
        "vulnerability reproduced",
        "exit_code\": 1",  # non-zero exit = crash
    ]

    return any(indicator in combined.lower() for indicator in success_indicators)


# ──────────────────────────────────────────────
# Batch Runner
# ──────────────────────────────────────────────


def run_batch(
    strategies: list[str],
    model_name: str,
    task_subset: list[dict],
    reps: int,
    cybergym_dir: Path,
    data_dir: Path,
    server: str,
    results_dir: Path,
    timeout: int = 1200,
    max_iter: int = 100,
    dry_run: bool = False,
) -> list[ExperimentResult]:
    """Run all experiments for given strategies, model, tasks, and repetitions."""

    total_runs = len(strategies) * len(task_subset) * reps
    logger.info(
        f"\n{'='*60}\n"
        f"EXPERIMENT BATCH\n"
        f"  Strategies: {strategies}\n"
        f"  Model: {model_name}\n"
        f"  Tasks: {len(task_subset)}\n"
        f"  Repetitions: {reps}\n"
        f"  Total runs: {total_runs}\n"
        f"{'='*60}\n"
    )

    results = []
    completed = 0

    for strategy in strategies:
        for task in task_subset:
            task_id = task["task_id"]
            for rep in range(1, reps + 1):
                completed += 1
                logger.info(f"\n[{completed}/{total_runs}]")

                result = run_single_task(
                    task_id=task_id,
                    strategy=strategy,
                    model_name=model_name,
                    rep=rep,
                    cybergym_dir=cybergym_dir,
                    data_dir=data_dir,
                    server=server,
                    results_dir=results_dir,
                    timeout=timeout,
                    max_iter=max_iter,
                    dry_run=dry_run,
                )
                results.append(result)

    # Summary
    successes = sum(1 for r in results if r.success)
    logger.info(
        f"\n{'='*60}\n"
        f"BATCH COMPLETE\n"
        f"  Total runs: {len(results)}\n"
        f"  Successes: {successes} ({100*successes/len(results):.1f}%)\n"
        f"  Failures: {len(results) - successes}\n"
        f"{'='*60}\n"
    )

    return results


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Run CyberGym prompt engineering experiments"
    )
    parser.add_argument(
        "--strategy",
        type=str,
        required=True,
        help=f"Prompt strategy to use. Options: {STRATEGY_NAMES + ['all']}",
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Model backend: deepseek-v3, llama-3.3-70b, qwen2.5-coder-32b",
    )
    parser.add_argument(
        "--task-subset",
        type=Path,
        default=Path("data/task_subset.json"),
        help="Path to filtered task subset JSON",
    )
    parser.add_argument(
        "--reps",
        type=int,
        default=3,
        help="Number of repetitions per task (default: 3)",
    )
    parser.add_argument(
        "--cybergym-dir",
        type=Path,
        default=Path("./cybergym"),
        help="Path to cloned CyberGym repository",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("./cybergym_data/data"),
        help="Path to CyberGym data directory",
    )
    parser.add_argument(
        "--server",
        type=str,
        default="http://localhost:8666",
        help="CyberGym submission server URL",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("data/results"),
        help="Directory to save results",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1200,
        help="Agent timeout in seconds (default: 1200)",
    )
    parser.add_argument(
        "--max-iter",
        type=int,
        default=100,
        help="Maximum agent iterations (default: 100)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be run without executing",
    )
    args = parser.parse_args()

    setup_logging()

    # Determine strategies to run
    if args.strategy == "all":
        strategies = STRATEGY_NAMES
    else:
        strategies = [args.strategy]

    # Load task subset
    tasks = load_task_subset(args.task_subset)
    logger.info(f"Loaded {len(tasks)} tasks from {args.task_subset}")

    # Run
    run_batch(
        strategies=strategies,
        model_name=args.model,
        task_subset=tasks,
        reps=args.reps,
        cybergym_dir=args.cybergym_dir,
        data_dir=args.data_dir,
        server=args.server,
        results_dir=args.results_dir,
        timeout=args.timeout,
        max_iter=args.max_iter,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
