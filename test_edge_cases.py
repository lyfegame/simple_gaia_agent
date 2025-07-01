#!/usr/bin/env python3
"""
Test script to check edge cases that might cause "No results available" issues.
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


async def test_edge_cases():
    """Test edge cases that might produce problematic responses."""

    test_cases = [
        {
            "name": "Empty Task",
            "task": "",
        },
        {
            "name": "Very Short Task",
            "task": "Explain.",
        },
        {
            "name": "Ambiguous Category Request",
            "task": "What category does this belong to?",
        },
        {
            "name": "Category Without Context",
            "task": "Explain the category.",
        },
        {
            "name": "Nonsensical Category Request",
            "task": "Explain the category of purple flying elephants that sing opera.",
        },
        {
            "name": "Category with No Clear Answer",
            "task": "What category do unicorns, dragons, and phoenixes belong to?",
        }
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"Task: '{test_case['task']}'")
        print(f"{'='*60}")

        try:
            final_answer, research_output = await run_task(test_case['task'])
            print(f"Answer: {final_answer}")

            # Check for problematic responses
            if final_answer and any(phrase in final_answer.lower() for phrase in [
                'no results available',
                'cannot provide',
                'unable to determine',
                'please provide more context',
                'i need more information'
            ]):
                print("⚠️  Agent gave a limited response")
                results.append(False)
            elif not final_answer or final_answer.strip() == "":
                print("❌ ISSUE: No answer provided")
                results.append(False)
            else:
                print("✅ Agent provided some form of answer")
                results.append(True)

        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append(False)

    passed = sum(results)
    total = len(results)

    print(f"\n{'='*60}")
    print(f"EDGE CASES TEST RESULTS: {passed}/{total} passed")
    print(f"{'='*60}")

    return passed == total


if __name__ == "__main__":
    configure_logging()
    success = asyncio.run(test_edge_cases())
    sys.exit(0 if success else 1)