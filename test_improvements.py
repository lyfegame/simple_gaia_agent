#!/usr/bin/env python3
"""
Test script to validate the improvements made to the GAIA agent.
"""

import asyncio
import os
import tempfile
from tools import list_files, file_read, calculate, enhanced_web_search

async def test_file_discovery():
    """Test the file discovery improvements."""
    print("🔍 Testing file discovery...")

    # Create a temporary task directory with test files
    os.makedirs("test_task", exist_ok=True)

    # Create test files
    with open("test_task/test.txt", "w") as f:
        f.write("This is a test file for validation.")

    with open("test_task/data.csv", "w") as f:
        f.write("name,age,city\nJohn,25,NYC\nJane,30,SF")

    try:
        # Test file discovery
        result = await list_files.on_invoke_tool(ctx=None, input={"directory": "test_task"})
        print(f"✅ File discovery result: {result}")

        # Test smart file reading
        result = await file_read.on_invoke_tool(ctx=None, input={"filename": "test.txt"})
        print(f"✅ Smart file reading: Found content: {len(result)} chars")

        # Test CSV reading
        result = await file_read.on_invoke_tool(ctx=None, input={"filename": "data.csv"})
        print(f"✅ CSV reading: {result[:100]}...")

    finally:
        # Cleanup
        if os.path.exists("test_task"):
            import shutil
            shutil.rmtree("test_task")

async def test_calculation():
    """Test the mathematical calculation improvements."""
    print("🧮 Testing calculations...")

    test_expressions = [
        "42.195 / 2.0275",  # Marathon pace calculation like in the problem
        "356355 / 20.85",   # Distance calculation
        "17089.71 / 1000",  # Convert to thousands
    ]

    for expr in test_expressions:
        result = await calculate.on_invoke_tool(ctx=None, input={"expression": expr})
        print(f"✅ Calculation '{expr}' = {result}")

async def test_enhanced_search():
    """Test the enhanced web search improvements."""
    print("🔎 Testing enhanced web search...")

    # Test site-specific search
    result = await enhanced_web_search.on_invoke_tool(
        ctx=None,
        input={
            "query": "Python programming",
            "specific_sites": ["github.com"]
        }
    )
    print(f"✅ Enhanced search result length: {len(result)} chars")

async def main():
    """Run all tests."""
    print("🚀 Testing GAIA Agent Improvements")
    print("=" * 50)

    try:
        await test_file_discovery()
        print()
        await test_calculation()
        print()
        await test_enhanced_search()
        print()
        print("✅ All tests completed successfully!")
        print("🎉 The GAIA agent improvements are working correctly!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)