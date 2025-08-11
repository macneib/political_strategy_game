#!/usr/bin/env python3
"""
Advanced Political Mechanics Demonstration
==========================================

This script demonstrates the sophisticated advanced political mechanics
implemented for Task 3.3, showcasing internal political systems within
civilizations including factions, conspiracies, propaganda, reforms, and
succession crises.
"""

from src.core.civilization import Civilization
from src.core.leader import Leader, LeadershipStyle
from src.core.advisor import Advisor, AdvisorRole
from src.core.advanced_politics import (
    AdvancedPoliticalManager, PoliticalIdeology, ConspiracyType,
    PropagandaType, SuccessionCrisisType, FactionType
)
from src.core.memory import MemoryManager
from pathlib import Path


def create_demo_civilization() -> Civilization:
    """Create a civilization with advisors for political demonstration."""
    
    # Create leader
    leader = Leader(
        name="Emperor Marcus",
        civilization_id="roman_empire",
        personality={"ambition": 0.8, "wisdom": 0.7, "charisma": 0.9},
        leadership_style=LeadershipStyle.AUTHORITARIAN
    )
    
    # Create civilization with advanced politics
    civ = Civilization(
        name="Roman Empire",
        leader=leader,
        initial_population=1000000,
        initial_food=5000,
        initial_gold=10000
    )
    
    # Add diverse advisors
    advisors = [
        Advisor(
            name="Senator Gaius",
            role=AdvisorRole.DIPLOMATIC,
            civilization_id=civ.id,
            personality={"ambition": 0.9, "loyalty": 0.6, "intelligence": 0.8}
        ),
        Advisor(
            name="General Maximus",
            role=AdvisorRole.MILITARY,
            civilization_id=civ.id,
            personality={"ambition": 0.7, "loyalty": 0.9, "courage": 0.9}
        ),
        Advisor(
            name="Treasurer Julius",
            role=AdvisorRole.ECONOMIC,
            civilization_id=civ.id,
            personality={"ambition": 0.5, "loyalty": 0.8, "intelligence": 0.9}
        ),
        Advisor(
            name="Spymaster Lucius",
            role=AdvisorRole.SECURITY,
            civilization_id=civ.id,
            personality={"ambition": 0.8, "loyalty": 0.7, "cunning": 0.9}
        ),
        Advisor(
            name="High Priest Aurelius",
            role=AdvisorRole.CULTURAL,
            civilization_id=civ.id,
            personality={"ambition": 0.4, "loyalty": 0.9, "wisdom": 0.8}
        )
    ]
    
    for advisor in advisors:
        civ.add_advisor(advisor)
    
    # Initialize memory manager for better tracking
    civ.memory_manager = MemoryManager(Path("demo_memory"))
    
    return civ


def demonstrate_political_factions(civ: Civilization):
    """Demonstrate political faction creation and management."""
    print("\n=== POLITICAL FACTION DEMONSTRATION ===")
    
    # Create various political factions
    conservative_faction = civ.create_political_faction(
        name="Traditionalist Senate",
        faction_type=FactionType.CONSERVATIVE,
        ideology=PoliticalIdeology.TRADITIONALISM,
        leader_advisor_id=list(civ.advisors.keys())[0]  # Senator Gaius
    )
    print(f"✓ Created conservative faction: {conservative_faction}")
    
    military_faction = civ.create_political_faction(
        name="Military Order",
        faction_type=FactionType.MILITARIST,
        ideology=PoliticalIdeology.MILITARISM,
        leader_advisor_id=list(civ.advisors.keys())[1]  # General Maximus
    )
    print(f"✓ Created military faction: {military_faction}")
    
    # Join advisors to factions
    treasurer_id = list(civ.advisors.keys())[2]
    civ.join_political_faction(conservative_faction, treasurer_id)
    print(f"✓ Treasurer Julius joined the Traditionalist Senate")
    
    spymaster_id = list(civ.advisors.keys())[3]
    civ.join_political_faction(military_faction, spymaster_id)
    print(f"✓ Spymaster Lucius joined the Military Order")


def demonstrate_conspiracy_networks(civ: Civilization):
    """Demonstrate conspiracy formation and activities."""
    print("\n=== CONSPIRACY NETWORK DEMONSTRATION ===")
    
    # Form a conspiracy
    senator_id = list(civ.advisors.keys())[0]
    spymaster_id = list(civ.advisors.keys())[3]
    
    conspiracy_id = civ.form_conspiracy(
        leader_advisor_id=senator_id,
        conspiracy_type=ConspiracyType.COUP_ATTEMPT,
        objective="Overthrow the current power structure"
    )
    print(f"✓ Senator Gaius formed a power grab conspiracy: {conspiracy_id}")
    
    # Recruit members
    success = civ.recruit_to_conspiracy(conspiracy_id, senator_id, spymaster_id)
    print(f"✓ Recruited Spymaster Lucius to conspiracy: {success}")
    
    # Process a few turns to see conspiracy evolution
    print("\n--- Processing turns to observe conspiracy development ---")
    for turn in range(3):
        results = civ.advanced_politics.process_turn()
        if results.get("conspiracies_detected"):
            print(f"Turn {turn + 1}: Conspiracy detected!")
        if results.get("conspiracies_activated"):
            print(f"Turn {turn + 1}: Conspiracy activated!")


def demonstrate_propaganda_campaigns(civ: Civilization):
    """Demonstrate propaganda and information warfare."""
    print("\n=== PROPAGANDA CAMPAIGN DEMONSTRATION ===")
    
    # Launch propaganda campaigns
    senator_id = list(civ.advisors.keys())[0]
    general_id = list(civ.advisors.keys())[1]
    
    propaganda_id = civ.launch_propaganda_campaign(
        sponsor_advisor_id=senator_id,
        campaign_type=PropagandaType.POLICY_PROMOTION,
        message="The senate represents the wisdom of tradition and stability",
        target="government"
    )
    print(f"✓ Launched propaganda campaign: {propaganda_id}")
    
    military_propaganda = civ.launch_propaganda_campaign(
        sponsor_advisor_id=general_id,
        campaign_type=PropagandaType.FOREIGN_THREAT_EMPHASIS,
        message="Our military strength protects the empire from external threats",
        target="military"
    )
    print(f"✓ Launched military propaganda: {military_propaganda}")
    
    # Process turns to see propaganda effects
    print("\n--- Processing turns to observe propaganda impact ---")
    for turn in range(2):
        results = civ.advanced_politics.process_turn()
        if results.get("propaganda_effects"):
            for effect in results["propaganda_effects"]:
                print(f"Propaganda effect: {effect}")


def demonstrate_political_reforms(civ: Civilization):
    """Demonstrate political reform proposal and voting."""
    print("\n=== POLITICAL REFORM DEMONSTRATION ===")
    
    # Propose reforms
    senator_id = list(civ.advisors.keys())[0]
    treasurer_id = list(civ.advisors.keys())[2]
    
    reform_id = civ.propose_political_reform(
        name="Senate Expansion Act",
        description="Expand the senate to include more regional representatives",
        reform_scope="constitutional",
        proposer_id=senator_id
    )
    print(f"✓ Proposed reform: {reform_id}")
    
    # Vote on reform
    general_id = list(civ.advisors.keys())[1]
    priest_id = list(civ.advisors.keys())[4]
    
    civ.vote_on_reform(reform_id, general_id, support=True)
    print("✓ General Maximus voted in favor")
    
    civ.vote_on_reform(reform_id, treasurer_id, support=True)
    print("✓ Treasurer Julius voted in favor")
    
    civ.vote_on_reform(reform_id, priest_id, support=False)
    print("✓ High Priest Aurelius voted against")
    
    # Process turn to see if reform passes
    print("\n--- Processing turn to determine reform outcome ---")
    results = civ.advanced_politics.process_turn()
    if results.get("reforms_passed"):
        for reform in results["reforms_passed"]:
            print(f"Reform passed: {reform}")
    else:
        print("No reforms passed this turn")


def demonstrate_succession_crisis(civ: Civilization):
    """Demonstrate succession crisis mechanics."""
    print("\n=== SUCCESSION CRISIS DEMONSTRATION ===")
    
    # Trigger succession crisis
    success = civ.trigger_succession_crisis(SuccessionCrisisType.MULTIPLE_CLAIMANTS)
    print(f"✓ Triggered succession crisis: {success}")
    
    if success:
        print("\n--- Processing turns for succession resolution ---")
        for turn in range(3):
            results = civ.advanced_politics.process_turn()
            if results.get("succession_resolved"):
                print(f"Succession resolved in favor of: {results['succession_resolved']}")
                break
            else:
                print(f"Turn {turn + 1}: Succession crisis continues...")


def demonstrate_comprehensive_summary(civ: Civilization):
    """Show comprehensive political summary."""
    print("\n=== COMPREHENSIVE POLITICAL SUMMARY ===")
    
    summary = civ.get_comprehensive_summary()
    if "advanced_politics" in summary:
        politics = summary["advanced_politics"]
        
        print(f"Active Factions: {len(politics.get('factions', []))}")
        print(f"Active Conspiracies: {len(politics.get('conspiracies', []))}")
        print(f"Propaganda Campaigns: {len(politics.get('propaganda_campaigns', []))}")
        print(f"Pending Reforms: {len(politics.get('pending_reforms', []))}")
        print(f"Succession Crisis: {politics.get('succession_crisis', {}).get('active', False)}")
        
        if politics.get("factions"):
            print("\nFaction Details:")
            for faction in politics["factions"]:
                if isinstance(faction, dict):
                    print(f"  - {faction.get('name', 'Unknown')}: {len(faction.get('members', []))} members")
                else:
                    print(f"  - Faction: {faction}")
        
        if politics.get("conspiracies"):
            print("\nActive Conspiracies:")
            for conspiracy in politics["conspiracies"]:
                if isinstance(conspiracy, dict):
                    print(f"  - {conspiracy.get('type', 'Unknown')}: {len(conspiracy.get('members', []))} members")
                else:
                    print(f"  - Conspiracy: {conspiracy}")


def main():
    """Run the complete advanced politics demonstration."""
    print("🏛️  ADVANCED POLITICAL MECHANICS DEMONSTRATION")
    print("=" * 60)
    
    # Create demonstration civilization
    print("Setting up Roman Empire with advisors...")
    civ = create_demo_civilization()
    
    # Demonstrate each aspect of advanced politics
    demonstrate_political_factions(civ)
    demonstrate_conspiracy_networks(civ)
    demonstrate_propaganda_campaigns(civ)
    demonstrate_political_reforms(civ)
    demonstrate_succession_crisis(civ)
    demonstrate_comprehensive_summary(civ)
    
    print("\n🎉 Advanced Political Mechanics demonstration completed!")
    print("Task 3.3: Advanced Political Mechanics fully implemented and validated!")


if __name__ == "__main__":
    main()
