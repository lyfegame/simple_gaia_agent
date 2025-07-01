#!/usr/bin/env python3
"""
Script to reproduce the specific formatting issues identified in the PR.
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


async def test_formatting_issues():
    """Test the specific formatting issues."""

    # Test 1: VSCode quote formatting
    print("=" * 60)
    print("TEST 1: VSCode Quote Formatting")
    print("=" * 60)

    task1 = """In the 2018 VSCode blog post on replit.com, what was the command they clicked on in the last video to remove extra lines?"""

    final_answer1, _ = await run_task(task1)
    print(f"Answer: '{final_answer1}'")

    if final_answer1 and (final_answer1.startswith('"') and final_answer1.endswith('"')):
        print("❌ ISSUE: Answer has unnecessary quotes")
    else:
        print("✅ OK: No unnecessary quotes")

    # Test 2: Thousand hours formatting
    print("\n" + "=" * 60)
    print("TEST 2: Thousand Hours Formatting")
    print("=" * 60)

    task2 = """If Eliud Kipchoge could maintain his record-making marathon pace indefinitely, how many thousand hours would it take him to run the distance between the Earth and the Moon its closest approach? Please use the minimum perigee value on the Wikipedia page for the Moon when carrying out your calculation. Round your result to the nearest 1000 hours and do not use any comma separators if necessary."""

    final_answer2, _ = await run_task(task2)
    print(f"Answer: '{final_answer2}'")

    if final_answer2 and (',' in final_answer2 or 'hours' in final_answer2.lower()):
        print("❌ ISSUE: Answer should be just the number of thousand hours")
    else:
        print("✅ OK: Correct format")


if __name__ == "__main__":
    configure_logging()
    asyncio.run(test_formatting_issues())