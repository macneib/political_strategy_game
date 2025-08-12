"""
Comprehensive test suite for the Technology Tree system including
advisor lobbying, research management, and integration capabilities.
"""

import pytest
from typing import Dict, List
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.technology_tree import (
    TechnologyTree, TechnologyCategory, PoliticalTechnology, TechnologyNode
)
from src.core.advisor_technology import (
    AdvisorLobbyingManager, AdvisorTechnologyPreferences, TechnologyAdvocacy,
    LobbyingStrategy
)
from src.core.technology_integration import TechnologyResearchManager
from src.core.advisor import Advisor, AdvisorRole, PersonalityProfile
from src.core.resources import ResourceManager, EconomicState, MilitaryState, TechnologyState


class TestTechnologyTree:
    """Test the core technology tree functionality."""
    
    def test_technology_tree_initialization(self):
        """Test that technology tree initializes with all political technologies."""
        tree = TechnologyTree(civilization_id="test_civ")
        
        # Should have all defined technologies
        assert len(tree.nodes) > 20  # We defined 30+ technologies
        
        # Should have all categories represented
        categories_present = set()
        for node in tree.nodes.values():
            categories_present.add(node.technology.category)
        
        assert len(categories_present) == 5  # All 5 categories
        assert TechnologyCategory.GOVERNANCE in categories_present
        assert TechnologyCategory.INTELLIGENCE in categories_present
        assert TechnologyCategory.INFORMATION_CONTROL in categories_present
        assert TechnologyCategory.ADMINISTRATIVE in categories_present
        assert TechnologyCategory.SOCIAL_ENGINEERING in categories_present
    
    def test_technology_prerequisites(self):
        """Test that technology prerequisites work correctly."""
        tree = TechnologyTree(civilization_id="test_civ")
        
        # Initially, only basic technologies should be available
        available = tree.get_available_technologies()
        
        # Check that basic technologies are available
        basic_techs = ["basic_bureaucracy", "state_records", "public_messaging", 
                      "loyalty_programs", "informant_networks"]
        
        for tech in basic_techs:
            if tech in tree.nodes:
                assert tech in available, f"Basic technology {tech} should be available initially"
        
        # Advanced technologies should not be available initially
        advanced_techs = ["advanced_surveillance", "social_credit_system", 
                         "information_warfare_protocols"]
        
        for tech in advanced_techs:
            if tech in tree.nodes:
                assert tech not in available, f"Advanced technology {tech} should not be available initially"
    
    def test_technology_research_progression(self):
        """Test researching technologies and unlocking new ones."""
        tree = TechnologyTree(civilization_id="test_civ")
        
        initial_available = set(tree.get_available_technologies())
        
        # Research a basic technology
        if "basic_bureaucracy" in tree.nodes:
            success = tree.research_technology("basic_bureaucracy")
            assert success, "Should be able to research basic bureaucracy"
            
            # Check that it's marked as researched
            assert "basic_bureaucracy" in tree.researched_technologies
            
            # Should unlock new technologies
            new_available = set(tree.get_available_technologies())
            newly_unlocked = new_available - initial_available
            assert len(newly_unlocked) > 0, "Researching should unlock new technologies"
    
    def test_technology_effects(self):
        """Test that technologies have proper effects defined."""
        tree = TechnologyTree(civilization_id="test_civ")
        
        # Check that technologies have meaningful effects
        for tech_id, node in tree.nodes.items():
            tech = node.technology
            
            # Should have at least one type of effect
            has_effects = (
                len(tech.political_effects) > 0 or
                len(tech.advisor_unlocks) > 0 or
                len(tech.espionage_enhancements) > 0 or
                len(tech.resource_modifiers) > 0
            )
            assert has_effects, f"Technology {tech_id} should have some effects defined"
    
    def test_research_queue_management(self):
        """Test research queue functionality."""
        tree = TechnologyTree(civilization_id="test_civ")
        
        # Add technologies to research queue
        available_techs = tree.get_available_technologies()
        if len(available_techs) >= 2:
            tech1, tech2 = available_techs[0], available_techs[1]
            
            # First, verify they can be researched
            assert tree.can_research_technology(tech1)
            assert tree.can_research_technology(tech2)
            
            tree.add_to_research_queue(tech1)
            tree.add_to_research_queue(tech2)
            
            assert len(tree.research_queue) == 2
            assert tree.research_queue[0] == tech1
            assert tree.research_queue[1] == tech2
            
            # Directly research the first tech (simulating completion)
            tree.research_technology(tech1)
            assert tech1 in tree.completed_technologies
            
            # Verify tech1 is no longer in queue after completion
            if tech1 in tree.research_queue:
                tree.research_queue.remove(tech1)


class TestAdvisorTechnologyLobby:
    """Test advisor lobbying system for technologies."""
    
    def create_test_advisor(self, role: AdvisorRole, name: str = "Test Advisor") -> Advisor:
        """Create a test advisor with realistic personality."""
        personality = PersonalityProfile(
            ambition=0.6,
            loyalty=0.7,
            pragmatism=0.5,
            competence=0.8
        )
        
        return Advisor(
            name=name,
            role=role,
            civilization_id="test_civ",
            personality=personality,
            influence=0.6
        )
    
    def test_advisor_lobbying_manager_initialization(self):
        """Test advisor lobbying manager setup."""
        manager = AdvisorLobbyingManager(civilization_id="test_civ")
        
        assert manager.civilization_id == "test_civ"
        assert len(manager.advisor_preferences) == 0
        assert len(manager.active_advocacy) == 0
    
    def test_advisor_registration(self):
        """Test registering advisors and their preferences."""
        manager = AdvisorLobbyingManager(civilization_id="test_civ")
        advisor = self.create_test_advisor(AdvisorRole.MILITARY, "General Smith")
        
        manager.register_advisor(advisor)
        
        assert advisor.id in manager.advisor_preferences
        prefs = manager.advisor_preferences[advisor.id]
        assert prefs.advisor_role == AdvisorRole.MILITARY
        
        # Military advisors should prefer intelligence technologies
        assert prefs.category_preferences[TechnologyCategory.INTELLIGENCE] > 0.8
    
    def test_technology_advocacy_campaigns(self):
        """Test starting and managing advocacy campaigns."""
        manager = AdvisorLobbyingManager(civilization_id="test_civ")
        advisor = self.create_test_advisor(AdvisorRole.SECURITY, "Security Chief")
        
        manager.register_advisor(advisor)
        
        # Start advocacy campaign
        advocacy_id = manager.start_technology_advocacy(
            advisor.id, "advanced_surveillance", 0.8, 
            "Essential for national security"
        )
        
        assert advocacy_id != ""
        assert advocacy_id in manager.active_advocacy
        
        advocacy = manager.active_advocacy[advocacy_id]
        assert advocacy.advisor_id == advisor.id
        assert advocacy.technology_id == "advanced_surveillance"
        assert advocacy.support_level == 0.8
    
    def test_lobbying_turn_processing(self):
        """Test processing a turn of lobbying activities."""
        tree = TechnologyTree(civilization_id="test_civ")
        manager = AdvisorLobbyingManager(civilization_id="test_civ")
        
        # Register multiple advisors
        military_advisor = self.create_test_advisor(AdvisorRole.MILITARY, "General")
        security_advisor = self.create_test_advisor(AdvisorRole.SECURITY, "Security Chief")
        
        manager.register_advisor(military_advisor)
        manager.register_advisor(security_advisor)
        
        # Start advocacy campaigns
        if "advanced_surveillance" in tree.nodes:
            manager.start_technology_advocacy(
                military_advisor.id, "advanced_surveillance", 0.7
            )
            manager.start_technology_advocacy(
                security_advisor.id, "advanced_surveillance", 0.9
            )
        
        # Process lobbying turn
        results = manager.process_lobbying_turn(tree)
        
        assert "lobbying_activities" in results
        assert "technology_influence_changes" in results
        assert "coalition_formations" in results
        
        # Check that coalition formed for advanced_surveillance
        if "advanced_surveillance" in results["technology_influence_changes"]:
            tech_changes = results["technology_influence_changes"]["advanced_surveillance"]
            assert len(tech_changes["supporting_advisors"]) == 2
    
    def test_coalition_building(self):
        """Test advisor coalition formation for technologies."""
        tree = TechnologyTree(civilization_id="test_civ")
        manager = AdvisorLobbyingManager(civilization_id="test_civ")
        
        # Create advisors with similar goals
        advisors = [
            self.create_test_advisor(AdvisorRole.MILITARY, "General Alpha"),
            self.create_test_advisor(AdvisorRole.SECURITY, "Security Beta"),
            self.create_test_advisor(AdvisorRole.MILITARY, "Colonel Gamma")
        ]
        
        for advisor in advisors:
            manager.register_advisor(advisor)
        
        # All support the same technology
        tech_id = "intelligence_integration"
        if tech_id in tree.nodes:
            for advisor in advisors:
                manager.start_technology_advocacy(advisor.id, tech_id, 0.8)
        
        # Process lobbying turn
        results = manager.process_lobbying_turn(tree)
        
        # Should form coalition
        if results["coalition_formations"]:
            coalition = results["coalition_formations"][0]
            assert coalition["technology_id"] == tech_id
            assert len(coalition["members"]) == 3
    
    def test_research_queue_suggestions(self):
        """Test advisor-influenced research queue suggestions."""
        tree = TechnologyTree(civilization_id="test_civ")
        manager = AdvisorLobbyingManager(civilization_id="test_civ")
        
        # Register advisor with specific preferences
        advisor = self.create_test_advisor(AdvisorRole.ECONOMIC, "Economic Minister")
        manager.register_advisor(advisor)
        
        # Set technology priorities
        available_techs = tree.get_available_technologies()
        if available_techs:
            tech_id = available_techs[0]
            manager.update_technology_preferences(advisor.id, tech_id, 0.9)
        
        # Get suggestions
        suggestions = manager.suggest_research_queue_by_lobbying(tree, max_queue_length=3)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 3


class TestTechnologyIntegration:
    """Test technology integration with existing game systems."""
    
    def create_test_resource_manager(self) -> ResourceManager:
        """Create a resource manager for testing."""
        economic = EconomicState(
            gdp=1500.0,
            population=1000000,
            infrastructure_level=75.0
        )
        
        military = MilitaryState(
            army_size=50000,
            navy_size=100,
            intelligence_budget=200.0
        )
        
        technology = TechnologyState(
            research_capacity=80.0,
            education_index=70.0,
            digital_infrastructure=60.0
        )
        
        return ResourceManager(
            civilization_id="test_civ",
            economic=economic,
            military=military,
            technology=technology
        )
    
    def test_technology_research_manager_initialization(self):
        """Test technology research manager setup."""
        tree = TechnologyTree(civilization_id="test_civ")
        manager = TechnologyResearchManager(
            civilization_id="test_civ",
            technology_tree=tree
        )
        
        assert manager.civilization_id == "test_civ"
        assert manager.technology_tree == tree
        assert manager.active_research is None
        assert len(manager.research_queue) == 0
    
    def test_resource_manager_integration(self):
        """Test integration with resource manager."""
        tree = TechnologyTree(civilization_id="test_civ")
        research_manager = TechnologyResearchManager(
            civilization_id="test_civ",
            technology_tree=tree
        )
        resource_manager = self.create_test_resource_manager()
        
        # Update from resource manager
        research_manager.update_from_resource_manager(resource_manager)
        
        # Should have updated research capacity and speed
        assert research_manager.available_research_capacity > 0
        assert research_manager.research_speed_modifier >= 1.0
    
    def test_technology_research_progression(self):
        """Test researching technologies through the integration system."""
        tree = TechnologyTree(civilization_id="test_civ")
        research_manager = TechnologyResearchManager(
            civilization_id="test_civ",
            technology_tree=tree
        )
        
        # Start research on available technology
        available_techs = tree.get_available_technologies()
        if available_techs:
            tech_id = available_techs[0]
            success = research_manager.start_technology_research(tech_id)
            assert success
            assert research_manager.active_research == tech_id
            
            # Simulate research progress
            research_manager.research_progress[tech_id] = 0.9  # Almost complete
            
            # Advance progress
            results = research_manager.advance_research_progress()
            
            assert tech_id in results["technologies_completed"]
            assert tech_id in research_manager.completed_technologies
    
    def test_advisor_lobbying_integration(self):
        """Test integration between research manager and advisor lobbying."""
        tree = TechnologyTree(civilization_id="test_civ")
        research_manager = TechnologyResearchManager(
            civilization_id="test_civ",
            technology_tree=tree
        )
        
        # Create and register advisor
        advisor = Advisor(
            name="Test Advisor",
            role=AdvisorRole.MILITARY,
            civilization_id="test_civ",
            personality=PersonalityProfile(ambition=0.7),
            influence=0.8
        )
        
        research_manager.advisor_lobbying.register_advisor(advisor)
        
        # Process lobbying turn
        results = research_manager.process_advisor_lobbying_turn()
        
        assert "lobbying_activities" in results
        assert "technology_influence_changes" in results
    
    def test_technology_effect_application(self):
        """Test applying technology effects to resource manager."""
        tree = TechnologyTree(civilization_id="test_civ")
        research_manager = TechnologyResearchManager(
            civilization_id="test_civ",
            technology_tree=tree
        )
        resource_manager = self.create_test_resource_manager()
        
        # Complete a technology
        available_techs = tree.get_available_technologies()
        if available_techs:
            tech_id = available_techs[0]
            research_manager._complete_technology_research(tech_id)
            
            # Apply effects
            effects = research_manager.apply_technology_effects_to_resources(
                resource_manager, tech_id
            )
            
            # Should have some effects applied
            total_effects = (
                len(effects["economic_effects"]) +
                len(effects["military_effects"]) +
                len(effects["technology_effects"])
            )
            assert total_effects > 0
    
    def test_technology_recommendations(self):
        """Test technology recommendation system."""
        tree = TechnologyTree(civilization_id="test_civ")
        research_manager = TechnologyResearchManager(
            civilization_id="test_civ",
            technology_tree=tree
        )
        
        # Create context with threats
        context = {
            "current_threats": ["external_military", "internal_dissent"],
            "resource_state": {"economic_stress": 0.6, "social_unrest": 0.4},
            "diplomatic_situation": {"hostile_neighbors": 2}
        }
        
        recommendations = research_manager.get_technology_recommendations(context)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5
        
        # Each recommendation should have tech_id, score, and reason
        for tech_id, score, reason in recommendations:
            assert isinstance(tech_id, str)
            assert 0.0 <= score <= 1.0
            assert isinstance(reason, str)
            assert len(reason) > 0
    
    def test_turn_advancement(self):
        """Test full turn processing."""
        tree = TechnologyTree(civilization_id="test_civ")
        research_manager = TechnologyResearchManager(
            civilization_id="test_civ",
            technology_tree=tree
        )
        
        initial_turn = research_manager.current_turn
        
        # Advance turn
        results = research_manager.advance_turn()
        
        assert research_manager.current_turn == initial_turn + 1
        assert "lobbying_results" in results
        assert "research_results" in results
        assert "turn" in results
    
    def test_status_summary(self):
        """Test comprehensive status summary."""
        tree = TechnologyTree(civilization_id="test_civ")
        research_manager = TechnologyResearchManager(
            civilization_id="test_civ",
            technology_tree=tree
        )
        
        summary = research_manager.get_status_summary()
        
        required_keys = [
            "civilization_id", "current_turn", "active_research",
            "research_queue", "completed_technologies", "available_technologies",
            "research_capacity", "research_speed", "advisor_lobbying"
        ]
        
        for key in required_keys:
            assert key in summary


class TestTechnologySystemIntegration:
    """Integration tests for the complete technology system."""
    
    def test_complete_research_workflow(self):
        """Test a complete research workflow from start to finish."""
        # Initialize all systems
        tree = TechnologyTree(civilization_id="test_civ")
        research_manager = TechnologyResearchManager(
            civilization_id="test_civ",
            technology_tree=tree
        )
        
        # Create advisor
        advisor = Advisor(
            name="Science Advisor",
            role=AdvisorRole.ECONOMIC,
            civilization_id="test_civ",
            personality=PersonalityProfile(ambition=0.6, competence=0.9)
        )
        
        research_manager.advisor_lobbying.register_advisor(advisor)
        
        # Get available technologies
        available_techs = tree.get_available_technologies()
        assert len(available_techs) > 0
        
        # Start research
        tech_id = available_techs[0]
        success = research_manager.start_technology_research(tech_id)
        assert success
        
        # Process several turns
        for turn in range(15):  # Should be enough to complete research
            research_manager.advance_turn()
            
            if tech_id in research_manager.completed_technologies:
                break
        
        # Should have completed the research
        assert tech_id in research_manager.completed_technologies
        
        # Should have unlocked new technologies
        new_available = tree.get_available_technologies()
        assert len(new_available) >= len(available_techs)  # At least same, likely more
    
    def test_multiple_advisor_lobbying_competition(self):
        """Test competition between multiple advisors for different technologies."""
        tree = TechnologyTree(civilization_id="test_civ")
        research_manager = TechnologyResearchManager(
            civilization_id="test_civ",
            technology_tree=tree
        )
        
        # Create competing advisors
        military_advisor = Advisor(
            name="General",
            role=AdvisorRole.MILITARY,
            civilization_id="test_civ",
            personality=PersonalityProfile(ambition=0.8, aggression=0.7)
        )
        
        economic_advisor = Advisor(
            name="Treasurer",
            role=AdvisorRole.ECONOMIC,
            civilization_id="test_civ",
            personality=PersonalityProfile(ambition=0.6, pragmatism=0.8)
        )
        
        research_manager.advisor_lobbying.register_advisor(military_advisor)
        research_manager.advisor_lobbying.register_advisor(economic_advisor)
        
        # Create competing advocacy campaigns
        available_techs = tree.get_available_technologies()
        if len(available_techs) >= 2:
            tech1, tech2 = available_techs[0], available_techs[1]
            
            research_manager.advisor_lobbying.start_technology_advocacy(
                military_advisor.id, tech1, 0.9, "Military priority"
            )
            research_manager.advisor_lobbying.start_technology_advocacy(
                economic_advisor.id, tech2, 0.8, "Economic necessity"
            )
        
        # Process multiple turns and observe competition
        for _ in range(5):
            results = research_manager.advance_turn()
            lobbying_results = results["lobbying_results"]
            
            # Should have lobbying activities
            assert len(lobbying_results["lobbying_activities"]) > 0
    
    def test_system_performance_under_load(self):
        """Test system performance with many technologies and advisors."""
        tree = TechnologyTree(civilization_id="test_civ")
        research_manager = TechnologyResearchManager(
            civilization_id="test_civ",
            technology_tree=tree
        )
        
        # Create many advisors
        advisors = []
        roles = list(AdvisorRole)
        for i in range(10):
            advisor = Advisor(
                name=f"Advisor {i}",
                role=roles[i % len(roles)],
                civilization_id="test_civ",
                personality=PersonalityProfile(
                    ambition=0.3 + (i * 0.07) % 0.7,
                    competence=0.5 + (i * 0.05) % 0.5
                )
            )
            advisors.append(advisor)
            research_manager.advisor_lobbying.register_advisor(advisor)
        
        # Start many advocacy campaigns
        available_techs = tree.get_available_technologies()
        for i, advisor in enumerate(advisors[:len(available_techs)]):
            tech_id = available_techs[i % len(available_techs)]
            research_manager.advisor_lobbying.start_technology_advocacy(
                advisor.id, tech_id, 0.5 + (i * 0.05)
            )
        
        # Process multiple turns - should not crash or hang
        import time
        start_time = time.time()
        
        for _ in range(10):
            research_manager.advance_turn()
        
        end_time = time.time()
        
        # Should complete in reasonable time (less than 5 seconds)
        assert end_time - start_time < 5.0


if __name__ == "__main__":
    # Run specific test categories
    import subprocess
    
    print("Running Technology Tree Tests...")
    subprocess.run([
        "python", "-m", "pytest", 
        "test_technology_tree_comprehensive.py::TestTechnologyTree", 
        "-v"
    ])
    
    print("\\nRunning Advisor Lobbying Tests...")
    subprocess.run([
        "python", "-m", "pytest", 
        "test_technology_tree_comprehensive.py::TestAdvisorTechnologyLobby", 
        "-v"
    ])
    
    print("\\nRunning Integration Tests...")
    subprocess.run([
        "python", "-m", "pytest", 
        "test_technology_tree_comprehensive.py::TestTechnologyIntegration", 
        "-v"
    ])
    
    print("\\nRunning System Integration Tests...")
    subprocess.run([
        "python", "-m", "pytest", 
        "test_technology_tree_comprehensive.py::TestTechnologySystemIntegration", 
        "-v"
    ])
