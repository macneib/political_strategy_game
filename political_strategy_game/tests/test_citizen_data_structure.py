#!/usr/bin/env python3
"""
Tests for the Citizen Data Structure implementation.
"""

import pytest
from typing import Set
from src.core.citizen import (
    Citizen, CitizenGenerator, Achievement, SocialRelationship,
    AchievementCategory, RelationshipType, SkillCategory, TraitCategory,
    get_era_achievements, create_citizen_generator
)
from src.core.technology_tree import TechnologyEra
from src.core.advisor import AdvisorRole


class TestCitizenDataStructure:
    """Test the core citizen data structure."""
    
    def test_citizen_creation(self):
        """Test basic citizen creation."""
        citizen = Citizen(
            name="Test Citizen",
            birth_turn=1,
            era_born=TechnologyEra.ANCIENT,
            civilization_id="test_civ"
        )
        
        assert citizen.name == "Test Citizen"
        assert citizen.birth_turn == 1
        assert citizen.era_born == TechnologyEra.ANCIENT
        assert citizen.civilization_id == "test_civ"
        assert citizen.is_alive is True
        assert citizen.age == 0
        assert citizen.advisor_potential == 0.0
        assert len(citizen.skills) == 0
        assert len(citizen.traits) == 0
        assert len(citizen.achievements) == 0
    
    def test_citizen_skills_validation(self):
        """Test skill validation."""
        citizen = Citizen(
            name="Skilled Citizen",
            birth_turn=1,
            era_born=TechnologyEra.CLASSICAL,
            civilization_id="test_civ",
            skills={"combat": 0.8, "leadership": 0.6, "crafting": 0.9}
        )
        
        assert citizen.skills["combat"] == 0.8
        assert citizen.skills["leadership"] == 0.6
        assert citizen.skills["crafting"] == 0.9
    
    def test_citizen_traits_validation(self):
        """Test trait validation."""
        citizen = Citizen(
            name="Trait Citizen", 
            birth_turn=1,
            era_born=TechnologyEra.MEDIEVAL,
            civilization_id="test_civ",
            traits={"courage": 0.8, "wisdom": -0.2, "charisma": 0.5}
        )
        
        assert citizen.traits["courage"] == 0.8
        assert citizen.traits["wisdom"] == -0.2
        assert citizen.traits["charisma"] == 0.5


class TestAchievement:
    """Test achievement system."""
    
    def test_achievement_creation(self):
        """Test achievement creation."""
        achievement = Achievement(
            category=AchievementCategory.MILITARY,
            title="Battle Hero",
            description="Won a decisive battle",
            impact_on_advisor_potential=0.3,
            era_granted=TechnologyEra.ANCIENT,
            turn_granted=10
        )
        
        assert achievement.category == AchievementCategory.MILITARY
        assert achievement.title == "Battle Hero"
        assert achievement.impact_on_advisor_potential == 0.3
        assert achievement.era_granted == TechnologyEra.ANCIENT
        assert achievement.turn_granted == 10
        assert achievement.rarity == 0.5  # Default value


class TestSocialRelationship:
    """Test social relationship system."""
    
    def test_relationship_creation(self):
        """Test relationship creation."""
        relationship = SocialRelationship(
            citizen_a="citizen_1",
            citizen_b="citizen_2",
            relationship_type=RelationshipType.ALLY,
            strength=0.8,
            established_turn=5,
            last_interaction_turn=10
        )
        
        assert relationship.citizen_a == "citizen_1"
        assert relationship.citizen_b == "citizen_2"
        assert relationship.relationship_type == RelationshipType.ALLY
        assert relationship.strength == 0.8
        assert relationship.mutual is True  # Default value


class TestCitizenGenerator:
    """Test the citizen generator."""
    
    @pytest.fixture
    def generator(self):
        """Create a citizen generator for testing."""
        return create_citizen_generator()
    
    def test_generator_creation(self, generator):
        """Test generator creation."""
        assert generator is not None
        assert hasattr(generator, 'era_skill_weights')
        assert hasattr(generator, 'era_name_patterns')
        assert hasattr(generator, 'era_trait_tendencies')
    
    def test_era_data_completeness(self, generator):
        """Test that all eras have data."""
        for era in TechnologyEra:
            assert era in generator.era_skill_weights
            assert era in generator.era_name_patterns
            assert era in generator.era_trait_tendencies
    
    def test_generate_ancient_citizen(self, generator):
        """Test generating an ancient era citizen."""
        citizen = generator.generate_citizen(
            era=TechnologyEra.ANCIENT,
            turn=1,
            civilization_id="test_civ"
        )
        
        assert citizen.era_born == TechnologyEra.ANCIENT
        assert citizen.birth_turn == 1
        assert citizen.civilization_id == "test_civ"
        assert citizen.is_alive is True
        assert citizen.age >= 18  # Adult citizen
        assert len(citizen.skills) > 0  # Should have some skills
        assert len(citizen.traits) > 0  # Should have some traits
        assert citizen.advisor_potential >= 0.0
        assert citizen.advisor_potential <= 1.0
    
    def test_generate_modern_citizen(self, generator):
        """Test generating a modern era citizen."""
        citizen = generator.generate_citizen(
            era=TechnologyEra.MODERN,
            turn=100,
            civilization_id="modern_civ"
        )
        
        assert citizen.era_born == TechnologyEra.MODERN
        assert citizen.birth_turn == 100
        assert len(citizen.skills) > 0
        assert len(citizen.traits) > 0
        
        # Modern citizens might have different skill focus
        skill_names = list(citizen.skills.keys())
        assert any(skill in ["science", "technology", "medicine"] for skill in skill_names)
    
    def test_era_appropriate_skills(self, generator):
        """Test that citizens get era-appropriate skills."""
        ancient_citizen = generator.generate_citizen(TechnologyEra.ANCIENT, 1, "test")
        modern_citizen = generator.generate_citizen(TechnologyEra.MODERN, 1, "test")
        
        # Ancient citizens should focus more on combat, crafting, agriculture
        ancient_skills = ancient_citizen.skills
        modern_skills = modern_citizen.skills
        
        # Check that different eras produce different skill distributions
        assert set(ancient_skills.keys()) != set(modern_skills.keys()) or \
               ancient_skills != modern_skills  # Skills or values should differ
    
    def test_advisor_role_determination(self, generator):
        """Test advisor role determination."""
        # Generate multiple citizens and check role assignment
        citizens = [
            generator.generate_citizen(TechnologyEra.CLASSICAL, 1, "test")
            for _ in range(10)
        ]
        
        # At least some citizens should have potential advisor roles
        total_roles = sum(len(citizen.potential_roles) for citizen in citizens)
        assert total_roles > 0
        
        # Check that roles are valid
        for citizen in citizens:
            for role in citizen.potential_roles:
                assert isinstance(role, AdvisorRole)
    
    def test_skill_development_rates(self, generator):
        """Test skill development rate generation."""
        citizen = generator.generate_citizen(TechnologyEra.RENAISSANCE, 1, "test")
        
        # Should have development rates for skills
        assert len(citizen.skill_development_rate) > 0
        
        # Development rates should be reasonable
        for skill, rate in citizen.skill_development_rate.items():
            assert 0.001 <= rate <= 0.1  # Between 0.1% and 10%
            assert skill in citizen.skills  # Rate exists for actual skills


class TestEraAchievements:
    """Test era-specific achievements."""
    
    def test_get_era_achievements(self):
        """Test getting achievements for specific eras."""
        ancient_achievements = get_era_achievements(TechnologyEra.ANCIENT)
        assert len(ancient_achievements) > 0
        
        for achievement in ancient_achievements:
            assert achievement.era_granted == TechnologyEra.ANCIENT
            # Since we use_enum_values=True, categories are stored as strings
            assert achievement.category in [cat.value for cat in AchievementCategory]
    
    def test_achievement_rarity(self):
        """Test achievement rarity values."""
        ancient_achievements = get_era_achievements(TechnologyEra.ANCIENT)
        
        for achievement in ancient_achievements:
            assert 0.0 <= achievement.rarity <= 1.0
            assert 0.0 <= achievement.impact_on_advisor_potential <= 1.0


class TestEnumValues:
    """Test enum value completeness."""
    
    def test_skill_categories(self):
        """Test skill category enum."""
        expected_skills = [
            "combat", "crafting", "leadership", "agriculture", "engineering",
            "philosophy", "administration", "scholarship", "trade", "diplomacy",
            "medicine", "arts", "science", "technology", "exploration", "innovation"
        ]
        
        for skill in expected_skills:
            assert hasattr(SkillCategory, skill.upper())
    
    def test_achievement_categories(self):
        """Test achievement category enum."""
        categories = [cat.value for cat in AchievementCategory]
        expected = ["military", "economic", "diplomatic", "cultural", 
                   "technological", "leadership", "social", "spiritual"]
        
        for category in expected:
            assert category in categories
    
    def test_relationship_types(self):
        """Test relationship type enum."""
        types = [rel.value for rel in RelationshipType]
        expected = ["family", "professional", "political", "mentor_student",
                   "rival", "friend", "ally", "clan", "guild"]
        
        for rel_type in expected:
            assert rel_type in types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
