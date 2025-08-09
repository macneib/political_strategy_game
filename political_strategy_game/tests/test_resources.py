"""
Tests for the resource management system.
"""

import pytest
import tempfile
from pathlib import Path

from src.core.resources import (
    ResourceManager, ResourceEvent, ResourceType,
    EconomicState, MilitaryState, TechnologyState
)
from src.core.civilization import Civilization
from src.core.leader import Leader, LeadershipStyle
from src.core.advisor import AdvisorRole, PersonalityProfile
from src.core.advisor_enhanced import AdvisorWithMemory


class TestResourceStates:
    """Test resource state models."""
    
    def test_economic_state_creation(self):
        """Test basic economic state creation."""
        economic = EconomicState()
        assert economic.treasury == 1000.0
        assert economic.income_per_turn == 100.0
        assert economic.expenses_per_turn == 80.0
        assert economic.economic_stability == 0.7
        assert len(economic.trade_routes) == 0
    
    def test_economic_state_custom_values(self):
        """Test economic state with custom values."""
        economic = EconomicState(
            treasury=5000.0,
            income_per_turn=200.0,
            unemployment_rate=0.1,
            inflation_rate=0.05
        )
        assert economic.treasury == 5000.0
        assert economic.income_per_turn == 200.0
        assert economic.unemployment_rate == 0.1
        assert economic.inflation_rate == 0.05
    
    def test_military_state_creation(self):
        """Test basic military state creation."""
        military = MilitaryState()
        assert military.army_size == 1000
        assert military.navy_size == 50
        assert military.military_strength == 0.6
        assert military.morale == 0.7
        assert len(military.active_conflicts) == 0
    
    def test_technology_state_creation(self):
        """Test basic technology state creation."""
        tech = TechnologyState()
        assert tech.research_points_per_turn == 10.0
        assert tech.military_tech_level == 0.3
        assert tech.economic_tech_level == 0.3
        assert tech.political_tech_level == 0.2
        assert len(tech.completed_techs) == 0


class TestResourceManager:
    """Test resource manager functionality."""
    
    @pytest.fixture
    def resource_manager(self):
        """Create a test resource manager."""
        return ResourceManager(civilization_id="test_civ")
    
    def test_resource_manager_creation(self, resource_manager):
        """Test basic resource manager creation."""
        assert resource_manager.civilization_id == "test_civ"
        assert resource_manager.current_turn == 1
        assert resource_manager.economic_state.treasury == 1000.0
        assert resource_manager.military_state.army_size == 1000
        assert resource_manager.technology_state.research_points_per_turn == 10.0
    
    def test_economic_update(self, resource_manager):
        """Test economic state updates."""
        initial_treasury = resource_manager.economic_state.treasury
        changes = resource_manager._update_economy()
        
        # Should have positive net income by default
        expected_income = (resource_manager.economic_state.income_per_turn - 
                         resource_manager.economic_state.expenses_per_turn)
        assert changes["treasury_change"] == expected_income
        assert resource_manager.economic_state.treasury == initial_treasury + expected_income
    
    def test_military_update(self, resource_manager):
        """Test military state updates."""
        # Set adequate budget for recruitment
        resource_manager.military_state.military_budget = 1000.0
        
        initial_army = resource_manager.military_state.army_size
        changes = resource_manager._update_military()
        
        # Should have some army growth with adequate budget
        assert "army_growth" in changes
        assert resource_manager.military_state.army_size >= initial_army
    
    def test_technology_update(self, resource_manager):
        """Test technology research updates."""
        # Set current research
        resource_manager.technology_state.current_research = "agriculture"
        
        initial_research = resource_manager.technology_state.accumulated_research
        changes = resource_manager._update_technology()
        
        assert changes["research_progress"] == 10.0  # Default research per turn
        assert resource_manager.technology_state.accumulated_research == initial_research + 10.0
    
    def test_technology_completion(self, resource_manager):
        """Test technology research completion."""
        # Set up technology research
        resource_manager.technology_state.current_research = "agriculture"
        resource_manager.technology_state.accumulated_research = 45.0  # Close to completion
        
        changes = resource_manager._update_technology()
        
        # Should complete agriculture research (cost 50)
        assert "agriculture" in resource_manager.technology_state.completed_techs
        assert resource_manager.technology_state.current_research is None
        assert "completed_research" in changes
    
    def test_resource_event_creation(self, resource_manager):
        """Test resource event creation."""
        # Force economic crisis conditions
        resource_manager.economic_state.treasury = 50.0
        resource_manager.economic_state.economic_stability = 0.2
        
        new_events = resource_manager._check_for_new_events()
        
        # Should create economic crisis event
        assert len(new_events) > 0
        crisis_event = new_events[0]
        assert crisis_event.resource_type == ResourceType.ECONOMIC
        assert crisis_event.event_name == "Economic Crisis"
        assert crisis_event.severity == 0.8
    
    def test_military_unrest_event(self, resource_manager):
        """Test military unrest event creation."""
        # Force military unrest conditions
        resource_manager.military_state.morale = 0.2
        resource_manager.military_state.military_budget = 30.0
        
        new_events = resource_manager._check_for_new_events()
        
        # Should create military unrest event
        military_events = [e for e in new_events if e.resource_type == ResourceType.MILITARY]
        assert len(military_events) > 0
        unrest_event = military_events[0]
        assert unrest_event.event_name == "Military Unrest"
    
    def test_full_resource_update(self, resource_manager):
        """Test full resource update cycle."""
        results = resource_manager.update_resources(3)  # 3 turns
        
        assert resource_manager.current_turn == 4  # Started at 1, added 3
        assert "economic_changes" in results
        assert "military_changes" in results
        assert "technology_changes" in results
        assert "events_processed" in results
        assert "new_events" in results
    
    def test_resource_summary(self, resource_manager):
        """Test resource summary generation."""
        summary = resource_manager.get_resource_summary()
        
        assert summary["civilization_id"] == "test_civ"
        assert summary["turn"] == 1
        assert "economic" in summary
        assert "military" in summary
        assert "technology" in summary
        assert "active_events" in summary
        
        # Check economic summary structure
        assert "treasury" in summary["economic"]
        assert "net_income" in summary["economic"]
        assert "stability" in summary["economic"]
        
        # Check military summary structure
        assert "total_forces" in summary["military"]
        assert "strength" in summary["military"]
        assert "morale" in summary["military"]
        
        # Check technology summary structure
        assert "research_rate" in summary["technology"]
        assert "completed_techs" in summary["technology"]
        assert "tech_levels" in summary["technology"]


class TestResourceIntegration:
    """Test resource system integration with civilization."""
    
    @pytest.fixture
    def test_leader(self):
        """Create a test leader."""
        personality = PersonalityProfile(
            aggression=0.5,
            diplomacy=0.6,
            loyalty=0.8,
            ambition=0.5,
            cunning=0.4
        )
        
        return Leader(
            name="Test Emperor",
            civilization_id="test_civ",
            personality=personality,
            leadership_style=LeadershipStyle.AUTHORITARIAN
        )
    
    @pytest.fixture
    def test_civilization(self, test_leader):
        """Create a test civilization with resource management."""
        return Civilization(
            name="Test Empire",
            leader=test_leader
        )
    
    def test_civilization_resource_initialization(self, test_civilization):
        """Test that civilization properly initializes resource management."""
        assert test_civilization.resource_manager is not None
        assert test_civilization.resource_manager.civilization_id == test_civilization.id
        assert test_civilization.resource_manager.current_turn == 1
    
    def test_resource_summary_integration(self, test_civilization):
        """Test resource summary through civilization."""
        summary = test_civilization.get_resource_summary()
        
        assert "economic" in summary
        assert "military" in summary
        assert "technology" in summary
        assert summary["civilization_id"] == test_civilization.id
    
    def test_research_starting(self, test_civilization):
        """Test starting research through civilization."""
        success = test_civilization.start_research("agriculture")
        assert success is True
        
        tech_state = test_civilization.resource_manager.technology_state
        assert tech_state.current_research == "agriculture"
    
    def test_military_budget_allocation(self, test_civilization):
        """Test military budget allocation."""
        initial_treasury = test_civilization.resource_manager.economic_state.treasury
        initial_military_budget = test_civilization.resource_manager.military_state.military_budget
        
        success = test_civilization.allocate_military_budget(200.0)
        assert success is True
        
        # Check treasury decreased
        assert test_civilization.resource_manager.economic_state.treasury == initial_treasury - 200.0
        # Check military budget increased
        assert test_civilization.resource_manager.military_state.military_budget == initial_military_budget + 200.0
    
    def test_trade_route_establishment(self, test_civilization):
        """Test establishing trade routes."""
        initial_trade_income = test_civilization.resource_manager.economic_state.trade_income
        
        success = test_civilization.establish_trade_route("other_civ", 50.0)
        assert success is True
        
        economic_state = test_civilization.resource_manager.economic_state
        assert "other_civ" in economic_state.trade_routes
        assert economic_state.trade_routes["other_civ"] == 50.0
        assert economic_state.trade_income == initial_trade_income + 50.0
    
    def test_resource_events_with_advisors(self, test_civilization):
        """Test resource events creating memories for advisors."""
        # Add advisors
        economic_advisor = AdvisorWithMemory(
            name="Economic Advisor",
            role=AdvisorRole.ECONOMIC,
            civilization_id=test_civilization.id,
            personality=PersonalityProfile(
                aggression=0.3,
                diplomacy=0.7,
                loyalty=0.8,
                ambition=0.5,
                cunning=0.5
            ),
            loyalty=0.8,
            influence=0.7
        )
        
        test_civilization.add_advisor(economic_advisor)
        
        # Force economic crisis
        test_civilization.resource_manager.economic_state.treasury = 50.0
        test_civilization.resource_manager.economic_state.economic_stability = 0.2
        
        # Process turn to trigger events
        results = test_civilization.process_turn()
        
        # Check that resource events were processed
        assert "resource_changes" in results
        assert "new_events" in results["resource_changes"]
        
        # Check that economic crisis event was created
        new_events = results["resource_changes"]["new_events"]
        economic_events = [e for e in new_events if e.resource_type == ResourceType.ECONOMIC]
        assert len(economic_events) > 0
    
    def test_comprehensive_summary(self, test_civilization):
        """Test comprehensive summary including all systems."""
        summary = test_civilization.get_comprehensive_summary()
        
        assert "political" in summary
        assert "resources" in summary
        assert "integration" in summary
        
        # Check integration status
        integration = summary["integration"]
        assert integration["memory_manager_active"] is True
        assert integration["event_manager_active"] is True
        assert integration["resource_manager_active"] is True
        assert "active_resource_events" in integration
    
    def test_resource_turn_processing(self, test_civilization):
        """Test resource processing during turn advancement."""
        initial_turn = test_civilization.current_turn
        initial_treasury = test_civilization.resource_manager.economic_state.treasury
        
        # Process several turns
        for _ in range(3):
            results = test_civilization.process_turn()
            assert "resource_changes" in results
        
        # Check turn advancement
        assert test_civilization.current_turn == initial_turn + 3
        
        # Check resource changes occurred
        final_treasury = test_civilization.resource_manager.economic_state.treasury
        assert final_treasury != initial_treasury  # Should have changed due to income/expenses


class TestResourceEvents:
    """Test resource event system."""
    
    def test_resource_event_creation(self):
        """Test creating resource events."""
        event = ResourceEvent(
            resource_type=ResourceType.ECONOMIC,
            event_name="Market Boom",
            description="Economic markets experience significant growth",
            economic_impact=0.2,
            political_impact=0.1,
            duration_turns=2,
            severity=0.6
        )
        
        assert event.resource_type == ResourceType.ECONOMIC
        assert event.event_name == "Market Boom"
        assert event.economic_impact == 0.2
        assert event.political_impact == 0.1
        assert event.duration_turns == 2
        assert event.turns_remaining == 1  # Default
    
    def test_resource_event_processing(self):
        """Test resource event processing."""
        manager = ResourceManager(civilization_id="test")
        
        # Create and add an event
        event = ResourceEvent(
            resource_type=ResourceType.MILITARY,
            event_name="Military Exercise",
            description="Large-scale military training improves readiness",
            military_impact=0.1,
            duration_turns=1,
            turns_remaining=1
        )
        
        manager.active_events.append(event)
        initial_morale = manager.military_state.morale
        
        # Process the event
        processed = manager._process_resource_events()
        
        assert len(processed) == 1
        assert processed[0].event_name == "Military Exercise"
        assert len(manager.active_events) == 0  # Event completed
        assert manager.military_state.morale > initial_morale  # Morale improved
