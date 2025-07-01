#!/usr/bin/env python3
"""
Script to reproduce the issues identified in the PR description.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from utils import configure_logging
from main import run_task

logger = logging.getLogger(__name__)

async def test_formatting_issues():
    """Test cases that demonstrate formatting issues."""
    logger.info("Testing formatting issues...")

    # Test case 1: Should return just "6" not "6 cups"
    task1 = """Use density measures from the chemistry materials licensed by Marisa Alviar-Agnew & Henry Agnew under the CK-12 license in LibreText's Introductory Chemistry materials as compiled 08/21/2023.

I have a gallon of honey and a gallon of mayonnaise at 25C. I remove one cup of honey at a time from the gallon of honey. How many times will I need to remove a cup to have the honey weigh less than the mayonaise? Assume the containers themselves weigh the same."""

    logger.info(f"Task 1: {task1[:100]}...")
    try:
        answer, _ = await run_task(task1)
        logger.info(f"Answer: '{answer}'")
        logger.info(f"Expected: '6' (just the number)")
        logger.info(f"Issue: Answer includes extra text/units")
    except Exception as e:
        logger.error(f"Error: {e}")

    # Test case 2: Should return "2" not "Two"
    task2 = """What is the minimum number of page links a person must click on to go from the english Wikipedia page on The Lord of the Rings (the book) to the english Wikipedia page on A Song of Ice and Fire (the book series)? In your count, include each link you would click on to get to the page. Use the pages as they appeared at the end of the day on July 3, 2023."""

    logger.info(f"\nTask 2: {task2[:100]}...")
    try:
        answer, _ = await run_task(task2)
        logger.info(f"Answer: '{answer}'")
        logger.info(f"Expected: '2' (numeral not word)")
        logger.info(f"Issue: Answer uses word instead of numeral")
    except Exception as e:
        logger.error(f"Error: {e}")

async def test_early_termination():
    """Test cases that demonstrate early termination issues."""
    logger.info("\nTesting early termination issues...")

    # Test case: Missing file should not cause immediate termination
    task = """How many applicants for the job in the PDF are only missing a single qualification?"""

    logger.info(f"Task: {task}")
    try:
        answer, _ = await run_task(task)
        logger.info(f"Answer: '{answer}'")
        logger.info(f"Issue: Should try alternative approaches instead of giving up")
    except Exception as e:
        logger.error(f"Error: {e}")

async def main():
    """Run all reproduction tests."""
    configure_logging()
    load_dotenv()

    logger.info("🧪 Reproducing issues from PR description\n")

    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not found. Please set it to run tests.")
        return

    await test_formatting_issues()
    await test_early_termination()

    logger.info("\n✅ Issue reproduction complete!")

if __name__ == "__main__":
    asyncio.run(main())