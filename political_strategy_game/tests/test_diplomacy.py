"""
Test suite for inter-civilization diplomacy and relations systems.

This module tests all aspects of diplomatic relations, trade networks,
military conflicts, and intelligence operations between civilizations.
"""

import pytest
import tempfile
from pathlib import Path
from typing import Dict, List

from src.core.diplomacy import (
    DiplomacyManager, CivilizationRelations, Treaty, TradeRoute,
    MilitaryConflict, IntelligenceNetwork, DiplomaticEvent,
    DiplomaticStatus, TreatyType, ConflictType, IntelligenceOperation
)
from src.core.civilization import Civilization
from src.core.leader import Leader, LeadershipStyle
from src.core.advisor_enhanced import AdvisorWithMemory, PersonalityProfile
from src.core.advisor import AdvisorRole
from src.core.memory import MemoryManager


class TestDiplomacyBasics:
    """Test basic diplomacy system components."""
    
    def test_diplomacy_manager_creation(self):
        """Test creating a diplomacy manager."""
        diplomacy = DiplomacyManager()
        
        assert diplomacy.current_turn == 1
        assert diplomacy.global_stability == 0.7
        assert len(diplomacy.active_civilizations) == 0
        assert len(diplomacy.civilization_relations) == 0
        assert len(diplomacy.active_treaties) == 0
    
    def test_civilization_registration(self):
        """Test registering civilizations with diplomacy manager."""
        diplomacy = DiplomacyManager()
        
        # Register first civilization
        diplomacy.register_civilization("civ_1")
        assert "civ_1" in diplomacy.active_civilizations
        assert len(diplomacy.civilization_relations) == 0
        
        # Register second civilization - should create relations
        diplomacy.register_civilization("civ_2")
        assert "civ_2" in diplomacy.active_civilizations
        assert len(diplomacy.civilization_relations) == 1
        
        relations = diplomacy.get_relations("civ_1", "civ_2")
        assert relations is not None
        assert relations.current_status == DiplomaticStatus.NEUTRAL
    
    def test_relationship_key_consistency(self):
        """Test that relationship keys are consistent regardless of order."""
        diplomacy = DiplomacyManager()
        
        key1 = diplomacy.get_relationship_key("civ_a", "civ_b")
        key2 = diplomacy.get_relationship_key("civ_b", "civ_a")
        
        assert key1 == key2
        assert key1 == "civ_a:civ_b"


class TestCivilizationRelations:
    """Test bilateral civilization relationships."""
    
    @pytest.fixture
    def diplomacy_manager(self):
        """Create a diplomacy manager with two civilizations."""
        diplomacy = DiplomacyManager()
        diplomacy.register_civilization("empire_1")
        diplomacy.register_civilization("empire_2")
        return diplomacy
    
    def test_relations_creation(self, diplomacy_manager):
        """Test basic relations creation and properties."""
        relations = diplomacy_manager.get_relations("empire_1", "empire_2")
        
        assert relations is not None
        assert relations.current_status == DiplomaticStatus.NEUTRAL
        assert relations.trust_level == 0.5
        assert relations.trade_dependency == 0.0
        assert not relations.embassy_established
        assert len(relations.active_treaties) == 0
    
    def test_establish_relations_existing(self, diplomacy_manager):
        """Test establishing relations when they already exist."""
        original_relations = diplomacy_manager.get_relations("empire_1", "empire_2")
        established_relations = diplomacy_manager.establish_relations("empire_1", "empire_2")
        
        assert original_relations is established_relations
        assert len(diplomacy_manager.civilization_relations) == 1
    
    def test_relations_status_changes(self, diplomacy_manager):
        """Test changing diplomatic status."""
        relations = diplomacy_manager.get_relations("empire_1", "empire_2")
        
        # Change to friendly
        relations.current_status = DiplomaticStatus.FRIENDLY
        relations.trust_level = 0.8
        
        assert relations.current_status == DiplomaticStatus.FRIENDLY
        assert relations.trust_level == 0.8
        
        # Change to hostile
        relations.current_status = DiplomaticStatus.HOSTILE
        relations.trust_level = 0.2
        
        assert relations.current_status == DiplomaticStatus.HOSTILE
        assert relations.trust_level == 0.2


class TestTreaties:
    """Test treaty system."""
    
    def test_treaty_creation(self):
        """Test creating different types of treaties."""
        trade_treaty = Treaty(
            treaty_type=TreatyType.TRADE_AGREEMENT,
            participants=["civ_1", "civ_2"],
            signed_turn=1,
            trade_value_per_turn=100.0
        )
        
        assert trade_treaty.treaty_type == TreatyType.TRADE_AGREEMENT
        assert len(trade_treaty.participants) == 2
        assert trade_treaty.active is True
        assert trade_treaty.trade_value_per_turn == 100.0
        
        defense_treaty = Treaty(
            treaty_type=TreatyType.DEFENSE_PACT,
            participants=["civ_1", "civ_2", "civ_3"],
            signed_turn=5,
            military_support_level=0.8
        )
        
        assert defense_treaty.treaty_type == TreatyType.DEFENSE_PACT
        assert len(defense_treaty.participants) == 3
        assert defense_treaty.military_support_level == 0.8
    
    def test_treaty_violation(self):
        """Test treaty violation mechanics."""
        treaty = Treaty(
            treaty_type=TreatyType.NON_AGGRESSION_PACT,
            participants=["civ_1", "civ_2"],
            signed_turn=1
        )
        
        # Violate treaty
        treaty.violated_by = "civ_1"
        treaty.violation_reason = "territorial_aggression"
        treaty.active = False
        
        assert treaty.violated_by == "civ_1"
        assert treaty.violation_reason == "territorial_aggression"
        assert not treaty.active


class TestTradeRoutes:
    """Test inter-civilization trade systems."""
    
    def test_trade_route_creation(self):
        """Test creating trade routes."""
        trade_route = TradeRoute(
            origin_civilization="merchant_empire",
            destination_civilization="resource_kingdom",
            trade_value_per_turn=150.0,
            established_turn=3
        )
        
        assert trade_route.origin_civilization == "merchant_empire"
        assert trade_route.destination_civilization == "resource_kingdom"
        assert trade_route.trade_value_per_turn == 150.0
        assert trade_route.active is True
        assert trade_route.total_value_exchanged == 0.0
    
    def test_trade_route_updates(self):
        """Test trade route value accumulation."""
        trade_route = TradeRoute(
            origin_civilization="civ_1",
            destination_civilization="civ_2",
            trade_value_per_turn=50.0,
            established_turn=1
        )
        
        # Simulate trade over multiple turns
        for turn in range(5):
            trade_route.total_value_exchanged += trade_route.trade_value_per_turn
        
        assert trade_route.total_value_exchanged == 250.0
    
    def test_trade_route_disruption(self):
        """Test trade route disruption mechanics."""
        trade_route = TradeRoute(
            origin_civilization="civ_1",
            destination_civilization="civ_2",
            trade_value_per_turn=75.0,
            established_turn=1
        )
        
        # Disrupt trade
        trade_route.active = False
        trade_route.disrupted_turns = 3
        trade_route.piracy_risk = 0.6
        
        assert not trade_route.active
        assert trade_route.disrupted_turns == 3
        assert trade_route.piracy_risk == 0.6


class TestMilitaryConflicts:
    """Test military conflict system."""
    
    def test_conflict_creation(self):
        """Test creating military conflicts."""
        conflict = MilitaryConflict(
            conflict_type=ConflictType.FULL_SCALE_WAR,
            belligerents={
                "attackers": ["aggressive_empire"],
                "defenders": ["peaceful_kingdom", "allied_republic"]
            },
            started_turn=10,
            objectives={"aggressive_empire": ["territory", "resources"]},
            military_balance={
                "aggressive_empire": 0.8,
                "peaceful_kingdom": 0.4,
                "allied_republic": 0.6
            }
        )
        
        assert conflict.conflict_type == ConflictType.FULL_SCALE_WAR
        assert len(conflict.belligerents["attackers"]) == 1
        assert len(conflict.belligerents["defenders"]) == 2
        assert conflict.active is True
        assert "territory" in conflict.objectives["aggressive_empire"]
    
    def test_conflict_progression(self):
        """Test conflict progression over time."""
        conflict = MilitaryConflict(
            conflict_type=ConflictType.BORDER_SKIRMISH,
            belligerents={
                "attackers": ["civ_1"],
                "defenders": ["civ_2"]
            },
            started_turn=1,
            war_exhaustion={"civ_1": 0.0, "civ_2": 0.0},
            civilian_support={"civ_1": 0.8, "civ_2": 0.7}
        )
        
        # Simulate conflict progression
        for turn in range(5):
            conflict.duration += 1
            for civ in ["civ_1", "civ_2"]:
                conflict.war_exhaustion[civ] = min(1.0, conflict.war_exhaustion[civ] + 0.05)
                conflict.civilian_support[civ] = max(0.0, conflict.civilian_support[civ] - 0.02)
        
        assert conflict.duration == 5
        assert conflict.war_exhaustion["civ_1"] == 0.25
        assert conflict.civilian_support["civ_1"] < 0.8
    
    def test_conflict_resolution(self):
        """Test conflict resolution mechanics."""
        conflict = MilitaryConflict(
            conflict_type=ConflictType.TERRITORIAL_DISPUTE,
            belligerents={
                "attackers": ["civ_1"],
                "defenders": ["civ_2"]
            },
            started_turn=1
        )
        
        # Resolve conflict
        conflict.active = False
        conflict.victor = "civ_2"
        conflict.peace_terms = {
            "territorial_changes": "status_quo",
            "reparations": 1000.0,
            "treaty_required": "non_aggression_pact"
        }
        
        assert not conflict.active
        assert conflict.victor == "civ_2"
        assert "reparations" in conflict.peace_terms


class TestIntelligenceOperations:
    """Test espionage and intelligence systems."""
    
    def test_intelligence_network_creation(self):
        """Test creating intelligence networks."""
        network = IntelligenceNetwork(
            operator_civilization="spy_empire",
            target_civilization="target_kingdom",
            operation_type=IntelligenceOperation.DIPLOMATIC_ESPIONAGE,
            network_strength=0.6
        )
        
        assert network.operator_civilization == "spy_empire"
        assert network.target_civilization == "target_kingdom"
        assert network.operation_type == IntelligenceOperation.DIPLOMATIC_ESPIONAGE
        assert network.network_strength == 0.6
        assert len(network.active_operations) == 0
    
    def test_intelligence_operations(self):
        """Test executing intelligence operations."""
        network = IntelligenceNetwork(
            operator_civilization="civ_1",
            target_civilization="civ_2",
            operation_type=IntelligenceOperation.MILITARY_INTELLIGENCE,
            network_strength=0.4
        )
        
        # Launch operations
        network.active_operations.append("military_recon_turn_5")
        network.agents_deployed += 2
        network.intelligence_gathered["military_strength"] = 0.7
        
        assert len(network.active_operations) == 1
        assert network.agents_deployed == 2
        assert "military_strength" in network.intelligence_gathered
    
    def test_counter_intelligence(self):
        """Test counter-intelligence mechanics."""
        network = IntelligenceNetwork(
            operator_civilization="civ_1",
            target_civilization="civ_2",
            operation_type=IntelligenceOperation.ECONOMIC_ESPIONAGE,
            network_strength=0.5,
            counter_intelligence_resistance=0.8
        )
        
        # Simulate counter-intelligence discovery
        network.discovered_operations.append({
            "operation": "trade_secret_theft",
            "discovered_turn": 10,
            "damage_assessment": "minimal"
        })
        network.assets_compromised += 1
        
        assert len(network.discovered_operations) == 1
        assert network.assets_compromised == 1


class TestDiplomaticEvents:
    """Test diplomatic event system."""
    
    def test_diplomatic_event_creation(self):
        """Test creating diplomatic events."""
        event = DiplomaticEvent(
            event_type="trade_dispute",
            civilizations_involved=["civ_1", "civ_2"],
            turn_created=15,
            title="Trade Route Disagreement",
            description="Dispute over tariff rates on luxury goods",
            instigator="civ_1",
            requires_response=True,
            response_deadline=18
        )
        
        assert event.event_type == "trade_dispute"
        assert len(event.civilizations_involved) == 2
        assert event.requires_response is True
        assert event.response_deadline == 18
    
    def test_diplomatic_event_impact(self):
        """Test diplomatic event impact on relationships."""
        event = DiplomaticEvent(
            event_type="cultural_festival",
            civilizations_involved=["civ_1", "civ_2"],
            turn_created=5,
            title="Cultural Exchange Festival",
            description="Joint cultural celebration",
            relationship_changes={
                "civ_1:civ_2": {
                    "trust_level": 0.1,
                    "cultural_affinity": 0.2
                }
            }
        )
        
        assert "civ_1:civ_2" in event.relationship_changes
        assert event.relationship_changes["civ_1:civ_2"]["trust_level"] == 0.1


class TestDiplomacyManagerIntegration:
    """Test complete diplomacy manager functionality."""
    
    @pytest.fixture
    def complex_diplomacy_setup(self):
        """Create a complex diplomatic scenario."""
        diplomacy = DiplomacyManager()
        
        # Register multiple civilizations
        civilizations = ["empire_1", "republic_2", "kingdom_3", "federation_4"]
        for civ in civilizations:
            diplomacy.register_civilization(civ)
        
        # Create some treaties
        trade_treaty = Treaty(
            treaty_type=TreatyType.TRADE_AGREEMENT,
            participants=["empire_1", "republic_2"],
            signed_turn=1,
            trade_value_per_turn=200.0
        )
        diplomacy.active_treaties[trade_treaty.id] = trade_treaty
        
        defense_pact = Treaty(
            treaty_type=TreatyType.DEFENSE_PACT,
            participants=["republic_2", "kingdom_3"],
            signed_turn=3,
            military_support_level=0.8
        )
        diplomacy.active_treaties[defense_pact.id] = defense_pact
        
        # Create trade routes
        trade_route = TradeRoute(
            origin_civilization="empire_1",
            destination_civilization="federation_4",
            trade_value_per_turn=150.0,
            established_turn=2
        )
        diplomacy.trade_routes[trade_route.id] = trade_route
        
        return diplomacy
    
    def test_diplomatic_turn_processing(self, complex_diplomacy_setup):
        """Test processing a diplomatic turn."""
        diplomacy = complex_diplomacy_setup
        
        results = diplomacy.update_diplomatic_turn(5)
        
        assert results["turn"] == 5
        assert "new_events" in results
        assert "treaty_changes" in results
        assert "trade_updates" in results
        assert "conflict_updates" in results
        assert "intelligence_operations" in results
    
    def test_diplomatic_summary_generation(self, complex_diplomacy_setup):
        """Test generating diplomatic summaries."""
        diplomacy = complex_diplomacy_setup
        
        summary = diplomacy.get_diplomatic_summary("empire_1")
        
        assert summary["civilization_id"] == "empire_1"
        assert "relations" in summary
        assert "active_treaties" in summary
        assert "trade_routes" in summary
        assert len(summary["relations"]) >= 3  # Relations with other 3 civilizations
    
    def test_global_stability_calculation(self, complex_diplomacy_setup):
        """Test global stability calculations."""
        diplomacy = complex_diplomacy_setup
        
        initial_stability = diplomacy.global_stability
        initial_conflicts = len([c for c in diplomacy.military_conflicts.values() if c.active])
        initial_treaties = len([t for t in diplomacy.active_treaties.values() if t.active])
        
        # Add a conflict
        conflict = MilitaryConflict(
            conflict_type=ConflictType.BORDER_SKIRMISH,
            belligerents={
                "attackers": ["empire_1"],
                "defenders": ["kingdom_3"]
            },
            started_turn=1,
            active=True  # Ensure conflict is active
        )
        diplomacy.military_conflicts[conflict.id] = conflict
        
        # Process turn to update stability
        diplomacy.update_diplomatic_turn(6)
        
        # Calculate expected stability: 0.7 - (new_conflicts * 0.1) + (treaties * 0.05)
        new_conflicts = len([c for c in diplomacy.military_conflicts.values() if c.active])
        active_treaties = len([t for t in diplomacy.active_treaties.values() if t.active])
        expected_stability = max(0.0, min(1.0, 0.7 - (new_conflicts * 0.1) + (active_treaties * 0.05)))
        
        # Verify stability calculation is working correctly
        assert diplomacy.global_stability == expected_stability
        # Since we added one conflict (0.1 penalty) but already have treaties (0.1 bonus), 
        # the stability should be the same unless we have more conflicts than treaties
        assert new_conflicts > initial_conflicts  # Verify we added a conflict


class TestCivilizationDiplomaticIntegration:
    """Test integration of diplomacy system with civilization management."""
    
    @pytest.fixture
    def diplomatic_civilizations(self):
        """Create two civilizations with diplomacy integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create first civilization
            leader1 = Leader(
                name="Emperor Marcus",
                civilization_id="roman_empire",
                personality=PersonalityProfile(
                    aggression=0.6,
                    diplomacy=0.8,
                    loyalty=0.7,
                    ambition=0.5,
                    cunning=0.6
                ),
                leadership_style=LeadershipStyle.PRAGMATIC
            )
            
            civ1 = Civilization(name="Roman Empire", leader=leader1)
            civ1.memory_manager = MemoryManager(data_dir=Path(temp_dir) / "civ1")
            
            # Create second civilization
            leader2 = Leader(
                name="Queen Isabella",
                civilization_id="spanish_kingdom",
                personality=PersonalityProfile(
                    aggression=0.4,
                    diplomacy=0.9,
                    loyalty=0.8,
                    ambition=0.6,
                    cunning=0.5
                ),
                leadership_style=LeadershipStyle.COLLABORATIVE
            )
            
            civ2 = Civilization(name="Spanish Kingdom", leader=leader2)
            civ2.memory_manager = MemoryManager(data_dir=Path(temp_dir) / "civ2")
            
            # Add diplomatic advisors
            for civ in [civ1, civ2]:
                diplomat = AdvisorWithMemory(
                    id=f"diplomat_{civ.id}",
                    name="Ambassador",
                    role=AdvisorRole.DIPLOMATIC,
                    civilization_id=civ.id,
                    personality=PersonalityProfile(
                        aggression=0.3,
                        diplomacy=0.9,
                        loyalty=0.8,
                        ambition=0.4,
                        cunning=0.7
                    ),
                    loyalty=0.8,
                    influence=0.7
                )
                civ.add_advisor(diplomat)
            
            # Create shared diplomacy manager
            diplomacy = DiplomacyManager()
            civ1.set_diplomacy_manager(diplomacy)
            civ2.set_diplomacy_manager(diplomacy)
            
            return civ1, civ2, diplomacy
    
    def test_embassy_establishment(self, diplomatic_civilizations):
        """Test establishing embassies between civilizations."""
        civ1, civ2, diplomacy = diplomatic_civilizations
        
        # Establish embassy
        success = civ1.establish_embassy(civ2.id, f"diplomat_{civ1.id}")
        
        assert success is True
        assert civ2.id in civ1.known_civilizations
        
        # Check relations updated
        relations = diplomacy.get_relations(civ1.id, civ2.id)
        assert relations.embassy_established is True
        assert relations.ambassador_assigned == f"diplomat_{civ1.id}"
    
    def test_treaty_proposal(self, diplomatic_civilizations):
        """Test proposing treaties between civilizations."""
        civ1, civ2, diplomacy = diplomatic_civilizations
        
        treaty_terms = {
            "trade_value": 200.0,
            "duration": 10,
            "tariff_reduction": 0.5
        }
        
        treaty_id = civ1.propose_treaty(civ2.id, "trade_agreement", treaty_terms)
        
        assert treaty_id is not None
        assert len(diplomacy.pending_negotiations) == 1
        
        # Check diplomatic memory created
        diplomat = civ1.get_advisor_by_role(AdvisorRole.DIPLOMATIC)
        memories = civ1.memory_manager.recall_memories(diplomat.id)
        treaty_memories = [m for m in memories if "treaty" in m.tags]
        assert len(treaty_memories) > 0
    
    def test_war_declaration(self, diplomatic_civilizations):
        """Test declaring war between civilizations."""
        civ1, civ2, diplomacy = diplomatic_civilizations
        
        war_objectives = ["territorial_expansion", "resource_control"]
        conflict_id = civ1.declare_war(civ2.id, war_objectives)
        
        assert conflict_id is not None
        assert len(diplomacy.military_conflicts) == 1
        
        # Check relations status updated
        relations = diplomacy.get_relations(civ1.id, civ2.id)
        assert relations.current_status == DiplomaticStatus.AT_WAR
        
        # Check political state affected
        assert civ1.political_state.internal_tension >= 0.2
        
        # Check war memories created
        for advisor in civ1.advisors.values():
            memories = civ1.memory_manager.recall_memories(advisor.id)
            war_memories = [m for m in memories if "war" in m.tags]
            assert len(war_memories) > 0
    
    def test_international_trade_establishment(self, diplomatic_civilizations):
        """Test establishing international trade routes."""
        civ1, civ2, diplomacy = diplomatic_civilizations
        
        trade_success = civ1.establish_international_trade_route(civ2.id, 150.0, "materials")
        
        assert trade_success is True
        assert len(diplomacy.trade_routes) == 1
        
        # Check economic state updated
        if civ1.resource_manager:
            economic_state = civ1.resource_manager.economic_state
            assert civ2.id in economic_state.trade_routes
            assert economic_state.trade_income >= 150.0
        
        # Check relations updated
        relations = diplomacy.get_relations(civ1.id, civ2.id)
        assert relations.trade_dependency > 0.0
        assert len(relations.trade_routes) == 1
    
    def test_intelligence_operation_launch(self, diplomatic_civilizations):
        """Test launching intelligence operations."""
        civ1, civ2, diplomacy = diplomatic_civilizations
        
        intel_success = civ1.launch_intelligence_operation(civ2.id, "diplomatic_espionage")
        
        assert intel_success is True
        assert civ2.id in civ1.espionage_capabilities
        assert len(diplomacy.intelligence_networks) == 1
        
        # Check intelligence memories created
        security_advisor = civ1.get_advisor_by_role(AdvisorRole.SECURITY)
        if security_advisor:
            memories = civ1.memory_manager.recall_memories(security_advisor.id)
            intel_memories = [m for m in memories if "intelligence" in m.tags]
            assert len(intel_memories) > 0
    
    def test_comprehensive_diplomatic_summary(self, diplomatic_civilizations):
        """Test comprehensive diplomatic summary generation."""
        civ1, civ2, diplomacy = diplomatic_civilizations
        
        # Establish various diplomatic relations
        civ1.establish_embassy(civ2.id)
        civ1.establish_international_trade_route(civ2.id, 100.0)
        
        # Get comprehensive summary
        summary = civ1.get_comprehensive_summary()
        
        assert "diplomacy" in summary
        assert "integration" in summary
        assert summary["integration"]["diplomacy_manager_active"] is True
        assert summary["integration"]["known_civilizations"] >= 1
    
    def test_diplomatic_memory_integration(self, diplomatic_civilizations):
        """Test that diplomatic actions create appropriate advisor memories."""
        civ1, civ2, diplomacy = diplomatic_civilizations
        
        # Perform various diplomatic actions
        civ1.establish_embassy(civ2.id)
        civ1.establish_international_trade_route(civ2.id, 75.0)
        civ1.launch_intelligence_operation(civ2.id, "economic_espionage")
        
        # Check that memories were created for relevant advisors
        diplomat = civ1.get_advisor_by_role(AdvisorRole.DIPLOMATIC)
        economic_advisor = civ1.get_advisor_by_role(AdvisorRole.ECONOMIC)
        security_advisor = civ1.get_advisor_by_role(AdvisorRole.SECURITY)
        
        if diplomat:
            diplomat_memories = civ1.memory_manager.recall_memories(diplomat.id)
            diplomatic_memories = [m for m in diplomat_memories if "diplomacy" in m.tags or "embassy" in m.tags]
            assert len(diplomatic_memories) > 0
        
        if security_advisor:
            security_memories = civ1.memory_manager.recall_memories(security_advisor.id)
            intel_memories = [m for m in security_memories if "intelligence" in m.tags]
            assert len(intel_memories) > 0


class TestDiplomaticTurnIntegration:
    """Test integration of diplomatic turns with civilization turns."""
    
    def test_diplomatic_turn_processing_with_civilizations(self):
        """Test diplomatic turn processing integrated with civilization turns."""
        # Create diplomacy manager
        diplomacy = DiplomacyManager()
        
        # Create civilizations
        civilizations = []
        for i in range(3):
            leader = Leader(
                name=f"Leader {i}",
                civilization_id=f"civ_{i}",
                personality=PersonalityProfile(
                    aggression=0.5,
                    diplomacy=0.6,
                    loyalty=0.7,
                    ambition=0.5,
                    cunning=0.5
                ),
                leadership_style=LeadershipStyle.PRAGMATIC
            )
            
            civ = Civilization(name=f"Civilization {i}", leader=leader)
            civ.set_diplomacy_manager(diplomacy)
            civilizations.append(civ)
        
        # Establish some diplomatic relations
        civilizations[0].establish_embassy(civilizations[1].id)
        civilizations[1].establish_international_trade_route(civilizations[2].id, 100.0)
        
        # Process multiple turns
        for turn in range(1, 6):
            # Process diplomatic turn
            diplomatic_results = diplomacy.update_diplomatic_turn(turn)
            
            # Process civilization turns
            for civ in civilizations:
                civ_results = civ.process_turn()
                
                # Verify integration
                assert diplomatic_results["turn"] == turn
                assert civ_results["turn"] == turn
        
        # Verify diplomatic state persisted
        assert diplomacy.current_turn == 5
        assert len(diplomacy.trade_routes) >= 1
        assert len(diplomacy.civilization_relations) >= 3
