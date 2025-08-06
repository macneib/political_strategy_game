#!/bin/bash
# Quick start script for Political Strategy Game

echo "🏛️  Political Strategy Game - Quick Start"
echo "========================================"

# Check if setup has been run
if [ ! -d ".venv" ]; then
    echo "🔧 Running initial setup..."
    bash setup_uv.sh
else
    echo "✅ Virtual environment already exists"
fi

echo ""
echo "🚀 Starting Political Strategy Game Demo..."
echo ""

# Run the demo
uv run python demo.py

echo ""
echo "🎯 Demo complete! Check out the following files:"
echo "   📁 src/core/          - Core game logic"
echo "   📄 README.md          - Full documentation"
echo "   📊 PROGRESS.md        - Implementation status"
echo "   🔧 config/           - Configuration options"
