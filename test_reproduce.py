#!/usr/bin/env python3
"""
Test script to reproduce the agent issues.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the repo to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import run_task
from utils import configure_logging

async def test_file_access():
    """Test file access issues."""
    print("Testing file access...")

    # Test with a file that should exist
    test_file = Path("gaia/files/2023/validation/389793a7-ca17-4e82-81cb-2b3a2391b4b9.txt")
    if test_file.exists():
        print(f"File exists: {test_file}")
        with open(test_file, 'r') as f:
            content = f.read()
            print(f"Content: {content[:200]}...")
    else:
        print(f"File does not exist: {test_file}")

async def test_simple_task():
    """Test a simple task."""
    print("Testing simple task...")

    task = "What is 2 + 2?"
    try:
        result, research = await run_task(task)
        print(f"Result: {result}")
        print(f"Research length: {len(research) if research else 0}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    configure_logging()
    asyncio.run(test_file_access())
    asyncio.run(test_simple_task())