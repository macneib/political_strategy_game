#!/usr/bin/env python3
"""
Technology Tree Integration Demonstration

Showcases the complete technology tree system with advisor lobbying,
research progression, and integration with existing game systems.
"""

import sys
import os
import json
from typing import Dict, List, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.technology_tree import TechnologyTree, TechnologyCategory
from src.core.advisor_technology import AdvisorLobbyingManager, LobbyingStrategy
from src.core.technology_integration import TechnologyResearchManager
from src.core.advisor import Advisor, AdvisorRole, PersonalityProfile
from src.core.resources import ResourceManager, EconomicState, MilitaryState, TechnologyState


def create_demo_advisors() -> List[Advisor]:
    """Create a set of advisors with diverse personalities and roles."""
    advisors = []
    
    # Military hawk
    military_advisor = Advisor(
        name="General Marcus Steel",
        role=AdvisorRole.MILITARY,
        civilization_id="demo_civ",
        personality=PersonalityProfile(
            ambition=0.8,
            loyalty=0.7,
            pragmatism=0.4,
            competence=0.9,
            paranoia=0.6
        ),
        influence=0.8
    )
    advisors.append(military_advisor)
    
    # Economic pragmatist
    economic_advisor = Advisor(
        name="Minister Elena Wise",
        role=AdvisorRole.ECONOMIC,
        civilization_id="demo_civ",
        personality=PersonalityProfile(
            ambition=0.6,
            loyalty=0.8,
            pragmatism=0.9,
            competence=0.8,
            corruption=0.2
        ),
        influence=0.7
    )
    advisors.append(economic_advisor)
    
    # Security chief
    security_advisor = Advisor(
        name="Director Sarah Blackwood",
        role=AdvisorRole.SECURITY,
        civilization_id="demo_civ",
        personality=PersonalityProfile(
            ambition=0.7,
            loyalty=0.6,
            pragmatism=0.7,
            competence=0.9,
            paranoia=0.8
        ),
        influence=0.9
    )
    advisors.append(security_advisor)
    
    # Religious leader
    religious_advisor = Advisor(
        name="Patriarch David Pure",
        role=AdvisorRole.RELIGIOUS,
        civilization_id="demo_civ",
        personality=PersonalityProfile(
            ambition=0.5,
            loyalty=0.9,
            pragmatism=0.3,
            competence=0.7,
            charisma=0.8
        ),
        influence=0.6
    )
    advisors.append(religious_advisor)
    
    # Diplomatic advisor
    diplomatic_advisor = Advisor(
        name="Ambassador Chen Harmony",
        role=AdvisorRole.DIPLOMATIC,
        civilization_id="demo_civ",
        personality=PersonalityProfile(
            ambition=0.4,
            loyalty=0.8,
            pragmatism=0.8,
            competence=0.8,
            charisma=0.9
        ),
        influence=0.7
    )
    advisors.append(diplomatic_advisor)
    
    return advisors


def create_demo_resource_manager() -> ResourceManager:
    """Create a resource manager representing a mid-tier civilization."""
    economic = EconomicState(
        gdp=2500.0,
        population=1500000,
        infrastructure_level=85.0
    )
    
    military = MilitaryState(
        army_size=75000,
        navy_size=150,
        air_force_size=50
    )
    
    technology = TechnologyState(
        research_points_per_turn=15.0,
        military_tech_level=0.6,
        economic_tech_level=0.7,
        political_tech_level=0.4
    )
    
    return ResourceManager(
        civilization_id="demo_civ",
        economic_state=economic,
        military_state=military,
        technology_state=technology
    )


def print_section_header(title: str) -> None:
    """Print a formatted section header."""
    print("\\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def print_technology_tree_overview(tree: TechnologyTree) -> None:
    """Print an overview of the technology tree."""
    print_section_header("TECHNOLOGY TREE OVERVIEW")
    
    # Count technologies by category
    category_counts = {}
    for node in tree.nodes.values():
        category = node.technology.category
        if category not in category_counts:
            category_counts[category] = {"total": 0, "researched": 0, "available": 0}
        category_counts[category]["total"] += 1
        if node.researched:
            category_counts[category]["researched"] += 1
        elif node.available_for_research:
            category_counts[category]["available"] += 1
    
    print(f"Total Technologies: {len(tree.nodes)}")
    print(f"Completed: {len(tree.completed_technologies)}")
    print(f"Available for Research: {len(tree.get_available_technologies())}")
    print(f"Current Research: {tree.current_research or 'None'}")
    print()
    
    # Category breakdown
    print("TECHNOLOGY CATEGORIES:")
    for category, counts in category_counts.items():
        print(f"  {category.value.upper()}: {counts['researched']}/{counts['total']} researched, "
              f"{counts['available']} available")
    
    print()
    print("CURRENTLY AVAILABLE TECHNOLOGIES:")
    available_techs = tree.get_available_technologies()
    for tech_id in available_techs[:10]:  # Show first 10
        node = tree.nodes[tech_id]
        tech = node.technology
        print(f"  • {tech.name} ({tech.category.value})")
        print(f"    {tech.description}")
        if tech.prerequisites:
            print(f"    Prerequisites: {', '.join(tech.prerequisites)}")


def demonstrate_advisor_lobbying(research_manager: TechnologyResearchManager, 
                                advisors: List[Advisor]) -> None:
    """Demonstrate advisor lobbying mechanics."""
    print_section_header("ADVISOR LOBBYING DEMONSTRATION")
    
    # Register advisors
    for advisor in advisors:
        research_manager.advisor_lobbying.register_advisor(advisor)
        print(f"Registered {advisor.name} ({advisor.role.value})")
        
        # Show their category preferences
        prefs = research_manager.advisor_lobbying.advisor_preferences[advisor.id]
        print(f"  Preferred strategy: {prefs.preferred_strategy.value}")
        print(f"  Top category preferences:")
        sorted_prefs = sorted(prefs.category_preferences.items(), 
                            key=lambda x: x[1], reverse=True)
        for category, preference in sorted_prefs[:3]:
            print(f"    - {category.value}: {preference:.2f}")
    
    print()
    print("STARTING ADVOCACY CAMPAIGNS:")
    
    # Start some advocacy campaigns
    available_techs = research_manager.technology_tree.get_available_technologies()
    
    # Military advisor advocates for intelligence tech
    intelligence_techs = [tech_id for tech_id in available_techs 
                         if research_manager.technology_tree.nodes[tech_id].technology.category 
                         == TechnologyCategory.INTELLIGENCE]
    if intelligence_techs:
        tech_id = intelligence_techs[0]
        advocacy_id = research_manager.advisor_lobbying.start_technology_advocacy(
            advisors[0].id, tech_id, 0.9, 
            "Essential for national security and military superiority"
        )
        print(f"  {advisors[0].name} advocates for {tech_id} (Intelligence)")
    
    # Economic advisor advocates for administrative tech
    admin_techs = [tech_id for tech_id in available_techs 
                  if research_manager.technology_tree.nodes[tech_id].technology.category 
                  == TechnologyCategory.ADMINISTRATIVE]
    if admin_techs:
        tech_id = admin_techs[0]
        advocacy_id = research_manager.advisor_lobbying.start_technology_advocacy(
            advisors[1].id, tech_id, 0.8,
            "Will improve economic efficiency and reduce administrative costs"
        )
        print(f"  {advisors[1].name} advocates for {tech_id} (Administrative)")
    
    # Security advisor also advocates for intelligence tech (potential coalition)
    if intelligence_techs:
        tech_id = intelligence_techs[0]
        advocacy_id = research_manager.advisor_lobbying.start_technology_advocacy(
            advisors[2].id, tech_id, 0.95,
            "Critical for maintaining internal security and surveillance capabilities"
        )
        print(f"  {advisors[2].name} also advocates for {tech_id} (Intelligence)")
    
    # Religious advisor advocates for social engineering
    social_techs = [tech_id for tech_id in available_techs 
                   if research_manager.technology_tree.nodes[tech_id].technology.category 
                   == TechnologyCategory.SOCIAL_ENGINEERING]
    if social_techs:
        tech_id = social_techs[0]
        advocacy_id = research_manager.advisor_lobbying.start_technology_advocacy(
            advisors[3].id, tech_id, 0.7,
            "Will help maintain social order and traditional values"
        )
        print(f"  {advisors[3].name} advocates for {tech_id} (Social Engineering)")


def simulate_research_turns(research_manager: TechnologyResearchManager, 
                           resource_manager: ResourceManager, turns: int = 10) -> None:
    """Simulate multiple turns of research and lobbying."""
    print_section_header(f"SIMULATING {turns} TURNS OF RESEARCH")
    
    for turn in range(1, turns + 1):
        print(f"\\n--- TURN {turn} ---")
        
        # Update research capacity from resources
        research_manager.update_from_resource_manager(resource_manager)
        
        # Process turn
        results = research_manager.advance_turn()
        
        # Report results
        print(f"Active Research: {results['active_research'] or 'None'}")
        print(f"Research Queue: {results['research_queue']}")
        
        if results['lobbying_results']['lobbying_activities']:
            print("Lobbying Activities:")
            for activity in results['lobbying_results']['lobbying_activities']:
                advisor_id = activity['advisor_id']
                tech_id = activity['technology_id']
                effectiveness = activity['effectiveness']
                outcome = activity['outcome']
                print(f"  • Advisor {advisor_id} lobbied for {tech_id}: "
                      f"{outcome} (effectiveness: {effectiveness:.2f})")
        
        if results['lobbying_results']['coalition_formations']:
            print("Coalition Formations:")
            for coalition in results['lobbying_results']['coalition_formations']:
                print(f"  • Coalition for {coalition['technology_id']}: "
                      f"{len(coalition['members'])} members, strength {coalition['strength']:.2f}")
        
        if results['research_results']['technologies_completed']:
            print("RESEARCH COMPLETED:")
            for tech_id in results['research_results']['technologies_completed']:
                tech = research_manager.technology_tree.nodes[tech_id].technology
                print(f"  • {tech.name} ({tech.category.value})")
                print(f"    Effects: {tech.political_effects}")
                
                # Apply effects to resource manager
                effects = research_manager.apply_technology_effects_to_resources(
                    resource_manager, tech_id
                )
                if any(effects.values()):
                    print(f"    Applied effects: {effects}")
        
        # Show current research progress
        if research_manager.active_research:
            progress = research_manager.research_progress.get(research_manager.active_research, 0.0)
            tech_name = research_manager.technology_tree.nodes[research_manager.active_research].technology.name
            print(f"Current research progress on {tech_name}: {progress:.1%}")


def show_technology_recommendations(research_manager: TechnologyResearchManager) -> None:
    """Show technology recommendations based on current situation."""
    print_section_header("TECHNOLOGY RECOMMENDATIONS")
    
    # Simulate some context
    context = {
        "current_threats": ["external_military", "internal_dissent"],
        "resource_state": {"economic_stress": 0.4, "social_unrest": 0.3},
        "diplomatic_situation": {"hostile_neighbors": 1, "allied_nations": 3}
    }
    
    recommendations = research_manager.get_technology_recommendations(context)
    
    print("RECOMMENDED TECHNOLOGIES (based on current situation):")
    for i, (tech_id, score, reason) in enumerate(recommendations, 1):
        tech = research_manager.technology_tree.nodes[tech_id].technology
        print(f"{i}. {tech.name} (Score: {score:.2f})")
        print(f"   Category: {tech.category.value}")
        print(f"   Reason: {reason}")
        print(f"   Description: {tech.description}")
        print()


def show_final_status(research_manager: TechnologyResearchManager) -> None:
    """Show final status of the technology system."""
    print_section_header("FINAL SYSTEM STATUS")
    
    status = research_manager.get_status_summary()
    
    print(f"Civilization: {status['civilization_id']}")
    print(f"Current Turn: {status['current_turn']}")
    print(f"Completed Technologies: {status['completed_technologies']}")
    print(f"Available Technologies: {status['available_technologies']}")
    print(f"Research Capacity: {status['research_capacity']:.2f}")
    print(f"Research Speed Multiplier: {status['research_speed']:.2f}")
    
    print("\\nActive Research:")
    if status['active_research']['technology_id']:
        print(f"  Technology: {status['active_research']['technology_id']}")
        print(f"  Progress: {status['active_research']['progress']:.1%}")
    else:
        print("  None")
    
    print(f"\\nResearch Queue: {status['research_queue']}")
    
    lobbying_summary = status['advisor_lobbying']
    print(f"\\nAdvisor Lobbying Summary:")
    print(f"  Active Campaigns: {lobbying_summary['active_campaigns']}")
    print(f"  Active Coalitions: {lobbying_summary['active_coalitions']}")
    print(f"  Registered Advisors: {lobbying_summary['registered_advisors']}")
    print(f"  Total Successful Lobbying: {lobbying_summary['total_successful_lobbying']}")
    
    if lobbying_summary['top_influential_advisors']:
        print("\\nMost Influential Advisors:")
        for advisor_id, influence in lobbying_summary['top_influential_advisors']:
            print(f"  • {advisor_id}: {influence:.2f}")
    
    if lobbying_summary['most_contested_technologies']:
        print("\\nMost Contested Technologies:")
        for tech_id, contest_level in lobbying_summary['most_contested_technologies']:
            print(f"  • {tech_id}: {contest_level} competing advisors")


def main():
    """Run the complete technology tree demonstration."""
    print("="*80)
    print("  POLITICAL STRATEGY GAME - TECHNOLOGY TREE DEMONSTRATION")
    print("="*80)
    print("\\nThis demonstration showcases the comprehensive technology tree system")
    print("with advisor lobbying, research progression, and system integration.")
    
    # Initialize systems
    print("\\nInitializing systems...")
    tree = TechnologyTree(civilization_id="demo_civ")
    research_manager = TechnologyResearchManager(
        civilization_id="demo_civ",
        technology_tree=tree
    )
    resource_manager = create_demo_resource_manager()
    advisors = create_demo_advisors()
    
    # Update research capacity from resources
    research_manager.update_from_resource_manager(resource_manager)
    
    # Demonstrate each component
    print_technology_tree_overview(tree)
    demonstrate_advisor_lobbying(research_manager, advisors)
    show_technology_recommendations(research_manager)
    simulate_research_turns(research_manager, resource_manager, 15)
    show_final_status(research_manager)
    
    print("\\n" + "="*80)
    print("  DEMONSTRATION COMPLETE")
    print("="*80)
    print("\\nThe technology tree system provides:")
    print("• 30+ political technologies across 5 categories")
    print("• Advisor-driven lobbying and preference systems")
    print("• Dynamic research prioritization based on political pressure")
    print("• Coalition building between advisors")
    print("• Integration with resource management and espionage systems")
    print("• Comprehensive testing and validation")
    print("\\nThis system enhances the political strategy game with realistic")
    print("technology progression driven by internal political dynamics.")


if __name__ == "__main__":
    main()
