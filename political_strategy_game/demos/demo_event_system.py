#!/usr/bin/env python3
"""
Political Strategy Game - Event System Demonstration

This script demonstrates the political event system working with the memory
and advisor systems to create a dynamic political simulation.
"""

import tempfile
import random
from pathlib import Path

from src.core.memory import MemoryManager
from src.core.advisor_enhanced import AdvisorWithMemory, AdvisorCouncil, PersonalityProfile
from src.core.events import EventManager
from src.core.event_library import EventLibrary
from src.core.advisor import AdvisorRole


def create_test_advisors() -> list[AdvisorWithMemory]:
    """Create a set of test advisors with diverse personalities."""
    advisors = []
    
    # Military Advisor - Aggressive and Loyal
    military_personality = PersonalityProfile(
        aggression=0.8,
        diplomacy=0.3,
        loyalty=0.9,
        ambition=0.6,
        cunning=0.5
    )
    military_advisor = AdvisorWithMemory(
        id="advisor_military",
        name="General Marcus Steelwind",
        role=AdvisorRole.MILITARY,
        civilization_id="test_civilization",
        personality=military_personality,
        loyalty=0.85,
        influence=0.7
    )
    advisors.append(military_advisor)
    
    # Diplomatic Advisor - Diplomatic and Cunning
    diplomatic_personality = PersonalityProfile(
        aggression=0.2,
        diplomacy=0.9,
        loyalty=0.7,
        ambition=0.7,
        cunning=0.8
    )
    diplomatic_advisor = AdvisorWithMemory(
        id="advisor_diplomatic",
        name="Lady Elara Goldtongue",
        role=AdvisorRole.DIPLOMATIC,
        civilization_id="test_civilization",
        personality=diplomatic_personality,
        loyalty=0.75,
        influence=0.8
    )
    advisors.append(diplomatic_advisor)
    
    # Economic Advisor - Practical and Ambitious
    economic_personality = PersonalityProfile(
        aggression=0.4,
        diplomacy=0.6,
        loyalty=0.6,
        ambition=0.8,
        cunning=0.7
    )
    economic_advisor = AdvisorWithMemory(
        id="advisor_economic",
        name="Master Roderick Coinsworth",
        role=AdvisorRole.ECONOMIC,
        civilization_id="test_civilization",
        personality=economic_personality,
        loyalty=0.65,
        influence=0.75
    )
    advisors.append(economic_advisor)
    
    # Security Advisor - Cunning and Ambitious
    spy_personality = PersonalityProfile(
        aggression=0.6,
        diplomacy=0.5,
        loyalty=0.5,
        ambition=0.9,
        cunning=0.95
    )
    security_advisor = AdvisorWithMemory(
        id="advisor_security",
        name="Shadow Whisper",
        role=AdvisorRole.SECURITY,
        civilization_id="test_civilization",
        personality=spy_personality,
        loyalty=0.55,
        influence=0.6
    )
    advisors.append(security_advisor)
    
    return advisors


def demonstrate_event_system():
    """Demonstrate the complete event system with advisors and memory."""
    print("🏛️  POLITICAL STRATEGY GAME - EVENT SYSTEM DEMONSTRATION")
    print("=" * 70)
    
    # Create temporary directory for memory storage
    with tempfile.TemporaryDirectory() as temp_dir:
        data_dir = Path(temp_dir)
        
        # Initialize core systems
        print("\n📊 Initializing Core Systems...")
        memory_manager = MemoryManager(data_dir=data_dir)
        
        # Create advisors and council
        advisors = create_test_advisors()
        
        # Create council with advisors as dictionary
        advisor_dict = {advisor.id: advisor for advisor in advisors}
        council = AdvisorCouncil(
            civilization_id="test_civilization",
            advisors=advisor_dict
        )
        council.set_memory_manager(memory_manager)
        
        # Register advisors with memory manager
        for advisor in advisors:
            memory_manager.register_advisor(advisor.id, "test_civilization")
        
        print(f"✅ Created {len(advisors)} advisors")
        print(f"✅ Initialized advisor council")
        
        # Initialize event system
        event_manager = EventManager(civilization_id="test_civilization", current_turn=1)
        
        # Load event templates from library
        templates = EventLibrary.get_all_templates()
        for template in templates.values():
            event_manager.add_event_template(template)
        
        print(f"✅ Loaded {len(templates)} event templates")
        print(f"✅ Event system ready\n")
        
        # Simulate several turns of political events
        print("🎭 SIMULATING POLITICAL EVENTS")
        print("-" * 40)
        
        for turn in range(1, 6):
            print(f"\n📅 TURN {turn}")
            
            # Get loyalty report
            loyalty_report = council.get_council_loyalty_report()
            avg_loyalty = sum(loyalty_report.values()) / len(loyalty_report) if loyalty_report else 0.0
            print(f"Average Council Loyalty: {avg_loyalty:.2f}")
            
            # Check coup risk
            coup_risk = council.detect_coup_risk()
            print(f"Coup Risk Level: {coup_risk['risk_level']}")
            
            # Advance turn and generate events
            new_events = event_manager.advance_turn(turn)
            
            # Also manually trigger some events for demonstration
            if turn == 2:
                # Trigger a natural disaster
                disaster_event = event_manager.trigger_event("natural_disaster", {
                    "disaster_type": "earthquake",
                    "location": "the capital"
                })
                new_events.append(disaster_event)
                print(f"🌊 Triggered natural disaster: {disaster_event.title}")
            
            if turn == 4:
                # Trigger a trade route discovery
                trade_event = event_manager.trigger_event("trade_route_discovery", {
                    "trade_type": "spice",
                    "destination": "Eastern Kingdoms"
                })
                new_events.append(trade_event)
                print(f"💰 Triggered trade opportunity: {trade_event.title}")
            
            # Get all active events
            active_events = event_manager.get_available_events()
            
            if active_events:
                print(f"\n📢 Active Events ({len(active_events)}):")
                
                for event in active_events[:2]:  # Handle up to 2 events per turn
                    print(f"\n🎯 EVENT: {event.title}")
                    print(f"   Type: {event.event_type.value}")
                    print(f"   Severity: {event.severity.value}")
                    print(f"   Description: {event.description[:100]}...")
                    
                    # Show available choices
                    print(f"   Choices:")
                    for i, choice in enumerate(event.choices):
                        required = f" (Requires {choice.required_role.value})" if choice.required_role else ""
                        print(f"     {i+1}. {choice.title}{required}")
                        print(f"        {choice.description[:80]}...")
                    
                    # Get advisor recommendations
                    print(f"\n🧠 Advisor Recommendations:")
                    
                    for advisor in advisors:
                        # Get advisor's recommendation based on memory and personality
                        options = [{'title': c.title, 'tags': list(c.tags)} for c in event.choices]
                        context = {
                            'event_type': event.event_type.value,
                            'severity': event.severity.value,
                            'tags': list(event.tags)
                        }
                        
                        if options:
                            recommendation = advisor.make_memory_informed_decision(
                                options=options,
                                context=context,
                                current_turn=turn
                            )
                            print(f"     {advisor.name} ({advisor.role.value}): {recommendation['title']}")
                        else:
                            print(f"     {advisor.name} ({advisor.role.value}): No clear recommendation")
                    
                    # Simulate decision-making
                    if event.choices:
                        # For demonstration, choose based on advisor roles and event type
                        chosen_choice = None
                        
                        if event.event_type.value == "crisis":
                            # In crisis, prefer military or diplomatic solutions
                            for choice in event.choices:
                                if choice.required_role in [AdvisorRole.MILITARY, AdvisorRole.DIPLOMATIC]:
                                    chosen_choice = choice
                                    break
                        elif event.event_type.value == "opportunity":
                            # In opportunities, prefer economic solutions
                            for choice in event.choices:
                                if choice.required_role == AdvisorRole.ECONOMIC or not choice.required_role:
                                    chosen_choice = choice
                                    break
                        
                        if not chosen_choice:
                            chosen_choice = random.choice(event.choices)  # nosec B311 - Using random for game mechanics, not security
                        
                        print(f"\n⚡ DECISION: {chosen_choice.title}")
                        
                        # Resolve the event
                        outcome = event_manager.respond_to_event(event.id, chosen_choice.id)
                        
                        print(f"📋 Outcome: {outcome.outcome_text}")
                        print(f"💫 Effects: {outcome.immediate_effects}")
                        
                        # Create memories for advisors
                        for advisor in advisors:
                            if advisor.id in event.affected_advisors or not event.affected_advisors:
                                memory_content = f"Witnessed response to {event.title} - chose {chosen_choice.title}"
                                
                                # Map event type to memory type
                                memory_type = "decision"  # Default
                                if event.event_type.value == "crisis":
                                    memory_type = "crisis"
                                elif event.event_type.value in ["diplomatic_event", "internal_conflict"]:
                                    memory_type = "relationship"
                                elif event.event_type.value == "opportunity":
                                    memory_type = "decision"
                                
                                advisor.remember_event(
                                    event_type=memory_type,
                                    content=memory_content,
                                    emotional_impact=0.3,
                                    tags=list(event.tags | chosen_choice.tags),
                                    current_turn=turn
                                )
                        
                        # Update advisor relationships based on the choice
                        # (This is simplified - in a full implementation, you'd have more sophisticated relationship updates)
                        
                        print(f"🧠 Created memories for advisors")
            else:
                print("   No active events this turn")
            
            # Update council dynamics
            council.simulate_council_dynamics()
            
            print(f"\n📊 Turn {turn} Summary:")
            # Show loyalty changes if any
            new_loyalty_report = council.get_council_loyalty_report()
            for advisor_id, new_loyalty in new_loyalty_report.items():
                old_loyalty = loyalty_report.get(advisor_id, new_loyalty)
                change = new_loyalty - old_loyalty
                advisor = next(a for a in advisors if a.id == advisor_id)
                if abs(change) > 0.01:
                    print(f"   {advisor.name}: loyalty {change:+.2f}")
        
        # Final status report
        print("\n" + "=" * 70)
        print("📈 FINAL POLITICAL STATUS")
        print("-" * 30)
        
        # Get final loyalty and coup risk
        final_loyalty_report = council.get_council_loyalty_report()
        avg_loyalty = sum(final_loyalty_report.values()) / len(final_loyalty_report) if final_loyalty_report else 0.0
        coup_risk = council.detect_coup_risk()
        
        print(f"Average Council Loyalty: {avg_loyalty:.2f}")
        print(f"Coup Risk Level: {coup_risk['risk_level']}")
        
        print(f"\n👥 Individual Advisor Status:")
        for advisor in advisors:
            memories = advisor.recall_memories_about() if advisor._memory_manager else []
            memory_count = len(memories)
            # Use a simple threat calculation based on loyalty
            threat_level = max(0.0, 1.0 - advisor.loyalty_to_leader)
            print(f"   {advisor.name}:")
            print(f"     Loyalty: {advisor.loyalty_to_leader:.2f}")
            print(f"     Influence: {advisor.influence:.2f}")
            print(f"     Memories: {memory_count}")
            print(f"     Threat Level: {threat_level:.2f}")
        
        print(f"\n📚 Event History:")
        print(f"   Total Events Resolved: {len(event_manager.event_history)}")
        print(f"   Active Events Remaining: {len(event_manager.active_events)}")
        
        # Show some sample memories
        print(f"\n🧠 Sample Advisor Memories:")
        for advisor in advisors[:2]:  # Show memories for first two advisors
            recent_memories = advisor.recall_memories_about() if advisor._memory_manager else []
            if recent_memories:
                print(f"   {advisor.name}:")
                for memory in recent_memories[:2]:  # Show up to 2 memories
                    print(f"     - {memory.content} (Turn {memory.created_turn})")
            else:
                print(f"   {advisor.name}: No memories stored")
        
        print("\n✨ Demonstration completed successfully!")
        print("The event system has been integrated with memory and advisor systems")
        print("to create a dynamic political simulation with persistent consequences.")


if __name__ == "__main__":
    # Set random seed for reproducible demonstration
    random.seed(42)
    
    try:
        demonstrate_event_system()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demonstration interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during demonstration: {e}")
        raise
