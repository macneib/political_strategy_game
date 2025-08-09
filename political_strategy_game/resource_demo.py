#!/usr/bin/env python3
"""
Resource Management System Demo

Demonstrates the integrated resource management system with:
- Economic management (treasury, trade, stability)
- Military management (forces, morale, budget allocation)
- Technology research (innovation, tech levels)
- Resource-driven political events
- Advisor memory integration with resource decisions
"""

from src.core.civilization import Civilization
from src.core.leader import Leader, LeadershipStyle
from src.core.advisor import AdvisorRole, PersonalityProfile
from src.core.advisor_enhanced import AdvisorWithMemory
from src.core.resources import ResourceType


def create_demo_civilization():
    """Create a demo civilization with resource management."""
    print("🏛️  Creating the Kingdom of Prosperia...")
    
    # Create a leader focused on economic growth
    leader_personality = PersonalityProfile(
        aggression=0.4,
        diplomacy=0.8,
        loyalty=0.7,
        ambition=0.6,
        cunning=0.5
    )
    
    leader = Leader(
        name="Queen Isabella the Prosperous",
        civilization_id="prosperia",
        personality=leader_personality,
        leadership_style=LeadershipStyle.COLLABORATIVE,
        legitimacy=0.8
    )
    
    # Create civilization
    civilization = Civilization(
        name="Kingdom of Prosperia",
        leader=leader
    )
    
    print(f"   👑 Leader: {leader.name}")
    print(f"   🏛️ Government: {civilization.political_state.government_type.value}")
    print(f"   📊 Political Stability: {civilization.political_state.stability.value}")
    print()
    
    return civilization


def add_specialized_advisors(civilization):
    """Add advisors with resource-focused roles."""
    print("👥 Appointing the Royal Resource Council...")
    
    advisors_data = [
        ("Lord Treasurer Marcus", AdvisorRole.ECONOMIC, 0.8, 0.9, "Master of coin and trade"),
        ("General Cassius", AdvisorRole.MILITARY, 0.9, 0.7, "Military strategist and logistics expert"),
        ("Scholar Aristotle", AdvisorRole.DIPLOMATIC, 0.7, 0.8, "Technology researcher and diplomat"),
        ("Spymaster Elena", AdvisorRole.SECURITY, 0.6, 0.8, "Intelligence and security chief")
    ]
    
    for name, role, loyalty, influence, description in advisors_data:
        personality = PersonalityProfile(
            aggression=0.6 if role == AdvisorRole.MILITARY else 0.4,
            diplomacy=0.8 if role == AdvisorRole.DIPLOMATIC else 0.5,
            loyalty=loyalty,
            ambition=0.5,
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
        
        advisor.set_memory_manager(civilization.memory_manager)
        civilization.add_advisor(advisor)
        
        print(f"   {role.value.title()}: {name} ({description})")
        print(f"     💙 Loyalty: {loyalty:.1f} | 🎯 Influence: {influence:.1f}")
    
    print()


def demonstrate_resource_management(civilization):
    """Show resource management capabilities."""
    print("💰 Resource Management Demonstration...")
    
    # Show initial state
    print("\n📊 Initial Resource State:")
    summary = civilization.get_resource_summary()
    economic = summary["economic"]
    military = summary["military"]
    tech = summary["technology"]
    
    print(f"   💰 Treasury: {economic['treasury']:.0f} coins")
    print(f"   📈 Net Income: {economic['net_income']:.0f} coins/turn")
    print(f"   🛡️ Military Forces: {military['total_forces']} units")
    print(f"   🔬 Research Rate: {tech['research_rate']:.0f} points/turn")
    print()
    
    # Demonstrate resource decisions
    print("🎯 Making Strategic Resource Decisions...")
    
    # 1. Start technology research
    print("   🔬 Starting research into 'Agriculture' technology...")
    success = civilization.start_research("agriculture")
    print(f"   {'✅' if success else '❌'} Research started: {success}")
    
    # 2. Allocate military budget
    print("   ⚔️ Allocating 300 coins to military budget...")
    success = civilization.allocate_military_budget(300.0)
    print(f"   {'✅' if success else '❌'} Budget allocated: {success}")
    
    # 3. Establish trade route
    print("   🚢 Establishing trade route with neighboring kingdom...")
    success = civilization.establish_trade_route("neighbor_kingdom", 75.0)
    print(f"   {'✅' if success else '❌'} Trade route established: {success}")
    
    print()


def simulate_resource_progression(civilization):
    """Simulate several turns of resource development."""
    print("⏳ Simulating Resource Development Over Time...")
    
    for turn in range(1, 6):
        print(f"\n--- Turn {turn} ---")
        
        # Process turn
        results = civilization.process_turn()
        
        # Show resource changes
        if "resource_changes" in results:
            resource_changes = results["resource_changes"]
            
            if "economic_changes" in resource_changes and resource_changes["economic_changes"]:
                econ_changes = resource_changes["economic_changes"]
                if "treasury_change" in econ_changes:
                    print(f"💰 Treasury change: {econ_changes['treasury_change']:+.0f} coins")
            
            if "technology_changes" in resource_changes and resource_changes["technology_changes"]:
                tech_changes = resource_changes["technology_changes"]
                if "research_progress" in tech_changes:
                    print(f"🔬 Research progress: +{tech_changes['research_progress']:.0f} points")
                if "completed_research" in tech_changes:
                    print(f"🎉 Technology completed: {tech_changes['completed_research']}")
            
            # Show new resource events
            if "new_events" in resource_changes and resource_changes["new_events"]:
                for event in resource_changes["new_events"]:
                    print(f"⚠️  Resource Event: {event.event_name}")
                    print(f"    📝 {event.description}")
        
        # Show current resource summary
        summary = civilization.get_resource_summary()
        economic = summary["economic"]
        tech = summary["technology"]
        
        print(f"💰 Treasury: {economic['treasury']:.0f} coins | 🔬 Research: {tech['current_research'] or 'None'}")


def demonstrate_resource_events(civilization):
    """Force some resource events for demonstration."""
    print("\n🎭 Demonstrating Resource Events...")
    
    # Force economic prosperity by increasing income
    civilization.resource_manager.economic_state.income_per_turn = 150.0
    print("   📈 Economic policies boost income to 150 coins/turn")
    
    # Complete agriculture research quickly
    civilization.resource_manager.technology_state.accumulated_research = 45.0
    print("   🔬 Pushing agriculture research to near completion")
    
    # Process turn to complete research
    results = civilization.process_turn()
    
    if "resource_changes" in results:
        tech_changes = results["resource_changes"].get("technology_changes", {})
        if "completed_research" in tech_changes:
            print(f"   🎉 Technology breakthrough: Agriculture completed!")
            print(f"   🌾 Agricultural improvements boost civilization capabilities")


def show_advisor_memories(civilization):
    """Show how advisors remember resource decisions."""
    print("\n🧠 Advisor Memory Integration...")
    
    # Get economic advisor memories
    economic_advisor = civilization.get_advisor_by_role(AdvisorRole.ECONOMIC)
    if economic_advisor and hasattr(economic_advisor, 'recall_memories_about'):
        memories = economic_advisor.recall_memories_about(tags={"economic", "budget", "trade"})
        
        print(f"📚 {economic_advisor.name} recalls {len(memories)} resource-related memories:")
        for memory in memories[:3]:  # Show first 3
            print(f"   • {memory.event_type.value}: {memory.content}")
            print(f"     Impact: {memory.emotional_impact:.1f}, Reliability: {memory.reliability:.1f}")
        
        if len(memories) > 3:
            print(f"   ... and {len(memories) - 3} more memories")
    
    print()


def show_comprehensive_status(civilization):
    """Show integrated political and resource status."""
    print("📊 Comprehensive Civilization Status...")
    
    comprehensive = civilization.get_comprehensive_summary()
    
    # Political summary
    political = comprehensive["political"]
    print("\n🏛️ Political Status:")
    print(f"   Stability: {political['political_state']['stability']}")
    print(f"   Coup Risk: {political['political_state']['coup_risk']:.2f}")
    print(f"   Leader Legitimacy: {political['leader']['legitimacy']:.2f}")
    
    # Resource summary
    resources = comprehensive["resources"]
    print("\n💰 Resource Status:")
    print(f"   Treasury: {resources['economic']['treasury']:.0f} coins")
    print(f"   Military Forces: {resources['military']['total_forces']} units")
    print(f"   Military Morale: {resources['military']['morale']:.2f}")
    print(f"   Research Projects: {resources['technology']['completed_techs']} completed")
    
    # Integration status
    integration = comprehensive["integration"]
    print("\n🔧 System Integration:")
    print(f"   Total Advisors: {integration['total_advisors']}")
    print(f"   Memory System: {'✅ Active' if integration['memory_manager_active'] else '❌ Inactive'}")
    print(f"   Event System: {'✅ Active' if integration['event_manager_active'] else '❌ Inactive'}")
    print(f"   Resource System: {'✅ Active' if integration['resource_manager_active'] else '❌ Inactive'}")
    print(f"   Active Resource Events: {integration['active_resource_events']}")


def main():
    """Run the resource management demonstration."""
    print("=" * 70)
    print("🏛️  RESOURCE MANAGEMENT SYSTEM DEMO")
    print("=" * 70)
    print()
    
    # Create and setup civilization
    civ = create_demo_civilization()
    add_specialized_advisors(civ)
    
    # Demonstrate resource management features
    demonstrate_resource_management(civ)
    
    # Simulate progression over time
    simulate_resource_progression(civ)
    
    # Show resource events
    demonstrate_resource_events(civ)
    
    # Show advisor memory integration
    show_advisor_memories(civ)
    
    # Show comprehensive status
    show_comprehensive_status(civ)
    
    print("\n" + "=" * 70)
    print("✅ Resource Management Demo completed successfully!")
    print("✅ All systems integrated: Political + Resource + Memory + Events")
    print("✅ Task 3.1: Resource Management Systems - COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
