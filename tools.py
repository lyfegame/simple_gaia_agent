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
    Scrape content from a webpage with improved content extraction.

    Args:
        url: The URL to scrape
    """
    logger.info(f"Web scrape called for URL: {url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside", "advertisement"]):
            element.decompose()

        # Try to find main content areas first
        main_content = None
        for selector in ["main", "article", ".content", "#content", ".main", "#main"]:
            main_content = soup.select_one(selector)
            if main_content:
                break

        # If no main content found, use the whole body
        if not main_content:
            main_content = soup.find("body") or soup

        # Get text with better formatting
        text = main_content.get_text(separator="\n", strip=True)

        # Clean up the text
        lines = []
        for line in text.split("\n"):
            line = line.strip()
            if line and len(line) > 2:  # Skip very short lines
                lines.append(line)

        text = "\n".join(lines)

        # Limit length but try to keep complete sentences
        original_length = len(text)
        if len(text) > 15000:
            # Find a good cutoff point near 15000 characters
            cutoff = text.rfind(".", 0, 15000)
            if cutoff > 10000:  # Make sure we don't cut too much
                text = text[:cutoff + 1] + "\n\n[Content truncated...]"
            else:
                text = text[:15000] + "..."
            logger.info(f"Truncated content from {original_length} to {len(text)} chars")

        logger.info(f"Web scrape successful, content length: {len(text)}")
        return f"Content from {url}:\n\n{text}"
    except Exception as e:
        logger.error(f"Web scrape failed for {url}: {str(e)}")
        return f"Error scraping {url}: {str(e)}. Please try a different URL or search for the information using web search."


@function_tool
async def list_directory(directory: str = ".") -> str:
    """
    List contents of a directory to discover available files.

    Args:
        directory: Path to the directory to list (default: current directory)
    """
    logger.info(f"Directory listing called for: {directory}")
    try:
        import os
        from pathlib import Path

        dir_path = Path(directory)

        # Check if directory exists
        if not dir_path.exists():
            return f"Error: Directory '{directory}' does not exist."

        if not dir_path.is_dir():
            return f"Error: '{directory}' is not a directory."

        # List all files and directories
        items = []
        try:
            for item in sorted(dir_path.iterdir()):
                if item.is_file():
                    size = item.stat().st_size
                    items.append(f"📄 {item.name} ({size} bytes)")
                elif item.is_dir():
                    items.append(f"📁 {item.name}/")
        except PermissionError:
            return f"Error: Permission denied to access '{directory}'."

        if not items:
            return f"Directory '{directory}' is empty."

        result = f"Contents of '{directory}':\n" + "\n".join(items)
        logger.info(f"Directory listing successful, found {len(items)} items")
        return result

    except Exception as e:
        logger.error(f"Directory listing failed for {directory}: {str(e)}")
        return f"Error listing directory '{directory}': {str(e)}"


@function_tool
async def file_read(ctx: RunContextWrapper, filename: str) -> str:
    """
    Read content from a file with support for various file types.

    Args:
        filename: Path to the file
    """
    logger.info(f"File read called for: {filename}")
    try:
        import os
        from pathlib import Path

        file_path = Path(filename)

        # Check if file exists
        if not file_path.exists():
            return f"Error: File '{filename}' does not exist. Please check the file path."

        # Get file extension to determine how to read it
        extension = file_path.suffix.lower()

        # Handle different file types
        if extension in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv']:
            # Text-based files
            try:
                async with aiofiles.open(filename, "r", encoding="utf-8") as f:
                    content = await f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                async with aiofiles.open(filename, "r", encoding="latin-1") as f:
                    content = await f.read()
        elif extension in ['.docx']:
            return f"Error: DOCX files require special handling. Please use the code interpreter tool to process this file."
        elif extension in ['.xlsx', '.xls']:
            return f"Error: Excel files require special handling. Please use the code interpreter tool to process this file."
        elif extension in ['.pdf']:
            return f"Error: PDF files require special handling. Please use the code interpreter tool to process this file."
        elif extension in ['.mp3', '.wav', '.mp4', '.avi']:
            return f"Error: Media files require special handling. Please use the code interpreter tool to process this file."
        else:
            # Try to read as text anyway
            try:
                async with aiofiles.open(filename, "r", encoding="utf-8") as f:
                    content = await f.read()
            except Exception:
                return f"Error: Cannot read file '{filename}'. File type '{extension}' may require special handling. Please use the code interpreter tool."

        # Limit content length for very large files
        if len(content) > 50000:
            content = content[:50000] + f"\n\n[File truncated - showing first 50,000 characters of {len(content)} total]"
            logger.info(f"Truncated large file content")

        logger.info(f"File read successful, content length: {len(content)} chars")
        return f"Content of {filename}:\n\n{content}"

    except Exception as e:
        logger.error(f"File read failed for {filename}: {str(e)}")
        return f"Error reading {filename}: {str(e)}. Please check the file path and permissions."


# Available tools
GAIA_TOOLS = [
    WebSearchTool(),
    web_scrape,
    list_directory,
    file_read,
    CodeInterpreterTool(
        tool_config={"type": "code_interpreter", "container": {"type": "auto"}}
    ),
]
