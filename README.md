# Simple GAIA Agent

A minimal two-agent system for solving GAIA benchmark tasks using web search and scraping.

## Quick Start

```bash
# Clone and enter the directory
cd simple_gaia_agent

# Make install script executable and run it
chmod +x install.sh
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

# With verbose logging
python main.py --task "Your question here" --verbose
```

## Testing

```bash
# Run the test suite
./test.sh
```

This runs a unified test that:
1. Tests imports
2. Tests simple questions (if API key is set):
   - Math: "What is 2 + 2?" → 4
   - Geography: "What is the capital of France?" → Paris

## Files

- `main.py` - Entry point, orchestrates the two agents (supports `--verbose` flag)
- `agent.py` - Agent definitions  
- `tools.py` - Web search, scraping, file reading (with logging)
- `test.py` - Unified test suite (imports + simple questions)
- `requirements.txt` - Python dependencies 