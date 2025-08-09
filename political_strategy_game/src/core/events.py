"""
Political event system for the strategy game.
"""

from typing import Dict, List, Optional, Set, Any, Callable
from enum import Enum
from pydantic import BaseModel, Field
import uuid
import random
from datetime import datetime

from .memory import MemoryType, Memory
from .advisor import AdvisorRole


class EventType(str, Enum):
    """Types of political events that can occur."""
    CRISIS = "crisis"
    OPPORTUNITY = "opportunity"
    DECISION = "decision"
    EXTERNAL_THREAT = "external_threat"
    INTERNAL_CONFLICT = "internal_conflict"
    ECONOMIC_EVENT = "economic_event"
    DIPLOMATIC_EVENT = "diplomatic_event"
    MILITARY_EVENT = "military_event"
    CULTURAL_EVENT = "cultural_event"
    RANDOM_EVENT = "random_event"


class EventSeverity(str, Enum):
    """Severity levels for events."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


class EventStatus(str, Enum):
    """Current status of an event."""
    PENDING = "pending"
    ACTIVE = "active"
    RESOLVED = "resolved"
    EXPIRED = "expired"


class EventChoice(BaseModel):
    """A choice option for responding to an event."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    required_role: Optional[AdvisorRole] = None
    consequences: Dict[str, float] = Field(default_factory=dict)
    requirements: Dict[str, Any] = Field(default_factory=dict)
    tags: Set[str] = Field(default_factory=set)


class PoliticalEvent(BaseModel):
    """A political event that requires player/advisor response."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    event_type: EventType
    severity: EventSeverity
    status: EventStatus = EventStatus.PENDING
    
    # Timing and duration
    triggered_turn: int
    expires_turn: Optional[int] = None
    auto_resolve_turn: Optional[int] = None
    
    # Event characteristics
    affected_advisors: Set[str] = Field(default_factory=set)
    required_roles: Set[AdvisorRole] = Field(default_factory=set)
    tags: Set[str] = Field(default_factory=set)
    
    # Player choices
    choices: List[EventChoice] = Field(default_factory=list)
    chosen_response: Optional[str] = None
    response_turn: Optional[int] = None
    
    # Event effects
    base_effects: Dict[str, float] = Field(default_factory=dict)
    ongoing_effects: Dict[str, float] = Field(default_factory=dict)
    
    # Narrative elements
    flavor_text: Optional[str] = None
    resolution_text: Optional[str] = None
    
    def is_active(self, current_turn: int) -> bool:
        """Check if event is currently active."""
        if self.status != EventStatus.ACTIVE:
            return False
        if self.expires_turn and current_turn >= self.expires_turn:
            return False
        return True
    
    def should_auto_resolve(self, current_turn: int) -> bool:
        """Check if event should auto-resolve."""
        return (self.auto_resolve_turn is not None and 
                current_turn >= self.auto_resolve_turn and
                self.status == EventStatus.ACTIVE)
    
    def add_choice(self, title: str, description: str, 
                   consequences: Optional[Dict[str, float]] = None,
                   required_role: Optional[AdvisorRole] = None,
                   **kwargs) -> EventChoice:
        """Add a choice option to this event."""
        choice = EventChoice(
            title=title,
            description=description,
            consequences=consequences or {},
            required_role=required_role,
            **kwargs
        )
        self.choices.append(choice)
        return choice


class EventTemplate(BaseModel):
    """Template for generating similar events."""
    
    id: str
    title_template: str
    description_template: str
    event_type: EventType
    severity: EventSeverity
    
    # Generation parameters
    trigger_conditions: Dict[str, Any] = Field(default_factory=dict)
    frequency_weight: float = 1.0
    cooldown_turns: int = 0
    
    # Template choices
    choice_templates: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Variable substitution
    variables: Dict[str, List[str]] = Field(default_factory=dict)
    
    def generate_event(self, current_turn: int, context: Dict[str, Any]) -> PoliticalEvent:
        """Generate a concrete event from this template."""
        # Substitute variables in title and description
        title = self._substitute_variables(self.title_template, context)
        description = self._substitute_variables(self.description_template, context)
        
        event = PoliticalEvent(
            title=title,
            description=description,
            event_type=self.event_type,
            severity=self.severity,
            triggered_turn=current_turn,
            tags=set(context.get('tags', [])),
            affected_advisors=set(context.get('affected_advisors', []))
        )
        
        # Set expiration based on severity
        if self.severity == EventSeverity.CRITICAL:
            event.expires_turn = current_turn + 3
            event.auto_resolve_turn = current_turn + 2
        elif self.severity == EventSeverity.MAJOR:
            event.expires_turn = current_turn + 5
            event.auto_resolve_turn = current_turn + 3
        else:
            event.expires_turn = current_turn + 10
            event.auto_resolve_turn = current_turn + 7
        
        # Generate choices from templates
        for choice_template in self.choice_templates:
            choice_title = self._substitute_variables(choice_template['title'], context)
            choice_desc = self._substitute_variables(choice_template['description'], context)
            
            event.add_choice(
                title=choice_title,
                description=choice_desc,
                consequences=choice_template.get('consequences', {}),
                required_role=choice_template.get('required_role'),
                tags=set(choice_template.get('tags', []))
            )
        
        return event
    
    def _substitute_variables(self, template: str, context: Dict[str, Any]) -> str:
        """Substitute variables in a template string."""
        result = template
        
        # Simple variable substitution
        for var_name, var_value in context.items():
            if isinstance(var_value, str):
                result = result.replace(f"{{{var_name}}}", var_value)
        
        # Random variable selection
        for var_name, options in self.variables.items():
            if f"{{{var_name}}}" in result:
                selected = random.choice(options)
                result = result.replace(f"{{{var_name}}}", selected)
        
        return result


class EventOutcome(BaseModel):
    """The result of resolving an event."""
    
    event_id: str
    choice_id: Optional[str]
    resolution_turn: int
    
    # Direct effects
    immediate_effects: Dict[str, float] = Field(default_factory=dict)
    ongoing_effects: Dict[str, float] = Field(default_factory=dict)
    
    # Memory creation for advisors
    advisor_memories: List[Memory] = Field(default_factory=list)
    
    # Relationship changes
    relationship_changes: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    
    # Follow-up events
    triggered_events: List[str] = Field(default_factory=list)
    
    # Narrative
    outcome_text: str = ""


class EventManager(BaseModel):
    """Manages the political event system."""
    
    model_config = {"arbitrary_types_allowed": True}
    
    civilization_id: str
    current_turn: int = 0
    
    # Active events
    active_events: Dict[str, PoliticalEvent] = Field(default_factory=dict)
    resolved_events: List[PoliticalEvent] = Field(default_factory=list)
    
    # Event generation
    event_templates: Dict[str, EventTemplate] = Field(default_factory=dict)
    template_cooldowns: Dict[str, int] = Field(default_factory=dict)
    
    # Event history for pattern analysis
    event_history: List[EventOutcome] = Field(default_factory=list)
    
    def advance_turn(self, new_turn: int) -> List[PoliticalEvent]:
        """Advance to a new turn and process events."""
        self.current_turn = new_turn
        
        # Check for auto-resolving events
        auto_resolved = []
        for event in list(self.active_events.values()):
            if event.should_auto_resolve(self.current_turn):
                outcome = self._auto_resolve_event(event)
                auto_resolved.append(event)
        
        # Remove expired events
        expired_events = []
        for event_id, event in list(self.active_events.items()):
            if not event.is_active(self.current_turn):
                event.status = EventStatus.EXPIRED
                self.resolved_events.append(event)
                del self.active_events[event_id]
                expired_events.append(event)
        
        # Generate new events
        new_events = self._generate_random_events()
        
        return new_events + auto_resolved
    
    def add_event_template(self, template: EventTemplate) -> None:
        """Add an event template for random generation."""
        self.event_templates[template.id] = template
    
    def trigger_event(self, template_id: str, context: Optional[Dict[str, Any]] = None) -> PoliticalEvent:
        """Manually trigger an event from a template."""
        if template_id not in self.event_templates:
            raise ValueError(f"Unknown event template: {template_id}")
        
        template = self.event_templates[template_id]
        event = template.generate_event(self.current_turn, context or {})
        event.status = EventStatus.ACTIVE
        
        self.active_events[event.id] = event
        return event
    
    def respond_to_event(self, event_id: str, choice_id: str, responding_advisor_id: Optional[str] = None) -> EventOutcome:
        """Respond to an event with a specific choice."""
        if event_id not in self.active_events:
            raise ValueError(f"Event {event_id} not found or not active")
        
        event = self.active_events[event_id]
        choice = None
        
        for c in event.choices:
            if c.id == choice_id:
                choice = c
                break
        
        if not choice:
            raise ValueError(f"Choice {choice_id} not found for event {event_id}")
        
        # Record the response
        event.chosen_response = choice_id
        event.response_turn = self.current_turn
        event.status = EventStatus.RESOLVED
        
        # Calculate outcome
        outcome = self._calculate_outcome(event, choice, responding_advisor_id)
        
        # Move event to resolved
        self.resolved_events.append(event)
        del self.active_events[event_id]
        
        # Add to history
        self.event_history.append(outcome)
        
        return outcome
    
    def get_available_events(self) -> List[PoliticalEvent]:
        """Get all currently active events."""
        return [event for event in self.active_events.values() 
                if event.is_active(self.current_turn)]
    
    def _generate_random_events(self) -> List[PoliticalEvent]:
        """Generate random events based on templates and conditions."""
        new_events = []
        
        # Simple random event generation
        if random.random() < 0.3:  # 30% chance per turn
            available_templates = []
            
            for template_id, template in self.event_templates.items():
                # Check cooldown
                if (template_id in self.template_cooldowns and 
                    self.current_turn < self.template_cooldowns[template_id]):
                    continue
                
                available_templates.append(template)
            
            if available_templates:
                # Weight-based selection
                weights = [t.frequency_weight for t in available_templates]
                selected_template = random.choices(available_templates, weights=weights)[0]
                
                # Generate event
                context = self._get_generation_context()
                event = selected_template.generate_event(self.current_turn, context)
                event.status = EventStatus.ACTIVE
                
                self.active_events[event.id] = event
                new_events.append(event)
                
                # Set cooldown
                if selected_template.cooldown_turns > 0:
                    self.template_cooldowns[selected_template.id] = (
                        self.current_turn + selected_template.cooldown_turns
                    )
        
        return new_events
    
    def _get_generation_context(self) -> Dict[str, Any]:
        """Get context information for event generation."""
        return {
            'current_turn': self.current_turn,
            'civilization_id': self.civilization_id,
            'tags': ['general'],
            'affected_advisors': []
        }
    
    def _auto_resolve_event(self, event: PoliticalEvent) -> PoliticalEvent:
        """Auto-resolve an event that wasn't responded to."""
        # Choose a random response or default negative outcome
        if event.choices:
            # Pick the least severe choice
            default_choice = min(event.choices, 
                               key=lambda c: sum(abs(v) for v in c.consequences.values()))
            outcome = self._calculate_outcome(event, default_choice, None)
        else:
            # Create a default negative outcome
            outcome = EventOutcome(
                event_id=event.id,
                choice_id=None,
                resolution_turn=self.current_turn,
                immediate_effects={'stability': -0.1},
                outcome_text="The situation was left unresolved and deteriorated."
            )
        
        event.status = EventStatus.RESOLVED
        event.resolution_text = outcome.outcome_text
        
        self.resolved_events.append(event)
        if event.id in self.active_events:
            del self.active_events[event.id]
        
        self.event_history.append(outcome)
        return event
    
    def _calculate_outcome(self, event: PoliticalEvent, choice: EventChoice, 
                          advisor_id: Optional[str]) -> EventOutcome:
        """Calculate the outcome of an event response."""
        outcome = EventOutcome(
            event_id=event.id,
            choice_id=choice.id,
            resolution_turn=self.current_turn,
            immediate_effects=choice.consequences.copy()
        )
        
        # Add base event effects
        for effect, value in event.base_effects.items():
            outcome.immediate_effects[effect] = outcome.immediate_effects.get(effect, 0) + value
        
        # Create memories for affected advisors
        for advisor_id in event.affected_advisors:
            memory = Memory(
                advisor_id=advisor_id,
                event_type=self._event_type_to_memory_type(event.event_type),
                content=f"Responded to {event.title} with {choice.title}",
                emotional_impact=self._calculate_emotional_impact(event, choice),
                created_turn=self.current_turn,
                last_accessed_turn=self.current_turn,
                tags=event.tags.union(choice.tags)
            )
            outcome.advisor_memories.append(memory)
        
        # Generate outcome text
        outcome.outcome_text = self._generate_outcome_text(event, choice)
        
        return outcome
    
    def _event_type_to_memory_type(self, event_type: EventType) -> MemoryType:
        """Convert event type to memory type."""
        mapping = {
            EventType.CRISIS: MemoryType.CRISIS,
            EventType.DECISION: MemoryType.DECISION,
            EventType.INTERNAL_CONFLICT: MemoryType.CONSPIRACY,
            EventType.DIPLOMATIC_EVENT: MemoryType.RELATIONSHIP,
            EventType.MILITARY_EVENT: MemoryType.DECISION,
        }
        return mapping.get(event_type, MemoryType.DECISION)
    
    def _calculate_emotional_impact(self, event: PoliticalEvent, choice: EventChoice) -> float:
        """Calculate emotional impact of an event resolution."""
        base_impact = {
            EventSeverity.MINOR: 0.2,
            EventSeverity.MODERATE: 0.4,
            EventSeverity.MAJOR: 0.6,
            EventSeverity.CRITICAL: 0.8
        }[event.severity]
        
        # Modify based on choice consequences
        consequence_magnitude = sum(abs(v) for v in choice.consequences.values())
        impact_modifier = min(1.0, consequence_magnitude / 2.0)
        
        return min(1.0, base_impact * impact_modifier)
    
    def _generate_outcome_text(self, event: PoliticalEvent, choice: EventChoice) -> str:
        """Generate descriptive text for the event outcome."""
        return f"Your response to '{event.title}' by choosing '{choice.title}' has been implemented."
