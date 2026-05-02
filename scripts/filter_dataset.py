#!/usr/bin/env python3
"""
filter_dataset.py — Filter CyberGym tasks.json to Heap-buffer-overflow READ instances.

Applies two-stage filtering:
1. Vulnerability type = "Heap-buffer-overflow" AND access type = "READ"
2. Ground-truth PoC size < 100 bytes (maximizes baseline signal per paper Figure 7)

Outputs a stratified subset of ~100 instances balanced across source projects.

Usage:
    python scripts/filter_dataset.py \
        --tasks-file ./cybergym_data/tasks.json \
        --output data/task_subset.json \
        --max-poc-size 100 \
        --target-count 100
"""

import argparse
import json
import logging
import random
from collections import Counter, defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)


def load_tasks(tasks_file: Path) -> list[dict]:
    """Load the CyberGym tasks.json file."""
    with open(tasks_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle both list format and dict-with-key format
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # Try common keys
        for key in ["tasks", "data", "instances"]:
            if key in data:
                return data[key]
        # If dict of task_id -> task_data
        return [{"task_id": k, **v} for k, v in data.items()]

    raise ValueError(f"Unexpected tasks.json format: {type(data)}")


def filter_hbo_read(tasks: list[dict], max_poc_size: int = 100) -> list[dict]:
    """
    Filter tasks to Heap-buffer-overflow READ with small PoCs.
    
    Attempts to identify HBO-READ instances using various field names
    that CyberGym might use in its task metadata.
    """
    filtered = []

    for task in tasks:
        # Extract vulnerability type — try multiple possible field names
        vuln_type = (
            task.get("vulnerability_type", "")
            or task.get("vuln_type", "")
            or task.get("sanitizer_type", "")
            or task.get("type", "")
            or task.get("bug_type", "")
        ).lower()

        # Check for heap-buffer-overflow
        is_hbo = any(
            pattern in vuln_type
            for pattern in [
                "heap-buffer-overflow",
                "heap_buffer_overflow",
                "heap buffer overflow",
            ]
        )

        if not is_hbo:
            continue

        # Check for READ access type
        access = (
            task.get("access_type", "")
            or task.get("access", "")
            or task.get("operation", "")
        ).upper()

        # Also check if "READ" appears in the vulnerability type string
        is_read = "READ" in access or "READ" in vuln_type.upper()

        if not is_read:
            continue

        # Check PoC size if available
        poc_size = task.get("poc_size", task.get("poc_size_bytes", None))
        if poc_size is not None and poc_size > max_poc_size:
            continue

        # Extract project name
        project = (
            task.get("project", "")
            or task.get("project_name", "")
            or task.get("target", "")
            or "unknown"
        )

        filtered.append({
            "task_id": task.get("task_id", task.get("id", "")),
            "project": project,
            "vulnerability_type": "Heap-buffer-overflow",
            "access_type": "READ",
            "poc_size_bytes": poc_size,
            "description_preview": str(
                task.get("description", task.get("vuln_description", ""))
            )[:200],
            "_original": task,  # Keep original for reference
        })

    return filtered


def stratified_sample(
    tasks: list[dict], target_count: int, max_per_project: float = 0.15
) -> list[dict]:
    """
    Create a stratified sample balanced across projects.
    
    No single project contributes more than max_per_project fraction.
    """
    if len(tasks) <= target_count:
        logger.info(
            f"Available tasks ({len(tasks)}) <= target ({target_count}). "
            "Using all available tasks."
        )
        return tasks

    # Group by project
    by_project = defaultdict(list)
    for task in tasks:
        by_project[task["project"]].append(task)

    # Calculate max per project
    max_count = int(target_count * max_per_project)

    # First pass: cap each project
    selected = []
    remaining = []
    for project, project_tasks in by_project.items():
        random.shuffle(project_tasks)
        selected.extend(project_tasks[:max_count])
        remaining.extend(project_tasks[max_count:])

    # If we have too many, subsample
    if len(selected) > target_count:
        random.shuffle(selected)
        selected = selected[:target_count]

    # If we need more, draw from remaining
    if len(selected) < target_count:
        needed = target_count - len(selected)
        random.shuffle(remaining)
        selected.extend(remaining[:needed])

    return selected


def main():
    parser = argparse.ArgumentParser(
        description="Filter CyberGym dataset to HBO-READ subset"
    )
    parser.add_argument(
        "--tasks-file",
        type=Path,
        required=True,
        help="Path to CyberGym tasks.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/task_subset.json"),
        help="Output path for filtered subset",
    )
    parser.add_argument(
        "--max-poc-size",
        type=int,
        default=100,
        help="Maximum ground-truth PoC size in bytes (default: 100)",
    )
    parser.add_argument(
        "--target-count",
        type=int,
        default=100,
        help="Target number of instances in subset (default: 100)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible sampling",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Set random seed
    random.seed(args.seed)

    # Load
    logger.info(f"Loading tasks from: {args.tasks_file}")
    all_tasks = load_tasks(args.tasks_file)
    logger.info(f"Total tasks loaded: {len(all_tasks)}")

    # Filter
    hbo_read = filter_hbo_read(all_tasks, max_poc_size=args.max_poc_size)
    logger.info(f"HBO-READ tasks (PoC < {args.max_poc_size}B): {len(hbo_read)}")

    if not hbo_read:
        logger.warning(
            "No HBO-READ tasks found! Check if tasks.json field names match "
            "expected format. Dumping first task's keys for debugging:"
        )
        if all_tasks:
            logger.info(f"Sample task keys: {list(all_tasks[0].keys())}")
        return

    # Project distribution
    project_counts = Counter(t["project"] for t in hbo_read)
    logger.info(f"Projects represented: {len(project_counts)}")
    for proj, count in project_counts.most_common(10):
        logger.info(f"  {proj}: {count} tasks")

    # Stratified sample
    subset = stratified_sample(hbo_read, args.target_count)
    logger.info(f"Final subset size: {len(subset)}")

    # Remove _original before saving
    for task in subset:
        task.pop("_original", None)

    # Save
    output = {
        "metadata": {
            "source": str(args.tasks_file),
            "filter_criteria": {
                "vulnerability_type": "Heap-buffer-overflow",
                "access_type": "READ",
                "max_poc_size_bytes": args.max_poc_size,
            },
            "total_before_filter": len(all_tasks),
            "total_after_filter": len(hbo_read),
            "subset_size": len(subset),
            "seed": args.seed,
            "created": __import__("datetime").datetime.now().isoformat(),
        },
        "tasks": subset,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    logger.info(f"Saved subset to: {args.output}")

    # Summary
    final_projects = Counter(t["project"] for t in subset)
    logger.info(f"\nFinal subset summary:")
    logger.info(f"  Tasks: {len(subset)}")
    logger.info(f"  Projects: {len(final_projects)}")
    for proj, count in final_projects.most_common():
        pct = 100 * count / len(subset)
        logger.info(f"    {proj}: {count} ({pct:.1f}%)")


if __name__ == "__main__":
    main()
