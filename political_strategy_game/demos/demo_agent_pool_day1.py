#!/usr/bin/env python3
"""
Agent Pool Management System Day 1 - Live Demonstration

This demonstration showcases the enhanced Agent class and AgentPoolManager
with detailed personality tracking, performance metrics, and lifecycle management.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.agent_pool import (
    Agent, AgentPoolManager, PersonalityProfile, PerformanceMetrics,
    AchievementRecord, NarrativeEvent, EnhancedRelationship, SocialNetwork,
    EventType, PerformanceTrend, create_agent_pool_manager
)
from src.core.citizen import CitizenGenerator, Achievement, AchievementCategory
from src.core.technology_tree import TechnologyEra
from src.core.advisor import AdvisorRole
import random


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f" {title}")
    print('=' * 80)


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n{'-' * 50}")
    print(f" {title}")
    print('-' * 50)


def print_agent_summary(agent: Agent):
    """Print a comprehensive summary of an agent."""
    print(f"\n🔹 Agent: {agent.name} (ID: {agent.id[:8]})")
    print(f"   Age: {agent.age}, Era Born: {agent.era_born.value}")
    print(f"   Pool Rank: #{agent.agent_pool_rank}, Tenure: {agent.pool_tenure} turns")
    
    # Skills
    print(f"   Skills: {', '.join([f'{k}: {v:.2f}' for k, v in list(agent.skills.items())[:4]])}")
    print(f"   Composite Score: {agent.calculate_composite_score():.3f}")
    print(f"   Advisor Candidacy: {agent.advisor_candidacy_score:.3f}")
    
    # Personality highlights
    dominant_traits = agent.personality_profile.dominant_traits[:3]
    print(f"   Dominant Traits: {', '.join(dominant_traits)}")
    print(f"   Decision Style: {agent.personality_profile.decision_making_style}")
    
    # Performance
    print(f"   Reputation: {agent.reputation:.3f}, Social Influence: {agent.social_network.social_influence_score:.3f}")
    print(f"   Achievement Count: {len(agent.achievement_history)}")
    
    # Specializations
    if agent.specialization_paths:
        print(f"   Specializations: {', '.join(agent.specialization_paths)}")


def demonstrate_personality_system():
    """Demonstrate the personality tracking system."""
    print_section("PERSONALITY SYSTEM DEMONSTRATION")
    
    # Create a sample citizen and promote to agent through pool manager
    generator = CitizenGenerator()
    citizen = generator.generate_citizen(TechnologyEra.CLASSICAL, 1, "demo_civ")
    citizen.age = 32
    citizen.name = "Marcus Aurelius"
    citizen.skills = {
        "leadership": 0.85,
        "philosophy": 0.90,
        "administration": 0.80,
        "diplomacy": 0.75
    }
    citizen.traits = {
        "wisdom": 0.9,
        "discipline": 0.8,
        "rationality": 0.85,
        "empathy": 0.7,
        "strategic_thinking": 0.8
    }
    citizen.reputation = 0.8
    citizen.advisor_potential = 0.85
    
    # Create pool manager and promote citizen to agent
    pool_manager = AgentPoolManager()
    agent = pool_manager.promote_to_agent_pool(citizen, turn=1)
    
    print(f"\n📋 Agent: {agent.name}")
    print(f"Personality Profile:")
    for trait, value in agent.personality_profile.core_traits.items():
        print(f"  • {trait}: {value:.3f}")
    
    print(f"\nPersonality Analysis:")
    print(f"  • Dominant Traits: {', '.join(agent.personality_profile.dominant_traits)}")
    print(f"  • Decision Making: {agent.personality_profile.decision_making_style}")
    print(f"  • Stability: {agent.personality_profile.personality_stability:.3f}")
    print(f"  • Drift Rate: {agent.personality_profile.personality_drift_rate:.3f}")
    
    # Simulate trait development over time
    print(f"\n📈 Trait Development Simulation (10 turns):")
    for turn in range(1, 11):
        # Simulate experience-based trait change
        if turn % 3 == 0 and agent.personality_profile.core_traits:  # Every 3 turns, if traits exist
            trait_to_change = random.choice(list(agent.personality_profile.core_traits.keys()))
            old_value = agent.personality_profile.core_traits[trait_to_change]
            change_amount = random.uniform(-0.05, 0.08)  # Slightly biased positive
            new_value = max(-1.0, min(1.0, old_value + change_amount))
            
            agent.personality_profile.core_traits[trait_to_change] = new_value
            
            print(f"  Turn {turn}: {trait_to_change} {old_value:.3f} → {new_value:.3f} "
                  f"({'↗' if change_amount > 0 else '↘'} {abs(change_amount):.3f})")


def demonstrate_performance_system():
    """Demonstrate the performance tracking system."""
    print_section("PERFORMANCE TRACKING SYSTEM")
    
    generator = CitizenGenerator()
    citizen = generator.generate_citizen(TechnologyEra.CLASSICAL, 1, "demo_civ")
    citizen.age = 28
    citizen.name = "Cicero the Orator"
    citizen.skills = {
        "diplomacy": 0.88,
        "leadership": 0.75,
        "administration": 0.70,
        "philosophy": 0.82
    }
    citizen.reputation = 0.8
    citizen.advisor_potential = 0.85
    
    # Create through pool manager to get proper initialization
    pool_manager = AgentPoolManager()
    agent = pool_manager.promote_to_agent_pool(citizen, turn=1)
    
    print(f"\n📊 Performance Metrics for: {agent.name}")
    
    # Access performance tracking
    metrics = agent.performance_metrics
    initial_score = agent.calculate_composite_score()
    
    print(f"Initial Composite Score: {initial_score:.3f}")
    print(f"Achievement Rate: {metrics.achievement_rate:.3f}")
    print(f"Leadership Emergence: {metrics.leadership_emergence_score:.3f}")
    print(f"Advisor Readiness: {metrics.advisor_readiness_score:.3f}")
    
    # Simulate performance over time
    print(f"\n📈 Performance Development Over 20 Turns:")
    for turn in range(1, 21):
        # Simulate skill improvement
        if turn % 5 == 0:  # Every 5 turns
            skill_to_improve = random.choice(list(agent.skills.keys()))
            improvement = random.uniform(0.02, 0.06)
            agent.skills[skill_to_improve] = min(1.0, agent.skills[skill_to_improve] + improvement)
        
        # Calculate new performance
        current_score = agent.calculate_composite_score()
        
        # Create performance snapshot
        if turn % 5 == 0:
            trend = PerformanceTrend.RISING if current_score > metrics.peak_composite_score else PerformanceTrend.STABLE
            
            snapshot = {
                "turn": turn,
                "composite_score": current_score,
                "skill_scores": agent.skills.copy(),
                "achievement_count": len(agent.achievement_history),
                "reputation": agent.reputation,
                "social_influence": agent.social_network.social_influence_score,
                "trend": trend
            }
            
            metrics.performance_trend.append(snapshot)
            
            # Update peak if necessary
            if current_score > metrics.peak_composite_score:
                metrics.peak_composite_score = current_score
                metrics.peak_performance_period = (turn - 4, turn)
            
            print(f"  Turn {turn:2d}: Score {current_score:.3f} (Peak: {metrics.peak_composite_score:.3f}) "
                  f"Trend: {trend.value}")
    
    print(f"\nFinal Performance Summary:")
    print(f"  • Peak Score: {metrics.peak_composite_score:.3f}")
    print(f"  • Peak Period: Turns {metrics.peak_performance_period}")
    print(f"  • Performance Snapshots: {len(metrics.performance_trend)}")


def demonstrate_social_network():
    """Demonstrate the enhanced social network system."""
    print_section("SOCIAL NETWORK SYSTEM")
    
    generator = CitizenGenerator()
    citizen = generator.generate_citizen(TechnologyEra.CLASSICAL, 1, "demo_civ")
    citizen.age = 35
    citizen.name = "Quintus Fabius"
    citizen.reputation = 0.7
    citizen.advisor_potential = 0.8
    
    # Create through pool manager to get proper initialization
    pool_manager = AgentPoolManager()
    agent = pool_manager.promote_to_agent_pool(citizen, turn=1)
    
    print(f"\n🌐 Social Network for: {agent.name}")
    
    # Create some relationships
    relationship_types = ["mentor", "colleague", "protege", "ally", "friend"]
    for i in range(5):
        other_agent_id = f"agent_{i:03d}"
        rel_type = random.choice(relationship_types)
        
        relationship = EnhancedRelationship(
            other_agent_id=other_agent_id,
            relationship_type=rel_type,
            strength=random.uniform(0.4, 0.9),
            trust_level=random.uniform(0.3, 0.8),
            loyalty=random.uniform(0.3, 0.8),
            compatibility=random.uniform(0.4, 0.9)
        )
        
        agent.social_network.relationships[other_agent_id] = relationship
    
    print(f"Network Capacity: {agent.social_network.relationship_capacity}")
    print(f"Social Influence: {agent.social_network.social_influence_score:.3f}")
    print(f"Network Centrality: {agent.social_network.network_centrality:.3f}")
    print(f"Connection Quality: {agent.social_network.connection_quality:.3f}")
    
    print(f"\n🔗 Relationships ({len(agent.social_network.relationships)}):")
    for agent_id, rel in agent.social_network.relationships.items():
        print(f"  • {agent_id}: {rel.relationship_type} "
              f"(Strength: {rel.strength:.2f}, Trust: {rel.trust_level:.2f}, "
              f"Loyalty: {rel.loyalty:.2f})")
    
    # Demonstrate mentorship
    print(f"\n👨‍🏫 Mentorship Simulation:")
    from src.core.agent_pool import MentorshipRecord
    
    mentorship = MentorshipRecord(
        mentor_id="agent_senior_001",
        mentee_id=agent.id,
        start_turn=10,
        end_turn=None,
        focus_skills=["leadership", "diplomacy"],
        effectiveness_score=0.85,
        mutual_benefit=True
    )
    
    agent.social_network.mentorship_relationships.append(mentorship)
    
    print(f"  Mentor: {mentorship.mentor_id}")
    print(f"  Focus Skills: {', '.join(mentorship.focus_skills)}")
    print(f"  Effectiveness: {mentorship.effectiveness_score:.2f}")
    print(f"  Mutual Benefit: {mentorship.mutual_benefit}")


def demonstrate_pool_management():
    """Demonstrate the agent pool management system."""
    print_section("AGENT POOL MANAGEMENT SYSTEM")
    
    # Create pool manager
    pool_manager = create_agent_pool_manager(pool_size_target=20)
    generator = CitizenGenerator()
    
    print(f"🏛️ Agent Pool Manager Configuration:")
    print(f"  Target Size: {pool_manager.pool_size_target}")
    print(f"  Min Size: {pool_manager.min_pool_size}")
    print(f"  Max Size: {pool_manager.max_pool_size}")
    
    # Create a population of citizens
    print(f"\n👥 Generating Population of 50 Citizens...")
    citizens = []
    for i in range(50):
        citizen = generator.generate_citizen(TechnologyEra.CLASSICAL, 1, "demo_civ")
        citizen.age = random.randint(25, 55)
        citizen.name = f"Citizen {i:03d}"
        
        # Vary the quality - some will be promotion-worthy
        skill_multiplier = random.uniform(0.5, 1.2)
        for skill in citizen.skills:
            citizen.skills[skill] *= skill_multiplier
            citizen.skills[skill] = min(1.0, citizen.skills[skill])
        
        citizen.reputation = random.uniform(0.3, 0.9)
        citizens.append(citizen)
    
    # Evaluate promotion candidates
    candidates = pool_manager.evaluate_promotion_candidates(citizens, turn=1)
    print(f"\n📋 Promotion Evaluation Results:")
    print(f"  Citizens Evaluated: {len(citizens)}")
    print(f"  Promotion Candidates: {len(candidates)}")
    
    if candidates:
        print(f"\n🌟 Top 5 Promotion Candidates:")
        for i, candidate in enumerate(candidates[:5]):
            score = pool_manager._calculate_promotion_score(candidate)
            print(f"  {i+1}. {candidate.name}: Score {score:.3f}, "
                  f"Skills: {len([s for s in candidate.skills.values() if s > 0.3])}, "
                  f"Rep: {candidate.reputation:.2f}")
    
    # Promote top candidates
    print(f"\n⬆️ Promoting Top Candidates...")
    promoted_count = 0
    for candidate in candidates[:10]:  # Promote up to 10
        if pool_manager._meets_promotion_criteria(candidate, 1):
            agent = pool_manager.promote_to_agent_pool(candidate, turn=1)
            promoted_count += 1
    
    print(f"  Agents Promoted: {promoted_count}")
    print(f"  Current Pool Size: {len(pool_manager.agent_pool)}")
    
    # Show top performers
    if pool_manager.agent_pool:
        print(f"\n🏆 Top 5 Agents in Pool:")
        top_agents = pool_manager.get_top_performers(5)
        for i, agent in enumerate(top_agents):
            print(f"  {i+1}. {agent.name}: Composite {agent.calculate_composite_score():.3f}, "
                  f"Candidacy {agent.advisor_candidacy_score:.3f}")


def demonstrate_narrative_events():
    """Demonstrate the narrative event system."""
    print_section("NARRATIVE EVENT SYSTEM")
    
    generator = CitizenGenerator()
    citizen = generator.generate_citizen(TechnologyEra.CLASSICAL, 1, "demo_civ")
    citizen.age = 29
    citizen.name = "Gaius Marius"
    citizen.reputation = 0.7
    citizen.advisor_potential = 0.8
    
    # Create through pool manager to get proper initialization
    pool_manager = AgentPoolManager()
    agent = pool_manager.promote_to_agent_pool(citizen, turn=1)
    
    # Create various narrative events
    events = [
        {
            "type": EventType.PROMOTION,
            "title": "Elevated to Elite Status",
            "description": "Recognized for exceptional leadership during crisis",
            "reputation_impact": 0.15,
            "skill_effects": {"leadership": 0.05, "administration": 0.03}
        },
        {
            "type": EventType.ACHIEVEMENT_UNLOCK,
            "title": "Master Negotiator",
            "description": "Successfully mediated complex trade disputes",
            "reputation_impact": 0.08,
            "skill_effects": {"diplomacy": 0.06, "trade": 0.04}
        },
        {
            "type": EventType.LEADERSHIP_EMERGENCE,
            "title": "Crisis Leadership",
            "description": "Took charge during economic downturn",
            "reputation_impact": 0.12,
            "skill_effects": {"leadership": 0.08, "administration": 0.05}
        },
        {
            "type": EventType.INNOVATION_SUCCESS,
            "title": "Administrative Innovation",
            "description": "Developed new taxation system",
            "reputation_impact": 0.10,
            "skill_effects": {"administration": 0.07, "innovation": 0.05}
        }
    ]
    
    print(f"\n📚 Narrative Events for: {agent.name}")
    
    for turn, event_data in enumerate(events, 1):
        event = NarrativeEvent(
            turn=turn * 10,
            event_type=event_data["type"],
            title=event_data["title"],
            description=event_data["description"],
            primary_agent_id=agent.id,
            impact_on_reputation=event_data["reputation_impact"],
            skill_development_effects=event_data["skill_effects"],
            narrative_weight=0.8,
            story_importance="major"
        )
        
        agent.narrative_history.append(event)
        
        # Apply effects
        agent.reputation = min(1.0, agent.reputation + event_data["reputation_impact"])
        for skill, effect in event_data["skill_effects"].items():
            if skill in agent.skills:
                agent.skills[skill] = min(1.0, agent.skills[skill] + effect)
            else:
                agent.skills[skill] = effect  # Add new skill if it doesn't exist
        
        print(f"\n  📅 Turn {event.turn}: {event.title}")
        print(f"      {event.description}")
        print(f"      Impact: Reputation +{event.impact_on_reputation:.2f}")
        print(f"      Skills: {', '.join([f'{k}+{v:.2f}' for k, v in event_data['skill_effects'].items()])}")
    
    print(f"\n📈 Final Status After Events:")
    print(f"  • Reputation: {agent.reputation:.3f}")
    print(f"  • Composite Score: {agent.calculate_composite_score():.3f}")
    print(f"  • Narrative Events: {len(agent.narrative_history)}")


def demonstrate_complete_system():
    """Demonstrate the complete integrated system."""
    print_section("COMPLETE SYSTEM INTEGRATION")
    
    # Create pool manager with realistic settings
    pool_manager = AgentPoolManager(pool_size_target=15, min_pool_size=8, max_pool_size=25)
    generator = CitizenGenerator()
    
    print(f"🎯 Multi-Turn Agent Pool Simulation")
    
    # Generate initial population
    population = []
    for i in range(100):
        citizen = generator.generate_citizen(TechnologyEra.CLASSICAL, 1, "demo_civ")
        citizen.age = random.randint(22, 60)
        population.append(citizen)
    
    print(f"\n👥 Initial Population: {len(population)} citizens")
    
    # Simulate multiple turns
    for turn in range(1, 11):
        print(f"\n--- Turn {turn} ---")
        
        # Update agent pool
        results = pool_manager.update_agent_pool(turn, population)
        
        print(f"Pool Update Results:")
        print(f"  • Promoted: {len(results['promoted'])}")
        print(f"  • Demoted: {len(results['demoted'])}")
        print(f"  • Current Size: {results['pool_size']}")
        
        # Age the population and agents
        for citizen in population:
            citizen.age += 1
        
        for agent in pool_manager.agent_pool:
            agent.age += 1
            agent.pool_tenure += 1
            
            # Simulate some development
            if random.random() < 0.3:  # 30% chance of skill improvement
                skill = random.choice(list(agent.skills.keys()))
                improvement = random.uniform(0.01, 0.03)
                agent.skills[skill] = min(1.0, agent.skills[skill] + improvement)
        
        # Show top performers every few turns
        if turn % 3 == 0:
            top_agents = pool_manager.get_top_performers(3)
            print(f"  Top 3 Agents:")
            for i, agent in enumerate(top_agents):
                print(f"    {i+1}. {agent.name}: {agent.calculate_composite_score():.3f}")
    
    # Final statistics
    print(f"\n📊 Final Pool Statistics:")
    stats = pool_manager.pool_statistics
    print(f"  • Total Promotions: {stats['total_promotions']}")
    print(f"  • Total Demotions: {stats['total_demotions']}")
    print(f"  • Average Tenure: {stats['average_tenure']:.1f} turns")
    print(f"  • Final Pool Size: {len(pool_manager.agent_pool)}")
    
    if pool_manager.agent_pool:
        print(f"\n🌟 Final Top Agents:")
        for i, agent in enumerate(pool_manager.get_top_performers(5)):
            print_agent_summary(agent)


def main():
    """Main demonstration function."""
    print("🎯 AGENT POOL MANAGEMENT SYSTEM - DAY 1 DEMONSTRATION")
    print("Task 1.3: Enhanced Agent Class and Pool Management")
    print(f"{'=' * 80}")
    
    try:
        # Individual system demonstrations
        demonstrate_personality_system()
        demonstrate_performance_system()
        demonstrate_social_network()
        demonstrate_narrative_events()
        demonstrate_pool_management()
        
        # Complete integrated demonstration
        demonstrate_complete_system()
        
        print_section("DEMONSTRATION COMPLETE")
        print("✅ All Agent Pool Management System components successfully demonstrated!")
        print("📋 Key Features Validated:")
        print("   • Enhanced Agent class with detailed personality profiles")
        print("   • Comprehensive performance tracking and metrics")
        print("   • Advanced social network and relationship management")
        print("   • Narrative event system for story consistency")
        print("   • Intelligent promotion and demotion criteria")
        print("   • Multi-turn lifecycle management")
        print("   • Complete pool statistics and analytics")
        
    except Exception as e:
        print(f"\n❌ Error in demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
