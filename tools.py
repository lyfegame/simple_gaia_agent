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
        if len(text) > 15000:
            text = text[:15000] + "..."
            logger.info(f"Truncated content from {original_length} to 15000 chars")

        logger.info(f"Web scrape successful, content length: {len(text)}")
        return f"Content from {url}:\n{text}"
    except Exception as e:
        logger.error(f"Web scrape failed for {url}: {str(e)}")
        return f"Error scraping {url}: {str(e)}"


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
                # Read all sheets
                excel_file = pd.ExcelFile(filename)
                result = f"Excel file with sheets: {excel_file.sheet_names}\n\n"

                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(filename, sheet_name=sheet_name)
                    result += f"Sheet '{sheet_name}':\n"
                    result += f"Shape: {df.shape}\n"
                    result += f"Columns: {list(df.columns)}\n"
                    result += f"Data:\n{df.to_string()}\n\n"

                logger.info(f"Excel file read successful, {len(excel_file.sheet_names)} sheets")
                return result
            except Exception as e:
                return f"Error reading Excel file: {str(e)}"

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
    file_read,
    file_analyze,
    CodeInterpreterTool(
        tool_config={"type": "code_interpreter", "container": {"type": "auto"}}
    ),
]