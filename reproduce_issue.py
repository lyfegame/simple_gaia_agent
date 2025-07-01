#!/usr/bin/env python3
"""
Script to reproduce the specific "No results available for category explanations" issue.
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


async def test_specific_issues():
    """Test specific scenarios that might produce problematic responses."""

    test_cases = [
        {
            "name": "Ambiguous Category Request",
            "task": "Explain the category.",
        },
        {
            "name": "Vague Explanation Request",
            "task": "What category does this belong to?",
        },
        {
            "name": "Missing Context Request",
            "task": "Provide category explanations.",
        },
        {
            "name": "File-based Category Request",
            "task": "Read the file 'categories.txt' and explain what category it describes.",
        },
        {
            "name": "Complex Missing File Request",
            "task": "Based on the data in 'analysis_results.csv', explain what category of phenomena these represent.",
        }
    ]

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
                if any(phrase in lower_answer for phrase in [
                    'no results available for category explanations',
                    'no results available for category',
                    'category explanations not available',
                    'cannot explain category',
                    'category explanation unavailable',
                    'i cannot provide',
                    'unable to access',
                    'please provide more information',
                    'need more context'
                ]):
                    print("❌ PROBLEMATIC: Agent gave unhelpful response")
                else:
                    print("✅ Agent provided helpful response")
            else:
                print("❌ ISSUE: No answer provided")

        except Exception as e:
            print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    configure_logging()
    asyncio.run(test_specific_issues())