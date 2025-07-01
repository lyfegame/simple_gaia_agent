#!/usr/bin/env python3
"""
Test script to reproduce the issues mentioned in the PR description.
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


async def test_file_access():
    """Test if the agent can access and read files properly."""
    logger.info("Testing file access...")

    # Test with a simple file that exists
    test_file = Path("README.md")
    if test_file.exists():
        task = f"What is the main purpose of this project based on the README.md file?"
        try:
            answer, research = await run_task(task, str(test_file))
            logger.info(f"File access test result: {answer}")
            # Check if the agent actually read the file and provided meaningful content
            return (answer is not None and
                    "unable" not in answer.lower() and
                    "cannot determine" not in answer.lower() and
                    "please upload" not in answer.lower() and
                    "please provide" not in answer.lower() and
                    len(answer.strip()) > 10)  # Should have substantial content
        except Exception as e:
            logger.error(f"File access test failed: {e}")
            return False
    else:
        logger.warning("README.md not found, skipping file access test")
        return True


async def test_information_extraction():
    """Test if the agent can extract specific information."""
    logger.info("Testing information extraction...")

    # Test with a simple web search task
    task = "What is the capital of France?"
    try:
        answer, research = await run_task(task)
        logger.info(f"Information extraction test result: {answer}")
        # Check if the answer contains "Paris" and is not saying "unable"
        return (answer is not None and
                "paris" in answer.lower() and
                "unable" not in answer.lower() and
                "no information" not in answer.lower())
    except Exception as e:
        logger.error(f"Information extraction test failed: {e}")
        return False


async def test_research_thoroughness():
    """Test if the agent conducts thorough research."""
    logger.info("Testing research thoroughness...")

    # Test with a task that requires multiple sources
    task = "What is the population of Tokyo as of 2023?"
    try:
        answer, research = await run_task(task)
        logger.info(f"Research thoroughness test result: {answer}")
        logger.info(f"Research length: {len(research) if research else 0} characters")

        # Check if research was conducted and answer is specific
        return (answer is not None and
                research is not None and
                len(research) > 100 and
                "unable" not in answer.lower() and
                "no information" not in answer.lower())
    except Exception as e:
        logger.error(f"Research thoroughness test failed: {e}")
        return False


async def main():
    """Run all tests to identify issues."""
    configure_logging()
    logger.info("🧪 Running issue reproduction tests\n")

    if not os.getenv("OPENAI_API_KEY"):
        logger.error("❌ No OPENAI_API_KEY found. Cannot run tests.")
        return False

    tests = [
        ("File Access", test_file_access),
        ("Information Extraction", test_information_extraction),
        ("Research Thoroughness", test_research_thoroughness),
    ]

    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {test_name} test...")
        logger.info(f"{'='*50}")

        try:
            result = await test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
        except Exception as e:
            logger.error(f"{test_name}: ❌ ERROR - {e}")
            results[test_name] = False

    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")

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