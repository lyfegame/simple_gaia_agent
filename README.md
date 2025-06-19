# Simple GAIA Agent

A barebones implementation of a two-agent system for solving GAIA benchmark tasks.

## Quick Start

```bash
# Clone the repository and navigate to it
cd simple_gaia_agent

# Run the installation script
./install.sh

# Create a .env file with your API key (recommended)
echo "OPENAI_API_KEY=your-actual-api-key-here" > .env

# Or export it as an environment variable
export OPENAI_API_KEY='your-actual-api-key-here'

# Run your first task
./run.sh --task "What is the capital of France?"
```

## Overview

This implementation uses a two-agent pattern:
1. **Research Agent**: Uses web search, web scraping, and file reading to gather information
2. **Answer Agent**: Takes the research output and provides a concise, direct answer

The system uses `python-dotenv` to load environment variables from a `.env` file, making it easy to manage your API keys securely.

## Installation

### Quick Setup (Recommended)

```bash
# Run the installation script
./install.sh

# Set your OpenAI API key
export OPENAI_API_KEY=your_api_key_here
```

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY=your_api_key_here
```

## Usage

After installation, you can run the agent using:

```bash
# Using the run script (created by install.sh)
./run.sh --task "Your question here"

# Or directly with Python (from the project directory)
python main.py --task "Your question here"
```

### Examples:
```bash
# Simple question
./run.sh --task "What is the capital of France?"
# Output: Paris.

# Research question  
./run.sh --task "What year was the Eiffel Tower completed and how tall is it?"
# Output: 1889; 300 meters (984 feet).

# Complex question
./run.sh --task "Find the CEO of OpenAI and their background"
```

## How It Works

1. **Research Phase**: The research agent receives the task and uses available tools to gather information
2. **Synthesis Phase**: The answer agent reviews the research and provides a concise answer
3. **Output**: The final answer is displayed on the console

## Tools Available

- `web_search`: Search the internet for information
- `web_scrape`: Extract content from specific webpages  
- `file_read`: Read content from files

## Testing

After installation, verify everything works:

```bash
# Run the import test (no API key required)
./test.sh

# Or directly
python test_import.py
```

This test will:
1. Verify the package structure is correct
2. Test importing the agents
3. Confirm the tools are loaded properly

To test the full flow with API calls:
```bash
# First set your API key
export OPENAI_API_KEY='your-actual-api-key'

# Then run the full test
python test_flow.py
```

## File Structure

```
simple_gaia_agent/
├── main.py       # Entry point with two-agent orchestration
├── agent.py      # Agent definitions (research + answer agents)
├── tools.py      # Tool implementations
├── test_flow.py  # Test to verify the agent flow
├── install.sh    # Installation script
└── setup.py      # Package setup
``` 