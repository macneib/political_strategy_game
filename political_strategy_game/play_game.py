#!/usr/bin/env python3
"""
Political Strategy Game Launcher

This script launches the interactive political strategy game with AI-enhanced advisors,
featuring sophisticated multi-advisor dialogues, conspiracy generation, and emotional modeling.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

try:
    from src.game.interactive import InteractiveGameCLI
    
    async def main():
        """Launch the interactive game with advanced AI features."""
        print("🏛️  Political Strategy Game with AI Advisors")
        print("=" * 50)
        print("🤖 Features: Multi-Advisor Dialogues, Conspiracy Generation, Emotional AI")
        print("⚡ Powered by vLLM and Local Language Models")
        print()
        
        cli = InteractiveGameCLI()
        await cli.start()
    
    if __name__ == "__main__":
        asyncio.run(main())
        
except KeyboardInterrupt:
    print("\n\n👋 Game interrupted by user. Goodbye!")
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nGame module not found. Let me show you what's currently available...")
    print("\n🎮 Current Game Features:")
    print("✅ Multi-Advisor Dialogue System")
    print("✅ AI-Driven Conspiracy Generation") 
    print("✅ Emotional State Modeling")
    print("✅ LLM-Enhanced Political Dynamics")
    print("\n📁 Available Demo Scripts:")
    print("• civilization_demo.py - Basic civilization simulation")
    print("• demo_advanced_politics.py - Advanced political mechanics")
    print("• resource_demo.py - Resource management systems")
    print("• diplomacy_demo.py - Inter-civilization diplomacy")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error starting game: {e}")
    print("\nTroubleshooting:")
    print("1. Ensure vLLM is installed: uv add vllm openai")
    print("2. Start vLLM server: uv run vllm serve Qwen/Qwen2-1.5B-Instruct")
    print("3. Check dependencies: uv sync")
    print("4. Try running existing demos first")
    sys.exit(1)
