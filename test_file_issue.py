#!/usr/bin/env python3
"""
Test script to verify file access issue is fixed.
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


async def test_file_issue():
    """Test that the agent handles missing files properly."""

    test_cases = [
        {
            "name": "Missing Category File",
            "task": "Read the file 'missing_categories.txt' and explain what category it describes.",
        },
        {
            "name": "Missing Data File",
            "task": "What is the content of line 42 in the file 'missing_data.csv'?",
        },
        {
            "name": "Missing Analysis File",
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
                problematic_phrases = [
                    'unable to access',
                    'cannot access',
                    'file not found',
                    'no results available',
                    'cannot provide',
                    'i cannot'
                ]

                if any(phrase in lower_answer for phrase in problematic_phrases):
                    print("❌ ISSUE: Agent gave problematic response")
                else:
                    print("✅ Agent provided helpful response")
            else:
                print("❌ ISSUE: No answer provided")

        except Exception as e:
            print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    configure_logging()
    asyncio.run(test_file_issue())