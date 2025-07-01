#!/usr/bin/env python3
"""
Test script to verify improvements to the agent.
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


async def test_improvements():
    """Test that the improved agent handles problematic cases better."""

    test_cases = [
        {
            "name": "Very Short Ambiguous Request",
            "task": "Explain.",
        },
        {
            "name": "Missing File Request",
            "task": "Read the file 'missing_categories.txt' and explain what category it describes.",
        },
        {
            "name": "Ambiguous Category Request",
            "task": "What category does this belong to?",
        },
        {
            "name": "Vague Category Explanation",
            "task": "Provide category explanations.",
        },
        {
            "name": "Missing Context Category",
            "task": "Explain the category.",
        }
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"Task: {test_case['task']}")
        print(f"{'='*60}")

        try:
            final_answer, research_output = await run_task(test_case['task'])
            print(f"Answer: {final_answer}")

            # Check for problematic responses
            if final_answer:
                lower_answer = final_answer.lower()
                problematic_phrases = [
                    'no results available',
                    'cannot provide',
                    'unable to access',
                    'i cannot',
                    'please provide more information',
                    'need more context',
                    'more details needed',
                    'cannot determine',
                    'unable to determine'
                ]

                if any(phrase in lower_answer for phrase in problematic_phrases):
                    print("❌ ISSUE: Agent gave problematic response")
                    results.append(False)
                else:
                    print("✅ Agent provided helpful response")
                    results.append(True)
            else:
                print("❌ ISSUE: No answer provided")
                results.append(False)

        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append(False)

    passed = sum(results)
    total = len(results)

    print(f"\n{'='*60}")
    print(f"IMPROVEMENTS TEST RESULTS: {passed}/{total} passed")
    print(f"{'='*60}")

    return passed == total


if __name__ == "__main__":
    configure_logging()
    success = asyncio.run(test_improvements())
    sys.exit(0 if success else 1)