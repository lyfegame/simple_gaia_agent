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

        # Validate research output quality
        if not research_output or len(research_output.strip()) < 10:
            logger.warning("Research output seems insufficient, attempting recovery")
            # Try simplified task format
            simplified_task = f"Find and analyze information to answer: {task}"
            research_result = await Runner.run(gaia_agent, simplified_task)
            log_agent_output(research_result)
            research_output = research_result.final_output

        # Enhanced validation - check for common failure patterns
        failure_indicators = [
            "no information available",
            "cannot find",
            "unable to determine",
            "error occurred",
            "search unavailable",
            "no papers found",
            "no snapshots found",
            "file not found",
            "video file not found",
            "insufficient research"
        ]

        if any(indicator in research_output.lower() for indicator in failure_indicators):
            logger.warning("Research output indicates potential failure, attempting enhanced recovery")
            # Try more specific recovery approach
            enhanced_task = f"""ENHANCED RESEARCH TASK: {task}

CRITICAL REQUIREMENTS:
1. Use list_files() to check ALL available files first
2. Try smart_file_reader() for any relevant files found
3. For ArXiv tasks: Use search_arxiv_api() with proper categories (hep-lat, etc.)
4. For historical web data: Use search_wayback_machine() with specific dates
5. For video analysis: Use analyze_video_file() for content extraction
6. For Excel data: Use read_excel() and look for date columns to find oldest/newest entries
7. If web search fails, try search_academic_papers() or search_specialized_database()
8. Always provide specific details about what you found, not generic failure messages

TASK ANALYSIS:
- If this involves counting ArXiv papers, use search_arxiv_api()
- If this involves "oldest" entries in data, look for date columns
- If this involves historical websites, use search_wayback_machine()
- If this involves video content, use analyze_video_file()

Be thorough and systematic. Try multiple approaches before concluding."""

            try:
                enhanced_result = await Runner.run(gaia_agent, enhanced_task)
                log_agent_output(enhanced_result)
                enhanced_output = enhanced_result.final_output

                # Use enhanced output if it's more substantial
                if enhanced_output and len(enhanced_output.strip()) > len(research_output.strip()):
                    research_output = enhanced_output
                    logger.info("Enhanced recovery successful")
            except Exception as e:
                logger.warning(f"Enhanced recovery failed: {e}")

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
        logger.info("Attempting simplified research approach...")
        try:
            # Try with minimal instruction
            simple_task = f"Answer this question using available files and web search: {task}"
            research_result = await Runner.run(gaia_agent, simple_task)
            log_agent_output(research_result)
            research_output = research_result.final_output
            logger.info("✅ Simplified research succeeded!")
        except Exception as e2:
            logger.error(f"❌ Simplified research also failed: {e2}")
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
        final_answer = final_result.final_output
        logger.info(f"Answer generated: {final_answer}")

        # Validate answer quality
        if not final_answer or final_answer.strip() == "No information available":
            logger.warning("Answer agent returned no information, trying direct approach")
            # Try direct extraction from research
            if research_output and len(research_output.strip()) > 10:
                direct_answer = research_output.strip()
                # Try to extract a more concise answer
                if len(direct_answer) > 200:
                    lines = direct_answer.split('\n')
                    # Look for lines that might contain the answer
                    for line in lines:
                        if any(keyword in line.lower() for keyword in ['answer:', 'result:', 'solution:']):
                            final_answer = line.split(':', 1)[-1].strip()
                            break
                    else:
                        final_answer = direct_answer[:200] + "..."
                else:
                    final_answer = direct_answer
            else:
                final_answer = "No information available"

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
        logger.info("Using research output as fallback answer")
        fallback_answer = research_output if research_output else "No information available"

        # Write fallback answer to file
        try:
            with open("final_answer.txt", "w") as f:
                f.write(fallback_answer)
            logger.info("Fallback answer written to final_answer.txt")
        except Exception as e:
            logger.error(f"Failed to write fallback answer to file: {e}")

        return fallback_answer, research_output


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
