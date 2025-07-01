#!/usr/bin/env python3
"""
Test specific issues identified in the PR description.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from utils import configure_logging
from main import run_task, post_process_answer

logger = logging.getLogger(__name__)

async def test_formatting_edge_cases():
    """Test specific formatting edge cases."""
    logger.info("Testing formatting edge cases...")

    # Test cases from the PR description
    test_cases = [
        # Case 1: Should return "egalitarian" not "Egalitarianism"
        ("What word describes a type of society?", "Egalitarianism", "egalitarian"),

        # Case 2: Should return "2" not "Two"
        ("How many links minimum?", "Two", "2"),

        # Case 3: Should return "6" not "6 cups"
        ("How many cups? Just give the number.", "6 cups", "6"),

        # Case 4: Should return movie title without asterisks
        ("What movie title?", "*A Nightmare on Elm Street*", "A Nightmare on Elm Street"),

        # Case 5: Should return "142" not "142,000 years old"
        ("How many thousands of years old?", "142,000 years old", "142"),
    ]

    for i, (task, raw_answer, expected) in enumerate(test_cases, 1):
        logger.info(f"\nTest {i}: {task}")
        processed = post_process_answer(raw_answer, task)
        logger.info(f"Raw: '{raw_answer}'")
        logger.info(f"Processed: '{processed}'")
        logger.info(f"Expected: '{expected}'")
        logger.info(f"Match: {processed == expected}")

async def test_early_termination_scenarios():
    """Test scenarios that should not cause early termination."""
    logger.info("\nTesting early termination scenarios...")

    # These should try alternative approaches, not give up immediately
    scenarios = [
        "How many applicants for the job in the PDF are only missing a single qualification?",
        "What is the average number of pre-2020 works on the open researcher pages?",
        "Which of the text elements under CATEGORIES in the XML would contain the one food?",
    ]

    for scenario in scenarios:
        logger.info(f"\nScenario: {scenario}")
        try:
            answer, _ = await run_task(scenario)
            logger.info(f"Answer: '{answer}'")

            # Check if it gave up too early
            early_termination_phrases = [
                "cannot be provided",
                "files are missing",
                "unavailable",
                "unable to provide",
                "can't provide",
                "not found"
            ]

            gave_up = any(phrase in answer.lower() for phrase in early_termination_phrases)
            logger.info(f"Gave up early: {gave_up}")

        except Exception as e:
            logger.error(f"Error: {e}")

async def main():
    """Run all specific issue tests."""
    configure_logging()
    load_dotenv()

    logger.info("🧪 Testing specific issues from PR description\n")

    await test_formatting_edge_cases()
    await test_early_termination_scenarios()

    logger.info("\n✅ Specific issue testing complete!")

if __name__ == "__main__":
    asyncio.run(main())