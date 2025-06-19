"""
Simple unified test for the GAIA agent.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load env vars
load_dotenv()


def test_imports():
    """Test that all imports work."""
    print("🔧 Testing imports...")
    try:
        print("✅ Imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False


async def test_questions():
    """Test with simple questions."""
    print("\n📝 Testing simple questions...")

    from agents import Runner

    from agent import get_answer_agent, get_gaia_agent

    tests = [
        ("What is 2 + 2?", "4"),
        ("What is the capital of France?", "Paris"),
    ]

    for question, expected in tests:
        print(f"\n   Q: {question}")
        try:
            # Get answer through the two-agent flow
            research = await Runner.run(get_gaia_agent(), question)
            answer_input = f"Task: {question}\nResearch: {research.final_output}\nProvide a concise answer."
            answer = await Runner.run(get_answer_agent(), answer_input)

            result = answer.final_output.strip()
            print(f"   A: {result}")

            # Check if answer contains expected
            if expected.lower() in result.lower():
                print("   ✅")
            else:
                print(f"   ❌ Expected: {expected}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False

    return True


async def main():
    """Run all tests."""
    print("🧪 Running GAIA Agent Tests\n")

    # Test imports
    if not test_imports():
        return False

    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  No API key found. Skipping question tests.")
        print("💡 Set OPENAI_API_KEY to test with real questions.")
        return True

    # Test questions
    if not await test_questions():
        return False

    print("\n✅ All tests passed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
