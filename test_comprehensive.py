#!/usr/bin/env python3
"""
Comprehensive test script for the improved agent.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the repo to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import run_task
from utils import configure_logging

async def test_calculation_task():
    """Test a calculation task similar to failed ones."""
    print("=== Testing Calculation Task ===")

    task = "Calculate the distance between the first and second atoms in a PDB file. For testing purposes, assume the first atom is at coordinates (1.0, 2.0, 3.0) and the second atom is at coordinates (4.0, 6.0, 8.0). Calculate the Euclidean distance."
    try:
        result, research = await run_task(task)
        print(f"Result: {result}")
        print(f"Research length: {len(research) if research else 0}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

async def test_file_exploration():
    """Test file exploration capabilities."""
    print("=== Testing File Exploration ===")

    task = "Explore the gaia/files/2023/validation directory. How many zip files are there and what are their names?"
    try:
        result, research = await run_task(task)
        print(f"Result: {result}")
        print(f"Research length: {len(research) if research else 0}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

async def test_web_research():
    """Test web research capabilities."""
    print("=== Testing Web Research ===")

    task = "What is the capital of Australia? Use web search to verify."
    try:
        result, research = await run_task(task)
        print(f"Result: {result}")
        print(f"Research length: {len(research) if research else 0}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

async def test_complex_calculation():
    """Test complex calculation with multiple steps."""
    print("=== Testing Complex Calculation ===")

    task = "Calculate the compound interest for an initial amount of $1000, with an annual interest rate of 5%, compounded monthly, over 3 years. What is the final amount?"
    try:
        result, research = await run_task(task)
        print(f"Result: {result}")
        print(f"Research length: {len(research) if research else 0}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    configure_logging()

    print("=== Comprehensive Agent Testing ===\n")

    # Run all tests
    results = []

    result1 = asyncio.run(test_calculation_task())
    results.append(("Calculation Task", result1))
    print("\n" + "="*60 + "\n")

    result2 = asyncio.run(test_file_exploration())
    results.append(("File Exploration", result2))
    print("\n" + "="*60 + "\n")

    result3 = asyncio.run(test_web_research())
    results.append(("Web Research", result3))
    print("\n" + "="*60 + "\n")

    result4 = asyncio.run(test_complex_calculation())
    results.append(("Complex Calculation", result4))
    print("\n" + "="*60 + "\n")

    # Summary
    print("=== TEST SUMMARY ===")
    for test_name, result in results:
        status = "✅ PASS" if result is not None else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            print(f"  Result: {result}")
    print("\n" + "="*60)