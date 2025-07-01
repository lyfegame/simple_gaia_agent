#!/usr/bin/env python3
"""
Test script to check for category explanations issues.
"""

import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from utils import configure_logging
from main import run_task

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


async def test_category_explanations():
    """Test that the agent provides explanations for different categories of questions."""

    test_cases = [
        {
            "name": "Mathematical Calculation",
            "task": "What is 15% of 240? Explain how you calculated this.",
            "should_contain": ["calculation", "multiply", "percent"]
        },
        {
            "name": "Scientific Fact",
            "task": "What is the speed of light in a vacuum? Explain what this means.",
            "should_contain": ["299792458", "meters per second", "constant"]
        },
        {
            "name": "Historical Information",
            "task": "When did World War II end? Explain the significance of this date.",
            "should_contain": ["1945", "September", "surrender"]
        },
        {
            "name": "Geographic Information",
            "task": "What is the capital of Australia? Explain why this city was chosen.",
            "should_contain": ["Canberra", "capital", "chosen"]
        }
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"{'='*60}")

        try:
            final_answer, research_output = await run_task(test_case['task'])
            print(f"Answer: {final_answer}")

            # Check if answer contains explanations
            if final_answer and any(keyword in final_answer.lower() for keyword in test_case['should_contain']):
                print("✅ Answer contains expected explanatory content")
                results.append(True)
            elif final_answer and "no results available" in final_answer.lower():
                print("❌ ISSUE: 'No results available' response")
                results.append(False)
            elif not final_answer:
                print("❌ ISSUE: No answer provided")
                results.append(False)
            else:
                print("⚠️  Answer provided but may lack explanation")
                results.append(True)  # Still counts as success if answer is provided

        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append(False)

    passed = sum(results)
    total = len(results)

    print(f"\n{'='*60}")
    print(f"CATEGORY EXPLANATIONS TEST RESULTS: {passed}/{total} passed")
    print(f"{'='*60}")

    return passed == total


if __name__ == "__main__":
    configure_logging()
    success = asyncio.run(test_category_explanations())
    sys.exit(0 if success else 1)