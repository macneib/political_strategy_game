#!/usr/bin/env python3
"""
Comprehensive test suite for Agent Development System Day 2 features.

Tests advanced skill development algorithms, achievement systems, and enhanced social modeling.
"""

import pytest
import random
from typing import Dict, List, Optional
from unittest.mock import Mock, patch

# Set up the path to import our modules
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from core.citizen import Citizen, Achievement, AchievementCategory
    from core.technology_tree import TechnologyEra
    from core.advisor import AdvisorRole
    from core.agent_pool import Agent, PersonalityProfile, PerformanceMetrics, SocialNetwork, MentorshipRecord
    from core.agent_development import (
        SkillDevelopmentManager, AchievementManager, EnhancedAchievement,
        SkillDevelopmentType, SkillDevelopmentEvent, LearningModifier,
        AchievementDifficulty, SkillSynergy, SkillSynergyEffect
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Attempting alternative import paths...")
    # Alternative import for different project structures
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from political_strategy_game.src.core.citizen import Citizen, Achievement, AchievementCategory
        from political_strategy_game.src.core.technology_tree import TechnologyEra
        from political_strategy_game.src.core.advisor import AdvisorRole
        from political_strategy_game.src.core.agent_pool import Agent, PersonalityProfile, PerformanceMetrics, SocialNetwork, MentorshipRecord
        from political_strategy_game.src.core.agent_development import (
            SkillDevelopmentManager, AchievementManager, EnhancedAchievement,
            SkillDevelopmentType, SkillDevelopmentEvent, LearningModifier,
            AchievementDifficulty, SkillSynergy, SkillSynergyEffect
        )
    except ImportError as e2:
        print(f"Alternative import also failed: {e2}")
        raise e


def create_test_agent(**kwargs):
    """Helper function to create test agents with default required fields."""
    defaults = {
        "birth_turn": 50,
        "era_born": TechnologyEra.CLASSICAL,
        "civilization_id": "test-civ-001"
    }
    defaults.update(kwargs)
    return Agent(**defaults)


@pytest.fixture
def skill_development_manager():
    """Create a skill development manager for testing."""
    return SkillDevelopmentManager()


@pytest.fixture
def achievement_manager():
    """Create an achievement manager for testing."""
    return AchievementManager()


@pytest.fixture
def sample_agent():
    """Create a sample agent for testing."""
    agent = Agent(
        citizen_id="test-citizen-123",
        name="Test Agent",
        birth_turn=50,
        era_born=TechnologyEra.CLASSICAL,
        civilization_id="test-civ-001",
        age=30,
        skills={
            "leadership": 0.6,
            "combat": 0.4,
            "diplomacy": 0.5,
            "innovation": 0.3
        },
        traits={
            "charisma": 0.7,
            "courage": 0.6,
            "intelligence": 0.8,
            "creativity": 0.5,
            "strategic_thinking": 0.7
        },
        reputation=0.6,
        advisor_potential=0.7
    )
    return agent


@pytest.fixture
def mentor_agent():
    """Create a mentor agent for testing."""
    mentor = Agent(
        citizen_id="mentor-123",
        name="Mentor Agent",
        birth_turn=25,
        era_born=TechnologyEra.CLASSICAL,
        civilization_id="test-civ-001",
        age=45,
        skills={
            "leadership": 0.9,
            "philosophy": 0.8,
            "diplomacy": 0.85
        },
        traits={
            "wisdom": 0.9,
            "empathy": 0.8,
            "patience": 0.7
        },
        reputation=0.9,
        advisor_potential=0.95
    )
    return mentor


class TestSkillDevelopmentManager:
    """Test the SkillDevelopmentManager class."""
    
    def test_initialization(self, skill_development_manager):
        """Test proper initialization of the skill development manager."""
        sdm = skill_development_manager
        
        assert len(sdm.base_learning_rates) > 0
        assert "leadership" in sdm.base_learning_rates
        assert "innovation" in sdm.base_learning_rates
        
        assert len(sdm.era_learning_modifiers) > 0
        assert TechnologyEra.ANCIENT in sdm.era_learning_modifiers
        
        assert len(sdm.skill_synergies) > 0
        assert len(sdm.synergy_matrix) > 0
    
    def test_age_effect_calculation(self, skill_development_manager):
        """Test age effects on learning rates."""
        sdm = skill_development_manager
        
        # Test peak age performance
        peak_effect = sdm._calculate_age_effect(35, "leadership")
        assert 0.9 <= peak_effect <= 1.3
        
        # Test young age
        young_effect = sdm._calculate_age_effect(20, "leadership")
        assert young_effect < peak_effect
        
        # Test old age penalty
        old_effect = sdm._calculate_age_effect(60, "leadership")
        assert old_effect < peak_effect
        
        # Test different skills have different peak ages
        combat_peak = sdm._calculate_age_effect(25, "combat")
        philosophy_peak = sdm._calculate_age_effect(45, "philosophy")
        assert combat_peak != philosophy_peak
    
    def test_trait_effect_calculation(self, skill_development_manager, sample_agent):
        """Test trait effects on skill learning."""
        sdm = skill_development_manager
        
        # Test leadership skill with good traits
        leadership_effect = sdm._calculate_trait_effect(sample_agent, "leadership")
        assert leadership_effect > 1.0  # Should have bonus
        
        # Test skill with no relevant traits
        agriculture_effect = sdm._calculate_trait_effect(sample_agent, "agriculture")
        assert agriculture_effect >= 1.0
    
    def test_synergy_bonus_calculation(self, skill_development_manager, sample_agent):
        """Test skill synergy bonus calculations."""
        sdm = skill_development_manager
        
        # Test leadership with diplomacy synergy
        leadership_synergy = sdm._calculate_synergy_bonus(sample_agent, "leadership")
        assert leadership_synergy > 0.0
        
        # Test skill with no synergies
        agriculture_synergy = sdm._calculate_synergy_bonus(sample_agent, "agriculture")
        assert agriculture_synergy >= 0.0
    
    def test_learning_rate_calculation(self, skill_development_manager, sample_agent):
        """Test comprehensive learning rate calculation."""
        sdm = skill_development_manager
        
        rate, modifiers = sdm.calculate_learning_rate(
            sample_agent, "leadership", TechnologyEra.CLASSICAL, 100
        )
        
        assert 0.001 <= rate <= 0.15
        assert isinstance(modifiers, list)
        
        # Test mentorship learning rate
        mentorship_rate, mentorship_modifiers = sdm.calculate_learning_rate(
            sample_agent, "leadership", TechnologyEra.CLASSICAL, 100,
            SkillDevelopmentType.MENTORSHIP
        )
        
        assert mentorship_rate >= rate  # Should be higher with mentorship
        assert LearningModifier.MENTORSHIP_BOOST in mentorship_modifiers
    
    def test_skill_development(self, skill_development_manager, sample_agent):
        """Test individual skill development."""
        sdm = skill_development_manager
        initial_leadership = sample_agent.skills["leadership"]
        
        event = sdm.develop_skill(
            sample_agent, "leadership", TechnologyEra.CLASSICAL, 100
        )
        
        assert event is not None
        assert event.agent_id == sample_agent.id
        assert event.skill_name == "leadership"
        assert event.new_value > event.old_value
        assert sample_agent.skills["leadership"] > initial_leadership
    
    def test_plateau_mechanics(self, skill_development_manager):
        """Test skill plateau and breakthrough mechanics."""
        sdm = skill_development_manager
        
        # Create agent with high skill
        high_skill_agent = Agent(
            citizen_id="high-skill-123",
            name="High Skill Agent",
            age=30,
            skills={"leadership": 0.85},  # Above plateau threshold
            traits={"charisma": 0.8}
        )
        
        # Test multiple development attempts to see plateau effects
        development_rates = []
        for _ in range(10):
            rate, modifiers = sdm.calculate_learning_rate(
                high_skill_agent, "leadership", TechnologyEra.CLASSICAL, 100
            )
            development_rates.append(rate)
            
            # Check for plateau modifier
            if rate < 0.01:  # Very low rate indicates plateau
                assert LearningModifier.SKILL_PLATEAU in modifiers
    
    def test_turn_development_processing(self, skill_development_manager, sample_agent):
        """Test processing development for an entire turn."""
        sdm = skill_development_manager
        
        events = sdm.process_turn_development(sample_agent, TechnologyEra.CLASSICAL, 100)
        
        assert isinstance(events, list)
        # Should have some development events (probabilistic)
        # Events might be empty due to randomness, but structure should be correct
        for event in events:
            assert isinstance(event, SkillDevelopmentEvent)
            assert event.agent_id == sample_agent.id
    
    def test_mentorship_development(self, skill_development_manager, sample_agent, mentor_agent):
        """Test mentorship-driven skill development."""
        sdm = skill_development_manager
        
        # Add mentorship relationship
        mentorship = MentorshipRecord(
            mentor_id=mentor_agent.id,
            mentee_id=sample_agent.id,
            start_turn=90,
            focus_skills=["leadership", "diplomacy"],
            effectiveness_score=0.8,
            mutual_benefit=True,
            end_turn=None
        )
        sample_agent.social_network.mentorship_relationships.append(mentorship)
        
        # Test mentorship bonus calculation
        bonus = sdm._calculate_mentorship_bonus(sample_agent, "leadership")
        assert bonus > 0.0
        
        # Test development with mentorship
        event = sdm.develop_skill(
            sample_agent, "leadership", TechnologyEra.CLASSICAL, 100,
            SkillDevelopmentType.MENTORSHIP, mentor_agent.id
        )
        
        assert event is not None
        assert event.mentor_id == mentor_agent.id
        assert event.development_type == SkillDevelopmentType.MENTORSHIP


class TestAchievementManager:
    """Test the AchievementManager class."""
    
    def test_initialization(self, achievement_manager):
        """Test proper initialization of achievement manager."""
        am = achievement_manager
        
        assert len(am.achievements) > 0
        assert len(am.achievement_chains) >= 0
        
        # Check that achievements have proper structure
        for achievement_id, achievement in am.achievements.items():
            assert isinstance(achievement, EnhancedAchievement)
            assert achievement.id == achievement_id
            assert achievement.title
            assert achievement.description
    
    def test_achievement_eligibility_basic(self, achievement_manager, sample_agent):
        """Test basic achievement eligibility checking."""
        am = achievement_manager
        
        # Find a simple achievement to test
        simple_achievements = [
            ach for ach in am.achievements.values() 
            if ach.difficulty == AchievementDifficulty.COMMON
        ]
        
        if simple_achievements:
            achievement = simple_achievements[0]
            eligible, failed_requirements = am.check_achievement_eligibility(
                sample_agent, achievement, TechnologyEra.CLASSICAL
            )
            
            assert isinstance(eligible, bool)
            assert isinstance(failed_requirements, list)
    
    def test_skill_requirement_checking(self, achievement_manager):
        """Test skill requirement validation."""
        am = achievement_manager
        
        # Create test achievement with specific skill requirements
        test_achievement = EnhancedAchievement(
            category=AchievementCategory.LEADERSHIP,
            title="Test Achievement",
            description="Test achievement for skill requirements",
            era_granted=TechnologyEra.CLASSICAL,
            turn_granted=100,
            skill_requirements={"leadership": 0.8, "diplomacy": 0.6}
        )
        
        # Test agent that meets requirements
        qualified_agent = Agent(
            citizen_id="qualified-123",
            name="Qualified Agent",
            age=30,
            skills={"leadership": 0.85, "diplomacy": 0.7}
        )
        
        eligible, failed = am.check_achievement_eligibility(
            qualified_agent, test_achievement, TechnologyEra.CLASSICAL
        )
        assert eligible
        assert len(failed) == 0
        
        # Test agent that doesn't meet requirements
        unqualified_agent = Agent(
            citizen_id="unqualified-123",
            name="Unqualified Agent",
            age=30,
            skills={"leadership": 0.5, "diplomacy": 0.4}
        )
        
        eligible, failed = am.check_achievement_eligibility(
            unqualified_agent, test_achievement, TechnologyEra.CLASSICAL
        )
        assert not eligible
        assert len(failed) > 0
    
    def test_trait_requirement_checking(self, achievement_manager):
        """Test trait requirement validation."""
        am = achievement_manager
        
        # Create test achievement with trait requirements
        test_achievement = EnhancedAchievement(
            category=AchievementCategory.LEADERSHIP,
            title="Charismatic Leader",
            description="Natural charismatic leadership",
            era_granted=TechnologyEra.CLASSICAL,
            turn_granted=100,
            trait_requirements={"charisma": 0.7, "empathy": 0.5}
        )
        
        # Test agent with good traits
        charismatic_agent = Agent(
            citizen_id="charismatic-123",
            name="Charismatic Agent",
            age=30,
            traits={"charisma": 0.8, "empathy": 0.6}
        )
        
        eligible, failed = am.check_achievement_eligibility(
            charismatic_agent, test_achievement, TechnologyEra.CLASSICAL
        )
        assert eligible
    
    def test_age_requirement_checking(self, achievement_manager):
        """Test age requirement validation."""
        am = achievement_manager
        
        # Create achievement with age restrictions
        mature_achievement = EnhancedAchievement(
            category=AchievementCategory.SOCIAL,
            title="Elder Wisdom",
            description="Wisdom that comes with age",
            era_granted=TechnologyEra.CLASSICAL,
            turn_granted=100,
            age_requirements=(50, 80)
        )
        
        # Test young agent (should fail)
        young_agent = create_test_agent(citizen_id="young-123", name="Young Agent", age=25)
        eligible, failed = am.check_achievement_eligibility(
            young_agent, mature_achievement, TechnologyEra.CLASSICAL
        )
        assert not eligible
        assert any("Age out of range" in req for req in failed)
        
        # Test appropriate age agent (should pass)
        mature_agent = create_test_agent(citizen_id="mature-123", name="Mature Agent", age=55)
        eligible, failed = am.check_achievement_eligibility(
            mature_agent, mature_achievement, TechnologyEra.CLASSICAL
        )
        assert eligible
    
    def test_achievement_unlocking(self, achievement_manager, sample_agent):
        """Test achievement unlocking process."""
        am = achievement_manager
        
        # Boost agent's skills to make them eligible for more achievements
        sample_agent.skills.update({
            "leadership": 0.9,
            "diplomacy": 0.8,
            "administration": 0.7,
            "philosophy": 0.6
        })
        sample_agent.traits.update({
            "charisma": 0.8,
            "wisdom": 0.7,
            "strategic_thinking": 0.8
        })
        
        initial_achievement_count = len(sample_agent.achievement_history)
        unlocked = am.attempt_achievement_unlock(sample_agent, TechnologyEra.CLASSICAL, 100)
        
        assert isinstance(unlocked, list)
        final_achievement_count = len(sample_agent.achievement_history)
        
        # Should have unlocked some achievements
        assert final_achievement_count >= initial_achievement_count
        assert len(unlocked) == final_achievement_count - initial_achievement_count
    
    def test_achievement_effects_application(self, achievement_manager, sample_agent):
        """Test that achievement effects are properly applied."""
        am = achievement_manager
        
        # Create test achievement with specific effects
        test_achievement = EnhancedAchievement(
            category=AchievementCategory.LEADERSHIP,
            title="Leadership Boost",
            description="Boosts leadership abilities",
            era_granted=TechnologyEra.CLASSICAL,
            turn_granted=100,
            skill_bonuses={"leadership": 0.1, "diplomacy": 0.05},
            reputation_bonus=0.15,
            advisor_potential_bonus=0.2
        )
        
        initial_leadership = sample_agent.skills.get("leadership", 0.0)
        initial_reputation = sample_agent.reputation
        initial_advisor_potential = sample_agent.advisor_potential
        
        am._apply_achievement_effects(sample_agent, test_achievement)
        
        # Check that effects were applied
        assert sample_agent.skills["leadership"] == initial_leadership + 0.1
        assert sample_agent.skills.get("diplomacy", 0.0) >= 0.05
        assert sample_agent.reputation == initial_reputation + 0.15
        assert sample_agent.advisor_potential == initial_advisor_potential + 0.2
    
    def test_achievement_rarity_calculation(self, achievement_manager):
        """Test achievement rarity calculations."""
        am = achievement_manager
        
        # Mock some unlock statistics
        test_achievement_id = list(am.achievements.keys())[0]
        am.unlock_statistics[test_achievement_id] = 10
        
        rarity = am.calculate_achievement_rarity(test_achievement_id, 100)
        assert 0.0 <= rarity <= 1.0
        assert rarity == 0.9  # 10 out of 100 unlocked it
        
        # Test with no unlocks
        new_achievement_id = "never-unlocked"
        rarity = am.calculate_achievement_rarity(new_achievement_id, 100)
        assert rarity == 1.0  # Most rare


class TestSkillSynergies:
    """Test skill synergy systems."""
    
    def test_synergy_effect_creation(self):
        """Test creation of skill synergy effects."""
        synergy = SkillSynergyEffect(
            primary_skill="leadership",
            supporting_skills=["diplomacy", "administration"],
            synergy_type=SkillSynergy.COMPLEMENTARY,
            synergy_strength=0.8,
            development_bonus=0.15,
            efficiency_multiplier=1.2
        )
        
        assert synergy.primary_skill == "leadership"
        assert "diplomacy" in synergy.supporting_skills
        assert synergy.synergy_type == SkillSynergy.COMPLEMENTARY
        assert synergy.development_bonus == 0.15
    
    def test_synergy_matrix_building(self, skill_development_manager):
        """Test that synergy matrix is properly built."""
        sdm = skill_development_manager
        
        assert len(sdm.synergy_matrix) > 0
        
        # Check specific synergies exist
        if "leadership" in sdm.synergy_matrix:
            leadership_synergies = sdm.synergy_matrix["leadership"]
            assert len(leadership_synergies) > 0
    
    def test_synergy_bonus_application(self, skill_development_manager):
        """Test that synergy bonuses are properly calculated."""
        sdm = skill_development_manager
        
        # Create agent with complementary skills
        synergy_agent = Agent(
            citizen_id="synergy-123",
            name="Synergy Agent",
            age=30,
            skills={
                "leadership": 0.6,
                "diplomacy": 0.7,
                "administration": 0.5,
                "philosophy": 0.4
            }
        )
        
        bonus = sdm._calculate_synergy_bonus(synergy_agent, "leadership")
        assert bonus >= 0.0
        assert bonus <= 0.5  # Should be capped


class TestDevelopmentTypes:
    """Test different skill development types."""
    
    def test_development_type_modifiers(self, skill_development_manager):
        """Test that different development types have different modifiers."""
        sdm = skill_development_manager
        
        natural_mod = sdm._get_development_type_modifier(SkillDevelopmentType.NATURAL_LEARNING)
        mentorship_mod = sdm._get_development_type_modifier(SkillDevelopmentType.MENTORSHIP)
        crisis_mod = sdm._get_development_type_modifier(SkillDevelopmentType.CRISIS_ACCELERATED)
        
        assert natural_mod == 1.0
        assert mentorship_mod > natural_mod
        assert crisis_mod > natural_mod
        assert crisis_mod > mentorship_mod
    
    def test_experience_based_development(self, skill_development_manager, sample_agent):
        """Test experience-based skill development."""
        sdm = skill_development_manager
        
        event = sdm.develop_skill(
            sample_agent, "combat", TechnologyEra.MEDIEVAL, 100,
            SkillDevelopmentType.EXPERIENCE_BASED
        )
        
        assert event is not None
        assert event.development_type == SkillDevelopmentType.EXPERIENCE_BASED
    
    def test_crisis_accelerated_development(self, skill_development_manager, sample_agent):
        """Test crisis-accelerated development."""
        sdm = skill_development_manager
        
        initial_leadership = sample_agent.skills["leadership"]
        
        event = sdm.develop_skill(
            sample_agent, "leadership", TechnologyEra.MEDIEVAL, 100,
            SkillDevelopmentType.CRISIS_ACCELERATED
        )
        
        assert event is not None
        assert event.development_type == SkillDevelopmentType.CRISIS_ACCELERATED
        # Crisis development should provide significant growth
        assert (event.new_value - event.old_value) > 0.0


class TestIntegrationScenarios:
    """Test integrated scenarios combining multiple systems."""
    
    def test_mentor_protege_development_cycle(self, skill_development_manager, achievement_manager, mentor_agent):
        """Test a full mentor-protégé development cycle."""
        sdm = skill_development_manager
        am = achievement_manager
        
        # Create protégé
        protege = Agent(
            citizen_id="protege-123",
            name="Eager Student",
            age=25,
            skills={"leadership": 0.3, "diplomacy": 0.2},
            traits={"curiosity": 0.8, "determination": 0.7}
        )
        
        # Establish mentorship
        mentorship = MentorshipRecord(
            mentor_id=mentor_agent.id,
            mentee_id=protege.id,
            start_turn=100,
            focus_skills=["leadership", "diplomacy"],
            effectiveness_score=0.85,
            mutual_benefit=True,
            end_turn=None
        )
        protege.social_network.mentorship_relationships.append(mentorship)
        
        # Simulate development over multiple turns
        for turn in range(100, 150):
            # Develop skills through mentorship
            leadership_event = sdm.develop_skill(
                protege, "leadership", TechnologyEra.CLASSICAL, turn,
                SkillDevelopmentType.MENTORSHIP, mentor_agent.id
            )
            
            diplomacy_event = sdm.develop_skill(
                protege, "diplomacy", TechnologyEra.CLASSICAL, turn,
                SkillDevelopmentType.MENTORSHIP, mentor_agent.id
            )
            
            # Check for achievement unlocks
            unlocked = am.attempt_achievement_unlock(protege, TechnologyEra.CLASSICAL, turn)
            
            if unlocked:
                print(f"Turn {turn}: Unlocked {len(unlocked)} achievements")
        
        # Verify growth occurred
        assert protege.skills["leadership"] > 0.3
        assert protege.skills["diplomacy"] > 0.2
    
    def test_skill_plateau_breakthrough_scenario(self, skill_development_manager):
        """Test the plateau and breakthrough system."""
        sdm = skill_development_manager
        
        # Create agent with high skills near plateau
        expert_agent = Agent(
            citizen_id="expert-123",
            name="Expert Agent",
            age=40,
            skills={"innovation": 0.78},  # Near plateau threshold
            traits={"creativity": 0.9, "persistence": 0.8}
        )
        
        breakthrough_occurred = False
        plateau_detected = False
        
        # Simulate many development attempts
        for turn in range(200, 250):
            rate, modifiers = sdm.calculate_learning_rate(
                expert_agent, "innovation", TechnologyEra.INDUSTRIAL, turn
            )
            
            if LearningModifier.SKILL_PLATEAU in modifiers:
                plateau_detected = True
            
            if LearningModifier.BREAKTHROUGH in modifiers:
                breakthrough_occurred = True
                break
            
            # Attempt development
            event = sdm.develop_skill(
                expert_agent, "innovation", TechnologyEra.INDUSTRIAL, turn
            )
        
        assert plateau_detected  # Should hit plateau with high skill
        # Breakthrough is probabilistic, so we can't guarantee it
    
    def test_multi_skill_synergy_development(self, skill_development_manager):
        """Test development with multiple skill synergies."""
        sdm = skill_development_manager
        
        # Create agent with multiple skills that have synergies
        renaissance_agent = Agent(
            citizen_id="renaissance-123",
            name="Renaissance Agent",
            age=35,
            skills={
                "arts": 0.5,
                "science": 0.4,
                "engineering": 0.3,
                "philosophy": 0.4,
                "innovation": 0.2
            },
            traits={"creativity": 0.9, "curiosity": 0.8, "intelligence": 0.7}
        )
        
        # Develop innovation skill (which should benefit from synergies)
        initial_innovation = renaissance_agent.skills["innovation"]
        
        for turn in range(300, 320):
            event = sdm.develop_skill(
                renaissance_agent, "innovation", TechnologyEra.RENAISSANCE, turn
            )
        
        final_innovation = renaissance_agent.skills["innovation"]
        
        # Should show growth enhanced by synergies
        assert final_innovation > initial_innovation
        
        # Check synergy bonus calculation
        synergy_bonus = sdm._calculate_synergy_bonus(renaissance_agent, "innovation")
        assert synergy_bonus > 0.0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
