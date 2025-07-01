#!/usr/bin/env python3
"""
Script to reproduce the early termination issue.
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


async def test_early_termination():
    """Test the early termination issue."""

    print("=" * 60)
    print("TEST: Early Termination Issue")
    print("=" * 60)

    task = """What was the volume in m^3 of the fish bag that was calculated in the University of Leicester paper "Can Hiccup Supply Enough Fish to Maintain a Dragon's Diet?" """

    final_answer, research_output = await run_task(task)

    print(f"\nResearch Output (first 500 chars):")
    print(research_output[:500] if research_output else "None")
    print("...")

    print(f"\nFinal Answer: '{final_answer}'")

    # Check if the research found the answer but the answer agent gave up
    if research_output and "8.592" in research_output:
        print("✅ Research agent found the volume: 8.592 m³")
        if final_answer and "8.592" in final_answer:
            print("✅ Answer agent correctly used the research")
        else:
            print("❌ ISSUE: Answer agent gave up despite research finding the answer")
    else:
        print("❌ Research agent didn't find the volume")


if __name__ == "__main__":
    configure_logging()
    asyncio.run(test_early_termination())