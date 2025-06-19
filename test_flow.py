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
    """Test the two-agent flow with a simple task."""
    print("🧪 Testing GAIA Agent Flow")
    print("=" * 50)

    # Test task
    test_task = "What is 2 + 2?"

    try:
        # Test Research Agent
        print("\n1️⃣ Testing Research Agent...")
        research_agent = get_gaia_agent()
        research_result = await Runner.run(research_agent, test_task)

        if not research_result or not research_result.final_output:
            print("❌ Research agent failed to produce output")
            return False

        print("✅ Research agent produced output")
        print(f"   Output length: {len(research_result.final_output)} chars")

        # Test Answer Agent
        print("\n2️⃣ Testing Answer Agent...")
        answer_agent = get_answer_agent()

        answer_input = f"""Original Task: {test_task}

Research Agent Output:
{research_result.final_output}

Based on the research above, provide a clear, concise answer to the original task."""

        answer_result = await Runner.run(answer_agent, answer_input)

        if not answer_result or not answer_result.final_output:
            print("❌ Answer agent failed to produce output")
            return False

        print("✅ Answer agent produced output")
        print(f"   Final answer: {answer_result.final_output}")

        # Verify the answer is concise
        if len(answer_result.final_output) > 500:
            print("⚠️  Warning: Answer might not be concise enough")

        print("\n✅ All tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return False


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
