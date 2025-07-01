#!/usr/bin/env python3
"""
Test script to simulate specific failure cases mentioned in the PR description.
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


async def test_no_information_available():
    """Test that agent doesn't give up with 'No information available'."""
    logger.info("Testing 'No information available' issue...")

    # Test with a question that should have information available
    task = "What is the population of New York City?"
    try:
        answer, research = await run_task(task)
        logger.info(f"Answer: {answer}")
        logger.info(f"Research length: {len(research) if research else 0}")

        # Check that agent doesn't give up
        failure_phrases = [
            "no information available",
            "unable to determine",
            "cannot find",
            "please provide",
            "please access"
        ]

        has_failure_phrase = any(phrase in answer.lower() for phrase in failure_phrases)
        has_meaningful_content = len(answer.strip()) > 10

        return not has_failure_phrase and has_meaningful_content

    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


async def test_file_processing():
    """Test that agent can process files when they exist."""
    logger.info("Testing file processing...")

    # Create a test file with specific content
    test_file = Path("test_data.txt")
    test_content = """
    Gift Recipients:
    - Alice: Received a book
    - Bob: Received a watch
    - Charlie: Did not receive a gift
    - Diana: Received flowers
    """

    try:
        with open(test_file, "w") as f:
            f.write(test_content)

        task = "Based on the test_data.txt file, who did not receive a gift?"
        answer, research = await run_task(task, str(test_file))

        logger.info(f"Answer: {answer}")

        # Check if the agent correctly identified Charlie
        success = (answer is not None and
                  "charlie" in answer.lower() and
                  "unable" not in answer.lower() and
                  "please provide" not in answer.lower())

        return success

    except Exception as e:
        logger.error(f"File processing test failed: {e}")
        return False
    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()


async def test_specific_information_extraction():
    """Test extraction of specific information like album counts."""
    logger.info("Testing specific information extraction...")

    # Test with a question about album counts (similar to failed task)
    task = "How many studio albums has Taylor Swift released as of 2023?"
    try:
        answer, research = await run_task(task)
        logger.info(f"Answer: {answer}")
        logger.info(f"Research length: {len(research) if research else 0}")

        # Check that we get a specific number, not just "Four studio albums"
        # The answer should be a number or contain a specific count
        has_number = any(char.isdigit() for char in answer)
        not_vague = "studio albums" not in answer.lower() or any(char.isdigit() for char in answer)
        not_failure = "unable" not in answer.lower() and "no information" not in answer.lower()

        return has_number and not_vague and not_failure

    except Exception as e:
        logger.error(f"Specific information extraction test failed: {e}")
        return False


async def test_web_content_analysis():
    """Test analysis of web content for specific commands or information."""
    logger.info("Testing web content analysis...")

    # Test with a question that requires finding specific information from web content
    task = "What is the current version of Python as of 2023?"
    try:
        answer, research = await run_task(task)
        logger.info(f"Answer: {answer}")

        # Check that we get specific version information
        has_version_info = any(char.isdigit() for char in answer) and ("3." in answer or "python" in answer.lower())
        not_failure = ("couldn't find" not in answer.lower() and
                      "unable" not in answer.lower() and
                      "no information" not in answer.lower())

        return has_version_info and not_failure

    except Exception as e:
        logger.error(f"Web content analysis test failed: {e}")
        return False


async def main():
    """Run all specific failure tests."""
    configure_logging()
    logger.info("🧪 Running specific failure case tests\n")

    if not os.getenv("OPENAI_API_KEY"):
        logger.error("❌ No OPENAI_API_KEY found. Cannot run tests.")
        return False

    tests = [
        ("No Information Available", test_no_information_available),
        ("File Processing", test_file_processing),
        ("Specific Information Extraction", test_specific_information_extraction),
        ("Web Content Analysis", test_web_content_analysis),
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
    logger.info("TEST SUMMARY")
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