"""
GAIA Agent definitions - Research agent and Answer agent.
"""

import logging

from agents import Agent

from tools import GAIA_TOOLS

# Set up logging
logger = logging.getLogger(__name__)

# Research agent with full capabilities
gaia_agent = Agent(
    name="gaia_research_agent",
    instructions="""You are a GAIA research agent designed to solve complex reasoning and research tasks.

Your approach:
1. Carefully analyze the task
2. Use web search to find relevant information
3. Use web scraping for detailed content from specific pages
4. Read files when provided
5. Gather comprehensive information

Remember to:
- Search multiple sources
- Extract detailed information
- Be thorough in your research
""",
    tools=GAIA_TOOLS,
)

# Answer agent that synthesizes concise responses
answer_agent = Agent(
    name="gaia_answer_agent",
    instructions="""You are an answer synthesis agent. Your role is to:

1. Review the research provided by the research agent
2. Extract the key answer to the original task
3. Provide a clear, concise, and direct answer

Guidelines:
- Be extremely concise - usually 1-3 sentences
- Focus only on answering the specific question asked
- Include only the most essential information
- If the answer is a number, date, or name - just provide that
- Don't include explanations unless specifically asked
""",
    tools=[],  # No tools needed - just synthesis
)


def get_gaia_agent() -> Agent:
    """Get the GAIA research agent."""
    logger.debug("Creating GAIA research agent")
    return gaia_agent


def get_answer_agent() -> Agent:
    """Get the answer synthesis agent."""
    logger.debug("Creating answer synthesis agent")
    return answer_agent
