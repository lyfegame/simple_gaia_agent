#!/usr/bin/env python3
"""
Script to reproduce the WebSearchTool error and other issues.
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Add the repo to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools import search_and_scrape, list_files
from agents import WebSearchTool

async def test_websearch_tool():
    """Test the WebSearchTool directly to see the error."""
    print("Testing WebSearchTool directly...")
    try:
        search_tool = WebSearchTool()
        # This should fail with 'WebSearchTool' object has no attribute 'run'
        result = await search_tool.run("test query")
        print(f"Search result: {result}")
    except AttributeError as e:
        print(f"ERROR: {e}")
        return False
    except Exception as e:
        print(f"Other error: {e}")
        return False
    return True

async def test_search_and_scrape():
    """Test the search_and_scrape function."""
    print("\nTesting search_and_scrape function...")
    try:
        result = await search_and_scrape("test query", max_results=1)
        print(f"Search and scrape result: {result[:200]}...")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

async def test_list_files():
    """Test the list_files function with different directory names."""
    print("\nTesting list_files function...")

    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        task_dir = Path(temp_dir) / "task"
        task_dir.mkdir()

        # Create some test files
        (task_dir / "problem.txt").write_text("Test problem")
        (task_dir / "data.txt").write_text("Test data")

        # Test with correct path
        try:
            result1 = await list_files(str(task_dir))
            print(f"list_files('{task_dir}'): {result1}")
        except Exception as e:
            print(f"ERROR with correct path: {e}")

        # Test with incorrect path (like the agent was using)
        try:
            result2 = await list_files("task folder")
            print(f"list_files('task folder'): {result2}")
        except Exception as e:
            print(f"ERROR with 'task folder': {e}")

async def main():
    """Run all tests."""
    print("Reproducing GAIA agent errors...\n")

    await test_websearch_tool()
    await test_search_and_scrape()
    await test_list_files()

    print("\nDone reproducing errors.")

if __name__ == "__main__":
    asyncio.run(main())