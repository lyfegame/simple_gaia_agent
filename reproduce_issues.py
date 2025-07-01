#!/usr/bin/env python3
"""
Script to reproduce the specific issues mentioned in the PR description.
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


async def test_file_discovery_issue():
    """Reproduce the file discovery issue from Task 1."""
    logger.info("Testing file discovery issue...")

    # Create a task folder with a file (simulating the GAIA setup)
    task_dir = Path("task")
    task_dir.mkdir(exist_ok=True)

    # Create a data file with Secret Santa information (different name than expected)
    data_file = task_dir / "secret_santa_data.csv"
    with open(data_file, "w") as f:
        f.write("Employee,Gift_Given,Gift_Received\n")
        f.write("Alice,Yes,Book\n")
        f.write("Bob,Yes,Watch\n")
        f.write("Charlie,No,None\n")
        f.write("Diana,Yes,Flowers\n")
        f.write("Eve,Yes,Chocolates\n")
        f.write("Frank,Yes,Coffee Mug\n")
        f.write("Grace,Yes,Plant\n")
        f.write("Henry,Yes,Notebook\n")
        f.write("Iris,Yes,Candle\n")
        f.write("Jack,Yes,Pen Set\n")
        f.write("Kate,Yes,Tea\n")
        f.write("Leo,No,None\n")

    task = """You need to solve the following problem:

'An office held a Secret Santa gift exchange where each of its twelve employees was assigned one other employee in the group to present with a gift. Each employee filled out a profile including three likes or hobbies. On the day of the gift exchange, only eleven gifts were given, each one specific to one of the recipient's interests. Based on the information in the document, who did not give a gift?'

Any relevant files are in the task folder."""

    try:
        answer, research = await run_task(task)
        logger.info(f"Answer: {answer}")

        # Check if the agent found the file and gave a proper answer
        # The correct answer should be "Charlie" or "Leo" (both didn't give gifts)
        success = (answer is not None and
                  "please provide" not in answer.lower() and
                  "unable to determine" not in answer.lower() and
                  "missing" not in answer.lower() and
                  "cannot determine" not in answer.lower() and
                  ("charlie" in answer.lower() or "leo" in answer.lower()) and
                  len(answer.strip()) > 3)

        return success

    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False
    finally:
        # Clean up
        if data_file.exists():
            data_file.unlink()
        if task_dir.exists() and not any(task_dir.iterdir()):
            task_dir.rmdir()


async def test_giving_up_too_early():
    """Test that agent doesn't give up with 'Unable to determine'."""
    logger.info("Testing giving up too early issue...")

    task = "What is the current population of New York City?"
    try:
        answer, research = await run_task(task)
        logger.info(f"Answer: {answer}")

        # Check that agent doesn't give up
        failure_phrases = [
            "unable to determine",
            "cannot find",
            "no information available",
            "please provide",
            "cannot determine",
            "information not found"
        ]

        has_failure_phrase = any(phrase in answer.lower() for phrase in failure_phrases)
        has_meaningful_content = len(answer.strip()) > 5
        has_number = any(char.isdigit() for char in answer)

        # Success if no failure phrases AND has meaningful content AND contains numbers
        return not has_failure_phrase and has_meaningful_content and has_number

    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


async def main():
    """Run reproduction tests."""
    configure_logging()
    logger.info("🔍 Reproducing issues from PR description\n")

    if not os.getenv("OPENAI_API_KEY"):
        logger.error("❌ No OPENAI_API_KEY found. Cannot run tests.")
        return False

    tests = [
        ("File Discovery Issue", test_file_discovery_issue),
        ("Giving Up Too Early", test_giving_up_too_early),
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
    logger.info("REPRODUCTION TEST SUMMARY")
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