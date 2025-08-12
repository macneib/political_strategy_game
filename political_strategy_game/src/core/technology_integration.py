"""
Technology Tree Integration Layer

Connects the technology tree system with existing game systems including
resource management, civilization progression, and advisor interactions.
"""

from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field

from .technology_tree import TechnologyTree, TechnologyCategory
from .advisor_technology import AdvisorLobbyingManager
from .resources import ResourceManager, TechnologyState
from .civilization import Civilization
from .advisor_enhanced import AdvisorCouncil
from .espionage import EspionageManager


class TechnologyResearchManager(BaseModel):
    """Manages technology research integration with existing game systems."""
    
    civilization_id: str
    current_turn: int = Field(default=1)
    
    # Core systems
    technology_tree: TechnologyTree
    advisor_lobbying: AdvisorLobbyingManager = Field(default=None)
    
    # Integration state
    active_research: Optional[str] = None  # Currently researching technology
    research_queue: List[str] = Field(default_factory=list)
    research_progress: Dict[str, float] = Field(default_factory=dict)  # tech_id -> progress (0-1)
    
    # Research modifiers
    research_speed_modifier: float = Field(default=1.0, ge=0.1)
    available_research_capacity: float = Field(default=1.0, ge=0.0)
    
    # Historical tracking
    completed_technologies: List[str] = Field(default_factory=list)
    research_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    def __init__(self, **data):
        # Initialize advisor lobbying manager if not provided
        if 'advisor_lobbying' not in data or data['advisor_lobbying'] is None:
            data['advisor_lobbying'] = AdvisorLobbyingManager(
                civilization_id=data.get('civilization_id', 'unknown'),
                current_turn=data.get('current_turn', 1)
            )
        super().__init__(**data)
    
    def update_from_resource_manager(self, resource_manager: ResourceManager) -> None:
        """Update research capacity and modifiers from resource manager."""
        tech_state = resource_manager.technology_state
        
        # Research capacity based on economic resources
        economic_factor = min(2.0, resource_manager.economic_state.gdp / 1000)
        tech_factor = min(2.0, tech_state.research_points_per_turn / 10)
        
        self.available_research_capacity = economic_factor * tech_factor / 2
        
        # Research speed modifiers based on tech levels
        infrastructure_bonus = resource_manager.economic_state.infrastructure_level / 200 if hasattr(resource_manager.economic_state, 'infrastructure_level') else 0.25
        tech_bonus = (tech_state.military_tech_level + tech_state.economic_tech_level) / 4
        
        self.research_speed_modifier = 1.0 + infrastructure_bonus + tech_bonus
        
        # Update technology tree with resource-based unlocks
        self._update_resource_based_prerequisites(resource_manager)
    
    def _update_resource_based_prerequisites(self, resource_manager: ResourceManager) -> None:
        """Update technology prerequisites based on resource availability."""
        # Some technologies might require minimum resource levels
        resource_thresholds = {
            "advanced_surveillance": {"economic.gdp": 2000, "military.intelligence_budget": 500},
            "mass_media_control": {"economic.gdp": 1500, "social.media_presence": 70},
            "digital_governance": {"technology.digital_infrastructure": 80},
            "social_credit_system": {"technology.surveillance_capacity": 75},
        }
        
        for tech_id, requirements in resource_thresholds.items():
            if tech_id in self.technology_tree.nodes:
                node = self.technology_tree.nodes[tech_id]
                
                # Check if resource requirements are met
                requirements_met = True
                for requirement, threshold in requirements.items():
                    resource_path = requirement.split('.')
                    if len(resource_path) == 2:
                        category, attribute = resource_path
                    if category == "economic":
                        value = getattr(resource_manager.economic_state, attribute, 0)
                    elif category == "military":
                        value = getattr(resource_manager.military_state, attribute, 0)
                    elif category == "technology":
                        value = getattr(resource_manager.technology_state, attribute, 0)
                    else:
                        value = 0
                    
                    if value < threshold:
                        requirements_met = False
                        break
                
                # Update availability based on resource requirements
                if not requirements_met and tech_id in self.technology_tree.get_available_technologies():
                    # Mark as resource-locked
                    node.resource_locked = True
                elif requirements_met:
                    node.resource_locked = False
    
    def register_advisors_from_council(self, advisor_council: AdvisorCouncil) -> None:
        """Register all advisors from the council for technology lobbying."""
        for advisor in advisor_council.advisors.values():
            self.advisor_lobbying.register_advisor(advisor)
    
    def process_advisor_lobbying_turn(self) -> Dict[str, Any]:
        """Process advisor lobbying and update research priorities."""
        lobbying_results = self.advisor_lobbying.process_lobbying_turn(self.technology_tree)
        
        # Update research queue based on lobbying influence
        if not self.research_queue or len(self.research_queue) < 3:
            suggested_queue = self.advisor_lobbying.suggest_research_queue_by_lobbying(
                self.technology_tree, max_queue_length=5
            )
            
            # Merge with existing queue, avoiding duplicates
            for tech_id in suggested_queue:
                if tech_id not in self.research_queue and tech_id not in self.completed_technologies:
                    self.research_queue.append(tech_id)
        
        return lobbying_results
    
    def start_technology_research(self, tech_id: str, force: bool = False) -> bool:
        """Start researching a specific technology."""
        if not self.can_research_technology(tech_id):
            return False
        
        if self.active_research and not force:
            # Add to queue instead
            if tech_id not in self.research_queue:
                self.research_queue.append(tech_id)
            return True
        
        # Start research
        self.active_research = tech_id
        if tech_id not in self.research_progress:
            self.research_progress[tech_id] = 0.0
        
        # Remove from queue if it was there
        if tech_id in self.research_queue:
            self.research_queue.remove(tech_id)
        
        # Record research start
        self.research_history.append({
            "turn": self.current_turn,
            "action": "research_started",
            "technology_id": tech_id,
            "advisor_influence": self._get_technology_advisor_influence(tech_id)
        })
        
        return True
    
    def can_research_technology(self, tech_id: str) -> bool:
        """Check if a technology can be researched."""
        if tech_id in self.completed_technologies:
            return False
        
        available_techs = self.technology_tree.get_available_technologies()
        return tech_id in available_techs
    
    def _get_technology_advisor_influence(self, tech_id: str) -> Dict[str, float]:
        """Get advisor influence levels for a specific technology."""
        influence_data = {}
        
        for advisor_id, preferences in self.advisor_lobbying.advisor_preferences.items():
            tech_priority = preferences.technology_priorities.get(tech_id, 0.0)
            influence_data[advisor_id] = tech_priority
        
        return influence_data
    
    def advance_research_progress(self, turns: int = 1) -> Dict[str, Any]:
        """Advance research progress and handle completion."""
        results = {
            "progress_made": {},
            "technologies_completed": [],
            "research_events": []
        }
        
        if not self.active_research:
            # Try to start next research from queue
            if self.research_queue:
                next_tech = self.research_queue[0]
                if self.start_technology_research(next_tech, force=True):
                    results["research_events"].append({
                        "type": "research_auto_started",
                        "technology_id": next_tech
                    })
        
        if self.active_research:
            tech_id = self.active_research
            
            # Calculate research progress based on capacity and modifiers
            base_progress = 0.1 * turns  # Base 10% per turn
            capacity_modifier = min(2.0, self.available_research_capacity)
            speed_modifier = self.research_speed_modifier
            
            # Advisor influence can speed up research
            advisor_boost = self._calculate_advisor_research_boost(tech_id)
            
            total_progress = base_progress * capacity_modifier * speed_modifier * (1 + advisor_boost)
            
            # Update progress
            current_progress = self.research_progress.get(tech_id, 0.0)
            new_progress = min(1.0, current_progress + total_progress)
            self.research_progress[tech_id] = new_progress
            
            results["progress_made"][tech_id] = total_progress
            
            # Check for completion
            if new_progress >= 1.0:
                self._complete_technology_research(tech_id)
                results["technologies_completed"].append(tech_id)
                
                # Start next research automatically
                self.active_research = None
                if self.research_queue:
                    next_tech = self.research_queue[0]
                    if self.start_technology_research(next_tech, force=True):
                        results["research_events"].append({
                            "type": "research_auto_continued",
                            "completed_technology": tech_id,
                            "new_technology": next_tech
                        })
        
        return results
    
    def _calculate_advisor_research_boost(self, tech_id: str) -> float:
        """Calculate research speed boost from advisor support."""
        total_boost = 0.0
        
        # Get lobbying pressure for this technology
        if tech_id in self.technology_tree.nodes:
            node = self.technology_tree.nodes[tech_id]
            lobbying_pressure = node.lobbying_pressure
            
            # Convert lobbying pressure to research boost (max 50% boost)
            pressure_boost = min(0.5, lobbying_pressure * 0.1)
            total_boost += pressure_boost
        
        # Coalition bonuses
        if tech_id in self.advisor_lobbying.coalition_strength:
            coalition_strength = self.advisor_lobbying.coalition_strength[tech_id]
            coalition_boost = min(0.3, coalition_strength * 0.05)
            total_boost += coalition_boost
        
        return total_boost
    
    def _complete_technology_research(self, tech_id: str) -> None:
        """Complete research of a technology and apply its effects."""
        # Mark as completed
        self.completed_technologies.append(tech_id)
        self.technology_tree.research_technology(tech_id)
        
        # Remove from progress tracking
        if tech_id in self.research_progress:
            del self.research_progress[tech_id]
        
        # Record completion
        self.research_history.append({
            "turn": self.current_turn,
            "action": "research_completed",
            "technology_id": tech_id,
            "advisor_influence": self._get_technology_advisor_influence(tech_id)
        })
        
        # Update advisor success tracking
        for advisor_id, preferences in self.advisor_lobbying.advisor_preferences.items():
            if preferences.technology_priorities.get(tech_id, 0.0) > 0.5:
                # Advisor successfully lobbied for this technology
                self.advisor_lobbying.successful_lobbying[advisor_id] = (
                    self.advisor_lobbying.successful_lobbying.get(advisor_id, 0) + 1
                )
    
    def apply_technology_effects_to_resources(self, resource_manager: ResourceManager,
                                            tech_id: str) -> Dict[str, Any]:
        """Apply completed technology effects to resource manager."""
        effects_applied = {
            "economic_effects": {},
            "military_effects": {},
            "technology_effects": {},
            "political_effects": {},
            "resource_modifiers": {},
            "advisor_unlocks": [],
            "espionage_enhancements": {}
        }
        
        if tech_id not in self.technology_tree.nodes:
            return effects_applied
        
        technology = self.technology_tree.nodes[tech_id].technology
        
        # Apply political effects (these would need custom handling based on effect type)
        for effect, value in technology.political_effects.items():
            effects_applied["political_effects"][effect] = value
            # Map to economic/military/technology effects based on effect type
            if "economic" in effect or "resource" in effect:
                effects_applied["economic_effects"][effect] = value
            elif "military" in effect or "defense" in effect:
                effects_applied["military_effects"][effect] = value
            else:
                effects_applied["technology_effects"][effect] = value
        
        # Apply resource modifiers
        for effect, value in technology.resource_modifiers.items():
            effects_applied["resource_modifiers"][effect] = value
            effects_applied["economic_effects"][effect] = value
            # Could apply to resource manager if specific effects are defined
        
        # Record advisor unlocks
        effects_applied["advisor_unlocks"] = list(technology.advisor_unlocks)
        
        # Record espionage enhancements  
        effects_applied["espionage_enhancements"] = technology.espionage_enhancements.copy()
        for enhancement, value in technology.espionage_enhancements.items():
            effects_applied["technology_effects"][enhancement] = value
        
        return effects_applied
    
    def integrate_with_espionage(self, espionage_manager: EspionageManager) -> None:
        """Integrate technology research with espionage capabilities."""
        # Technologies can enhance espionage capabilities
        intelligence_techs = [
            "advanced_surveillance", "digital_monitoring", "behavioral_analysis",
            "social_network_analysis", "predictive_modeling"
        ]
        
        espionage_bonus = 0.0
        for tech_id in intelligence_techs:
            if tech_id in self.completed_technologies:
                espionage_bonus += 0.1  # 10% bonus per intelligence technology
        
        # Apply bonus to espionage manager
        if hasattr(espionage_manager, 'technology_bonus'):
            espionage_manager.technology_bonus = espionage_bonus
        
        # Some technologies might unlock new espionage operations
        if "social_credit_system" in self.completed_technologies:
            # Unlock advanced social monitoring operations
            pass
        
        if "information_warfare_protocols" in self.completed_technologies:
            # Unlock disinformation campaigns
            pass
    
    def get_technology_recommendations(self, context: Dict[str, Any]) -> List[Tuple[str, float, str]]:
        """Get technology recommendations based on current situation."""
        recommendations = []
        available_techs = self.technology_tree.get_available_technologies()
        
        # Analyze current situation
        threats = context.get("current_threats", [])
        resources = context.get("resource_state", {})
        diplomatic_situation = context.get("diplomatic_situation", {})
        
        for tech_id in available_techs:
            if tech_id in self.completed_technologies:
                continue
            
            tech_node = self.technology_tree.nodes[tech_id]
            technology = tech_node.technology
            
            # Calculate recommendation score
            score = 0.0
            reasons = []
            
            # Military threats might prioritize intelligence/defense technologies
            if threats and technology.category in [TechnologyCategory.INTELLIGENCE, TechnologyCategory.GOVERNANCE]:
                score += 0.3
                reasons.append("addresses current security threats")
            
            # Economic needs might prioritize administrative technologies
            economic_stress = resources.get("economic_stress", 0.0)
            if economic_stress > 0.5 and technology.category == TechnologyCategory.ADMINISTRATIVE:
                score += 0.4
                reasons.append("improves economic efficiency")
            
            # Social unrest might prioritize social engineering
            social_unrest = resources.get("social_unrest", 0.0)
            if social_unrest > 0.5 and technology.category == TechnologyCategory.SOCIAL_ENGINEERING:
                score += 0.4
                reasons.append("helps manage social stability")
            
            # Advisor influence
            advisor_support = sum(tech_node.advisor_support.values())
            if advisor_support > 1.0:
                score += min(0.3, advisor_support * 0.1)
                reasons.append("strong advisor support")
            
            # Lobbying pressure
            if tech_node.lobbying_pressure > 0.5:
                score += min(0.2, tech_node.lobbying_pressure * 0.1)
                reasons.append("significant political pressure")
            
            if score > 0.2:  # Only recommend technologies with meaningful scores
                reason_text = "; ".join(reasons) if reasons else "general development"
                recommendations.append((tech_id, score, reason_text))
        
        # Sort by score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:5]  # Top 5 recommendations
    
    def advance_turn(self) -> Dict[str, Any]:
        """Advance one turn for the technology research manager."""
        self.current_turn += 1
        self.advisor_lobbying.current_turn = self.current_turn
        
        # Process advisor lobbying
        lobbying_results = self.process_advisor_lobbying_turn()
        
        # Advance research progress
        research_results = self.advance_research_progress()
        
        return {
            "turn": self.current_turn,
            "lobbying_results": lobbying_results,
            "research_results": research_results,
            "active_research": self.active_research,
            "research_queue": self.research_queue.copy(),
            "completed_technologies": len(self.completed_technologies)
        }
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary of technology research."""
        return {
            "civilization_id": self.civilization_id,
            "current_turn": self.current_turn,
            "active_research": {
                "technology_id": self.active_research,
                "progress": self.research_progress.get(self.active_research, 0.0) if self.active_research else 0.0
            },
            "research_queue": self.research_queue.copy(),
            "completed_technologies": len(self.completed_technologies),
            "available_technologies": len(self.technology_tree.get_available_technologies()),
            "research_capacity": self.available_research_capacity,
            "research_speed": self.research_speed_modifier,
            "advisor_lobbying": self.advisor_lobbying.get_lobbying_summary(),
            "recent_completions": [
                entry for entry in self.research_history[-5:]
                if entry["action"] == "research_completed"
            ]
        }
