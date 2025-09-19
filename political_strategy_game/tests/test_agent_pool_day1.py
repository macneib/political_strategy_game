#!/usr/bin/env python3
"""
Comprehensive test suite for Agent Pool Management System (Task 1.3 Day 1)

Tests the enhanced Agent class, AgentPoolManager, and all associated
personality, performance, and lifecycle tracking systems.
"""

import pytest
import random
from typing import List, Dict
from unittest.mock import Mock, patch

# Import the modules we're testing
from src.core.agent_pool import (
    Agent, AgentPoolManager, PersonalityProfile, PerformanceMetrics,
    AchievementRecord, NarrativeEvent, EnhancedRelationship, SocialNetwork,
    TraitChange, PerformanceSnapshot, MentorshipRecord, FactionAffiliation,
    TraitChangeType, EventType, PerformanceTrend, PromotionCriteria, DemotionCriteria,
    create_agent_pool_manager
)
from src.core.citizen import Citizen, CitizenGenerator, Achievement, AchievementCategory
from src.core.technology_tree import TechnologyEra
from src.core.advisor import AdvisorRole


class TestPersonalityProfile:
    """Test the PersonalityProfile system."""
    
    def test_personality_profile_creation(self):
        """Test creating a basic personality profile."""
        profile = PersonalityProfile(
            core_traits={"leadership": 0.8, "creativity": 0.6, "analytical_thinking": 0.7},
            personality_drift_rate=0.03,
            dominant_traits=["leadership", "analytical_thinking", "creativity"]
        )
        
        assert profile.core_traits["leadership"] == 0.8
        assert profile.personality_drift_rate == 0.03
        assert len(profile.dominant_traits) == 3
        assert profile.personality_stability >= 0.0
        assert profile.decision_making_style == "balanced"
    
    def test_trait_development_history(self):
        """Test trait change tracking."""
        profile = PersonalityProfile()
        
        trait_change = TraitChange(
            turn=10,
            trait_name="leadership",
            old_value=0.5,
            new_value=0.6,
            change_type=TraitChangeType.EXPERIENCE_BASED,
            cause="Successful project leadership",
            impact_magnitude=0.1
        )
        
        profile.trait_development_history.append(trait_change)
        
        assert len(profile.trait_development_history) == 1
        assert profile.trait_development_history[0].trait_name == "leadership"
        assert profile.trait_development_history[0].change_type == TraitChangeType.EXPERIENCE_BASED


class TestPerformanceMetrics:
    """Test the PerformanceMetrics system."""
    
    def test_performance_metrics_initialization(self):
        """Test creating performance metrics."""
        metrics = PerformanceMetrics(
            achievement_rate=0.05,
            leadership_emergence_score=0.7,
            advisor_readiness_score=0.6
        )
        
        assert metrics.achievement_rate == 0.05
        assert metrics.leadership_emergence_score == 0.7
        assert metrics.advisor_readiness_score == 0.6
        assert metrics.peak_composite_score == 0.0
        assert len(metrics.performance_trend) == 0
    
    def test_performance_snapshot(self):
        """Test performance snapshot creation."""
        snapshot = PerformanceSnapshot(
            turn=15,
            composite_score=0.75,
            skill_scores={"leadership": 0.8, "diplomacy": 0.7},
            achievement_count=5,
            reputation=0.7,
            social_influence=0.6,
            trend=PerformanceTrend.RISING
        )
        
        assert snapshot.turn == 15
        assert snapshot.composite_score == 0.75
        assert snapshot.trend == PerformanceTrend.RISING
        assert len(snapshot.skill_scores) == 2
    
    def test_skill_plateau_detection(self):
        """Test skill plateau detection system."""
        metrics = PerformanceMetrics()
        metrics.skill_plateau_detection = {
            "leadership": True,
            "diplomacy": False,
            "combat": False
        }
        
        assert metrics.skill_plateau_detection["leadership"] is True
        assert metrics.skill_plateau_detection["diplomacy"] is False


class TestEnhancedRelationship:
    """Test the enhanced relationship system."""
    
    def test_relationship_creation(self):
        """Test creating enhanced relationships."""
        relationship = EnhancedRelationship(
            other_agent_id="agent_123",
            relationship_type="mentor",
            strength=0.8,
            trust_level=0.9,
            loyalty=0.7,
            compatibility=0.8
        )
        
        assert relationship.other_agent_id == "agent_123"
        assert relationship.relationship_type == "mentor"
        assert relationship.strength == 0.8
        assert relationship.trust_level == 0.9
        assert relationship.interaction_frequency == 0.1  # Default value
    
    def test_relationship_development_tracking(self):
        """Test relationship history tracking."""
        relationship = EnhancedRelationship(
            other_agent_id="agent_456",
            relationship_type="colleague",
            strength=0.5
        )
        
        # Add relationship history
        relationship.relationship_history.append((10, 0.5))
        relationship.relationship_history.append((20, 0.6))
        relationship.relationship_history.append((30, 0.7))
        
        assert len(relationship.relationship_history) == 3
        assert relationship.relationship_history[-1] == (30, 0.7)


class TestSocialNetwork:
    """Test the social network system."""
    
    def test_social_network_creation(self):
        """Test creating a social network."""
        network = SocialNetwork(
            relationship_capacity=25,
            social_influence_score=0.6,
            network_centrality=0.4
        )
        
        assert network.relationship_capacity == 25
        assert network.social_influence_score == 0.6
        assert network.network_centrality == 0.4
        assert len(network.relationships) == 0
        assert len(network.mentorship_relationships) == 0
    
    def test_mentorship_relationships(self):
        """Test mentorship relationship tracking."""
        network = SocialNetwork()
        
        mentorship = MentorshipRecord(
            mentor_id="mentor_123",
            mentee_id="mentee_456",
            start_turn=15,
            end_turn=None,
            focus_skills=["leadership", "diplomacy"],
            effectiveness_score=0.8,
            mutual_benefit=True
        )
        
        network.mentorship_relationships.append(mentorship)
        
        assert len(network.mentorship_relationships) == 1
        assert network.mentorship_relationships[0].mentor_id == "mentor_123"
        assert network.mentorship_relationships[0].mutual_benefit is True
    
    def test_faction_affiliations(self):
        """Test faction affiliation tracking."""
        network = SocialNetwork()
        
        affiliation = FactionAffiliation(
            faction_id="faction_001",
            faction_name="Progressive Alliance",
            affiliation_strength=0.7,
            join_turn=25,
            role_in_faction="strategic_advisor",
            influence_level=0.6
        )
        
        network.factional_affiliations.append(affiliation)
        
        assert len(network.factional_affiliations) == 1
        assert network.factional_affiliations[0].faction_name == "Progressive Alliance"
        assert network.factional_affiliations[0].role_in_faction == "strategic_advisor"


class TestNarrativeEvent:
    """Test the narrative event system."""
    
    def test_narrative_event_creation(self):
        """Test creating narrative events."""
        event = NarrativeEvent(
            turn=42,
            event_type=EventType.ACHIEVEMENT_UNLOCK,
            title="Master Diplomat Achievement",
            description="Agent successfully negotiated complex trade agreement",
            primary_agent_id="agent_789",
            impact_on_reputation=0.15,
            narrative_weight=0.8
        )
        
        assert event.turn == 42
        assert event.event_type == EventType.ACHIEVEMENT_UNLOCK
        assert event.title == "Master Diplomat Achievement"
        assert event.impact_on_reputation == 0.15
        assert event.narrative_weight == 0.8
        assert event.story_importance == "minor"  # Default value
    
    def test_event_with_effects(self):
        """Test events with multiple effect types."""
        event = NarrativeEvent(
            turn=55,
            event_type=EventType.LEADERSHIP_EMERGENCE,
            title="Crisis Leadership Demonstrated",
            description="Agent took charge during economic crisis",
            primary_agent_id="agent_999",
            skill_development_effects={"leadership": 0.1, "administration": 0.05},
            trait_development_effects={"decisiveness": 0.08, "stress_resistance": 0.06},
            relationship_effects={"agent_111": 0.1, "agent_222": 0.05}
        )
        
        assert len(event.skill_development_effects) == 2
        assert len(event.trait_development_effects) == 2
        assert len(event.relationship_effects) == 2
        assert event.skill_development_effects["leadership"] == 0.1


class TestAgent:
    """Test the enhanced Agent class."""
    
    @pytest.fixture
    def sample_citizen(self):
        """Create a sample citizen for testing."""
        generator = CitizenGenerator()
        citizen = generator.generate_citizen(
            era=TechnologyEra.CLASSICAL,
            turn=1,
            civilization_id="test_civ"
        )
        citizen.age = 35
        citizen.name = "Test Citizen"
        citizen.skills = {
            "leadership": 0.8,
            "diplomacy": 0.7,
            "administration": 0.6,
            "combat": 0.5
        }
        citizen.reputation = 0.7
        citizen.advisor_potential = 0.75
        return citizen
    
    def test_agent_creation_from_citizen(self, sample_citizen):
        """Test creating an agent from a citizen."""
        agent = Agent(**sample_citizen.model_dump())
        
        assert agent.name == sample_citizen.name
        assert agent.age == sample_citizen.age
        assert agent.skills == sample_citizen.skills
        assert agent.reputation == sample_citizen.reputation
        assert isinstance(agent.personality_profile, PersonalityProfile)
        assert isinstance(agent.performance_metrics, PerformanceMetrics)
        assert isinstance(agent.social_network, SocialNetwork)
    
    def test_composite_score_calculation(self, sample_citizen):
        """Test composite score calculation."""
        agent = Agent(**sample_citizen.model_dump())
        
        composite_score = agent.calculate_composite_score()
        
        assert 0.0 <= composite_score <= 1.0
        assert composite_score > 0.6  # Should be high for our test citizen
    
    def test_advisor_candidacy_score_update(self, sample_citizen):
        """Test advisor candidacy score updates."""
        agent = Agent(**sample_citizen.model_dump())
        
        candidacy_score = agent.update_advisor_candidacy_score(TechnologyEra.CLASSICAL)
        
        assert 0.0 <= candidacy_score <= 1.0
        assert agent.advisor_candidacy_score == candidacy_score
    
    def test_specialization_strength(self, sample_citizen):
        """Test specialization strength calculation."""
        agent = Agent(**sample_citizen.model_dump())
        agent.specialization_progress = {
            "military_leadership": 0.7,
            "diplomatic_relations": 0.8
        }
        
        military_strength = agent.get_specialization_strength("military_leadership")
        diplomatic_strength = agent.get_specialization_strength("diplomatic_relations")
        unknown_strength = agent.get_specialization_strength("unknown_spec")
        
        assert 0.0 <= military_strength <= 1.0
        assert 0.0 <= diplomatic_strength <= 1.0
        assert unknown_strength == 0.0
        assert diplomatic_strength > 0.5  # Should be relatively high
    
    def test_agent_lifecycle_tracking(self, sample_citizen):
        """Test agent lifecycle and tenure tracking."""
        agent = Agent(**sample_citizen.model_dump())
        agent.promotion_turn = 10
        agent.pool_tenure = 25
        agent.peak_performance_period = (20, 35)
        
        assert agent.promotion_turn == 10
        assert agent.pool_tenure == 25
        assert agent.peak_performance_period == (20, 35)
        assert agent.performance_decline_started is None
        assert agent.retirement_probability == 0.0


class TestPromotionCriteria:
    """Test promotion criteria evaluation."""
    
    def test_promotion_criteria_defaults(self):
        """Test default promotion criteria."""
        criteria = PromotionCriteria()
        
        assert criteria.min_composite_score == 0.7
        assert criteria.min_skill_count == 3
        assert criteria.min_reputation == 0.6
        assert criteria.age_preference_range == (25, 55)
        assert criteria.achievement_weight == 0.3
    
    def test_custom_promotion_criteria(self):
        """Test custom promotion criteria."""
        criteria = PromotionCriteria(
            min_composite_score=0.8,
            min_skill_count=4,
            min_reputation=0.7,
            age_preference_range=(30, 50)
        )
        
        assert criteria.min_composite_score == 0.8
        assert criteria.min_skill_count == 4
        assert criteria.min_reputation == 0.7
        assert criteria.age_preference_range == (30, 50)


class TestDemotionCriteria:
    """Test demotion criteria evaluation."""
    
    def test_demotion_criteria_defaults(self):
        """Test default demotion criteria."""
        criteria = DemotionCriteria()
        
        assert criteria.performance_decline_threshold == 0.2
        assert criteria.inactivity_turns == 50
        assert criteria.age_retirement_threshold == 65
        assert criteria.min_pool_performance_percentile == 0.4
        assert criteria.narrative_consistency_weight == 0.3


class TestAgentPoolManager:
    """Test the agent pool management system."""
    
    @pytest.fixture
    def pool_manager(self):
        """Create a pool manager for testing."""
        return AgentPoolManager(pool_size_target=50, min_pool_size=25, max_pool_size=100)
    
    @pytest.fixture
    def sample_citizens(self):
        """Create sample citizens for testing."""
        generator = CitizenGenerator()
        citizens = []
        
        for i in range(20):
            citizen = generator.generate_citizen(
                era=TechnologyEra.CLASSICAL,
                turn=1,
                civilization_id="test_civ"
            )
            citizen.age = random.randint(25, 55)
            citizen.name = f"Test Citizen {i}"
            
            # Give varying skill levels
            citizen.skills = {
                "leadership": random.uniform(0.3, 0.9),
                "diplomacy": random.uniform(0.3, 0.9),
                "administration": random.uniform(0.3, 0.9),
                "combat": random.uniform(0.3, 0.9)
            }
            citizen.reputation = random.uniform(0.4, 0.9)
            citizen.advisor_potential = random.uniform(0.4, 0.9)
            citizens.append(citizen)
        
        return citizens
    
    def test_pool_manager_initialization(self, pool_manager):
        """Test pool manager initialization."""
        assert pool_manager.pool_size_target == 50
        assert pool_manager.min_pool_size == 25
        assert pool_manager.max_pool_size == 100
        assert len(pool_manager.agent_pool) == 0
        assert isinstance(pool_manager.promotion_criteria, PromotionCriteria)
        assert isinstance(pool_manager.demotion_criteria, DemotionCriteria)
    
    def test_promotion_candidate_evaluation(self, pool_manager, sample_citizens):
        """Test evaluating promotion candidates."""
        # Set high skills for some citizens to make them eligible
        for i in range(5):
            sample_citizens[i].skills = {
                "leadership": 0.8,
                "diplomacy": 0.7,
                "administration": 0.75,
                "combat": 0.6
            }
            sample_citizens[i].reputation = 0.7
        
        candidates = pool_manager.evaluate_promotion_candidates(sample_citizens, turn=1)
        
        assert len(candidates) >= 0
        assert len(candidates) <= pool_manager.pool_size_target // 4
        
        # Candidates should be sorted by promotion score
        if len(candidates) > 1:
            scores = [pool_manager._calculate_promotion_score(c) for c in candidates]
            assert scores == sorted(scores, reverse=True)
    
    def test_agent_promotion_process(self, pool_manager, sample_citizens):
        """Test promoting a citizen to agent pool."""
        # Prepare a high-quality citizen
        citizen = sample_citizens[0]
        citizen.skills = {
            "leadership": 0.85,
            "diplomacy": 0.8,
            "administration": 0.75,
            "combat": 0.7
        }
        citizen.reputation = 0.8
        citizen.advisor_potential = 0.85
        
        # Promote citizen
        agent = pool_manager.promote_to_agent_pool(citizen, turn=10)
        
        assert isinstance(agent, Agent)
        assert agent.name == citizen.name
        assert agent.promotion_turn == 10
        assert agent.pool_tenure == 0
        assert len(pool_manager.agent_pool) == 1
        assert len(agent.narrative_history) >= 1
        assert agent.narrative_history[0].event_type == EventType.PROMOTION
    
    def test_agent_demotion_process(self, pool_manager):
        """Test demoting an agent from pool."""
        # Create a mock agent for demotion
        generator = CitizenGenerator()
        base_citizen = generator.generate_citizen(TechnologyEra.CLASSICAL, 1, "test_civ")
        base_citizen.age = 35
        base_citizen.name = "Test Agent"
        
        agent = Agent(**base_citizen.model_dump())
        agent.age = 70  # Above retirement threshold
        agent.promotion_turn = 1
        agent.pool_tenure = 100
        
        pool_manager.agent_pool.append(agent)
        
        # Demote agent
        citizen = pool_manager.demote_from_agent_pool(agent, turn=101, reason="age_retirement")
        
        assert isinstance(citizen, Citizen)
        assert citizen.name == agent.name
        assert len(pool_manager.agent_pool) == 0
        assert len(agent.narrative_history) >= 1
    
    def test_promotion_criteria_evaluation(self, pool_manager):
        """Test promotion criteria evaluation."""
        generator = CitizenGenerator()
        
        # Create citizens with different characteristics
        good_citizen = generator.generate_citizen(TechnologyEra.CLASSICAL, 1, "test_civ")
        good_citizen.age = 35
        good_citizen.name = "Good Citizen"
        good_citizen.skills = {
            "leadership": 0.8,
            "diplomacy": 0.75,
            "administration": 0.7,
            "combat": 0.6
        }
        good_citizen.reputation = 0.75
        
        poor_citizen = generator.generate_citizen(TechnologyEra.CLASSICAL, 1, "test_civ")
        poor_citizen.age = 30
        poor_citizen.name = "Poor Citizen"
        poor_citizen.skills = {
            "leadership": 0.3,
            "diplomacy": 0.4
        }
        poor_citizen.reputation = 0.4
        
        old_citizen = generator.generate_citizen(TechnologyEra.CLASSICAL, 1, "test_civ")
        old_citizen.age = 70
        old_citizen.name = "Old Citizen"
        old_citizen.skills = {
            "leadership": 0.8,
            "diplomacy": 0.7,
            "administration": 0.75
        }
        old_citizen.reputation = 0.8
        
        assert pool_manager._meets_promotion_criteria(good_citizen, 10) is True
        assert pool_manager._meets_promotion_criteria(poor_citizen, 10) is False
        assert pool_manager._meets_promotion_criteria(old_citizen, 10) is False  # Too old
    
    def test_demotion_criteria_evaluation(self, pool_manager):
        """Test demotion criteria evaluation."""
        generator = CitizenGenerator()
        base_citizen = generator.generate_citizen(TechnologyEra.CLASSICAL, 1, "test_civ")
        base_citizen.age = 40
        base_citizen.name = "Test Agent"
        
        # Test age retirement
        old_agent = Agent(**base_citizen.model_dump())
        old_agent.age = 70
        assert pool_manager._meets_demotion_criteria(old_agent, 100) is True
        
        # Test performance decline
        declining_agent = Agent(**base_citizen.model_dump())
        declining_agent.performance_metrics.peak_composite_score = 0.8
        declining_agent.skills = {"leadership": 0.3, "diplomacy": 0.3}  # Low current performance
        assert pool_manager._meets_demotion_criteria(declining_agent, 100) is True
        
        # Test good agent (should not be demoted)
        good_agent = Agent(**base_citizen.model_dump())
        good_agent.age = 45
        good_agent.skills = {"leadership": 0.8, "diplomacy": 0.7}
        assert pool_manager._meets_demotion_criteria(good_agent, 100) is False
    
    def test_pool_update_process(self, pool_manager, sample_citizens):
        """Test complete pool update process."""
        # Prepare some high-quality citizens for promotion
        for i in range(3):
            sample_citizens[i].skills = {
                "leadership": 0.8,
                "diplomacy": 0.75,
                "administration": 0.7,
                "combat": 0.6
            }
            sample_citizens[i].reputation = 0.75
        
        results = pool_manager.update_agent_pool(turn=1, available_citizens=sample_citizens)
        
        assert "promoted" in results
        assert "demoted" in results
        assert "pool_size" in results
        assert len(results["promoted"]) >= 0
        assert results["pool_size"] == len(pool_manager.agent_pool)
    
    def test_top_performers_retrieval(self, pool_manager):
        """Test retrieving top performers from pool."""
        # Add some agents with varying performance
        generator = CitizenGenerator()
        
        for i in range(10):
            citizen = generator.generate_citizen(TechnologyEra.CLASSICAL, 1, "test_civ")
            citizen.age = 35
            citizen.name = f"Agent {i}"
            citizen.skills = {
                "leadership": 0.5 + i * 0.05,  # Varying skill levels
                "diplomacy": 0.5 + i * 0.04,
                "administration": 0.5 + i * 0.03
            }
            agent = Agent(**citizen.model_dump())
            pool_manager.agent_pool.append(agent)
        
        top_performers = pool_manager.get_top_performers(count=5)
        
        assert len(top_performers) == 5
        
        # Should be sorted by composite score (highest first)
        scores = [agent.calculate_composite_score() for agent in top_performers]
        assert scores == sorted(scores, reverse=True)
    
    def test_specialization_filtering(self, pool_manager):
        """Test filtering agents by specialization."""
        generator = CitizenGenerator()
        
        # Create agents with different specializations
        for i, spec in enumerate(["military_leadership", "diplomatic_relations", "economic_management"]):
            citizen = generator.generate_citizen(TechnologyEra.CLASSICAL, 1, "test_civ")
            citizen.age = 35
            citizen.name = f"Agent {i}"
            agent = Agent(**citizen.model_dump())
            agent.specialization_paths = [spec]
            pool_manager.agent_pool.append(agent)
        
        military_agents = pool_manager.get_agents_by_specialization("military_leadership")
        diplomatic_agents = pool_manager.get_agents_by_specialization("diplomatic_relations")
        
        assert len(military_agents) == 1
        assert len(diplomatic_agents) == 1
        assert military_agents[0].specialization_paths[0] == "military_leadership"
        assert diplomatic_agents[0].specialization_paths[0] == "diplomatic_relations"
    
    def test_pool_statistics_tracking(self, pool_manager):
        """Test pool statistics tracking."""
        initial_stats = pool_manager.pool_statistics.copy()
        
        assert initial_stats["total_promotions"] == 0
        assert initial_stats["total_demotions"] == 0
        assert initial_stats["average_tenure"] == 0.0
        
        # Add some agents and update statistics
        generator = CitizenGenerator()
        for i in range(3):
            citizen = generator.generate_citizen(TechnologyEra.CLASSICAL, 1, "test_civ")
            citizen.age = 35
            citizen.name = f"Agent {i}"
            pool_manager.promote_to_agent_pool(citizen, turn=1)
        
        pool_manager._update_pool_statistics(turn=10)
        
        assert pool_manager.pool_statistics["total_promotions"] == 3
        assert "top_performers" in pool_manager.pool_statistics
        assert "specialization_distribution" in pool_manager.pool_statistics


class TestAgentPoolFactory:
    """Test the agent pool factory functions."""
    
    def test_create_agent_pool_manager(self):
        """Test factory function for creating agent pool manager."""
        manager = create_agent_pool_manager(pool_size_target=75)
        
        assert isinstance(manager, AgentPoolManager)
        assert manager.pool_size_target == 75
        assert manager.min_pool_size == 50  # Default
        assert manager.max_pool_size == 500  # Default


class TestIntegrationScenarios:
    """Test integration scenarios for the complete system."""
    
    def test_complete_agent_lifecycle(self):
        """Test complete agent lifecycle from promotion to potential demotion."""
        pool_manager = AgentPoolManager(pool_size_target=20)
        generator = CitizenGenerator()
        
        # Create high-quality citizen
        citizen = generator.generate_citizen(TechnologyEra.CLASSICAL, 1, "test_civ")
        citizen.age = 30
        citizen.name = "Lifecycle Test"
        citizen.skills = {
            "leadership": 0.8,
            "diplomacy": 0.75,
            "administration": 0.7,
            "combat": 0.65
        }
        citizen.reputation = 0.8
        citizen.advisor_potential = 0.85
        
        # Step 1: Promotion
        agent = pool_manager.promote_to_agent_pool(citizen, turn=1)
        assert len(pool_manager.agent_pool) == 1
        assert isinstance(agent, Agent)
        
        # Step 2: Development tracking over time
        for turn in range(2, 52):  # 50 turns of development
            agent.pool_tenure = turn - 1
            
            # Simulate some development
            if turn % 10 == 0:
                # Add achievement every 10 turns
                achievement = Achievement(
                    category=AchievementCategory.LEADERSHIP,
                    title=f"Achievement at turn {turn}",
                    description="Test achievement",
                    impact_on_advisor_potential=0.1,
                    era_granted=TechnologyEra.CLASSICAL,
                    turn_granted=turn,
                    prerequisites=[],
                    rarity=0.5
                )
                agent.achievement_history.append(AchievementRecord(
                    achievement=achievement,
                    unlock_turn=turn,
                    unlock_circumstances="Test scenario"
                ))
        
        # Step 3: Check agent development
        assert agent.pool_tenure == 50
        assert len(agent.achievement_history) == 5  # One every 10 turns
        
        # Step 4: Test potential demotion (age agent)
        agent.age = 70  # Age beyond retirement threshold
        demotion_candidates = pool_manager.evaluate_demotion_candidates(turn=52)
        
        assert len(demotion_candidates) == 1
        assert demotion_candidates[0].id == agent.id
        
        # Step 5: Actual demotion
        citizen_result = pool_manager.demote_from_agent_pool(agent, turn=52, reason="age_retirement")
        
        assert isinstance(citizen_result, Citizen)
        assert len(pool_manager.agent_pool) == 0
        assert pool_manager.pool_statistics["total_demotions"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
