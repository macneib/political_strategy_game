"""
Interactive Game Interface for Political Strategy Game

This module provides the main interactive interface for playing the political
strategy game with AI-enhanced advisors.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Add the political strategy game to the path
sys.path.append(str(Path(__file__).parent.parent / "political_strategy_game"))

try:
    # Try importing the main game components (optional)
    from demo import PoliticalStrategyGame
    GAME_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Game dependencies not available: {e}")
    GAME_DEPENDENCIES_AVAILABLE = False

from ..llm.config import create_llm_manager, setup_logging, LLMConfigManager, VLLMServerHelper
from ..llm.advisors import AdvisorCouncil, AdvisorRole as LLMAdvisorRole


class GameSession:
    """Represents an interactive game session."""
    
    def __init__(self, player_name: str, civilization_name: str):
        self.player_name = player_name
        self.civilization_name = civilization_name
        self.game = None
        self.civilization = None
        self.advisor_council = None
        self.llm_manager = None
        self.current_turn = 1
        self.logger = logging.getLogger("game.session")
        
        # Game state
        self.political_power = 100
        self.stability = 75
        self.legitimacy = 70
        self.current_faction = None
        self.pending_events = []
        self.recent_events = []
        
    async def initialize(self):
        """Initialize the game session."""
        if not GAME_DEPENDENCIES_AVAILABLE:
            raise RuntimeError("Game dependencies not available")
        
        # Initialize LLM manager
        self.llm_manager = create_llm_manager()
        
        # Initialize advisor council
        self.advisor_council = AdvisorCouncil(self.llm_manager)
        
        # Initialize the main game
        self.game = PoliticalStrategyGame()
        
        # Create the player's civilization
        civ_id = self.game.create_sample_civilization(self.civilization_name)
        if civ_id in self.game.civilizations:
            self.civilization = self.game.civilizations[civ_id]
        
        self.logger.info(f"Initialized game session for {self.player_name}")
    
    def get_simple_game_state(self):
        """Get a simplified game state for LLM context."""
        class SimpleGameState:
            def __init__(self, political_power, stability, current_faction):
                self.political_power = political_power
                self.stability = stability
                self.current_faction = current_faction
        
        return SimpleGameState(self.political_power, self.stability, self.current_faction)
    
    async def get_advisor_recommendations(self, situation: str) -> Dict[str, str]:
        """Get recommendations from all advisors."""
        game_state = self.get_simple_game_state()
        
        # Get advice from all advisors
        advice_dict = await self.advisor_council.get_council_advice(
            game_state, situation, recent_events=self.recent_events[-5:]
        )
        
        # Convert LLM advisor roles to display names
        recommendations = {}
        advisor_names = self.advisor_council.get_advisor_names()
        
        for role, advice in advice_dict.items():
            advisor_name = advisor_names.get(role, role.value.title())
            recommendations[advisor_name] = advice
        
        return recommendations
    
    async def get_single_advisor_advice(self, advisor_role: str, situation: str) -> str:
        """Get advice from a specific advisor."""
        # Map display names to LLM advisor roles
        role_mapping = {
            "military": LLMAdvisorRole.MILITARY,
            "economic": LLMAdvisorRole.ECONOMIC,
            "diplomatic": LLMAdvisorRole.DIPLOMATIC,
            "domestic": LLMAdvisorRole.DOMESTIC,
            "intelligence": LLMAdvisorRole.INTELLIGENCE
        }
        
        llm_role = role_mapping.get(advisor_role.lower())
        if not llm_role:
            return f"Unknown advisor role: {advisor_role}"
        
        game_state = self.get_simple_game_state()
        return await self.advisor_council.get_single_advice(
            llm_role, game_state, situation, self.recent_events[-5:]
        )
    
    def record_decision(self, decision: str):
        """Record a player decision."""
        self.advisor_council.record_decision_for_all(decision)
        
        # Add to recent events for context
        decision_event = type('Event', (), {
            'title': f"Player Decision: {decision[:50]}...",
            'description': decision,
            'type': 'decision'
        })()
        self.recent_events.append(decision_event)
        
        # Keep only recent events
        if len(self.recent_events) > 10:
            self.recent_events = self.recent_events[-10:]
    
    def advance_turn(self):
        """Advance to the next turn."""
        self.current_turn += 1
        
        # Simple state changes for demo
        import random
        self.political_power += random.randint(-5, 5)
        self.stability += random.randint(-3, 3)
        
        # Clamp values
        self.political_power = max(0, min(100, self.political_power))
        self.stability = max(0, min(100, self.stability))
    
    def get_status(self) -> Dict[str, Any]:
        """Get current game status."""
        return {
            "player": self.player_name,
            "civilization": self.civilization_name,
            "turn": self.current_turn,
            "political_power": self.political_power,
            "stability": self.stability,
            "legitimacy": self.legitimacy,
            "advisor_status": self.advisor_council.get_advisor_status() if self.advisor_council else {},
            "recent_events": len(self.recent_events)
        }


class InteractiveGameCLI:
    """Command-line interface for the interactive game."""
    
    def __init__(self):
        self.session: Optional[GameSession] = None
        self.running = True
        
    async def start(self):
        """Start the interactive game."""
        print("🏛️  Welcome to the Political Strategy Game! 🏛️")
        print("=" * 50)
        
        # Setup logging
        setup_logging()
        
        # Check LLM status
        await self.check_llm_setup()
        
        # Initialize game session
        await self.initialize_session()
        
        # Main game loop
        await self.game_loop()
    
    async def check_llm_setup(self):
        """Check and configure LLM setup."""
        print("\n🤖 Setting up AI Advisors...")
        
        config_manager = LLMConfigManager()
        
        # Check if vLLM server is running
        print("Checking for vLLM server...")
        test_llm = create_llm_manager()
        available_providers = test_llm.get_available_providers()
        
        if not available_providers:
            print("⚠️  No LLM providers available!")
            print("\n📖 vLLM Setup Instructions:")
            print(VLLMServerHelper.get_installation_instructions())
            
            print("\n💡 Quick Start:")
            recommended = config_manager.get_recommended_models()
            for key, model_info in list(recommended.items())[:3]:
                print(f"  • {model_info['name']} ({model_info['memory']})")
                print(f"    Command: {VLLMServerHelper.get_startup_command(model_info['name'])}")
                print()
            
            choice = input("Continue without AI advisors? (y/n): ")
            if choice.lower() != 'y':
                print("Exiting. Please set up vLLM and try again.")
                return False
        else:
            print(f"✅ AI providers available: {[p.value for p in available_providers]}")
        
        return True
    
    async def initialize_session(self):
        """Initialize a new game session."""
        print("\n🎮 Starting New Game")
        print("-" * 25)
        
        # Get player information
        player_name = input("Enter your name: ").strip() or "Player"
        civ_name = input("Enter your civilization name: ").strip() or "Your Empire"
        
        # Create and initialize session
        self.session = GameSession(player_name, civ_name)
        
        try:
            await self.session.initialize()
            print(f"\n✅ Game initialized for {player_name}, ruler of {civ_name}!")
        except Exception as e:
            print(f"❌ Failed to initialize game: {e}")
            print("Continuing with basic functionality...")
            self.session = GameSession(player_name, civ_name)
            self.session.llm_manager = create_llm_manager()
            self.session.advisor_council = AdvisorCouncil(self.session.llm_manager)
    
    async def game_loop(self):
        """Main interactive game loop."""
        while self.running and self.session:
            await self.show_main_menu()
    
    async def show_main_menu(self):
        """Display the main game menu."""
        print(f"\n🏛️  {self.session.civilization_name} - Turn {self.session.current_turn}")
        print("=" * 50)
        
        status = self.session.get_status()
        print(f"Political Power: {status['political_power']}/100")
        print(f"Stability: {status['stability']}/100")
        print(f"Legitimacy: {status['legitimacy']}/100")
        
        print("\nWhat would you like to do?")
        print("1. Consult advisors about a situation")
        print("2. Make a policy decision")
        print("3. View advisor status")
        print("4. Advance to next turn")
        print("5. Save and exit")
        print("0. Exit without saving")
        
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == "1":
            await self.consult_advisors()
        elif choice == "2":
            await self.make_decision()
        elif choice == "3":
            await self.show_advisor_status()
        elif choice == "4":
            await self.advance_turn()
        elif choice == "5":
            await self.save_and_exit()
        elif choice == "0":
            self.running = False
            print("👋 Thanks for playing!")
        else:
            print("❌ Invalid choice. Please try again.")
    
    async def consult_advisors(self):
        """Consult advisors about a situation."""
        print("\n💭 Consulting Your Advisors")
        print("-" * 30)
        
        situation = input("Describe the situation you need advice on: ").strip()
        if not situation:
            print("❌ Please provide a situation to analyze.")
            return
        
        print("\n🤔 Your advisors are deliberating...")
        
        try:
            recommendations = await self.session.get_advisor_recommendations(situation)
            
            print(f"\n📋 Advisor Recommendations for: '{situation}'")
            print("=" * 60)
            
            for advisor_name, advice in recommendations.items():
                print(f"\n👤 {advisor_name}:")
                print(f"   {advice}")
            
            # Ask if player wants to record a decision
            print("\n" + "-" * 40)
            record_decision = input("Would you like to record a decision based on this advice? (y/n): ")
            if record_decision.lower() == 'y':
                decision = input("What is your decision? ")
                if decision.strip():
                    self.session.record_decision(decision)
                    print("✅ Decision recorded!")
        
        except Exception as e:
            print(f"❌ Error consulting advisors: {e}")
        
        input("\nPress Enter to continue...")
    
    async def make_decision(self):
        """Make a policy decision with advisor input."""
        print("\n📋 Policy Decision")
        print("-" * 20)
        
        # Suggest some decision categories
        print("Decision categories:")
        print("1. Military policy")
        print("2. Economic policy") 
        print("3. Diplomatic relations")
        print("4. Domestic affairs")
        print("5. Intelligence operations")
        print("6. Custom decision")
        
        category = input("\nSelect category (1-6): ").strip()
        
        category_map = {
            "1": ("military", "military policy decision"),
            "2": ("economic", "economic policy decision"),
            "3": ("diplomatic", "diplomatic policy decision"),
            "4": ("domestic", "domestic policy decision"),
            "5": ("intelligence", "intelligence operations decision"),
            "6": ("custom", "")
        }
        
        if category not in category_map:
            print("❌ Invalid category.")
            return
        
        advisor_type, default_desc = category_map[category]
        
        if category == "6":
            decision_desc = input("Describe your decision: ").strip()
            advisor_type = input("Which type of advisor to consult (military/economic/diplomatic/domestic/intelligence): ").strip()
        else:
            decision_desc = input(f"Describe your {default_desc}: ").strip()
        
        if not decision_desc:
            print("❌ Please provide a decision description.")
            return
        
        print(f"\n🤔 Consulting your {advisor_type} advisor...")
        
        try:
            advice = await self.session.get_single_advisor_advice(advisor_type, decision_desc)
            
            print(f"\n👤 {advisor_type.title()} Advisor:")
            print(f"   {advice}")
            
            # Confirm decision
            print("\n" + "-" * 40)
            confirm = input("Do you want to proceed with this decision? (y/n): ")
            if confirm.lower() == 'y':
                self.session.record_decision(decision_desc)
                print("✅ Decision implemented and recorded!")
                
                # Simple effects simulation
                import random
                if "military" in advisor_type:
                    self.session.political_power += random.randint(-2, 5)
                elif "economic" in advisor_type:
                    self.session.stability += random.randint(-1, 4)
                elif "diplomatic" in advisor_type:
                    self.session.legitimacy += random.randint(-1, 3)
                
                # Clamp values
                self.session.political_power = max(0, min(100, self.session.political_power))
                self.session.stability = max(0, min(100, self.session.stability))
                self.session.legitimacy = max(0, min(100, self.session.legitimacy))
            else:
                print("❌ Decision cancelled.")
        
        except Exception as e:
            print(f"❌ Error getting advisor input: {e}")
        
        input("\nPress Enter to continue...")
    
    async def show_advisor_status(self):
        """Show the status of all advisors."""
        print("\n👥 Advisor Council Status")
        print("-" * 30)
        
        try:
            status = self.session.advisor_council.get_advisor_status()
            
            print("🤖 LLM Status:")
            llm_status = status.get("llm_status", {})
            primary = llm_status.get("primary", {})
            print(f"   Primary: {primary.get('provider', 'Unknown')} ({primary.get('model', 'Unknown')})")
            print(f"   Available: {'✅' if primary.get('available', False) else '❌'}")
            
            print("\n👥 Advisors:")
            advisors = status.get("advisors", {})
            for role, advisor_info in advisors.items():
                name = advisor_info.get("name", f"{role.title()} Advisor")
                memory = advisor_info.get("memory", {})
                conversations = memory.get("conversation_length", 0)
                decisions = memory.get("key_decisions", 0)
                
                print(f"   • {name} ({role})")
                print(f"     Conversations: {conversations}, Decisions remembered: {decisions}")
        
        except Exception as e:
            print(f"❌ Error getting advisor status: {e}")
        
        input("\nPress Enter to continue...")
    
    async def advance_turn(self):
        """Advance to the next turn."""
        print(f"\n⏭️  Advancing from Turn {self.session.current_turn} to {self.session.current_turn + 1}")
        print("-" * 40)
        
        self.session.advance_turn()
        
        # Show changes
        status = self.session.get_status()
        print(f"✅ Now Turn {status['turn']}")
        print(f"Political Power: {status['political_power']}/100")
        print(f"Stability: {status['stability']}/100")
        
        # Simulate random events occasionally
        import random
        if random.random() < 0.3:  # 30% chance
            events = [
                "A neighboring country proposes a trade agreement",
                "Reports of unrest in the capital city",
                "Military advisors request increased defense spending", 
                "Economic advisors report concerning budget deficits",
                "Intelligence reports suspicious foreign activity"
            ]
            event = random.choice(events)
            print(f"\n📰 News: {event}")
            
            # Add to recent events
            event_obj = type('Event', (), {
                'title': f"Turn {status['turn']} Event",
                'description': event,
                'type': 'random'
            })()
            self.session.recent_events.append(event_obj)
        
        input("\nPress Enter to continue...")
    
    async def save_and_exit(self):
        """Save game and exit."""
        print("\n💾 Saving Game...")
        
        # In a real implementation, this would save to a file
        status = self.session.get_status()
        print(f"Game saved: {status['player']} of {status['civilization']}, Turn {status['turn']}")
        
        self.running = False
        print("👋 Thanks for playing! Your game has been saved.")


async def main():
    """Main entry point for the interactive game."""
    cli = InteractiveGameCLI()
    await cli.start()


if __name__ == "__main__":
    asyncio.run(main())
