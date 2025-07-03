#!/usr/bin/env python3
"""
Simple test of the improvements.
"""

import asyncio
from tools import format_final_answer

async def test_direct():
    """Test the formatting function directly."""
    print("Testing format_final_answer directly...")

    # Test 1: Quote removal
    result1 = await format_final_answer('"Format Document"', "what command did they click")
    print(f"Test 1: '{result1}' (should be 'Format Document')")

    # Test 2: Capitalization
    result2 = await format_final_answer("right", "If you understand this sentence, write the opposite of left")
    print(f"Test 2: '{result2}' (should be 'Right')")

    return result1 == "Format Document" and result2 == "Right"

if __name__ == "__main__":
    result = asyncio.run(test_direct())
    print(f"Direct test {'PASSED' if result else 'FAILED'}")