#!/usr/bin/env python3
"""
Test script to check for "No results available" issues.
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


async def test_no_results_issue():
    """Test scenarios that might produce 'No results available' responses."""

    test_cases = [
        {
            "name": "Missing File with No Fallback",
            "task": "Read the file 'completely_nonexistent_file_12345.txt' and tell me its contents.",
        },
        {
            "name": "Obscure Information Request",
            "task": "What is the exact temperature in Celsius at coordinates 45.123456, -123.654321 right now?",
        },
        {
            "name": "Specific File Content Request",
            "task": "What is the content of line 42 in the file 'missing_data.csv'?",
        },
        {
            "name": "Complex Calculation with Missing Data",
            "task": "Calculate the exact volume of the container described in the file 'container_specs.pdf'.",
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

            # Check for "No results available" or similar phrases
            if final_answer and any(phrase in final_answer.lower() for phrase in [
                'no results available',
                'cannot provide',
                'unable to access',
                'please provide',
                'file not found',
                'i cannot',
                'not available'
            ]):
                print("❌ ISSUE: Agent gave 'No results available' type response")
                results.append(False)
            elif not final_answer:
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
    print(f"NO RESULTS AVAILABLE TEST RESULTS: {passed}/{total} passed")
    print(f"{'='*60}")

    return passed == total


if __name__ == "__main__":
    configure_logging()
    success = asyncio.run(test_no_results_issue())
    sys.exit(0 if success else 1)