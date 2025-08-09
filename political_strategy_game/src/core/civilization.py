"""
Civilization class that manages the complete political state of an AI empire.
"""

from typing import Dict, List, Optional, Set, Any
from enum import Enum
from pydantic import BaseModel, Field
import uuid

from .advisor import AdvisorRole, AdvisorStatus
from .advisor_enhanced import AdvisorWithMemory, AdvisorCouncil, PersonalityProfile
from .leader import Leader, LeadershipStyle
from .memory import MemoryBank, MemoryManager, Memory, MemoryType
from .events import EventManager, PoliticalEvent, EventType, EventSeverity
from .resources import ResourceManager, ResourceEvent, ResourceType
from .diplomacy import DiplomacyManager, DiplomaticStatus, Treaty, TradeRoute
from .advanced_politics import (
    AdvancedPoliticalManager, ConspiracyType, FactionType, PoliticalIdeology,
    PropagandaType, SuccessionCrisisType, ConspiracyNetwork, PoliticalFaction
)


class PoliticalStability(str, Enum):
    """Overall political stability of the civilization."""
    STABLE = "stable"
    TENSE = "tense"
    UNSTABLE = "unstable"
    CRISIS = "crisis"
    COLLAPSE = "collapse"


class GovernmentType(str, Enum):
    """Type of government structure."""
    MONARCHY = "monarchy"
    REPUBLIC = "republic"
    OLIGARCHY = "oligarchy"
    THEOCRACY = "theocracy"
    MILITARY_JUNTA = "military_junta"
    COUNCIL = "council"


class PoliticalState(BaseModel):
    """Current political state of the civilization."""
    
    stability: PoliticalStability = PoliticalStability.STABLE
    legitimacy: float = Field(default=0.7, ge=0.0, le=1.0)
    corruption_level: float = Field(default=0.1, ge=0.0, le=1.0)
    internal_tension: float = Field(default=0.0, ge=0.0, le=1.0)
    coup_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Government structure
    government_type: GovernmentType = GovernmentType.MONARCHY
    advisor_council_autonomy: float = Field(default=0.3, ge=0.0, le=1.0)
    
    # Recent events impact
    recent_crises: List[str] = Field(default_factory=list)
    recent_successes: List[str] = Field(default_factory=list)
    propaganda_effectiveness: float = Field(default=0.5, ge=0.0, le=1.0)


class Civilization(BaseModel):
    """Complete civilization with political dynamics."""
    
    model_config = {"arbitrary_types_allowed": True}
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    current_turn: int = Field(default=1)
    
    # Leadership
    leader: Leader
    advisors: Dict[str, AdvisorWithMemory] = Field(default_factory=dict)
    
    # Political state
    political_state: PoliticalState = Field(default_factory=PoliticalState)
    memory_bank: Optional[MemoryBank] = Field(default=None)
    memory_manager: Optional[MemoryManager] = Field(default=None, exclude=True)
    
    # Event management
    event_manager: Optional[EventManager] = Field(default=None, exclude=True)
    event_history: List[PoliticalEvent] = Field(default_factory=list)
    pending_events: List[PoliticalEvent] = Field(default_factory=list)
    
    # Resource management
    resource_manager: Optional[ResourceManager] = Field(default=None, exclude=True)
    
    # Diplomacy and international relations
    diplomacy_manager: Optional[DiplomacyManager] = Field(default=None, exclude=True)
    international_treaties: List[str] = Field(default_factory=list)  # Treaty IDs
    known_civilizations: Set[str] = Field(default_factory=set)
    
    # Advanced political systems
    advanced_politics: Optional[AdvancedPoliticalManager] = Field(default=None, exclude=True)
    
    # Technologies and capabilities
    unlocked_technologies: Set[str] = Field(default_factory=set)
    espionage_capabilities: Dict[str, float] = Field(default_factory=dict)
    
    def model_post_init(self, __context):
        """Initialize managers after model creation."""
        # Initialize memory bank
        self.memory_bank = MemoryBank(civilization_id=self.id)
        
        # Initialize memory manager with temporary directory for tests
        # In real usage, this would be set externally
        import tempfile
        from pathlib import Path
        temp_dir = Path(tempfile.gettempdir()) / "civilization_memory" / self.id
        temp_dir.mkdir(parents=True, exist_ok=True)
        self.memory_manager = MemoryManager(data_dir=temp_dir)
        
        # Initialize event manager
        self.event_manager = EventManager(civilization_id=self.id, current_turn=self.current_turn)
        
        # Initialize resource manager
        self.resource_manager = ResourceManager(civilization_id=self.id, current_turn=self.current_turn)
        
        # Initialize diplomacy manager (shared instance will be set externally)
        self.diplomacy_manager = None
        
        # Initialize advanced politics manager
        self.advanced_politics = AdvancedPoliticalManager(
            civilization_id=self.id, 
            current_turn=self.current_turn
        )
    
    def set_memory_manager(self, memory_manager: MemoryManager) -> None:
        """Set the memory manager for this civilization."""
        self.memory_manager = memory_manager
        # Register all advisors with the memory manager
        for advisor in self.advisors.values():
            memory_manager.register_advisor(advisor.id, self.id)
    
    def add_advisor(self, advisor: AdvisorWithMemory) -> bool:
        """Add a new advisor to the civilization."""
        if advisor.role in [a.role for a in self.advisors.values() if a.status == AdvisorStatus.ACTIVE]:
            return False  # Role already filled
        
        advisor.civilization_id = self.id
        advisor.appointment_turn = self.current_turn
        advisor.appointed_by_leader = self.leader.id
        
        self.advisors[advisor.id] = advisor
        
        # Create appointment memory for the advisor
        appointment_memory = Memory(
            advisor_id=advisor.id,
            event_type=MemoryType.DECISION,
            content=f"Appointed to {advisor.role.value} position in {self.name}",
            emotional_impact=0.3,
            created_turn=self.current_turn,
            last_accessed_turn=self.current_turn,
            tags={"appointment", advisor.role.value, "leadership"}
        )
        
        if self.memory_manager:
            self.memory_manager.store_memory(advisor.id, appointment_memory)
        
        return True
    
    def dismiss_advisor(self, advisor_id: str, reason: str = "performance") -> bool:
        """Dismiss an advisor from their position."""
        if advisor_id not in self.advisors:
            return False
        
        advisor = self.advisors[advisor_id]
        if advisor.status != AdvisorStatus.ACTIVE:
            return False
        
        advisor.status = AdvisorStatus.DISMISSED
        
        # Create dismissal memory
        dismissal_memory = Memory(
            advisor_id=advisor_id,
            event_type=MemoryType.CRISIS,
            content=f"Dismissed from {advisor.role.value} position for {reason}",
            emotional_impact=0.8,
            created_turn=self.current_turn,
            last_accessed_turn=self.current_turn,
            tags={"dismissal", advisor.role.value, reason}
        )
        
        if self.memory_manager:
            self.memory_manager.store_memory(advisor_id, dismissal_memory)
        
        # Update political state
        self._update_political_stability()
        
        return True
    
    def get_active_advisors(self) -> List[AdvisorWithMemory]:
        """Get all currently active advisors."""
        return [advisor for advisor in self.advisors.values() 
                if advisor.status == AdvisorStatus.ACTIVE]
    
    def get_advisor_by_role(self, role: AdvisorRole) -> Optional[AdvisorWithMemory]:
        """Get the current advisor for a specific role."""
        for advisor in self.advisors.values():
            if advisor.role == role and advisor.status == AdvisorStatus.ACTIVE:
                return advisor
        return None
    
    def assess_coup_risk(self) -> float:
        """Calculate the current risk of a coup attempt."""
        active_advisors = self.get_active_advisors()
        if len(active_advisors) < 2:
            return 0.0
        
        total_motivation = 0.0
        conspiracy_strength = 0.0
        
        for advisor in active_advisors:
            motivation = advisor.calculate_coup_motivation()
            total_motivation += motivation
            
            # Check for existing conspiracies
            for relationship in advisor.relationships.values():
                if relationship.conspiracy_level > 0.3:
                    conspiracy_strength += relationship.conspiracy_level
        
        # Base risk from average motivation
        base_risk = total_motivation / len(active_advisors)
        
        # Amplify if there are conspiracies
        conspiracy_factor = min(1.0, conspiracy_strength / len(active_advisors))
        
        # Leader's legitimacy affects coup risk
        legitimacy_factor = 1.0 - self.leader.legitimacy
        
        total_risk = (base_risk + conspiracy_factor) * legitimacy_factor
        return min(1.0, total_risk)
    
    def detect_conspiracies(self) -> List[Dict[str, Any]]:
        """Identify potential conspiracies among advisors."""
        conspiracies = []
        active_advisors = self.get_active_advisors()
        
        # Look for groups of advisors with high conspiracy levels
        checked_pairs = set()
        
        for advisor in active_advisors:
            potential_conspirators = [advisor.id]
            
            for other_id, relationship in advisor.relationships.items():
                if (relationship.conspiracy_level > 0.3 and 
                    other_id in self.advisors and
                    self.advisors[other_id].status == AdvisorStatus.ACTIVE):
                    
                    pair_key = tuple(sorted([advisor.id, other_id]))
                    if pair_key not in checked_pairs:
                        potential_conspirators.append(other_id)
                        checked_pairs.add(pair_key)
            
            if len(potential_conspirators) > 1:
                # Calculate conspiracy strength
                total_conspiracy = sum(
                    advisor.get_relationship(other_id).conspiracy_level
                    for other_id in potential_conspirators[1:]
                )
                avg_conspiracy = total_conspiracy / (len(potential_conspirators) - 1)
                
                conspiracies.append({
                    "conspirators": potential_conspirators,
                    "strength": avg_conspiracy,
                    "motivation": sum(self.advisors[aid].calculate_coup_motivation() 
                                    for aid in potential_conspirators) / len(potential_conspirators)
                })
        
        # Sort by strength
        conspiracies.sort(key=lambda x: x["strength"] * x["motivation"], reverse=True)
        return conspiracies
    
    def attempt_coup(self, conspirators: List[str]) -> bool:
        """Execute a coup attempt."""
        if len(conspirators) < 2:
            return False
        
        # Calculate coup success probability
        total_influence = sum(self.advisors[aid].influence for aid in conspirators 
                            if aid in self.advisors)
        avg_motivation = sum(self.advisors[aid].calculate_coup_motivation() 
                           for aid in conspirators if aid in self.advisors) / len(conspirators)
        
        leader_strength = self.leader.legitimacy + self.leader.popularity
        
        # Base success chance
        success_chance = (total_influence + avg_motivation) / (2.0 + leader_strength)
        
        # Random factor
        import random
        success = random.random() < success_chance
        
        # Create coup memories for all involved parties
        coup_content = f"{'Successful' if success else 'Failed'} coup attempt by {len(conspirators)} conspirators"
        
        for conspirator_id in conspirators:
            if conspirator_id in self.advisors:
                coup_memory = Memory(
                    advisor_id=conspirator_id,
                    event_type=MemoryType.CONSPIRACY,
                    content=coup_content,
                    emotional_impact=0.9 if success else 0.7,
                    created_turn=self.current_turn,
                    last_accessed_turn=self.current_turn,
                    tags={"coup", "conspiracy", "success" if success else "failure"}
                )
                
                if self.memory_manager:
                    self.memory_manager.store_memory(conspirator_id, coup_memory)
        
        if success:
            self._execute_successful_coup(conspirators[0])  # First conspirator becomes leader
        else:
            self._handle_failed_coup(conspirators)
        
        self._update_political_stability()
        return success
    
    def _execute_successful_coup(self, new_leader_id: str) -> None:
        """Handle the aftermath of a successful coup."""
        # Remove old leader
        old_leader = self.leader
        
        # Promote conspirator to leader
        new_leader_advisor = self.advisors[new_leader_id]
        new_leader_advisor.status = AdvisorStatus.ACTIVE  # Ensure they're active
        
        # Create new leader from advisor
        self.leader = Leader(
            name=new_leader_advisor.name,
            civilization_id=self.id,
            personality=new_leader_advisor.personality,
            leadership_style=LeadershipStyle.AUTHORITARIAN,  # New leaders often start authoritarian
            legitimacy=0.3,  # Low legitimacy initially
            came_to_power_by="coup"
        )
        
        # Remove the advisor from advisor list (they're now leader)
        del self.advisors[new_leader_id]
        
        # Update political state
        self.political_state.stability = PoliticalStability.UNSTABLE
        self.political_state.legitimacy = 0.3
        self.political_state.internal_tension = 0.8
    
    def _handle_failed_coup(self, conspirators: List[str]) -> None:
        """Handle the aftermath of a failed coup."""
        for conspirator_id in conspirators:
            if conspirator_id in self.advisors:
                advisor = self.advisors[conspirator_id]
                # Punish conspirators
                advisor.status = AdvisorStatus.IMPRISONED
                advisor.loyalty_to_leader = 0.0
                advisor.influence *= 0.1  # Lose most influence
        
        # Leader becomes more paranoid
        self.leader.paranoia_level = min(1.0, self.leader.paranoia_level + 0.3)
        self.leader.legitimacy = min(1.0, self.leader.legitimacy + 0.1)  # Surviving coup increases legitimacy
    
    def process_turn(self) -> Dict[str, Any]:
        """Process one turn of political simulation."""
        turn_results = {
            "turn": self.current_turn,
            "events": [],
            "conspiracy_detected": False,
            "coup_attempted": False,
            "new_events": []
        }
        
        # Advance all advisor states
        for advisor in self.advisors.values():
            advisor.advance_turn(self.current_turn)
        
        # Advance leader state
        self.leader.advance_turn(self.current_turn)
        
        # Check for conspiracies
        conspiracies = self.detect_conspiracies()
        if conspiracies:
            turn_results["conspiracy_detected"] = True
            
            # Strongest conspiracy might attempt coup
            strongest_conspiracy = conspiracies[0]
            if (strongest_conspiracy["strength"] > 0.6 and 
                strongest_conspiracy["motivation"] > 0.7):
                
                success = self.attempt_coup(strongest_conspiracy["conspirators"])
                turn_results["coup_attempted"] = True
                turn_results["coup_success"] = success
        
        # Update political stability
        self._update_political_stability()
        
        # Update coup risk
        self.political_state.coup_risk = self.assess_coup_risk()
        
        # Process resource management
        if self.resource_manager:
            resource_results = self.resource_manager.update_resources(1)
            turn_results["resource_changes"] = resource_results
            
            # Check if resource events affect political stability
            for event in resource_results.get("new_events", []):
                if event.political_impact != 0:
                    # Resource events can affect political stability
                    stability_change = event.political_impact * 0.1
                    self.political_state.internal_tension = max(0.0, min(1.0,
                        self.political_state.internal_tension - stability_change))
                    
                    # Create memories for advisors about resource events
                    self._create_resource_event_memories(event)
        
        # Process advanced political mechanics
        if self.advanced_politics:
            # Update advanced politics turn counter
            self.advanced_politics.current_turn = self.current_turn + 1
            
            # Process advanced political events
            advanced_results = self.advanced_politics.process_turn()
            turn_results["advanced_politics"] = advanced_results
            
            # Create memories for political events
            self._create_advanced_political_memories(advanced_results)
        
        # Advance turn counter
        self.current_turn += 1
        
        return turn_results
    
    def _update_political_stability(self) -> None:
        """Update the overall political stability assessment."""
        coup_risk = self.assess_coup_risk()
        
        if coup_risk > 0.8:
            self.political_state.stability = PoliticalStability.CRISIS
        elif coup_risk > 0.6:
            self.political_state.stability = PoliticalStability.UNSTABLE
        elif coup_risk > 0.3:
            self.political_state.stability = PoliticalStability.TENSE
        else:
            self.political_state.stability = PoliticalStability.STABLE
        
        # Update internal tension
        active_advisors = self.get_active_advisors()
        if active_advisors:
            avg_loyalty = sum(a.loyalty_to_leader for a in active_advisors) / len(active_advisors)
            self.political_state.internal_tension = 1.0 - avg_loyalty
    
    def get_political_summary(self) -> Dict[str, Any]:
        """Get a summary of the current political situation."""
        active_advisors = self.get_active_advisors()
        
        summary = {
            "civilization_name": self.name,
            "current_turn": self.current_turn,
            "leader": {
                "name": self.leader.name,
                "legitimacy": self.leader.legitimacy,
                "popularity": self.leader.popularity,
                "paranoia": self.leader.paranoia_level,
                "leadership_style": self.leader.leadership_style.value
            },
            "political_state": {
                "stability": self.political_state.stability.value,
                "coup_risk": self.political_state.coup_risk,
                "internal_tension": self.political_state.internal_tension,
                "corruption": self.political_state.corruption_level
            },
            "advisors": [
                {
                    "name": advisor.name,
                    "role": advisor.role.value,
                    "loyalty": advisor.loyalty_to_leader,
                    "influence": advisor.influence,
                    "coup_motivation": advisor.calculate_coup_motivation()
                }
                for advisor in active_advisors
            ],
            "conspiracies": self.detect_conspiracies(),
            "recent_events": len(self.event_history[-5:])  # Last 5 events
        }
        
        return summary
    
    def _create_resource_event_memories(self, event: ResourceEvent) -> None:
        """Create memories for advisors about resource events."""
        if not self.memory_manager:
            return
        
        # Determine which advisors would be most interested in this event
        interested_roles = {
            ResourceType.ECONOMIC: [AdvisorRole.ECONOMIC, AdvisorRole.DIPLOMATIC],
            ResourceType.MILITARY: [AdvisorRole.MILITARY, AdvisorRole.SECURITY],
            ResourceType.TECHNOLOGY: [AdvisorRole.ECONOMIC, AdvisorRole.MILITARY],
            ResourceType.POPULATION: [AdvisorRole.ECONOMIC, AdvisorRole.SECURITY],
            ResourceType.FOOD: [AdvisorRole.ECONOMIC],
            ResourceType.MATERIALS: [AdvisorRole.ECONOMIC, AdvisorRole.MILITARY]
        }
        
        relevant_roles = interested_roles.get(event.resource_type, [])
        
        for advisor in self.advisors.values():
            if advisor.role in relevant_roles:
                # Create memory with appropriate emotional impact
                emotional_impact = min(0.9, abs(event.severity))
                if (event.resource_type == ResourceType.ECONOMIC and 
                    advisor.role == AdvisorRole.ECONOMIC):
                    emotional_impact *= 1.2  # Economic advisor more affected by economic events
                
                memory = Memory(
                    advisor_id=advisor.id,
                    event_type=MemoryType.CRISIS if event.severity > 0.6 else MemoryType.DECISION,
                    content=f"Resource event: {event.event_name} - {event.description}",
                    emotional_impact=min(1.0, emotional_impact),
                    created_turn=self.current_turn,
                    last_accessed_turn=self.current_turn,
                    tags={event.resource_type.value, "resource_event", event.event_name.lower().replace(" ", "_")}
                )
                
                self.memory_manager.store_memory(advisor.id, memory)
    
    def _create_advanced_political_memories(self, advanced_results: Dict[str, Any]) -> None:
        """Create memories for advisors about advanced political events."""
        if not self.memory_manager:
            return
        
        # Process conspiracy detections
        for detected_conspiracy in advanced_results.get("conspiracies_detected", []):
            for advisor in self.advisors.values():
                # Security advisors are more likely to know about conspiracy detection
                if advisor.role == AdvisorRole.SECURITY:
                    memory = Memory(
                        advisor_id=advisor.id,
                        event_type=MemoryType.CONSPIRACY,
                        content=f"Detected conspiracy led by {detected_conspiracy['leader']} involving {len(detected_conspiracy['members'])} members",
                        emotional_impact=0.8,
                        created_turn=self.current_turn,
                        last_accessed_turn=self.current_turn,
                        tags={"conspiracy", "detection", detected_conspiracy["type"], "security"}
                    )
                    self.memory_manager.store_memory(advisor.id, memory)
                elif advisor.id not in detected_conspiracy.get("members", []):
                    # Other advisors might hear rumors
                    memory = Memory(
                        advisor_id=advisor.id,
                        event_type=MemoryType.INTELLIGENCE,
                        content=f"Rumors of conspiracy involving {detected_conspiracy['type']} have surfaced",
                        emotional_impact=0.6,
                        created_turn=self.current_turn,
                        last_accessed_turn=self.current_turn,
                        tags={"conspiracy", "rumors", detected_conspiracy["type"]}
                    )
                    self.memory_manager.store_memory(advisor.id, memory)
        
        # Process conspiracy activations
        for activated_conspiracy in advanced_results.get("conspiracies_activated", []):
            for advisor in self.advisors.values():
                if advisor.role in [AdvisorRole.SECURITY, AdvisorRole.DIPLOMATIC]:
                    memory = Memory(
                        advisor_id=advisor.id,
                        event_type=MemoryType.DECISION,
                        content=f"Political conspiracy of type {activated_conspiracy['type']} has become active",
                        emotional_impact=0.7,
                        created_turn=self.current_turn,
                        last_accessed_turn=self.current_turn,
                        tags={"conspiracy", "activation", activated_conspiracy["type"], "instability"}
                    )
                    self.memory_manager.store_memory(advisor.id, memory)
        
        # Process propaganda effects
        for propaganda_effect in advanced_results.get("propaganda_effects", []):
            # Advisors involved in politics would notice propaganda campaigns
            for advisor in self.advisors.values():
                if advisor.role in [AdvisorRole.DIPLOMATIC, AdvisorRole.SECURITY]:
                    memory = Memory(
                        advisor_id=advisor.id,
                        event_type=MemoryType.DECISION,
                        content=f"Propaganda campaign affecting {propaganda_effect['target']} has shifted public opinion",
                        emotional_impact=0.5,
                        created_turn=self.current_turn,
                        last_accessed_turn=self.current_turn,
                        tags={"propaganda", "information_warfare", "public_opinion"}
                    )
                    self.memory_manager.store_memory(advisor.id, memory)
        
        # Process passed reforms
        for passed_reform in advanced_results.get("reforms_passed", []):
            for advisor in self.advisors.values():
                # All advisors would know about major political reforms
                memory = Memory(
                    advisor_id=advisor.id,
                    event_type=MemoryType.DECISION,
                    content=f"Political reform '{passed_reform['name']}' has been enacted",
                    emotional_impact=0.6,
                    created_turn=self.current_turn,
                    last_accessed_turn=self.current_turn,
                    tags={"reform", "politics", "legislation", "change"}
                )
                self.memory_manager.store_memory(advisor.id, memory)
    
    def get_resource_summary(self) -> Dict[str, Any]:
        """Get a summary of civilization resources."""
        if not self.resource_manager:
            return {"error": "Resource manager not initialized"}
        
        return self.resource_manager.get_resource_summary()
    
    def start_research(self, technology: str) -> bool:
        """Start researching a specific technology."""
        if not self.resource_manager:
            return False
        
        tech_state = self.resource_manager.technology_state
        if tech_state.current_research is None:
            tech_state.current_research = technology
            
            # Create memory for advisors about research decision
            if self.memory_manager:
                for advisor in self.advisors.values():
                    if advisor.role in [AdvisorRole.ECONOMIC, AdvisorRole.MILITARY]:
                        memory = Memory(
                            advisor_id=advisor.id,
                            event_type=MemoryType.DECISION,
                            content=f"Civilization began research into {technology}",
                            emotional_impact=0.3,
                            created_turn=self.current_turn,
                            last_accessed_turn=self.current_turn,
                            tags={"technology", "research", technology.lower()}
                        )
                        self.memory_manager.store_memory(advisor.id, memory)
            
            return True
        else:
            # Add to research queue
            if technology not in tech_state.research_queue:
                tech_state.research_queue.append(technology)
                return True
        
        return False
    
    def allocate_military_budget(self, amount: float) -> bool:
        """Allocate military budget from treasury."""
        if not self.resource_manager:
            return False
        
        economic_state = self.resource_manager.economic_state
        military_state = self.resource_manager.military_state
        
        if economic_state.treasury >= amount:
            economic_state.treasury -= amount
            military_state.military_budget += amount
            
            # Create memory for military and economic advisors
            if self.memory_manager:
                memory_content = f"Military budget increased by {amount} coins"
                for advisor in self.advisors.values():
                    if advisor.role in [AdvisorRole.MILITARY, AdvisorRole.ECONOMIC]:
                        memory = Memory(
                            advisor_id=advisor.id,
                            event_type=MemoryType.DECISION,
                            content=memory_content,
                            emotional_impact=0.4 if advisor.role == AdvisorRole.MILITARY else 0.2,
                            created_turn=self.current_turn,
                            last_accessed_turn=self.current_turn,
                            tags={"military", "budget", "allocation"}
                        )
                        self.memory_manager.store_memory(advisor.id, memory)
            
            return True
        
        return False
    
    def establish_trade_route(self, target_civilization_id: str, trade_value: float) -> bool:
        """Establish a trade route with another civilization."""
        if not self.resource_manager:
            return False
        
        economic_state = self.resource_manager.economic_state
        economic_state.trade_routes[target_civilization_id] = trade_value
        economic_state.trade_income += trade_value
        
        # Create memory for diplomatic and economic advisors
        if self.memory_manager:
            memory_content = f"Established trade route worth {trade_value} per turn"
            for advisor in self.advisors.values():
                if advisor.role in [AdvisorRole.DIPLOMATIC, AdvisorRole.ECONOMIC]:
                    memory = Memory(
                        advisor_id=advisor.id,
                        event_type=MemoryType.DECISION,
                        content=memory_content,
                        emotional_impact=0.5,
                        created_turn=self.current_turn,
                        last_accessed_turn=self.current_turn,
                        tags={"trade", "diplomacy", "economic", target_civilization_id}
                    )
                    self.memory_manager.store_memory(advisor.id, memory)
        
        return True
    
    # ========== DIPLOMATIC METHODS ==========
    
    def set_diplomacy_manager(self, diplomacy_manager: DiplomacyManager) -> None:
        """Set the shared diplomacy manager for this civilization."""
        self.diplomacy_manager = diplomacy_manager
        diplomacy_manager.register_civilization(self.id)
    
    def establish_embassy(self, target_civilization_id: str, ambassador_advisor_id: Optional[str] = None) -> bool:
        """Establish an embassy with another civilization."""
        if not self.diplomacy_manager:
            return False
        
        # Get or establish relations
        relations = self.diplomacy_manager.establish_relations(self.id, target_civilization_id)
        
        if not relations.embassy_established:
            relations.embassy_established = True
            relations.last_diplomatic_contact = self.current_turn
            
            # Assign ambassador if specified
            if ambassador_advisor_id and ambassador_advisor_id in self.advisors:
                advisor = self.advisors[ambassador_advisor_id]
                if advisor.role == AdvisorRole.DIPLOMATIC:
                    relations.ambassador_assigned = ambassador_advisor_id
            
            # Create diplomatic memory for relevant advisors
            if self.memory_manager:
                memory_content = f"Established embassy with {target_civilization_id}"
                for advisor in self.advisors.values():
                    if advisor.role in [AdvisorRole.DIPLOMATIC, AdvisorRole.SECURITY]:
                        memory = Memory(
                            advisor_id=advisor.id,
                            event_type=MemoryType.DECISION,
                            content=memory_content,
                            emotional_impact=0.4,
                            created_turn=self.current_turn,
                            last_accessed_turn=self.current_turn,
                            tags={"diplomacy", "embassy", "international", target_civilization_id}
                        )
                        self.memory_manager.store_memory(advisor.id, memory)
            
            # Add to known civilizations
            self.known_civilizations.add(target_civilization_id)
            
            return True
        
        return False
    
    def propose_treaty(self, target_civilization_id: str, treaty_type: str, terms: Dict[str, Any]) -> Optional[str]:
        """Propose a treaty with another civilization."""
        if not self.diplomacy_manager:
            return None
        
        from .diplomacy import TreatyType, Treaty
        
        # Ensure relations exist
        relations = self.diplomacy_manager.establish_relations(self.id, target_civilization_id)
        
        # Create treaty proposal
        treaty = Treaty(
            treaty_type=TreatyType(treaty_type),
            participants=[self.id, target_civilization_id],
            terms=terms,
            signed_turn=self.current_turn,
            active=False  # Not active until accepted
        )
        
        # Add to pending negotiations
        key = f"{self.id}:{target_civilization_id}:{treaty.id}"
        self.diplomacy_manager.pending_negotiations[key] = {
            "treaty_id": treaty.id,
            "proposer": self.id,
            "target": target_civilization_id,
            "proposed_turn": self.current_turn,
            "terms": terms
        }
        
        # Create diplomatic memory
        if self.memory_manager:
            memory_content = f"Proposed {treaty_type} with {target_civilization_id}"
            for advisor in self.advisors.values():
                if advisor.role == AdvisorRole.DIPLOMATIC:
                    memory = Memory(
                        advisor_id=advisor.id,
                        event_type=MemoryType.DECISION,
                        content=memory_content,
                        emotional_impact=0.6,
                        created_turn=self.current_turn,
                        last_accessed_turn=self.current_turn,
                        tags={"diplomacy", "treaty", treaty_type, target_civilization_id}
                    )
                    self.memory_manager.store_memory(advisor.id, memory)
        
        return treaty.id
    
    def declare_war(self, target_civilization_id: str, war_objectives: List[str]) -> Optional[str]:
        """Declare war on another civilization."""
        if not self.diplomacy_manager:
            return None
        
        from .diplomacy import MilitaryConflict, ConflictType
        
        # Get current relations
        relations = self.diplomacy_manager.get_relations(self.id, target_civilization_id)
        if relations:
            relations.current_status = DiplomaticStatus.AT_WAR
        
        # Create military conflict
        conflict = MilitaryConflict(
            conflict_type=ConflictType.FULL_SCALE_WAR,
            belligerents={
                "attackers": [self.id],
                "defenders": [target_civilization_id]
            },
            started_turn=self.current_turn,
            objectives={self.id: war_objectives},
            military_balance={
                self.id: self._calculate_military_strength(),
                target_civilization_id: 0.5  # Placeholder, would get from target civ
            },
            war_exhaustion={self.id: 0.0, target_civilization_id: 0.0},
            civilian_support={self.id: 0.7, target_civilization_id: 0.7},
            economic_cost_per_turn={self.id: 100.0, target_civilization_id: 100.0}
        )
        
        self.diplomacy_manager.military_conflicts[conflict.id] = conflict
        
        # Add conflict to relations
        if relations:
            relations.ongoing_conflicts.append(conflict.id)
        
        # Update political state - war increases internal tension
        self.political_state.internal_tension = min(1.0, self.political_state.internal_tension + 0.2)
        
        # Create war declaration memories
        if self.memory_manager:
            memory_content = f"Declared war on {target_civilization_id} with objectives: {', '.join(war_objectives)}"
            for advisor in self.advisors.values():
                emotional_impact = 0.8 if advisor.role == AdvisorRole.MILITARY else 0.6
                memory = Memory(
                    advisor_id=advisor.id,
                    event_type=MemoryType.CRISIS,
                    content=memory_content,
                    emotional_impact=emotional_impact,
                    created_turn=self.current_turn,
                    last_accessed_turn=self.current_turn,
                    tags={"war", "military", "international", target_civilization_id}
                )
                self.memory_manager.store_memory(advisor.id, memory)
        
        return conflict.id
    
    def establish_international_trade_route(self, target_civilization_id: str, trade_value: float, resource_type: Optional[str] = None) -> bool:
        """Establish an international trade route with another civilization."""
        if not self.diplomacy_manager:
            return False
        
        from .diplomacy import TradeRoute
        from .resources import ResourceType
        
        # Check if we have economic resources to support trade
        if self.resource_manager:
            economic_state = self.resource_manager.economic_state
            if economic_state.treasury < trade_value * 2:  # Need reserves
                return False
        
        # Create trade route
        trade_route = TradeRoute(
            origin_civilization=self.id,
            destination_civilization=target_civilization_id,
            trade_value_per_turn=trade_value,
            resource_type=ResourceType(resource_type) if resource_type else None,
            established_turn=self.current_turn,
            trade_efficiency=1.0
        )
        
        self.diplomacy_manager.trade_routes[trade_route.id] = trade_route
        
        # Update relations
        relations = self.diplomacy_manager.establish_relations(self.id, target_civilization_id)
        relations.trade_routes.append(trade_route.id)
        relations.trade_dependency = min(1.0, relations.trade_dependency + 0.2)
        
        # Update our economic state
        if self.resource_manager:
            economic_state = self.resource_manager.economic_state
            economic_state.trade_income += trade_value
            economic_state.trade_routes[target_civilization_id] = trade_value
        
        # Create trade establishment memories
        if self.memory_manager:
            memory_content = f"Established international trade route worth {trade_value} per turn with {target_civilization_id}"
            for advisor in self.advisors.values():
                if advisor.role in [AdvisorRole.DIPLOMATIC, AdvisorRole.ECONOMIC]:
                    memory = Memory(
                        advisor_id=advisor.id,
                        event_type=MemoryType.DECISION,
                        content=memory_content,
                        emotional_impact=0.5,
                        created_turn=self.current_turn,
                        last_accessed_turn=self.current_turn,
                        tags={"trade", "diplomacy", "international", target_civilization_id}
                    )
                    self.memory_manager.store_memory(advisor.id, memory)
        
        return True
    
    def launch_intelligence_operation(self, target_civilization_id: str, operation_type: str) -> bool:
        """Launch an intelligence operation against another civilization."""
        if not self.diplomacy_manager:
            return False
        
        from .diplomacy import IntelligenceNetwork, IntelligenceOperation
        
        # Check if we have espionage capabilities
        if target_civilization_id not in self.espionage_capabilities:
            self.espionage_capabilities[target_civilization_id] = 0.1
        
        # Get or create intelligence network
        network_key = f"{self.id}:{target_civilization_id}"
        if network_key not in self.diplomacy_manager.intelligence_networks:
            network = IntelligenceNetwork(
                operator_civilization=self.id,
                target_civilization=target_civilization_id,
                operation_type=IntelligenceOperation(operation_type),
                network_strength=self.espionage_capabilities[target_civilization_id]
            )
            self.diplomacy_manager.intelligence_networks[network_key] = network
        else:
            network = self.diplomacy_manager.intelligence_networks[network_key]
        
        # Launch operation
        network.active_operations.append(f"{operation_type}_{self.current_turn}")
        network.agents_deployed += 1
        
        # Update espionage capabilities
        self.espionage_capabilities[target_civilization_id] = min(1.0, 
            self.espionage_capabilities[target_civilization_id] + 0.1)
        
        # Create intelligence operation memories
        if self.memory_manager:
            memory_content = f"Launched {operation_type} against {target_civilization_id}"
            for advisor in self.advisors.values():
                if advisor.role == AdvisorRole.SECURITY:
                    memory = Memory(
                        advisor_id=advisor.id,
                        event_type=MemoryType.DECISION,
                        content=memory_content,
                        emotional_impact=0.7,
                        created_turn=self.current_turn,
                        last_accessed_turn=self.current_turn,
                        tags={"intelligence", "espionage", operation_type, target_civilization_id}
                    )
                    self.memory_manager.store_memory(advisor.id, memory)
        
        return True
    
    def _calculate_military_strength(self) -> float:
        """Calculate overall military strength for diplomatic purposes."""
        if not self.resource_manager:
            return 0.5
        
        military_state = self.resource_manager.military_state
        strength = 0.0
        strength += military_state.army_size * 0.3
        strength += military_state.navy_size * 0.2
        strength += military_state.air_force_size * 0.2
        strength += military_state.unit_quality * 0.2
        strength += military_state.morale * 0.1
        
        return min(1.0, strength / 100.0)  # Normalize to 0-1
    
    def get_diplomatic_summary(self) -> Dict[str, Any]:
        """Get diplomatic status summary for this civilization."""
        if not self.diplomacy_manager:
            return {"error": "Diplomacy manager not initialized"}
        
        return self.diplomacy_manager.get_diplomatic_summary(self.id)
    
    # ========== END DIPLOMATIC METHODS ==========
    
    # ========== ADVANCED POLITICAL METHODS ==========
    
    def create_political_faction(self, name: str, faction_type: FactionType, 
                                ideology: PoliticalIdeology, leader_advisor_id: Optional[str] = None) -> str:
        """Create a new political faction within the civilization."""
        if not self.advanced_politics:
            return ""
        
        faction_id = self.advanced_politics.create_faction(name, faction_type, ideology, leader_advisor_id)
        
        # Create memory for advisors about faction formation
        if self.memory_manager and leader_advisor_id:
            memory_content = f"Founded political faction '{name}' with {ideology.value} ideology"
            memory = Memory(
                advisor_id=leader_advisor_id,
                event_type=MemoryType.DECISION,
                content=memory_content,
                emotional_impact=0.8,
                created_turn=self.current_turn,
                last_accessed_turn=self.current_turn,
                tags={"faction", "politics", faction_type.value, ideology.value}
            )
            self.memory_manager.store_memory(leader_advisor_id, memory)
        
        return faction_id
    
    def join_political_faction(self, advisor_id: str, faction_id: str) -> bool:
        """Have an advisor join a political faction."""
        if not self.advanced_politics:
            return False
        
        success = self.advanced_politics.join_faction(advisor_id, faction_id)
        
        if success and self.memory_manager:
            # Find faction name for memory
            faction = self.advanced_politics._find_faction(faction_id)
            faction_name = faction.name if faction else "Unknown Faction"
            
            memory_content = f"Joined political faction '{faction_name}'"
            memory = Memory(
                advisor_id=advisor_id,
                event_type=MemoryType.DECISION,
                content=memory_content,
                emotional_impact=0.6,
                created_turn=self.current_turn,
                last_accessed_turn=self.current_turn,
                tags={"faction", "politics", "membership"}
            )
            self.memory_manager.store_memory(advisor_id, memory)
        
        return success
    
    def form_conspiracy(self, leader_advisor_id: str, conspiracy_type: ConspiracyType,
                       objective: str, target: Optional[str] = None) -> str:
        """Form a conspiracy within the civilization."""
        if not self.advanced_politics:
            return ""
        
        conspiracy_id = self.advanced_politics.form_conspiracy(
            leader_advisor_id, conspiracy_type, objective, target
        )
        
        # Create memory for conspiracy leader (secret memory)
        if self.memory_manager:
            memory_content = f"Formed secret conspiracy: {objective}"
            memory = Memory(
                advisor_id=leader_advisor_id,
                event_type=MemoryType.CONSPIRACY,
                content=memory_content,
                emotional_impact=0.9,
                created_turn=self.current_turn,
                last_accessed_turn=self.current_turn,
                tags={"conspiracy", "secret", conspiracy_type.value, "leader"}
            )
            self.memory_manager.store_memory(leader_advisor_id, memory)
        
        return conspiracy_id
    
    def recruit_to_conspiracy(self, conspiracy_id: str, recruiter_id: str, target_id: str) -> bool:
        """Attempt to recruit an advisor to a conspiracy."""
        if not self.advanced_politics:
            return False
        
        # Get advisor relationships for recruitment calculation
        advisor_relationships = {}
        for advisor_id, advisor in self.advisors.items():
            advisor_relationships[advisor_id] = {}
            for other_id, relationship in advisor.relationships.items():
                advisor_relationships[advisor_id][other_id] = {
                    'trust': relationship.trust,
                    'conspiracy_level': relationship.conspiracy_level
                }
        
        success = self.advanced_politics.recruit_to_conspiracy(
            conspiracy_id, recruiter_id, target_id, advisor_relationships
        )
        
        if success and self.memory_manager:
            # Create memory for both recruiter and target
            conspiracy = self.advanced_politics._find_conspiracy(conspiracy_id)
            objective = conspiracy.objective if conspiracy else "Unknown conspiracy"
            
            # Recruiter memory
            recruiter_memory = Memory(
                advisor_id=recruiter_id,
                event_type=MemoryType.CONSPIRACY,
                content=f"Successfully recruited {target_id} to conspiracy: {objective}",
                emotional_impact=0.7,
                created_turn=self.current_turn,
                last_accessed_turn=self.current_turn,
                tags={"conspiracy", "recruitment", "success"}
            )
            self.memory_manager.store_memory(recruiter_id, recruiter_memory)
            
            # Target memory
            target_memory = Memory(
                advisor_id=target_id,
                event_type=MemoryType.CONSPIRACY,
                content=f"Joined conspiracy led by {recruiter_id}: {objective}",
                emotional_impact=0.8,
                created_turn=self.current_turn,
                last_accessed_turn=self.current_turn,
                tags={"conspiracy", "secret", "member"}
            )
            self.memory_manager.store_memory(target_id, target_memory)
        
        return success
    
    def launch_propaganda_campaign(self, sponsor_advisor_id: str, campaign_type: PropagandaType,
                                  message: str, target: Optional[str] = None, funding: float = 100.0) -> str:
        """Launch a propaganda campaign."""
        if not self.advanced_politics:
            return ""
        
        campaign_id = self.advanced_politics.launch_propaganda_campaign(
            sponsor_advisor_id, campaign_type, message, target, funding
        )
        
        # Create memory for sponsor
        if self.memory_manager:
            memory_content = f"Launched {campaign_type.value} propaganda campaign: {message}"
            memory = Memory(
                advisor_id=sponsor_advisor_id,
                event_type=MemoryType.DECISION,
                content=memory_content,
                emotional_impact=0.6,
                created_turn=self.current_turn,
                last_accessed_turn=self.current_turn,
                tags={"propaganda", "information_warfare", campaign_type.value}
            )
            self.memory_manager.store_memory(sponsor_advisor_id, memory)
        
        return campaign_id
    
    def propose_political_reform(self, proposer_id: str, name: str, description: str,
                                reform_scope: str, required_votes: int = 3) -> str:
        """Propose a political reform."""
        if not self.advanced_politics:
            return ""
        
        reform_id = self.advanced_politics.propose_reform(
            proposer_id, name, description, reform_scope, required_votes
        )
        
        # Create memory for proposer
        if self.memory_manager:
            memory_content = f"Proposed political reform '{name}': {description}"
            memory = Memory(
                advisor_id=proposer_id,
                event_type=MemoryType.DECISION,
                content=memory_content,
                emotional_impact=0.7,
                created_turn=self.current_turn,
                last_accessed_turn=self.current_turn,
                tags={"reform", "politics", "proposal", reform_scope}
            )
            self.memory_manager.store_memory(proposer_id, memory)
        
        return reform_id
    
    def vote_on_reform(self, reform_id: str, voter_id: str, support: bool) -> bool:
        """Cast a vote on a proposed reform."""
        if not self.advanced_politics:
            return False
        
        success = self.advanced_politics.vote_on_reform(reform_id, voter_id, support)
        
        if success and self.memory_manager:
            # Find reform name for memory
            reform = self.advanced_politics._find_reform(reform_id)
            reform_name = reform.name if reform else "Unknown Reform"
            
            memory_content = f"Voted {'for' if support else 'against'} reform '{reform_name}'"
            memory = Memory(
                advisor_id=voter_id,
                event_type=MemoryType.DECISION,
                content=memory_content,
                emotional_impact=0.5,
                created_turn=self.current_turn,
                last_accessed_turn=self.current_turn,
                tags={"reform", "vote", "support" if support else "opposition"}
            )
            self.memory_manager.store_memory(voter_id, memory)
        
        return success
    
    def trigger_succession_crisis(self, crisis_type: SuccessionCrisisType) -> bool:
        """Trigger a succession crisis."""
        if not self.advanced_politics:
            return False
        
        success = self.advanced_politics.trigger_succession_crisis(crisis_type)
        
        if success and self.memory_manager:
            # Create memories for all advisors about the crisis
            memory_content = f"Succession crisis triggered: {crisis_type.value}"
            for advisor in self.advisors.values():
                memory = Memory(
                    advisor_id=advisor.id,
                    event_type=MemoryType.CRISIS,
                    content=memory_content,
                    emotional_impact=0.9,
                    created_turn=self.current_turn,
                    last_accessed_turn=self.current_turn,
                    tags={"succession", "crisis", crisis_type.value, "instability"}
                )
                self.memory_manager.store_memory(advisor.id, memory)
        
        return success
    
    def get_political_factions(self) -> List[Dict[str, Any]]:
        """Get information about all political factions."""
        if not self.advanced_politics:
            return []
        
        factions_info = []
        for faction in self.advanced_politics.political_factions:
            factions_info.append({
                "id": faction.id,
                "name": faction.name,
                "type": faction.faction_type,
                "ideology": faction.ideology,
                "leader_id": faction.leader_id,
                "member_count": len(faction.members),
                "influence": faction.influence,
                "popularity": faction.popularity,
                "political_power": faction.calculate_political_power()
            })
        
        return factions_info
    
    def get_active_conspiracies(self) -> List[Dict[str, Any]]:
        """Get information about active conspiracies (for debugging/admin view)."""
        if not self.advanced_politics:
            return []
        
        conspiracies_info = []
        for conspiracy in self.advanced_politics.active_conspiracies:
            conspiracies_info.append({
                "id": conspiracy.id,
                "type": conspiracy.conspiracy_type,
                "status": conspiracy.status,
                "leader_id": conspiracy.leader_id,
                "member_count": len(conspiracy.members),
                "objective": conspiracy.objective,
                "target": conspiracy.target,
                "network_strength": conspiracy.network_strength,
                "secrecy_level": conspiracy.secrecy_level,
                "discovery_risk": conspiracy.discovery_risk,
                "success_probability": conspiracy.calculate_success_probability()
            })
        
        return conspiracies_info
    
    def get_advanced_political_summary(self) -> Dict[str, Any]:
        """Get comprehensive advanced political situation summary."""
        if not self.advanced_politics:
            return {"error": "Advanced politics not initialized"}
        
        return self.advanced_politics.get_political_summary()
    
    # ========== END ADVANCED POLITICAL METHODS ==========
    
    def get_comprehensive_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary including political, resource, diplomatic, and advanced political information."""
        political_summary = self.get_political_summary()
        resource_summary = self.get_resource_summary()
        diplomatic_summary = self.get_diplomatic_summary()
        advanced_political_summary = self.get_advanced_political_summary()
        
        return {
            "political": political_summary,
            "resources": resource_summary,
            "diplomacy": diplomatic_summary,
            "advanced_politics": advanced_political_summary,
            "integration": {
                "total_advisors": len(self.advisors),
                "memory_manager_active": self.memory_manager is not None,
                "event_manager_active": self.event_manager is not None,
                "resource_manager_active": self.resource_manager is not None,
                "diplomacy_manager_active": self.diplomacy_manager is not None,
                "advanced_politics_active": self.advanced_politics is not None,
                "active_resource_events": len(self.resource_manager.active_events) if self.resource_manager else 0,
                "known_civilizations": len(self.known_civilizations),
                "active_treaties": len(self.international_treaties)
            }
        }
