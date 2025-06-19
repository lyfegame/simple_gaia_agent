#!/bin/bash

# Simple GAIA Agent Installation Script

echo "🚀 Simple GAIA Agent Setup"
echo "=========================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check for API key
echo
echo "🔑 Checking for OpenAI API key..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OpenAI API key not found in environment."
    echo
    echo "To set your API key, run:"
    echo "  export OPENAI_API_KEY='your-api-key-here'"
    echo
    echo "Or add it to your shell profile (~/.bashrc, ~/.zshrc, etc.)"
    echo
fi

# Create a run script
echo "📝 Creating run script..."
cat > run.sh << 'EOF'
#!/bin/bash
# Activate virtual environment and run the agent
source venv/bin/activate
python main.py "$@"
EOF
chmod +x run.sh

# Create test script
echo "🧪 Creating test script..."
cat > test.sh << 'EOF'
#!/bin/bash
# Run the import test
source venv/bin/activate
python test_import.py
EOF
chmod +x test.sh

# Success message
echo
echo "✅ Installation complete!"
echo
echo "To use the agent:"
echo "  1. Set your OpenAI API key (if not already set):"
echo "     export OPENAI_API_KEY='your-api-key-here'"
echo
echo "  2. Run the agent:"
echo "     ./run.sh --task 'Your question here'"
echo
echo "  3. Test the installation:"
echo "     ./test.sh"
echo
echo "Example:"
echo "  ./run.sh --task 'What is the capital of France?'"
echo 