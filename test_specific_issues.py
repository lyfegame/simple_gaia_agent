#!/usr/bin/env python3
"""
Test script to reproduce specific issues from the PR description.
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


async def test_potato_bag_formatting():
    """Test the exact potato bag problem from the PR description."""
    logger.info("Testing potato bag formatting issue...")

    task = """My family reunion is this week, and I was assigned the mashed potatoes to bring. The attendees include my married mother and father, my twin brother and his family, my aunt and her family, my grandma and her brother, her brother's daughter, and his daughter's family. All the adults but me have been married, and no one is divorced or remarried, but my grandpa and my grandma's sister-in-law passed away last year. All living spouses are attending. My brother has two children that are still kids, my aunt has one six-year-old, and my grandma's brother's daughter has three kids under 12. I figure each adult will eat about 1.5 potatoes of mashed potatoes and each kid will eat about 1/2 a potato of mashed potatoes, except my second cousins don't eat carbs. The average potato is about half a pound, and potatoes are sold in 5-pound bags. How many whole bags of potatoes do I need? Just give the number."""

    try:
        final_answer, research_output = await run_task(task)
        logger.info(f"Answer: '{final_answer}'")

        # Check if answer contains extra text like "bags"
        if final_answer and any(word in final_answer.lower() for word in ['bags', 'bag', 'potatoes', 'potato']):
            logger.error(f"❌ FORMATTING ISSUE: Answer '{final_answer}' contains extra text when only number was requested")
            return False
        elif final_answer and final_answer.strip().isdigit():
            logger.info("✅ Formatting is correct - just the number")
            return True
        else:
            logger.error(f"❌ FORMATTING ISSUE: Answer '{final_answer}' is not just a number")
            return False

    except Exception as e:
        logger.error(f"❌ Error in test: {e}")
        return False


async def test_vscode_quote_formatting():
    """Test the VSCode quote formatting issue."""
    logger.info("Testing VSCode quote formatting issue...")

    task = """In the 2018 VSCode blog post on replit.com, what was the command they clicked on in the last video to remove extra lines?"""

    try:
        final_answer, research_output = await run_task(task)
        logger.info(f"Answer: '{final_answer}'")

        # Check if answer has unnecessary quotes
        if final_answer and (final_answer.startswith('"') and final_answer.endswith('"')):
            logger.error(f"❌ FORMATTING ISSUE: Answer '{final_answer}' has unnecessary quotes")
            return False
        else:
            logger.info("✅ Formatting is correct - no unnecessary quotes")
            return True

    except Exception as e:
        logger.error(f"❌ Error in test: {e}")
        return False


async def test_thousand_hours_formatting():
    """Test the thousand hours formatting issue."""
    logger.info("Testing thousand hours formatting issue...")

    task = """If Eliud Kipchoge could maintain his record-making marathon pace indefinitely, how many thousand hours would it take him to run the distance between the Earth and the Moon its closest approach? Please use the minimum perigee value on the Wikipedia page for the Moon when carrying out your calculation. Round your result to the nearest 1000 hours and do not use any comma separators if necessary."""

    try:
        final_answer, research_output = await run_task(task)
        logger.info(f"Answer: '{final_answer}'")

        # Check if answer is in wrong format (should be "17" not "17,000 hours")
        if final_answer and (',' in final_answer or 'hours' in final_answer.lower()):
            logger.error(f"❌ FORMATTING ISSUE: Answer '{final_answer}' should be just the number of thousand hours")
            return False
        else:
            logger.info("✅ Formatting looks correct")
            return True

    except Exception as e:
        logger.error(f"❌ Error in test: {e}")
        return False


async def test_early_termination_with_missing_file():
    """Test early termination when files are missing."""
    logger.info("Testing early termination with missing file...")

    task = """What was the volume in m^3 of the fish bag that was calculated in the University of Leicester paper "Can Hiccup Supply Enough Fish to Maintain a Dragon's Diet?" """

    try:
        final_answer, research_output = await run_task(task)
        logger.info(f"Answer: '{final_answer}'")

        # Check if agent gives up too early
        if final_answer and any(phrase in final_answer.lower() for phrase in [
            'cannot provide', 'unable to access', 'please provide', 'please upload'
        ]):
            logger.error(f"❌ EARLY_TERMINATION: Agent gave up too early: '{final_answer}'")
            return False
        else:
            logger.info("✅ Agent tried alternative approaches")
            return True

    except Exception as e:
        logger.error(f"❌ Error in test: {e}")
        return False


async def test_web_search_for_missing_data():
    """Test if agent uses web search when specific data is missing."""
    logger.info("Testing web search for missing data...")

    task = """Compute the check digit the Tropicos ID for the Order Helotiales would have if it were an ISBN-10 number."""

    try:
        final_answer, research_output = await run_task(task)
        logger.info(f"Answer: '{final_answer}'")

        # Check if agent tries to find the Tropicos ID online
        if final_answer and any(phrase in final_answer.lower() for phrase in [
            'cannot compute', 'please provide', 'without the tropicos id'
        ]):
            logger.error(f"❌ MISSING_TOOL: Agent didn't try to search for Tropicos ID online: '{final_answer}'")
            return False
        else:
            logger.info("✅ Agent attempted to find missing data")
            return True

    except Exception as e:
        logger.error(f"❌ Error in test: {e}")
        return False


async def main():
    """Run all tests."""
    configure_logging()
    logger.info("🧪 Testing Specific Agent Issues from PR Description\n")

    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("❌ No OPENAI_API_KEY found. Cannot run tests.")
        return False

    tests = [
        test_potato_bag_formatting,
        test_vscode_quote_formatting,
        test_thousand_hours_formatting,
        test_early_termination_with_missing_file,
        test_web_search_for_missing_data,
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
        logger.error("❌ Some tests failed - these are the issues we need to fix")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)