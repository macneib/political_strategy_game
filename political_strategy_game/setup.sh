#!/bin/bash
# Setup script for Political Strategy Game using uv

set -e

echo "🏛️  Setting up Political Strategy Game..."
echo "=================================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

echo "✅ uv is available"

# Create virtual environment
echo "🐍 Creating virtual environment..."
uv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
uv pip install -e ".[dev]"

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data/memories data/saves logs

# Copy environment template
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.template .env
    echo "📝 Please edit .env file with your API keys"
fi

# Run tests to verify installation
echo "🧪 Running tests to verify installation..."
python tests/test_core_structures.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Next steps:"
echo "   1. Activate virtual environment: source .venv/bin/activate"
echo "   2. Run demo: python demo.py"
echo "   3. Edit .env file with your API keys (for future LLM features)"
echo ""
echo "📚 Commands available:"
echo "   uv run python demo.py              # Run demo"
echo "   uv run python tests/test_core_structures.py  # Run tests"
echo "   uv pip install -e \".[llm]\"        # Install LLM dependencies"
echo ""
    echo "⚠️  No virtual environment detected. Creating one..."
    python3 -m venv venv
    echo "📁 Virtual environment created in ./venv"
    echo "🔧 Activate it with: source venv/bin/activate"
    source venv/bin/activate
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/memories
mkdir -p data/saves  
mkdir -p logs
mkdir -p config

# Copy environment template if .env doesn't exist
if [ ! -f ".env" ]; then
    cp .env.template .env
    echo "📝 Environment template copied to .env"
    echo "   Edit .env to add your API keys (for future LLM integration)"
fi

# Run basic tests
echo "🧪 Running basic tests..."
python tests/test_core_structures.py

if [ $? -eq 0 ]; then
    echo "✅ Basic tests passed"
else
    echo "❌ Some tests failed"
fi

# Run demo
echo "🎮 Running demo simulation..."
python demo.py

echo ""
echo "🎯 Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Review the demo output above"
echo "2. Check README.md for detailed documentation"
echo "3. Explore the code in src/ directory"
echo "4. Run 'python demo.py' anytime to see the simulation"
echo ""
echo "For development:"
echo "- Edit .env for API keys (future LLM integration)"
echo "- Modify config/game_config.py for game parameters"
echo "- Check .spec/ directory for full project specifications"
