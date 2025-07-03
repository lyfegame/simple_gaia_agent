"""
Tools for the GAIA agent - web search and web scraping.
"""

import logging

import aiofiles
import requests
from agents import (
    RunContextWrapper,
    function_tool,
    CodeInterpreterTool,
)
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize AsyncOpenAI client lazily
_client = None


def get_client():
    """Get or create the AsyncOpenAI client."""
    global _client
    if _client is None:
        _client = AsyncOpenAI()
    return _client


@function_tool
async def web_search(query: str) -> str:
    """
    Search the web for information.

    Args:
        query: The search query
    """
    logger.info(f"Web search called with query: {query}")
    try:
        client = get_client()
        response = await client.responses.create(
            model="gpt-4.1", tools=[{"type": "web_search_preview"}], input=query
        )
        logger.info(
            f"Web search successful, response length: {len(response.output_text)}"
        )
        return response.output_text
    except Exception as e:
        logger.error(f"Web search failed: {str(e)}")
        return f"Web search error: {str(e)}"


@function_tool
async def web_scrape(url: str) -> str:
    """
    Scrape content from a webpage.

    Args:
        url: The URL to scrape
    """
    logger.info(f"Web scrape called for URL: {url}")
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)

        # Limit length
        original_length = len(text)
        if len(text) > 10000:
            text = text[:10000] + "..."
            logger.info(f"Truncated content from {original_length} to 10000 chars")

        logger.info(f"Web scrape successful, content length: {len(text)}")
        return f"Content from {url}:\n{text}"
    except Exception as e:
        logger.error(f"Web scrape failed for {url}: {str(e)}")
        return f"Error scraping {url}: {str(e)}"


@function_tool
async def file_read(ctx: RunContextWrapper, filename: str) -> str:
    """
    Read content from a file.

    Args:
        filename: Path to the file
    """
    logger.info(f"File read called for: {filename}")
    try:
        async with aiofiles.open(filename, "r") as f:
            content = await f.read()
        logger.info(f"File read successful, content length: {len(content)} chars")
        return content
    except Exception as e:
        logger.error(f"File read failed for {filename}: {str(e)}")
        return f"Error reading {filename}: {str(e)}"


# Available tools
GAIA_TOOLS = [
    web_search,
    web_scrape,
    file_read,
    CodeInterpreterTool(
        tool_config={"type": "code_interpreter", "container": {"type": "auto"}}
    ),
]
