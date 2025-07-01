"""
Simple GAIA Agent - Barebones implementation with two-agent pattern.
"""

import argparse
import asyncio
import logging
import os
import sys

from utils import configure_logging, log_agent_output

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import Runner
from dotenv import load_dotenv

from agent import get_answer_agent, get_gaia_agent

logger = logging.getLogger(__name__)


def post_process_answer(answer: str, task: str) -> str:
    """
    Post-process the answer to ensure proper formatting based on the task requirements.

    Args:
        answer: The raw answer from the agent
        task: The original task/question

    Returns:
        Properly formatted answer
    """
    if not answer:
        return answer

    # Clean up the answer
    answer = answer.strip()

    # Remove common formatting issues
    # Remove quotes if they wrap the entire answer
    if (answer.startswith('"') and answer.endswith('"')) or (answer.startswith("'") and answer.endswith("'")):
        answer = answer[1:-1]

    # Remove asterisks if they wrap the entire answer
    if answer.startswith('*') and answer.endswith('*'):
        answer = answer[1:-1]

    # Check for specific formatting requirements in the task
    task_lower = task.lower()

    # If task asks for "just the number" or "just give the number"
    if "just give the number" in task_lower or "just the number" in task_lower:
        # Extract only the number
        import re
        numbers = re.findall(r'\d+', answer)
        if numbers:
            return numbers[0]

    # If task asks for a number and answer contains units, remove them
    if any(phrase in task_lower for phrase in ["how many", "what is the number", "minimum number", "maximum number"]):
        # Remove common units and extra text
        import re
        # Look for number followed by units
        match = re.search(r'(\d+)\s*(bags?|cups?|times?|hours?|years?|people?|items?|things?)', answer, re.IGNORECASE)
        if match:
            return match.group(1)

        # Look for written numbers and convert to digits
        word_to_num = {
            'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
            'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10'
        }
        answer_lower = answer.lower()
        for word, num in word_to_num.items():
            if answer_lower == word or answer_lower == word + '.':
                return num

    # If task asks for thousands of years, convert appropriately
    if "thousands of years" in task_lower and "years old" in answer:
        import re
        match = re.search(r'(\d+),?(\d+)?\s*years', answer)
        if match:
            if match.group(2):  # Has comma (e.g., "142,000")
                full_number = int(match.group(1) + match.group(2))
                return str(full_number // 1000)
            else:
                return match.group(1)

    # Remove extra explanatory text if it's just a simple answer
    if len(answer.split()) == 1:
        return answer

    # If answer starts with "The answer is" or similar, extract just the answer
    import re
    patterns = [
        r'^(?:The answer is|The result is|The number is|It is|This is)\s*:?\s*(.+)$',
        r'^(.+?)\s*(?:is the answer|is the result)\.?$'
    ]

    for pattern in patterns:
        match = re.search(pattern, answer, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return answer


async def run_task(task: str, file_path: str = None):
    """Run the task through GAIA agent and then through answer agent for concise response."""

    logger.info("🚀 Starting GAIA agent system...")
    logger.info(f"📋 Task: {task}")
    logger.info("-" * 50)
    logger.info(f"Processing task: {task}")

    # Step 1: Run the GAIA research agent with detailed logging
    logger.info("Initializing research agent")
    gaia_agent = get_gaia_agent()
    logger.info("🔍 Research agent working...")

    try:
        research_result = await Runner.run(gaia_agent, task)
        log_agent_output(research_result)
        research_output = research_result.final_output
        logger.info(f"Research complete. Output length: {len(research_output)} chars")

        # Get conversation history from research phase
        conversation_history = []
        for item in research_result.new_items:
            conversation_history.append(
                {"type": item.__class__.__name__, "content": str(item)}
            )
        logger.debug(f"Collected {len(conversation_history)} conversation items")

        logger.info("✅ Research complete!")
        logger.info("-" * 50)

    except Exception as e:
        logger.error(f"❌ Research agent failed: {e}")
        return None, None

    # Step 2: Pass to answer agent for concise response with detailed logging
    logger.info("Initializing answer agent")
    answer_agent = get_answer_agent()
    logger.info("📝 Answer agent synthesizing...")

    # Create input for answer agent with task and research
    answer_input = f"""Original Task: {task}

Research Agent Output:
{research_output}

Based on the research above, provide a clear, concise answer to the original task."""

    try:
        final_result = await Runner.run(answer_agent, answer_input)
        log_agent_output(final_result)
        raw_answer = final_result.final_output

        # Post-process the answer to ensure proper formatting
        final_answer = post_process_answer(raw_answer, task)
        logger.info(f"Raw answer: {raw_answer}")
        logger.info(f"Processed answer: {final_answer}")

        logger.info("\n✅ Final answer ready!")
        logger.info("=" * 50)
        logger.info("FINAL ANSWER:")
        logger.info(final_answer)
        logger.info("=" * 50)

        # Write the final answer to a file for the executor
        try:
            with open("final_answer.txt", "w") as f:
                f.write(final_answer)
            logger.info("Final answer written to final_answer.txt")
        except Exception as e:
            logger.error(f"Failed to write final answer to file: {e}")

        return final_answer, research_output

    except Exception as e:
        logger.error(f"❌ Answer agent failed: {e}")
        return None, research_output


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Simple argument parsing
    parser = argparse.ArgumentParser(description="Simple GAIA agent for solving tasks")
    parser.add_argument(
        "--task", type=str, required=True, help="The task/question to solve"
    )
    parser.add_argument(
        "--file_path",
        type=str,
        default=None,
        help="Path to a file to analyze for the task",
    )
    args = parser.parse_args()

    # Run the task
    asyncio.run(run_task(args.task, args.file_path))


if __name__ == "__main__":
    configure_logging()
    main()
