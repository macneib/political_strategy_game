#!/usr/bin/env python3
"""
Agent Development System for Advanced Skill Growth and Achievement Management

This module implements sophisticated skill development algorithms, achievement systems,
and advanced relationship modeling for agent pool management Day 2.
"""

from typing import Dict, List, Optional, Tuple, Any, Union, Set
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from dataclasses import dataclass
from datetime import datetime
import uuid
import random
import math
from collections import defaultdict
import numpy as np

# Import from existing systems
try:
    from .citizen import Citizen, Achievement, AchievementCategory
    from .technology_tree import TechnologyEra
    from .advisor import AdvisorRole
    from .agent_pool import Agent, PersonalityProfile, PerformanceMetrics, SocialNetwork, MentorshipRecord
except ImportError:
    # For testing/standalone execution, attempt relative imports
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from political_strategy_game.src.core.citizen import Citizen, Achievement, AchievementCategory
    from political_strategy_game.src.core.technology_tree import TechnologyEra
    from political_strategy_game.src.core.advisor import AdvisorRole
    from political_strategy_game.src.core.agent_pool import Agent, PersonalityProfile, PerformanceMetrics, SocialNetwork, MentorshipRecord


class SkillDevelopmentType(str, Enum):
    """Types of skill development mechanisms."""
    NATURAL_LEARNING = "natural_learning"
    MENTORSHIP = "mentorship"
    EXPERIENCE_BASED = "experience_based"
    CRISIS_ACCELERATED = "crisis_accelerated"
    COLLABORATIVE = "collaborative"
    SELF_STUDY = "self_study"
    PRACTICAL_APPLICATION = "practical_application"
    INNOVATION = "innovation"


class LearningModifier(str, Enum):
    """Modifiers that affect learning rates."""
    AGE_PENALTY = "age_penalty"
    AGE_BONUS = "age_bonus"
    TRAIT_SYNERGY = "trait_synergy"
    SKILL_PLATEAU = "skill_plateau"
    BREAKTHROUGH = "breakthrough"
    MENTORSHIP_BOOST = "mentorship_boost"
    STRESS_PENALTY = "stress_penalty"
    MOTIVATION_BOOST = "motivation_boost"


class AchievementDifficulty(str, Enum):
    """Difficulty levels for achievements."""
    TRIVIAL = "trivial"      # 80%+ of eligible population achieves
    COMMON = "common"        # 40-80% achievement rate
    UNCOMMON = "uncommon"    # 15-40% achievement rate
    RARE = "rare"           # 5-15% achievement rate
    LEGENDARY = "legendary"  # 1-5% achievement rate
    MYTHIC = "mythic"       # <1% achievement rate


class SkillSynergy(str, Enum):
    """Types of skill synergies for cross-skill development."""
    COMPLEMENTARY = "complementary"    # Skills that support each other
    COMPETITIVE = "competitive"        # Skills that compete for development time
    FOUNDATIONAL = "foundational"      # Skills that boost all others
    SPECIALIZED = "specialized"        # Skills that require focus
    CREATIVE = "creative"             # Skills that enhance innovation


# Day 3: Advanced Lifecycle Management Enums

class LifecycleStage(str, Enum):
    """Lifecycle stages for agent development."""
    EMERGING = "emerging"          # 18-25: High learning, low experience
    DEVELOPING = "developing"      # 26-35: Peak learning, growing experience
    PRIME = "prime"               # 36-50: Peak performance, established reputation
    MATURE = "mature"             # 51-65: High wisdom, declining physical abilities
    ELDER = "elder"               # 66-80: Maximum wisdom, mentor role
    DECLINING = "declining"       # 81+: Significant decline, retirement consideration


class ReputationDimension(str, Enum):
    """Different dimensions of agent reputation."""
    COMPETENCE = "competence"         # Technical skill and effectiveness
    INTEGRITY = "integrity"           # Trustworthiness and moral character
    INNOVATION = "innovation"         # Creativity and progressive thinking
    LEADERSHIP = "leadership"         # Ability to inspire and guide others
    WISDOM = "wisdom"                # Deep understanding and good judgment
    CHARISMA = "charisma"            # Personal magnetism and influence
    RELIABILITY = "reliability"       # Consistency and dependability
    VISION = "vision"                # Strategic thinking and foresight


class SocialInfluenceType(str, Enum):
    """Types of social influence an agent can wield."""
    FORMAL_AUTHORITY = "formal_authority"     # Official position power
    EXPERTISE = "expertise"                   # Knowledge-based influence
    PERSONAL_CHARM = "personal_charm"         # Charismatic influence
    NETWORK_CENTRALITY = "network_centrality" # Position in social networks
    REPUTATION = "reputation"                 # Respect and standing
    RESOURCE_CONTROL = "resource_control"     # Economic/material influence
    CULTURAL_STANDING = "cultural_standing"   # Traditional/cultural respect
    MENTORSHIP = "mentorship"                 # Influence through teaching


class SuccessionType(str, Enum):
    """Types of succession planning."""
    DIRECT_APPOINTMENT = "direct_appointment"     # Chosen successor
    COMPETITIVE_SELECTION = "competitive_selection" # Multiple candidates compete
    NATURAL_EMERGENCE = "natural_emergence"      # Organic successor identification
    CRISIS_SUCCESSION = "crisis_succession"      # Emergency succession
    COLLECTIVE_DECISION = "collective_decision"  # Group choice
    TRADITIONAL = "traditional"                  # Cultural/traditional succession


class RelationshipEvolution(str, Enum):
    """How relationships evolve over time."""
    STRENGTHENING = "strengthening"    # Growing closer
    WEAKENING = "weakening"           # Growing apart
    STABLE = "stable"                 # Maintaining current level
    TRANSFORMING = "transforming"     # Changing nature of relationship
    CYCLING = "cycling"               # Periodic ups and downs
    CONFLICTING = "conflicting"       # Developing tension
    RECONCILING = "reconciling"       # Resolving conflicts


@dataclass
class SkillDevelopmentEvent:
    """Record of a skill development event."""
    turn: int
    agent_id: str
    skill_name: str
    development_type: SkillDevelopmentType
    old_value: float
    new_value: float
    learning_rate: float
    modifiers: List[LearningModifier]
    context: str
    mentor_id: Optional[str] = None
    achievement_unlocked: Optional[str] = None


@dataclass
class SkillSynergyEffect:
    """Effect of skill synergies on development."""
    primary_skill: str
    supporting_skills: List[str]
    synergy_type: SkillSynergy
    synergy_strength: float
    development_bonus: float
    efficiency_multiplier: float


# Day 3: Advanced Lifecycle Management Data Structures

@dataclass
class LifecycleEvent:
    """Significant events in an agent's lifecycle."""
    turn: int
    agent_id: str
    event_type: str
    description: str
    impact_areas: List[str]  # Skills, traits, or attributes affected
    magnitude: float  # -1.0 to 1.0, negative for setbacks, positive for advantages
    narrative_weight: float  # How significant for storytelling
    triggers: List[str]  # What triggered this event
    consequences: List[str]  # What this event might lead to


@dataclass
class ReputationRecord:
    """Record of reputation changes and events."""
    turn: int
    agent_id: str
    dimension: ReputationDimension
    old_value: float
    new_value: float
    change_reason: str
    witnesses: List[str]  # Agent IDs who observed the reputation change
    public_awareness: float  # How widely known is this change (0.0-1.0)
    decay_rate: float  # How quickly this reputation change fades


@dataclass
class SocialInfluenceEvent:
    """Record of social influence being exercised."""
    turn: int
    influencer_id: str
    target_ids: List[str]
    influence_type: SocialInfluenceType
    success_rate: float
    magnitude: float
    context: str
    resistance_factors: List[str]
    amplification_factors: List[str]


@dataclass
class SuccessionPlan:
    """Plans for agent succession and legacy transfer."""
    mentor_id: str
    potential_successors: List[str]
    succession_type: SuccessionType
    readiness_scores: Dict[str, float]  # successor_id -> readiness score
    preparation_activities: List[str]
    knowledge_transfer_plan: Dict[str, List[str]]  # skill -> learning activities
    timeline: int  # Expected turns until succession
    contingency_plans: List[str]
    cultural_considerations: List[str]


@dataclass
class RelationshipDynamics:
    """Dynamic aspects of agent relationships."""
    agent_a_id: str
    agent_b_id: str
    current_strength: float
    evolution_trend: RelationshipEvolution
    interaction_frequency: float
    shared_experiences: List[str]
    conflict_history: List[str]
    mutual_benefits: List[str]
    influence_balance: float  # -1.0 to 1.0, negative means A influences B more
    trust_level: float
    respect_level: float
    dependency_level: float


class EnhancedAchievement(BaseModel):
    """Enhanced achievement with complex prerequisites and effects."""
    
    # Basic achievement data
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: AchievementCategory
    title: str
    description: str
    era_granted: TechnologyEra
    turn_granted: int
    
    # Enhanced attributes
    difficulty: AchievementDifficulty = Field(default=AchievementDifficulty.COMMON)
    rarity_score: float = Field(default=0.5, ge=0.0, le=1.0)
    prestige_value: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Complex prerequisites
    skill_requirements: Dict[str, float] = Field(default_factory=dict)
    trait_requirements: Dict[str, float] = Field(default_factory=dict)
    achievement_prerequisites: List[str] = Field(default_factory=list)
    era_requirements: List[TechnologyEra] = Field(default_factory=list)
    age_requirements: Optional[Tuple[int, int]] = Field(default=None)
    social_requirements: Dict[str, float] = Field(default_factory=dict)  # reputation, influence, etc.
    
    # Dynamic effects
    skill_bonuses: Dict[str, float] = Field(default_factory=dict)
    trait_bonuses: Dict[str, float] = Field(default_factory=dict)
    reputation_bonus: float = Field(default=0.0)
    social_influence_bonus: float = Field(default=0.0)
    advisor_potential_bonus: float = Field(default=0.0)
    
    # Achievement chains and progression
    achievement_chain: Optional[str] = Field(default=None)
    next_achievements: List[str] = Field(default_factory=list)
    mutually_exclusive: List[str] = Field(default_factory=list)
    
    # Narrative and context
    unlock_conditions: List[str] = Field(default_factory=list)
    narrative_significance: float = Field(default=0.5, ge=0.0, le=1.0)
    historical_context: str = Field(default="")
    unique_per_civilization: bool = Field(default=False)
    
    model_config = ConfigDict(use_enum_values=True)


class SkillDevelopmentManager(BaseModel):
    """Manages sophisticated skill development for agents."""
    
    # Learning rate configuration
    base_learning_rates: Dict[str, float] = Field(default_factory=dict)
    era_learning_modifiers: Dict[TechnologyEra, Dict[str, float]] = Field(default_factory=dict)
    age_learning_curves: Dict[str, List[Tuple[int, float]]] = Field(default_factory=dict)
    
    # Skill synergies
    skill_synergies: List[SkillSynergyEffect] = Field(default_factory=list)
    synergy_matrix: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    
    # Plateau and breakthrough mechanics
    plateau_thresholds: Dict[str, float] = Field(default_factory=dict)
    breakthrough_probabilities: Dict[str, float] = Field(default_factory=dict)
    
    # Development history
    development_history: List[SkillDevelopmentEvent] = Field(default_factory=list)
    
    model_config = ConfigDict(use_enum_values=True)
    
    def __init__(self, **data):
        super().__init__(**data)
        self._initialize_default_configurations()
    
    def _initialize_default_configurations(self):
        """Initialize default learning configurations."""
        # Base learning rates for different skills
        self.base_learning_rates = {
            "combat": 0.04,
            "crafting": 0.03,
            "leadership": 0.025,
            "agriculture": 0.035,
            "engineering": 0.03,
            "philosophy": 0.02,
            "administration": 0.025,
            "scholarship": 0.02,
            "trade": 0.03,
            "diplomacy": 0.025,
            "medicine": 0.025,
            "arts": 0.03,
            "science": 0.02,
            "technology": 0.025,
            "exploration": 0.04,
            "innovation": 0.015
        }
        
        # Era-specific learning modifiers
        self.era_learning_modifiers = {
            TechnologyEra.ANCIENT: {
                "combat": 1.5, "crafting": 1.3, "agriculture": 1.4,
                "leadership": 1.2, "philosophy": 0.8
            },
            TechnologyEra.CLASSICAL: {
                "philosophy": 1.4, "administration": 1.3, "diplomacy": 1.2,
                "arts": 1.2, "scholarship": 1.1
            },
            TechnologyEra.MEDIEVAL: {
                "crafting": 1.2, "trade": 1.3, "engineering": 1.1,
                "leadership": 1.1
            },
            TechnologyEra.RENAISSANCE: {
                "arts": 1.5, "innovation": 1.4, "scholarship": 1.3,
                "engineering": 1.2, "exploration": 1.3
            },
            TechnologyEra.INDUSTRIAL: {
                "engineering": 1.4, "innovation": 1.3, "trade": 1.2,
                "science": 1.3
            },
            TechnologyEra.MODERN: {
                "science": 1.5, "technology": 1.4, "medicine": 1.3,
                "administration": 1.2
            },
            TechnologyEra.CONTEMPORARY: {
                "technology": 1.5, "science": 1.4, "innovation": 1.4,
                "medicine": 1.2
            },
            TechnologyEra.FUTURE: {
                "innovation": 1.6, "technology": 1.5, "science": 1.3,
                "exploration": 1.2
            }
        }
        
        # Plateau thresholds (where learning slows significantly)
        self.plateau_thresholds = {skill: 0.75 for skill in self.base_learning_rates.keys()}
        
        # Breakthrough probabilities (chance to overcome plateaus)
        self.breakthrough_probabilities = {skill: 0.05 for skill in self.base_learning_rates.keys()}
        
        # Initialize skill synergies
        self._initialize_skill_synergies()
    
    def _initialize_skill_synergies(self):
        """Initialize skill synergy effects."""
        self.skill_synergies = [
            # Leadership synergies
            SkillSynergyEffect(
                primary_skill="leadership",
                supporting_skills=["diplomacy", "administration", "philosophy"],
                synergy_type=SkillSynergy.COMPLEMENTARY,
                synergy_strength=0.8,
                development_bonus=0.15,
                efficiency_multiplier=1.2
            ),
            
            # Innovation synergies
            SkillSynergyEffect(
                primary_skill="innovation",
                supporting_skills=["science", "engineering", "technology"],
                synergy_type=SkillSynergy.CREATIVE,
                synergy_strength=0.9,
                development_bonus=0.2,
                efficiency_multiplier=1.3
            ),
            
            # Scholarship foundations
            SkillSynergyEffect(
                primary_skill="scholarship",
                supporting_skills=["philosophy", "science", "medicine"],
                synergy_type=SkillSynergy.FOUNDATIONAL,
                synergy_strength=0.7,
                development_bonus=0.1,
                efficiency_multiplier=1.15
            ),
            
            # Trade and diplomacy
            SkillSynergyEffect(
                primary_skill="trade",
                supporting_skills=["diplomacy", "administration"],
                synergy_type=SkillSynergy.COMPLEMENTARY,
                synergy_strength=0.75,
                development_bonus=0.12,
                efficiency_multiplier=1.18
            ),
            
            # Combat specialization
            SkillSynergyEffect(
                primary_skill="combat",
                supporting_skills=["leadership", "engineering"],
                synergy_type=SkillSynergy.SPECIALIZED,
                synergy_strength=0.85,
                development_bonus=0.18,
                efficiency_multiplier=1.25
            )
        ]
        
        # Build synergy matrix for quick lookups
        self.synergy_matrix = defaultdict(lambda: defaultdict(float))
        for synergy in self.skill_synergies:
            for supporting_skill in synergy.supporting_skills:
                self.synergy_matrix[synergy.primary_skill][supporting_skill] = synergy.development_bonus
    
    def calculate_learning_rate(self, agent: Agent, skill: str, era: TechnologyEra, 
                               turn: int, development_type: SkillDevelopmentType = SkillDevelopmentType.NATURAL_LEARNING) -> Tuple[float, List[LearningModifier]]:
        """Calculate the effective learning rate for a skill."""
        if skill not in self.base_learning_rates:
            return 0.0, []
        
        base_rate = self.base_learning_rates[skill]
        modifiers = []
        rate_multiplier = 1.0
        
        # Era modifier
        era_modifiers = self.era_learning_modifiers.get(era, {})
        if skill in era_modifiers:
            rate_multiplier *= era_modifiers[skill]
        
        # Age effects
        age_effect = self._calculate_age_effect(agent.age, skill)
        rate_multiplier *= age_effect
        if age_effect < 0.9:
            modifiers.append(LearningModifier.AGE_PENALTY)
        elif age_effect > 1.1:
            modifiers.append(LearningModifier.AGE_BONUS)
        
        # Trait effects
        trait_effect = self._calculate_trait_effect(agent, skill)
        rate_multiplier *= trait_effect
        if trait_effect > 1.2:
            modifiers.append(LearningModifier.TRAIT_SYNERGY)
        
        # Current skill level effects (diminishing returns)
        current_skill = agent.skills.get(skill, 0.0)
        plateau_threshold = self.plateau_thresholds.get(skill, 0.75)
        
        if current_skill > plateau_threshold:
            plateau_penalty = 0.3 + 0.4 * (1.0 - current_skill) / (1.0 - plateau_threshold)
            rate_multiplier *= plateau_penalty
            modifiers.append(LearningModifier.SKILL_PLATEAU)
            
            # Breakthrough chance
            breakthrough_prob = self.breakthrough_probabilities.get(skill, 0.05)
            if random.random() < breakthrough_prob:
                rate_multiplier *= 2.0
                modifiers.append(LearningModifier.BREAKTHROUGH)
        
        # Skill synergy effects
        synergy_bonus = self._calculate_synergy_bonus(agent, skill)
        rate_multiplier *= (1.0 + synergy_bonus)
        
        # Development type modifiers
        type_modifier = self._get_development_type_modifier(development_type)
        rate_multiplier *= type_modifier
        
        # Mentorship effects (if applicable)
        if development_type == SkillDevelopmentType.MENTORSHIP:
            mentorship_bonus = self._calculate_mentorship_bonus(agent, skill)
            rate_multiplier *= (1.0 + mentorship_bonus)
            modifiers.append(LearningModifier.MENTORSHIP_BOOST)
        
        final_rate = base_rate * rate_multiplier
        return max(0.001, min(0.15, final_rate)), modifiers  # Cap between 0.1% and 15%
    
    def _calculate_age_effect(self, age: int, skill: str) -> float:
        """Calculate age effect on learning rate."""
        # Peak learning ages vary by skill type
        peak_ages = {
            "combat": 25, "crafting": 30, "leadership": 40, "agriculture": 35,
            "engineering": 35, "philosophy": 45, "administration": 42,
            "scholarship": 30, "trade": 35, "diplomacy": 40, "medicine": 38,
            "arts": 28, "science": 32, "technology": 30, "exploration": 27,
            "innovation": 33
        }
        
        peak_age = peak_ages.get(skill, 35)
        
        # Learning efficiency curve: peaks at optimal age, declines gradually
        if age <= peak_age:
            # Gradual improvement to peak
            efficiency = 0.7 + 0.3 * (age / peak_age)
        else:
            # Gradual decline after peak
            decline_rate = 0.02  # 2% per year after peak
            years_past_peak = age - peak_age
            efficiency = 1.0 - (decline_rate * years_past_peak)
        
        return max(0.3, min(1.3, efficiency))  # Cap between 30% and 130%
    
    def _calculate_trait_effect(self, agent: Agent, skill: str) -> float:
        """Calculate trait effects on skill learning."""
        trait_mappings = {
            "combat": ["courage", "strength", "determination", "discipline"],
            "crafting": ["creativity", "precision", "patience", "innovation"],
            "leadership": ["charisma", "confidence", "empathy", "strategic_thinking"],
            "agriculture": ["patience", "pragmatism", "observation", "perseverance"],
            "engineering": ["analytical_thinking", "precision", "innovation", "pragmatism"],
            "philosophy": ["wisdom", "curiosity", "rationality", "contemplation"],
            "administration": ["organization", "efficiency", "attention_to_detail", "pragmatism"],
            "scholarship": ["intelligence", "curiosity", "memory", "analytical_thinking"],
            "trade": ["social_skills", "persuasion", "adaptability", "opportunism"],
            "diplomacy": ["charisma", "empathy", "eloquence", "cultural_sensitivity"],
            "medicine": ["empathy", "precision", "analytical_thinking", "dedication"],
            "arts": ["creativity", "emotional_intelligence", "aesthetic_sense", "expression"],
            "science": ["analytical_thinking", "curiosity", "precision", "methodical"],
            "technology": ["innovation", "analytical_thinking", "adaptability", "precision"],
            "exploration": ["courage", "adaptability", "curiosity", "resilience"],
            "innovation": ["creativity", "vision", "risk_taking", "unconventional_thinking"]
        }
        
        relevant_traits = trait_mappings.get(skill, [])
        if not relevant_traits:
            return 1.0
        
        trait_bonus = 0.0
        trait_count = 0
        
        for trait in relevant_traits:
            if trait in agent.traits:
                trait_value = agent.traits[trait]
                # Convert trait value from [-1, 1] to learning modifier
                trait_bonus += max(0, trait_value) * 0.3  # Up to 30% bonus per trait
                trait_count += 1
        
        if trait_count > 0:
            average_bonus = trait_bonus / trait_count
            return 1.0 + average_bonus
        
        return 1.0
    
    def _calculate_synergy_bonus(self, agent: Agent, skill: str) -> float:
        """Calculate skill synergy bonus for learning."""
        total_bonus = 0.0
        
        if skill in self.synergy_matrix:
            for supporting_skill, bonus_rate in self.synergy_matrix[skill].items():
                if supporting_skill in agent.skills:
                    supporting_level = agent.skills[supporting_skill]
                    # Synergy bonus proportional to supporting skill level
                    total_bonus += bonus_rate * supporting_level
        
        return min(0.5, total_bonus)  # Cap synergy bonus at 50%
    
    def _get_development_type_modifier(self, development_type: SkillDevelopmentType) -> float:
        """Get modifier based on development type."""
        modifiers = {
            SkillDevelopmentType.NATURAL_LEARNING: 1.0,
            SkillDevelopmentType.MENTORSHIP: 1.4,
            SkillDevelopmentType.EXPERIENCE_BASED: 1.2,
            SkillDevelopmentType.CRISIS_ACCELERATED: 1.6,
            SkillDevelopmentType.COLLABORATIVE: 1.3,
            SkillDevelopmentType.SELF_STUDY: 0.9,
            SkillDevelopmentType.PRACTICAL_APPLICATION: 1.25,
            SkillDevelopmentType.INNOVATION: 0.8
        }
        
        return modifiers.get(development_type, 1.0)
    
    def _calculate_mentorship_bonus(self, agent: Agent, skill: str) -> float:
        """Calculate mentorship bonus for skill development."""
        # Check for active mentorship relationships
        mentorship_bonus = 0.0
        
        for mentorship in agent.social_network.mentorship_relationships:
            if mentorship.end_turn is None and skill in mentorship.focus_skills:
                # Active mentorship in this skill
                effectiveness = mentorship.effectiveness_score
                mutual_bonus = 0.1 if mentorship.mutual_benefit else 0.0
                skill_bonus = effectiveness * 0.3 + mutual_bonus  # Up to 40% bonus
                mentorship_bonus = max(mentorship_bonus, skill_bonus)
        
        return mentorship_bonus
    
    def develop_skill(self, agent: Agent, skill: str, era: TechnologyEra, turn: int,
                     development_type: SkillDevelopmentType = SkillDevelopmentType.NATURAL_LEARNING,
                     mentor_id: Optional[str] = None) -> Optional[SkillDevelopmentEvent]:
        """Develop a skill for an agent."""
        current_value = agent.skills.get(skill, 0.0)
        
        # Don't develop skills that are already maxed
        if current_value >= 1.0:
            return None
        
        learning_rate, modifiers = self.calculate_learning_rate(agent, skill, era, turn, development_type)
        
        # Calculate skill increase
        base_increase = learning_rate
        
        # Add some randomness (±25%)
        random_factor = random.uniform(0.75, 1.25)
        actual_increase = base_increase * random_factor
        
        new_value = min(1.0, current_value + actual_increase)
        agent.skills[skill] = new_value
        
        # Create development event record
        event = SkillDevelopmentEvent(
            turn=turn,
            agent_id=agent.id,
            skill_name=skill,
            development_type=development_type,
            old_value=current_value,
            new_value=new_value,
            learning_rate=learning_rate,
            modifiers=modifiers,
            context=f"Skill development through {development_type.value}",
            mentor_id=mentor_id
        )
        
        self.development_history.append(event)
        
        # Update agent's skill development rates
        if skill in agent.skill_development_rate:
            # Adjust development rate based on recent performance
            if actual_increase > base_increase:
                agent.skill_development_rate[skill] *= 1.05  # Boost for good performance
            else:
                agent.skill_development_rate[skill] *= 0.98  # Slight penalty for poor performance
        
        return event
    
    def process_turn_development(self, agent: Agent, era: TechnologyEra, turn: int) -> List[SkillDevelopmentEvent]:
        """Process all skill development for an agent in a turn."""
        events = []
        
        # Natural learning for all skills agent has
        for skill in list(agent.skills.keys()):
            if random.random() < 0.3:  # 30% chance per skill per turn
                event = self.develop_skill(agent, skill, era, turn, SkillDevelopmentType.NATURAL_LEARNING)
                if event:
                    events.append(event)
        
        # Mentorship-driven development
        for mentorship in agent.social_network.mentorship_relationships:
            if mentorship.end_turn is None:  # Active mentorship
                for skill in mentorship.focus_skills:
                    if random.random() < 0.6:  # 60% chance for mentored skills
                        event = self.develop_skill(agent, skill, era, turn, 
                                                 SkillDevelopmentType.MENTORSHIP, 
                                                 mentorship.mentor_id)
                        if event:
                            events.append(event)
        
        return events


class AchievementManager(BaseModel):
    """Manages complex achievement systems with prerequisites and chains."""
    
    # Achievement definitions
    achievements: Dict[str, EnhancedAchievement] = Field(default_factory=dict)
    achievement_chains: Dict[str, List[str]] = Field(default_factory=dict)
    era_achievements: Dict[TechnologyEra, List[str]] = Field(default_factory=dict)
    
    # Tracking and statistics
    unlock_statistics: Dict[str, int] = Field(default_factory=dict)
    rarity_calculations: Dict[str, float] = Field(default_factory=dict)
    
    model_config = ConfigDict(use_enum_values=True)
    
    def __init__(self, **data):
        super().__init__(**data)
        self._initialize_achievements()
    
    def _initialize_achievements(self):
        """Initialize the achievement system with complex achievements."""
        self._create_leadership_achievements()
        self._create_skill_mastery_achievements()
        self._create_social_achievements()
        self._create_innovation_achievements()
        self._create_legendary_achievements()
    
    def _create_leadership_achievements(self):
        """Create leadership-focused achievements."""
        # Emerging Leader
        emerging_leader = EnhancedAchievement(
            category=AchievementCategory.LEADERSHIP,
            title="Emerging Leader",
            description="Demonstrated natural leadership abilities among peers",
            era_granted=TechnologyEra.ANCIENT,
            turn_granted=0,
            difficulty=AchievementDifficulty.COMMON,
            skill_requirements={"leadership": 0.5},
            trait_requirements={"charisma": 0.3},
            age_requirements=(20, 40),
            skill_bonuses={"leadership": 0.05, "administration": 0.02},
            reputation_bonus=0.05,
            advisor_potential_bonus=0.1
        )
        self.achievements[emerging_leader.id] = emerging_leader
        
        # Strategic Mastermind
        strategic_mastermind = EnhancedAchievement(
            category=AchievementCategory.LEADERSHIP,
            title="Strategic Mastermind",
            description="Developed exceptional strategic thinking and long-term planning",
            era_granted=TechnologyEra.CLASSICAL,
            turn_granted=0,
            difficulty=AchievementDifficulty.RARE,
            skill_requirements={"leadership": 0.8, "administration": 0.6, "philosophy": 0.5},
            trait_requirements={"strategic_thinking": 0.7, "wisdom": 0.5},
            achievement_prerequisites=[emerging_leader.id],
            skill_bonuses={"leadership": 0.1, "administration": 0.08, "diplomacy": 0.05},
            reputation_bonus=0.15,
            advisor_potential_bonus=0.25,
            achievement_chain="leadership_mastery"
        )
        self.achievements[strategic_mastermind.id] = strategic_mastermind
    
    def _create_skill_mastery_achievements(self):
        """Create skill mastery achievements."""
        # Master Craftsman
        master_craftsman = EnhancedAchievement(
            category=AchievementCategory.ECONOMIC,
            title="Master Craftsman",
            description="Achieved exceptional skill in crafting and creation",
            era_granted=TechnologyEra.ANCIENT,
            turn_granted=0,
            difficulty=AchievementDifficulty.UNCOMMON,
            skill_requirements={"crafting": 0.9},
            trait_requirements={"creativity": 0.4, "precision": 0.5},
            age_requirements=(25, 60),
            skill_bonuses={"crafting": 0.08, "engineering": 0.04, "arts": 0.03},
            reputation_bonus=0.08,
            social_influence_bonus=0.05
        )
        self.achievements[master_craftsman.id] = master_craftsman
        
        # Renaissance Polymath
        renaissance_polymath = EnhancedAchievement(
            category=AchievementCategory.CULTURAL,
            title="Renaissance Polymath",
            description="Mastered multiple disciplines in the spirit of the Renaissance",
            era_granted=TechnologyEra.RENAISSANCE,
            turn_granted=0,
            difficulty=AchievementDifficulty.LEGENDARY,
            skill_requirements={
                "arts": 0.7, "science": 0.7, "engineering": 0.6, 
                "philosophy": 0.6, "innovation": 0.5
            },
            trait_requirements={"curiosity": 0.8, "creativity": 0.7, "intelligence": 0.6},
            era_requirements=[TechnologyEra.RENAISSANCE],
            skill_bonuses={
                "innovation": 0.15, "arts": 0.1, "science": 0.1, 
                "engineering": 0.08, "philosophy": 0.08
            },
            reputation_bonus=0.25,
            advisor_potential_bonus=0.3,
            unique_per_civilization=True
        )
        self.achievements[renaissance_polymath.id] = renaissance_polymath
    
    def _create_social_achievements(self):
        """Create social and relationship-based achievements."""
        # Beloved Mentor
        beloved_mentor = EnhancedAchievement(
            category=AchievementCategory.SOCIAL,
            title="Beloved Mentor",
            description="Guided many protégés to success through wise mentorship",
            era_granted=TechnologyEra.CLASSICAL,
            turn_granted=0,
            difficulty=AchievementDifficulty.RARE,
            skill_requirements={"leadership": 0.6, "philosophy": 0.5},
            trait_requirements={"wisdom": 0.6, "empathy": 0.5, "patience": 0.4},
            social_requirements={"mentorship_effectiveness": 0.8, "protégé_count": 3.0},
            age_requirements=(35, 80),
            skill_bonuses={"leadership": 0.12, "philosophy": 0.08},
            social_influence_bonus=0.15,
            reputation_bonus=0.12
        )
        self.achievements[beloved_mentor.id] = beloved_mentor
    
    def _create_innovation_achievements(self):
        """Create innovation and discovery achievements."""
        # Visionary Innovator
        visionary_innovator = EnhancedAchievement(
            category=AchievementCategory.TECHNOLOGICAL,
            title="Visionary Innovator",
            description="Pioneered groundbreaking innovations that changed society",
            era_granted=TechnologyEra.INDUSTRIAL,
            turn_granted=0,
            difficulty=AchievementDifficulty.LEGENDARY,
            skill_requirements={"innovation": 0.9, "science": 0.7, "engineering": 0.6},
            trait_requirements={"creativity": 0.8, "vision": 0.7, "risk_taking": 0.6},
            era_requirements=[TechnologyEra.INDUSTRIAL, TechnologyEra.MODERN, TechnologyEra.CONTEMPORARY],
            skill_bonuses={"innovation": 0.15, "science": 0.12, "technology": 0.1},
            reputation_bonus=0.3,
            advisor_potential_bonus=0.35,
            prestige_value=0.9
        )
        self.achievements[visionary_innovator.id] = visionary_innovator
    
    def _create_legendary_achievements(self):
        """Create legendary achievements with mythic difficulty."""
        # Immortal Legacy
        immortal_legacy = EnhancedAchievement(
            category=AchievementCategory.LEADERSHIP,
            title="Immortal Legacy",
            description="Created a lasting impact that will be remembered for generations",
            era_granted=TechnologyEra.FUTURE,
            turn_granted=0,
            difficulty=AchievementDifficulty.MYTHIC,
            skill_requirements={
                "leadership": 0.95, "innovation": 0.8, "philosophy": 0.7,
                "administration": 0.8, "diplomacy": 0.7
            },
            trait_requirements={"vision": 0.9, "wisdom": 0.8, "charisma": 0.8},
            social_requirements={"reputation": 0.95, "social_influence": 0.9},
            age_requirements=(40, 70),
            skill_bonuses={skill: 0.2 for skill in ["leadership", "innovation", "philosophy"]},
            reputation_bonus=0.5,
            advisor_potential_bonus=0.5,
            prestige_value=1.0,
            unique_per_civilization=True,
            narrative_significance=1.0
        )
        self.achievements[immortal_legacy.id] = immortal_legacy
    
    def check_achievement_eligibility(self, agent: Agent, achievement: EnhancedAchievement, era: TechnologyEra) -> Tuple[bool, List[str]]:
        """Check if an agent is eligible for a specific achievement."""
        failed_requirements = []
        
        # Check skill requirements
        for skill, required_level in achievement.skill_requirements.items():
            if agent.skills.get(skill, 0.0) < required_level:
                failed_requirements.append(f"Insufficient {skill} ({agent.skills.get(skill, 0.0):.2f} < {required_level:.2f})")
        
        # Check trait requirements
        for trait, required_level in achievement.trait_requirements.items():
            if agent.traits.get(trait, 0.0) < required_level:
                failed_requirements.append(f"Insufficient {trait} ({agent.traits.get(trait, 0.0):.2f} < {required_level:.2f})")
        
        # Check achievement prerequisites
        agent_achievement_ids = [record.achievement.id for record in agent.achievement_history]
        for prereq_id in achievement.achievement_prerequisites:
            if prereq_id not in agent_achievement_ids:
                prereq_achievement = self.achievements.get(prereq_id)
                prereq_title = prereq_achievement.title if prereq_achievement else prereq_id
                failed_requirements.append(f"Missing prerequisite achievement: {prereq_title}")
        
        # Check era requirements
        if achievement.era_requirements:
            # Convert current era to string for comparison
            current_era_str = era.value if hasattr(era, 'value') else str(era)
            
            # Convert requirement eras to strings for comparison
            valid_era_strs = []
            for req_era in achievement.era_requirements:
                if hasattr(req_era, 'value'):
                    valid_era_strs.append(req_era.value)
                else:
                    valid_era_strs.append(str(req_era))
            
            if current_era_str not in valid_era_strs:
                failed_requirements.append(f"Wrong era (current: {current_era_str}, required: {valid_era_strs})")
        
        # Check age requirements
        if achievement.age_requirements:
            min_age, max_age = achievement.age_requirements
            if not (min_age <= agent.age <= max_age):
                failed_requirements.append(f"Age out of range ({agent.age} not in {min_age}-{max_age})")
        
        # Check social requirements
        for social_req, required_level in achievement.social_requirements.items():
            if social_req == "reputation":
                if agent.reputation < required_level:
                    failed_requirements.append(f"Insufficient reputation ({agent.reputation:.2f} < {required_level:.2f})")
            elif social_req == "social_influence":
                if agent.social_network.social_influence_score < required_level:
                    failed_requirements.append(f"Insufficient social influence ({agent.social_network.social_influence_score:.2f} < {required_level:.2f})")
            elif social_req == "mentorship_effectiveness":
                avg_effectiveness = self._calculate_average_mentorship_effectiveness(agent)
                if avg_effectiveness < required_level:
                    failed_requirements.append(f"Insufficient mentorship effectiveness ({avg_effectiveness:.2f} < {required_level:.2f})")
            elif social_req == "protégé_count":
                protégé_count = len([m for m in agent.social_network.mentorship_relationships if m.mentor_id == agent.id])
                if protégé_count < required_level:
                    failed_requirements.append(f"Insufficient protégé count ({protégé_count} < {required_level})")
        
        # Check uniqueness constraints
        if achievement.unique_per_civilization:
            # This would require civilization context - simplified for now
            pass
        
        return len(failed_requirements) == 0, failed_requirements
    
    def _calculate_average_mentorship_effectiveness(self, agent: Agent) -> float:
        """Calculate average mentorship effectiveness for an agent."""
        mentor_relationships = [m for m in agent.social_network.mentorship_relationships if m.mentor_id == agent.id]
        if not mentor_relationships:
            return 0.0
        
        total_effectiveness = sum(m.effectiveness_score for m in mentor_relationships)
        return total_effectiveness / len(mentor_relationships)
    
    def attempt_achievement_unlock(self, agent: Agent, era: TechnologyEra, turn: int) -> List[EnhancedAchievement]:
        """Attempt to unlock achievements for an agent."""
        unlocked_achievements = []
        
        for achievement in self.achievements.values():
            # Skip if already unlocked
            if any(record.achievement.id == achievement.id for record in agent.achievement_history):
                continue
            
            eligible, failed_requirements = self.check_achievement_eligibility(agent, achievement, era)
            
            if eligible:
                # Add achievement to agent's history
                try:
                    from .agent_pool import AchievementRecord
                except ImportError:
                    from political_strategy_game.src.core.agent_pool import AchievementRecord
                
                # Convert EnhancedAchievement to basic Achievement for compatibility
                try:
                    from .citizen import Achievement
                except ImportError:
                    from political_strategy_game.src.core.citizen import Achievement
                
                basic_achievement = Achievement(
                    category=achievement.category,
                    title=achievement.title,
                    description=achievement.description,
                    impact_on_advisor_potential=achievement.advisor_potential_bonus,
                    era_granted=achievement.era_granted,
                    turn_granted=turn  # Use current turn instead of stored turn
                )
                
                achievement_record = AchievementRecord(
                    achievement=basic_achievement,
                    unlock_turn=turn,
                    unlock_circumstances=f"Unlocked through meeting all requirements in {era} era",
                    impact_on_development=achievement.skill_bonuses.copy(),
                    reputation_impact=achievement.reputation_bonus,
                    social_influence_impact=achievement.social_influence_bonus,
                    narrative_significance=achievement.narrative_significance
                )
                
                agent.achievement_history.append(achievement_record)
                
                # Apply achievement effects
                self._apply_achievement_effects(agent, achievement)
                
                # Update statistics
                self.unlock_statistics[achievement.id] = self.unlock_statistics.get(achievement.id, 0) + 1
                
                unlocked_achievements.append(achievement)
        
        return unlocked_achievements
    
    def _apply_achievement_effects(self, agent: Agent, achievement: EnhancedAchievement):
        """Apply the effects of an unlocked achievement to an agent."""
        # Apply skill bonuses
        for skill, bonus in achievement.skill_bonuses.items():
            if skill in agent.skills:
                agent.skills[skill] = min(1.0, agent.skills[skill] + bonus)
            else:
                agent.skills[skill] = bonus
        
        # Apply trait bonuses
        for trait, bonus in achievement.trait_bonuses.items():
            if trait in agent.traits:
                agent.traits[trait] = max(-1.0, min(1.0, agent.traits[trait] + bonus))
            else:
                agent.traits[trait] = bonus
        
        # Apply other bonuses
        agent.reputation = min(1.0, agent.reputation + achievement.reputation_bonus)
        agent.social_network.social_influence_score = min(1.0, 
            agent.social_network.social_influence_score + achievement.social_influence_bonus)
        agent.advisor_potential = min(1.0, agent.advisor_potential + achievement.advisor_potential_bonus)
    
    def calculate_achievement_rarity(self, achievement_id: str, total_eligible_agents: int) -> float:
        """Calculate the rarity of an achievement based on unlock statistics."""
        unlock_count = self.unlock_statistics.get(achievement_id, 0)
        
        if total_eligible_agents == 0:
            return 1.0
        
        rarity = 1.0 - (unlock_count / total_eligible_agents)
        self.rarity_calculations[achievement_id] = rarity
        return rarity


def create_skill_development_manager() -> SkillDevelopmentManager:
    """Factory function to create a skill development manager."""
    return SkillDevelopmentManager()


def create_achievement_manager() -> AchievementManager:
    """Factory function to create an achievement manager."""
    return AchievementManager()


# Day 3: Advanced Lifecycle Management Classes

class AdvancedLifecycleManager(BaseModel):
    """Manages sophisticated agent lifecycle including aging, retirement, and succession."""
    
    # Lifecycle configuration
    lifecycle_stage_thresholds: Dict[LifecycleStage, Tuple[int, int]] = Field(default_factory=dict)
    aging_effects: Dict[str, Dict[LifecycleStage, float]] = Field(default_factory=dict)
    retirement_probability_curves: Dict[LifecycleStage, float] = Field(default_factory=dict)
    
    # Event tracking
    lifecycle_events: List[LifecycleEvent] = Field(default_factory=list)
    major_life_transitions: Dict[str, List[LifecycleEvent]] = Field(default_factory=dict)
    
    # Succession management
    succession_plans: Dict[str, SuccessionPlan] = Field(default_factory=dict)
    succession_readiness_criteria: Dict[str, float] = Field(default_factory=dict)
    
    model_config = ConfigDict(use_enum_values=True)
    
    def __init__(self, **data):
        super().__init__(**data)
        self._initialize_lifecycle_configurations()
    
    def _initialize_lifecycle_configurations(self):
        """Initialize default lifecycle configurations."""
        # Define age ranges for lifecycle stages
        self.lifecycle_stage_thresholds = {
            LifecycleStage.EMERGING: (18, 25),
            LifecycleStage.DEVELOPING: (26, 35),
            LifecycleStage.PRIME: (36, 50),
            LifecycleStage.MATURE: (51, 65),
            LifecycleStage.ELDER: (66, 80),
            LifecycleStage.DECLINING: (81, 120)
        }
        
        # Define aging effects on different attributes
        self.aging_effects = {
            "physical_skills": {
                LifecycleStage.EMERGING: 0.95,    # Still developing
                LifecycleStage.DEVELOPING: 1.0,   # Peak physical
                LifecycleStage.PRIME: 0.98,       # Slight decline
                LifecycleStage.MATURE: 0.92,      # Noticeable decline
                LifecycleStage.ELDER: 0.85,       # Significant decline
                LifecycleStage.DECLINING: 0.75    # Major decline
            },
            "mental_skills": {
                LifecycleStage.EMERGING: 0.90,    # Still learning
                LifecycleStage.DEVELOPING: 0.98,  # Good capability
                LifecycleStage.PRIME: 1.0,        # Peak mental
                LifecycleStage.MATURE: 1.02,      # Experience bonus
                LifecycleStage.ELDER: 1.0,        # Wisdom peak
                LifecycleStage.DECLINING: 0.90    # Some decline
            },
            "wisdom_skills": {
                LifecycleStage.EMERGING: 0.70,    # Limited wisdom
                LifecycleStage.DEVELOPING: 0.85,  # Growing wisdom
                LifecycleStage.PRIME: 0.95,       # Good wisdom
                LifecycleStage.MATURE: 1.05,      # High wisdom
                LifecycleStage.ELDER: 1.10,       # Peak wisdom
                LifecycleStage.DECLINING: 1.05    # Retained wisdom
            },
            "learning_rate": {
                LifecycleStage.EMERGING: 1.20,    # Fast learning
                LifecycleStage.DEVELOPING: 1.10,  # Good learning
                LifecycleStage.PRIME: 1.0,        # Normal learning
                LifecycleStage.MATURE: 0.85,      # Slower learning
                LifecycleStage.ELDER: 0.70,       # Much slower
                LifecycleStage.DECLINING: 0.50    # Very slow
            }
        }
        
        # Retirement probability by lifecycle stage
        self.retirement_probability_curves = {
            LifecycleStage.EMERGING: 0.001,      # Very unlikely
            LifecycleStage.DEVELOPING: 0.002,    # Extremely rare
            LifecycleStage.PRIME: 0.005,         # Rare
            LifecycleStage.MATURE: 0.02,         # Possible
            LifecycleStage.ELDER: 0.15,          # Likely
            LifecycleStage.DECLINING: 0.40       # Very likely
        }
        
        # Succession readiness criteria
        self.succession_readiness_criteria = {
            "skill_threshold": 0.7,       # Minimum skill level for succession
            "experience_years": 5,        # Minimum years of experience
            "reputation_threshold": 0.6,  # Minimum reputation score
            "mentorship_bonus": 0.2,      # Bonus for being mentored
            "relationship_strength": 0.5  # Minimum relationship with mentor
        }
    
    def determine_lifecycle_stage(self, agent: Agent) -> LifecycleStage:
        """Determine the current lifecycle stage of an agent."""
        for stage, (min_age, max_age) in self.lifecycle_stage_thresholds.items():
            if min_age <= agent.age <= max_age:
                return stage
        return LifecycleStage.DECLINING  # Fallback for very old agents
    
    def apply_aging_effects(self, agent: Agent, stage: LifecycleStage) -> Dict[str, float]:
        """Apply aging effects to an agent's capabilities."""
        effects_applied = {}
        
        # Apply physical skill aging
        physical_skills = ["combat", "crafting", "engineering", "exploration"]
        physical_modifier = self.aging_effects["physical_skills"][stage]
        for skill in physical_skills:
            if skill in agent.skills:
                old_value = agent.skills[skill]
                agent.skills[skill] *= physical_modifier
                effects_applied[f"{skill}_aging"] = agent.skills[skill] - old_value
        
        # Apply mental skill aging
        mental_skills = ["scholarship", "science", "technology", "innovation"]
        mental_modifier = self.aging_effects["mental_skills"][stage]
        for skill in mental_skills:
            if skill in agent.skills:
                old_value = agent.skills[skill]
                agent.skills[skill] *= mental_modifier
                effects_applied[f"{skill}_aging"] = agent.skills[skill] - old_value
        
        # Apply wisdom skill aging
        wisdom_skills = ["leadership", "philosophy", "administration", "diplomacy"]
        wisdom_modifier = self.aging_effects["wisdom_skills"][stage]
        for skill in wisdom_skills:
            if skill in agent.skills:
                old_value = agent.skills[skill]
                agent.skills[skill] *= wisdom_modifier
                effects_applied[f"{skill}_aging"] = agent.skills[skill] - old_value
        
        return effects_applied
    
    def calculate_retirement_probability(self, agent: Agent, stage: LifecycleStage) -> float:
        """Calculate probability of agent retirement."""
        base_probability = self.retirement_probability_curves[stage]
        
        # Modifiers based on agent characteristics
        modifiers = 1.0
        
        # Health and vigor (inverse of age effect)
        if "health" in agent.traits:
            health_modifier = 1.0 - (agent.traits["health"] * 0.3)  # Better health = less likely to retire
            modifiers *= health_modifier
        
        # Passion for work
        if "dedication" in agent.traits:
            dedication_modifier = 1.0 - (agent.traits["dedication"] * 0.4)
            modifiers *= dedication_modifier
        
        # Financial security (higher reputation = more secure = more likely to retire)
        reputation_modifier = 1.0 + (agent.reputation * 0.2)
        modifiers *= reputation_modifier
        
        # Family considerations (random factor)
        family_modifier = random.uniform(0.8, 1.2)
        modifiers *= family_modifier
        
        return min(0.8, base_probability * modifiers)
    
    def create_succession_plan(self, mentor: Agent, potential_successors: List[Agent], 
                             succession_type: SuccessionType = SuccessionType.COMPETITIVE_SELECTION) -> SuccessionPlan:
        """Create a succession plan for an agent."""
        readiness_scores = {}
        
        for successor in potential_successors:
            readiness_score = self._calculate_succession_readiness(mentor, successor)
            readiness_scores[successor.id] = readiness_score
        
        # Sort successors by readiness
        sorted_successors = sorted(readiness_scores.keys(), 
                                 key=lambda x: readiness_scores[x], reverse=True)
        
        # Create knowledge transfer plan
        knowledge_transfer_plan = self._create_knowledge_transfer_plan(mentor, potential_successors)
        
        succession_plan = SuccessionPlan(
            mentor_id=mentor.id,
            potential_successors=sorted_successors,
            succession_type=succession_type,
            readiness_scores=readiness_scores,
            preparation_activities=self._generate_preparation_activities(mentor),
            knowledge_transfer_plan=knowledge_transfer_plan,
            timeline=self._estimate_succession_timeline(mentor),
            contingency_plans=self._create_contingency_plans(mentor, potential_successors),
            cultural_considerations=self._identify_cultural_considerations(mentor)
        )
        
        self.succession_plans[mentor.id] = succession_plan
        return succession_plan
    
    def _calculate_succession_readiness(self, mentor: Agent, successor: Agent) -> float:
        """Calculate how ready a successor is to take over."""
        readiness_factors = {}
        
        # Skill similarity and competence
        skill_readiness = 0.0
        relevant_skills = 0
        for skill, mentor_level in mentor.skills.items():
            if mentor_level > 0.3:  # Only consider skills mentor is competent in
                successor_level = successor.skills.get(skill, 0.0)
                skill_ratio = min(1.0, successor_level / max(0.1, mentor_level))
                skill_readiness += skill_ratio
                relevant_skills += 1
        
        if relevant_skills > 0:
            readiness_factors["skill_competence"] = skill_readiness / relevant_skills
        else:
            readiness_factors["skill_competence"] = 0.0
        
        # Experience factor (age proxy)
        min_experience_age = 30
        experience_factor = min(1.0, max(0.0, (successor.age - 18) / (min_experience_age - 18)))
        readiness_factors["experience"] = experience_factor
        
        # Reputation and social standing
        reputation_factor = successor.reputation
        readiness_factors["reputation"] = reputation_factor
        
        # Relationship with mentor (check for mentorship relationships)
        relationship_strength = 0.5  # Default
        if hasattr(successor, 'social_network') and hasattr(successor.social_network, 'mentorship_relationships'):
            for record in successor.social_network.mentorship_relationships:
                if record.mentor_id == mentor.id:
                    relationship_strength = record.effectiveness_score
                    break
        
        # Alternative: check enhanced relationships
        if hasattr(successor, 'social_network') and hasattr(successor.social_network, 'relationships'):
            if mentor.id in successor.social_network.relationships:
                rel = successor.social_network.relationships[mentor.id]
                if hasattr(rel, 'strength'):
                    relationship_strength = rel.strength
                elif isinstance(rel, (int, float)):
                    relationship_strength = rel
                    
        readiness_factors["mentorship_bond"] = relationship_strength
        
        # Leadership traits
        leadership_traits = ["leadership", "charisma", "wisdom", "integrity"]
        leadership_score = 0.0
        for trait in leadership_traits:
            if trait in successor.traits:
                leadership_score += successor.traits[trait]
        leadership_score /= len(leadership_traits)
        readiness_factors["leadership_potential"] = leadership_score
        
        # Calculate weighted average
        weights = {
            "skill_competence": 0.35,
            "experience": 0.20,
            "reputation": 0.15,
            "mentorship_bond": 0.15,
            "leadership_potential": 0.15
        }
        
        total_readiness = sum(readiness_factors[factor] * weights[factor] 
                            for factor in weights if factor in readiness_factors)
        
        return total_readiness
    
    def _create_knowledge_transfer_plan(self, mentor: Agent, successors: List[Agent]) -> Dict[str, List[str]]:
        """Create a plan for transferring knowledge to successors."""
        transfer_plan = {}
        
        # Identify mentor's key skills
        key_skills = {skill: level for skill, level in mentor.skills.items() if level > 0.5}
        
        for skill, level in key_skills.items():
            activities = []
            
            if level > 0.8:
                activities.extend([
                    f"Advanced {skill} workshops",
                    f"Real-world {skill} project leadership",
                    f"Complex {skill} problem-solving sessions"
                ])
            elif level > 0.6:
                activities.extend([
                    f"Intermediate {skill} training",
                    f"Supervised {skill} practice",
                    f"{skill} case study analysis"
                ])
            else:
                activities.extend([
                    f"Basic {skill} instruction",
                    f"Guided {skill} exercises",
                    f"{skill} fundamentals review"
                ])
            
            transfer_plan[skill] = activities
        
        return transfer_plan
    
    def _generate_preparation_activities(self, mentor: Agent) -> List[str]:
        """Generate preparation activities for succession."""
        activities = [
            "Document key processes and procedures",
            "Identify critical relationships and contacts",
            "Transfer institutional knowledge",
            "Review major decisions and rationale",
            "Prepare succession timeline and milestones"
        ]
        
        # Add role-specific activities based on mentor's strengths
        if mentor.skills.get("leadership", 0) > 0.7:
            activities.append("Leadership transition planning")
        if mentor.skills.get("diplomacy", 0) > 0.7:
            activities.append("Diplomatic relationship transfer")
        if mentor.skills.get("administration", 0) > 0.7:
            activities.append("Administrative system documentation")
        
        return activities
    
    def _estimate_succession_timeline(self, mentor: Agent) -> int:
        """Estimate timeline for succession preparation."""
        stage = self.determine_lifecycle_stage(mentor)
        
        # Base timeline by lifecycle stage
        base_timelines = {
            LifecycleStage.EMERGING: 20,     # Long preparation time
            LifecycleStage.DEVELOPING: 15,   # Moderate preparation
            LifecycleStage.PRIME: 10,        # Normal preparation
            LifecycleStage.MATURE: 8,        # Shorter preparation
            LifecycleStage.ELDER: 5,         # Urgent preparation
            LifecycleStage.DECLINING: 3      # Emergency preparation
        }
        
        return base_timelines.get(stage, 10)
    
    def _create_contingency_plans(self, mentor: Agent, successors: List[Agent]) -> List[str]:
        """Create contingency plans for succession."""
        plans = [
            "Emergency succession protocol",
            "Interim leadership arrangement",
            "Knowledge preservation measures",
            "Stakeholder communication plan"
        ]
        
        if len(successors) > 1:
            plans.append("Competitive selection process")
        else:
            plans.append("Single successor intensive preparation")
        
        return plans
    
    def _identify_cultural_considerations(self, mentor: Agent) -> List[str]:
        """Identify cultural considerations for succession."""
        considerations = [
            "Traditional succession customs",
            "Cultural leadership expectations",
            "Community acceptance factors",
            "Religious or spiritual considerations"
        ]
        
        # Add era-specific considerations
        if hasattr(mentor, 'era_born'):
            if mentor.era_born in ["ancient", "classical"]:
                considerations.append("Bloodline and family honor traditions")
            elif mentor.era_born in ["medieval", "renaissance"]:
                considerations.append("Guild and craft traditions")
            elif mentor.era_born in ["industrial", "modern"]:
                considerations.append("Meritocratic selection expectations")
        
        return considerations
    
    def process_lifecycle_events(self, agent: Agent, turn: int) -> List[LifecycleEvent]:
        """Process lifecycle events for an agent."""
        events = []
        current_stage = self.determine_lifecycle_stage(agent)
        
        # Check for stage transitions
        if hasattr(agent, '_last_lifecycle_stage'):
            if agent._last_lifecycle_stage != current_stage:
                transition_event = LifecycleEvent(
                    turn=turn,
                    agent_id=agent.id,
                    event_type="lifecycle_transition",
                    description=f"Transitioned from {agent._last_lifecycle_stage} to {current_stage}",
                    impact_areas=["all_skills", "learning_rate", "social_standing"],
                    magnitude=0.1,  # Generally positive as it represents growth
                    narrative_weight=0.7,
                    triggers=[f"age_{agent.age}"],
                    consequences=[f"new_capabilities_{current_stage}", f"changed_social_role"]
                )
                events.append(transition_event)
                self.lifecycle_events.append(transition_event)
        
        agent._last_lifecycle_stage = current_stage
        
        # Apply aging effects
        aging_effects = self.apply_aging_effects(agent, current_stage)
        if aging_effects:
            aging_event = LifecycleEvent(
                turn=turn,
                agent_id=agent.id,
                event_type="aging_effects",
                description=f"Applied aging effects for {current_stage} stage",
                impact_areas=list(aging_effects.keys()),
                magnitude=sum(aging_effects.values()) / len(aging_effects) if aging_effects else 0.0,
                narrative_weight=0.3,
                triggers=[f"lifecycle_stage_{current_stage}"],
                consequences=["capability_changes", "role_adaptation"]
            )
            events.append(aging_event)
            self.lifecycle_events.append(aging_event)
        
        # Check for retirement
        retirement_prob = self.calculate_retirement_probability(agent, current_stage)
        if random.random() < retirement_prob:
            retirement_event = LifecycleEvent(
                turn=turn,
                agent_id=agent.id,
                event_type="retirement_consideration",
                description=f"Agent considering retirement (probability: {retirement_prob:.2f})",
                impact_areas=["career_planning", "succession_planning"],
                magnitude=-0.2,  # Negative as it represents ending of active career
                narrative_weight=0.9,
                triggers=[f"age_{agent.age}", f"stage_{current_stage}"],
                consequences=["succession_planning", "legacy_preparation"]
            )
            events.append(retirement_event)
            self.lifecycle_events.append(retirement_event)
        
        return events


class ReputationManager(BaseModel):
    """Manages sophisticated reputation and influence systems."""
    
    # Reputation tracking
    reputation_records: List[ReputationRecord] = Field(default_factory=list)
    reputation_decay_rates: Dict[ReputationDimension, float] = Field(default_factory=dict)
    reputation_weights: Dict[ReputationDimension, float] = Field(default_factory=dict)
    
    # Influence tracking
    influence_events: List[SocialInfluenceEvent] = Field(default_factory=list)
    influence_networks: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    
    model_config = ConfigDict(use_enum_values=True)
    
    def __init__(self, **data):
        super().__init__(**data)
        self._initialize_reputation_system()
    
    def _initialize_reputation_system(self):
        """Initialize reputation system parameters."""
        # Decay rates for different reputation dimensions
        self.reputation_decay_rates = {
            ReputationDimension.COMPETENCE: 0.02,     # Slow decay - skills are observable
            ReputationDimension.INTEGRITY: 0.005,    # Very slow decay - fundamental character
            ReputationDimension.INNOVATION: 0.03,    # Moderate decay - "what have you done lately"
            ReputationDimension.LEADERSHIP: 0.015,   # Slow decay - leadership is remembered
            ReputationDimension.WISDOM: 0.001,       # Extremely slow decay - wisdom grows with age
            ReputationDimension.CHARISMA: 0.025,     # Moderate decay - requires ongoing demonstration
            ReputationDimension.RELIABILITY: 0.01,   # Slow decay - reliability builds over time
            ReputationDimension.VISION: 0.02         # Moderate decay - vision must be updated
        }
        
        # Weights for overall reputation calculation
        self.reputation_weights = {
            ReputationDimension.COMPETENCE: 0.20,
            ReputationDimension.INTEGRITY: 0.18,
            ReputationDimension.INNOVATION: 0.12,
            ReputationDimension.LEADERSHIP: 0.15,
            ReputationDimension.WISDOM: 0.13,
            ReputationDimension.CHARISMA: 0.10,
            ReputationDimension.RELIABILITY: 0.08,
            ReputationDimension.VISION: 0.04
        }
    
    def update_reputation(self, agent: Agent, dimension: ReputationDimension, 
                         change: float, reason: str, witnesses: List[str] = None,
                         public_awareness: float = 0.5, turn: int = 0) -> float:
        """Update an agent's reputation in a specific dimension."""
        # Use private attribute to store reputation dimensions to avoid Pydantic validation
        if not hasattr(agent, '_reputation_dimensions'):
            agent._reputation_dimensions = {dim: 0.5 for dim in ReputationDimension}
        
        old_value = agent._reputation_dimensions.get(dimension, 0.5)
        new_value = max(0.0, min(1.0, old_value + change))
        agent._reputation_dimensions[dimension] = new_value
        
        # Record the reputation change
        record = ReputationRecord(
            turn=turn,
            agent_id=agent.id,
            dimension=dimension,
            old_value=old_value,
            new_value=new_value,
            change_reason=reason,
            witnesses=witnesses or [],
            public_awareness=public_awareness,
            decay_rate=self.reputation_decay_rates[dimension]
        )
        self.reputation_records.append(record)
        
        # Update overall reputation
        agent.reputation = self._calculate_overall_reputation(agent)
        
        return new_value
    
    def _calculate_overall_reputation(self, agent: Agent) -> float:
        """Calculate overall reputation from dimensional scores."""
        if not hasattr(agent, '_reputation_dimensions'):
            return agent.reputation
        
        weighted_sum = sum(agent._reputation_dimensions.get(dim, 0.5) * weight 
                          for dim, weight in self.reputation_weights.items())
        
        return weighted_sum
    
    def apply_reputation_decay(self, agent: Agent, turn: int) -> Dict[ReputationDimension, float]:
        """Apply natural reputation decay over time."""
        if not hasattr(agent, '_reputation_dimensions'):
            agent._reputation_dimensions = {dim: 0.5 for dim in ReputationDimension}
        
        decay_applied = {}
        
        for dimension, current_value in agent._reputation_dimensions.items():
            decay_rate = self.reputation_decay_rates[dimension]
            
            # Decay towards neutral (0.5) rather than zero
            if current_value > 0.5:
                decay_amount = (current_value - 0.5) * decay_rate
                new_value = current_value - decay_amount
            elif current_value < 0.5:
                decay_amount = (0.5 - current_value) * decay_rate
                new_value = current_value + decay_amount
            else:
                new_value = current_value
            
            agent._reputation_dimensions[dimension] = new_value
            decay_applied[dimension] = new_value - current_value
        
        # Update overall reputation
        agent.reputation = self._calculate_overall_reputation(agent)
        
        return decay_applied
    
    def calculate_social_influence(self, influencer: Agent, target: Agent, 
                                 influence_type: SocialInfluenceType) -> float:
        """Calculate the social influence one agent has over another."""
        influence_factors = {}
        
        # Base influence from reputation dimensions
        if hasattr(influencer, '_reputation_dimensions'):
            if influence_type == SocialInfluenceType.EXPERTISE:
                influence_factors["competence"] = influencer._reputation_dimensions.get(ReputationDimension.COMPETENCE, 0.5)
                influence_factors["innovation"] = influencer._reputation_dimensions.get(ReputationDimension.INNOVATION, 0.5)
            elif influence_type == SocialInfluenceType.PERSONAL_CHARM:
                influence_factors["charisma"] = influencer._reputation_dimensions.get(ReputationDimension.CHARISMA, 0.5)
                influence_factors["integrity"] = influencer._reputation_dimensions.get(ReputationDimension.INTEGRITY, 0.5)
            elif influence_type == SocialInfluenceType.FORMAL_AUTHORITY:
                influence_factors["leadership"] = influencer._reputation_dimensions.get(ReputationDimension.LEADERSHIP, 0.5)
                influence_factors["reliability"] = influencer._reputation_dimensions.get(ReputationDimension.RELIABILITY, 0.5)
            else:
                # General influence
                influence_factors["overall_reputation"] = influencer.reputation
        else:
            # Fallback to overall reputation
            influence_factors["overall_reputation"] = influencer.reputation
        
        # Relationship strength modifier
        relationship_strength = 0.5  # Default neutral
        if hasattr(target, 'social_network') and hasattr(target.social_network, 'relationships'):
            if influencer.id in target.social_network.relationships:
                rel = target.social_network.relationships[influencer.id]
                if hasattr(rel, 'strength'):
                    relationship_strength = rel.strength
                elif isinstance(rel, (int, float)):
                    relationship_strength = rel
        influence_factors["relationship"] = relationship_strength
        
        # Skill differential (expert influence)
        if influence_type == SocialInfluenceType.EXPERTISE:
            relevant_skills = ["scholarship", "science", "technology", "innovation"]
            skill_advantage = 0.0
            for skill in relevant_skills:
                influencer_skill = influencer.skills.get(skill, 0.0)
                target_skill = target.skills.get(skill, 0.0)
                skill_advantage += max(0.0, influencer_skill - target_skill)
            influence_factors["skill_advantage"] = min(1.0, skill_advantage / len(relevant_skills))
        
        # Age and experience factors
        age_difference = influencer.age - target.age
        if age_difference > 10:
            influence_factors["experience_advantage"] = min(0.3, age_difference / 50)
        elif age_difference < -10:
            influence_factors["youth_energy"] = min(0.2, abs(age_difference) / 30)
        
        # Calculate weighted influence score
        weights = {
            "competence": 0.20,
            "innovation": 0.15,
            "charisma": 0.20,
            "integrity": 0.15,
            "leadership": 0.20,
            "reliability": 0.10,
            "overall_reputation": 0.25,
            "relationship": 0.30,
            "skill_advantage": 0.20,
            "experience_advantage": 0.15,
            "youth_energy": 0.10
        }
        
        total_influence = 0.0
        total_weight = 0.0
        
        for factor, value in influence_factors.items():
            if factor in weights:
                total_influence += value * weights[factor]
                total_weight += weights[factor]
        
        if total_weight > 0:
            return total_influence / total_weight
        else:
            return 0.5
    
    def record_influence_event(self, influencer: Agent, targets: List[Agent], 
                             influence_type: SocialInfluenceType, context: str,
                             turn: int) -> SocialInfluenceEvent:
        """Record a social influence event."""
        target_ids = [target.id for target in targets]
        
        # Calculate average influence and success rate
        total_influence = 0.0
        for target in targets:
            influence_score = self.calculate_social_influence(influencer, target, influence_type)
            total_influence += influence_score
        
        average_influence = total_influence / len(targets) if targets else 0.0
        success_rate = min(1.0, average_influence * 1.2)  # Slight boost for success calculation
        
        # Create influence event
        event = SocialInfluenceEvent(
            turn=turn,
            influencer_id=influencer.id,
            target_ids=target_ids,
            influence_type=influence_type,
            success_rate=success_rate,
            magnitude=average_influence,
            context=context,
            resistance_factors=self._identify_resistance_factors(influencer, targets),
            amplification_factors=self._identify_amplification_factors(influencer, targets)
        )
        
        self.influence_events.append(event)
        return event
    
    def _identify_resistance_factors(self, influencer: Agent, targets: List[Agent]) -> List[str]:
        """Identify factors that might resist influence."""
        resistance_factors = []
        
        for target in targets:
            # Strong personality traits that resist influence
            if target.traits.get("independence", 0) > 0.7:
                resistance_factors.append("high_independence")
            if target.traits.get("skepticism", 0) > 0.7:
                resistance_factors.append("high_skepticism")
            if target.traits.get("stubbornness", 0) > 0.7:
                resistance_factors.append("stubbornness")
            
            # Negative relationships
            relationship_strength = 0.5
            if hasattr(target, 'social_network') and hasattr(target.social_network, 'relationships'):
                relationship_strength = target.social_network.relationships.get(influencer.id, 0.5)
            
            if relationship_strength < 0.3:
                resistance_factors.append("poor_relationship")
            
            # Competing loyalties
            if hasattr(target, 'social_network') and hasattr(target.social_network, 'mentorship_relationships'):
                for record in target.social_network.mentorship_relationships:
                    if record.mentor_id != influencer.id and record.relationship_strength > 0.7:
                        resistance_factors.append("competing_mentor_loyalty")
        
        return list(set(resistance_factors))  # Remove duplicates
    
    def _identify_amplification_factors(self, influencer: Agent, targets: List[Agent]) -> List[str]:
        """Identify factors that might amplify influence."""
        amplification_factors = []
        
        # Influencer characteristics that amplify influence
        if influencer.reputation > 0.8:
            amplification_factors.append("high_reputation")
        if influencer.skills.get("charisma", 0) > 0.8:
            amplification_factors.append("exceptional_charisma")
        if influencer.skills.get("leadership", 0) > 0.8:
            amplification_factors.append("strong_leadership")
        
        for target in targets:
            # Target characteristics that make them more susceptible
            if target.traits.get("openness", 0) > 0.7:
                amplification_factors.append("target_openness")
            if target.age < 25:
                amplification_factors.append("youth_impressionability")
            
            # Strong positive relationships
            relationship_strength = 0.5
            if hasattr(target, 'social_network') and hasattr(target.social_network, 'relationships'):
                relationship_strength = target.social_network.relationships.get(influencer.id, 0.5)
            
            if relationship_strength > 0.8:
                amplification_factors.append("strong_relationship")
            
            # Mentorship relationships
            if hasattr(target, 'social_network') and hasattr(target.social_network, 'mentorship_relationships'):
                for record in target.social_network.mentorship_relationships:
                    if record.mentor_id == influencer.id and record.relationship_strength > 0.7:
                        amplification_factors.append("mentorship_bond")
        
        return list(set(amplification_factors))  # Remove duplicates


class SocialDynamicsManager(BaseModel):
    """Manages complex social network dynamics and relationship evolution."""
    
    # Relationship tracking
    relationship_dynamics: Dict[str, RelationshipDynamics] = Field(default_factory=dict)
    interaction_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Network analysis
    network_metrics: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    influence_cascades: List[Dict[str, Any]] = Field(default_factory=list)
    
    model_config = ConfigDict(use_enum_values=True)
    
    def create_relationship_dynamics(self, agent_a: Agent, agent_b: Agent) -> RelationshipDynamics:
        """Create or update relationship dynamics between two agents."""
        pair_key = self._get_relationship_key(agent_a.id, agent_b.id)
        
        # Get current relationship strength
        current_strength = 0.5  # Default neutral
        if hasattr(agent_a, 'social_network') and hasattr(agent_a.social_network, 'relationships'):
            current_strength = agent_a.social_network.relationships.get(agent_b.id, 0.5)
        
        dynamics = RelationshipDynamics(
            agent_a_id=agent_a.id,
            agent_b_id=agent_b.id,
            current_strength=current_strength,
            evolution_trend=RelationshipEvolution.STABLE,
            interaction_frequency=self._calculate_interaction_frequency(agent_a, agent_b),
            shared_experiences=[],
            conflict_history=[],
            mutual_benefits=[],
            influence_balance=self._calculate_influence_balance(agent_a, agent_b),
            trust_level=current_strength,  # Start with relationship strength
            respect_level=self._calculate_initial_respect(agent_a, agent_b),
            dependency_level=self._calculate_dependency(agent_a, agent_b)
        )
        
        self.relationship_dynamics[pair_key] = dynamics
        return dynamics
    
    def _get_relationship_key(self, agent_a_id: str, agent_b_id: str) -> str:
        """Generate a consistent key for relationship pairs."""
        return f"{min(agent_a_id, agent_b_id)}_{max(agent_a_id, agent_b_id)}"
    
    def _calculate_interaction_frequency(self, agent_a: Agent, agent_b: Agent) -> float:
        """Calculate how frequently two agents interact."""
        frequency_factors = 0.0
        
        # Similar roles and skills increase interaction
        skill_similarity = self._calculate_skill_similarity(agent_a, agent_b)
        frequency_factors += skill_similarity * 0.3
        
        # Age proximity increases interaction
        age_difference = abs(agent_a.age - agent_b.age)
        age_factor = max(0.0, 1.0 - (age_difference / 30))  # Decreases as age gap increases
        frequency_factors += age_factor * 0.2
        
        # Similar traits increase interaction
        trait_similarity = self._calculate_trait_similarity(agent_a, agent_b)
        frequency_factors += trait_similarity * 0.3
        
        # Mentorship relationships increase interaction
        if hasattr(agent_a, 'social_network') and hasattr(agent_a.social_network, 'mentorship_relationships'):
            for record in agent_a.social_network.mentorship_relationships:
                if record.mentor_id == agent_b.id or record.mentee_id == agent_b.id:
                    frequency_factors += 0.4
                    break
        
        # Random factor for unpredictable interactions
        random_factor = random.uniform(0.0, 0.2)
        frequency_factors += random_factor
        
        return min(1.0, frequency_factors)
    
    def _calculate_skill_similarity(self, agent_a: Agent, agent_b: Agent) -> float:
        """Calculate skill similarity between agents."""
        all_skills = set(agent_a.skills.keys()) | set(agent_b.skills.keys())
        if not all_skills:
            return 0.0
        
        similarity_sum = 0.0
        for skill in all_skills:
            level_a = agent_a.skills.get(skill, 0.0)
            level_b = agent_b.skills.get(skill, 0.0)
            similarity_sum += 1.0 - abs(level_a - level_b)
        
        return similarity_sum / len(all_skills)
    
    def _calculate_trait_similarity(self, agent_a: Agent, agent_b: Agent) -> float:
        """Calculate trait similarity between agents."""
        all_traits = set(agent_a.traits.keys()) | set(agent_b.traits.keys())
        if not all_traits:
            return 0.0
        
        similarity_sum = 0.0
        for trait in all_traits:
            level_a = agent_a.traits.get(trait, 0.0)
            level_b = agent_b.traits.get(trait, 0.0)
            similarity_sum += 1.0 - abs(level_a - level_b)
        
        return similarity_sum / len(all_traits)
    
    def _calculate_influence_balance(self, agent_a: Agent, agent_b: Agent) -> float:
        """Calculate the balance of influence between agents (-1 to 1)."""
        factors_a = agent_a.reputation + agent_a.advisor_potential + agent_a.age / 100
        factors_b = agent_b.reputation + agent_b.advisor_potential + agent_b.age / 100
        
        total_factors = factors_a + factors_b
        if total_factors == 0:
            return 0.0
        
        # Return -1 to 1, where negative means A has more influence, positive means B has more
        return (factors_b - factors_a) / max(factors_a, factors_b, 1.0)
    
    def _calculate_initial_respect(self, agent_a: Agent, agent_b: Agent) -> float:
        """Calculate initial respect level between agents."""
        respect_factors = []
        
        # Respect for competence
        competence_difference = agent_b.reputation - agent_a.reputation
        if competence_difference > 0:
            respect_factors.append(0.5 + min(0.4, competence_difference))
        else:
            respect_factors.append(0.5 + max(-0.3, competence_difference))
        
        # Respect for age and experience
        age_difference = agent_b.age - agent_a.age
        if age_difference > 5:
            respect_factors.append(0.5 + min(0.3, age_difference / 20))
        else:
            respect_factors.append(0.5)
        
        # Respect for similar values (trait alignment)
        trait_alignment = self._calculate_trait_similarity(agent_a, agent_b)
        respect_factors.append(0.3 + trait_alignment * 0.4)
        
        return sum(respect_factors) / len(respect_factors)
    
    def _calculate_dependency(self, agent_a: Agent, agent_b: Agent) -> float:
        """Calculate how dependent agent A is on agent B."""
        dependency_factors = []
        
        # Skill complementarity
        complementary_skills = 0.0
        for skill, level_a in agent_a.skills.items():
            level_b = agent_b.skills.get(skill, 0.0)
            if level_b > level_a + 0.2:  # B is significantly better at this skill
                complementary_skills += (level_b - level_a)
        dependency_factors.append(min(1.0, complementary_skills))
        
        # Mentorship dependency
        mentorship_dependency = 0.0
        if hasattr(agent_a, 'social_network') and hasattr(agent_a.social_network, 'mentorship_relationships'):
            for record in agent_a.social_network.mentorship_relationships:
                if record.mentor_id == agent_b.id:
                    mentorship_dependency = record.relationship_strength * 0.8
                    break
        dependency_factors.append(mentorship_dependency)
        
        # Experience dependency (younger depending on older)
        age_difference = agent_b.age - agent_a.age
        if age_difference > 10:
            experience_dependency = min(0.6, age_difference / 30)
            dependency_factors.append(experience_dependency)
        else:
            dependency_factors.append(0.0)
        
        return sum(dependency_factors) / len(dependency_factors)
    
    def evolve_relationship(self, dynamics: RelationshipDynamics, 
                          interaction_type: str, outcome: str,
                          turn: int) -> RelationshipDynamics:
        """Evolve a relationship based on interactions and outcomes."""
        # Record the interaction
        interaction_record = {
            "turn": turn,
            "type": interaction_type,
            "outcome": outcome,
            "participants": [dynamics.agent_a_id, dynamics.agent_b_id]
        }
        self.interaction_history.append(interaction_record)
        
        # Update shared experiences
        if outcome in ["success", "mutual_benefit", "collaboration"]:
            experience = f"{interaction_type}_{outcome}_{turn}"
            dynamics.shared_experiences.append(experience)
            if len(dynamics.shared_experiences) > 10:  # Keep recent experiences
                dynamics.shared_experiences = dynamics.shared_experiences[-10:]
        
        # Update conflict history
        if outcome in ["conflict", "disagreement", "failure", "escalation", "stalemate"]:
            conflict = f"{interaction_type}_{outcome}_{turn}"
            dynamics.conflict_history.append(conflict)
            if len(dynamics.conflict_history) > 5:  # Keep recent conflicts
                dynamics.conflict_history = dynamics.conflict_history[-5:]
        
        # Calculate relationship changes
        strength_change = self._calculate_strength_change(interaction_type, outcome)
        trust_change = self._calculate_trust_change(interaction_type, outcome)
        respect_change = self._calculate_respect_change(interaction_type, outcome)
        
        # Apply changes with bounds
        dynamics.current_strength = max(0.0, min(1.0, dynamics.current_strength + strength_change))
        dynamics.trust_level = max(0.0, min(1.0, dynamics.trust_level + trust_change))
        dynamics.respect_level = max(0.0, min(1.0, dynamics.respect_level + respect_change))
        
        # Update evolution trend
        recent_changes = [strength_change, trust_change, respect_change]
        avg_change = sum(recent_changes) / len(recent_changes)
        
        if avg_change > 0.05:
            dynamics.evolution_trend = RelationshipEvolution.STRENGTHENING
        elif avg_change < -0.05:
            dynamics.evolution_trend = RelationshipEvolution.WEAKENING
        elif len(dynamics.conflict_history) > 0 and len(dynamics.shared_experiences) > 0:
            dynamics.evolution_trend = RelationshipEvolution.CYCLING
        else:
            dynamics.evolution_trend = RelationshipEvolution.STABLE
        
        return dynamics
    
    def _calculate_strength_change(self, interaction_type: str, outcome: str) -> float:
        """Calculate how an interaction affects relationship strength."""
        base_changes = {
            "collaboration": {"success": 0.1, "failure": -0.05, "partial": 0.03},
            "mentorship": {"success": 0.08, "failure": -0.03, "progress": 0.05},
            "competition": {"victory": 0.02, "defeat": -0.02, "draw": 0.01},
            "conflict": {"resolution": 0.05, "escalation": -0.15, "stalemate": -0.05},
            "support": {"given": 0.06, "received": 0.04, "mutual": 0.08},
            "betrayal": {"discovered": -0.3, "forgiven": 0.1, "repeated": -0.5}
        }
        
        return base_changes.get(interaction_type, {}).get(outcome, 0.0)
    
    def _calculate_trust_change(self, interaction_type: str, outcome: str) -> float:
        """Calculate how an interaction affects trust."""
        trust_impacts = {
            "collaboration": {"success": 0.08, "failure": -0.03},
            "mentorship": {"success": 0.06, "betrayed": -0.20},
            "conflict": {"resolution": 0.05, "escalation": -0.15, "stalemate": -0.05},
            "support": {"given": 0.10, "received": 0.05, "withheld": -0.08},
            "secret_sharing": {"kept": 0.15, "revealed": -0.25},
            "promise": {"kept": 0.12, "broken": -0.18},
            "betrayal": {"discovered": -0.40, "forgiven": -0.10}
        }
        
        return trust_impacts.get(interaction_type, {}).get(outcome, 0.0)
    
    def _calculate_respect_change(self, interaction_type: str, outcome: str) -> float:
        """Calculate how an interaction affects respect."""
        respect_impacts = {
            "achievement": {"witnessed": 0.08, "shared": 0.05},
            "wisdom_sharing": {"valuable": 0.10, "irrelevant": -0.02},
            "leadership": {"effective": 0.12, "poor": -0.08},
            "skill_demonstration": {"impressive": 0.06, "lacking": -0.04},
            "moral_stand": {"admirable": 0.15, "questionable": -0.10},
            "humility": {"shown": 0.05, "lacking": -0.03}
        }
        
        return respect_impacts.get(interaction_type, {}).get(outcome, 0.0)
    
    def analyze_network_position(self, agent: Agent, all_agents: List[Agent]) -> Dict[str, float]:
        """Analyze an agent's position in the social network."""
        metrics = {}
        
        # Calculate centrality measures
        metrics["degree_centrality"] = self._calculate_degree_centrality(agent, all_agents)
        metrics["closeness_centrality"] = self._calculate_closeness_centrality(agent, all_agents)
        metrics["betweenness_centrality"] = self._calculate_betweenness_centrality(agent, all_agents)
        
        # Calculate influence metrics
        metrics["influence_score"] = self._calculate_network_influence(agent, all_agents)
        metrics["reputation_spread"] = self._calculate_reputation_spread(agent, all_agents)
        
        # Calculate relationship quality metrics
        metrics["average_relationship_strength"] = self._calculate_avg_relationship_strength(agent)
        metrics["relationship_diversity"] = self._calculate_relationship_diversity(agent, all_agents)
        
        self.network_metrics[agent.id] = metrics
        return metrics
    
    def _calculate_degree_centrality(self, agent: Agent, all_agents: List[Agent]) -> float:
        """Calculate degree centrality (number of connections)."""
        if not hasattr(agent, 'social_network') or not hasattr(agent.social_network, 'relationships'):
            return 0.0
        
        connections = 0
        for rel in agent.social_network.relationships.values():
            if hasattr(rel, 'strength') and rel.strength > 0.3:
                connections += 1
            elif isinstance(rel, (int, float)) and rel > 0.3:
                connections += 1
        
        max_possible_connections = len(all_agents) - 1  # Exclude self
        
        return connections / max_possible_connections if max_possible_connections > 0 else 0.0
    
    def _calculate_closeness_centrality(self, agent: Agent, all_agents: List[Agent]) -> float:
        """Calculate closeness centrality (how close to all other agents)."""
        if not hasattr(agent, 'social_network') or not hasattr(agent.social_network, 'relationships'):
            return 0.0
        
        total_distance = 0.0
        reachable_agents = 0
        
        for other_agent in all_agents:
            if other_agent.id == agent.id:
                continue
            
            # Simple distance calculation based on relationship strength
            relationship_strength = agent.social_network.relationships.get(other_agent.id, 0.0)
            if relationship_strength > 0.1:  # Consider as connected
                distance = 1.0 / (relationship_strength + 0.1)  # Stronger relationship = shorter distance
                total_distance += distance
                reachable_agents += 1
        
        if reachable_agents == 0:
            return 0.0
        
        average_distance = total_distance / reachable_agents
        return 1.0 / average_distance if average_distance > 0 else 0.0
    
    def _calculate_betweenness_centrality(self, agent: Agent, all_agents: List[Agent]) -> float:
        """Calculate betweenness centrality (how often agent is on shortest paths)."""
        # Simplified calculation - in a full implementation, this would use graph algorithms
        if not hasattr(agent, 'social_network') or not hasattr(agent.social_network, 'relationships'):
            return 0.0
        
        bridge_connections = 0
        total_paths = 0
        
        # Count how many agent pairs this agent connects
        connected_agents = [aid for aid, strength in agent.social_network.relationships.items() if strength > 0.3]
        
        for i, agent_a_id in enumerate(connected_agents):
            for agent_b_id in connected_agents[i+1:]:
                total_paths += 1
                
                # Check if A and B are directly connected (agent is not needed as bridge)
                agent_a = next((a for a in all_agents if a.id == agent_a_id), None)
                if agent_a and hasattr(agent_a, 'social_network'):
                    direct_connection = agent_a.social_network.relationships.get(agent_b_id, 0.0)
                    if direct_connection < 0.3:  # No strong direct connection
                        bridge_connections += 1
        
        return bridge_connections / total_paths if total_paths > 0 else 0.0
    
    def _calculate_network_influence(self, agent: Agent, all_agents: List[Agent]) -> float:
        """Calculate overall network influence."""
        if not hasattr(agent, 'social_network') or not hasattr(agent.social_network, 'relationships'):
            return agent.reputation * 0.5
        
        direct_influence = 0.0
        indirect_influence = 0.0
        
        for other_agent_id, relationship_strength in agent.social_network.relationships.items():
            if relationship_strength > 0.3:
                # Direct influence
                other_agent = next((a for a in all_agents if a.id == other_agent_id), None)
                if other_agent:
                    influence_score = relationship_strength * agent.reputation
                    direct_influence += influence_score
                    
                    # Indirect influence through this agent's connections
                    if hasattr(other_agent, 'social_network'):
                        secondary_connections = len([r for r in other_agent.social_network.relationships.values() if r > 0.3])
                        indirect_influence += influence_score * 0.3 * secondary_connections / 10  # Scaled down
        
        total_influence = direct_influence + indirect_influence
        max_possible_influence = len(all_agents) * agent.reputation
        
        return min(1.0, total_influence / max_possible_influence) if max_possible_influence > 0 else 0.0
    
    def _calculate_reputation_spread(self, agent: Agent, all_agents: List[Agent]) -> float:
        """Calculate how widely the agent's reputation is known."""
        if not hasattr(agent, 'social_network') or not hasattr(agent.social_network, 'relationships'):
            return 0.1  # Minimal reputation spread
        
        # Agents who know this agent well
        well_known_by = len([rel for rel in agent.social_network.relationships.values() if rel > 0.5])
        
        # Agents who have some knowledge
        somewhat_known_by = len([rel for rel in agent.social_network.relationships.values() if rel > 0.2])
        
        # Calculate spread
        total_population = len(all_agents)
        reputation_spread = (well_known_by * 1.0 + somewhat_known_by * 0.5) / total_population
        
        return min(1.0, reputation_spread)
    
    def _calculate_avg_relationship_strength(self, agent: Agent) -> float:
        """Calculate average relationship strength."""
        if not hasattr(agent, 'social_network') or not hasattr(agent.social_network, 'relationships'):
            return 0.0
        
        relationships = agent.social_network.relationships
        if not relationships:
            return 0.0
        
        strengths = []
        for rel in relationships.values():
            if hasattr(rel, 'strength'):
                strengths.append(rel.strength)
            elif isinstance(rel, (int, float)):
                strengths.append(rel)
        
        return sum(strengths) / len(strengths) if strengths else 0.0
    
    def _calculate_relationship_diversity(self, agent: Agent, all_agents: List[Agent]) -> float:
        """Calculate diversity of relationships (different types of people)."""
        if not hasattr(agent, 'social_network') or not hasattr(agent.social_network, 'relationships'):
            return 0.0
        
        connected_agent_ids = [aid for aid, strength in agent.social_network.relationships.items() if strength > 0.3]
        if not connected_agent_ids:
            return 0.0
        
        # Calculate diversity across multiple dimensions
        age_diversity = self._calculate_age_diversity(agent, connected_agent_ids, all_agents)
        skill_diversity = self._calculate_skill_diversity(agent, connected_agent_ids, all_agents)
        trait_diversity = self._calculate_trait_diversity(agent, connected_agent_ids, all_agents)
        
        return (age_diversity + skill_diversity + trait_diversity) / 3
    
    def _calculate_age_diversity(self, agent: Agent, connected_ids: List[str], all_agents: List[Agent]) -> float:
        """Calculate age diversity in relationships."""
        connected_ages = []
        for agent_id in connected_ids:
            other_agent = next((a for a in all_agents if a.id == agent_id), None)
            if other_agent:
                connected_ages.append(other_agent.age)
        
        if len(connected_ages) < 2:
            return 0.0
        
        # Calculate age spread
        age_range = max(connected_ages) - min(connected_ages)
        max_possible_range = 60  # Reasonable max age difference
        
        return min(1.0, age_range / max_possible_range)
    
    def _calculate_skill_diversity(self, agent: Agent, connected_ids: List[str], all_agents: List[Agent]) -> float:
        """Calculate skill diversity in relationships."""
        all_skills_in_network = set()
        
        for agent_id in connected_ids:
            other_agent = next((a for a in all_agents if a.id == agent_id), None)
            if other_agent:
                # Add skills where the other agent is competent
                competent_skills = [skill for skill, level in other_agent.skills.items() if level > 0.5]
                all_skills_in_network.update(competent_skills)
        
        # Compare to total possible skills
        all_possible_skills = set()
        for a in all_agents:
            all_possible_skills.update(a.skills.keys())
        
        if not all_possible_skills:
            return 0.0
        
        return len(all_skills_in_network) / len(all_possible_skills)
    
    def _calculate_trait_diversity(self, agent: Agent, connected_ids: List[str], all_agents: List[Agent]) -> float:
        """Calculate trait diversity in relationships."""
        trait_variations = []
        
        for trait in agent.traits.keys():
            connected_trait_values = []
            for agent_id in connected_ids:
                other_agent = next((a for a in all_agents if a.id == agent_id), None)
                if other_agent and trait in other_agent.traits:
                    connected_trait_values.append(other_agent.traits[trait])
            
            if len(connected_trait_values) > 1:
                trait_range = max(connected_trait_values) - min(connected_trait_values)
                trait_variations.append(trait_range)
        
        return sum(trait_variations) / len(trait_variations) if trait_variations else 0.0


# Factory functions for Day 3 classes

def create_advanced_lifecycle_manager() -> AdvancedLifecycleManager:
    """Factory function to create an advanced lifecycle manager."""
    return AdvancedLifecycleManager()


def create_reputation_manager() -> ReputationManager:
    """Factory function to create a reputation manager."""
    return ReputationManager()


def create_social_dynamics_manager() -> SocialDynamicsManager:
    """Factory function to create a social dynamics manager."""
    return SocialDynamicsManager()
