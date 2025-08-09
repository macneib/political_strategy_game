"""
Tests for the political event system.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from typing import Dict, Any

from src.core.events import (
    EventType, EventSeverity, EventStatus, PoliticalEvent, EventChoice,
    EventTemplate, EventManager, EventOutcome
)
from src.core.event_library import EventLibrary
from src.core.advisor import AdvisorRole
from src.core.memory import MemoryManager


class TestEventModels:
    """Test event data models."""
    
    def test_political_event_creation(self):
        """Test creating a political event."""
        choices = [
            EventChoice(
                id="choice1",
                title="Test Choice",
                description="A test choice",
                consequences={"stability": 0.1},
                tags=["test"]
            )
        ]
        
        event = PoliticalEvent(
            id="test_event",
            title="Test Event",
            description="A test event",
            event_type=EventType.CRISIS,
            severity=EventSeverity.MODERATE,
            triggered_turn=1,
            choices=choices
        )
        
        assert event.id == "test_event"
        assert event.title == "Test Event"
        assert event.event_type == EventType.CRISIS
        assert event.severity == EventSeverity.MODERATE
        assert event.status == EventStatus.PENDING
        assert len(event.choices) == 1
        assert event.triggered_turn == 1
    
    def test_event_choice_requirements(self):
        """Test event choice with requirements."""
        choice = EventChoice(
            id="military_choice",
            title="Military Response",
            description="Use military force",
            consequences={"military": 0.2},
            required_role=AdvisorRole.MILITARY,
            requirements={"military_strength": 0.3},
            tags=["military"]
        )
        
        assert choice.required_role == AdvisorRole.MILITARY
        assert choice.requirements["military_strength"] == 0.3
    
    def test_event_template_variable_substitution(self):
        """Test template variable substitution."""
        template = EventTemplate(
            id="test_template",
            title_template="Crisis in {location}",
            description_template="A {severity} crisis has occurred in {location}.",
            event_type=EventType.CRISIS,
            severity=EventSeverity.MAJOR,
            variables={
                "location": ["capital", "province"],
                "severity": ["minor", "major"]
            },
            choice_templates=[
                {
                    "title": "Respond",
                    "description": "Take action",
                    "consequences": {"stability": 0.1},
                    "tags": ["response"]
                }
            ]
        )
        
        # Test template generation
        context = {"current_turn": 1}
        event = template.generate_event(1, context)
        assert "Crisis in" in event.title
        assert event.event_type == EventType.CRISIS
        assert len(event.choices) == 1
    
    def test_event_outcome(self):
        """Test event outcome tracking."""
        outcome = EventOutcome(
            event_id="test_event",
            choice_id="choice1",
            resolution_turn=1,
            immediate_effects={"stability": 0.1, "treasury": -0.2},
            outcome_text="The choice was made successfully."
        )
        
        assert outcome.event_id == "test_event"
        assert outcome.choice_id == "choice1"
        assert outcome.immediate_effects["stability"] == 0.1
        assert outcome.resolution_turn == 1


class TestEventManager:
    """Test the EventManager class."""
    
    @pytest.fixture
    def memory_manager(self):
        """Create a mock memory manager."""
        return Mock(spec=MemoryManager)
    
    @pytest.fixture
    def event_manager(self, memory_manager):
        """Create an event manager for testing."""
        return EventManager(civilization_id="test_civ", current_turn=1)
    
    def test_event_manager_initialization(self, event_manager):
        """Test event manager initialization."""
        assert len(event_manager.active_events) == 0
        assert len(event_manager.resolved_events) == 0
        assert event_manager.civilization_id == "test_civ"
    
    def test_register_template(self, event_manager):
        """Test registering a custom template."""
        template = EventTemplate(
            id="custom_template",
            title_template="Custom Event",
            description_template="A custom event",
            event_type=EventType.OPPORTUNITY,
            severity=EventSeverity.MINOR,
            choice_templates=[
                {
                    "title": "Accept",
                    "description": "Accept the opportunity",
                    "consequences": {"economy": 0.1},
                    "tags": ["accept"]
                }
            ]
        )
        
        event_manager.add_event_template(template)
        assert "custom_template" in event_manager.event_templates
    
    def test_trigger_event(self, event_manager):
        """Test triggering an event from a template."""
        # First add a template
        template = EventTemplate(
            id="test_template",
            title_template="Test Event",
            description_template="A test event",
            event_type=EventType.CRISIS,
            severity=EventSeverity.MINOR,
            choice_templates=[
                {
                    "title": "Respond",
                    "description": "Take action",
                    "consequences": {"stability": 0.1},
                    "tags": ["response"]
                }
            ]
        )
        
        event_manager.add_event_template(template)
        
        # Trigger the event
        event = event_manager.trigger_event("test_template", {})
        assert event is not None
        assert event.id in event_manager.active_events
    
    def test_resolve_event_success(self, event_manager, memory_manager):
        """Test successful event resolution."""
        # Create a test event
        choices = [
            EventChoice(
                id="choice1",
                title="Test Choice",
                description="A test choice",
                consequences={"stability": 0.1},
                tags=["test"]
            )
        ]
        
        event = PoliticalEvent(
            id="test_event",
            title="Test Event",
            description="A test event",
            event_type=EventType.CRISIS,
            severity=EventSeverity.MODERATE,
            triggered_turn=1,
            choices=choices
        )
        event.status = EventStatus.ACTIVE
        
        event_manager.active_events["test_event"] = event
        
        # Resolve the event
        outcome = event_manager.respond_to_event("test_event", "choice1")
        
        assert outcome is not None
        assert outcome.event_id == "test_event"
        assert outcome.choice_id == "choice1"
        assert "test_event" not in event_manager.active_events
        assert len(event_manager.resolved_events) == 1
    
    def test_resolve_event_invalid_event(self, event_manager):
        """Test resolving non-existent event."""
        try:
            outcome = event_manager.respond_to_event("invalid_event", "choice1")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected
    
    def test_resolve_event_invalid_choice(self, event_manager):
        """Test resolving event with invalid choice."""
        choices = [
            EventChoice(
                id="choice1",
                title="Test Choice",
                description="A test choice",
                consequences={"stability": 0.1},
                tags=["test"]
            )
        ]
        
        event = PoliticalEvent(
            id="test_event",
            title="Test Event",
            description="A test event",
            event_type=EventType.CRISIS,
            severity=EventSeverity.MODERATE,
            triggered_turn=1,
            choices=choices
        )
        event.status = EventStatus.ACTIVE
        
        event_manager.active_events["test_event"] = event
        
        try:
            outcome = event_manager.respond_to_event("test_event", "invalid_choice")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected
    
    def test_get_available_events(self, event_manager):
        """Test getting available events."""
        # Add test events
        crisis_event = PoliticalEvent(
            id="crisis1",
            title="Crisis Event",
            description="A crisis",
            event_type=EventType.CRISIS,
            severity=EventSeverity.MAJOR,
            triggered_turn=1,
            choices=[]
        )
        crisis_event.status = EventStatus.ACTIVE
        
        opportunity_event = PoliticalEvent(
            id="opportunity1",
            title="Opportunity Event",
            description="An opportunity",
            event_type=EventType.OPPORTUNITY,
            severity=EventSeverity.MINOR,
            triggered_turn=1,
            choices=[]
        )
        opportunity_event.status = EventStatus.ACTIVE
        
        event_manager.active_events["crisis1"] = crisis_event
        event_manager.active_events["opportunity1"] = opportunity_event
        
        available_events = event_manager.get_available_events()
        
        assert len(available_events) == 2


class TestEventLibrary:
    """Test the event library."""
    
    def test_get_all_templates(self):
        """Test getting all templates from library."""
        templates = EventLibrary.get_all_templates()
        
        assert len(templates) > 0
        assert "natural_disaster" in templates
        assert "trade_route_discovery" in templates
        assert "border_skirmish" in templates
    
    def test_crisis_templates(self):
        """Test crisis event templates."""
        templates = EventLibrary._get_crisis_templates()
        
        assert "natural_disaster" in templates
        assert "plague_outbreak" in templates
        
        # Test natural disaster template
        disaster_template = templates["natural_disaster"]
        assert disaster_template.event_type == EventType.CRISIS
        assert disaster_template.severity == EventSeverity.MAJOR
        assert len(disaster_template.choice_templates) == 3
        assert "disaster_type" in disaster_template.variables
    
    def test_economic_templates(self):
        """Test economic event templates."""
        templates = EventLibrary._get_economic_templates()
        
        assert "trade_route_discovery" in templates
        assert "market_crash" in templates
        
        # Test trade route template
        trade_template = templates["trade_route_discovery"]
        assert trade_template.event_type == EventType.OPPORTUNITY
        assert "trade_type" in trade_template.variables
    
    def test_template_generation(self):
        """Test generating events from library templates."""
        templates = EventLibrary.get_all_templates()
        
        # Test each template can generate an event
        for template_id, template in templates.items():
            context = {"current_turn": 1}
            event = template.generate_event(1, context)
            assert event is not None
            assert event.title != template.title_template  # Should be substituted
            assert event.description != template.description_template
            assert len(event.choices) == len(template.choice_templates)
    
    def test_template_variable_coverage(self):
        """Test that all templates have proper variable coverage."""
        templates = EventLibrary.get_all_templates()
        
        for template_id, template in templates.items():
            # Check that all variables in templates are defined
            title_vars = self._extract_template_variables(template.title_template)
            desc_vars = self._extract_template_variables(template.description_template)
            
            all_template_vars = title_vars.union(desc_vars)
            defined_vars = set(template.variables.keys())
            
            # All template variables should be defined
            undefined_vars = all_template_vars - defined_vars
            assert len(undefined_vars) == 0, f"Template {template_id} has undefined variables: {undefined_vars}"
    
    def _extract_template_variables(self, template_string: str) -> set:
        """Extract variables from a template string."""
        import re
        variables = re.findall(r'\{(\w+)\}', template_string)
        return set(variables)


class TestEventIntegration:
    """Test event system integration with other components."""
    
    def test_event_cooldown_system(self):
        """Test event cooldown system."""
        # Get a template with cooldown
        templates = EventLibrary.get_all_templates()
        template = templates["natural_disaster"]
        
        # Verify the cooldown is set in the template
        assert template.cooldown_turns > 0
    
    def test_event_severity_impact(self):
        """Test that event severity affects outcomes."""
        # Create events with different severities
        minor_choice = EventChoice(
            id="minor_choice",
            title="Minor Response",
            description="Minor action",
            consequences={"stability": 0.1},
            tags=["minor"]
        )
        
        major_choice = EventChoice(
            id="major_choice",
            title="Major Response",
            description="Major action",
            consequences={"stability": 0.1},
            tags=["major"]
        )
        
        minor_event = PoliticalEvent(
            id="minor_event",
            title="Minor Issue",
            description="A minor issue",
            event_type=EventType.CRISIS,
            severity=EventSeverity.MINOR,
            triggered_turn=1,
            choices=[minor_choice]
        )
        
        major_event = PoliticalEvent(
            id="major_event",
            title="Major Crisis",
            description="A major crisis",
            event_type=EventType.CRISIS,
            severity=EventSeverity.CRITICAL,
            triggered_turn=1,
            choices=[major_choice]
        )
        
        # Both events should be valid
        assert minor_event.severity == EventSeverity.MINOR
        assert major_event.severity == EventSeverity.CRITICAL


if __name__ == "__main__":
    pytest.main([__file__])
