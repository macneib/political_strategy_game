#!/usr/bin/env python3
"""
Test script for the Interactive Conspiracy Management Interface

This script demonstrates the conspiracy detection, investigation, and response
functionality with AI advisor consultation and real-time alert systems.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.interactive.conspiracy_management import (
    InteractiveConspiracyManager,
    InvestigationAction,
    ResponseAction,
    ConspiracyAlert,
    ConspiracyThreat,
    ThreatLevel
)
from src.llm.conspiracy import ConspiracyGenerator
from src.llm.dialogue import MultiAdvisorDialogue
from src.llm.advisors import AdvisorCouncil, AdvisorAI, AdvisorPersonality, AdvisorRole


async def test_conspiracy_management():
    """Test the interactive conspiracy management interface."""
    
    print("🕵️  Interactive Conspiracy Management Interface Test")
    print("=" * 65)
    
    # Mock LLM Manager
    class MockLLMManager:
        async def generate_response(self, messages, config=None):
            return "Mock advisor response for conspiracy analysis."
    
    # Create LLM manager and advisors
    llm_manager = MockLLMManager()
    advisors = [
        AdvisorAI(AdvisorPersonality.get_personality(AdvisorRole.INTELLIGENCE), llm_manager),
        AdvisorAI(AdvisorPersonality.get_personality(AdvisorRole.MILITARY), llm_manager),
        AdvisorAI(AdvisorPersonality.get_personality(AdvisorRole.DIPLOMATIC), llm_manager)
    ]
    
    advisor_council = AdvisorCouncil(advisors)
    dialogue_system = MultiAdvisorDialogue(llm_manager, advisor_council)
    
    # Mock conspiracy generator
    class MockConspiracyGenerator:
        async def detect_conspiracies(self, activities):
            # Return a mock conspiracy threat for testing
            return [
                ConspiracyThreat(
                    threat_id="threat_001",
                    conspiracy_type="military_coup",
                    threat_level=ThreatLevel.HIGH,
                    participants=["General Marcus Steel", "Colonel Unknown", "Political Contact"],
                    description="Suspicious military coordination suggests potential coup planning",
                    evidence_strength=0.7,
                    estimated_timeline="2-4 weeks"
                )
            ]
    
    conspiracy_generator = MockConspiracyGenerator()
    
    # Create conspiracy management interface
    conspiracy_manager = InteractiveConspiracyManager(
        llm_manager, advisor_council, dialogue_system, conspiracy_generator
    )
    
    print("✅ Interactive conspiracy manager created successfully")
    
    # Register test callbacks
    alerts_received = []
    investigations_updated = []
    evidence_discovered = []
    
    async def alert_callback(alert: ConspiracyAlert):
        alerts_received.append(alert)
        print(f"🚨 CONSPIRACY ALERT: {alert.title}")
        print(f"   Threat Level: {alert.threat_level.value}")
        print(f"   Suspected Actors: {', '.join(alert.suspected_actors)}")
        print(f"   Urgency: {alert.urgency_score:.2f}")
        print(f"   Recommended Actions: {[action.value for action in alert.recommended_actions]}")
        
    async def investigation_callback(event_type: str, investigation_id: str, investigation):
        investigations_updated.append((event_type, investigation_id))
        print(f"🔍 Investigation Update: {event_type} - {investigation_id}")
        print(f"   Status: {investigation.status}")
        print(f"   Confidence: {investigation.confidence_score:.2f}")
        print(f"   Evidence Items: {len(investigation.evidence_chain)}")
        
    async def evidence_callback(investigation_id: str, evidence: list):
        evidence_discovered.extend(evidence)
        print(f"📋 New Evidence Discovered in {investigation_id}:")
        for item in evidence:
            print(f"   - {item}")
    
    conspiracy_manager.register_alert_callback(alert_callback)
    conspiracy_manager.register_investigation_callback(investigation_callback)
    conspiracy_manager.register_evidence_callback(evidence_callback)
    
    print("✅ Callbacks registered successfully")
    
    try:
        # Test 1: Start conspiracy monitoring
        print(f"\n🔍 Starting conspiracy threat monitoring...")
        await conspiracy_manager.start_alert_monitoring()
        
        # Wait for alerts to be generated
        await asyncio.sleep(3)
        
        print(f"✅ Monitoring started - alerts generated: {len(alerts_received)}")
        
        # Test 2: Check pending alerts
        pending_alerts = conspiracy_manager.get_pending_alerts()
        print(f"📋 Pending alerts: {len(pending_alerts)}")
        
        if pending_alerts:
            alert = pending_alerts[0]
            print(f"🎯 Processing alert: {alert.title}")
            
            # Acknowledge the alert
            acknowledged = await conspiracy_manager.acknowledge_alert(alert.alert_id)
            print(f"✅ Alert acknowledged: {acknowledged}")
            
            # Test 3: Start investigation
            print(f"\n🔍 Starting formal investigation...")
            investigation_id = await conspiracy_manager.start_investigation(
                alert.alert_id, 
                assigned_advisors=["intelligence", "military"]
            )
            print(f"✅ Investigation started: {investigation_id}")
            
            # Test 4: Add investigation steps
            print(f"\n📋 Adding investigation steps...")
            
            # Step 1: Gather intelligence
            step1 = await conspiracy_manager.add_investigation_step(
                investigation_id,
                InvestigationAction.GATHER_INTELLIGENCE,
                "General Marcus Steel",
                resources=2
            )
            print(f"✅ Added intelligence gathering step")
            
            # Step 2: Surveillance
            step2 = await conspiracy_manager.add_investigation_step(
                investigation_id,
                InvestigationAction.SURVEILLANCE,
                "Military meetings",
                resources=3
            )
            print(f"✅ Added surveillance step")
            
            # Wait for investigation steps to complete
            await asyncio.sleep(3)
            
            # Test 5: Consult advisors
            print(f"\n🎯 Consulting advisors on investigation...")
            advisor_input = await conspiracy_manager.consult_advisors_on_investigation(
                investigation_id,
                "What is the likelihood this is a genuine coup threat?"
            )
            
            print(f"💭 Advisor Consultation Results:")
            for advisor, response in advisor_input.items():
                print(f"   {advisor}: {response}")
            
            # Test 6: Check investigation status
            investigation_status = conspiracy_manager.get_investigation_status(investigation_id)
            if investigation_status:
                print(f"\n📊 Investigation Status:")
                print(f"   Confidence Level: {investigation_status.confidence_score:.2f}")
                print(f"   Evidence Items: {len(investigation_status.evidence_chain)}")
                print(f"   Completed Steps: {sum(1 for step in investigation_status.investigation_steps if step.completed)}")
                
            # Test 7: Propose response action
            print(f"\n⚡ Proposing response action...")
            response_proposal = await conspiracy_manager.propose_response_action(
                investigation_id,
                ResponseAction.COUNTER_INTELLIGENCE,
                "Prevent coup while gathering more evidence"
            )
            
            print(f"📋 Response Proposal:")
            print(f"   Action: {response_proposal['action']}")
            print(f"   Feasibility: {response_proposal['feasibility']:.2f}")
            print(f"   Recommended: {response_proposal['recommended']}")
            print(f"   Risks: {response_proposal['risks']}")
            
            # Test 8: Close investigation
            print(f"\n🏁 Closing investigation...")
            closed = await conspiracy_manager.close_investigation(investigation_id, "completed")
            print(f"✅ Investigation closed: {closed}")
        
        # Test summary
        print(f"\n📊 Test Summary:")
        print(f"   Alerts received: {len(alerts_received)}")
        print(f"   Investigation updates: {len(investigations_updated)}")
        print(f"   Evidence discovered: {len(evidence_discovered)}")
        print(f"   Active investigations: {len(conspiracy_manager.get_active_investigations())}")
        print(f"   Completed investigations: {len(conspiracy_manager.completed_investigations)}")
        
        # Stop monitoring
        await conspiracy_manager.stop_alert_monitoring()
        print(f"✅ Monitoring stopped")
        
    except Exception as e:
        print(f"❌ Error during conspiracy management test: {e}")
        await conspiracy_manager.stop_alert_monitoring()
        return False
    
    print(f"\n🎉 Interactive Conspiracy Management test completed successfully!")
    return True


async def main():
    """Main test function."""
    try:
        success = await test_conspiracy_management()
        if success:
            print("\n✅ All conspiracy management tests passed!")
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
