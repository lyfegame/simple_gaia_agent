"""
Simple test to verify the GAIA agent flow works correctly.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import Runner
from dotenv import load_dotenv

from agent import get_answer_agent, get_gaia_agent


async def test_agent_flow():
    """Test the two-agent flow with simple tasks and verify answers."""
    print("🧪 Testing GAIA Agent Flow")
    print("=" * 50)

    # Test cases with expected answers
    test_cases = [
        {"task": "What is 2 + 2?", "expected": "4"},
        {"task": "What is the capital of France?", "expected": "Paris"},
        {"task": "Is water H2O? Answer yes or no.", "expected": ["yes", "Yes"]},
    ]

    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        test_task = test_case["task"]
        expected = test_case["expected"]

        print(f"\n📝 Test {i}: {test_task}")
        print("-" * 40)

        try:
            # Test Research Agent
            print("🔍 Running research agent...")
            research_agent = get_gaia_agent()
            research_result = await Runner.run(research_agent, test_task)

            if not research_result or not research_result.final_output:
                print("❌ Research agent failed to produce output")
                all_passed = False
                continue

            # Test Answer Agent
            print("📝 Running answer agent...")
            answer_agent = get_answer_agent()

            answer_input = f"""Original Task: {test_task}

Research Agent Output:
{research_result.final_output}

Based on the research above, provide a clear, concise answer to the original task."""

            answer_result = await Runner.run(answer_agent, answer_input)

            if not answer_result or not answer_result.final_output:
                print("❌ Answer agent failed to produce output")
                all_passed = False
                continue

            final_answer = answer_result.final_output.strip()
            print(f"   Answer: {final_answer}")

            # Verify the answer
            if isinstance(expected, list):
                # Multiple acceptable answers
                if any(
                    final_answer.lower() == exp.lower()
                    or exp.lower() in final_answer.lower()
                    for exp in expected
                ):
                    print("✅ Answer is correct!")
                else:
                    print(f"❌ Answer is incorrect. Expected one of: {expected}")
                    all_passed = False
            else:
                # Single expected answer
                if (
                    final_answer.lower() == expected.lower()
                    or expected.lower() in final_answer.lower()
                ):
                    print("✅ Answer is correct!")
                else:
                    print(f"❌ Answer is incorrect. Expected: {expected}")
                    all_passed = False

        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed.")

    return all_passed


def main():
    """Run the test."""
    load_dotenv()

    # Check if API key is set
    import os

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)

    # Run the test
    success = asyncio.run(test_agent_flow())

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
