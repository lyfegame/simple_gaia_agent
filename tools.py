"""
Tools for the GAIA agent - web search and web scraping.
"""

import aiofiles
import requests
from agents import RunContextWrapper, function_tool
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import AsyncOpenAI

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
    try:
        client = get_client()
        response = await client.responses.create(
            model="gpt-4.1", tools=[{"type": "web_search_preview"}], input=query
        )
        return response.output_text
    except Exception as e:
        return f"Web search error: {str(e)}"


@function_tool
async def web_scrape(url: str) -> str:
    """
    Scrape content from a webpage.

    Args:
        url: The URL to scrape
    """
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
        if len(text) > 10000:
            text = text[:10000] + "..."

        return f"Content from {url}:\n{text}"
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"


@function_tool
async def file_read(ctx: RunContextWrapper, filename: str) -> str:
    """
    Read content from a file.

    Args:
        filename: Path to the file
    """
    try:
        async with aiofiles.open(filename, "r") as f:
            content = await f.read()
        return content
    except Exception as e:
        return f"Error reading {filename}: {str(e)}"


# Available tools
GAIA_TOOLS = [web_search, web_scrape, file_read]
