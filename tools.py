"""
Advanced tools for the GAIA agent - comprehensive file format support and data analysis.
"""

import logging
import os
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Union

import aiofiles
import requests
import pandas as pd
import PyPDF2
from PIL import Image
from docx import Document
from pptx import Presentation
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
    Scrape content from a webpage with enhanced capabilities.

    Args:
        url: The URL to scrape
    """
    logger.info(f"Web scrape called for URL: {url}")
    try:
        # Enhanced headers to bypass basic anti-bot measures
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        # Try with session to maintain cookies
        session = requests.Session()
        session.headers.update(headers)

        response = session.get(url, timeout=30)
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
        if len(text) > 15000:
            text = text[:15000] + "..."
            logger.info(f"Truncated content from {original_length} to 15000 chars")

        logger.info(f"Web scrape successful, content length: {len(text)}")
        return f"Content from {url}:\n{text}"
    except Exception as e:
        logger.error(f"Web scrape failed for {url}: {str(e)}")
        return f"Error scraping {url}: {str(e)}"


@function_tool
async def wayback_machine_search(url: str, date: str = "") -> str:
    """
    Search for historical versions of a webpage using the Wayback Machine.

    Args:
        url: The URL to search for historical versions
        date: Optional date in YYYYMMDD format (e.g., "20210322"). If not provided, finds the latest available snapshot.
    """
    logger.info(f"Wayback Machine search called for URL: {url}, date: {date}")

    try:
        # Wayback Machine CDX API to find snapshots
        if date:
            # Search for snapshots on or before a specific date
            cdx_url = f"http://web.archive.org/cdx/search/cdx?url={url}&closest={date}&limit=1&output=json"
        else:
            # Get latest snapshot
            cdx_url = f"http://web.archive.org/cdx/search/cdx?url={url}&limit=1&output=json"

        headers = {"User-Agent": "Mozilla/5.0 (compatible; Research Bot)"}
        response = requests.get(cdx_url, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        if len(data) < 2:  # First row is headers
            return f"No archived versions found for {url}"

        # Extract the snapshot info
        snapshot = data[1]  # First actual result
        timestamp = snapshot[1]
        archived_url = f"http://web.archive.org/web/{timestamp}/{url}"

        logger.info(f"Found archived version: {archived_url}")

        # Now scrape the archived page
        archive_response = requests.get(archived_url, headers=headers, timeout=30)
        archive_response.raise_for_status()

        soup = BeautifulSoup(archive_response.text, "html.parser")

        # Remove Wayback Machine's own elements
        for element in soup.find_all(['div', 'script'], {'id': lambda x: x and 'wm-' in x}):
            element.decompose()
        for element in soup.find_all(class_=lambda x: x and 'wb-' in x):
            element.decompose()

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
        if len(text) > 15000:
            text = text[:15000] + "..."
            logger.info(f"Truncated archived content from {original_length} to 15000 chars")

        logger.info(f"Wayback Machine scrape successful, content length: {len(text)}")
        return f"Archived content from {url} (captured {timestamp[:8]}):\n{text}"

    except Exception as e:
        logger.error(f"Wayback Machine search failed for {url}: {str(e)}")
        return f"Error accessing archived version of {url}: {str(e)}"


@function_tool
async def github_search(query: str, search_type: str = "repositories") -> str:
    """
    Search GitHub repositories, issues, or other entities using GitHub's search API.

    Args:
        query: The search query (e.g., "opencv mask-rcnn", "repo:numpy/numpy label:regression")
        search_type: Type of search - "repositories", "issues", "code", "commits", "users"
    """
    logger.info(f"GitHub search called for query: {query}, type: {search_type}")

    try:
        # GitHub API endpoint
        base_url = "https://api.github.com/search"
        url = f"{base_url}/{search_type}"

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Research-Bot/1.0"
        }

        # Add GitHub token if available
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            headers["Authorization"] = f"token {github_token}"

        params = {
            "q": query,
            "sort": "updated",
            "order": "desc",
            "per_page": 10
        }

        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        total_count = data.get("total_count", 0)
        items = data.get("items", [])

        if not items:
            return f"No {search_type} found for query: {query}"

        result = f"GitHub {search_type} search results for '{query}' ({total_count} total):\n\n"

        for i, item in enumerate(items[:5], 1):  # Limit to top 5 results
            if search_type == "repositories":
                result += f"{i}. {item.get('full_name', 'Unknown')}\n"
                result += f"   Description: {item.get('description', 'No description')}\n"
                result += f"   Stars: {item.get('stargazers_count', 0)}\n"
                result += f"   URL: {item.get('html_url', '')}\n\n"

            elif search_type == "issues":
                result += f"{i}. {item.get('title', 'No title')}\n"
                result += f"   State: {item.get('state', 'unknown')}\n"
                result += f"   Labels: {', '.join([label['name'] for label in item.get('labels', [])])}\n"
                result += f"   Created: {item.get('created_at', 'unknown')}\n"
                result += f"   URL: {item.get('html_url', '')}\n\n"

            elif search_type == "code":
                result += f"{i}. {item.get('name', 'Unknown file')}\n"
                result += f"   Repository: {item.get('repository', {}).get('full_name', 'Unknown')}\n"
                result += f"   Path: {item.get('path', 'Unknown')}\n"
                result += f"   URL: {item.get('html_url', '')}\n\n"

            elif search_type == "commits":
                result += f"{i}. {item.get('commit', {}).get('message', 'No message')[:100]}...\n"
                result += f"   Author: {item.get('commit', {}).get('author', {}).get('name', 'Unknown')}\n"
                result += f"   Date: {item.get('commit', {}).get('author', {}).get('date', 'Unknown')}\n"
                result += f"   Repository: {item.get('repository', {}).get('full_name', 'Unknown')}\n"
                result += f"   URL: {item.get('html_url', '')}\n\n"

        logger.info(f"GitHub search successful, found {len(items)} results")
        return result

    except Exception as e:
        logger.error(f"GitHub search failed for query '{query}': {str(e)}")
        return f"Error searching GitHub for '{query}': {str(e)}"


@function_tool
async def github_get_repo_info(repo_path: str) -> str:
    """
    Get detailed information about a specific GitHub repository.

    Args:
        repo_path: Repository path in format "owner/repo" (e.g., "opencv/opencv")
    """
    logger.info(f"GitHub repo info called for: {repo_path}")

    try:
        url = f"https://api.github.com/repos/{repo_path}"

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Research-Bot/1.0"
        }

        # Add GitHub token if available
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            headers["Authorization"] = f"token {github_token}"

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        repo = response.json()

        result = f"Repository: {repo.get('full_name', 'Unknown')}\n"
        result += f"Description: {repo.get('description', 'No description')}\n"
        result += f"Language: {repo.get('language', 'Unknown')}\n"
        result += f"Stars: {repo.get('stargazers_count', 0)}\n"
        result += f"Forks: {repo.get('forks_count', 0)}\n"
        result += f"Created: {repo.get('created_at', 'Unknown')}\n"
        result += f"Updated: {repo.get('updated_at', 'Unknown')}\n"
        result += f"Default branch: {repo.get('default_branch', 'Unknown')}\n"
        result += f"Topics: {', '.join(repo.get('topics', []))}\n"
        result += f"URL: {repo.get('html_url', '')}\n"

        # Get contributors
        contributors_url = f"https://api.github.com/repos/{repo_path}/contributors"
        contributors_response = requests.get(contributors_url, headers=headers, timeout=30)
        if contributors_response.status_code == 200:
            contributors = contributors_response.json()
            result += f"\nTop contributors:\n"
            for i, contributor in enumerate(contributors[:10], 1):
                result += f"  {i}. {contributor.get('login', 'Unknown')} ({contributor.get('contributions', 0)} contributions)\n"

        logger.info(f"GitHub repo info retrieved successfully")
        return result

    except Exception as e:
        logger.error(f"GitHub repo info failed for {repo_path}: {str(e)}")
        return f"Error getting repository info for {repo_path}: {str(e)}"


@function_tool
async def parse_json_ld(content: str) -> str:
    """
    Parse JSON-LD content and extract structured data with intelligent analysis.

    Args:
        content: JSON-LD content as string
    """
    logger.info(f"JSON-LD parsing called")

    try:
        # Parse the JSON-LD
        data = json.loads(content)

        result = "JSON-LD Analysis:\n"
        result += "=" * 40 + "\n\n"

        # Basic structure info
        if isinstance(data, dict):
            result += f"Type: {data.get('@type', 'Unknown')}\n"
            result += f"Context: {data.get('@context', 'None')}\n"
            result += f"ID: {data.get('@id', 'None')}\n\n"

            # Extract ORCID IDs if present
            orcid_ids = []

            def extract_orcids(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if 'orcid' in key.lower() and isinstance(value, str):
                            if value.startswith('http'):
                                orcid_ids.append(value)
                            elif value.startswith('0000-'):
                                orcid_ids.append(f"https://orcid.org/{value}")
                        extract_orcids(value, f"{path}.{key}")
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        extract_orcids(item, f"{path}[{i}]")
                elif isinstance(obj, str) and 'orcid.org' in obj:
                    orcid_ids.append(obj)

            extract_orcids(data)

            if orcid_ids:
                result += f"ORCID IDs found: {len(orcid_ids)}\n"
                for i, orcid in enumerate(orcid_ids, 1):
                    result += f"  {i}. {orcid}\n"
                result += "\n"

            # Extract other identifiers
            identifiers = []
            def extract_identifiers(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key.lower() in ['id', 'identifier', '@id'] and isinstance(value, str):
                            identifiers.append(f"{key}: {value}")
                        extract_identifiers(value, f"{path}.{key}")
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        extract_identifiers(item, f"{path}[{i}]")

            extract_identifiers(data)

            if identifiers:
                result += f"Identifiers found:\n"
                for identifier in identifiers[:10]:  # Limit to first 10
                    result += f"  - {identifier}\n"
                result += "\n"

            # Extract names/titles
            names = []
            def extract_names(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key.lower() in ['name', 'title', 'givenname', 'familyname'] and isinstance(value, str):
                            names.append(f"{key}: {value}")
                        extract_names(value, f"{path}.{key}")
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        extract_names(item, f"{path}[{i}]")

            extract_names(data)

            if names:
                result += f"Names/Titles found:\n"
                for name in names[:10]:  # Limit to first 10
                    result += f"  - {name}\n"
                result += "\n"

            # Show raw structure (truncated)
            result += "Raw structure (key overview):\n"
            def show_structure(obj, indent=0, max_depth=3):
                if indent > max_depth:
                    return "..."
                if isinstance(obj, dict):
                    items = []
                    for key, value in list(obj.items())[:5]:  # Show first 5 keys
                        if isinstance(value, (dict, list)):
                            items.append(f"{'  ' * indent}{key}: {show_structure(value, indent+1, max_depth)}")
                        else:
                            items.append(f"{'  ' * indent}{key}: {type(value).__name__}")
                    if len(obj) > 5:
                        items.append(f"{'  ' * indent}... ({len(obj) - 5} more keys)")
                    return "{\n" + "\n".join(items) + "\n" + "  " * (indent-1) + "}"
                elif isinstance(obj, list):
                    if obj:
                        return f"[{len(obj)} items, first: {show_structure(obj[0], indent+1, max_depth)}]"
                    else:
                        return "[]"
                else:
                    return f"{type(obj).__name__}"

            result += show_structure(data)

        elif isinstance(data, list):
            result += f"Array with {len(data)} items\n"
            if data:
                result += f"First item type: {type(data[0]).__name__}\n"
                if isinstance(data[0], dict):
                    result += f"First item keys: {list(data[0].keys())[:10]}\n"

        logger.info(f"JSON-LD parsing successful")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"JSON-LD parsing failed - invalid JSON: {str(e)}")
        return f"Error: Invalid JSON format - {str(e)}"
    except Exception as e:
        logger.error(f"JSON-LD parsing failed: {str(e)}")
        return f"Error parsing JSON-LD: {str(e)}"


@function_tool
async def format_final_answer(answer: str, task_context: str = "") -> str:
    """
    Format the final answer according to common patterns and requirements.
    Handles capitalization, quotes, and other formatting issues.

    Args:
        answer: The raw answer to format
        task_context: Context from the original task to help with formatting decisions
    """
    logger.info(f"Answer formatting called for: {answer}")

    try:
        formatted_answer = answer.strip()

        # Remove common wrapping quotes if they seem unnecessary
        if (formatted_answer.startswith('"') and formatted_answer.endswith('"') and
            not ('quote' in task_context.lower() or 'quotation' in task_context.lower())):
            formatted_answer = formatted_answer[1:-1]

        if (formatted_answer.startswith("'") and formatted_answer.endswith("'") and
            not ('quote' in task_context.lower() or 'quotation' in task_context.lower())):
            formatted_answer = formatted_answer[1:-1]

        # Handle specific formatting based on context clues
        context_lower = task_context.lower()

        # Capitalization rules
        if ('proper noun' in context_lower or 'name' in context_lower or
            'title' in context_lower or 'capitalize' in context_lower):
            # Capitalize first letter of each word for names/titles
            formatted_answer = formatted_answer.title()
        elif ('sentence' in context_lower or 'capitalize first' in context_lower):
            # Capitalize first letter only
            formatted_answer = formatted_answer.capitalize()
        elif 'lowercase' in context_lower:
            formatted_answer = formatted_answer.lower()
        elif 'uppercase' in context_lower:
            formatted_answer = formatted_answer.upper()
        elif len(formatted_answer.split()) == 1 and formatted_answer.isalpha():
            # Single word answers - check if it's the start of a sentence context
            if any(phrase in context_lower for phrase in ['if you understand', 'write the', 'answer with']):
                formatted_answer = formatted_answer.capitalize()

        # Number formatting
        if 'just the number' in context_lower or 'only the number' in context_lower:
            # Extract just the number if there's extra text
            import re
            numbers = re.findall(r'-?\d+\.?\d*', formatted_answer)
            if numbers:
                formatted_answer = numbers[0]

        # Handle "Format Document" type answers - remove quotes if present
        if 'command' in context_lower and formatted_answer.startswith('"') and formatted_answer.endswith('"'):
            formatted_answer = formatted_answer[1:-1]

        # List formatting
        if 'comma delimited' in context_lower or 'comma separated' in context_lower:
            # Ensure proper comma-space formatting
            if ',' in formatted_answer:
                items = [item.strip() for item in formatted_answer.split(',')]
                formatted_answer = ', '.join(items)

        # Alphabetical sorting if requested
        if 'alphabetically' in context_lower or 'sorted alphabetically' in context_lower:
            if ',' in formatted_answer:
                items = [item.strip() for item in formatted_answer.split(',')]
                items.sort()
                formatted_answer = ', '.join(items)

        logger.info(f"Answer formatted from '{answer}' to '{formatted_answer}'")
        return formatted_answer

    except Exception as e:
        logger.error(f"Answer formatting failed: {str(e)}")
        return answer  # Return original if formatting fails


@function_tool
async def file_analyze(filename: str = "") -> str:
    """
    Analyze and list all available files in current directory and subdirectories.

    Args:
        filename: Optional specific filename to analyze. If empty, lists all files.
    """
    logger.info(f"File analyze called for: {filename if filename else 'all files'}")

    try:
        if filename and os.path.exists(filename):
            # Analyze specific file
            file_path = Path(filename)
            file_size = file_path.stat().st_size
            file_type = file_path.suffix.lower()

            result = f"File: {filename} ({file_size} bytes)\nType: {file_type}\n\n"

            # Try to read content based on type
            if file_type in ['.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv']:
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(content) > 500:
                            content = content[:500] + "..."
                        result += f"Text file content ({len(content)} characters):\n{content}"
                except:
                    result += "Could not read text content"

            elif file_type in ['.xlsx', '.xls']:
                try:
                    df = pd.read_excel(filename, nrows=10)
                    result += f"Excel file preview:\nColumns: {list(df.columns)}\nRows: {len(df)}\nFirst few rows:\n{df.head()}"
                except:
                    result += "Could not read Excel content"

            elif file_type == '.pdf':
                try:
                    with open(filename, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        pages = len(reader.pages)
                        first_page = reader.pages[0].extract_text()[:500] + "..." if reader.pages else ""
                        result += f"PDF file: {pages} pages\nFirst page preview:\n{first_page}"
                except:
                    result += "Could not read PDF content"

            return result
        else:
            # List files, prioritizing task folder and gaia files
            important_files = []
            other_files = []

            for root, dirs, files in os.walk('.'):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        file_info = f"{file_path} ({size} bytes)"

                        # Prioritize task files and gaia data files
                        if ('task/' in file_path or 'gaia/files' in file_path or
                            file_path.endswith(('.xlsx', '.pdf', '.txt', '.csv', '.mp3', '.jpg', '.png'))):
                            important_files.append(file_info)
                        else:
                            other_files.append(file_info)
                    except:
                        file_info = f"{file_path} (size unknown)"
                        if 'task/' in file_path or 'gaia/files' in file_path:
                            important_files.append(file_info)
                        else:
                            other_files.append(file_info)

            # Limit output to prevent context overflow
            result = "Important/Data files:\n" + "\n".join(sorted(important_files))
            if len(other_files) > 50:
                result += f"\n\nOther files: {len(other_files)} files (listing truncated for brevity)"
            else:
                result += "\n\nOther files:\n" + "\n".join(sorted(other_files[:50]))

            logger.info(f"Listed {len(important_files)} important files, {len(other_files)} other files")
            return result

    except Exception as e:
        logger.error(f"File analyze failed: {str(e)}")
        return f"Error analyzing files: {str(e)}"


@function_tool
async def file_read(filename: str) -> str:
    """
    Advanced file reader supporting multiple formats including Excel, PDF, images, audio, etc.

    Args:
        filename: Path to the file to read
    """
    logger.info(f"File read called for: {filename}")

    if not os.path.exists(filename):
        # Try to find the file in common locations
        possible_paths = [
            filename,
            f"task/{filename}",
            f"task/data.{filename.split('.')[-1]}",
            f"gaia/files/{filename}",
        ]

        # Also search for files with similar names
        if "/" in filename:
            base_name = filename.split("/")[-1]
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if file == base_name or filename.endswith(file):
                        possible_paths.append(os.path.join(root, file))

        found_file = None
        for path in possible_paths:
            if os.path.exists(path):
                found_file = path
                logger.info(f"Found file at: {path}")
                break

        if not found_file:
            error_msg = f"File not found: {filename}. Searched in: {possible_paths}"
            logger.error(error_msg)
            return f"Error reading {filename}: [Errno 2] No such file or directory: '{filename}'"

        filename = found_file

    try:
        file_path = Path(filename)
        file_ext = file_path.suffix.lower()

        logger.info(f"Processing file type: {file_ext}")

        # Handle different file types
        if file_ext in ['.txt', '.py', '.js', '.html', '.css', '.json', '.xml']:
            async with aiofiles.open(filename, "r", encoding='utf-8') as f:
                content = await f.read()
                logger.info(f"File read successful, content length: {len(content)} chars")
                return content

        elif file_ext in ['.xlsx', '.xls']:
            try:
                # Try multiple engines for better compatibility
                engines = ['openpyxl', 'xlrd', None]  # None lets pandas choose

                for engine in engines:
                    try:
                        if engine:
                            excel_file = pd.ExcelFile(filename, engine=engine)
                        else:
                            excel_file = pd.ExcelFile(filename)
                        break
                    except Exception as e:
                        if engine == engines[-1]:  # Last engine failed
                            raise e
                        continue

                result = f"Excel file with sheets: {excel_file.sheet_names}\n\n"

                for sheet_name in excel_file.sheet_names:
                    try:
                        if engine:
                            df = pd.read_excel(filename, sheet_name=sheet_name, engine=engine)
                        else:
                            df = pd.read_excel(filename, sheet_name=sheet_name)

                        result += f"Sheet '{sheet_name}':\n"
                        result += f"Shape: {df.shape}\n"
                        result += f"Columns: {list(df.columns)}\n"

                        # Show data with better formatting
                        if df.shape[0] > 20:
                            result += f"Data (first 20 rows):\n{df.head(20).to_string()}\n"
                            result += f"... ({df.shape[0] - 20} more rows)\n\n"
                        else:
                            result += f"Data:\n{df.to_string()}\n\n"

                    except Exception as sheet_error:
                        result += f"Sheet '{sheet_name}': Error reading - {str(sheet_error)}\n\n"

                logger.info(f"Excel file read successful, {len(excel_file.sheet_names)} sheets")
                return result
            except Exception as e:
                # Enhanced error message with troubleshooting info
                error_msg = f"Error reading Excel file: {str(e)}\n"
                error_msg += "Troubleshooting info:\n"
                error_msg += f"- File exists: {os.path.exists(filename)}\n"
                error_msg += f"- File size: {os.path.getsize(filename) if os.path.exists(filename) else 'N/A'} bytes\n"
                error_msg += f"- File extension: {file_ext}\n"
                error_msg += "- Try installing: pip install openpyxl xlrd\n"
                return error_msg

        elif file_ext == '.csv':
            try:
                df = pd.read_csv(filename)
                result = f"CSV file shape: {df.shape}\n"
                result += f"Columns: {list(df.columns)}\n"
                result += f"Data:\n{df.to_string()}"
                logger.info(f"CSV file read successful, shape: {df.shape}")
                return result
            except Exception as e:
                return f"Error reading CSV file: {str(e)}"

        elif file_ext == '.pdf':
            try:
                with open(filename, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text_content = ""
                    for page_num, page in enumerate(reader.pages):
                        text_content += f"\n--- Page {page_num + 1} ---\n"
                        text_content += page.extract_text()

                logger.info(f"PDF read successful, {len(reader.pages)} pages")
                return f"PDF Content ({len(reader.pages)} pages):\n{text_content}"
            except Exception as e:
                return f"Error reading PDF file: {str(e)}"

        elif file_ext in ['.docx']:
            try:
                doc = Document(filename)
                content = ""
                for paragraph in doc.paragraphs:
                    content += paragraph.text + "\n"
                logger.info(f"DOCX file read successful")
                return f"DOCX Content:\n{content}"
            except Exception as e:
                return f"Error reading DOCX file: {str(e)}"

        elif file_ext in ['.pptx']:
            try:
                prs = Presentation(filename)
                content = ""
                for slide_num, slide in enumerate(prs.slides):
                    content += f"\n--- Slide {slide_num + 1} ---\n"
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            content += shape.text + "\n"
                logger.info(f"PPTX file read successful, {len(prs.slides)} slides")
                return f"PPTX Content ({len(prs.slides)} slides):\n{content}"
            except Exception as e:
                return f"Error reading PPTX file: {str(e)}"

        elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            try:
                with Image.open(filename) as img:
                    info = {
                        'format': img.format,
                        'mode': img.mode,
                        'size': img.size,
                        'filename': filename
                    }
                logger.info(f"Image file analyzed: {info}")
                return f"Image file: {json.dumps(info, indent=2)}\nNote: Image content analysis would require vision capabilities."
            except Exception as e:
                return f"Error reading image file: {str(e)}"

        elif file_ext in ['.mp3', '.wav', '.m4a']:
            try:
                # Basic audio file info
                file_size = os.path.getsize(filename)
                logger.info(f"Audio file detected: {filename}, size: {file_size}")
                return f"Audio file: {filename}\nSize: {file_size} bytes\nNote: Audio transcription would require speech-to-text capabilities."
            except Exception as e:
                return f"Error reading audio file: {str(e)}"

        elif file_ext == '.zip':
            try:
                with zipfile.ZipFile(filename, 'r') as zip_file:
                    file_list = zip_file.namelist()
                    content = f"ZIP file contents ({len(file_list)} files):\n"
                    for file_name in file_list:
                        content += f"  - {file_name}\n"

                    # Extract and read small text files
                    for file_name in file_list[:5]:  # Limit to first 5 files
                        if file_name.endswith(('.txt', '.csv', '.json', '.xml')):
                            try:
                                with zip_file.open(file_name) as inner_file:
                                    inner_content = inner_file.read().decode('utf-8')
                                    if len(inner_content) < 1000:
                                        content += f"\nContent of {file_name}:\n{inner_content}\n"
                                    else:
                                        content += f"\nContent of {file_name} (truncated):\n{inner_content[:500]}...\n"
                            except:
                                content += f"\nCould not read {file_name}\n"

                logger.info(f"ZIP file processed, {len(file_list)} files")
                return content
            except Exception as e:
                return f"Error reading ZIP file: {str(e)}"

        elif file_ext in ['.jsonld']:
            try:
                async with aiofiles.open(filename, "r", encoding='utf-8') as f:
                    content = await f.read()
                    # Try to parse as JSON for better formatting
                    try:
                        json_data = json.loads(content)
                        formatted_content = json.dumps(json_data, indent=2)
                        logger.info(f"JSON-LD file read and formatted successfully")
                        return f"JSON-LD Content:\n{formatted_content}"
                    except:
                        logger.info(f"JSON-LD file read as text")
                        return f"JSON-LD Content (raw):\n{content}"
            except Exception as e:
                return f"Error reading JSON-LD file: {str(e)}"

        else:
            # Fallback: try to read as text
            try:
                async with aiofiles.open(filename, "r", encoding='utf-8') as f:
                    content = await f.read()
                    logger.info(f"File read as text, content length: {len(content)} chars")
                    return content
            except:
                # If text reading fails, read as binary and show info
                file_size = os.path.getsize(filename)
                logger.info(f"Binary file detected: {filename}, size: {file_size}")
                return f"Binary file: {filename}\nSize: {file_size} bytes\nFile type: {file_ext}\nNote: Binary content cannot be displayed as text."

    except Exception as e:
        logger.error(f"File read failed for {filename}: {str(e)}")
        return f"Error reading {filename}: {str(e)}"


# Available tools
GAIA_TOOLS = [
    WebSearchTool(),
    web_scrape,
    wayback_machine_search,
    github_search,
    github_get_repo_info,
    parse_json_ld,
    format_final_answer,
    file_read,
    file_analyze,
    CodeInterpreterTool(
        tool_config={"type": "code_interpreter", "container": {"type": "auto"}}
    ),
]

# Tools specifically for answer formatting
ANSWER_TOOLS = [
    format_final_answer,
]