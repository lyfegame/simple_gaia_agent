# Simple GAIA Agent

A minimal two-agent system for solving GAIA benchmark tasks using web search and scraping.

## Quick Start

```bash
# Clone and enter the directory
cd simple_gaia_agent

# Install everything
./install.sh

# Set your OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" > .env

# Run a task
./run.sh --task "What is the capital of France?"
```

## How It Works

**Two-agent pattern:**
1. **Research Agent** - Searches web, scrapes pages, reads files
2. **Answer Agent** - Synthesizes research into concise answers

## Examples

```bash
# Simple question
./run.sh --task "What is the capital of France?"
# → Paris.

# Research question  
./run.sh --task "What year was the Eiffel Tower completed?"
# → 1889

# Complex question
./run.sh --task "Who is the CEO of OpenAI?"
# → Sam Altman
```

## Installation Details

The `install.sh` script:
- Creates a virtual environment
- Installs dependencies from `requirements.txt`
- Creates `run.sh` and `test.sh` helper scripts

## Manual Usage

```bash
# Activate environment
source venv/bin/activate

# Run directly
python main.py --task "Your question here"
```

## Testing

```bash
# Test imports (no API key needed)
./test.sh

# Test with API calls
python test_flow.py
```

## Files

- `main.py` - Entry point, orchestrates the two agents
- `agent.py` - Agent definitions  
- `tools.py` - Web search, scraping, file reading
- `requirements.txt` - Python dependencies 