#!/bin/bash
# Test the uv setup manually
echo "🧪 Testing uv setup manually..."

cd /home/macneib/epoch/political_strategy_game

echo "Checking uv version..."
uv --version

echo "Creating virtual environment..."
uv venv

echo "Installing dependencies..."
uv pip install -e ".[dev]"

echo "Running demo..."
uv run python demo.py
