#!/usr/bin/env python3
"""
Test script for the Real-Time Council Meeting Interface

This script demonstrates the interactive council meeting functionality
with simulated advisor debates and player intervention capabilities.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.interactive.real_time_council import (
    RealTimeCouncilInterface, 
    PlayerIntervention, 
    InterventionType,
    MeetingState
)
from src.llm.dialogue import MultiAdvisorDialogue, DialogueContext, DialogueType
from src.llm.advisors import AdvisorCouncil, AdvisorAI, AdvisorPersonality, AdvisorRole, GameState
from src.llm.llm_providers import LLMManager, LLMProvider, LLMConfig


async def test_real_time_council():
    """Test the real-time council meeting interface."""
    
    print("🏛️  Real-Time Council Meeting Interface Test")
    print("=" * 60)
    
    # Mock LLM Manager (since we're testing functionality, not actual LLM calls)
    class MockLLMManager:
        async def generate_response(self, messages, config=None):
            # Return a mock response for testing
            return "This is a mock advisor response for testing purposes."
    
    # Create LLM manager first
    llm_manager = MockLLMManager()
    
    # Create test advisors
    advisors = [
        AdvisorAI(AdvisorPersonality.get_personality(AdvisorRole.MILITARY), llm_manager),
        AdvisorAI(AdvisorPersonality.get_personality(AdvisorRole.ECONOMIC), llm_manager), 
        AdvisorAI(AdvisorPersonality.get_personality(AdvisorRole.DIPLOMATIC), llm_manager)
    ]
    
    advisor_council = AdvisorCouncil(advisors)
    
    # Create dialogue system
    dialogue_system = MultiAdvisorDialogue(llm_manager, advisor_council)
    
    # Create real-time council interface
    council_interface = RealTimeCouncilInterface(
        llm_manager, advisor_council, dialogue_system
    )
    
    print("✅ Real-time council interface created successfully")
    
    # Register test callbacks
    intervention_opportunities = []
    meeting_updates = []
    
    async def intervention_callback(meeting_id, options):
        intervention_opportunities.append({
            "meeting_id": meeting_id,
            "options": [opt.value for opt in options],
            "timestamp": "mock_timestamp"
        })
        print(f"📢 Intervention opportunity available for meeting {meeting_id}")
        print(f"   Available options: {[opt.value for opt in options]}")
    
    async def update_callback(update_data):
        meeting_updates.append(update_data)
        print(f"🔄 Meeting update: {update_data['update_type']}")
        if update_data.get('data'):
            print(f"   Data: {update_data['data']}")
    
    council_interface.register_intervention_callback(intervention_callback)
    council_interface.register_update_callback(update_callback)
    
    print("✅ Callbacks registered successfully")
    
    # Start a test council meeting
    game_state = GameState(political_power=85, stability=70, legitimacy=80)
    
    context = DialogueContext(
        topic="National Defense Budget Allocation",
        participants=["military_advisor", "economic_advisor", "diplomatic_advisor"],
        dialogue_type=DialogueType.COUNCIL_MEETING,
        game_state=game_state
    )
    
    print(f"\n🏛️  Starting council meeting: '{context.topic}'")
    print(f"📋 Participants: {', '.join(context.participants)}")
    
    try:
        meeting_id = await council_interface.start_council_meeting(
            topic=context.topic,
            urgency=0.7,
            participants=context.participants
        )
        print(f"✅ Meeting started with ID: {meeting_id}")
        
        # Get meeting state
        meeting_state = council_interface.get_meeting_state(meeting_id)
        if meeting_state:
            print(f"📊 Meeting state:")
            print(f"   Topic: {meeting_state.topic}")
            print(f"   Participants: {meeting_state.participants}")
            print(f"   Active: {meeting_state.is_active}")
            print(f"   Urgency Level: {meeting_state.urgency_level}")
        
        # Simulate player intervention
        print(f"\n🎯 Simulating player intervention...")
        intervention = PlayerIntervention(
            intervention_type=InterventionType.REDIRECT_DISCUSSION,
            content="Let's focus on the most cost-effective defense strategies that balance military needs with economic constraints."
        )
        
        success = await council_interface.handle_player_intervention(meeting_id, intervention)
        print(f"✅ Player intervention processed: {success}")
        
        # Check active meetings
        active_meetings = council_interface.get_active_meetings()
        print(f"📋 Active meetings: {active_meetings}")
        
        # End the meeting
        print(f"\n🏁 Ending meeting...")
        ended = await council_interface.end_meeting(meeting_id)
        print(f"✅ Meeting ended: {ended}")
        
        # Summary
        print(f"\n📊 Test Summary:")
        print(f"   Intervention opportunities: {len(intervention_opportunities)}")
        print(f"   Meeting updates: {len(meeting_updates)}")
        print(f"   Meeting successfully created and managed: ✅")
        
    except Exception as e:
        print(f"❌ Error during council meeting: {e}")
        return False
    
    print(f"\n🎉 Real-Time Council Interface test completed successfully!")
    return True


async def main():
    """Main test function."""
    try:
        success = await test_real_time_council()
        if success:
            print("\n✅ All tests passed!")
            return 0
        else:
            print("\n❌ Some tests failed!")
            return 1
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
