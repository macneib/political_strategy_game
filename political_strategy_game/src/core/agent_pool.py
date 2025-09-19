#!/usr/bin/env python3
"""
Agent Pool Management System for Political Advisor System

This module implements detailed tracking for the top 1-5% of population with
full personality profiles, achievement histories, and lifecycle management.
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

# Import from existing systems
from .citizen import Citizen, Achievement, AchievementCategory, CitizenGenerator
from .technology_tree import TechnologyEra
from .advisor import AdvisorRole


class TraitChangeType(str, Enum):
    """Types of trait changes over time."""
    NATURAL_DEVELOPMENT = "natural_development"
    EXPERIENCE_BASED = "experience_based"
    MENTORSHIP_INFLUENCE = "mentorship_influence"
    CRISIS_RESPONSE = "crisis_response"
    ACHIEVEMENT_IMPACT = "achievement_impact"
    SOCIAL_INFLUENCE = "social_influence"


class EventType(str, Enum):
    """Types of narrative events for agents."""
    PROMOTION = "promotion"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    SKILL_BREAKTHROUGH = "skill_breakthrough"
    MENTORSHIP_BEGAN = "mentorship_began"
    LEADERSHIP_EMERGENCE = "leadership_emergence"
    CRISIS_LEADERSHIP = "crisis_leadership"
    INNOVATION_SUCCESS = "innovation_success"
    SOCIAL_INFLUENCE_GAIN = "social_influence_gain"
    SPECIALIZATION_CHOICE = "specialization_choice"
    PEAK_PERFORMANCE = "peak_performance"


class PerformanceTrend(str, Enum):
    """Performance trend indicators."""
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"
    PEAK = "peak"
    PLATEAU = "plateau"


@dataclass
class TraitChange:
    """Record of a trait change over time."""
    turn: int
    trait_name: str
    old_value: float
    new_value: float
    change_type: TraitChangeType
    cause: str
    impact_magnitude: float


@dataclass
class PerformanceSnapshot:
    """Snapshot of agent performance at a specific time."""
    turn: int
    composite_score: float
    skill_scores: Dict[str, float]
    achievement_count: int
    reputation: float
    social_influence: float
    trend: PerformanceTrend


@dataclass
class MentorshipRecord:
    """Record of mentorship relationships."""
    mentor_id: str
    mentee_id: str
    start_turn: int
    end_turn: Optional[int]
    focus_skills: List[str]
    effectiveness_score: float
    mutual_benefit: bool


@dataclass
class FactionAffiliation:
    """Agent's affiliation with political or social factions."""
    faction_id: str
    faction_name: str
    affiliation_strength: float
    join_turn: int
    role_in_faction: str
    influence_level: float


class PersonalityProfile(BaseModel):
    """Detailed personality profile for agents with development tracking."""
    
    # Enhanced trait tracking
    core_traits: Dict[str, float] = Field(default_factory=dict)
    trait_development_history: List[TraitChange] = Field(default_factory=list)
    personality_drift_rate: float = Field(default=0.02, ge=0.0, le=0.1)
    
    # Personality analysis
    dominant_traits: List[str] = Field(default_factory=list)
    trait_interactions: Dict[str, float] = Field(default_factory=dict)
    personality_stability: float = Field(default=0.7, ge=0.0, le=1.0)
    
    # Behavioral patterns
    decision_making_style: str = Field(default="balanced")
    stress_response_pattern: str = Field(default="adaptive")
    leadership_style: str = Field(default="collaborative")
    learning_preferences: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(use_enum_values=True)


class PerformanceMetrics(BaseModel):
    """Comprehensive performance tracking for agents."""
    
    # Peak performance tracking
    skill_peak_ages: Dict[str, int] = Field(default_factory=dict)
    peak_performance_period: Optional[Tuple[int, int]] = Field(default=None)
    peak_composite_score: float = Field(default=0.0)
    
    # Development metrics
    achievement_rate: float = Field(default=0.0, ge=0.0)  # Achievements per turn
    skill_development_velocity: Dict[str, float] = Field(default_factory=dict)
    leadership_emergence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    advisor_readiness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Performance history
    performance_trend: List[PerformanceSnapshot] = Field(default_factory=list)
    recent_achievements: List[str] = Field(default_factory=list)
    skill_plateau_detection: Dict[str, bool] = Field(default_factory=dict)
    
    # Predictive metrics
    potential_ceiling: float = Field(default=1.0, ge=0.0, le=1.0)
    growth_trajectory: str = Field(default="linear")
    specialization_readiness: Dict[str, float] = Field(default_factory=dict)
    
    model_config = ConfigDict(use_enum_values=True)


class AchievementRecord(BaseModel):
    """Detailed achievement tracking with temporal and impact data."""
    
    achievement: Achievement
    unlock_turn: int
    unlock_circumstances: str
    
    # Impact tracking
    impact_on_development: Dict[str, float] = Field(default_factory=dict)
    reputation_impact: float = Field(default=0.0)
    social_influence_impact: float = Field(default=0.0)
    narrative_significance: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Context and progression
    prerequisites_met: List[str] = Field(default_factory=list)
    progression_chain: Optional[str] = Field(default=None)
    rarity_at_unlock: float = Field(default=0.5, ge=0.0, le=1.0)
    
    model_config = ConfigDict(use_enum_values=True)


class NarrativeEvent(BaseModel):
    """Story events for narrative consistency and agent development."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    turn: int
    event_type: EventType
    title: str
    description: str
    
    # Participants and relationships
    primary_agent_id: str
    secondary_participants: List[str] = Field(default_factory=list)
    faction_involvement: List[str] = Field(default_factory=list)
    
    # Impact and consequences
    impact_on_reputation: float = Field(default=0.0)
    skill_development_effects: Dict[str, float] = Field(default_factory=dict)
    trait_development_effects: Dict[str, float] = Field(default_factory=dict)
    relationship_effects: Dict[str, float] = Field(default_factory=dict)
    
    # Narrative elements
    narrative_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    story_importance: str = Field(default="minor")
    consequences: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(use_enum_values=True)


class EnhancedRelationship(BaseModel):
    """Enhanced relationship tracking for agents."""
    
    # Basic relationship data
    other_agent_id: str
    relationship_type: str
    strength: float = Field(ge=0.0, le=1.0)
    
    # Development tracking
    relationship_history: List[Tuple[int, float]] = Field(default_factory=list)  # (turn, strength)
    interaction_frequency: float = Field(default=0.1, ge=0.0, le=1.0)
    mutual_influence: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Professional aspects
    collaboration_projects: List[str] = Field(default_factory=list)
    skill_exchange: Dict[str, float] = Field(default_factory=dict)
    mentorship_aspect: Optional[str] = Field(default=None)
    
    # Personal aspects
    trust_level: float = Field(default=0.5, ge=0.0, le=1.0)
    loyalty: float = Field(default=0.5, ge=0.0, le=1.0)
    compatibility: float = Field(default=0.5, ge=0.0, le=1.0)
    
    model_config = ConfigDict(use_enum_values=True)


class SocialNetwork(BaseModel):
    """Enhanced social network for agents."""
    
    # Relationship management
    relationships: Dict[str, EnhancedRelationship] = Field(default_factory=dict)
    relationship_capacity: int = Field(default=20, ge=5, le=50)
    
    # Network metrics
    social_influence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    network_centrality: float = Field(default=0.0, ge=0.0, le=1.0)
    connection_quality: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Specialized relationships
    mentorship_relationships: List[MentorshipRecord] = Field(default_factory=list)
    factional_affiliations: List[FactionAffiliation] = Field(default_factory=list)
    
    # Network evolution
    network_growth_rate: float = Field(default=0.05, ge=0.0, le=0.2)
    relationship_maintenance_skill: float = Field(default=0.5, ge=0.0, le=1.0)
    social_capital: float = Field(default=0.0, ge=0.0)
    
    model_config = ConfigDict(use_enum_values=True)


class Agent(Citizen):
    """
    Enhanced citizen with detailed agent-level tracking for top performers.
    
    Extends the base Citizen class with comprehensive personality, performance,
    achievement, and social network tracking suitable for potential advisors.
    """
    
    # Enhanced personality and development
    personality_profile: PersonalityProfile = Field(default_factory=PersonalityProfile)
    performance_metrics: PerformanceMetrics = Field(default_factory=PerformanceMetrics)
    achievement_history: List[AchievementRecord] = Field(default_factory=list)
    narrative_history: List[NarrativeEvent] = Field(default_factory=list)
    social_network: SocialNetwork = Field(default_factory=SocialNetwork)
    
    # Agent pool specific tracking
    promotion_turn: int = Field(default=0)
    agent_pool_rank: int = Field(default=0)
    pool_tenure: int = Field(default=0)  # Turns in agent pool
    
    # Specialization and development
    specialization_paths: List[str] = Field(default_factory=list)
    primary_specialization: Optional[str] = Field(default=None)
    specialization_progress: Dict[str, float] = Field(default_factory=dict)
    
    # Mentorship networks
    mentor_relationships: List[str] = Field(default_factory=list)  # Agent IDs of mentors
    protege_relationships: List[str] = Field(default_factory=list)  # Agent IDs of proteges
    mentorship_effectiveness: Dict[str, float] = Field(default_factory=dict)
    
    # Lifecycle and succession
    peak_performance_period: Optional[Tuple[int, int]] = Field(default=None)
    performance_decline_started: Optional[int] = Field(default=None)
    retirement_probability: float = Field(default=0.0, ge=0.0, le=1.0)
    succession_candidates: List[str] = Field(default_factory=list)
    legacy_achievements: List[str] = Field(default_factory=list)
    
    # Agent-specific metrics
    agent_composite_score: float = Field(default=0.0, ge=0.0, le=1.0)
    advisor_candidacy_score: float = Field(default=0.0, ge=0.0, le=1.0)
    leadership_potential: float = Field(default=0.0, ge=0.0, le=1.0)
    innovation_potential: float = Field(default=0.0, ge=0.0, le=1.0)
    
    model_config = ConfigDict(use_enum_values=True)
    
    def calculate_composite_score(self) -> float:
        """Calculate comprehensive agent performance score."""
        if not self.skills:
            return 0.0
        
        # Base skill score
        skill_score = sum(self.skills.values()) / len(self.skills)
        
        # Achievement bonus
        achievement_bonus = min(0.3, len(self.achievement_history) * 0.02)
        
        # Social influence bonus
        social_bonus = self.social_network.social_influence_score * 0.2
        
        # Reputation bonus
        reputation_bonus = (self.reputation - 0.5) * 0.2
        
        # Performance metrics bonus
        performance_bonus = self.performance_metrics.leadership_emergence_score * 0.1
        
        composite = skill_score + achievement_bonus + social_bonus + reputation_bonus + performance_bonus
        return max(0.0, min(1.0, composite))
    
    def update_advisor_candidacy_score(self, era: TechnologyEra) -> float:
        """Update and return advisor candidacy score for current era."""
        # Implementation will be enhanced in Day 2
        base_score = self.calculate_composite_score()
        
        # Era-specific adjustments (placeholder for now)
        era_adjustment = 1.0
        
        # Potential role alignment
        role_alignment = len(self.potential_roles) / 7.0  # Max 7 advisor roles
        
        candidacy_score = base_score * era_adjustment * (0.7 + 0.3 * role_alignment)
        self.advisor_candidacy_score = max(0.0, min(1.0, candidacy_score))
        
        return self.advisor_candidacy_score
    
    def get_specialization_strength(self, specialization: str) -> float:
        """Get strength in a particular specialization."""
        if specialization not in self.specialization_progress:
            return 0.0
        
        base_progress = self.specialization_progress[specialization]
        
        # Factor in relevant skills
        relevant_skills = self._get_specialization_skills(specialization)
        skill_strength = sum(self.skills.get(skill, 0.0) for skill in relevant_skills) / max(1, len(relevant_skills))
        
        # Combine progress and skill strength
        return (base_progress * 0.6 + skill_strength * 0.4)
    
    def _get_specialization_skills(self, specialization: str) -> List[str]:
        """Get relevant skills for a specialization."""
        specialization_skills = {
            "military_leadership": ["combat", "leadership", "administration"],
            "economic_management": ["trade", "administration", "innovation"],
            "diplomatic_relations": ["diplomacy", "leadership", "philosophy"],
            "scientific_research": ["science", "scholarship", "innovation"],
            "cultural_development": ["arts", "philosophy", "leadership"],
            "technological_innovation": ["technology", "engineering", "innovation"],
            "intelligence_operations": ["scholarship", "diplomacy", "administration"]
        }
        
        return specialization_skills.get(specialization, [])


@dataclass
class PromotionCriteria:
    """Criteria for promoting citizens to agent pool."""
    min_composite_score: float = 0.7
    min_skill_count: int = 3
    min_reputation: float = 0.6
    achievement_weight: float = 0.3
    social_influence_weight: float = 0.2
    age_preference_range: Tuple[int, int] = (25, 55)
    era_specific_adjustments: Dict[TechnologyEra, float] = None


@dataclass
class DemotionCriteria:
    """Criteria for demoting agents from pool."""
    performance_decline_threshold: float = 0.2  # 20% decline
    inactivity_turns: int = 50
    age_retirement_threshold: int = 65
    min_pool_performance_percentile: float = 0.4  # Bottom 40%
    narrative_consistency_weight: float = 0.3


class AgentPoolManager:
    """
    Central manager for agent pool operations and lifecycle management.
    
    Manages the promotion and demotion of citizens to/from the elite agent pool,
    tracks detailed development, and maintains narrative consistency.
    """
    
    def __init__(self, pool_size_target: int = 100, min_pool_size: int = 50, max_pool_size: int = 500):
        self.agent_pool: List[Agent] = []
        self.pool_size_target = pool_size_target
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size
        
        self.promotion_criteria = PromotionCriteria()
        self.demotion_criteria = DemotionCriteria()
        
        self.promotion_history: List[Tuple[int, str]] = []  # (turn, agent_id)
        self.demotion_history: List[Tuple[int, str]] = []  # (turn, agent_id)
        
        self.pool_statistics = {
            "total_promotions": 0,
            "total_demotions": 0,
            "average_tenure": 0.0,
            "top_performers": [],
            "specialization_distribution": {}
        }
    
    def evaluate_promotion_candidates(self, citizens: List[Citizen], turn: int) -> List[Citizen]:
        """Evaluate citizens for potential promotion to agent pool."""
        candidates = []
        
        for citizen in citizens:
            if self._meets_promotion_criteria(citizen, turn):
                candidates.append(citizen)
        
        # Sort by composite score (highest first)
        candidates.sort(key=lambda c: self._calculate_promotion_score(c), reverse=True)
        
        # Limit candidates to reasonable number
        max_candidates = min(len(candidates), self.pool_size_target // 4)
        return candidates[:max_candidates]
    
    def promote_to_agent_pool(self, citizen: Citizen, turn: int) -> Agent:
        """Promote a citizen to agent pool with enhanced tracking."""
        # Create enhanced agent from citizen
        agent = Agent(
            **citizen.model_dump(),
            promotion_turn=turn,
            agent_pool_rank=len(self.agent_pool) + 1,
            pool_tenure=0
        )
        
        # Initialize agent-specific tracking
        agent.personality_profile = self._create_personality_profile(citizen)
        agent.performance_metrics = self._initialize_performance_metrics(citizen, turn)
        agent.social_network = self._initialize_social_network(citizen)
        
        # Create promotion narrative event
        promotion_event = NarrativeEvent(
            turn=turn,
            event_type=EventType.PROMOTION,
            title=f"{agent.name} Promoted to Elite Status",
            description=f"Citizen {agent.name} has been promoted to the elite agent pool due to exceptional performance.",
            primary_agent_id=agent.id,
            impact_on_reputation=0.1,
            narrative_weight=0.7,
            story_importance="major"
        )
        
        agent.narrative_history.append(promotion_event)
        
        # Add to pool
        self.agent_pool.append(agent)
        self.promotion_history.append((turn, agent.id))
        self.pool_statistics["total_promotions"] += 1
        
        return agent
    
    def evaluate_demotion_candidates(self, turn: int) -> List[Agent]:
        """Evaluate agents for potential demotion from pool."""
        candidates = []
        
        for agent in self.agent_pool:
            if self._meets_demotion_criteria(agent, turn):
                candidates.append(agent)
        
        # Sort by performance (lowest first for demotion priority)
        candidates.sort(key=lambda a: a.calculate_composite_score())
        
        return candidates
    
    def demote_from_agent_pool(self, agent: Agent, turn: int, reason: str = "performance_decline") -> Citizen:
        """Demote an agent from pool back to general population."""
        # Create demotion narrative event
        demotion_event = NarrativeEvent(
            turn=turn,
            event_type=EventType.PROMOTION,  # Using promotion type for now, can add demotion type
            title=f"{agent.name} Returned to General Population",
            description=f"Agent {agent.name} has been demoted from elite status due to {reason}.",
            primary_agent_id=agent.id,
            impact_on_reputation=-0.05,
            narrative_weight=0.5,
            story_importance="minor"
        )
        
        agent.narrative_history.append(demotion_event)
        
        # Convert back to citizen (preserve base citizen data)
        citizen_data = {k: v for k, v in agent.model_dump().items() 
                       if k in Citizen.model_fields}
        
        citizen = Citizen(**citizen_data)
        
        # Remove from pool
        self.agent_pool.remove(agent)
        self.demotion_history.append((turn, agent.id))
        self.pool_statistics["total_demotions"] += 1
        
        return citizen
    
    def update_agent_pool(self, turn: int, available_citizens: List[Citizen]) -> Dict[str, List[str]]:
        """Update agent pool with promotions and demotions."""
        results = {
            "promoted": [],
            "demoted": [],
            "pool_size": len(self.agent_pool)
        }
        
        # Handle demotions first
        demotion_candidates = self.evaluate_demotion_candidates(turn)
        needed_demotions = max(0, len(self.agent_pool) - self.max_pool_size)
        
        for agent in demotion_candidates[:needed_demotions]:
            citizen = self.demote_from_agent_pool(agent, turn)
            results["demoted"].append(citizen.id)
        
        # Handle promotions
        current_pool_size = len(self.agent_pool)
        needed_promotions = max(0, self.pool_size_target - current_pool_size)
        
        if needed_promotions > 0:
            promotion_candidates = self.evaluate_promotion_candidates(available_citizens, turn)
            
            for citizen in promotion_candidates[:needed_promotions]:
                agent = self.promote_to_agent_pool(citizen, turn)
                results["promoted"].append(agent.id)
        
        # Update pool statistics
        self._update_pool_statistics(turn)
        results["pool_size"] = len(self.agent_pool)
        
        return results
    
    def get_top_performers(self, count: int = 10) -> List[Agent]:
        """Get top performing agents from the pool."""
        sorted_agents = sorted(self.agent_pool, 
                             key=lambda a: a.calculate_composite_score(), 
                             reverse=True)
        return sorted_agents[:count]
    
    def get_agents_by_specialization(self, specialization: str) -> List[Agent]:
        """Get agents with a specific specialization."""
        return [agent for agent in self.agent_pool 
                if specialization in agent.specialization_paths]
    
    def _meets_promotion_criteria(self, citizen: Citizen, turn: int) -> bool:
        """Check if citizen meets promotion criteria."""
        # Calculate composite score
        if not citizen.skills:
            return False
        
        composite_score = sum(citizen.skills.values()) / len(citizen.skills)
        if composite_score < self.promotion_criteria.min_composite_score:
            return False
        
        # Check skill count
        significant_skills = [s for s in citizen.skills.values() if s > 0.3]
        if len(significant_skills) < self.promotion_criteria.min_skill_count:
            return False
        
        # Check reputation
        if citizen.reputation < self.promotion_criteria.min_reputation:
            return False
        
        # Check age preference
        age_min, age_max = self.promotion_criteria.age_preference_range
        if not (age_min <= citizen.age <= age_max):
            return False
        
        return True
    
    def _meets_demotion_criteria(self, agent: Agent, turn: int) -> bool:
        """Check if agent meets demotion criteria."""
        # Check age retirement
        if agent.age >= self.demotion_criteria.age_retirement_threshold:
            return True
        
        # Check performance decline
        current_score = agent.calculate_composite_score()
        if (agent.performance_metrics.peak_composite_score > 0 and 
            current_score < agent.performance_metrics.peak_composite_score * 
            (1 - self.demotion_criteria.performance_decline_threshold)):
            return True
        
        # Check inactivity (simplified - could be enhanced)
        if agent.pool_tenure > self.demotion_criteria.inactivity_turns and current_score < 0.5:
            return True
        
        return False
    
    def _calculate_promotion_score(self, citizen: Citizen) -> float:
        """Calculate promotion score for ranking candidates."""
        if not citizen.skills:
            return 0.0
        
        skill_score = sum(citizen.skills.values()) / len(citizen.skills)
        achievement_score = min(0.3, len(citizen.achievements) * 0.05)
        reputation_score = citizen.reputation
        potential_score = citizen.advisor_potential
        
        return (skill_score * 0.4 + achievement_score * 0.2 + 
                reputation_score * 0.2 + potential_score * 0.2)
    
    def _create_personality_profile(self, citizen: Citizen) -> PersonalityProfile:
        """Create detailed personality profile from citizen traits."""
        profile = PersonalityProfile(
            core_traits=citizen.traits.copy(),
            personality_drift_rate=random.uniform(0.01, 0.05),
            personality_stability=random.uniform(0.6, 0.9)
        )
        
        # Identify dominant traits (top 3 positive traits)
        positive_traits = {k: v for k, v in citizen.traits.items() if v > 0}
        sorted_traits = sorted(positive_traits.items(), key=lambda x: x[1], reverse=True)
        profile.dominant_traits = [trait[0] for trait in sorted_traits[:3]]
        
        # Set decision making style based on traits
        if citizen.traits.get("analytical_thinking", 0) > 0.6:
            profile.decision_making_style = "analytical"
        elif citizen.traits.get("intuition", 0) > 0.6:
            profile.decision_making_style = "intuitive"
        else:
            profile.decision_making_style = "balanced"
        
        return profile
    
    def _initialize_performance_metrics(self, citizen: Citizen, turn: int) -> PerformanceMetrics:
        """Initialize performance metrics for new agent."""
        metrics = PerformanceMetrics(
            achievement_rate=0.0,
            leadership_emergence_score=citizen.advisor_potential,
            advisor_readiness_score=citizen.advisor_potential
        )
        
        # Initialize skill development velocity
        for skill, rate in citizen.skill_development_rate.items():
            metrics.skill_development_velocity[skill] = rate
        
        # Create initial performance snapshot
        initial_snapshot = PerformanceSnapshot(
            turn=turn,
            composite_score=sum(citizen.skills.values()) / len(citizen.skills) if citizen.skills else 0.0,
            skill_scores=citizen.skills.copy(),
            achievement_count=len(citizen.achievements),
            reputation=citizen.reputation,
            social_influence=citizen.social_influence,
            trend=PerformanceTrend.RISING
        )
        
        metrics.performance_trend.append(initial_snapshot)
        
        return metrics
    
    def _initialize_social_network(self, citizen: Citizen) -> SocialNetwork:
        """Initialize social network for new agent."""
        network = SocialNetwork(
            social_influence_score=citizen.social_influence,
            relationship_capacity=random.randint(15, 30),
            network_growth_rate=random.uniform(0.03, 0.08),
            relationship_maintenance_skill=random.uniform(0.4, 0.8)
        )
        
        # Convert existing relationships to enhanced relationships
        for citizen_id, relationship_id in citizen.relationships.items():
            enhanced_rel = EnhancedRelationship(
                other_agent_id=citizen_id,
                relationship_type="colleague",  # Default type
                strength=random.uniform(0.3, 0.7),
                trust_level=random.uniform(0.4, 0.8),
                loyalty=random.uniform(0.3, 0.7),
                compatibility=random.uniform(0.4, 0.8)
            )
            network.relationships[citizen_id] = enhanced_rel
        
        return network
    
    def _update_pool_statistics(self, turn: int):
        """Update pool statistics."""
        if not self.agent_pool:
            return
        
        # Calculate average tenure
        total_tenure = sum(agent.pool_tenure for agent in self.agent_pool)
        self.pool_statistics["average_tenure"] = total_tenure / len(self.agent_pool)
        
        # Update top performers
        self.pool_statistics["top_performers"] = [
            agent.id for agent in self.get_top_performers(5)
        ]
        
        # Update specialization distribution
        specialization_counts = defaultdict(int)
        for agent in self.agent_pool:
            for spec in agent.specialization_paths:
                specialization_counts[spec] += 1
        
        self.pool_statistics["specialization_distribution"] = dict(specialization_counts)


def create_agent_pool_manager(pool_size_target: int = 100) -> AgentPoolManager:
    """Factory function to create an agent pool manager."""
    return AgentPoolManager(pool_size_target=pool_size_target)
