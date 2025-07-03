#!/usr/bin/env python3
"""
Test the improvements made to the GAIA agent system.
"""

import asyncio
import logging
from tools import wayback_machine_search, format_final_answer, github_search, parse_json_ld

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_wayback_machine():
    """Test the Wayback Machine functionality."""
    print("Testing Wayback Machine...")
    result = await wayback_machine_search.on_invoke_tool(
        ctx=None,
        input={"url": "https://wikipedia.org", "date": "20200101"}
    )
    print(f"Wayback result: {result[:200]}...")
    return "wayback" in result.lower()

async def test_formatting():
    """Test the answer formatting functionality."""
    print("Testing answer formatting...")

    # Test quote removal
    result1 = await format_final_answer.on_invoke_tool(
        ctx=None,
        input={"answer": '"Format Document"', "task_context": "what command did they click"}
    )
    print(f"Format test 1: '{result1}' (should be 'Format Document')")

    # Test capitalization
    result2 = await format_final_answer.on_invoke_tool(
        ctx=None,
        input={"answer": "right", "task_context": "If you understand this sentence, write the opposite of left"}
    )
    print(f"Format test 2: '{result2}' (should be 'Right')")

    return result1 == "Format Document" and result2 == "Right"

async def test_github_search():
    """Test GitHub search functionality."""
    print("Testing GitHub search...")
    result = await github_search.on_invoke_tool(
        ctx=None,
        input={"query": "opencv", "search_type": "repositories"}
    )
    print(f"GitHub result: {result[:200]}...")
    return "opencv" in result.lower()

async def test_json_ld_parsing():
    """Test JSON-LD parsing functionality."""
    print("Testing JSON-LD parsing...")
    test_json = '{"@context": "https://schema.org", "@type": "Person", "name": "John Doe", "orcid": "0000-0000-0000-0000"}'
    result = await parse_json_ld.on_invoke_tool(
        ctx=None,
        input={"content": test_json}
    )
    print(f"JSON-LD result: {result[:200]}...")
    return "orcid" in result.lower()

async def main():
    """Run all tests."""
    print("Running improvement tests...\n")

    tests = [
        ("Wayback Machine", test_wayback_machine),
        ("Answer Formatting", test_formatting),
        ("GitHub Search", test_github_search),
        ("JSON-LD Parsing", test_json_ld_parsing),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
            print(f"✅ {test_name}: {'PASSED' if result else 'FAILED'}\n")
        except Exception as e:
            results[test_name] = False
            print(f"❌ {test_name}: FAILED - {str(e)}\n")

    print("Test Summary:")
    print("=" * 40)
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    passed_count = sum(results.values())
    total_count = len(results)
    print(f"\nOverall: {passed_count}/{total_count} tests passed")

if __name__ == "__main__":
    asyncio.run(main())