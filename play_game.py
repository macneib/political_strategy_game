#!/usr/bin/env python3
"""
Political Strategy Game Launcher

This script launches the interactive political strategy game with AI-enhanced advisors.
Uses uv for package management and execution.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.game.interactive import InteractiveGameCLI
    
    async def main():
        """Launch the interactive game."""
        print("🏛️  Political Strategy Game with AI Advisors")
        print("=" * 50)
        print("Powered by vLLM and Local Language Models")
        print()
        
        cli = InteractiveGameCLI()
        await cli.start()
    
    if __name__ == "__main__":
        asyncio.run(main())
        
except KeyboardInterrupt:
    print("\n\n👋 Game interrupted by user. Goodbye!")
except Exception as e:
    print(f"\n❌ Error starting game: {e}")
    print("\nTroubleshooting:")
    print("1. Ensure vLLM is installed: uv pip install vllm openai")
    print("2. Start vLLM server: uv run --with vllm vllm serve Qwen/Qwen2-1.5B-Instruct")
    print("3. Check that all dependencies are installed: uv pip install -r requirements-llm.txt")
    print("4. Or run with uv: uv run play_game.py")
    sys.exit(1)
