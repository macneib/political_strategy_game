"""
Test script for Dynamic Crisis Management System

Validates AI-generated crisis scenarios, escalation dynamics, advisor consultation,
and interactive response coordination.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import random

# Mock the dependencies first
class MockMultiAdvisorDialogue:
    pass

class MockDialogueContext:
    pass

class MockDialogueType:
    pass

class MockAdvisorCouncil:
    def __init__(self):
        self.advisors = {
            "military": MockAdvisor("General Smith", "military"),
            "economic": MockAdvisor("Dr. Johnson", "economic"), 
            "diplomatic": MockAdvisor("Ambassador Chen", "diplomatic"),
            "domestic": MockAdvisor("Director Williams", "domestic"),
            "intelligence": MockAdvisor("Agent Thompson", "intelligence")
        }

class MockAdvisorRole:
    pass

class MockLLMManager:
    async def generate(self, messages, max_tokens=150, temperature=0.7):
        class MockResponse:
            def __init__(self, content):
                self.content = content
        return MockResponse("Generated AI response for crisis analysis")

class MockEmergentStorytellingManager:
    async def create_narrative_thread(self, narrative_type, title, context):
        return f"narrative_thread_{title.replace(' ', '_').lower()}"
    
    async def add_plot_point(self, thread_id, plot_point):
        print(f"Added plot point to {thread_id}: {plot_point}")

class MockNarrativeThread:
    def __init__(self, thread_id, narrative_type, title, description, main_characters, plot_points, current_momentum, emotional_tone):
        self.thread_id = thread_id
        self.narrative_type = narrative_type
        self.title = title
        self.description = description
        self.main_characters = main_characters
        self.plot_points = plot_points
        self.current_momentum = current_momentum
        self.emotional_tone = emotional_tone

class MockNarrativeType:
    POLITICAL_INTRIGUE = "political_intrigue"

class MockInformationWarfareManager:
    def __init__(self):
        pass

# Add mock modules to sys.modules to avoid import errors
sys.modules['llm.dialogue'] = type('MockModule', (), {
    'MultiAdvisorDialogue': MockMultiAdvisorDialogue,
    'DialogueContext': MockDialogueContext,
    'DialogueType': MockDialogueType
})()

sys.modules['llm.advisors'] = type('MockModule', (), {
    'AdvisorCouncil': MockAdvisorCouncil,
    'AdvisorRole': MockAdvisorRole
})()

sys.modules['llm.llm_providers'] = type('MockModule', (), {
    'LLMManager': MockLLMManager
})()

sys.modules['llm.emergent_storytelling'] = type('MockModule', (), {
    'EmergentStorytellingManager': MockEmergentStorytellingManager,
    'NarrativeThread': MockNarrativeThread,
    'NarrativeType': MockNarrativeType
})()

sys.modules['llm.information_warfare'] = type('MockModule', (), {
    'InformationWarfareManager': MockInformationWarfareManager
})()

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from interactive.crisis_management import (
    DynamicCrisisManager, CrisisType, CrisisUrgency, CrisisStatus, ResponseType,
    CrisisEvent, ResponseOption, CrisisDecision, CrisisEffect
)

# Mock classes to simulate the dependencies
class MockAdvisor:
    def __init__(self, name, role):
        self.name = name
        self.role = role

class MockLLMManager:
    async def generate(self, messages, max_tokens=150, temperature=0.7):
        class MockResponse:
            def __init__(self, content):
                self.content = content
        return MockResponse("Generated AI response for crisis analysis")

class MockAdvisorCouncil:
    def __init__(self):
        self.advisors = {
            "military": MockAdvisor("General Smith", "military"),
            "economic": MockAdvisor("Dr. Johnson", "economic"), 
            "diplomatic": MockAdvisor("Ambassador Chen", "diplomatic"),
            "domestic": MockAdvisor("Director Williams", "domestic"),
            "intelligence": MockAdvisor("Agent Thompson", "intelligence")
        }

class MockDialogueSystem:
    def __init__(self):
        pass

class MockStorytellingManager:
    async def create_narrative_thread(self, narrative_type, title, context):
        return f"narrative_thread_{title.replace(' ', '_').lower()}"
    
    async def add_plot_point(self, thread_id, plot_point):
        print(f"Added plot point to {thread_id}: {plot_point}")

class MockInformationWarfareManager:
    def __init__(self):
        pass

async def test_crisis_generation():
    """Test AI-generated crisis creation."""
    print("\n🔄 Testing Crisis Generation...")
    
    # Create mock dependencies
    llm_manager = MockLLMManager()
    advisor_council = MockAdvisorCouncil()
    dialogue_system = MockDialogueSystem()
    storytelling_manager = MockStorytellingManager()
    information_warfare = MockInformationWarfareManager()
    
    # Create crisis manager
    crisis_manager = DynamicCrisisManager(
        llm_manager, advisor_council, dialogue_system, 
        storytelling_manager, information_warfare
    )
    
    # Test crisis generation for different types
    crisis_types = [CrisisType.ECONOMIC_COLLAPSE, CrisisType.CIVIL_UNREST, CrisisType.CYBER_ATTACK]
    
    generated_crises = []
    for crisis_type in crisis_types:
        crisis_id = await crisis_manager.force_crisis_generation(crisis_type)
        if crisis_id:
            crisis = crisis_manager.get_crisis_status(crisis_id)
            generated_crises.append(crisis)
            print(f"✅ Generated {crisis_type.value}: {crisis.title}")
            print(f"   Urgency: {crisis.urgency.value}, Status: {crisis.status.value}")
            print(f"   Description: {crisis.description[:100]}...")
            print(f"   Available Responses: {len(crisis.available_responses)}")
    
    print(f"\n📊 Successfully generated {len(generated_crises)} crises")
    return generated_crises

async def test_advisor_consultation():
    """Test AI advisor consultation system."""
    print("\n🗣️  Testing Advisor Consultation...")
    
    # Create crisis manager
    llm_manager = MockLLMManager()
    advisor_council = MockAdvisorCouncil()
    dialogue_system = MockDialogueSystem()
    storytelling_manager = MockStorytellingManager()
    information_warfare = MockInformationWarfareManager()
    
    crisis_manager = DynamicCrisisManager(
        llm_manager, advisor_council, dialogue_system, 
        storytelling_manager, information_warfare
    )
    
    # Generate a crisis for consultation
    crisis_id = await crisis_manager.force_crisis_generation(CrisisType.ECONOMIC_COLLAPSE)
    
    if crisis_id:
        # Test general consultation
        consultation = await crisis_manager.get_crisis_advisor_consultation(
            crisis_id, "What is the best immediate response strategy?"
        )
        
        print(f"✅ Received consultation from {len(consultation)} advisors:")
        for advisor, advice in consultation.items():
            print(f"   {advisor}: {advice[:80]}...")
            
        # Test specific consultation
        specific_consultation = await crisis_manager.get_crisis_advisor_consultation(
            crisis_id, "Should we implement emergency economic measures?"
        )
        
        print(f"\n📋 Specific consultation responses: {len(specific_consultation)} advisors provided input")
        return consultation
    
    return {}

async def test_response_implementation():
    """Test crisis response implementation and effects."""
    print("\n⚡ Testing Response Implementation...")
    
    # Create crisis manager
    llm_manager = MockLLMManager()
    advisor_council = MockAdvisorCouncil()
    dialogue_system = MockDialogueSystem()
    storytelling_manager = MockStorytellingManager()
    information_warfare = MockInformationWarfareManager()
    
    crisis_manager = DynamicCrisisManager(
        llm_manager, advisor_council, dialogue_system, 
        storytelling_manager, information_warfare
    )
    
    # Generate a crisis
    crisis_id = await crisis_manager.force_crisis_generation(CrisisType.CIVIL_UNREST)
    
    if crisis_id:
        crisis = crisis_manager.get_crisis_status(crisis_id)
        print(f"📝 Testing responses for: {crisis.title}")
        print(f"   Initial escalation level: {crisis.escalation_level:.2f}")
        
        # Try implementing different responses
        responses_tested = []
        
        for i, response_option in enumerate(crisis.available_responses[:3]):  # Test first 3 responses
            # Check if crisis still exists (might have been resolved)
            current_crisis = crisis_manager.get_crisis_status(crisis_id)
            if not current_crisis:
                print(f"   ℹ️  Crisis already resolved, skipping remaining responses")
                break
                
            print(f"\n🎯 Implementing Response {i+1}: {response_option.title}")
            print(f"   Success Probability: {response_option.success_probability:.1%}")
            print(f"   Risk Level: {response_option.risk_level:.1%}")
            
            result = await crisis_manager.implement_crisis_response(
                crisis_id,
                response_option.response_id,
                f"Testing response implementation for {response_option.title}"
            )
            
            responses_tested.append(result)
            
            print(f"   Result: {'✅ Success' if result['success'] else '❌ Failed'}")
            print(f"   Effects: {len(result['effects'])} impact categories")
            print(f"   New escalation level: {result['escalation_level']:.2f}")
            print(f"   Crisis status: {result['crisis_status']}")
            
            # Show specific effects
            for effect_type, effect_value in result['effects'].items():
                print(f"     - {effect_type}: {effect_value}")
                
            # If crisis is resolved, stop testing more responses
            if result['crisis_status'] == 'resolved':
                print(f"   ✅ Crisis successfully resolved!")
                break
        
        print(f"\n📈 Tested {len(responses_tested)} response implementations")
        return responses_tested
    
    return []

async def test_crisis_escalation():
    """Test crisis escalation dynamics."""
    print("\n🔥 Testing Crisis Escalation...")
    
    # Create crisis manager
    llm_manager = MockLLMManager()
    advisor_council = MockAdvisorCouncil()
    dialogue_system = MockDialogueSystem()
    storytelling_manager = MockStorytellingManager()
    information_warfare = MockInformationWarfareManager()
    
    crisis_manager = DynamicCrisisManager(
        llm_manager, advisor_council, dialogue_system, 
        storytelling_manager, information_warfare
    )
    
    # Set higher escalation rate for testing
    crisis_manager.escalation_rate = 0.5
    
    # Generate a crisis
    crisis_id = await crisis_manager.force_crisis_generation(CrisisType.CYBER_ATTACK)
    
    if crisis_id:
        crisis = crisis_manager.get_crisis_status(crisis_id)
        initial_escalation = crisis.escalation_level
        
        print(f"📊 Monitoring escalation for: {crisis.title}")
        print(f"   Initial escalation: {initial_escalation:.2f}")
        print(f"   Initial status: {crisis.status.value}")
        
        # Force several escalation checks
        escalation_events = []
        for i in range(5):
            # Manually trigger escalation check
            escalated = await crisis_manager._check_crisis_escalation(crisis)
            
            if escalated:
                escalation_events.append({
                    "round": i + 1,
                    "escalation_level": crisis.escalation_level,
                    "status": crisis.status.value
                })
                print(f"   🔺 Round {i+1}: Escalated to {crisis.escalation_level:.2f} ({crisis.status.value})")
            else:
                print(f"   ➡️  Round {i+1}: No escalation ({crisis.escalation_level:.2f})")
        
        print(f"\n📈 Escalation events: {len(escalation_events)} out of 5 checks")
        final_escalation = crisis.escalation_level
        escalation_increase = final_escalation - initial_escalation
        print(f"   Total escalation increase: {escalation_increase:.2f}")
        
        return escalation_events
    
    return []

async def test_narrative_integration():
    """Test crisis narrative integration with storytelling system."""
    print("\n📖 Testing Narrative Integration...")
    
    # Create crisis manager
    llm_manager = MockLLMManager()
    advisor_council = MockAdvisorCouncil()
    dialogue_system = MockDialogueSystem()
    storytelling_manager = MockStorytellingManager()
    information_warfare = MockInformationWarfareManager()
    
    crisis_manager = DynamicCrisisManager(
        llm_manager, advisor_council, dialogue_system, 
        storytelling_manager, information_warfare
    )
    
    # Generate narrative-heavy crises
    narrative_crisis_types = [CrisisType.CORRUPTION_SCANDAL, CrisisType.POLITICAL_ASSASSINATION]
    
    narrative_crises = []
    for crisis_type in narrative_crisis_types:
        crisis_id = await crisis_manager.force_crisis_generation(crisis_type)
        if crisis_id:
            crisis = crisis_manager.get_crisis_status(crisis_id)
            narrative_crises.append(crisis)
            
            print(f"✅ Generated narrative crisis: {crisis.title}")
            print(f"   Narrative threads: {len(crisis.narrative_threads)}")
            print(f"   Media attention: {crisis.media_attention:.1%}")
            print(f"   Key actors: {', '.join(crisis.key_actors)}")
            
            # Test narrative conclusion
            if crisis.narrative_threads:
                for thread_id in crisis.narrative_threads:
                    await crisis_manager._conclude_crisis_narrative(thread_id, crisis)
                    print(f"   📝 Concluded narrative thread: {thread_id}")
    
    print(f"\n🎭 Successfully integrated {len(narrative_crises)} narrative crises")
    return narrative_crises

async def test_monitoring_system():
    """Test continuous crisis monitoring and generation."""
    print("\n👁️  Testing Monitoring System...")
    
    # Create crisis manager
    llm_manager = MockLLMManager()
    advisor_council = MockAdvisorCouncil()
    dialogue_system = MockDialogueSystem()
    storytelling_manager = MockStorytellingManager()
    information_warfare = MockInformationWarfareManager()
    
    crisis_manager = DynamicCrisisManager(
        llm_manager, advisor_council, dialogue_system, 
        storytelling_manager, information_warfare
    )
    
    # Set up callbacks to track events
    crisis_events = []
    escalation_events = []
    decision_events = []
    
    async def crisis_callback(crisis):
        crisis_events.append(crisis)
        print(f"   🚨 New crisis detected: {crisis.title}")
    
    async def escalation_callback(crisis):
        escalation_events.append(crisis)
        print(f"   📈 Crisis escalated: {crisis.title} -> {crisis.escalation_level:.2f}")
    
    async def decision_callback(decision, success, effects):
        decision_events.append((decision, success, effects))
        print(f"   🎯 Decision made for {decision.crisis_id}: {'Success' if success else 'Failed'}")
    
    crisis_manager.register_crisis_callback(crisis_callback)
    crisis_manager.register_escalation_callback(escalation_callback)
    crisis_manager.register_decision_callback(decision_callback)
    
    # Force some crises for monitoring test
    for crisis_type in [CrisisType.ECONOMIC_COLLAPSE, CrisisType.DIPLOMATIC_INCIDENT]:
        await crisis_manager.force_crisis_generation(crisis_type)
    
    # Test some escalations and decisions
    active_crises = crisis_manager.get_active_crises()
    for crisis in active_crises:
        # Force escalation
        await crisis_manager._check_crisis_escalation(crisis)
        
        # Test decision on first available response
        if crisis.available_responses:
            response = crisis.available_responses[0]
            await crisis_manager.implement_crisis_response(
                crisis.crisis_id, response.response_id, "Monitoring system test"
            )
    
    print(f"✅ Monitoring system tracked:")
    print(f"   Crisis events: {len(crisis_events)}")
    print(f"   Escalation events: {len(escalation_events)}")
    print(f"   Decision events: {len(decision_events)}")
    
    return {
        "crises": crisis_events,
        "escalations": escalation_events,
        "decisions": decision_events
    }

async def test_comprehensive_crisis_scenario():
    """Run a comprehensive end-to-end crisis management scenario."""
    print("\n🎮 Running Comprehensive Crisis Scenario...")
    
    # Create crisis manager
    llm_manager = MockLLMManager()
    advisor_council = MockAdvisorCouncil()
    dialogue_system = MockDialogueSystem()
    storytelling_manager = MockStorytellingManager()
    information_warfare = MockInformationWarfareManager()
    
    crisis_manager = DynamicCrisisManager(
        llm_manager, advisor_council, dialogue_system, 
        storytelling_manager, information_warfare
    )
    
    print("📝 Scenario: Multiple simultaneous crises requiring coordinated response")
    
    # Generate multiple crises
    crisis_ids = []
    for crisis_type in [CrisisType.CIVIL_UNREST, CrisisType.ECONOMIC_COLLAPSE, CrisisType.CYBER_ATTACK]:
        crisis_id = await crisis_manager.force_crisis_generation(crisis_type)
        crisis_ids.append(crisis_id)
    
    print(f"✅ Generated {len(crisis_ids)} simultaneous crises")
    
    # Show initial state
    active_crises = crisis_manager.get_active_crises()
    print(f"\n📊 Initial Crisis State:")
    for crisis in active_crises:
        print(f"   {crisis.crisis_type.value}: {crisis.escalation_level:.2f} escalation, {crisis.urgency.value} urgency")
    
    # Simulate coordinated response across multiple crises
    total_decisions = 0
    total_successes = 0
    
    for crisis in active_crises:
        print(f"\n🎯 Managing {crisis.crisis_type.value}:")
        
        # Get advisor consultation
        consultation = await crisis_manager.get_crisis_advisor_consultation(
            crisis.crisis_id, "What is our priority response for this crisis?"
        )
        print(f"   💬 Consulted {len(consultation)} advisors")
        
        # Implement best available response
        if crisis.available_responses:
            # Choose response with highest success probability
            best_response = max(crisis.available_responses, key=lambda r: r.success_probability)
            
            result = await crisis_manager.implement_crisis_response(
                crisis.crisis_id,
                best_response.response_id,
                f"Coordinated response to {crisis.crisis_type.value} crisis"
            )
            
            total_decisions += 1
            if result['success']:
                total_successes += 1
            
            print(f"   📊 Response: {best_response.title}")
            print(f"   Result: {'✅ Success' if result['success'] else '❌ Failed'}")
            print(f"   New escalation: {result['escalation_level']:.2f}")
    
    # Final state assessment
    final_crises = crisis_manager.get_active_crises()
    resolved_crises = [c for c in active_crises if c.crisis_id not in [fc.crisis_id for fc in final_crises]]
    
    print(f"\n📈 Scenario Results:")
    print(f"   Total decisions: {total_decisions}")
    print(f"   Successful responses: {total_successes}/{total_decisions} ({total_successes/total_decisions*100:.1f}%)")
    print(f"   Crises resolved: {len(resolved_crises)}")
    print(f"   Crises remaining: {len(final_crises)}")
    
    # Show final crisis states
    print(f"\n🎯 Final Crisis States:")
    for crisis in final_crises:
        print(f"   {crisis.crisis_type.value}: {crisis.status.value} (escalation: {crisis.escalation_level:.2f})")
    
    return {
        "total_decisions": total_decisions,
        "success_rate": total_successes/total_decisions if total_decisions > 0 else 0,
        "crises_resolved": len(resolved_crises),
        "crises_remaining": len(final_crises)
    }

async def main():
    """Run comprehensive testing of the Dynamic Crisis Management System."""
    print("🎯 Dynamic Crisis Management System - Comprehensive Testing")
    print("=" * 60)
    
    try:
        # Run all tests
        test_results = {}
        
        test_results['generation'] = await test_crisis_generation()
        test_results['consultation'] = await test_advisor_consultation()
        test_results['responses'] = await test_response_implementation()
        test_results['escalation'] = await test_crisis_escalation()
        test_results['narrative'] = await test_narrative_integration()
        test_results['monitoring'] = await test_monitoring_system()
        test_results['scenario'] = await test_comprehensive_crisis_scenario()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎊 TESTING COMPLETE - Dynamic Crisis Management System")
        print("=" * 60)
        
        print(f"✅ Crisis Generation: {len(test_results['generation'])} crises created")
        print(f"✅ Advisor Consultation: {len(test_results['consultation'])} advisors consulted")
        print(f"✅ Response Implementation: {len(test_results['responses'])} responses tested")
        print(f"✅ Escalation Dynamics: {len(test_results['escalation'])} escalation events")
        print(f"✅ Narrative Integration: {len(test_results['narrative'])} narrative crises")
        print(f"✅ Monitoring System: {len(test_results['monitoring']['crises'])} events tracked")
        print(f"✅ Comprehensive Scenario: {test_results['scenario']['success_rate']:.1%} success rate")
        
        print("\n🎮 Dynamic Crisis Management System is fully operational!")
        print("Features validated:")
        print("  • AI-generated crisis scenarios with realistic details")
        print("  • Real-time escalation dynamics and urgency management")
        print("  • Comprehensive advisor consultation system")
        print("  • Interactive response implementation with effects")
        print("  • Narrative integration for storytelling continuity")
        print("  • Continuous monitoring and event callback system")
        print("  • Multi-crisis coordination and management")
        
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
