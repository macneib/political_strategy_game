"""
Inter-civilization diplomacy and relations management system.

This module provides the core framework for managing diplomatic relations, trade networks,
military conflicts, and intelligence operations between civilizations.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from .advisor import AdvisorRole
from .memory import Memory, MemoryType
from .resources import ResourceType, ResourceEvent


class DiplomaticStatus(str, Enum):
    """Current diplomatic relationship status between civilizations."""
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"
    ALLIED = "allied"
    HOSTILE = "hostile"
    AT_WAR = "at_war"
    TRADE_EMBARGO = "trade_embargo"
    NON_AGGRESSION = "non_aggression"


class TreatyType(str, Enum):
    """Types of treaties that can be established between civilizations."""
    TRADE_AGREEMENT = "trade_agreement"
    DEFENSE_PACT = "defense_pact"
    NON_AGGRESSION_PACT = "non_aggression_pact"
    CULTURAL_EXCHANGE = "cultural_exchange"
    MILITARY_ACCESS = "military_access"
    RESEARCH_COOPERATION = "research_cooperation"
    MUTUAL_PROTECTION = "mutual_protection"


class IntelligenceOperation(str, Enum):
    """Types of intelligence operations between civilizations."""
    DIPLOMATIC_ESPIONAGE = "diplomatic_espionage"
    MILITARY_INTELLIGENCE = "military_intelligence"
    ECONOMIC_ESPIONAGE = "economic_espionage"
    COUNTER_INTELLIGENCE = "counter_intelligence"
    SABOTAGE = "sabotage"
    PROPAGANDA = "propaganda"
    ASSASSINATION = "assassination"


class ConflictType(str, Enum):
    """Types of military conflicts between civilizations."""
    BORDER_SKIRMISH = "border_skirmish"
    TRADE_WAR = "trade_war"
    TERRITORIAL_DISPUTE = "territorial_dispute"
    FULL_SCALE_WAR = "full_scale_war"
    CIVIL_INTERVENTION = "civil_intervention"
    RESOURCE_CONFLICT = "resource_conflict"


class Treaty(BaseModel):
    """A formal agreement between two or more civilizations."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    treaty_type: TreatyType
    participants: List[str] = Field(min_length=2)  # Civilization IDs
    terms: Dict[str, Any] = Field(default_factory=dict)
    signed_turn: int
    duration: Optional[int] = None  # None means permanent
    auto_renewal: bool = False
    
    # Status
    active: bool = True
    violated_by: Optional[str] = None
    violation_reason: Optional[str] = None
    
    # Trade-specific terms
    trade_value_per_turn: Optional[float] = None
    resource_exchanges: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    
    # Military terms
    military_support_level: Optional[float] = None
    shared_intelligence: bool = False
    
    # Economic terms
    tariff_reductions: Dict[str, float] = Field(default_factory=dict)
    joint_projects: List[str] = Field(default_factory=list)


class TradeRoute(BaseModel):
    """A trade connection between two civilizations."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    origin_civilization: str
    destination_civilization: str
    trade_value_per_turn: float = Field(gt=0.0)
    resource_type: Optional[ResourceType] = None
    
    # Status
    active: bool = True
    established_turn: int
    disrupted_turns: int = 0
    total_value_exchanged: float = 0.0
    
    # Efficiency and risk factors
    trade_efficiency: float = Field(default=1.0, ge=0.0, le=2.0)
    piracy_risk: float = Field(default=0.1, ge=0.0, le=1.0)
    diplomatic_modifier: float = Field(default=1.0, ge=0.0, le=2.0)


class MilitaryConflict(BaseModel):
    """An ongoing military conflict between civilizations."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conflict_type: ConflictType
    belligerents: Dict[str, List[str]] = Field(default_factory=dict)  # "attackers": [civ_ids], "defenders": [civ_ids]
    
    # Timeline
    started_turn: int
    duration: int = 0
    expected_resolution: Optional[int] = None
    
    # Stakes and objectives
    objectives: Dict[str, List[str]] = Field(default_factory=dict)  # civ_id -> list of objectives
    territorial_claims: Dict[str, List[str]] = Field(default_factory=dict)
    resource_stakes: Dict[str, float] = Field(default_factory=dict)
    
    # Current state
    military_balance: Dict[str, float] = Field(default_factory=dict)  # civ_id -> military strength
    war_exhaustion: Dict[str, float] = Field(default_factory=dict)  # civ_id -> exhaustion level
    civilian_support: Dict[str, float] = Field(default_factory=dict)  # civ_id -> public support
    
    # Economic impact
    economic_cost_per_turn: Dict[str, float] = Field(default_factory=dict)
    trade_disruption: float = Field(default=0.3, ge=0.0, le=1.0)
    
    active: bool = True
    victor: Optional[str] = None
    peace_terms: Optional[Dict[str, Any]] = None


class IntelligenceNetwork(BaseModel):
    """Intelligence operations and spy networks between civilizations."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    operator_civilization: str
    target_civilization: str
    operation_type: IntelligenceOperation
    
    # Network strength and capabilities
    network_strength: float = Field(default=0.1, ge=0.0, le=1.0)
    infiltration_level: float = Field(default=0.0, ge=0.0, le=1.0)
    counter_intelligence_resistance: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Operations
    active_operations: List[str] = Field(default_factory=list)
    completed_operations: List[Dict[str, Any]] = Field(default_factory=list)
    discovered_operations: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Resources
    intelligence_budget: float = 0.0
    agents_deployed: int = 0
    assets_compromised: int = 0
    
    # Results
    intelligence_gathered: Dict[str, Any] = Field(default_factory=dict)
    sabotage_damage: float = 0.0
    propaganda_effectiveness: float = 0.0


class CivilizationRelations(BaseModel):
    """Manages bilateral relationship between two specific civilizations."""
    
    civilization_a: str
    civilization_b: str
    current_status: DiplomaticStatus = DiplomaticStatus.NEUTRAL
    
    # Relationship metrics
    trust_level: float = Field(default=0.5, ge=0.0, le=1.0)
    trade_dependency: float = Field(default=0.0, ge=0.0, le=1.0)
    cultural_affinity: float = Field(default=0.5, ge=0.0, le=1.0)
    military_threat_perception: float = Field(default=0.3, ge=0.0, le=1.0)
    
    # Historical context
    relationship_history: List[Dict[str, Any]] = Field(default_factory=list)
    shared_conflicts: List[str] = Field(default_factory=list)
    mutual_enemies: List[str] = Field(default_factory=list)
    mutual_allies: List[str] = Field(default_factory=list)
    
    # Active agreements and connections
    active_treaties: List[str] = Field(default_factory=list)  # Treaty IDs
    trade_routes: List[str] = Field(default_factory=list)  # TradeRoute IDs
    ongoing_conflicts: List[str] = Field(default_factory=list)  # MilitaryConflict IDs
    intelligence_networks: List[str] = Field(default_factory=list)  # IntelligenceNetwork IDs
    
    # Diplomatic state
    embassy_established: bool = False
    ambassador_assigned: Optional[str] = None  # Advisor ID
    diplomatic_immunity: bool = False
    last_diplomatic_contact: Optional[int] = None
    
    # Recent events impact
    recent_diplomatic_events: List[Dict[str, Any]] = Field(default_factory=list)
    pending_negotiations: List[Dict[str, Any]] = Field(default_factory=list)


class DiplomaticEvent(BaseModel):
    """A diplomatic event affecting inter-civilization relations."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    civilizations_involved: List[str]
    turn_created: int
    
    # Event details
    title: str
    description: str
    instigator: Optional[str] = None
    
    # Impact on relationships
    relationship_changes: Dict[str, Dict[str, float]] = Field(default_factory=dict)  # civ_pair -> relationship metrics
    treaty_effects: Dict[str, str] = Field(default_factory=dict)  # treaty_id -> effect
    trade_effects: Dict[str, float] = Field(default_factory=dict)  # trade_route_id -> modifier
    
    # Consequences
    advisor_memory_impact: Dict[str, float] = Field(default_factory=dict)  # advisor_id -> emotional_impact
    resource_consequences: Dict[str, Dict[str, float]] = Field(default_factory=dict)  # civ_id -> resource changes
    
    # Response requirements
    requires_response: bool = False
    response_deadline: Optional[int] = None
    available_responses: List[Dict[str, Any]] = Field(default_factory=list)
    chosen_responses: Dict[str, str] = Field(default_factory=dict)  # civ_id -> response_id


class DiplomacyManager(BaseModel):
    """Central manager for all inter-civilization diplomatic relations."""
    
    model_config = {"arbitrary_types_allowed": True}
    
    # Core data
    civilization_relations: Dict[str, CivilizationRelations] = Field(default_factory=dict)  # "civ_a_id:civ_b_id" -> relations
    active_treaties: Dict[str, Treaty] = Field(default_factory=dict)
    trade_routes: Dict[str, TradeRoute] = Field(default_factory=dict)
    military_conflicts: Dict[str, MilitaryConflict] = Field(default_factory=dict)
    intelligence_networks: Dict[str, IntelligenceNetwork] = Field(default_factory=dict)
    
    # Event tracking
    diplomatic_events: List[DiplomaticEvent] = Field(default_factory=list)
    pending_negotiations: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Global state
    current_turn: int = 1
    global_stability: float = Field(default=0.7, ge=0.0, le=1.0)
    active_civilizations: Set[str] = Field(default_factory=set)
    
    def get_relationship_key(self, civ_a: str, civ_b: str) -> str:
        """Generate consistent key for civilization pair."""
        return f"{min(civ_a, civ_b)}:{max(civ_a, civ_b)}"
    
    def get_relations(self, civ_a: str, civ_b: str) -> Optional[CivilizationRelations]:
        """Get relationship between two civilizations."""
        key = self.get_relationship_key(civ_a, civ_b)
        return self.civilization_relations.get(key)
    
    def establish_relations(self, civ_a: str, civ_b: str) -> CivilizationRelations:
        """Establish diplomatic relations between two civilizations."""
        key = self.get_relationship_key(civ_a, civ_b)
        if key not in self.civilization_relations:
            self.civilization_relations[key] = CivilizationRelations(
                civilization_a=min(civ_a, civ_b),
                civilization_b=max(civ_a, civ_b)
            )
        return self.civilization_relations[key]
    
    def register_civilization(self, civilization_id: str) -> None:
        """Register a new civilization in the diplomatic system."""
        self.active_civilizations.add(civilization_id)
        
        # Establish neutral relations with all existing civilizations
        for existing_civ in self.active_civilizations:
            if existing_civ != civilization_id:
                self.establish_relations(civilization_id, existing_civ)
    
    def update_diplomatic_turn(self, current_turn: int) -> Dict[str, Any]:
        """Process one turn of diplomatic activities."""
        self.current_turn = current_turn
        results = {
            "turn": current_turn,
            "new_events": [],
            "treaty_changes": [],
            "trade_updates": [],
            "conflict_updates": [],
            "intelligence_operations": []
        }
        
        # Update trade routes
        for trade_route in self.trade_routes.values():
            if trade_route.active:
                trade_route.total_value_exchanged += trade_route.trade_value_per_turn
        
        # Update ongoing conflicts
        for conflict in self.military_conflicts.values():
            if conflict.active:
                conflict.duration += 1
                # Increase war exhaustion
                for civ_id in conflict.belligerents.get("attackers", []) + conflict.belligerents.get("defenders", []):
                    if civ_id in conflict.war_exhaustion:
                        conflict.war_exhaustion[civ_id] = min(1.0, conflict.war_exhaustion[civ_id] + 0.05)
        
        # Process intelligence operations
        for intel_network in self.intelligence_networks.values():
            if intel_network.network_strength > 0.3:
                # Successful intelligence gathering
                results["intelligence_operations"].append({
                    "operator": intel_network.operator_civilization,
                    "target": intel_network.target_civilization,
                    "operation": intel_network.operation_type.value,
                    "success": True
                })
        
        # Update global stability based on conflicts and cooperation
        active_conflicts = len([c for c in self.military_conflicts.values() if c.active])
        active_treaties = len([t for t in self.active_treaties.values() if t.active])
        self.global_stability = max(0.0, min(1.0, 0.7 - (active_conflicts * 0.1) + (active_treaties * 0.05)))
        
        return results
    
    def create_diplomatic_event(self, event_type: str, civilizations: List[str], 
                              title: str, description: str, **kwargs) -> DiplomaticEvent:
        """Create a new diplomatic event."""
        event = DiplomaticEvent(
            event_type=event_type,
            civilizations_involved=civilizations,
            turn_created=self.current_turn,
            title=title,
            description=description,
            **kwargs
        )
        self.diplomatic_events.append(event)
        return event
    
    def get_diplomatic_summary(self, civilization_id: str) -> Dict[str, Any]:
        """Get diplomatic status summary for a specific civilization."""
        summary = {
            "civilization_id": civilization_id,
            "turn": self.current_turn,
            "relations": {},
            "active_treaties": [],
            "trade_routes": [],
            "conflicts": [],
            "intelligence_operations": []
        }
        
        # Get relations with other civilizations
        for key, relations in self.civilization_relations.items():
            if civilization_id in [relations.civilization_a, relations.civilization_b]:
                other_civ = relations.civilization_b if relations.civilization_a == civilization_id else relations.civilization_a
                summary["relations"][other_civ] = {
                    "status": relations.current_status.value,
                    "trust": relations.trust_level,
                    "trade_dependency": relations.trade_dependency,
                    "embassy": relations.embassy_established
                }
        
        # Get active treaties
        for treaty in self.active_treaties.values():
            if civilization_id in treaty.participants:
                summary["active_treaties"].append({
                    "type": treaty.treaty_type.value,
                    "participants": treaty.participants,
                    "signed_turn": treaty.signed_turn
                })
        
        # Get trade routes
        for trade_route in self.trade_routes.values():
            if civilization_id in [trade_route.origin_civilization, trade_route.destination_civilization]:
                partner = trade_route.destination_civilization if trade_route.origin_civilization == civilization_id else trade_route.origin_civilization
                summary["trade_routes"].append({
                    "partner": partner,
                    "value_per_turn": trade_route.trade_value_per_turn,
                    "total_exchanged": trade_route.total_value_exchanged
                })
        
        return summary
