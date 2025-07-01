"""
Tools for the GAIA agent - web search and web scraping.
"""

import logging

import aiofiles
import requests
from agents import (
    RunContextWrapper,
    function_tool,
    WebSearchTool,
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
    except FileNotFoundError:
        logger.warning(f"File not found: {filename}")
        # Try common alternative paths
        import os
        from pathlib import Path

        alternatives = []
        base_name = os.path.basename(filename)

        # Try in current directory
        if os.path.exists(base_name):
            alternatives.append(base_name)

        # Try in task folder
        task_path = f"task/{base_name}"
        if os.path.exists(task_path):
            alternatives.append(task_path)

        # Try in gaia/files
        gaia_path = f"gaia/files/{base_name}"
        if os.path.exists(gaia_path):
            alternatives.append(gaia_path)

        if alternatives:
            logger.info(f"Found alternative file: {alternatives[0]}")
            try:
                async with aiofiles.open(alternatives[0], "r") as f:
                    content = await f.read()
                logger.info(f"Alternative file read successful, content length: {len(content)} chars")
                return content
            except Exception as e2:
                logger.error(f"Alternative file read failed: {str(e2)}")

        return f"File not found: {filename}. Tried alternatives: {alternatives}. Consider using web search to find the information instead."
    except Exception as e:
        logger.error(f"File read failed for {filename}: {str(e)}")
        return f"Error reading {filename}: {str(e)}. Consider using web search to find the information instead."


@function_tool
async def list_files(ctx: RunContextWrapper, directory: str = ".") -> str:
    """
    List files in a directory to help find available files.

    Args:
        directory: Directory path to list (default: current directory)
    """
    logger.info(f"Listing files in directory: {directory}")
    try:
        import os
        files = []
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                rel_path = os.path.relpath(os.path.join(root, filename), directory)
                files.append(rel_path)

        if not files:
            return f"No files found in directory: {directory}"

        # Limit to first 50 files to avoid overwhelming output
        if len(files) > 50:
            files = files[:50]
            result = f"Files in {directory} (showing first 50 of {len(files)}):\n" + "\n".join(files)
        else:
            result = f"Files in {directory}:\n" + "\n".join(files)

        logger.info(f"Listed {len(files)} files in {directory}")
        return result
    except Exception as e:
        logger.error(f"Failed to list files in {directory}: {str(e)}")
        return f"Error listing files in {directory}: {str(e)}"


@function_tool
async def check_file_exists(ctx: RunContextWrapper, filename: str) -> str:
    """
    Check if a file exists and suggest alternatives if not.

    Args:
        filename: Path to the file to check
    """
    logger.info(f"Checking if file exists: {filename}")
    import os

    if os.path.exists(filename):
        return f"File exists: {filename}"

    # Look for similar files
    base_name = os.path.basename(filename)
    alternatives = []

    # Check common directories
    for directory in [".", "task", "gaia/files", "data"]:
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file == base_name or base_name.lower() in file.lower():
                        alternatives.append(os.path.join(root, file))

    if alternatives:
        return f"File not found: {filename}\nSimilar files found: {alternatives[:5]}"
    else:
        return f"File not found: {filename}\nNo similar files found. Consider using web search for the information."


# Available tools
GAIA_TOOLS = [
    WebSearchTool(),
    web_scrape,
    file_read,
    list_files,
    check_file_exists,
    CodeInterpreterTool(
        tool_config={"type": "code_interpreter", "container": {"type": "auto"}}
    ),
]
