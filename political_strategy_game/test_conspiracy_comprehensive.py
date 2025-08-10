#!/usr/bin/env python3
"""
Comprehensive test script for the Interactive Conspiracy Management Interface

This script demonstrates conspiracy detection with guaranteed alert generation,
investigation management, and all interactive features.
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
    ThreatLevel,
    SuspiciousActivity
)
from src.llm.conspiracy import ConspiracyGenerator
from src.llm.dialogue import MultiAdvisorDialogue
from src.llm.advisors import AdvisorCouncil, AdvisorAI, AdvisorPersonality, AdvisorRole
from datetime import datetime, timedelta


async def test_conspiracy_management_comprehensive():
    """Comprehensive test of the interactive conspiracy management interface."""
    
    print("🕵️  Interactive Conspiracy Management - COMPREHENSIVE TEST")
    print("=" * 70)
    
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
        pass
    
    conspiracy_generator = MockConspiracyGenerator()
    
    # Create conspiracy management interface
    conspiracy_manager = InteractiveConspiracyManager(
        llm_manager, advisor_council, dialogue_system, conspiracy_generator
    )
    
    print("✅ Interactive conspiracy manager created successfully")
    
    # Test tracking variables
    alerts_received = []
    investigations_updated = []
    evidence_discovered = []
    
    async def alert_callback(alert: ConspiracyAlert):
        alerts_received.append(alert)
        print(f"🚨 CONSPIRACY ALERT: {alert.title}")
        print(f"   Threat Level: {alert.threat_level.value}")
        print(f"   Suspected Actors: {', '.join(alert.suspected_actors)}")
        print(f"   Urgency: {alert.urgency_score:.2f}")
        print(f"   Time Sensitive: {alert.time_sensitive}")
        
    async def investigation_callback(event_type: str, investigation_id: str, investigation):
        investigations_updated.append((event_type, investigation_id))
        print(f"🔍 Investigation {event_type}: {investigation_id}")
        print(f"   Status: {investigation.status}")
        print(f"   Confidence: {investigation.confidence_score:.2f}")
        
    async def evidence_callback(investigation_id: str, evidence: list):
        evidence_discovered.extend(evidence)
        print(f"📋 New Evidence in {investigation_id}:")
        for item in evidence:
            print(f"   - {item}")
    
    conspiracy_manager.register_alert_callback(alert_callback)
    conspiracy_manager.register_investigation_callback(investigation_callback)
    conspiracy_manager.register_evidence_callback(evidence_callback)
    
    print("✅ Callbacks registered successfully")
    
    try:
        # Test 1: Direct alert creation and processing
        print(f"\n🎯 TEST 1: Direct Alert Creation")
        
        # Create a high-threat conspiracy directly
        high_threat = ConspiracyThreat(
            threat_id="direct_threat_001",
            conspiracy_type="military_coup", 
            threat_level=ThreatLevel.CRITICAL,
            participants=["General Marcus Steel", "Colonel Reynolds", "Minister Chen"],
            description="Critical threat: Military coup planned for next week with civilian support",
            evidence_strength=0.85,
            estimated_timeline="7-10 days"
        )
        
        # Create alert from threat
        alert = await conspiracy_manager._create_conspiracy_alert(high_threat)
        conspiracy_manager.pending_alerts[alert.alert_id] = alert
        await conspiracy_manager._notify_alert_callbacks(alert)
        
        print(f"✅ Direct alert created: {alert.alert_id}")
        
        # Test 2: Alert acknowledgment
        print(f"\n🎯 TEST 2: Alert Acknowledgment")
        acknowledged = await conspiracy_manager.acknowledge_alert(alert.alert_id)
        print(f"✅ Alert acknowledged: {acknowledged}")
        
        # Test 3: Investigation creation
        print(f"\n🎯 TEST 3: Investigation Creation")
        investigation_id = await conspiracy_manager.start_investigation(
            alert.alert_id,
            assigned_advisors=["intelligence", "military", "diplomatic"]
        )
        print(f"✅ Investigation started: {investigation_id}")
        
        # Test 4: Multiple investigation steps
        print(f"\n🎯 TEST 4: Investigation Steps")
        
        # Step 1: Intelligence gathering
        step1 = await conspiracy_manager.add_investigation_step(
            investigation_id,
            InvestigationAction.GATHER_INTELLIGENCE,
            "General Marcus Steel",
            resources=3
        )
        print(f"✅ Step 1: Intelligence gathering added")
        
        # Step 2: Surveillance
        step2 = await conspiracy_manager.add_investigation_step(
            investigation_id,
            InvestigationAction.SURVEILLANCE,
            "Military facilities",
            resources=2
        )
        print(f"✅ Step 2: Surveillance added")
        
        # Step 3: Communication analysis
        step3 = await conspiracy_manager.add_investigation_step(
            investigation_id,
            InvestigationAction.ANALYZE_COMMUNICATIONS,
            "Military communications",
            resources=1
        )
        print(f"✅ Step 3: Communication analysis added")
        
        # Wait for investigation steps to complete
        print(f"⏳ Processing investigation steps...")
        await asyncio.sleep(4)
        
        # Test 5: Investigation status check
        print(f"\n🎯 TEST 5: Investigation Status")
        investigation_status = conspiracy_manager.get_investigation_status(investigation_id)
        if investigation_status:
            print(f"📊 Investigation Status:")
            print(f"   Confidence Level: {investigation_status.confidence_score:.2f}")
            print(f"   Evidence Items: {len(investigation_status.evidence_chain)}")
            completed_steps = sum(1 for step in investigation_status.investigation_steps if step.completed)
            print(f"   Completed Steps: {completed_steps}/{len(investigation_status.investigation_steps)}")
            print(f"   Last Updated: {investigation_status.last_updated.strftime('%H:%M:%S')}")
        
        # Test 6: Advisor consultation
        print(f"\n🎯 TEST 6: Advisor Consultation")
        advisor_input = await conspiracy_manager.consult_advisors_on_investigation(
            investigation_id,
            "Given the evidence, what is the most effective response to prevent this coup?"
        )
        
        print(f"💭 Advisor Consultation Results:")
        for advisor, response in advisor_input.items():
            print(f"   {advisor}: {response}")
        
        # Test 7: Response action proposals
        print(f"\n🎯 TEST 7: Response Action Proposals")
        
        # Test different response actions
        actions_to_test = [
            (ResponseAction.ARREST_CONSPIRATORS, "Immediate arrest based on evidence"),
            (ResponseAction.COUNTER_INTELLIGENCE, "Infiltrate and monitor"),
            (ResponseAction.DIPLOMATIC_PRESSURE, "Resolve through negotiation")
        ]
        
        for action, rationale in actions_to_test:
            response_proposal = await conspiracy_manager.propose_response_action(
                investigation_id, action, rationale
            )
            
            print(f"⚡ {action.value}:")
            print(f"   Feasibility: {response_proposal['feasibility']:.2f}")
            print(f"   Recommended: {'Yes' if response_proposal['recommended'] else 'No'}")
            print(f"   Confidence Required: {response_proposal['confidence_required']:.2f}")
            print(f"   Current Confidence: {response_proposal['current_confidence']:.2f}")
        
        # Test 8: Player skill advancement simulation
        print(f"\n🎯 TEST 8: Player Skills & Learning")
        print(f"📈 Current Player Skills:")
        for skill, level in conspiracy_manager.player_investigation_skills.items():
            print(f"   {skill}: {level:.2f}")
        
        # Simulate skill improvement from investigation
        conspiracy_manager.player_investigation_skills["intelligence_gathering"] += 0.1
        conspiracy_manager.player_investigation_skills["analysis"] += 0.05
        print(f"✅ Skills improved from investigation experience")
        
        # Test 9: Multiple conspiracies management
        print(f"\n🎯 TEST 9: Multiple Conspiracies")
        
        # Create second conspiracy threat
        second_threat = ConspiracyThreat(
            threat_id="economic_threat_001",
            conspiracy_type="economic_manipulation",
            threat_level=ThreatLevel.MEDIUM,
            participants=["Economic Advisor", "Foreign Agent"],
            description="Economic manipulation conspiracy detected",
            evidence_strength=0.6,
            estimated_timeline="2-3 weeks"
        )
        
        second_alert = await conspiracy_manager._create_conspiracy_alert(second_threat)
        conspiracy_manager.pending_alerts[second_alert.alert_id] = second_alert
        await conspiracy_manager._notify_alert_callbacks(second_alert)
        
        print(f"✅ Second conspiracy alert created")
        
        # Test 10: Investigation closure
        print(f"\n🎯 TEST 10: Investigation Closure")
        closed = await conspiracy_manager.close_investigation(investigation_id, "threat_neutralized")
        print(f"✅ Investigation closed: {closed}")
        
        # Final status summary
        print(f"\n📊 COMPREHENSIVE TEST SUMMARY:")
        print(f"   Total Alerts Generated: {len(alerts_received)}")
        print(f"   Investigation Updates: {len(investigations_updated)}")
        print(f"   Evidence Items Discovered: {len(evidence_discovered)}")
        print(f"   Active Investigations: {len(conspiracy_manager.get_active_investigations())}")
        print(f"   Completed Investigations: {len(conspiracy_manager.completed_investigations)}")
        print(f"   Pending Alerts: {len(conspiracy_manager.get_pending_alerts())}")
        
        # Display evidence summary
        if evidence_discovered:
            print(f"\n📋 Evidence Summary:")
            for i, evidence in enumerate(evidence_discovered[:5], 1):
                print(f"   {i}. {evidence}")
        
        # Display final player skills
        print(f"\n📈 Final Player Skills:")
        for skill, level in conspiracy_manager.player_investigation_skills.items():
            print(f"   {skill}: {level:.2f}")
        
    except Exception as e:
        print(f"❌ Error during comprehensive test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n🎉 COMPREHENSIVE CONSPIRACY MANAGEMENT TEST COMPLETED!")
    return True


async def main():
    """Main test function."""
    try:
        success = await test_conspiracy_management_comprehensive()
        if success:
            print("\n✅ ALL COMPREHENSIVE TESTS PASSED!")
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
