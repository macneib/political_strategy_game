"""
Advisor Technology Lobbying System

Implements advisor preferences for technology research directions,
lobbying mechanics, and influence on research prioritization.
"""

from typing import Dict, List, Optional, Set, Any, Tuple
from enum import Enum
from pydantic import BaseModel, Field
import random

from .advisor import AdvisorRole, Advisor
from .technology_tree import TechnologyCategory, TechnologyTree


class LobbyingStrategy(str, Enum):
    """Different approaches advisors can take when lobbying for technologies."""
    AGGRESSIVE = "aggressive"          # High pressure, risk of backlash
    DIPLOMATIC = "diplomatic"          # Balanced approach
    SUBTLE = "subtle"                 # Low key, gradual influence
    COALITION_BUILDING = "coalition_building"  # Work with other advisors


class TechnologyAdvocacy(BaseModel):
    """Represents an advisor's advocacy for a specific technology."""
    
    advisor_id: str
    technology_id: str
    support_level: float = Field(ge=0.0, le=1.0)  # How much they support this tech
    lobbying_intensity: float = Field(ge=0.0, le=1.0)  # How hard they're pushing
    strategy: LobbyingStrategy = LobbyingStrategy.DIPLOMATIC
    
    # Reasoning and justification
    justification: str = ""
    personal_benefit: float = Field(default=0.0, ge=0.0, le=1.0)  # Personal gain from this tech
    civilization_benefit: float = Field(default=0.0, ge=0.0, le=1.0)  # Perceived civ benefit
    
    # Lobbying state
    total_lobbying_effort: float = Field(default=0.0)
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    resistance_encountered: float = Field(default=0.0, ge=0.0, le=1.0)


class AdvisorTechnologyPreferences(BaseModel):
    """Technology research preferences for a specific advisor."""
    
    advisor_id: str
    advisor_role: AdvisorRole
    
    # Category preferences (how much they value each category)
    category_preferences: Dict[TechnologyCategory, float] = Field(default_factory=dict)
    
    # Specific technology preferences
    technology_priorities: Dict[str, float] = Field(default_factory=dict)  # tech_id -> priority
    
    # Lobbying behavior
    lobbying_aggressiveness: float = Field(default=0.5, ge=0.0, le=1.0)
    influence_resources: float = Field(default=1.0, ge=0.0)  # Available political capital
    preferred_strategy: LobbyingStrategy = LobbyingStrategy.DIPLOMATIC
    
    # Coalition building
    ally_advisors: Set[str] = Field(default_factory=set)
    rival_advisors: Set[str] = Field(default_factory=set)
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.category_preferences:
            self._initialize_role_based_preferences()
    
    def _initialize_role_based_preferences(self) -> None:
        """Set default category preferences based on advisor role."""
        role_preferences = {
            AdvisorRole.ECONOMIC: {
                TechnologyCategory.ADMINISTRATIVE: 0.8,
                TechnologyCategory.SOCIAL_ENGINEERING: 0.6,
                TechnologyCategory.GOVERNANCE: 0.5,
                TechnologyCategory.INFORMATION_CONTROL: 0.3,
                TechnologyCategory.INTELLIGENCE: 0.2
            },
            AdvisorRole.MILITARY: {
                TechnologyCategory.INTELLIGENCE: 0.9,
                TechnologyCategory.GOVERNANCE: 0.7,
                TechnologyCategory.INFORMATION_CONTROL: 0.6,
                TechnologyCategory.ADMINISTRATIVE: 0.4,
                TechnologyCategory.SOCIAL_ENGINEERING: 0.3
            },
            AdvisorRole.DIPLOMATIC: {
                TechnologyCategory.GOVERNANCE: 0.9,
                TechnologyCategory.INFORMATION_CONTROL: 0.7,
                TechnologyCategory.ADMINISTRATIVE: 0.6,
                TechnologyCategory.INTELLIGENCE: 0.5,
                TechnologyCategory.SOCIAL_ENGINEERING: 0.4
            },
            AdvisorRole.RELIGIOUS: {
                TechnologyCategory.SOCIAL_ENGINEERING: 0.9,
                TechnologyCategory.INFORMATION_CONTROL: 0.7,
                TechnologyCategory.GOVERNANCE: 0.6,
                TechnologyCategory.ADMINISTRATIVE: 0.4,
                TechnologyCategory.INTELLIGENCE: 0.2
            },
            AdvisorRole.SECURITY: {
                TechnologyCategory.INTELLIGENCE: 1.0,
                TechnologyCategory.INFORMATION_CONTROL: 0.8,
                TechnologyCategory.GOVERNANCE: 0.6,
                TechnologyCategory.ADMINISTRATIVE: 0.5,
                TechnologyCategory.SOCIAL_ENGINEERING: 0.3
            },
            AdvisorRole.CULTURAL: {
                TechnologyCategory.SOCIAL_ENGINEERING: 0.8,
                TechnologyCategory.INFORMATION_CONTROL: 0.7,
                TechnologyCategory.GOVERNANCE: 0.5,
                TechnologyCategory.ADMINISTRATIVE: 0.4,
                TechnologyCategory.INTELLIGENCE: 0.2
            }
        }
        
        if self.advisor_role in role_preferences:
            self.category_preferences = role_preferences[self.advisor_role]
        else:
            # Default preferences for unknown roles
            self.category_preferences = {cat: 0.5 for cat in TechnologyCategory}


class AdvisorLobbyingManager(BaseModel):
    """Manages advisor lobbying for technology research."""
    
    civilization_id: str
    current_turn: int = Field(default=1)
    
    # Advisor preferences and lobbying
    advisor_preferences: Dict[str, AdvisorTechnologyPreferences] = Field(default_factory=dict)
    active_advocacy: Dict[str, TechnologyAdvocacy] = Field(default_factory=dict)  # advocacy_id -> advocacy
    
    # Lobbying outcomes and history
    lobbying_history: List[Dict[str, Any]] = Field(default_factory=list)
    successful_lobbying: Dict[str, int] = Field(default_factory=dict)  # advisor_id -> success_count
    
    # Coalition dynamics
    advisor_coalitions: Dict[str, Set[str]] = Field(default_factory=dict)  # tech_id -> advisor_ids
    coalition_strength: Dict[str, float] = Field(default_factory=dict)  # tech_id -> total_strength
    
    def register_advisor(self, advisor: Advisor) -> None:
        """Register an advisor and initialize their technology preferences."""
        preferences = AdvisorTechnologyPreferences(
            advisor_id=advisor.id,
            advisor_role=advisor.role,
            lobbying_aggressiveness=advisor.personality.ambition if hasattr(advisor, 'personality') else 0.5,
            influence_resources=advisor.influence if hasattr(advisor, 'influence') else 1.0
        )
        
        # Adjust lobbying style based on personality
        if hasattr(advisor, 'personality'):
            if advisor.personality.corruption > 0.7:
                preferences.preferred_strategy = LobbyingStrategy.SUBTLE
            elif advisor.personality.ambition > 0.7:
                preferences.preferred_strategy = LobbyingStrategy.AGGRESSIVE
            elif advisor.personality.charisma > 0.7:
                preferences.preferred_strategy = LobbyingStrategy.DIPLOMATIC
            else:
                preferences.preferred_strategy = LobbyingStrategy.COALITION_BUILDING
        
        self.advisor_preferences[advisor.id] = preferences
    
    def update_technology_preferences(self, advisor_id: str, tech_id: str, 
                                    priority: float, justification: str = "") -> bool:
        """Update an advisor's priority for a specific technology."""
        if advisor_id not in self.advisor_preferences:
            return False
        
        preferences = self.advisor_preferences[advisor_id]
        preferences.technology_priorities[tech_id] = max(0.0, min(1.0, priority))
        
        return True
    
    def start_technology_advocacy(self, advisor_id: str, tech_id: str,
                                support_level: float, justification: str = "") -> str:
        """Start an advisor's advocacy campaign for a technology."""
        if advisor_id not in self.advisor_preferences:
            return ""
        
        preferences = self.advisor_preferences[advisor_id]
        
        advocacy_id = f"{advisor_id}_{tech_id}_{self.current_turn}"
        advocacy = TechnologyAdvocacy(
            advisor_id=advisor_id,
            technology_id=tech_id,
            support_level=support_level,
            lobbying_intensity=preferences.lobbying_aggressiveness,
            strategy=preferences.preferred_strategy,
            justification=justification,
            personal_benefit=self._calculate_personal_benefit(advisor_id, tech_id),
            civilization_benefit=self._calculate_civilization_benefit(advisor_id, tech_id)
        )
        
        self.active_advocacy[advocacy_id] = advocacy
        return advocacy_id
    
    def _calculate_personal_benefit(self, advisor_id: str, tech_id: str) -> float:
        """Calculate how much an advisor would personally benefit from a technology."""
        if advisor_id not in self.advisor_preferences:
            return 0.0
        
        preferences = self.advisor_preferences[advisor_id]
        
        # Base benefit from role alignment (simplified calculation)
        role_alignment = 0.5  # Default
        
        # Technology-specific benefits could be added here based on
        # technology effects and advisor role
        
        return min(1.0, role_alignment)
    
    def _calculate_civilization_benefit(self, advisor_id: str, tech_id: str) -> float:
        """Calculate perceived civilization benefit from advisor's perspective."""
        if advisor_id not in self.advisor_preferences:
            return 0.5
        
        preferences = self.advisor_preferences[advisor_id]
        
        # Advisors perceive benefits differently based on their role and priorities
        # This is a simplified calculation - could be enhanced with more sophisticated logic
        base_benefit = 0.6  # Assume most technologies are generally beneficial
        
        # Role-based perspective modifier
        role_modifier = 1.0
        if preferences.advisor_role == AdvisorRole.ECONOMIC:
            # Economic advisors might overvalue economic technologies
            role_modifier = 1.2
        elif preferences.advisor_role == AdvisorRole.MILITARY:
            # Military advisors might undervalue social technologies
            role_modifier = 0.8
        
        return min(1.0, base_benefit * role_modifier)
    
    def process_lobbying_turn(self, technology_tree: TechnologyTree) -> Dict[str, Any]:
        """Process one turn of advisor lobbying activities."""
        results = {
            "lobbying_activities": [],
            "technology_influence_changes": {},
            "coalition_formations": [],
            "conflicts": [],
            "successful_advocacy": []
        }
        
        # Process each active advocacy
        for advocacy_id, advocacy in self.active_advocacy.items():
            lobbying_result = self._process_individual_lobbying(advocacy, technology_tree)
            results["lobbying_activities"].append(lobbying_result)
            
            # Apply influence to technology tree
            if advocacy.technology_id in technology_tree.nodes:
                node = technology_tree.nodes[advocacy.technology_id]
                
                # Update advisor support
                node.advisor_support[advocacy.advisor_id] = advocacy.support_level
                
                # Update lobbying pressure
                pressure_increase = advocacy.lobbying_intensity * lobbying_result["effectiveness"]
                node.lobbying_pressure += pressure_increase
                
                if advocacy.technology_id not in results["technology_influence_changes"]:
                    results["technology_influence_changes"][advocacy.technology_id] = {
                        "total_support": 0.0,
                        "lobbying_pressure": 0.0,
                        "supporting_advisors": []
                    }
                
                tech_changes = results["technology_influence_changes"][advocacy.technology_id]
                tech_changes["total_support"] += advocacy.support_level
                tech_changes["lobbying_pressure"] += pressure_increase
                tech_changes["supporting_advisors"].append(advocacy.advisor_id)
        
        # Process coalition building
        coalition_results = self._process_coalition_building(technology_tree)
        results["coalition_formations"] = coalition_results["formations"]
        results["conflicts"] = coalition_results["conflicts"]
        
        # Clean up completed advocacy campaigns
        self._cleanup_completed_advocacy()
        
        self.current_turn += 1
        return results
    
    def _process_individual_lobbying(self, advocacy: TechnologyAdvocacy, 
                                   technology_tree: TechnologyTree) -> Dict[str, Any]:
        """Process lobbying for a single advocacy campaign."""
        result = {
            "advocacy_id": f"{advocacy.advisor_id}_{advocacy.technology_id}",
            "advisor_id": advocacy.advisor_id,
            "technology_id": advocacy.technology_id,
            "strategy": advocacy.strategy.value,
            "effectiveness": 0.0,
            "resistance": 0.0,
            "outcome": "ongoing"
        }
        
        # Calculate base effectiveness based on strategy
        strategy_effectiveness = {
            LobbyingStrategy.AGGRESSIVE: 0.8,
            LobbyingStrategy.DIPLOMATIC: 0.6,
            LobbyingStrategy.SUBTLE: 0.4,
            LobbyingStrategy.COALITION_BUILDING: 0.7
        }
        
        base_effectiveness = strategy_effectiveness[advocacy.strategy]
        
        # Modify effectiveness based on various factors
        advisor_prefs = self.advisor_preferences.get(advocacy.advisor_id)
        if advisor_prefs:
            # Influence resources affect effectiveness
            resource_modifier = min(1.5, advisor_prefs.influence_resources)
            base_effectiveness *= resource_modifier
            
            # Success history provides bonus
            success_count = self.successful_lobbying.get(advocacy.advisor_id, 0)
            experience_bonus = min(0.3, success_count * 0.05)
            base_effectiveness += experience_bonus
        
        # Random factor for uncertainty
        random_factor = 0.8 + (random.random() * 0.4)  # nosec B311 - Using random for game mechanics, not security (0.8 to 1.2)
        final_effectiveness = base_effectiveness * random_factor
        
        # Calculate resistance
        resistance = self._calculate_lobbying_resistance(advocacy, technology_tree)
        
        # Update advocacy state
        advocacy.total_lobbying_effort += advocacy.lobbying_intensity
        advocacy.success_rate = final_effectiveness
        advocacy.resistance_encountered = resistance
        
        result["effectiveness"] = final_effectiveness
        result["resistance"] = resistance
        
        # Determine if lobbying succeeds this turn
        if final_effectiveness > resistance + 0.3:  # Threshold for success
            result["outcome"] = "successful"
            self.successful_lobbying[advocacy.advisor_id] = (
                self.successful_lobbying.get(advocacy.advisor_id, 0) + 1
            )
        elif resistance > final_effectiveness + 0.5:  # Threshold for failure
            result["outcome"] = "failed"
        
        return result
    
    def _calculate_lobbying_resistance(self, advocacy: TechnologyAdvocacy,
                                     technology_tree: TechnologyTree) -> float:
        """Calculate resistance to advisor lobbying."""
        base_resistance = 0.3  # Base bureaucratic resistance
        
        # Resistance from competing priorities
        available_techs = technology_tree.get_available_technologies()
        if len(available_techs) > 5:  # Many options create more resistance
            base_resistance += 0.2
        
        # Resistance from other advisors with different priorities
        competing_advocacy = 0.0
        for other_advocacy in self.active_advocacy.values():
            if (other_advocacy.advisor_id != advocacy.advisor_id and 
                other_advocacy.technology_id != advocacy.technology_id):
                competing_advocacy += other_advocacy.lobbying_intensity * 0.1
        
        total_resistance = min(1.0, base_resistance + competing_advocacy)
        return total_resistance
    
    def _process_coalition_building(self, technology_tree: TechnologyTree) -> Dict[str, Any]:
        """Process coalition building between advisors."""
        results = {
            "formations": [],
            "conflicts": []
        }
        
        # Group advocacy by technology
        tech_advocates = {}
        for advocacy in self.active_advocacy.values():
            tech_id = advocacy.technology_id
            if tech_id not in tech_advocates:
                tech_advocates[tech_id] = []
            tech_advocates[tech_id].append(advocacy)
        
        # Look for coalition opportunities
        for tech_id, advocates in tech_advocates.items():
            if len(advocates) > 1:
                # Multiple advisors support the same technology
                coalition_strength = sum(adv.support_level for adv in advocates)
                
                if coalition_strength > 1.5:  # Threshold for meaningful coalition
                    coalition_id = f"coalition_{tech_id}_{self.current_turn}"
                    coalition_members = [adv.advisor_id for adv in advocates]
                    
                    # Update coalition tracking
                    self.advisor_coalitions[tech_id] = set(coalition_members)
                    self.coalition_strength[tech_id] = coalition_strength
                    
                    # Update technology tree with coalition bonus
                    if tech_id in technology_tree.nodes:
                        node = technology_tree.nodes[tech_id]
                        node.lobbying_pressure += coalition_strength * 0.2  # Coalition bonus
                    
                    results["formations"].append({
                        "coalition_id": coalition_id,
                        "technology_id": tech_id,
                        "members": coalition_members,
                        "strength": coalition_strength
                    })
        
        return results
    
    def _cleanup_completed_advocacy(self) -> None:
        """Remove completed or expired advocacy campaigns."""
        to_remove = []
        
        for advocacy_id, advocacy in self.active_advocacy.items():
            # Remove if lobbying effort is very high (campaign exhausted)
            if advocacy.total_lobbying_effort > 5.0:
                to_remove.append(advocacy_id)
            # Remove if resistance is overwhelming
            elif advocacy.resistance_encountered > 0.8:
                to_remove.append(advocacy_id)
        
        for advocacy_id in to_remove:
            del self.active_advocacy[advocacy_id]
    
    def get_technology_priorities_by_advisor_influence(self, 
                                                     available_technologies: List[str]) -> List[Tuple[str, float]]:
        """Calculate technology priorities based on advisor influence and lobbying."""
        tech_scores = {}
        
        for tech_id in available_technologies:
            total_influence = 0.0
            
            # Sum influence from all advisors
            for advisor_id, preferences in self.advisor_preferences.items():
                # Base preference from category and specific tech priorities
                tech_priority = preferences.technology_priorities.get(tech_id, 0.0)
                advisor_influence = preferences.influence_resources
                
                total_influence += tech_priority * advisor_influence
            
            # Add coalition bonuses
            if tech_id in self.coalition_strength:
                total_influence += self.coalition_strength[tech_id] * 0.5
            
            tech_scores[tech_id] = total_influence
        
        # Sort by influence score
        sorted_techs = sorted(tech_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_techs
    
    def suggest_research_queue_by_lobbying(self, technology_tree: TechnologyTree,
                                         max_queue_length: int = 5) -> List[str]:
        """Suggest a research queue based on advisor lobbying and preferences."""
        available_techs = technology_tree.get_available_technologies()
        prioritized_techs = self.get_technology_priorities_by_advisor_influence(available_techs)
        
        suggested_queue = []
        for tech_id, influence_score in prioritized_techs:
            if len(suggested_queue) >= max_queue_length:
                break
            
            # Only include technologies with meaningful support
            if influence_score > 0.5:
                suggested_queue.append(tech_id)
        
        return suggested_queue
    
    def get_lobbying_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of current lobbying activities."""
        active_campaigns = len(self.active_advocacy)
        active_coalitions = len(self.advisor_coalitions)
        
        # Most influential advisors
        advisor_influence = {}
        for advisor_id, preferences in self.advisor_preferences.items():
            influence = preferences.influence_resources
            success_rate = self.successful_lobbying.get(advisor_id, 0) / max(1, self.current_turn // 10)
            advisor_influence[advisor_id] = influence * (1 + success_rate)
        
        top_advisors = sorted(advisor_influence.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Most contested technologies
        contested_techs = {}
        for advocacy in self.active_advocacy.values():
            tech_id = advocacy.technology_id
            if tech_id not in contested_techs:
                contested_techs[tech_id] = 0
            contested_techs[tech_id] += 1
        
        most_contested = sorted(contested_techs.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "civilization_id": self.civilization_id,
            "current_turn": self.current_turn,
            "active_campaigns": active_campaigns,
            "active_coalitions": active_coalitions,
            "registered_advisors": len(self.advisor_preferences),
            "top_influential_advisors": top_advisors,
            "most_contested_technologies": most_contested,
            "total_successful_lobbying": sum(self.successful_lobbying.values())
        }
