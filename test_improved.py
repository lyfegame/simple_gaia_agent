#!/usr/bin/env python3
"""
Test script for the improved agent.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the repo to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import run_task
from utils import configure_logging

async def test_file_listing():
    """Test file listing functionality."""
    print("Testing file listing...")

    task = "List the files in the gaia/files/2023/validation directory and tell me how many files are there."
    try:
        result, research = await run_task(task)
        print(f"Result: {result}")
        print(f"Research length: {len(research) if research else 0}")
    except Exception as e:
        print(f"Error: {e}")

async def test_calculation():
    """Test calculation functionality."""
    print("Testing calculation...")

    task = "Calculate 123 * 456 + 789. Use code execution to get the exact answer."
    try:
        result, research = await run_task(task)
        print(f"Result: {result}")
        print(f"Research length: {len(research) if research else 0}")
    except Exception as e:
        print(f"Error: {e}")

async def test_file_access():
    """Test file access with a specific file."""
    print("Testing file access...")

    task = "What type of file is 389793a7-ca17-4e82-81cb-2b3a2391b4b9.txt and can you read its contents?"
    file_path = "gaia/files/2023/validation/389793a7-ca17-4e82-81cb-2b3a2391b4b9.txt"
    try:
        result, research = await run_task(task, file_path)
        print(f"Result: {result}")
        print(f"Research length: {len(research) if research else 0}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    configure_logging()

    print("=== Testing Improved Agent ===")
    asyncio.run(test_calculation())
    print("\n" + "="*50 + "\n")
    asyncio.run(test_file_listing())
    print("\n" + "="*50 + "\n")
    asyncio.run(test_file_access())