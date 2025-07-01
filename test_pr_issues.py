#!/usr/bin/env python3
"""
Test script to reproduce the specific issues mentioned in the PR description.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from main import run_task
from utils import configure_logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


async def test_git_lfs_file_issue():
    """Test the Git LFS file issue from Task 5."""
    logger.info("Testing Git LFS file issue...")

    # Create a task folder with a Git LFS pointer file
    task_dir = Path("task")
    task_dir.mkdir(exist_ok=True)

    # Create a mock Git LFS pointer file (like in the PR description)
    lfs_file = task_dir / "data.jsonld"
    lfs_content = """version https://git-lfs.github.com/spec/v1
oid sha256:8b15cca1dbf8b53a2bac6127a1d4d62f4889fca8037e9cce739569f258521549
size 2897289"""

    try:
        with open(lfs_file, "w") as f:
            f.write(lfs_content)

        task = """You need to solve the following problem:

'What is the average number of pre-2020 works on the open researcher and contributor identification pages of the people whose identification is in this file?'

Any relevant files are in the task folder."""

        answer, research = await run_task(task)

        logger.info(f"Answer: {answer}")
        logger.info(f"Research length: {len(research) if research else 0}")

        # Check if agent properly handles LFS files instead of giving up
        failure_phrases = [
            "the average cannot be calculated",
            "unable to determine",
            "cannot determine",
            "please provide",
            "file not available",
            "actual content is not available"
        ]

        has_failure = any(phrase in answer.lower() for phrase in failure_phrases)

        # Success if agent doesn't give up and tries alternative approaches
        return not has_failure

    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False
    finally:
        # Clean up
        if lfs_file.exists():
            lfs_file.unlink()
        if task_dir.exists() and not any(task_dir.iterdir()):
            task_dir.rmdir()


async def test_missing_file_issue():
    """Test the missing file issue where agent says 'Please provide the file'."""
    logger.info("Testing missing file issue...")

    # Create a task folder but with no files (simulating the issue)
    task_dir = Path("task")
    task_dir.mkdir(exist_ok=True)

    # Create only a problem.txt file
    problem_file = task_dir / "problem.txt"
    with open(problem_file, "w") as f:
        f.write("'An office held a Secret Santa gift exchange where each of its twelve employees was assigned one other employee in the group to present with a gift. Each employee filled out a profile including three likes or hobbies. On the day of the gift exchange, only eleven gifts were given, each one specific to one of the recipient's interests. Based on the information in the document, who did not give a gift?'")

    task = """You need to solve the following problem:

'An office held a Secret Santa gift exchange where each of its twelve employees was assigned one other employee in the group to present with a gift. Each employee filled out a profile including three likes or hobbies. On the day of the gift exchange, only eleven gifts were given, each one specific to one of the recipient's interests. Based on the information in the document, who did not give a gift?'

Any relevant files are in the task folder."""

    try:
        answer, research = await run_task(task)

        logger.info(f"Answer: {answer}")

        # Check if agent gives up with "Please provide the file"
        failure_phrases = [
            "please provide the file",
            "please provide",
            "file not found",
            "cannot access",
            "unable to determine",
            "cannot determine"
        ]

        has_failure = any(phrase in answer.lower() for phrase in failure_phrases)

        # Success if agent doesn't give up and tries alternative approaches
        return not has_failure

    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False
    finally:
        # Clean up
        if problem_file.exists():
            problem_file.unlink()
        if task_dir.exists() and not any(task_dir.iterdir()):
            task_dir.rmdir()


async def test_complex_file_discovery():
    """Test complex file discovery where files have unexpected names."""
    logger.info("Testing complex file discovery...")

    # Create a task folder with files that have unexpected names
    task_dir = Path("task")
    task_dir.mkdir(exist_ok=True)

    # Create a data file with an unexpected name
    data_file = task_dir / "data.xlsx"  # Excel file that needs special handling
    # Create a mock Excel file content (actually just text for testing)
    with open(data_file, "w") as f:
        f.write("Mock Excel file content - requires code interpreter")

    task = """You need to solve the following problem:

'Each cell in the attached spreadsheet represents a plot of land. The color of the cell indicates who owns that plot. Green cells are plots owned by Earl Smith. Can Earl walk through every plot he owns (and no other plots) and return to his starting plot without backtracking? For this question, consider backtracking to be any instance where Earl would enter a plot of land he had already entered since leaving his starting plot.'

Any relevant files are in the task folder."""

    try:
        answer, research = await run_task(task)

        logger.info(f"Answer: {answer}")

        # Check if agent properly handles Excel files
        handles_excel = ("code interpreter" in research.lower() or
                        "excel" in research.lower() or
                        "spreadsheet" in research.lower())

        failure_phrases = [
            "unable to determine",
            "cannot determine",
            "file not provided",
            "necessary file was not provided"
        ]

        has_failure = any(phrase in answer.lower() for phrase in failure_phrases)

        # Success if agent recognizes Excel file and doesn't give up
        return handles_excel and not has_failure

    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False
    finally:
        # Clean up
        if data_file.exists():
            data_file.unlink()
        if task_dir.exists() and not any(task_dir.iterdir()):
            task_dir.rmdir()


async def test_timeout_issue():
    """Test timeout issue where agent takes too long."""
    logger.info("Testing timeout issue...")

    # Test with a complex question that might cause timeout
    task = """You need to solve the following problem:

'In the NCATS PubChem compound database for Food Additive Status classification, find the compound that has a molecular weight of 100 g/mol or less, 6 heavy atoms, 1 or fewer hydrogen bond acceptors, and a complexity between 10 and 15. Of the shared gene-chemical co-occurrences between its two possible enzyme transformations, what is the PubChem CID of the heaviest by molecular weight?'

Any relevant files are in the task folder."""

    try:
        import time
        start_time = time.time()

        answer, research = await run_task(task)

        end_time = time.time()
        duration = end_time - start_time

        logger.info(f"Answer: {answer}")
        logger.info(f"Duration: {duration:.2f} seconds")

        # Check if agent provides a meaningful answer within reasonable time
        has_meaningful_answer = (answer is not None and
                               len(answer.strip()) > 3 and
                               "unable" not in answer.lower())

        reasonable_time = duration < 300  # Less than 5 minutes

        return has_meaningful_answer and reasonable_time

    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


async def main():
    """Run PR issue reproduction tests."""
    configure_logging()
    logger.info("🔍 Testing specific PR issues\n")

    if not os.getenv("OPENAI_API_KEY"):
        logger.error("❌ No OPENAI_API_KEY found. Cannot run tests.")
        return False

    tests = [
        ("Git LFS File Issue", test_git_lfs_file_issue),
        ("Missing File Issue", test_missing_file_issue),
        ("Complex File Discovery", test_complex_file_discovery),
        ("Timeout Issue", test_timeout_issue),
    ]

    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n{'='*60}")
        logger.info(f"Running {test_name} test...")
        logger.info(f"{'='*60}")

        try:
            result = await test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
        except Exception as e:
            logger.error(f"{test_name}: ❌ ERROR - {e}")
            results[test_name] = False

    logger.info(f"\n{'='*60}")
    logger.info("PR ISSUE TEST SUMMARY")
    logger.info(f"{'='*60}")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")

    logger.info(f"\nOverall: {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)