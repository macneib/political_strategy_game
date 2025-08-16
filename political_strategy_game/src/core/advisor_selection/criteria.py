"""
Advisor Selection Criteria Definitions

This module contains all the criteria, methods, and context definitions
for the advisor candidate selection system.
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass

from ..advisor import AdvisorRole


class SelectionCriterion(str, Enum):
    """Criteria for advisor candidate evaluation."""
    COMPETENCE = "competence"
    INTEGRITY = "integrity"
    INNOVATION = "innovation"
    LEADERSHIP = "leadership"
    WISDOM = "wisdom"
    CHARISMA = "charisma"
    RELIABILITY = "reliability"
    VISION = "vision"
    LOYALTY = "loyalty"
    PRAGMATISM = "pragmatism"
    EXPERIENCE = "experience"
    NETWORK_INFLUENCE = "network_influence"
    ADAPTABILITY = "adaptability"
    CRISIS_MANAGEMENT = "crisis_management"
    STRATEGIC_THINKING = "strategic_thinking"


class SelectionMethod(str, Enum):
    """Methods for candidate selection algorithm."""
    AHP = "analytical_hierarchy_process"
    FUZZY_AHP = "fuzzy_analytical_hierarchy_process"
    TOPSIS = "technique_for_order_preference"
    WEIGHTED_SUM = "weighted_sum_model"
    PROMETHEE = "preference_ranking_organization"
    ELECTRE = "elimination_choice_reality"
    HYBRID_AHP_TOPSIS = "hybrid_ahp_topsis"


class SelectionContext(str, Enum):
    """Context for advisor selection."""
    NORMAL_SUCCESSION = "normal_succession"
    CRISIS_LEADERSHIP = "crisis_leadership"
    REFORM_INITIATIVE = "reform_initiative"
    WAR_TIME = "war_time"
    DIPLOMATIC_MISSION = "diplomatic_mission"
    ECONOMIC_CRISIS = "economic_crisis"
    INNOVATION_DRIVE = "innovation_drive"
    STABILITY_FOCUS = "stability_focus"


class CandidateFilterType(str, Enum):
    """Types of candidate filtering mechanisms."""
    MINIMUM_THRESHOLD = "minimum_threshold"
    TOP_PERCENTILE = "top_percentile"
    ROLE_SPECIFIC = "role_specific"
    DIVERSITY_BALANCE = "diversity_balance"
    SUCCESSION_READINESS = "succession_readiness"
    LOYALTY_SCREEN = "loyalty_screen"
    COMPETENCE_GATE = "competence_gate"


@dataclass
class SelectionCriteria:
    """Comprehensive selection criteria for advisor candidates."""
    criterion: SelectionCriterion
    weight: float  # 0.0 to 1.0
    threshold: float  # Minimum acceptable value
    preference_direction: str  # "maximize" or "minimize"
    fuzzy_tolerance: float  # For fuzzy AHP
    context_multiplier: Dict[SelectionContext, float]  # Context-specific adjustments


@dataclass
class CandidateScore:
    """Comprehensive scoring result for a candidate."""
    agent_id: str
    overall_score: float
    criteria_scores: Dict[SelectionCriterion, float]
    method_scores: Dict[SelectionMethod, float]
    rank_position: int
    selection_confidence: float
    strengths: List[str]
    weaknesses: List[str]
    context_suitability: Dict[SelectionContext, float]


@dataclass
class SelectionHistory:
    """Historical record of selection decisions."""
    turn: int
    context: SelectionContext
    role: AdvisorRole
    selected_agent_id: str
    selection_score: float
    alternatives_count: int
    method_used: SelectionMethod
    criteria_weights: Dict[SelectionCriterion, float]
    outcome_success: Optional[float]  # Filled in later based on performance


def get_default_role_criteria(role: AdvisorRole) -> List[SelectionCriteria]:
    """Get default selection criteria for a specific advisor role."""
    
    if role == AdvisorRole.MILITARY:
        return [
            SelectionCriteria(
                criterion=SelectionCriterion.LEADERSHIP,
                weight=0.25, threshold=0.7, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.WAR_TIME: 1.5}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.COMPETENCE,
                weight=0.20, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.CRISIS_LEADERSHIP: 1.3}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.CRISIS_MANAGEMENT,
                weight=0.20, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.15, context_multiplier={SelectionContext.WAR_TIME: 1.4}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.LOYALTY,
                weight=0.15, threshold=0.5, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.STABILITY_FOCUS: 1.2}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.STRATEGIC_THINKING,
                weight=0.20, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.12, context_multiplier={SelectionContext.WAR_TIME: 1.3}
            )
        ]
    
    elif role == AdvisorRole.ECONOMIC:
        return [
            SelectionCriteria(
                criterion=SelectionCriterion.COMPETENCE,
                weight=0.30, threshold=0.7, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.ECONOMIC_CRISIS: 1.5}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.INNOVATION,
                weight=0.20, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.15, context_multiplier={SelectionContext.INNOVATION_DRIVE: 1.4}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.PRAGMATISM,
                weight=0.15, threshold=0.5, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.ECONOMIC_CRISIS: 1.3}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.STRATEGIC_THINKING,
                weight=0.20, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.12, context_multiplier={SelectionContext.REFORM_INITIATIVE: 1.2}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.INTEGRITY,
                weight=0.15, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.REFORM_INITIATIVE: 1.2}
            )
        ]
    
    elif role == AdvisorRole.DIPLOMATIC:
        return [
            SelectionCriteria(
                criterion=SelectionCriterion.CHARISMA,
                weight=0.25, threshold=0.7, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.DIPLOMATIC_MISSION: 1.5}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.WISDOM,
                weight=0.20, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.12, context_multiplier={SelectionContext.DIPLOMATIC_MISSION: 1.3}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.INTEGRITY,
                weight=0.20, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.DIPLOMATIC_MISSION: 1.2}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.NETWORK_INFLUENCE,
                weight=0.20, threshold=0.5, preference_direction="maximize",
                fuzzy_tolerance=0.15, context_multiplier={SelectionContext.DIPLOMATIC_MISSION: 1.4}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.ADAPTABILITY,
                weight=0.15, threshold=0.5, preference_direction="maximize",
                fuzzy_tolerance=0.12, context_multiplier={SelectionContext.CRISIS_LEADERSHIP: 1.3}
            )
        ]
    
    elif role == AdvisorRole.CULTURAL:
        return [
            SelectionCriteria(
                criterion=SelectionCriterion.WISDOM,
                weight=0.25, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.12, context_multiplier={SelectionContext.STABILITY_FOCUS: 1.3}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.CHARISMA,
                weight=0.20, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.REFORM_INITIATIVE: 1.2}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.INTEGRITY,
                weight=0.20, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.STABILITY_FOCUS: 1.4}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.INNOVATION,
                weight=0.15, threshold=0.5, preference_direction="maximize",
                fuzzy_tolerance=0.15, context_multiplier={SelectionContext.INNOVATION_DRIVE: 1.5}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.VISION,
                weight=0.20, threshold=0.5, preference_direction="maximize",
                fuzzy_tolerance=0.15, context_multiplier={SelectionContext.REFORM_INITIATIVE: 1.3}
            )
        ]
    
    elif role == AdvisorRole.SCIENTIFIC:
        return [
            SelectionCriteria(
                criterion=SelectionCriterion.INNOVATION,
                weight=0.30, threshold=0.7, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.INNOVATION_DRIVE: 1.6}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.COMPETENCE,
                weight=0.25, threshold=0.7, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.INNOVATION_DRIVE: 1.4}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.STRATEGIC_THINKING,
                weight=0.20, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.INNOVATION_DRIVE: 1.3}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.VISION,
                weight=0.15, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.INNOVATION_DRIVE: 1.3}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.ADAPTABILITY,
                weight=0.10, threshold=0.5, preference_direction="maximize",
                fuzzy_tolerance=0.15, context_multiplier={SelectionContext.INNOVATION_DRIVE: 1.2}
            )
        ]
    
    elif role == AdvisorRole.SECURITY:
        return [
            SelectionCriteria(
                criterion=SelectionCriterion.LOYALTY,
                weight=0.25, threshold=0.7, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.CRISIS_LEADERSHIP: 1.5}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.COMPETENCE,
                weight=0.20, threshold=0.7, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.CRISIS_LEADERSHIP: 1.4}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.CRISIS_MANAGEMENT,
                weight=0.20, threshold=0.7, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.CRISIS_LEADERSHIP: 1.5}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.RELIABILITY,
                weight=0.20, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.STABILITY_FOCUS: 1.3}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.STRATEGIC_THINKING,
                weight=0.15, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.CRISIS_LEADERSHIP: 1.3}
            )
        ]
    
    elif role == AdvisorRole.RELIGIOUS:
        return [
            SelectionCriteria(
                criterion=SelectionCriterion.WISDOM,
                weight=0.30, threshold=0.7, preference_direction="maximize",
                fuzzy_tolerance=0.12, context_multiplier={SelectionContext.STABILITY_FOCUS: 1.4}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.INTEGRITY,
                weight=0.25, threshold=0.7, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.STABILITY_FOCUS: 1.5}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.CHARISMA,
                weight=0.20, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.REFORM_INITIATIVE: 1.2}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.LOYALTY,
                weight=0.15, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={SelectionContext.STABILITY_FOCUS: 1.3}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.VISION,
                weight=0.10, threshold=0.5, preference_direction="maximize",
                fuzzy_tolerance=0.15, context_multiplier={SelectionContext.REFORM_INITIATIVE: 1.3}
            )
        ]
    
    else:
        # Default criteria for unknown roles
        return [
            SelectionCriteria(
                criterion=SelectionCriterion.COMPETENCE,
                weight=0.30, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.INTEGRITY,
                weight=0.25, threshold=0.6, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.LEADERSHIP,
                weight=0.20, threshold=0.5, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.RELIABILITY,
                weight=0.15, threshold=0.5, preference_direction="maximize",
                fuzzy_tolerance=0.1, context_multiplier={}
            ),
            SelectionCriteria(
                criterion=SelectionCriterion.WISDOM,
                weight=0.10, threshold=0.5, preference_direction="maximize",
                fuzzy_tolerance=0.12, context_multiplier={}
            )
        ]


def get_default_context_weights() -> Dict[SelectionContext, Dict[SelectionCriterion, float]]:
    """Get default context-specific weight adjustments for criteria."""
    
    return {
        SelectionContext.NORMAL_SUCCESSION: {
            SelectionCriterion.COMPETENCE: 1.0,
            SelectionCriterion.INTEGRITY: 1.1,
            SelectionCriterion.EXPERIENCE: 1.2,
            SelectionCriterion.RELIABILITY: 1.1,
            SelectionCriterion.LOYALTY: 1.0
        },
        
        SelectionContext.CRISIS_LEADERSHIP: {
            SelectionCriterion.LEADERSHIP: 1.4,
            SelectionCriterion.CRISIS_MANAGEMENT: 1.5,
            SelectionCriterion.ADAPTABILITY: 1.3,
            SelectionCriterion.COMPETENCE: 1.2,
            SelectionCriterion.STRATEGIC_THINKING: 1.3
        },
        
        SelectionContext.WAR_TIME: {
            SelectionCriterion.LEADERSHIP: 1.5,
            SelectionCriterion.LOYALTY: 1.4,
            SelectionCriterion.CRISIS_MANAGEMENT: 1.4,
            SelectionCriterion.STRATEGIC_THINKING: 1.3,
            SelectionCriterion.COMPETENCE: 1.2
        },
        
        SelectionContext.DIPLOMATIC_MISSION: {
            SelectionCriterion.CHARISMA: 1.5,
            SelectionCriterion.WISDOM: 1.3,
            SelectionCriterion.NETWORK_INFLUENCE: 1.4,
            SelectionCriterion.INTEGRITY: 1.2,
            SelectionCriterion.ADAPTABILITY: 1.3
        },
        
        SelectionContext.ECONOMIC_CRISIS: {
            SelectionCriterion.COMPETENCE: 1.5,
            SelectionCriterion.INNOVATION: 1.3,
            SelectionCriterion.PRAGMATISM: 1.3,
            SelectionCriterion.CRISIS_MANAGEMENT: 1.2,
            SelectionCriterion.STRATEGIC_THINKING: 1.2
        },
        
        SelectionContext.REFORM_INITIATIVE: {
            SelectionCriterion.VISION: 1.4,
            SelectionCriterion.INNOVATION: 1.4,
            SelectionCriterion.LEADERSHIP: 1.2,
            SelectionCriterion.INTEGRITY: 1.2,
            SelectionCriterion.STRATEGIC_THINKING: 1.2
        },
        
        SelectionContext.INNOVATION_DRIVE: {
            SelectionCriterion.INNOVATION: 1.5,
            SelectionCriterion.VISION: 1.4,
            SelectionCriterion.ADAPTABILITY: 1.3,
            SelectionCriterion.COMPETENCE: 1.2,
            SelectionCriterion.LEADERSHIP: 1.1
        },
        
        SelectionContext.STABILITY_FOCUS: {
            SelectionCriterion.RELIABILITY: 1.4,
            SelectionCriterion.INTEGRITY: 1.4,
            SelectionCriterion.LOYALTY: 1.3,
            SelectionCriterion.WISDOM: 1.3,
            SelectionCriterion.EXPERIENCE: 1.2
        }
    }
