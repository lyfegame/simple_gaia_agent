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
from utils import configure_logging
from main import run_task

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


async def test_formatting_issue():
    """Test the formatting issue - agent should return just numbers when requested."""
    logger.info("Testing formatting issue...")

    # Test case similar to the potato bag problem
    task = "If I need 2 bags of potatoes, how many bags do I need? Just give the number."

    try:
        final_answer, research_output = await run_task(task)
        logger.info(f"Answer: '{final_answer}'")

        # Check if answer contains extra text
        if final_answer and any(word in final_answer.lower() for word in ['bags', 'bag', 'potatoes']):
            logger.error("❌ FORMATTING ISSUE: Answer contains extra text when only number was requested")
            return False
        else:
            logger.info("✅ Formatting looks good")
            return True

    except Exception as e:
        logger.error(f"❌ Error in test: {e}")
        return False


async def test_missing_file_handling():
    """Test how agent handles missing files."""
    logger.info("Testing missing file handling...")

    task = "Read the file 'nonexistent_file.txt' and tell me what it contains."

    try:
        final_answer, research_output = await run_task(task)
        logger.info(f"Answer: '{final_answer}'")

        # Check if agent gives up too early
        if final_answer and any(phrase in final_answer.lower() for phrase in [
            'cannot provide', 'unable to access', 'please provide', 'file not found'
        ]):
            logger.error("❌ EARLY_TERMINATION: Agent gave up without trying alternatives")
            return False
        else:
            logger.info("✅ Agent handled missing file appropriately")
            return True

    except Exception as e:
        logger.error(f"❌ Error in test: {e}")
        return False


async def test_web_search_fallback():
    """Test if agent uses web search when files are missing."""
    logger.info("Testing web search fallback...")

    task = "What is the capital of France? (Pretend you need to read a file first, but if it's missing, use web search)"

    try:
        final_answer, research_output = await run_task(task)
        logger.info(f"Answer: '{final_answer}'")

        # Check if agent found the answer despite missing file
        if final_answer and 'paris' in final_answer.lower():
            logger.info("✅ Agent successfully used fallback strategy")
            return True
        else:
            logger.error("❌ Agent failed to use fallback strategy")
            return False

    except Exception as e:
        logger.error(f"❌ Error in test: {e}")
        return False


async def main():
    """Run all tests."""
    configure_logging()
    logger.info("🧪 Testing Agent Issues\n")

    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("❌ No OPENAI_API_KEY found. Cannot run tests.")
        return False

    tests = [
        test_formatting_issue,
        test_missing_file_handling,
        test_web_search_fallback,
    ]

    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
            logger.info("-" * 50)
        except Exception as e:
            logger.error(f"❌ Test failed with exception: {e}")
            results.append(False)

    passed = sum(results)
    total = len(results)

    logger.info(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        logger.info("✅ All tests passed!")
        return True
    else:
        logger.error("❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)