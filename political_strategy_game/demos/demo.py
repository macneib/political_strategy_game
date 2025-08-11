"""
Main game engine and demonstration script.
"""

import sys
from pathlib import Path
import json
import random

try:
    from src.core.advisor import Advisor, PersonalityProfile, AdvisorRole, AdvisorStatus
    from src.core.leader import Leader, LeadershipStyle
    from src.core.civilization import Civilization, PoliticalState
    from src.core.memory import MemoryManager
    from src.core.political_event import EventFactory
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Dependencies not available: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    DEPENDENCIES_AVAILABLE = False


class PoliticalStrategyGame:
    """Main game class that orchestrates political simulations."""
    
    def __init__(self):
        self.civilizations = {}
        self.current_turn = 1
        self.memory_manager = None
        
        if DEPENDENCIES_AVAILABLE:
            self.memory_manager = MemoryManager(Path("data/memories"))
    
    def create_sample_civilization(self, civ_name: str = "Sample Empire") -> str:
        """Create a sample civilization with leader and advisors for testing."""
        if not DEPENDENCIES_AVAILABLE:
            print("Cannot create civilization - dependencies not installed")
            return ""
        
        # Create leader
        leader_personality = PersonalityProfile(
            ambition=random.uniform(0.4, 0.9),
            loyalty=random.uniform(0.6, 1.0),
            charisma=random.uniform(0.3, 0.8),
            pragmatism=random.uniform(0.2, 0.8),
            ideology="pragmatic"
        )
        
        leader = Leader(
            name=f"Ruler of {civ_name}",
            civilization_id="",  # Will be set after civilization creation
            personality=leader_personality,
            leadership_style=random.choice(list(LeadershipStyle))
        )
        
        # Create civilization
        civilization = Civilization(
            name=civ_name,
            leader=leader,
            current_turn=self.current_turn
        )
        
        # Update leader's civilization_id
        leader.civilization_id = civilization.id
        
        # Create sample advisors
        advisor_configs = [
            ("General Marcus", AdvisorRole.MILITARY, {"ambition": 0.7, "loyalty": 0.6}),
            ("Treasurer Elena", AdvisorRole.ECONOMIC, {"ambition": 0.4, "loyalty": 0.8}),
            ("Ambassador Chen", AdvisorRole.DIPLOMATIC, {"ambition": 0.5, "loyalty": 0.7}),
            ("High Priest Amal", AdvisorRole.RELIGIOUS, {"ambition": 0.3, "loyalty": 0.9}),
            ("Spymaster Vera", AdvisorRole.SECURITY, {"ambition": 0.8, "loyalty": 0.4})
        ]
        
        for name, role, personality_overrides in advisor_configs:
            personality_data = {
                "ambition": random.uniform(0.2, 0.8),
                "loyalty": random.uniform(0.3, 0.9),
                "charisma": random.uniform(0.2, 0.7),
                "pragmatism": random.uniform(0.3, 0.8),
                "corruption": random.uniform(0.0, 0.3),
                "paranoia": random.uniform(0.0, 0.4),
                "competence": random.uniform(0.4, 0.9),
                "ideology": random.choice(["militaristic", "diplomatic", "economic", "religious", "pragmatic"])
            }
            personality_data.update(personality_overrides)
            
            advisor_personality = PersonalityProfile(**personality_data)
            
            advisor = Advisor(
                name=name,
                role=role,
                civilization_id=civilization.id,
                personality=advisor_personality
            )
            
            civilization.add_advisor(advisor)
        
        # Add some initial relationships between advisors
        active_advisors = civilization.get_active_advisors()
        for i, advisor1 in enumerate(active_advisors):
            for advisor2 in active_advisors[i+1:]:
                # Create some random relationships
                compatibility = advisor1.personality.compatibility_score(advisor2.personality)
                
                relationship1 = advisor1.get_relationship(advisor2.id)
                relationship1.trust = random.uniform(-0.3, compatibility)
                relationship1.influence = random.uniform(0.0, 0.5)
                
                relationship2 = advisor2.get_relationship(advisor1.id)
                relationship2.trust = random.uniform(-0.3, compatibility)
                relationship2.influence = random.uniform(0.0, 0.5)
        
        self.civilizations[civilization.id] = civilization
        return civilization.id
    
    def simulate_turn(self, civilization_id: str) -> dict:
        """Simulate one turn for a civilization."""
        if not DEPENDENCIES_AVAILABLE:
            return {"error": "Dependencies not available"}
        
        if civilization_id not in self.civilizations:
            return {"error": "Civilization not found"}
        
        civilization = self.civilizations[civilization_id]
        
        # Process the turn
        turn_results = civilization.process_turn()
        
        return turn_results
    
    def run_demo_simulation(self, turns: int = 10) -> None:
        """Run a demonstration simulation."""
        if not DEPENDENCIES_AVAILABLE:
            print("Cannot run simulation - dependencies not installed")
            return
        
        print("🏛️  Political Strategy Game - Demo Simulation")
        print("=" * 50)
        
        # Create sample civilization
        civ_id = self.create_sample_civilization("Demo Empire")
        civilization = self.civilizations[civ_id]
        
        print(f"Created civilization: {civilization.name}")
        print(f"Leader: {civilization.leader.name} ({civilization.leader.leadership_style.value})")
        print(f"Advisors: {len(civilization.get_active_advisors())}")
        print()
        
        # Display initial state
        self.display_political_summary(civ_id)
        
        # Simulate turns
        for turn in range(turns):
            print(f"\n📅 Turn {civilization.current_turn}")
            print("-" * 30)
            
            # Simulate the turn
            results = self.simulate_turn(civ_id)
            
            # Report results
            if results.get("conspiracy_detected"):
                print("🕵️  Conspiracy detected among advisors!")
            
            if results.get("coup_attempted"):
                success = results.get("coup_success", False)
                if success:
                    print("💥 COUP SUCCESSFUL! Leadership has changed!")
                else:
                    print("🛡️  Coup attempt failed - conspirators punished")
            
            # Show updated political state every few turns
            if turn % 3 == 0 or results.get("coup_attempted"):
                self.display_political_summary(civ_id)
        
        print("\n🎯 Simulation Complete!")
        print("Final state:")
        self.display_political_summary(civ_id)
    
    def display_political_summary(self, civilization_id: str) -> None:
        """Display current political state of a civilization."""
        if not DEPENDENCIES_AVAILABLE:
            return
        
        if civilization_id not in self.civilizations:
            print("Civilization not found")
            return
        
        summary = self.civilizations[civilization_id].get_political_summary()
        
        print(f"\n🏛️  {summary['civilization_name']} (Turn {summary['current_turn']})")
        print(f"Leader: {summary['leader']['name']}")
        print(f"  Legitimacy: {summary['leader']['legitimacy']:.2f}")
        print(f"  Popularity: {summary['leader']['popularity']:.2f}")
        print(f"  Paranoia: {summary['leader']['paranoia']:.2f}")
        print(f"  Style: {summary['leader']['leadership_style']}")
        
        print(f"\nPolitical State:")
        print(f"  Stability: {summary['political_state']['stability']}")
        print(f"  Coup Risk: {summary['political_state']['coup_risk']:.2f}")
        print(f"  Internal Tension: {summary['political_state']['internal_tension']:.2f}")
        
        print(f"\nAdvisors:")
        for advisor in summary['advisors']:
            loyalty_emoji = "💚" if advisor['loyalty'] > 0.7 else "💛" if advisor['loyalty'] > 0.4 else "❤️"
            print(f"  {advisor['name']} ({advisor['role']}) {loyalty_emoji}")
            print(f"    Loyalty: {advisor['loyalty']:.2f}, Influence: {advisor['influence']:.2f}")
            print(f"    Coup Motivation: {advisor['coup_motivation']:.2f}")
        
        if summary['conspiracies']:
            print(f"\n🕵️  Active Conspiracies: {len(summary['conspiracies'])}")
            for i, conspiracy in enumerate(summary['conspiracies'][:2]):  # Show top 2
                conspirator_count = len(conspiracy['conspirators'])
                print(f"  Conspiracy {i+1}: {conspirator_count} members, "
                     f"Strength: {conspiracy['strength']:.2f}")


def main():
    """Main entry point for the demo."""
    print("Political Strategy Game - Core Systems Demo")
    print("=" * 50)
    
    if not DEPENDENCIES_AVAILABLE:
        print("\n❌ Required dependencies not installed!")
        print("Please run: pip install -r requirements.txt")
        print("\nThis demo requires:")
        print("- pydantic>=2.0.0")
        print("- python>=3.11")
        return
    
    try:
        # Create game instance
        game = PoliticalStrategyGame()
        
        # Run the demo simulation
        game.run_demo_simulation(turns=15)
        
        print("\n✅ Demo completed successfully!")
        print("\nThis demonstrates:")
        print("- Core data structures (Advisor, Leader, Civilization)")
        print("- Political relationship dynamics")
        print("- Turn-based simulation")
        print("- Conspiracy detection")
        print("- Coup mechanics")
        print("- Memory system foundation")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
