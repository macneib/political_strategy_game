"""
Civilization class that manages the complete political state of an AI empire.
"""

from typing import Dict, List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field
import uuid

from .advisor import Advisor, AdvisorRole, AdvisorStatus
from .leader import Leader, LeadershipStyle
from .memory import MemoryBank
from .political_event import PoliticalEvent, EventFactory, EventProcessor


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
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    current_turn: int = Field(default=1)
    
    # Leadership
    leader: Leader
    advisors: Dict[str, Advisor] = Field(default_factory=dict)
    
    # Political state
    political_state: PoliticalState = Field(default_factory=PoliticalState)
    memory_bank: Optional[MemoryBank] = Field(default=None)
    
    # Event management
    event_history: List[PoliticalEvent] = Field(default_factory=list)
    pending_events: List[PoliticalEvent] = Field(default_factory=list)
    
    # Technologies and capabilities
    unlocked_technologies: Set[str] = Field(default_factory=set)
    espionage_capabilities: Dict[str, float] = Field(default_factory=dict)
    
    def model_post_init(self, __context):
        """Initialize computed fields after model creation."""
        if self.memory_bank is None:
            self.memory_bank = MemoryBank(civilization_id=self.id)
    
    def add_advisor(self, advisor: Advisor) -> bool:
        """Add a new advisor to the civilization."""
        if advisor.role in [a.role for a in self.advisors.values() if a.status == AdvisorStatus.ACTIVE]:
            return False  # Role already filled
        
        advisor.civilization_id = self.id
        advisor.appointment_turn = self.current_turn
        advisor.appointed_by_leader = self.leader.id
        
        self.advisors[advisor.id] = advisor
        
        # Create appointment event
        event = EventFactory.create_appointment_event(
            civilization_id=self.id,
            leader_id=self.leader.id,
            advisor_id=advisor.id,
            role=advisor.role.value,
            action="appoint",
            turn=self.current_turn
        )
        self.event_history.append(event)
        
        return True
    
    def dismiss_advisor(self, advisor_id: str, reason: str = "performance") -> bool:
        """Dismiss an advisor from their position."""
        if advisor_id not in self.advisors:
            return False
        
        advisor = self.advisors[advisor_id]
        if advisor.status != AdvisorStatus.ACTIVE:
            return False
        
        advisor.status = AdvisorStatus.DISMISSED
        
        # Create dismissal event
        event = EventFactory.create_appointment_event(
            civilization_id=self.id,
            leader_id=self.leader.id,
            advisor_id=advisor_id,
            role=advisor.role.value,
            action="dismiss",
            turn=self.current_turn
        )
        event.context["reason"] = reason
        self.event_history.append(event)
        
        # Update political state
        self._update_political_stability()
        
        return True
    
    def get_active_advisors(self) -> List[Advisor]:
        """Get all currently active advisors."""
        return [advisor for advisor in self.advisors.values() 
                if advisor.status == AdvisorStatus.ACTIVE]
    
    def get_advisor_by_role(self, role: AdvisorRole) -> Optional[Advisor]:
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
    
    def detect_conspiracies(self) -> List[Dict[str, any]]:
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
        
        # Create coup event
        event = EventFactory.create_coup_event(
            civilization_id=self.id,
            conspirators=conspirators,
            target_leader_id=self.leader.id,
            success=success,
            turn=self.current_turn
        )
        self.event_history.append(event)
        
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
    
    def process_turn(self) -> Dict[str, any]:
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
    
    def get_political_summary(self) -> Dict[str, any]:
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
