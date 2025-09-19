#!/usr/bin/env python3
"""
Demo: Agent Development Day 3 - Advanced Lifecycle Management and Social Modeling

This demo showcases the advanced lifecycle management, multi-dimensional reputation 
tracking, and complex social dynamics systems implemented in Day 3.

Features demonstrated:
- Advanced lifecycle stages and aging effects
- Multi-dimensional reputation management
- Social dynamics and relationship evolution
- Succession planning and knowledge transfer
- Integration of all Day 3 systems

Run: python demo_agent_development_day3.py
"""

import random
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.agent_development import (
    AdvancedLifecycleManager, ReputationManager, SocialDynamicsManager,
    LifecycleStage, ReputationDimension, RelationshipEvolution, SuccessionType,
    SocialInfluenceType
)
from src.core.agent_pool import Agent, SocialNetwork, PersonalityProfile, PerformanceMetrics


def create_demo_agent(agent_id: str, name: str, age: int, skills: dict, traits: dict) -> Agent:
    """Create a sample agent for demonstration."""
    return Agent(
        id=agent_id,
        name=name,
        birth_turn=1,
        era_born="classical",
        civilization_id="demo_civ",
        age=age,
        is_alive=True,
        skills=skills,
        traits=traits,
        achievements=[],
        achievement_points=0.0,
        relationships={},
        social_influence=0.0,
        reputation=0.5,
        advisor_potential=0.5,
        potential_roles=set(),
        advisor_readiness=False,
        last_potential_calculation=0,
        primary_occupation=None,
        specializations=[],
        notable_contributions=[],
        recent_performance=[],
        peak_performance_turn=None,
        peak_performance_value=0.0,
        personality_profile=PersonalityProfile(),
        performance_metrics=PerformanceMetrics(),
        achievement_history=[],
        narrative_history=[],
        social_network=SocialNetwork(),
        promotion_turn=0,
        agent_pool_rank=0,
        pool_tenure=0,
        specialization_paths=[],
        primary_specialization=None,
        specialization_progress={},
        mentor_relationships=[],
        protege_relationships=[],
        mentorship_effectiveness={},
        peak_performance_period=None,
        performance_decline_started=None,
        retirement_probability=0.0,
        succession_candidates=[],
        legacy_achievements=[],
        agent_composite_score=0.0,
        advisor_candidacy_score=0.0,
        leadership_potential=0.0,
        innovation_potential=0.0
    )


def print_section_header(title: str):
    """Print a formatted section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def print_subsection(title: str):
    """Print a formatted subsection."""
    print(f"\n--- {title} ---")


def demo_lifecycle_management():
    """Demonstrate advanced lifecycle management features."""
    print_section_header("ADVANCED LIFECYCLE MANAGEMENT DEMO")
    
    lifecycle_manager = AdvancedLifecycleManager()
    
    # Create agents at different lifecycle stages
    agents = [
        create_demo_agent("young_001", "Marcus", 22, 
                         {"leadership": 0.3, "learning": 0.8}, {"curiosity": 0.7, "energy": 0.9}),
        create_demo_agent("prime_001", "Sophia", 42, 
                         {"leadership": 0.8, "diplomacy": 0.7}, {"wisdom": 0.6, "charisma": 0.8}),
        create_demo_agent("elder_001", "Aurelius", 68, 
                         {"wisdom": 0.9, "leadership": 0.9}, {"wisdom": 0.9, "patience": 0.8})
    ]
    
    print_subsection("Lifecycle Stage Determination")
    for agent in agents:
        stage = lifecycle_manager.determine_lifecycle_stage(agent)
        print(f"{agent.name} (age {agent.age}): {stage.value}")
        
        # Show aging effects
        effects = lifecycle_manager.apply_aging_effects(agent, stage)
        if effects:
            print(f"  Aging effects: {effects}")
    
    print_subsection("Retirement Probability Analysis")
    for agent in agents:
        stage = lifecycle_manager.determine_lifecycle_stage(agent)
        retirement_prob = lifecycle_manager.calculate_retirement_probability(agent, stage)
        print(f"{agent.name}: {retirement_prob:.2%} retirement probability")
    
    print_subsection("Succession Planning")
    # Use the elder agent as mentor
    mentor = agents[2]
    candidates = agents[:2]  # Young and prime agents as candidates
    
    succession_plan = lifecycle_manager.create_succession_plan(
        mentor, candidates, SuccessionType.COMPETITIVE_SELECTION
    )
    
    print(f"Succession plan for {mentor.name}:")
    print(f"  Type: {succession_plan.succession_type}")
    print(f"  Timeline: {succession_plan.timeline} turns")
    print(f"  Candidates: {len(succession_plan.readiness_scores)}")
    
    for candidate_id, score in succession_plan.readiness_scores.items():
        candidate = next(c for c in candidates if c.id == candidate_id)
        print(f"    {candidate.name}: {score:.2f} readiness score")
    
    # Create knowledge transfer plan
    if candidates:
        best_candidate = max(candidates, key=lambda c: succession_plan.readiness_scores.get(c.id, 0))
        transfer_plan = lifecycle_manager._create_knowledge_transfer_plan(mentor, best_candidate)
        
        print(f"\nKnowledge Transfer Plan ({mentor.name} → {best_candidate.name}):")
        print(f"  Plan Details: {transfer_plan}")
        if isinstance(transfer_plan, dict):
            print(f"  Skills to Transfer: {list(transfer_plan.keys())}")
        else:
            print(f"  Focus Skills: {transfer_plan.focus_skills}")
            print(f"  Methods: {transfer_plan.transfer_methods}")
            print(f"  Timeline: {transfer_plan.estimated_duration} turns")


def demo_reputation_management():
    """Demonstrate multi-dimensional reputation management."""
    print_section_header("MULTI-DIMENSIONAL REPUTATION MANAGEMENT DEMO")
    
    reputation_manager = ReputationManager()
    
    # Create agents with different reputation profiles
    diplomat = create_demo_agent("diplomat_001", "Cicero", 45,
                                {"diplomacy": 0.9, "rhetoric": 0.8}, {"charisma": 0.8, "integrity": 0.7})
    
    warrior = create_demo_agent("warrior_001", "Spartacus", 35,
                               {"combat": 0.9, "leadership": 0.7}, {"courage": 0.9, "honor": 0.8})
    
    # Initialize reputation dimensions using private attributes
    object.__setattr__(diplomat, '_reputation_dimensions', {dim: 0.5 for dim in ReputationDimension})
    object.__setattr__(warrior, '_reputation_dimensions', {dim: 0.5 for dim in ReputationDimension})
    
    print_subsection("Initial Reputation Profiles")
    
    agents = [diplomat, warrior]
    for agent in agents:
        overall_rep = reputation_manager._calculate_overall_reputation(agent)
        print(f"{agent.name}: {overall_rep:.2f} overall reputation")
    
    print_subsection("Reputation Updates from Events")
    
    # Diplomat successful negotiation
    new_rep = reputation_manager.update_reputation(
        diplomat,
        ReputationDimension.CHARISMA,
        0.15,
        "Successfully negotiated peace treaty",
        ["witness_001", "witness_002", "witness_003"],
        public_awareness=0.9,
        turn=50
    )
    print(f"Diplomat charisma reputation after peace treaty: {new_rep:.2f}")
    
    # Warrior demonstrates leadership in battle
    new_rep = reputation_manager.update_reputation(
        warrior,
        ReputationDimension.LEADERSHIP,
        0.2,
        "Led successful military campaign",
        ["soldier_001", "soldier_002"],
        public_awareness=0.7,
        turn=51
    )
    print(f"Warrior leadership reputation after military success: {new_rep:.2f}")
    
    print_subsection("Social Influence Calculation")
    
    # Calculate influence between agents
    influence_score = reputation_manager.calculate_social_influence(
        diplomat, warrior, SocialInfluenceType.PERSONAL_CHARM
    )
    print(f"Diplomat's charm influence on Warrior: {influence_score:.2f}")
    
    # Check resistance and amplification factors
    resistance = reputation_manager._identify_resistance_factors(diplomat, [warrior])
    amplification = reputation_manager._identify_amplification_factors(diplomat, [warrior])
    
    print(f"Resistance factors: {resistance}")
    print(f"Amplification factors: {amplification}")
    
    print_subsection("Reputation Decay Over Time")
    
    # Apply reputation decay
    original_rep = diplomat._reputation_dimensions[ReputationDimension.CHARISMA]
    decay_applied = reputation_manager.apply_reputation_decay(diplomat, turn=100)
    new_rep = diplomat._reputation_dimensions[ReputationDimension.CHARISMA]
    
    print(f"Diplomat charisma reputation decay: {original_rep:.2f} → {new_rep:.2f}")
    print(f"Decay details: {decay_applied}")


def demo_social_dynamics():
    """Demonstrate complex social dynamics and relationship evolution."""
    print_section_header("COMPLEX SOCIAL DYNAMICS DEMO")
    
    dynamics_manager = SocialDynamicsManager()
    
    # Create a network of agents
    agents = [
        create_demo_agent("leader_001", "Augustus", 40,
                         {"leadership": 0.9, "strategy": 0.8}, {"charisma": 0.8, "ambition": 0.7}),
        create_demo_agent("advisor_001", "Seneca", 50,
                         {"wisdom": 0.9, "philosophy": 0.8}, {"wisdom": 0.9, "patience": 0.7}),
        create_demo_agent("general_001", "Germanicus", 35,
                         {"combat": 0.9, "tactics": 0.8}, {"courage": 0.9, "loyalty": 0.8})
    ]
    
    print_subsection("Initial Relationship Dynamics Creation")
    
    # Create relationships between agents
    relationships = []
    for i, agent_a in enumerate(agents):
        for agent_b in agents[i+1:]:
            dynamics = dynamics_manager.create_relationship_dynamics(agent_a, agent_b)
            relationships.append(dynamics)
            print(f"{agent_a.name} ↔ {agent_b.name}: {dynamics.current_strength:.2f} strength, "
                  f"{dynamics.trust_level:.2f} trust")
    
    print_subsection("Relationship Evolution Through Interactions")
    
    # Simulate interactions between Augustus and Seneca
    augustus_seneca = relationships[0]  # Assume this is Augustus-Seneca relationship
    
    interactions = [
        ("consultation", "success", "Augustus seeks Seneca's counsel"),
        ("collaboration", "success", "Joint policy development"),
        ("disagreement", "resolution", "Philosophical debate resolved"),
        ("support", "given", "Seneca supports Augustus in crisis")
    ]
    
    print(f"Evolving {augustus_seneca.agent_a_id} ↔ {augustus_seneca.agent_b_id} relationship:")
    
    for turn, (interaction_type, outcome, description) in enumerate(interactions, 60):
        print(f"\nTurn {turn}: {description}")
        original_strength = augustus_seneca.current_strength
        original_trust = augustus_seneca.trust_level
        
        augustus_seneca = dynamics_manager.evolve_relationship(
            augustus_seneca, interaction_type, outcome, turn
        )
        
        print(f"  Strength: {original_strength:.2f} → {augustus_seneca.current_strength:.2f}")
        print(f"  Trust: {original_trust:.2f} → {augustus_seneca.trust_level:.2f}")
        print(f"  Evolution: {augustus_seneca.evolution_trend.value}")
        
        if augustus_seneca.shared_experiences:
            print(f"  Latest experience: {augustus_seneca.shared_experiences[-1]}")
    
    print_subsection("Network Position Analysis")
    
    # Analyze network positions
    for agent in agents:
        position_metrics = dynamics_manager.analyze_network_position(agent, agents)
        print(f"\n{agent.name}'s Network Position:")
        for metric, value in position_metrics.items():
            print(f"  {metric}: {value:.3f}")
    
    print_subsection("Interaction Frequency Calculation")
    
    # Calculate interaction frequencies
    for relationship in relationships:
        agent_a = next(a for a in agents if a.id == relationship.agent_a_id)
        agent_b = next(a for a in agents if a.id == relationship.agent_b_id)
        
        frequency = dynamics_manager._calculate_interaction_frequency(agent_a, agent_b)
        print(f"{agent_a.name} ↔ {agent_b.name}: {frequency:.2f} interaction frequency")


def demo_integrated_systems():
    """Demonstrate integration of all Day 3 systems working together."""
    print_section_header("INTEGRATED SYSTEMS DEMONSTRATION")
    
    # Initialize all managers
    lifecycle_manager = AdvancedLifecycleManager()
    reputation_manager = ReputationManager()
    dynamics_manager = SocialDynamicsManager()
    
    # Create a comprehensive scenario with aging mentor and rising successor
    mentor = create_demo_agent("mentor_001", "Marcus Aurelius", 65,
                              {"wisdom": 0.95, "leadership": 0.9, "philosophy": 0.9},
                              {"wisdom": 0.9, "patience": 0.8, "integrity": 0.9})
    
    successor = create_demo_agent("successor_001", "Commodus", 28,
                                 {"leadership": 0.6, "ambition": 0.8},
                                 {"ambition": 0.8, "charisma": 0.7})
    
    # Initialize reputation dimensions
    object.__setattr__(mentor, '_reputation_dimensions', {
        ReputationDimension.WISDOM: 0.95,
        ReputationDimension.INTEGRITY: 0.9,
        ReputationDimension.LEADERSHIP: 0.9,
        ReputationDimension.COMPETENCE: 0.85
    })
    
    object.__setattr__(successor, '_reputation_dimensions', {dim: 0.5 for dim in ReputationDimension})
    
    print_subsection("Initial System State")
    
    # Analyze mentor's lifecycle stage
    mentor_stage = lifecycle_manager.determine_lifecycle_stage(mentor)
    retirement_prob = lifecycle_manager.calculate_retirement_probability(mentor, mentor_stage)
    
    print(f"Mentor ({mentor.name}):")
    print(f"  Age: {mentor.age}, Stage: {mentor_stage.value}")
    print(f"  Retirement Probability: {retirement_prob:.2%}")
    print(f"  Overall Reputation: {reputation_manager._calculate_overall_reputation(mentor):.2f}")
    
    successor_stage = lifecycle_manager.determine_lifecycle_stage(successor)
    print(f"\nSuccessor ({successor.name}):")
    print(f"  Age: {successor.age}, Stage: {successor_stage.value}")
    print(f"  Overall Reputation: {reputation_manager._calculate_overall_reputation(successor):.2f}")
    
    print_subsection("Mentorship Relationship Development")
    
    # Create mentorship relationship
    relationship = dynamics_manager.create_relationship_dynamics(mentor, successor)
    print(f"Initial relationship strength: {relationship.current_strength:.2f}")
    
    # Simulate mentorship interactions over time
    mentorship_interactions = [
        ("mentorship", "progress", "Philosophy lessons"),
        ("mentorship", "success", "Leadership training completed"),
        ("collaboration", "success", "Joint policy decisions"),
        ("wisdom_sharing", "valuable", "Strategic guidance provided")
    ]
    
    for turn, (interaction_type, outcome, description) in enumerate(mentorship_interactions, 100):
        print(f"\nTurn {turn}: {description}")
        relationship = dynamics_manager.evolve_relationship(
            relationship, interaction_type, outcome, turn
        )
        
        # Update successor's reputation based on mentorship success
        if outcome == "success":
            reputation_manager.update_reputation(
                successor,
                ReputationDimension.COMPETENCE,
                0.05,
                f"Mentorship progress: {description}",
                [mentor.id],
                public_awareness=0.3,
                turn=turn
            )
    
    print(f"Final relationship strength: {relationship.current_strength:.2f}")
    print(f"Successor's improved reputation: {reputation_manager._calculate_overall_reputation(successor):.2f}")
    
    print_subsection("Succession Planning Integration")
    
    # Create comprehensive succession plan
    succession_plan = lifecycle_manager.create_succession_plan(
        mentor, [successor], SuccessionType.DIRECT_APPOINTMENT
    )
    
    print(f"Succession Plan:")
    print(f"  Successor Readiness: {succession_plan.readiness_scores.get(successor.id, 0):.2f}")
    print(f"  Knowledge Transfer Required: {len(succession_plan.knowledge_transfer_plan)} skill areas")
    print(f"  Timeline: {succession_plan.timeline} turns")
    
    # Create knowledge transfer plan
    transfer_plan = lifecycle_manager._create_knowledge_transfer_plan(mentor, successor)
    print(f"\nKnowledge Transfer Plan:")
    print(f"  Plan Details: {transfer_plan}")
    if isinstance(transfer_plan, dict):
        print(f"  Skills to Transfer: {list(transfer_plan.keys())}")
    else:
        print(f"  Focus Skills: {transfer_plan.focus_skills}")
        print(f"  Duration: {transfer_plan.estimated_duration} turns")
        print(f"  Success Probability: {transfer_plan.success_probability:.2%}")
    
    print_subsection("Long-term Projection")
    
    # Project future states
    print("Future projections:")
    
    # Mentor aging effects
    aging_effects = lifecycle_manager.apply_aging_effects(mentor, mentor_stage)
    if aging_effects:
        print(f"  Mentor aging effects: {aging_effects}")
    
    # Social influence dynamics
    influence = reputation_manager.calculate_social_influence(mentor, successor, SocialInfluenceType.MENTORSHIP)
    print(f"  Mentor's influence on successor: {influence:.2f}")
    
    # Network position evolution
    successor_position = dynamics_manager.analyze_network_position(successor, [mentor, successor])
    print(f"  Successor's network influence score: {successor_position.get('influence_score', 0):.2f}")


def main():
    """Run the complete Day 3 demonstration."""
    print("🎭 AGENT DEVELOPMENT DAY 3 DEMONSTRATION")
    print("Advanced Lifecycle Management and Social Modeling Systems")
    print(f"{'='*80}")
    
    try:
        # Run all demonstrations
        demo_lifecycle_management()
        demo_reputation_management()
        demo_social_dynamics()
        demo_integrated_systems()
        
        print_section_header("DEMONSTRATION COMPLETE")
        print("✅ All Day 3 systems successfully demonstrated!")
        print("\nKey systems showcased:")
        print("  🔄 Advanced Lifecycle Management with 6 lifecycle stages")
        print("  🌟 Multi-dimensional Reputation System with 8 dimensions") 
        print("  🤝 Complex Social Dynamics with relationship evolution")
        print("  📊 Integrated succession planning and knowledge transfer")
        print("  🎯 Realistic aging effects and retirement modeling")
        print("  📈 Social influence calculations and network analysis")
        
        print("\n🚀 Ready for Task 1.4: Advisor Candidate Selection Algorithm!")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
