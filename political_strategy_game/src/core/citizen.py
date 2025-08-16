#!/usr/bin/env python3
"""
Citizen Data Structure for Political Advisor System

This module implements comprehensive citizen tracking for population-driven advisor
emergence, including skills, traits, achievements, social relationships, and
advisor potential calculation.
"""

from typing import Dict, List, Optional, Set, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid
import random
import math
from dataclasses import dataclass

# Import from existing systems
from .technology_tree import TechnologyEra
from .advisor import AdvisorRole


class AchievementCategory(str, Enum):
    """Categories of achievements that citizens can earn."""
    MILITARY = "military"
    ECONOMIC = "economic"
    DIPLOMATIC = "diplomatic"
    CULTURAL = "cultural"
    TECHNOLOGICAL = "technological"
    LEADERSHIP = "leadership"
    SOCIAL = "social"
    SPIRITUAL = "spiritual"


class RelationshipType(str, Enum):
    """Types of social relationships between citizens."""
    FAMILY = "family"
    PROFESSIONAL = "professional"
    POLITICAL = "political"
    MENTOR_STUDENT = "mentor_student"
    RIVAL = "rival"
    FRIEND = "friend"
    ALLY = "ally"
    CLAN = "clan"
    GUILD = "guild"


class SkillCategory(str, Enum):
    """Categories of skills that citizens can develop."""
    COMBAT = "combat"
    CRAFTING = "crafting"
    LEADERSHIP = "leadership"
    AGRICULTURE = "agriculture"
    ENGINEERING = "engineering"
    PHILOSOPHY = "philosophy"
    ADMINISTRATION = "administration"
    SCHOLARSHIP = "scholarship"
    TRADE = "trade"
    DIPLOMACY = "diplomacy"
    MEDICINE = "medicine"
    ARTS = "arts"
    SCIENCE = "science"
    TECHNOLOGY = "technology"
    EXPLORATION = "exploration"
    INNOVATION = "innovation"


class TraitCategory(str, Enum):
    """Categories of personality traits."""
    LEADERSHIP_TRAITS = "leadership"
    INTELLECTUAL_TRAITS = "intellectual"
    SOCIAL_TRAITS = "social"
    EMOTIONAL_TRAITS = "emotional"
    PHYSICAL_TRAITS = "physical"
    MORAL_TRAITS = "moral"


@dataclass
class EraSkillWeights:
    """Skill importance weights for different eras."""
    
    combat: float = 0.0
    crafting: float = 0.0
    leadership: float = 0.0
    agriculture: float = 0.0
    engineering: float = 0.0
    philosophy: float = 0.0
    administration: float = 0.0
    scholarship: float = 0.0
    trade: float = 0.0
    diplomacy: float = 0.0
    medicine: float = 0.0
    arts: float = 0.0
    science: float = 0.0
    technology: float = 0.0
    exploration: float = 0.0
    innovation: float = 0.0


class Achievement(BaseModel):
    """An achievement earned by a citizen."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: AchievementCategory
    title: str
    description: str
    impact_on_advisor_potential: float = Field(ge=0.0, le=1.0)
    era_granted: TechnologyEra
    turn_granted: int
    prerequisites: List[str] = Field(default_factory=list)  # Required skills or other achievements
    rarity: float = Field(default=0.5, ge=0.0, le=1.0)  # How rare this achievement is
    
    model_config = ConfigDict(use_enum_values=True)


class SocialRelationship(BaseModel):
    """A social relationship between two citizens."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    citizen_a: str  # citizen ID
    citizen_b: str  # citizen ID
    relationship_type: RelationshipType
    strength: float = Field(ge=0.0, le=1.0)
    established_turn: int
    last_interaction_turn: int
    mutual: bool = Field(default=True)  # Whether relationship is bidirectional
    
    model_config = ConfigDict(use_enum_values=True)


class Citizen(BaseModel):
    """
    A citizen in the political strategy game with comprehensive tracking
    for skills, traits, achievements, and advisor potential.
    """
    
    # Core identity
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    birth_turn: int
    era_born: TechnologyEra
    civilization_id: str
    
    # Age and lifecycle
    age: int = Field(default=0, ge=0)
    is_alive: bool = Field(default=True)
    death_turn: Optional[int] = Field(default=None)
    retirement_turn: Optional[int] = Field(default=None)
    
    # Skills (era-appropriate, 0.0-1.0 scale)
    skills: Dict[str, float] = Field(default_factory=dict)
    skill_development_rate: Dict[str, float] = Field(default_factory=dict)  # How fast they learn each skill
    
    # Traits (personality & aptitude, -1.0 to 1.0 scale)
    traits: Dict[str, float] = Field(default_factory=dict)
    
    # Achievements and history
    achievements: List[Achievement] = Field(default_factory=list)
    achievement_points: float = Field(default=0.0, ge=0.0)
    
    # Social network
    relationships: Dict[str, str] = Field(default_factory=dict)  # citizen_id -> relationship_id
    social_influence: float = Field(default=0.0, ge=0.0, le=1.0)
    reputation: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Advisor potential
    advisor_potential: float = Field(default=0.0, ge=0.0, le=1.0)
    potential_roles: Set[AdvisorRole] = Field(default_factory=set)
    advisor_readiness: bool = Field(default=False)
    last_potential_calculation: int = Field(default=0)
    
    # Career and specialization
    primary_occupation: Optional[str] = Field(default=None)
    specializations: List[str] = Field(default_factory=list)
    notable_contributions: List[str] = Field(default_factory=list)
    
    # Performance tracking
    recent_performance: List[float] = Field(default_factory=list)  # Last 10 turns of performance
    peak_performance_turn: Optional[int] = Field(default=None)
    peak_performance_value: float = Field(default=0.0)
    
    model_config = ConfigDict(use_enum_values=True)


class CitizenGenerator:
    """Generates era-appropriate citizens with realistic characteristics."""
    
    def __init__(self):
        self.era_skill_weights = self._initialize_era_skill_weights()
        self.era_name_patterns = self._initialize_era_name_patterns()
        self.era_trait_tendencies = self._initialize_era_trait_tendencies()
    
    def _initialize_era_skill_weights(self) -> Dict[TechnologyEra, EraSkillWeights]:
        """Initialize skill importance weights for each era."""
        return {
            TechnologyEra.ANCIENT: EraSkillWeights(
                combat=0.25, crafting=0.20, leadership=0.15, agriculture=0.20,
                engineering=0.05, philosophy=0.05, administration=0.10
            ),
            TechnologyEra.CLASSICAL: EraSkillWeights(
                combat=0.20, crafting=0.15, leadership=0.15, agriculture=0.15,
                engineering=0.10, philosophy=0.10, administration=0.15
            ),
            TechnologyEra.MEDIEVAL: EraSkillWeights(
                combat=0.15, crafting=0.15, leadership=0.15, agriculture=0.10,
                engineering=0.10, philosophy=0.10, administration=0.15, trade=0.10
            ),
            TechnologyEra.RENAISSANCE: EraSkillWeights(
                combat=0.10, crafting=0.10, leadership=0.15, agriculture=0.08,
                engineering=0.12, philosophy=0.10, administration=0.15, trade=0.10, arts=0.10
            ),
            TechnologyEra.INDUSTRIAL: EraSkillWeights(
                combat=0.08, crafting=0.10, leadership=0.15, agriculture=0.05,
                engineering=0.15, philosophy=0.08, administration=0.15, trade=0.12, science=0.12
            ),
            TechnologyEra.MODERN: EraSkillWeights(
                combat=0.05, crafting=0.05, leadership=0.15, agriculture=0.03,
                engineering=0.15, philosophy=0.08, administration=0.15, trade=0.10, 
                science=0.15, medicine=0.09
            ),
            TechnologyEra.CONTEMPORARY: EraSkillWeights(
                combat=0.05, leadership=0.15, engineering=0.15, administration=0.15,
                trade=0.08, science=0.20, medicine=0.10, technology=0.12
            ),
            TechnologyEra.FUTURE: EraSkillWeights(
                leadership=0.15, engineering=0.10, administration=0.15, trade=0.10,
                science=0.15, medicine=0.08, technology=0.25, innovation=0.02
            )
        }
    
    def _initialize_era_name_patterns(self) -> Dict[TechnologyEra, List[str]]:
        """Initialize era-appropriate name patterns."""
        return {
            TechnologyEra.ANCIENT: [
                "Marcus", "Gaius", "Lucius", "Titus", "Quintus", "Cassius", "Brutus",
                "Alexander", "Demetrius", "Apollodorus", "Xenophon", "Aristides"
            ],
            TechnologyEra.CLASSICAL: [
                "Augustus", "Aurelius", "Cicero", "Seneca", "Pliny", "Tacitus",
                "Aristotle", "Plato", "Socrates", "Epictetus", "Plutarch"
            ],
            TechnologyEra.MEDIEVAL: [
                "William", "Henry", "Richard", "Geoffrey", "Baldwin", "Godfrey",
                "Thomas", "Robert", "Edward", "Roger", "Hugh", "Walter"
            ],
            TechnologyEra.RENAISSANCE: [
                "Lorenzo", "Cosimo", "Francesco", "Giovanni", "Niccolò", "Leonardo",
                "Raphael", "Michelangelo", "Donatello", "Brunelleschi"
            ],
            TechnologyEra.INDUSTRIAL: [
                "James", "Charles", "George", "William", "Thomas", "John",
                "Alexander", "Benjamin", "Samuel", "Isaac", "Robert"
            ],
            TechnologyEra.MODERN: [
                "Albert", "Werner", "Niels", "Ernest", "Marie", "Louis",
                "Alexander", "Thomas", "Henry", "Charles", "Frederick"
            ],
            TechnologyEra.CONTEMPORARY: [
                "Robert", "Enrico", "Leo", "Edward", "Stanislaw", "Eugene",
                "Richard", "Murray", "Hans", "Victor", "Glenn"
            ],
            TechnologyEra.FUTURE: [
                "Alan", "John", "Steve", "Bill", "Larry", "Sergey",
                "Mark", "Jeff", "Elon", "Tim", "Satya", "Susan"
            ]
        }
    
    def _initialize_era_trait_tendencies(self) -> Dict[TechnologyEra, Dict[str, float]]:
        """Initialize era-specific trait tendencies."""
        return {
            TechnologyEra.ANCIENT: {
                "courage": 0.7, "honor": 0.8, "strength": 0.7, "loyalty": 0.8,
                "pragmatism": 0.6, "ambition": 0.7, "charisma": 0.6
            },
            TechnologyEra.CLASSICAL: {
                "wisdom": 0.7, "honor": 0.7, "eloquence": 0.6, "discipline": 0.7,
                "curiosity": 0.6, "rationality": 0.6, "civic_duty": 0.8
            },
            TechnologyEra.MEDIEVAL: {
                "faith": 0.8, "honor": 0.8, "loyalty": 0.8, "courage": 0.7,
                "tradition": 0.8, "humility": 0.6, "perseverance": 0.7
            },
            TechnologyEra.RENAISSANCE: {
                "curiosity": 0.8, "creativity": 0.8, "ambition": 0.7, "eloquence": 0.7,
                "innovation": 0.6, "individualism": 0.6, "artistic_sense": 0.7
            },
            TechnologyEra.INDUSTRIAL: {
                "innovation": 0.8, "pragmatism": 0.8, "ambition": 0.8, "efficiency": 0.7,
                "rationality": 0.7, "perseverance": 0.8, "entrepreneurship": 0.6
            },
            TechnologyEra.MODERN: {
                "analytical_thinking": 0.8, "innovation": 0.8, "collaboration": 0.7,
                "adaptability": 0.7, "scientific_method": 0.8, "precision": 0.7
            },
            TechnologyEra.CONTEMPORARY: {
                "analytical_thinking": 0.9, "innovation": 0.8, "responsibility": 0.7,
                "caution": 0.6, "scientific_rigor": 0.9, "ethical_concern": 0.6
            },
            TechnologyEra.FUTURE: {
                "adaptability": 0.9, "innovation": 0.9, "systems_thinking": 0.8,
                "collaboration": 0.8, "speed": 0.7, "global_perspective": 0.7
            }
        }
    
    def generate_citizen(self, era: TechnologyEra, turn: int, civilization_id: str) -> Citizen:
        """Generate an era-appropriate citizen with realistic characteristics."""
        
        # Generate basic identity
        name = self._generate_era_appropriate_name(era)
        citizen_id = str(uuid.uuid4())
        
        # Generate skills based on era
        skills = self._generate_era_skills(era)
        
        # Generate traits based on era tendencies
        traits = self._generate_era_traits(era)
        
        # Generate initial skill development rates
        skill_development_rate = self._generate_skill_development_rates(skills, traits)
        
        # Create citizen
        citizen = Citizen(
            id=citizen_id,
            name=name,
            birth_turn=turn,
            era_born=era,
            civilization_id=civilization_id,
            age=random.randint(18, 45),  # Adult citizens
            skills=skills,
            skill_development_rate=skill_development_rate,
            traits=traits,
            reputation=random.uniform(0.3, 0.7)  # Starting reputation
        )
        
        # Calculate initial advisor potential
        citizen.advisor_potential = self._calculate_initial_advisor_potential(citizen, era)
        citizen.potential_roles = self._determine_potential_advisor_roles(citizen, era)
        citizen.last_potential_calculation = turn
        
        return citizen
    
    def _generate_era_appropriate_name(self, era: TechnologyEra) -> str:
        """Generate a name appropriate for the era."""
        names = self.era_name_patterns.get(era, ["Citizen"])
        base_name = random.choice(names)
        
        # Add some variation
        if random.random() < 0.3:  # 30% chance of name variation
            suffixes = ["the Wise", "the Bold", "the Just", "the Great", "the Elder"]
            return f"{base_name} {random.choice(suffixes)}"
        
        return base_name
    
    def _generate_era_skills(self, era: TechnologyEra) -> Dict[str, float]:
        """Generate era-appropriate skills for a citizen."""
        skills = {}
        era_weights = self.era_skill_weights.get(era, EraSkillWeights())
        
        # Generate skills based on era importance
        for skill_name, weight in era_weights.__dict__.items():
            if weight > 0:
                # Higher weight = higher chance of good skill
                base_skill = random.uniform(0.0, weight * 2)  # Max skill proportional to era importance
                # Add some randomness but cap at 1.0
                skills[skill_name] = min(1.0, base_skill + random.uniform(-0.1, 0.1))
        
        # Add some random skills from other categories with lower values
        all_skills = [skill.value for skill in SkillCategory]
        for skill in all_skills:
            if skill not in skills and random.random() < 0.3:  # 30% chance
                skills[skill] = random.uniform(0.0, 0.3)  # Lower proficiency
        
        return skills
    
    def _generate_era_traits(self, era: TechnologyEra) -> Dict[str, float]:
        """Generate era-appropriate traits for a citizen."""
        traits = {}
        era_tendencies = self.era_trait_tendencies.get(era, {})
        
        # Generate traits based on era tendencies
        for trait_name, tendency in era_tendencies.items():
            # Tendency influences the average, but there's still individual variation
            base_value = random.gauss(tendency, 0.2)  # Normal distribution around tendency
            traits[trait_name] = max(-1.0, min(1.0, base_value))  # Clamp to [-1, 1]
        
        # Add some additional random traits
        additional_traits = ["intelligence", "creativity", "social_skills", "determination", 
                           "empathy", "strategic_thinking", "communication", "adaptability"]
        
        for trait in additional_traits:
            if trait not in traits:
                traits[trait] = random.uniform(-0.5, 0.5)  # Moderate random values
        
        return traits
    
    def _generate_skill_development_rates(self, skills: Dict[str, float], traits: Dict[str, float]) -> Dict[str, float]:
        """Generate skill development rates based on existing skills and traits."""
        development_rates = {}
        
        for skill_name, skill_value in skills.items():
            # Base development rate
            base_rate = random.uniform(0.01, 0.05)  # 1-5% per turn
            
            # Modify based on traits
            trait_modifiers = {
                "intelligence": 0.02,
                "curiosity": 0.015,
                "determination": 0.01,
                "adaptability": 0.01
            }
            
            for trait_name, modifier in trait_modifiers.items():
                if trait_name in traits:
                    base_rate += traits[trait_name] * modifier
            
            # Lower development rate for skills you're already good at (diminishing returns)
            if skill_value > 0.7:
                base_rate *= 0.5
            elif skill_value > 0.5:
                base_rate *= 0.75
            
            development_rates[skill_name] = max(0.001, min(0.1, base_rate))  # Cap between 0.1% and 10%
        
        return development_rates
    
    def _calculate_initial_advisor_potential(self, citizen: Citizen, era: TechnologyEra) -> float:
        """Calculate the initial advisor potential for a citizen."""
        # This is a simplified initial calculation
        # More sophisticated calculation will be implemented in Day 3
        
        skill_score = sum(citizen.skills.values()) / max(1, len(citizen.skills))
        trait_score = sum(max(0, trait_val) for trait_val in citizen.traits.values()) / max(1, len(citizen.traits))
        
        # Combine scores with some randomness
        potential = (skill_score * 0.6 + trait_score * 0.4) * random.uniform(0.8, 1.2)
        
        return max(0.0, min(1.0, potential))
    
    def _determine_potential_advisor_roles(self, citizen: Citizen, era: TechnologyEra) -> Set[AdvisorRole]:
        """Determine which advisor roles this citizen could potentially fill."""
        potential_roles = set()
        
        # Role mapping based on skills and traits
        role_requirements = {
            AdvisorRole.MILITARY: ["combat", "leadership", "courage", "strategic_thinking"],
            AdvisorRole.ECONOMIC: ["trade", "administration", "pragmatism", "analytical_thinking"],
            AdvisorRole.DIPLOMATIC: ["diplomacy", "eloquence", "charisma", "empathy"],
            AdvisorRole.SCIENTIFIC: ["scholarship", "curiosity", "analytical_thinking", "adaptability"],
            AdvisorRole.SECURITY: ["combat", "leadership", "caution", "loyalty"],
            AdvisorRole.CULTURAL: ["arts", "creativity", "social_skills", "charisma"],
            AdvisorRole.RELIGIOUS: ["philosophy", "wisdom", "charisma", "faith"]
        }
        
        for role, requirements in role_requirements.items():
            # Calculate suitability for this role
            suitability = 0.0
            requirement_count = 0
            
            for requirement in requirements:
                if requirement in citizen.skills:
                    suitability += citizen.skills[requirement]
                    requirement_count += 1
                elif requirement in citizen.traits:
                    # Normalize trait value from [-1,1] to [0,1] for positive traits
                    trait_value = max(0, citizen.traits[requirement])
                    suitability += trait_value
                    requirement_count += 1
            
            if requirement_count > 0:
                avg_suitability = suitability / requirement_count
                if avg_suitability > 0.4:  # Threshold for role potential
                    potential_roles.add(role)
        
        return potential_roles


# Era-specific achievement definitions
ERA_ACHIEVEMENTS = {
    TechnologyEra.ANCIENT: [
        Achievement(
            category=AchievementCategory.MILITARY,
            title="Veteran Warrior",
            description="Survived 10 battles and demonstrated exceptional combat prowess",
            impact_on_advisor_potential=0.3,
            era_granted=TechnologyEra.ANCIENT,
            turn_granted=0,
            prerequisites=["combat"],
            rarity=0.1
        ),
        Achievement(
            category=AchievementCategory.LEADERSHIP,
            title="Tribal Chief",
            description="Led a tribal community through difficult times",
            impact_on_advisor_potential=0.4,
            era_granted=TechnologyEra.ANCIENT,
            turn_granted=0,
            prerequisites=["leadership"],
            rarity=0.05
        ),
        Achievement(
            category=AchievementCategory.ECONOMIC,
            title="Master Craftsman",
            description="Achieved mastery in essential crafting skills",
            impact_on_advisor_potential=0.25,
            era_granted=TechnologyEra.ANCIENT,
            turn_granted=0,
            prerequisites=["crafting"],
            rarity=0.15
        )
    ],
    # Additional era achievements will be added as needed
}


def get_era_achievements(era: TechnologyEra) -> List[Achievement]:
    """Get available achievements for a specific era."""
    return ERA_ACHIEVEMENTS.get(era, [])


def create_citizen_generator() -> CitizenGenerator:
    """Factory function to create a citizen generator."""
    return CitizenGenerator()
