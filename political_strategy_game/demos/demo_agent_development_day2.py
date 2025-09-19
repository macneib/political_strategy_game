#!/usr/bin/env python3
"""
Demo script for Agent Development System Day 2 features.

Demonstrates advanced skill development algorithms, achievement systems,
and enhanced social modeling in action.
"""

import sys
import os
import random
from typing import Dict, List

# Set up the path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from core.citizen import Citizen, Achievement, AchievementCategory
    from core.technology_tree import TechnologyEra
    from core.advisor import AdvisorRole
    from core.agent_pool import Agent, PersonalityProfile, PerformanceMetrics, SocialNetwork, MentorshipRecord
    from core.agent_development import (
        SkillDevelopmentManager, AchievementManager, EnhancedAchievement,
        SkillDevelopmentType, LearningModifier, AchievementDifficulty,
        create_skill_development_manager, create_achievement_manager
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("This demo requires the political strategy game modules to be properly installed.")
    sys.exit(1)


def create_sample_agents() -> List[Agent]:
    """Create a diverse set of sample agents for demonstration."""
    agents = []
    
    # Young prodigy agent
    prodigy = Agent(
        citizen_id="prodigy-001",
        name="Alexandria the Prodigy",
        birth_turn=50,
        era_born=TechnologyEra.CLASSICAL,
        civilization_id="demo-civ-001",
        age=22,
        skills={
            "scholarship": 0.6,
            "innovation": 0.5,
            "philosophy": 0.4,
            "science": 0.3
        },
        traits={
            "intelligence": 0.95,
            "curiosity": 0.9,
            "creativity": 0.8,
            "determination": 0.7
        },
        reputation=0.4,
        advisor_potential=0.8
    )
    agents.append(prodigy)
    
    # Experienced leader
    leader = Agent(
        citizen_id="leader-001",
        name="Marcus the Strategist",
        birth_turn=25,
        era_born=TechnologyEra.CLASSICAL,
        civilization_id="demo-civ-001",
        age=45,
        skills={
            "leadership": 0.8,
            "administration": 0.7,
            "diplomacy": 0.75,
            "combat": 0.6,
            "philosophy": 0.5
        },
        traits={
            "charisma": 0.85,
            "strategic_thinking": 0.9,
            "wisdom": 0.8,
            "empathy": 0.6,
            "courage": 0.7
        },
        reputation=0.85,
        advisor_potential=0.9
    )
    agents.append(leader)
    
    # Master craftsman
    craftsman = Agent(
        citizen_id="craftsman-001",
        name="Elena the Artisan",
        birth_turn=32,
        era_born=TechnologyEra.CLASSICAL,
        civilization_id="demo-civ-001",
        age=38,
        skills={
            "crafting": 0.9,
            "engineering": 0.6,
            "arts": 0.7,
            "innovation": 0.4,
            "trade": 0.5
        },
        traits={
            "creativity": 0.8,
            "precision": 0.9,
            "patience": 0.85,
            "aesthetic_sense": 0.8
        },
        reputation=0.6,
        advisor_potential=0.5
    )
    agents.append(craftsman)
    
    # Rising diplomat
    diplomat = Agent(
        citizen_id="diplomat-001",
        name="Chen the Mediator",
        birth_turn=35,
        era_born=TechnologyEra.CLASSICAL,
        civilization_id="demo-civ-001",
        age=35,
        skills={
            "diplomacy": 0.75,
            "trade": 0.6,
            "leadership": 0.5,
            "administration": 0.4,
            "philosophy": 0.6
        },
        traits={
            "empathy": 0.9,
            "charisma": 0.7,
            "cultural_sensitivity": 0.85,
            "patience": 0.8,
            "eloquence": 0.8
        },
        reputation=0.7,
        advisor_potential=0.75
    )
    agents.append(diplomat)
    
    # Young warrior
    warrior = Agent(
        citizen_id="warrior-001",
        name="Bjorn the Bold",
        birth_turn=42,
        era_born=TechnologyEra.CLASSICAL,
        civilization_id="demo-civ-001",
        age=28,
        skills={
            "combat": 0.85,
            "leadership": 0.4,
            "crafting": 0.3,
            "exploration": 0.6
        },
        traits={
            "courage": 0.95,
            "strength": 0.9,
            "determination": 0.8,
            "loyalty": 0.85
        },
        reputation=0.5,
        advisor_potential=0.4
    )
    agents.append(warrior)
    
    return agents


def establish_mentorship_relationships(agents: List[Agent]) -> None:
    """Establish mentorship relationships between agents."""
    # Marcus (leader) mentors younger agents
    leader = next(a for a in agents if a.name == "Marcus the Strategist")
    prodigy = next(a for a in agents if a.name == "Alexandria the Prodigy")
    diplomat = next(a for a in agents if a.name == "Chen the Mediator")
    warrior = next(a for a in agents if a.name == "Bjorn the Bold")
    
    # Leader mentors prodigy in leadership and philosophy
    mentorship1 = MentorshipRecord(
        mentor_id=leader.id,
        mentee_id=prodigy.id,
        start_turn=50,
        focus_skills=["leadership", "philosophy", "administration"],
        effectiveness_score=0.85,
        mutual_benefit=True,
        end_turn=None
    )
    prodigy.social_network.mentorship_relationships.append(mentorship1)
    
    # Leader mentors diplomat in leadership
    mentorship2 = MentorshipRecord(
        mentor_id=leader.id,
        mentee_id=diplomat.id,
        start_turn=30,
        focus_skills=["leadership", "administration"],
        effectiveness_score=0.75,
        mutual_benefit=False,
        end_turn=None
    )
    diplomat.social_network.mentorship_relationships.append(mentorship2)
    
    # Elena (craftsman) mentors warrior in crafting
    craftsman = next(a for a in agents if a.name == "Elena the Artisan")
    mentorship3 = MentorshipRecord(
        mentor_id=craftsman.id,
        mentee_id=warrior.id,
        start_turn=40,
        focus_skills=["crafting", "engineering"],
        effectiveness_score=0.8,
        mutual_benefit=False,
        end_turn=None
    )
    warrior.social_network.mentorship_relationships.append(mentorship3)


def demonstrate_skill_development():
    """Demonstrate the advanced skill development system."""
    print("\n" + "="*80)
    print("AGENT DEVELOPMENT SYSTEM DAY 2 DEMONSTRATION")
    print("="*80)
    
    # Initialize systems
    print("\n📚 Initializing Advanced Development Systems...")
    skill_manager = create_skill_development_manager()
    achievement_manager = create_achievement_manager()
    
    print(f"✓ Skill Development Manager initialized with {len(skill_manager.base_learning_rates)} skills")
    print(f"✓ Achievement Manager initialized with {len(achievement_manager.achievements)} achievements")
    print(f"✓ {len(skill_manager.skill_synergies)} skill synergy relationships configured")
    
    # Create agents
    print("\n👥 Creating Sample Agents...")
    agents = create_sample_agents()
    establish_mentorship_relationships(agents)
    
    for agent in agents:
        print(f"✓ {agent.name} (Age {agent.age}) - {len(agent.skills)} skills, {len(agent.traits)} traits")
    
    # Demonstrate learning rate calculations
    print("\n🧮 Learning Rate Analysis")
    print("-" * 50)
    
    prodigy = agents[0]  # Alexandria
    for skill in ["scholarship", "innovation", "philosophy"]:
        rate, modifiers = skill_manager.calculate_learning_rate(
            prodigy, skill, TechnologyEra.CLASSICAL, 100
        )
        modifier_names = [mod.value for mod in modifiers]
        print(f"📈 {skill.capitalize()}: {rate:.4f} learning rate | Modifiers: {modifier_names}")
    
    # Demonstrate skill synergies
    print("\n🔗 Skill Synergy Analysis")
    print("-" * 50)
    
    for agent in agents[:2]:  # Show first two agents
        print(f"\n{agent.name}:")
        for skill in list(agent.skills.keys())[:3]:  # Show first 3 skills
            synergy_bonus = skill_manager._calculate_synergy_bonus(agent, skill)
            if synergy_bonus > 0:
                print(f"  ⚡ {skill.capitalize()}: +{synergy_bonus:.1%} synergy bonus")
    
    # Simulate development over time
    print("\n⏱️  Simulating Development Over 20 Turns")
    print("-" * 50)
    
    current_era = TechnologyEra.CLASSICAL
    development_events = []
    
    for turn in range(100, 120):
        print(f"\n📅 Turn {turn}")
        
        for agent in agents:
            # Process natural development
            events = skill_manager.process_turn_development(agent, current_era, turn)
            development_events.extend(events)
            
            # Attempt achievement unlocks
            unlocked_achievements = achievement_manager.attempt_achievement_unlock(agent, current_era, turn)
            
            if events or unlocked_achievements:
                event_summary = f"{len(events)} skill developments" if events else "No developments"
                achievement_summary = f"{len(unlocked_achievements)} achievements unlocked" if unlocked_achievements else "No achievements"
                print(f"  🎯 {agent.name}: {event_summary}, {achievement_summary}")
                
                # Show achievement details
                for achievement in unlocked_achievements:
                    # Handle both enum and string difficulty values
                    difficulty_str = achievement.difficulty.value if hasattr(achievement.difficulty, 'value') else str(achievement.difficulty)
                    print(f"    🏆 '{achievement.title}' ({difficulty_str})")
    
    # Show final statistics
    print("\n📊 Development Summary")
    print("-" * 50)
    
    print(f"Total development events: {len(development_events)}")
    
    # Skill improvements
    skill_improvements = {}
    for event in development_events:
        if event.skill_name not in skill_improvements:
            skill_improvements[event.skill_name] = []
        improvement = event.new_value - event.old_value
        skill_improvements[event.skill_name].append(improvement)
    
    for skill, improvements in skill_improvements.items():
        avg_improvement = sum(improvements) / len(improvements)
        total_improvement = sum(improvements)
        print(f"📈 {skill.capitalize()}: {len(improvements)} events, avg +{avg_improvement:.3f}, total +{total_improvement:.3f}")
    
    # Development type distribution
    type_counts = {}
    for event in development_events:
        dev_type = event.development_type.value
        type_counts[dev_type] = type_counts.get(dev_type, 0) + 1
    
    print("\n🎲 Development Type Distribution:")
    for dev_type, count in sorted(type_counts.items()):
        percentage = (count / len(development_events)) * 100
        print(f"  📋 {dev_type}: {count} events ({percentage:.1f}%)")
    
    # Achievement statistics
    print("\n🏆 Achievement Statistics")
    print("-" * 50)
    
    total_achievements_unlocked = 0
    difficulty_counts = {}
    
    for agent in agents:
        agent_achievements = len(agent.achievement_history)
        total_achievements_unlocked += agent_achievements
        print(f"🎖️  {agent.name}: {agent_achievements} achievements")
        
        # Note: Basic Achievement class doesn't track difficulty, 
        # so we can't show difficulty breakdown in this demo
    
    print(f"\nTotal achievements unlocked: {total_achievements_unlocked}")
    
    if difficulty_counts:
        print("\nBy difficulty:")
        for difficulty, count in sorted(difficulty_counts.items()):
            print(f"  🌟 {difficulty.capitalize()}: {count}")
    else:
        print("\nNote: Achievement difficulty tracking requires enhanced achievement system integration")
    
    # Demonstrate mentorship effects
    print("\n👨‍🏫 Mentorship Impact Analysis")
    print("-" * 50)
    
    mentorship_events = [e for e in development_events if e.development_type == SkillDevelopmentType.MENTORSHIP]
    natural_events = [e for e in development_events if e.development_type == SkillDevelopmentType.NATURAL_LEARNING]
    
    if mentorship_events and natural_events:
        avg_mentorship_gain = sum(e.new_value - e.old_value for e in mentorship_events) / len(mentorship_events)
        avg_natural_gain = sum(e.new_value - e.old_value for e in natural_events) / len(natural_events)
        
        mentorship_advantage = (avg_mentorship_gain / avg_natural_gain - 1) * 100
        
        print(f"📚 Mentorship development events: {len(mentorship_events)}")
        print(f"🌱 Natural development events: {len(natural_events)}")
        print(f"📈 Average mentorship gain: {avg_mentorship_gain:.4f}")
        print(f"📈 Average natural gain: {avg_natural_gain:.4f}")
        print(f"⚡ Mentorship advantage: +{mentorship_advantage:.1f}%")
    
    # Show agent progression
    print("\n🎯 Agent Progression Summary")
    print("-" * 50)
    
    for agent in agents:
        print(f"\n{agent.name} (Age {agent.age}):")
        
        # Top skills
        top_skills = sorted(agent.skills.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"  🎯 Top Skills: {', '.join(f'{skill} ({value:.2f})' for skill, value in top_skills)}")
        
        # Achievements
        if agent.achievement_history:
            latest_achievement = agent.achievement_history[-1].achievement.title
            print(f"  🏆 Latest Achievement: '{latest_achievement}'")
        
        # Potential rating
        potential_rating = "Excellent" if agent.advisor_potential > 0.8 else "Good" if agent.advisor_potential > 0.6 else "Moderate"
        print(f"  ⭐ Advisor Potential: {agent.advisor_potential:.2f} ({potential_rating})")
    
    # Advanced analytics
    print("\n🔬 Advanced Analytics")
    print("-" * 50)
    
    # Age effect analysis
    age_groups = {"Young (20-30)": [], "Middle (31-45)": [], "Mature (46+)": []}
    for agent in agents:
        if agent.age <= 30:
            age_groups["Young (20-30)"].append(agent)
        elif agent.age <= 45:
            age_groups["Middle (31-45)"].append(agent)
        else:
            age_groups["Mature (46+)"].append(agent)
    
    for group_name, group_agents in age_groups.items():
        if group_agents:
            avg_achievements = sum(len(a.achievement_history) for a in group_agents) / len(group_agents)
            avg_potential = sum(a.advisor_potential for a in group_agents) / len(group_agents)
            print(f"📊 {group_name}: {len(group_agents)} agents, avg {avg_achievements:.1f} achievements, {avg_potential:.2f} potential")
    
    # Trait correlation analysis
    print("\n🧬 High-Impact Traits Analysis:")
    trait_impacts = {}
    for agent in agents:
        achievement_count = len(agent.achievement_history)
        for trait, value in agent.traits.items():
            if trait not in trait_impacts:
                trait_impacts[trait] = []
            trait_impacts[trait].append((value, achievement_count))
    
    # Calculate correlation for traits with enough data
    for trait, data in trait_impacts.items():
        if len(data) >= 3:  # Need at least 3 data points
            # Simple correlation analysis
            trait_values = [d[0] for d in data]
            achievement_counts = [d[1] for d in data]
            
            # Calculate Pearson correlation coefficient
            n = len(data)
            sum_x = sum(trait_values)
            sum_y = sum(achievement_counts)
            sum_xy = sum(x * y for x, y in data)
            sum_x2 = sum(x * x for x in trait_values)
            sum_y2 = sum(y * y for y in achievement_counts)
            
            if n * sum_x2 - sum_x * sum_x != 0 and n * sum_y2 - sum_y * sum_y != 0:
                correlation = (n * sum_xy - sum_x * sum_y) / (
                    ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
                )
                
                if abs(correlation) > 0.5:  # Show significant correlations
                    strength = "Strong" if abs(correlation) > 0.7 else "Moderate"
                    direction = "positive" if correlation > 0 else "negative"
                    print(f"  🔍 {trait}: {strength} {direction} correlation ({correlation:.2f})")
    
    print("\n✅ Agent Development System Day 2 demonstration complete!")
    print("="*80)


if __name__ == "__main__":
    try:
        demonstrate_skill_development()
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
