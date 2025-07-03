#!/usr/bin/env python3
"""
Evaluate the GAIA agent on the validation set.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

from main import run_task
from utils import configure_logging

logger = logging.getLogger(__name__)


def load_validation_tasks(metadata_path: Path) -> List[Dict]:
    """Load validation tasks from metadata.jsonl file."""
    tasks = []

    with open(metadata_path, "r") as f:
        for line in f:
            try:
                task = json.loads(line.strip())
                tasks.append(task)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing line: {e}")
                continue

    logger.info(f"Loaded {len(tasks)} tasks from {metadata_path}")
    return tasks


async def evaluate_task(task: Dict, data_dir: Path) -> Dict:
    """Evaluate a single task."""
    task_id = task.get("task_id", "unknown")
    question = task.get("Question", "")
    file_name = task.get("file_name", "")
    expected_answer = task.get("Final answer", "")
    level = task.get("Level", 0)

    logger.info(f"\n{'=' * 80}")
    logger.info(f"Task ID: {task_id}")
    logger.info(f"Level: {level}")
    logger.info(
        f"Question: {question[:100]}..."
        if len(question) > 100
        else f"Question: {question}"
    )
    logger.info(f"Expected answer: {expected_answer}")

    # Prepare the file path if a file is associated with the task
    file_path = None
    if file_name:
        file_path = data_dir / file_name
        if file_path.exists():
            logger.info(f"Associated file: {file_path}")
        else:
            logger.warning(f"File not found: {file_path}")
            file_path = None

    # Run the task
    try:
        final_answer, research_output = await run_task(question, file_path)

        result = {
            "task_id": task_id,
            "level": level,
            "question": question,
            "expected_answer": expected_answer,
            "predicted_answer": final_answer,
            "file_path": str(file_path) if file_path else None,
            "success": final_answer is not None,
            "research_output_length": len(research_output) if research_output else 0,
        }

        logger.info(f"Predicted answer: {final_answer}")
        logger.info(
            f"Match: {final_answer == expected_answer}"
            if final_answer
            else "Failed to generate answer"
        )

    except Exception as e:
        logger.error(f"Error evaluating task {task_id}: {e}")
        result = {
            "task_id": task_id,
            "level": level,
            "question": question,
            "expected_answer": expected_answer,
            "predicted_answer": None,
            "file_path": str(file_path) if file_path else None,
            "success": False,
            "error": str(e),
        }

    return result


async def evaluate_all(
    tasks: List[Dict], data_dir: Path, results_dir: Path, limit: Optional[int] = None
) -> List[Dict]:
    """Evaluate all tasks."""
    if limit:
        tasks = tasks[:limit]
        logger.info(f"Limited to first {limit} tasks")

    results = []
    for i, task in enumerate(tasks, 1):
        logger.info(f"\nProcessing task {i}/{len(tasks)}")
        result = await evaluate_task(task, data_dir)
        results.append(result)

        # Save intermediate results
        with open(results_dir / "evaluation_results.jsonl", "a") as f:
            f.write(json.dumps(result) + "\n")

    return results


def print_summary(results: List[Dict]):
    """Print evaluation summary."""
    total = len(results)
    successful = sum(1 for r in results if r["success"])
    correct = sum(
        1 for r in results if r.get("predicted_answer") == r.get("expected_answer")
    )

    logger.info(f"\n{'=' * 80}")
    logger.info("EVALUATION SUMMARY")
    logger.info(f"{'=' * 80}")
    logger.info(f"Total tasks: {total}")
    logger.info(
        f"Successful completions: {successful} ({successful / total * 100:.1f}%)"
    )
    logger.info(f"Correct answers: {correct} ({correct / total * 100:.1f}%)")

    # Break down by level
    by_level = {}
    for r in results:
        level = r["level"]
        if level not in by_level:
            by_level[level] = {"total": 0, "success": 0, "correct": 0}
        by_level[level]["total"] += 1
        if r["success"]:
            by_level[level]["success"] += 1
        if r.get("predicted_answer") == r.get("expected_answer"):
            by_level[level]["correct"] += 1

    logger.info("\nBy difficulty level:")
    for level in sorted(by_level.keys()):
        stats = by_level[level]
        logger.info(
            f"  Level {level}: {stats['correct']}/{stats['total']} correct "
            f"({stats['correct'] / stats['total'] * 100:.1f}%)"
        )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Evaluate GAIA agent on validation set"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="gaia/files/2023/validation",
        help="Path to the GAIA validation data directory",
    )
    parser.add_argument(
        "--limit", type=int, help="Limit the number of tasks to evaluate"
    )
    parser.add_argument(
        "--task-ids",
        type=str,
        nargs="+",
        help="Evaluate only specific task IDs (space-separated list)",
    )
    parser.add_argument(
        "--level",
        type=int,
        choices=[1, 2, 3],
        help="Evaluate only tasks of a specific difficulty level",
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default="results",
        help="Path to the results directory",
    )

    args = parser.parse_args()

    configure_logging()

    data_dir = Path(args.data_dir)
    metadata_path = data_dir / "metadata.jsonl"
    results_dir = Path(args.results_dir)

    # Create results directory if it doesn't exist
    results_dir.mkdir(parents=True, exist_ok=True)

    if not metadata_path.exists():
        logger.error(f"Metadata file not found: {metadata_path}")
        sys.exit(1)

    tasks = load_validation_tasks(metadata_path)

    if args.task_ids:
        requested_task_ids = set(args.task_ids)
        tasks = [t for t in tasks if t.get("task_id") in requested_task_ids]
        found_task_ids = set(
            t.get("task_id") for t in tasks if t.get("task_id") is not None
        )

        if not tasks:
            logger.error(f"No tasks found for the provided task IDs: {args.task_ids}")
            sys.exit(1)

        # Check if any requested task IDs were not found
        missing_task_ids = requested_task_ids - found_task_ids
        if missing_task_ids:
            logger.warning(f"Task IDs not found: {sorted(list(missing_task_ids))}")

        logger.info(
            f"Filtered to {len(tasks)} tasks from task IDs: {sorted(found_task_ids)}"
        )

    if args.level:
        tasks = [t for t in tasks if t.get("Level") == args.level]
        logger.info(f"Filtered to {len(tasks)} tasks of level {args.level}")

    # Clear previous results file if starting fresh
    if not args.task_ids and os.path.exists(results_dir / "evaluation_results.jsonl"):
        os.remove(results_dir / "evaluation_results.jsonl")

    # Run evaluation
    results = asyncio.run(evaluate_all(tasks, data_dir, results_dir, args.limit))
    print_summary(results)

    # Save final summary
    summary = {
        "total_tasks": len(results),
        "successful": sum(1 for r in results if r["success"]),
        "correct": sum(
            1 for r in results if r.get("predicted_answer") == r.get("expected_answer")
        ),
        "results": results,
    }

    with open(results_dir / "evaluation_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    logger.info(
        f"\nResults saved to {results_dir}/evaluation_results.jsonl and {results_dir}/evaluation_summary.json"
    )


if __name__ == "__main__":
    main()
