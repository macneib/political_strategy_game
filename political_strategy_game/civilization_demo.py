#!/usr/bin/env python3
"""
Civilization System Integration Demo

Demonstrates the fully integrated civilization management system with:
- Enhanced advisors with memory capabilities
- Dynamic political event processing
- Memory-driven decision making
- Political stability calculations
"""

from src.core.civilization import Civilization
from src.core.leader import Leader, LeadershipStyle
from src.core.advisor import AdvisorRole, PersonalityProfile
from src.core.advisor_enhanced import AdvisorWithMemory
from src.core.memory import MemoryType
import tempfile
from pathlib import Path


def create_demo_civilization():
    """Create a demo civilization with realistic setup."""
    print("🏛️  Creating the Empire of Aurelia...")
    
    # Create a leader with strong personality
    leader_personality = PersonalityProfile(
        aggression=0.6,
        diplomacy=0.7,
        loyalty=0.8,
        ambition=0.7,
        cunning=0.5
    )
    
    leader = Leader(
        name="Emperor Marcus Aurelius",
        civilization_id="aurelia",
        personality=leader_personality,
        leadership_style=LeadershipStyle.AUTHORITARIAN,
        legitimacy=0.75
    )
    
    # Create civilization
    civilization = Civilization(
        name="Empire of Aurelia",
        leader=leader
    )
    
    print(f"   👑 Leader: {leader.name}")
    print(f"   🏛️ Government: {civilization.political_state.government_type.value}")
    print(f"   📊 Initial Stability: {civilization.political_state.stability.value}")
    print()
    
    return civilization


def add_demo_advisors(civilization):
    """Add a diverse council of advisors."""
    print("👥 Appointing the Royal Council...")
    
    advisors_data = [
        ("General Valerius", AdvisorRole.MILITARY, 0.9, 0.8, "A loyal veteran general"),
        ("Senator Cicero", AdvisorRole.DIPLOMATIC, 0.6, 0.9, "A cunning politician"),
        ("Treasurer Crassus", AdvisorRole.ECONOMIC, 0.7, 0.7, "A wealthy merchant noble"),
        ("Spymaster Brutus", AdvisorRole.SECURITY, 0.4, 0.8, "A shadowy intelligence chief")
    ]
    
    for name, role, loyalty, influence, description in advisors_data:
        personality = PersonalityProfile(
            aggression=0.5,
            diplomacy=0.6,
            loyalty=loyalty,
            ambition=0.6,
            cunning=0.7 if role == AdvisorRole.SECURITY else 0.5
        )
        
        advisor = AdvisorWithMemory(
            name=name,
            role=role,
            civilization_id=civilization.id,
            personality=personality,
            loyalty=loyalty,
            influence=influence
        )
        
        # Set memory manager for the advisor
        advisor.set_memory_manager(civilization.memory_manager)
        
        civilization.add_advisor(advisor)
        
        # Create some initial memories for the advisor
        advisor.remember_event(
            event_type=MemoryType.APPOINTMENT,
            content=f"Appointed as {role.value} advisor by {civilization.leader.name}",
            emotional_impact=0.8,
            current_turn=1,
            tags={"appointment", "loyalty", role.value}
        )
        
        print(f"   {role.value.title()}: {name} ({description})")
        print(f"     💙 Loyalty: {loyalty:.1f} | 🎯 Influence: {influence:.1f}")
    
    print()


def simulate_political_events(civilization):
    """Simulate some political events and show memory integration."""
    print("📜 Simulating Political Events...")
    
    # Simulate a few turns of political activity
    for turn in range(1, 4):
        print(f"\n--- Turn {turn} ---")
        
        # Process turn
        results = civilization.process_turn()
        
        # Show political summary
        summary = civilization.get_political_summary()
        print(f"Political Stability: {summary['political_state']['stability']}")
        print(f"Coup Risk: {summary['political_state']['coup_risk']:.2f}")
        print(f"Internal Tension: {summary['political_state']['internal_tension']:.2f}")
        
        # Check for conspiracies
        conspiracies = civilization.detect_conspiracies()
        if conspiracies:
            print(f"⚠️  Detected {len(conspiracies)} potential conspiracies!")
        
        # Show advisor memories (for one advisor as example)
        security_advisor = civilization.get_advisor_by_role(AdvisorRole.SECURITY)
        if security_advisor and hasattr(security_advisor, 'recall_memories_about'):
            memories = security_advisor.recall_memories_about(tags={"intelligence", "conspiracy"})
            if memories:
                print(f"🕵️  {security_advisor.name} recalls {len(memories)} intelligence memories")


def demonstrate_memory_system(civilization):
    """Show the memory system in action."""
    print("\n🧠 Memory System Demonstration...")
    
    # Get an advisor and show their memories
    diplomatic_advisor = civilization.get_advisor_by_role(AdvisorRole.DIPLOMATIC)
    if diplomatic_advisor and hasattr(diplomatic_advisor, 'recall_memories_about'):
        
        # Add a specific memory
        diplomatic_advisor.remember_event(
            event_type=MemoryType.INTELLIGENCE,
            content="Overheard rumors of discontent among the military ranks",
            emotional_impact=0.6,
            current_turn=civilization.current_turn,
            tags={"military", "rumor", "intelligence"}
        )
        
        # Recall all memories
        all_memories = diplomatic_advisor.recall_memories_about()
        print(f"📚 {diplomatic_advisor.name} has {len(all_memories)} total memories")
        
        # Show memory content
        for memory in all_memories[:3]:  # Show first 3
            print(f"   • {memory.event_type.value}: {memory.content[:50]}...")
            print(f"     Impact: {memory.emotional_impact:.1f}, Reliability: {memory.reliability:.1f}")


def main():
    """Run the civilization integration demo."""
    print("=" * 60)
    print("🏛️  CIVILIZATION MANAGEMENT SYSTEM DEMO")
    print("=" * 60)
    print()
    
    # Create and setup civilization
    civ = create_demo_civilization()
    add_demo_advisors(civ)
    
    # Show initial state
    print("📊 Initial Civilization State:")
    print(f"   Leaders: {civ.leader.name}")
    print(f"   Advisors: {len(civ.advisors)}")
    print(f"   Memory Manager: {'✅ Active' if civ.memory_manager else '❌ Inactive'}")
    print(f"   Event Manager: {'✅ Active' if civ.event_manager else '❌ Inactive'}")
    print()
    
    # Simulate political activity
    simulate_political_events(civ)
    
    # Demonstrate memory system
    demonstrate_memory_system(civ)
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("✅ Civilization system fully integrated and operational")
    print("=" * 60)


if __name__ == "__main__":
    main()
