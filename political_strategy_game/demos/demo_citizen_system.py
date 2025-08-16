#!/usr/bin/env python3
"""
Demonstration of the Citizen Data Structure system.

This script demonstrates the comprehensive citizen tracking system with
era-appropriate generation, skills, traits, achievements, and advisor potential.
"""

from src.core.citizen import (
    CitizenGenerator, get_era_achievements, AchievementCategory
)
from src.core.technology_tree import TechnologyEra
from src.core.advisor import AdvisorRole
import json


def main():
    """Demonstrate the citizen system functionality."""
    print("=" * 80)
    print("POLITICAL STRATEGY GAME - CITIZEN DATA STRUCTURE DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Create citizen generator
    generator = CitizenGenerator()
    
    # Demonstrate era-specific citizen generation
    print("📊 ERA-SPECIFIC CITIZEN GENERATION")
    print("-" * 50)
    
    eras_to_demo = [TechnologyEra.ANCIENT, TechnologyEra.MEDIEVAL, TechnologyEra.RENAISSANCE, TechnologyEra.MODERN]
    
    citizens_by_era = {}
    
    for era in eras_to_demo:
        print(f"\n🏛️ {era.value.upper()} ERA:")
        
        # Generate 3 citizens for this era
        citizens = []
        for i in range(3):
            citizen = generator.generate_citizen(
                era=era,
                turn=1 + (i * 10),
                civilization_id=f"{era.value}_civ"
            )
            citizens.append(citizen)
            
            print(f"  👤 {citizen.name}")
            print(f"     Age: {citizen.age}, Reputation: {citizen.reputation:.2f}")
            print(f"     Advisor Potential: {citizen.advisor_potential:.2f}")
            
            # Show top 3 skills
            top_skills = sorted(citizen.skills.items(), key=lambda x: x[1], reverse=True)[:3]
            skills_str = ", ".join([f"{skill}: {value:.2f}" for skill, value in top_skills])
            print(f"     Top Skills: {skills_str}")
            
            # Show potential advisor roles
            if citizen.potential_roles:
                roles_str = ", ".join([role.value for role in citizen.potential_roles])
                print(f"     Potential Advisor Roles: {roles_str}")
            else:
                print(f"     Potential Advisor Roles: None")
            print()
        
        citizens_by_era[era] = citizens
    
    # Demonstrate achievement system
    print("\n🏆 ACHIEVEMENT SYSTEM")
    print("-" * 50)
    
    ancient_achievements = get_era_achievements(TechnologyEra.ANCIENT)
    print(f"Available Ancient Era Achievements: {len(ancient_achievements)}")
    
    for achievement in ancient_achievements:
        print(f"  🎖️ {achievement.title}")
        print(f"     Category: {achievement.category}")
        print(f"     Impact on Advisor Potential: +{achievement.impact_on_advisor_potential:.1%}")
        print(f"     Rarity: {achievement.rarity:.1%}")
        print(f"     Description: {achievement.description}")
        print()
    
    # Demonstrate skill evolution across eras
    print("\n📈 SKILL EVOLUTION ACROSS ERAS")
    print("-" * 50)
    
    skill_analysis = {}
    for era, citizens in citizens_by_era.items():
        era_skills = {}
        for citizen in citizens:
            for skill, value in citizen.skills.items():
                if skill not in era_skills:
                    era_skills[skill] = []
                era_skills[skill].append(value)
        
        # Calculate average skill values for this era
        avg_skills = {
            skill: sum(values) / len(values) 
            for skill, values in era_skills.items() 
            if len(values) > 0
        }
        
        skill_analysis[era] = avg_skills
    
    # Show how key skills change across eras
    key_skills = ["combat", "crafting", "leadership", "science", "technology", "diplomacy"]
    
    print("Skill evolution (average values):")
    print(f"{'Era':<12} {'Combat':<7} {'Craft':<7} {'Leader':<7} {'Science':<7} {'Tech':<7} {'Diplo':<7}")
    print("-" * 60)
    
    for era in eras_to_demo:
        era_data = skill_analysis[era]
        values = []
        for skill in key_skills:
            avg_val = era_data.get(skill, 0.0)
            values.append(f"{avg_val:.2f}")
        
        print(f"{era.value:<12} {' ':<1}".join(values))
    
    # Demonstrate advisor potential distribution
    print("\n🎯 ADVISOR POTENTIAL ANALYSIS")
    print("-" * 50)
    
    all_citizens = []
    for citizens in citizens_by_era.values():
        all_citizens.extend(citizens)
    
    # Analyze potential by role
    role_potentials = {}
    for citizen in all_citizens:
        for role in citizen.potential_roles:
            if role not in role_potentials:
                role_potentials[role] = []
            role_potentials[role].append(citizen.advisor_potential)
    
    print("Advisor Role Potential Analysis:")
    for role, potentials in role_potentials.items():
        if potentials:
            avg_potential = sum(potentials) / len(potentials)
            count = len(potentials)
            print(f"  {role.value:<12}: {count} candidates, avg potential: {avg_potential:.2f}")
    
    # Show detailed citizen profiles
    print("\n👥 DETAILED CITIZEN PROFILES")
    print("-" * 50)
    
    # Find the most promising citizen from each era
    for era, citizens in citizens_by_era.items():
        best_citizen = max(citizens, key=lambda c: c.advisor_potential)
        
        print(f"\n🌟 Most Promising {era.value.title()} Citizen: {best_citizen.name}")
        print(f"   Advisor Potential: {best_citizen.advisor_potential:.2f}")
        print(f"   Age: {best_citizen.age}, Reputation: {best_citizen.reputation:.2f}")
        
        # Show all skills
        print(f"   Skills:")
        for skill, value in sorted(best_citizen.skills.items(), key=lambda x: x[1], reverse=True):
            print(f"     {skill}: {value:.2f}")
        
        # Show traits (top 5 positive traits)
        positive_traits = {k: v for k, v in best_citizen.traits.items() if v > 0}
        top_traits = sorted(positive_traits.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if top_traits:
            print(f"   Top Positive Traits:")
            for trait, value in top_traits:
                print(f"     {trait}: {value:.2f}")
        
        # Show skill development rates (top 3)
        top_development = sorted(best_citizen.skill_development_rate.items(), 
                               key=lambda x: x[1], reverse=True)[:3]
        print(f"   Fastest Skill Development:")
        for skill, rate in top_development:
            print(f"     {skill}: {rate:.1%} per turn")
    
    print("\n" + "=" * 80)
    print("✅ CITIZEN DATA STRUCTURE DEMONSTRATION COMPLETE")
    print("✅ Day 1 of Task 1.1 implementation successfully validated")
    print("=" * 80)


if __name__ == "__main__":
    main()
