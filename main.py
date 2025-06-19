"""
Simple GAIA Agent - Barebones implementation with two-agent pattern.
"""

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import Runner
from dotenv import load_dotenv

from agent import get_answer_agent, get_gaia_agent


async def run_task(task: str):
    """Run the task through GAIA agent and then through answer agent for concise response."""
    print("🚀 Starting GAIA agent system...")
    print(f"📋 Task: {task}")
    print("-" * 50)

    # Step 1: Run the GAIA research agent
    gaia_agent = get_gaia_agent()
    print("🔍 Research agent working...")

    research_result = await Runner.run(gaia_agent, task)
    research_output = research_result.final_output

    # Get conversation history from research phase
    conversation_history = []
    for item in research_result.new_items:
        conversation_history.append(
            {"type": item.__class__.__name__, "content": str(item)}
        )

    print("\n✅ Research complete!")
    print("-" * 50)

    # Step 2: Pass to answer agent for concise response
    answer_agent = get_answer_agent()
    print("📝 Answer agent synthesizing...")

    # Create input for answer agent with task and research
    answer_input = f"""Original Task: {task}

Research Agent Output:
{research_output}

Based on the research above, provide a clear, concise answer to the original task."""

    final_result = await Runner.run(answer_agent, answer_input)
    final_answer = final_result.final_output

    print("\n✅ Final answer ready!")
    print("=" * 50)
    print("FINAL ANSWER:")
    print(final_answer)
    print("=" * 50)

    return final_answer, research_output


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Simple argument parsing
    parser = argparse.ArgumentParser(description="Simple GAIA agent for solving tasks")
    parser.add_argument(
        "--task", type=str, required=True, help="The task/question to solve"
    )

    args = parser.parse_args()

    # Run the task
    asyncio.run(run_task(args.task))


if __name__ == "__main__":
    main()
