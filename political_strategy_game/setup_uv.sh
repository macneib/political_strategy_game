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

# Install dependencies (uv automatically activates the venv)
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
uv run python tests/test_core_structures.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Next steps:"
echo "   1. Run demo: uv run python demo.py"
echo "   2. Run tests: uv run python tests/test_core_structures.py"
echo "   3. Edit .env file with your API keys (for future LLM features)"
echo ""
echo "📚 Available commands:"
echo "   uv run python demo.py                    # Run political simulation demo"
echo "   uv run python tests/test_core_structures.py  # Run core tests"
echo "   uv pip install -e \".[llm]\"             # Install LLM dependencies"
echo "   uv pip install -e \".[game-engine]\"     # Install game engine deps"
echo ""
echo "🔧 Development commands:"
echo "   uv run black src/                        # Format code"
echo "   uv run flake8 src/                      # Lint code"
echo "   uv run mypy src/                        # Type checking"
echo ""
