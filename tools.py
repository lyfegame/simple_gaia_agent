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
    Read content from a file. Handles various file formats and Git LFS files.

    Args:
        filename: Path to the file
    """
    logger.info(f"File read called for: {filename}")

    import os
    from pathlib import Path

    try:
        file_path = Path(filename)

        # Check if file exists
        if not file_path.exists():
            return f"Error: File {filename} does not exist"

        # Check if it's a Git LFS file
        with open(file_path, 'rb') as f:
            first_line = f.readline().decode('utf-8', errors='ignore').strip()
            if first_line.startswith('version https://git-lfs.github.com/spec/v1'):
                return f"Error: File {filename} is stored with Git LFS and content is not available. The file appears to be a {file_path.suffix} file that needs to be downloaded from Git LFS first."

        # Handle different file types
        file_extension = file_path.suffix.lower()

        if file_extension in ['.txt', '.md', '.py', '.json', '.csv', '.jsonl']:
            # Text files
            async with aiofiles.open(filename, "r", encoding='utf-8', errors='ignore') as f:
                content = await f.read()
            logger.info(f"Text file read successful, content length: {len(content)} chars")
            return content

        elif file_extension in ['.pdf']:
            return f"Error: PDF file {filename} requires special handling. The file appears to be stored with Git LFS and is not directly accessible."

        elif file_extension in ['.xlsx', '.xls']:
            return f"Error: Excel file {filename} requires special handling. The file appears to be stored with Git LFS and is not directly accessible."

        elif file_extension in ['.png', '.jpg', '.jpeg', '.gif']:
            return f"Error: Image file {filename} requires special handling. The file appears to be stored with Git LFS and is not directly accessible."

        elif file_extension in ['.mp3', '.wav']:
            return f"Error: Audio file {filename} requires special handling. The file appears to be stored with Git LFS and is not directly accessible."

        elif file_extension in ['.zip']:
            return f"Error: Archive file {filename} requires extraction. The file appears to be stored with Git LFS and is not directly accessible."

        else:
            # Try to read as text
            try:
                async with aiofiles.open(filename, "r", encoding='utf-8', errors='ignore') as f:
                    content = await f.read()
                logger.info(f"File read as text successful, content length: {len(content)} chars")
                return content
            except:
                return f"Error: Cannot read file {filename}. Unsupported file type {file_extension} or file is binary."

    except Exception as e:
        logger.error(f"File read failed for {filename}: {str(e)}")
        return f"Error reading {filename}: {str(e)}"


@function_tool
async def list_files(directory: str = ".") -> str:
    """
    List files and directories in the specified directory.

    Args:
        directory: Path to the directory to list (default: current directory)
    """
    logger.info(f"List files called for directory: {directory}")

    import os
    from pathlib import Path

    try:
        dir_path = Path(directory)

        if not dir_path.exists():
            return f"Error: Directory {directory} does not exist"

        if not dir_path.is_dir():
            return f"Error: {directory} is not a directory"

        items = []
        for item in sorted(dir_path.iterdir()):
            if item.is_file():
                size = item.stat().st_size
                # Check if it's a Git LFS file
                try:
                    with open(item, 'rb') as f:
                        first_line = f.readline().decode('utf-8', errors='ignore').strip()
                        if first_line.startswith('version https://git-lfs.github.com/spec/v1'):
                            items.append(f"📄 {item.name} (Git LFS file, {item.suffix})")
                        else:
                            items.append(f"📄 {item.name} ({size} bytes)")
                except:
                    items.append(f"📄 {item.name} ({size} bytes)")
            elif item.is_dir():
                items.append(f"📁 {item.name}/")

        if not items:
            return f"Directory {directory} is empty"

        result = f"Contents of {directory}:\n" + "\n".join(items)
        logger.info(f"Listed {len(items)} items in {directory}")
        return result

    except Exception as e:
        logger.error(f"List files failed for {directory}: {str(e)}")
        return f"Error listing {directory}: {str(e)}"


@function_tool
async def extract_and_list_zip(zip_path: str) -> str:
    """
    Extract and list contents of a zip file (if not Git LFS).

    Args:
        zip_path: Path to the zip file
    """
    logger.info(f"Extract and list zip called for: {zip_path}")

    import zipfile
    import tempfile
    import os
    from pathlib import Path

    try:
        zip_file_path = Path(zip_path)

        if not zip_file_path.exists():
            return f"Error: Zip file {zip_path} does not exist"

        # Check if it's a Git LFS file
        with open(zip_file_path, 'rb') as f:
            first_line = f.readline().decode('utf-8', errors='ignore').strip()
            if first_line.startswith('version https://git-lfs.github.com/spec/v1'):
                return f"Error: Zip file {zip_path} is stored with Git LFS and cannot be extracted. The file is not directly accessible."

        # Try to extract and list contents
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                # List extracted contents
                extracted_items = []
                temp_path = Path(temp_dir)

                for item in temp_path.rglob('*'):
                    if item.is_file():
                        relative_path = item.relative_to(temp_path)
                        size = item.stat().st_size
                        extracted_items.append(f"📄 {relative_path} ({size} bytes)")
                    elif item.is_dir() and item != temp_path:
                        relative_path = item.relative_to(temp_path)
                        extracted_items.append(f"📁 {relative_path}/")

                if not extracted_items:
                    return f"Zip file {zip_path} is empty"

                result = f"Contents of {zip_path}:\n" + "\n".join(extracted_items)
                logger.info(f"Successfully extracted and listed {len(extracted_items)} items from {zip_path}")
                return result

            except zipfile.BadZipFile:
                return f"Error: {zip_path} is not a valid zip file"
            except Exception as e:
                return f"Error extracting {zip_path}: {str(e)}"

    except Exception as e:
        logger.error(f"Extract zip failed for {zip_path}: {str(e)}")
        return f"Error processing {zip_path}: {str(e)}"


@function_tool
async def search_and_scrape(query: str, max_results: int = 3) -> str:
    """
    Search the web and automatically scrape the top results for comprehensive information.

    Note: This function cannot directly perform web searches as the WebSearchTool is designed for LLM use only.
    Instead, it provides guidance on using the web_search tool.

    Args:
        query: Search query
        max_results: Maximum number of results to scrape (default: 3)
    """
    logger.info(f"Search and scrape called for query: {query}")

    return f"""To search for "{query}", you should use the web_search tool directly in your conversation.

The search_and_scrape function cannot directly perform web searches as the WebSearchTool is designed for LLM use only.

Instead, please:
1. Use the web_search tool to search for: {query}
2. Then use web_scrape to scrape specific URLs from the search results
3. Or use the ResponseFunctionWebSearch in your conversation

This approach will give you better results than this combined function."""


# Available tools
GAIA_TOOLS = [
    WebSearchTool(),
    web_scrape,
    search_and_scrape,
    file_read,
    list_files,
    extract_and_list_zip,
    CodeInterpreterTool(
        tool_config={"type": "code_interpreter", "container": {"type": "auto"}}
    ),
]
