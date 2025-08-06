"""
Political events that drive the internal dynamics of civilizations.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class EventType(str, Enum):
    """Types of political events that can occur."""
    DECISION = "decision"              # Leader makes a major decision
    CRISIS = "crisis"                  # External crisis requiring response
    CONSPIRACY = "conspiracy"          # Advisors plotting together
    COUP = "coup"                     # Attempt to overthrow leader
    APPOINTMENT = "appointment"        # New advisor appointed or dismissed
    BETRAYAL = "betrayal"             # Advisor betrays another or the leader
    SCANDAL = "scandal"               # Corruption or misconduct exposed
    SUCCESS = "success"               # Major achievement for the civilization
    FAILURE = "failure"               # Major failure or setback
    INTELLIGENCE = "intelligence"      # Espionage or information warfare


class EventSeverity(str, Enum):
    """How severe the political impact of an event is."""
    MINOR = "minor"        # Small local impact
    MODERATE = "moderate"  # Noticeable but manageable impact
    MAJOR = "major"        # Significant political ramifications
    CRITICAL = "critical"  # Civilization-threatening event


class Consequence(BaseModel):
    """A specific consequence of a political event."""
    
    target_type: str = Field(description="What is affected: advisor, leader, relationship, etc.")
    target_id: str = Field(description="ID of the specific target")
    effect_type: str = Field(description="Type of effect: loyalty_change, trust_change, etc.")
    magnitude: float = Field(description="Strength of the effect (-1.0 to 1.0)")
    description: str = Field(description="Human-readable description of the consequence")


class PoliticalEvent(BaseModel):
    """A political event that affects the internal dynamics of a civilization."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType
    severity: EventSeverity
    civilization_id: str
    turn_occurred: int
    
    # Event details
    title: str = Field(description="Short title for the event")
    description: str = Field(description="Detailed description of what happened")
    
    # Participants
    initiator_id: Optional[str] = Field(default=None, description="Who started this event")
    participants: List[str] = Field(default_factory=list, description="All involved advisor IDs")
    target_id: Optional[str] = Field(default=None, description="Primary target of the event")
    
    # Event context and data
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    
    # Consequences and results
    consequences: List[Consequence] = Field(default_factory=list)
    success_probability: Optional[float] = Field(default=None, description="Chance of success (for risky events)")
    actual_outcome: Optional[str] = Field(default=None, description="What actually happened")
    
    # Meta information
    is_secret: bool = Field(default=False, description="Whether this event is known publicly")
    witnesses: List[str] = Field(default_factory=list, description="Who knows about this event")
    
    def add_consequence(self, target_type: str, target_id: str, effect_type: str, 
                       magnitude: float, description: str) -> None:
        """Add a consequence to this event."""
        consequence = Consequence(
            target_type=target_type,
            target_id=target_id,
            effect_type=effect_type,
            magnitude=magnitude,
            description=description
        )
        self.consequences.append(consequence)
    
    def get_consequences_for_target(self, target_id: str) -> List[Consequence]:
        """Get all consequences affecting a specific target."""
        return [c for c in self.consequences if c.target_id == target_id]
    
    def is_visible_to(self, advisor_id: str) -> bool:
        """Check if an advisor knows about this event."""
        if not self.is_secret:
            return True
        return advisor_id in self.witnesses or advisor_id in self.participants


class EventFactory:
    """Factory for creating common types of political events."""
    
    @staticmethod
    def create_decision_event(civilization_id: str, leader_id: str, decision_type: str,
                            advisor_recommendations: Dict[str, str], 
                            leader_choice: str, turn: int) -> PoliticalEvent:
        """Create an event for a major leader decision."""
        
        # Determine if leader followed advisor recommendations
        followed_advice = leader_choice in advisor_recommendations.values()
        
        event = PoliticalEvent(
            type=EventType.DECISION,
            severity=EventSeverity.MODERATE,
            civilization_id=civilization_id,
            turn_occurred=turn,
            title=f"Leader Decision: {decision_type}",
            description=f"Leader chose '{leader_choice}' regarding {decision_type}",
            initiator_id=leader_id,
            participants=[leader_id] + list(advisor_recommendations.keys()),
            context={
                "decision_type": decision_type,
                "recommendations": advisor_recommendations,
                "choice": leader_choice,
                "followed_advice": followed_advice
            },
            tags=["decision", decision_type]
        )
        
        # Add consequences for advisors based on whether their advice was followed
        for advisor_id, recommendation in advisor_recommendations.items():
            if recommendation == leader_choice:
                # Advisor's recommendation was followed - increase trust and influence
                event.add_consequence(
                    target_type="advisor",
                    target_id=advisor_id,
                    effect_type="influence_increase",
                    magnitude=0.1,
                    description=f"Advisor's recommendation was followed"
                )
                event.add_consequence(
                    target_type="relationship",
                    target_id=f"{leader_id}-{advisor_id}",
                    effect_type="trust_increase",
                    magnitude=0.15,
                    description="Leader followed advisor's counsel"
                )
            else:
                # Advisor's recommendation was ignored - potential loyalty decrease
                event.add_consequence(
                    target_type="advisor",
                    target_id=advisor_id,
                    effect_type="loyalty_decrease",
                    magnitude=0.05,
                    description="Leader ignored advisor's recommendation"
                )
        
        return event
    
    @staticmethod
    def create_conspiracy_event(civilization_id: str, conspirators: List[str], 
                              target_id: str, conspiracy_type: str, turn: int) -> PoliticalEvent:
        """Create an event for advisors forming a conspiracy."""
        
        event = PoliticalEvent(
            type=EventType.CONSPIRACY,
            severity=EventSeverity.MAJOR,
            civilization_id=civilization_id,
            turn_occurred=turn,
            title=f"Conspiracy Formed: {conspiracy_type}",
            description=f"Advisors have formed a conspiracy to {conspiracy_type}",
            participants=conspirators,
            target_id=target_id,
            context={
                "conspiracy_type": conspiracy_type,
                "conspirator_count": len(conspirators)
            },
            tags=["conspiracy", conspiracy_type],
            is_secret=True,
            witnesses=conspirators
        )
        
        # Increase conspiracy relationships between participants
        for i, conspirator1 in enumerate(conspirators):
            for conspirator2 in conspirators[i+1:]:
                event.add_consequence(
                    target_type="relationship",
                    target_id=f"{conspirator1}-{conspirator2}",
                    effect_type="conspiracy_increase",
                    magnitude=0.2,
                    description="Participated in conspiracy together"
                )
        
        return event
    
    @staticmethod
    def create_coup_event(civilization_id: str, conspirators: List[str], 
                         target_leader_id: str, success: bool, turn: int) -> PoliticalEvent:
        """Create an event for a coup attempt."""
        
        outcome = "successful" if success else "failed"
        severity = EventSeverity.CRITICAL
        
        event = PoliticalEvent(
            type=EventType.COUP,
            severity=severity,
            civilization_id=civilization_id,
            turn_occurred=turn,
            title=f"Coup Attempt: {outcome.capitalize()}",
            description=f"Advisors attempted to overthrow the leader - {outcome}",
            participants=conspirators,
            target_id=target_leader_id,
            context={
                "success": success,
                "conspirator_count": len(conspirators)
            },
            tags=["coup", outcome],
            actual_outcome=outcome
        )
        
        if success:
            # Successful coup - new leader appointed from conspirators
            event.add_consequence(
                target_type="leader",
                target_id=target_leader_id,
                effect_type="removed_from_power",
                magnitude=1.0,
                description="Overthrown in coup"
            )
            
            # Promote lead conspirator to leader
            if conspirators:
                event.add_consequence(
                    target_type="advisor",
                    target_id=conspirators[0],
                    effect_type="promoted_to_leader",
                    magnitude=1.0,
                    description="Led successful coup and became new leader"
                )
        else:
            # Failed coup - conspirators face consequences
            for conspirator in conspirators:
                event.add_consequence(
                    target_type="advisor",
                    target_id=conspirator,
                    effect_type="loyalty_decrease",
                    magnitude=0.5,
                    description="Participated in failed coup"
                )
                event.add_consequence(
                    target_type="advisor",
                    target_id=conspirator,
                    effect_type="influence_decrease",
                    magnitude=0.3,
                    description="Lost influence after failed coup"
                )
        
        return event
    
    @staticmethod
    def create_appointment_event(civilization_id: str, leader_id: str, 
                               advisor_id: str, role: str, action: str, turn: int) -> PoliticalEvent:
        """Create an event for advisor appointment or dismissal."""
        
        action_past = "appointed" if action == "appoint" else "dismissed"
        
        event = PoliticalEvent(
            type=EventType.APPOINTMENT,
            severity=EventSeverity.MODERATE,
            civilization_id=civilization_id,
            turn_occurred=turn,
            title=f"Advisor {action_past.capitalize()}",
            description=f"Leader {action_past} advisor to role of {role}",
            initiator_id=leader_id,
            participants=[leader_id, advisor_id],
            context={
                "action": action,
                "role": role
            },
            tags=["appointment", action, role]
        )
        
        if action == "appoint":
            event.add_consequence(
                target_type="advisor",
                target_id=advisor_id,
                effect_type="influence_increase",
                magnitude=0.2,
                description=f"Appointed to {role} position"
            )
        else:  # dismiss
            event.add_consequence(
                target_type="advisor",
                target_id=advisor_id,
                effect_type="influence_decrease",
                magnitude=0.3,
                description=f"Dismissed from {role} position"
            )
            event.add_consequence(
                target_type="advisor",
                target_id=advisor_id,
                effect_type="loyalty_decrease",
                magnitude=0.4,
                description="Dismissed by leader"
            )
        
        return event
    
    @staticmethod
    def create_crisis_event(civilization_id: str, crisis_type: str, 
                          severity: EventSeverity, turn: int) -> PoliticalEvent:
        """Create an event for an external crisis requiring response."""
        
        event = PoliticalEvent(
            type=EventType.CRISIS,
            severity=severity,
            civilization_id=civilization_id,
            turn_occurred=turn,
            title=f"Crisis: {crisis_type}",
            description=f"The civilization faces a {crisis_type} crisis",
            context={
                "crisis_type": crisis_type,
                "requires_response": True
            },
            tags=["crisis", crisis_type]
        )
        
        return event


class EventProcessor:
    """Processes political events and applies their consequences."""
    
    def __init__(self):
        self.processed_events: List[str] = []
    
    def process_event(self, event: PoliticalEvent, advisors: Dict[str, Any], 
                     leaders: Dict[str, Any]) -> Dict[str, Any]:
        """Process an event and apply its consequences."""
        if event.id in self.processed_events:
            return {"error": "Event already processed"}
        
        results = {
            "event_id": event.id,
            "consequences_applied": [],
            "errors": []
        }
        
        # Apply each consequence
        for consequence in event.consequences:
            try:
                result = self._apply_consequence(consequence, advisors, leaders)
                results["consequences_applied"].append(result)
            except Exception as e:
                results["errors"].append(f"Error applying consequence: {str(e)}")
        
        self.processed_events.append(event.id)
        return results
    
    def _apply_consequence(self, consequence: Consequence, 
                          advisors: Dict[str, Any], leaders: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a single consequence to the game state."""
        result = {
            "consequence_type": consequence.effect_type,
            "target": consequence.target_id,
            "magnitude": consequence.magnitude,
            "applied": False
        }
        
        if consequence.target_type == "advisor":
            advisor = advisors.get(consequence.target_id)
            if advisor:
                self._apply_advisor_effect(advisor, consequence)
                result["applied"] = True
        
        elif consequence.target_type == "leader":
            leader = leaders.get(consequence.target_id)
            if leader:
                self._apply_leader_effect(leader, consequence)
                result["applied"] = True
        
        elif consequence.target_type == "relationship":
            # Handle relationship effects between advisors or advisor-leader
            self._apply_relationship_effect(consequence, advisors, leaders)
            result["applied"] = True
        
        return result
    
    def _apply_advisor_effect(self, advisor: Any, consequence: Consequence) -> None:
        """Apply an effect to an advisor."""
        if consequence.effect_type == "loyalty_decrease":
            advisor.loyalty_to_leader = max(0.0, 
                advisor.loyalty_to_leader - abs(consequence.magnitude))
        elif consequence.effect_type == "loyalty_increase":
            advisor.loyalty_to_leader = min(1.0, 
                advisor.loyalty_to_leader + abs(consequence.magnitude))
        elif consequence.effect_type == "influence_decrease":
            advisor.influence = max(0.0, 
                advisor.influence - abs(consequence.magnitude))
        elif consequence.effect_type == "influence_increase":
            advisor.influence = min(1.0, 
                advisor.influence + abs(consequence.magnitude))
    
    def _apply_leader_effect(self, leader: Any, consequence: Consequence) -> None:
        """Apply an effect to a leader."""
        if consequence.effect_type == "legitimacy_decrease":
            leader.legitimacy = max(0.0, 
                leader.legitimacy - abs(consequence.magnitude))
        elif consequence.effect_type == "legitimacy_increase":
            leader.legitimacy = min(1.0, 
                leader.legitimacy + abs(consequence.magnitude))
        elif consequence.effect_type == "paranoia_increase":
            leader.paranoia_level = min(1.0, 
                leader.paranoia_level + abs(consequence.magnitude))
    
    def _apply_relationship_effect(self, consequence: Consequence, 
                                  advisors: Dict[str, Any], leaders: Dict[str, Any]) -> None:
        """Apply an effect to a relationship between two entities."""
        # Parse relationship ID (format: "entity1_id-entity2_id")
        if "-" in consequence.target_id:
            id1, id2 = consequence.target_id.split("-", 1)
            
            # Find the entities and update their relationship
            entity1 = advisors.get(id1) or leaders.get(id1)
            entity2 = advisors.get(id2) or leaders.get(id2)
            
            if entity1 and hasattr(entity1, 'relationships'):
                relationship = entity1.get_relationship(id2)
                if consequence.effect_type == "trust_increase":
                    relationship.trust = min(1.0, relationship.trust + abs(consequence.magnitude))
                elif consequence.effect_type == "trust_decrease":
                    relationship.trust = max(-1.0, relationship.trust - abs(consequence.magnitude))
                elif consequence.effect_type == "conspiracy_increase":
                    relationship.conspiracy_level = min(1.0, 
                        relationship.conspiracy_level + abs(consequence.magnitude))
