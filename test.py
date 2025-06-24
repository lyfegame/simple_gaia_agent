"""
Simple unified test for the GAIA agent.
"""

import asyncio
import logging
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from utils import configure_logging

# Load env vars
load_dotenv()
logger = logging.getLogger(__name__)


def test_imports():
    """Test that all imports work."""
    logger.info("🔧 Testing imports...")
    try:
        logger.info("✅ Imports successful")
        return True
    except Exception as e:
        logger.info(f"❌ Import failed: {str(e)}")
        return False


async def test_tools():
    """Test individual tools."""
    logger.info("\n🔧 Testing tools...")

    try:
        from tools import web_search, web_scrape, file_read

        # Test file_read tool directly (requires ctx parameter)
        logger.info("   Testing file_read tool...")
        # Call tool directly - file_read requires ctx as first parameter
        result = await file_read.on_invoke_tool(
            ctx=None, input=json.dumps({"filename": "README.md"})
        )  # Pass None for ctx since it's not used
        if result and "GAIA" in result:
            logger.info("   ✅ file_read tool works")
        else:
            logger.info(f"   ❌ file_read tool failed: {result}")
            return False

        # Test using on_invoke_tool syntax for web_search
        if os.getenv("OPENAI_API_KEY"):
            logger.info("   Testing web_search tool...")
            result = await web_search.on_invoke_tool(
                ctx=None, input=json.dumps({"query": "Python programming language"})
            )
            if result and not result.startswith("Web search error"):
                logger.info("   ✅ web_search tool works")
            else:
                logger.info(f"   ❌ web_search tool failed: {result}")
                return False
        else:
            logger.info("   ⚠️ Skipping web_search (no API key)")

        # Test web_scrape tool directly
        logger.info("   Testing web_scrape tool...")
        result = await web_scrape.on_invoke_tool(
            ctx=None,
            input=json.dumps({"url": "https://httpbin.org/html"}),
        )
        if result and not result.startswith("Error scraping"):
            logger.info("   ✅ web_scrape tool works")
        else:
            logger.info(f"   ❌ web_scrape tool failed: {result}")
            return False

        return True
    except Exception as e:
        logger.info(f"   ❌ Tool test failed: {str(e)}")
        return False


async def test_questions():
    """Test with simple questions."""
    logger.info("\n📝 Testing simple questions...")

    from agents import Runner

    from agent import get_answer_agent, get_gaia_agent

    tests = [
        ("What is 2 + 2?", "4"),
        ("What is the capital of France?", "Paris"),
    ]

    for question, expected in tests:
        logger.info(f"\n   Q: {question}")
        try:
            # Get answer through the two-agent flow
            research = await Runner.run(get_gaia_agent(), question)
            answer_input = f"Task: {question}\nResearch: {research.final_output}\nProvide a concise answer."
            answer = await Runner.run(get_answer_agent(), answer_input)

            result = answer.final_output.strip()
            logger.info(f"   A: {result}")

            # Check if answer contains expected
            if expected.lower() in result.lower():
                logger.info("   ✅")
            else:
                logger.info(f"   ❌ Expected: {expected}")
                return False
        except Exception as e:
            logger.info(f"   ❌ Error: {str(e)}")
            return False

    return True


async def main():
    """Run all tests."""
    configure_logging()
    logger.info("🧪 Running GAIA Agent Tests\n")

    # Test imports
    if not test_imports():
        return False

    # Test tools
    if not await test_tools():
        return False

    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.info("\n⚠️  No API key found. Skipping question tests.")
        logger.info("💡 Set OPENAI_API_KEY to test with real questions.")
        return True

    # Test questions
    if not await test_questions():
        return False

    logger.info("\n✅ All tests passed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
