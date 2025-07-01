#!/usr/bin/env python3
"""
Test script to reproduce the specific "No results available for category explanations" issue.
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


async def test_category_explanations_issue():
    """Test scenarios that might produce 'No results available for category explanations' responses."""

    # These are tasks that might require explanations for different categories
    test_cases = [
        {
            "name": "Mathematical Category Explanation",
            "task": "Explain the category of mathematical operations that includes addition, subtraction, multiplication, and division.",
        },
        {
            "name": "Scientific Category Explanation",
            "task": "Explain the category of scientific phenomena that includes photosynthesis, respiration, and fermentation.",
        },
        {
            "name": "Historical Category Explanation",
            "task": "Explain the category of historical events that includes the Renaissance, Enlightenment, and Industrial Revolution.",
        },
        {
            "name": "Geographic Category Explanation",
            "task": "Explain the category of geographic features that includes mountains, valleys, and plateaus.",
        },
        {
            "name": "Biological Category Explanation",
            "task": "Explain the category of biological processes that includes mitosis, meiosis, and binary fission.",
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

            # Check for "No results available for category explanations" or similar
            if final_answer and any(phrase in final_answer.lower() for phrase in [
                'no results available for category explanations',
                'no results available for category',
                'category explanations not available',
                'cannot explain category',
                'category explanation unavailable'
            ]):
                print("❌ ISSUE: 'No results available for category explanations' response")
                results.append(False)
            elif not final_answer:
                print("❌ ISSUE: No answer provided")
                results.append(False)
            else:
                print("✅ Agent provided category explanation")
                results.append(True)

        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append(False)

    passed = sum(results)
    total = len(results)

    print(f"\n{'='*60}")
    print(f"CATEGORY EXPLANATIONS ISSUE TEST: {passed}/{total} passed")
    print(f"{'='*60}")

    if passed < total:
        print("❌ Found 'No results available for category explanations' issue!")
        return False
    else:
        print("✅ No 'No results available for category explanations' issue found")
        return True


if __name__ == "__main__":
    configure_logging()
    success = asyncio.run(test_category_explanations_issue())
    sys.exit(0 if success else 1)