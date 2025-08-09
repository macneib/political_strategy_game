"""
Resource management system for civilizations.

Handles economic, military, and technological resources that influence
political dynamics and advisor decision-making.
"""

from typing import Dict, List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class ResourceType(str, Enum):
    """Types of civilization resources."""
    ECONOMIC = "economic"
    MILITARY = "military"
    TECHNOLOGY = "technology"
    POPULATION = "population"
    FOOD = "food"
    MATERIALS = "materials"


class EconomicState(BaseModel):
    """Economic status of the civilization."""
    
    treasury: float = Field(default=1000.0, ge=0.0)
    income_per_turn: float = Field(default=100.0)
    expenses_per_turn: float = Field(default=80.0)
    
    # Economic health indicators
    gdp: float = Field(default=10000.0, ge=0.0)
    unemployment_rate: float = Field(default=0.05, ge=0.0, le=1.0)
    inflation_rate: float = Field(default=0.02, ge=-0.1, le=1.0)
    
    # Trade and commerce
    trade_routes: Dict[str, float] = Field(default_factory=dict)  # civilization_id -> trade_value
    trade_income: float = Field(default=0.0)
    embargo_list: Set[str] = Field(default_factory=set)  # civilizations under embargo
    
    # Economic stability
    economic_stability: float = Field(default=0.7, ge=0.0, le=1.0)
    market_confidence: float = Field(default=0.6, ge=0.0, le=1.0)


class MilitaryState(BaseModel):
    """Military status of the civilization."""
    
    # Basic military metrics
    army_size: int = Field(default=1000, ge=0)
    navy_size: int = Field(default=50, ge=0)
    air_force_size: int = Field(default=0, ge=0)
    
    # Military effectiveness
    military_strength: float = Field(default=0.6, ge=0.0, le=1.0)
    unit_quality: float = Field(default=0.5, ge=0.0, le=1.0)
    morale: float = Field(default=0.7, ge=0.0, le=1.0)
    
    # Military logistics
    supply_lines: float = Field(default=0.8, ge=0.0, le=1.0)
    military_budget: float = Field(default=200.0, ge=0.0)
    recruitment_rate: float = Field(default=0.02, ge=0.0, le=1.0)
    
    # Military threats and capabilities
    active_conflicts: Set[str] = Field(default_factory=set)  # civilization_ids in conflict
    defensive_pacts: Set[str] = Field(default_factory=set)  # defensive alliance partners
    intelligence_network: float = Field(default=0.3, ge=0.0, le=1.0)


class TechnologyState(BaseModel):
    """Technology and research status of the civilization."""
    
    # Research capabilities
    research_points_per_turn: float = Field(default=10.0, ge=0.0)
    accumulated_research: float = Field(default=0.0, ge=0.0)
    
    # Technology levels (0.0 = stone age, 1.0 = future tech)
    military_tech_level: float = Field(default=0.3, ge=0.0, le=1.0)
    economic_tech_level: float = Field(default=0.3, ge=0.0, le=1.0)
    political_tech_level: float = Field(default=0.2, ge=0.0, le=1.0)
    
    # Active research projects
    current_research: Optional[str] = Field(default=None)
    research_queue: List[str] = Field(default_factory=list)
    completed_techs: Set[str] = Field(default_factory=set)
    
    # Innovation and knowledge
    innovation_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    knowledge_sharing: Dict[str, float] = Field(default_factory=dict)  # civ_id -> sharing_level


class ResourceEvent(BaseModel):
    """Resource-related events that can occur."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resource_type: ResourceType
    event_name: str
    description: str
    
    # Event effects
    economic_impact: float = Field(default=0.0)
    military_impact: float = Field(default=0.0)
    technology_impact: float = Field(default=0.0)
    political_impact: float = Field(default=0.0)
    
    # Event duration and timing
    duration_turns: int = Field(default=1, ge=1)
    turns_remaining: int = Field(default=1, ge=0)
    severity: float = Field(default=0.5, ge=0.0, le=1.0)


class ResourceManager(BaseModel):
    """Manages all resource systems for a civilization."""
    
    civilization_id: str
    current_turn: int = Field(default=1)
    
    # Resource states
    economic_state: EconomicState = Field(default_factory=EconomicState)
    military_state: MilitaryState = Field(default_factory=MilitaryState)
    technology_state: TechnologyState = Field(default_factory=TechnologyState)
    
    # Active resource events
    active_events: List[ResourceEvent] = Field(default_factory=list)
    event_history: List[ResourceEvent] = Field(default_factory=list)
    
    def update_resources(self, turns: int = 1) -> Dict[str, any]:
        """Update all resource states for the given number of turns."""
        results = {
            "economic_changes": {},
            "military_changes": {},
            "technology_changes": {},
            "events_processed": [],
            "new_events": []
        }
        
        for turn in range(turns):
            self.current_turn += 1
            
            # Update economic resources
            economic_changes = self._update_economy()
            results["economic_changes"].update(economic_changes)
            
            # Update military resources
            military_changes = self._update_military()
            results["military_changes"].update(military_changes)
            
            # Update technology resources
            tech_changes = self._update_technology()
            results["technology_changes"].update(tech_changes)
            
            # Process active events
            processed_events = self._process_resource_events()
            results["events_processed"].extend(processed_events)
            
            # Check for new events
            new_events = self._check_for_new_events()
            results["new_events"].extend(new_events)
        
        return results
    
    def _update_economy(self) -> Dict[str, float]:
        """Update economic state for one turn."""
        changes = {}
        
        # Calculate net income
        net_income = self.economic_state.income_per_turn - self.economic_state.expenses_per_turn
        net_income += self.economic_state.trade_income
        
        # Update treasury
        old_treasury = self.economic_state.treasury
        self.economic_state.treasury += net_income
        changes["treasury_change"] = self.economic_state.treasury - old_treasury
        
        # Update economic stability based on trends
        if net_income > 0:
            self.economic_state.economic_stability = min(1.0, self.economic_state.economic_stability + 0.01)
            self.economic_state.market_confidence = min(1.0, self.economic_state.market_confidence + 0.005)
        elif net_income < -50:
            self.economic_state.economic_stability = max(0.0, self.economic_state.economic_stability - 0.02)
            self.economic_state.market_confidence = max(0.0, self.economic_state.market_confidence - 0.01)
        
        changes["stability_change"] = self.economic_state.economic_stability
        changes["confidence_change"] = self.economic_state.market_confidence
        
        return changes
    
    def _update_military(self) -> Dict[str, float]:
        """Update military state for one turn."""
        changes = {}
        
        # Military maintenance costs
        maintenance_cost = (self.military_state.army_size * 0.5 + 
                          self.military_state.navy_size * 2.0 + 
                          self.military_state.air_force_size * 5.0)
        
        changes["maintenance_cost"] = maintenance_cost
        
        # Recruitment if budget allows
        if self.military_state.military_budget > maintenance_cost:
            available_budget = self.military_state.military_budget - maintenance_cost
            potential_recruits = int(available_budget / 10.0 * self.military_state.recruitment_rate)
            
            old_army = self.military_state.army_size
            self.military_state.army_size += potential_recruits
            changes["army_growth"] = self.military_state.army_size - old_army
        
        # Update morale based on budget adequacy
        budget_ratio = self.military_state.military_budget / max(1.0, maintenance_cost)
        if budget_ratio >= 1.2:
            self.military_state.morale = min(1.0, self.military_state.morale + 0.01)
        elif budget_ratio < 0.8:
            self.military_state.morale = max(0.0, self.military_state.morale - 0.02)
        
        changes["morale_change"] = self.military_state.morale
        
        return changes
    
    def _update_technology(self) -> Dict[str, float]:
        """Update technology state for one turn."""
        changes = {}
        
        # Accumulate research points
        old_research = self.technology_state.accumulated_research
        self.technology_state.accumulated_research += self.technology_state.research_points_per_turn
        changes["research_progress"] = self.technology_state.accumulated_research - old_research
        
        # Check if current research is complete
        if self.technology_state.current_research:
            research_cost = self._get_research_cost(self.technology_state.current_research)
            if self.technology_state.accumulated_research >= research_cost:
                # Complete research
                self.technology_state.completed_techs.add(self.technology_state.current_research)
                self.technology_state.accumulated_research -= research_cost
                
                # Apply technology effects
                tech_effects = self._apply_technology_effects(self.technology_state.current_research)
                changes.update(tech_effects)
                
                # Start next research in queue
                if self.technology_state.research_queue:
                    self.technology_state.current_research = self.technology_state.research_queue.pop(0)
                else:
                    self.technology_state.current_research = None
                
                changes["completed_research"] = self.technology_state.current_research
        
        return changes
    
    def _process_resource_events(self) -> List[ResourceEvent]:
        """Process active resource events for this turn."""
        processed = []
        remaining_events = []
        
        for event in self.active_events:
            event.turns_remaining -= 1
            
            if event.turns_remaining <= 0:
                # Event completed, apply final effects
                self._apply_event_effects(event)
                processed.append(event)
                self.event_history.append(event)
            else:
                # Event continues, apply ongoing effects
                self._apply_event_effects(event, partial=True)
                remaining_events.append(event)
        
        self.active_events = remaining_events
        return processed
    
    def _check_for_new_events(self) -> List[ResourceEvent]:
        """Check if new resource events should be triggered."""
        new_events = []
        
        # Economic crisis check
        if (self.economic_state.treasury < 100 and 
            self.economic_state.economic_stability < 0.3):
            
            crisis_event = ResourceEvent(
                resource_type=ResourceType.ECONOMIC,
                event_name="Economic Crisis",
                description="The civilization faces severe economic difficulties",
                economic_impact=-0.2,
                political_impact=-0.1,
                duration_turns=3,
                turns_remaining=3,
                severity=0.8
            )
            new_events.append(crisis_event)
            self.active_events.append(crisis_event)
        
        # Military uprising check
        if (self.military_state.morale < 0.3 and 
            self.military_state.military_budget < 50):
            
            uprising_event = ResourceEvent(
                resource_type=ResourceType.MILITARY,
                event_name="Military Unrest",
                description="Military forces show signs of discontent",
                military_impact=-0.1,
                political_impact=-0.15,
                duration_turns=2,
                turns_remaining=2,
                severity=0.6
            )
            new_events.append(uprising_event)
            self.active_events.append(uprising_event)
        
        # Technological breakthrough check
        if (self.technology_state.innovation_rate > 0.8 and 
            len(self.technology_state.completed_techs) > 5):
            
            breakthrough_event = ResourceEvent(
                resource_type=ResourceType.TECHNOLOGY,
                event_name="Scientific Breakthrough",
                description="A major scientific discovery advances the civilization",
                technology_impact=0.15,
                economic_impact=0.05,
                duration_turns=1,
                turns_remaining=1,
                severity=0.7
            )
            new_events.append(breakthrough_event)
            self.active_events.append(breakthrough_event)
        
        return new_events
    
    def _apply_event_effects(self, event: ResourceEvent, partial: bool = False) -> None:
        """Apply the effects of a resource event."""
        effect_multiplier = 1.0 if not partial else (1.0 / event.duration_turns)
        
        # Apply economic effects
        if event.economic_impact != 0:
            income_change = event.economic_impact * effect_multiplier * 50
            self.economic_state.income_per_turn += income_change
            
            stability_change = event.economic_impact * effect_multiplier * 0.1
            self.economic_state.economic_stability = max(0.0, min(1.0, 
                self.economic_state.economic_stability + stability_change))
        
        # Apply military effects
        if event.military_impact != 0:
            morale_change = event.military_impact * effect_multiplier * 0.1
            self.military_state.morale = max(0.0, min(1.0,
                self.military_state.morale + morale_change))
        
        # Apply technology effects
        if event.technology_impact != 0:
            research_change = event.technology_impact * effect_multiplier * 5
            self.technology_state.research_points_per_turn += research_change
    
    def _get_research_cost(self, technology: str) -> float:
        """Get the research cost for a specific technology."""
        # Simple cost calculation - could be expanded with tech tree
        base_costs = {
            "agriculture": 50,
            "writing": 75,
            "iron_working": 100,
            "mathematics": 125,
            "engineering": 150,
            "gunpowder": 200,
            "printing_press": 175,
            "steam_engine": 250,
            "electricity": 300,
            "computers": 400
        }
        return base_costs.get(technology, 100)
    
    def _apply_technology_effects(self, technology: str) -> Dict[str, any]:
        """Apply the effects of a completed technology."""
        effects = {}
        
        tech_effects = {
            "agriculture": {"economic_tech_level": 0.1, "income_boost": 20},
            "writing": {"political_tech_level": 0.1, "research_boost": 2},
            "iron_working": {"military_tech_level": 0.1, "army_effectiveness": 0.1},
            "mathematics": {"economic_tech_level": 0.05, "research_boost": 3},
            "engineering": {"military_tech_level": 0.1, "economic_tech_level": 0.05},
            "gunpowder": {"military_tech_level": 0.2, "army_effectiveness": 0.2},
            "printing_press": {"political_tech_level": 0.15, "research_boost": 5},
            "steam_engine": {"economic_tech_level": 0.2, "income_boost": 50},
            "electricity": {"economic_tech_level": 0.15, "military_tech_level": 0.1},
            "computers": {"political_tech_level": 0.2, "research_boost": 10}
        }
        
        if technology in tech_effects:
            tech_effect = tech_effects[technology]
            
            # Apply technology level increases
            if "economic_tech_level" in tech_effect:
                self.technology_state.economic_tech_level = min(1.0,
                    self.technology_state.economic_tech_level + tech_effect["economic_tech_level"])
                effects["economic_tech_increase"] = tech_effect["economic_tech_level"]
            
            if "military_tech_level" in tech_effect:
                self.technology_state.military_tech_level = min(1.0,
                    self.technology_state.military_tech_level + tech_effect["military_tech_level"])
                effects["military_tech_increase"] = tech_effect["military_tech_level"]
            
            if "political_tech_level" in tech_effect:
                self.technology_state.political_tech_level = min(1.0,
                    self.technology_state.political_tech_level + tech_effect["political_tech_level"])
                effects["political_tech_increase"] = tech_effect["political_tech_level"]
            
            # Apply economic benefits
            if "income_boost" in tech_effect:
                self.economic_state.income_per_turn += tech_effect["income_boost"]
                effects["income_increase"] = tech_effect["income_boost"]
            
            # Apply research benefits
            if "research_boost" in tech_effect:
                self.technology_state.research_points_per_turn += tech_effect["research_boost"]
                effects["research_increase"] = tech_effect["research_boost"]
            
            # Apply military benefits
            if "army_effectiveness" in tech_effect:
                self.military_state.unit_quality = min(1.0,
                    self.military_state.unit_quality + tech_effect["army_effectiveness"])
                effects["military_effectiveness_increase"] = tech_effect["army_effectiveness"]
        
        return effects
    
    def get_resource_summary(self) -> Dict[str, any]:
        """Get a comprehensive summary of all resource states."""
        return {
            "civilization_id": self.civilization_id,
            "turn": self.current_turn,
            "economic": {
                "treasury": self.economic_state.treasury,
                "net_income": (self.economic_state.income_per_turn - 
                             self.economic_state.expenses_per_turn),
                "stability": self.economic_state.economic_stability,
                "trade_routes": len(self.economic_state.trade_routes)
            },
            "military": {
                "total_forces": (self.military_state.army_size + 
                               self.military_state.navy_size + 
                               self.military_state.air_force_size),
                "strength": self.military_state.military_strength,
                "morale": self.military_state.morale,
                "active_conflicts": len(self.military_state.active_conflicts)
            },
            "technology": {
                "research_rate": self.technology_state.research_points_per_turn,
                "current_research": self.technology_state.current_research,
                "completed_techs": len(self.technology_state.completed_techs),
                "tech_levels": {
                    "military": self.technology_state.military_tech_level,
                    "economic": self.technology_state.economic_tech_level,
                    "political": self.technology_state.political_tech_level
                }
            },
            "active_events": len(self.active_events)
        }
