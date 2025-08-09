"""
Unit tests for the enhanced advisor system with memory integration.
"""

import pytest
import tempfile
from pathlib import Path
from typing import Set

from src.core.advisor import PersonalityProfile, AdvisorRole, AdvisorStatus
from src.core.advisor_enhanced import AdvisorWithMemory, AdvisorCouncil
from src.core.memory import MemoryManager, Memory, MemoryType
from src.core.memory_factory import MemoryFactory, MemoryScenario


class TestPersonalityProfile:
    """Test the PersonalityProfile class."""
    
    def test_personality_creation(self):
        """Test basic personality profile creation."""
        personality = PersonalityProfile(
            ambition=0.8,
            loyalty=0.6,
            ideology="authoritarian",
            corruption=0.2,
            pragmatism=0.7,
            paranoia=0.3,
            charisma=0.9,
            competence=0.8
        )
        
        assert personality.ambition == 0.8
        assert personality.loyalty == 0.6
        assert personality.ideology == "authoritarian"
        assert personality.corruption == 0.2
    
    def test_compatibility_score(self):
        """Test personality compatibility calculation."""
        personality1 = PersonalityProfile(
            ambition=0.3,
            loyalty=0.8,
            ideology="democratic",
            corruption=0.1,
            pragmatism=0.8,
            paranoia=0.2
        )
        
        personality2 = PersonalityProfile(
            ambition=0.2,
            loyalty=0.9,
            ideology="democratic",
            corruption=0.1,
            pragmatism=0.7,
            paranoia=0.1
        )
        
        # Very similar personalities should be highly compatible
        compatibility = personality1.compatibility_score(personality2)
        assert compatibility > 0.7
        
        # Test with conflicting personalities
        personality3 = PersonalityProfile(
            ambition=0.9,
            loyalty=0.2,
            ideology="authoritarian",
            corruption=0.8,
            pragmatism=0.2,
            paranoia=0.9
        )
        
        conflict_compatibility = personality1.compatibility_score(personality3)
        assert conflict_compatibility < 0.5


class TestAdvisorWithMemory:
    """Test the enhanced advisor with memory integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory_manager = MemoryManager(Path(self.temp_dir))
        
        self.advisor = AdvisorWithMemory(
            name="Test Advisor",
            role=AdvisorRole.MILITARY,
            civilization_id="test_civ",
            personality=PersonalityProfile(
                ambition=0.6,
                loyalty=0.7,
                competence=0.8
            ),
            memory_manager=self.memory_manager
        )
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_advisor_creation_with_memory(self):
        """Test creating advisor with memory manager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_manager = MemoryManager(Path(temp_dir))
            
            advisor = AdvisorWithMemory(
                name="Memory Advisor",
                role=AdvisorRole.DIPLOMATIC,
                civilization_id="test_civ",
                personality=PersonalityProfile(),
                memory_manager=memory_manager
            )
            
            assert advisor.name == "Memory Advisor"
            assert advisor.role == AdvisorRole.DIPLOMATIC
            assert advisor._memory_manager is memory_manager
    
    def test_remember_event(self):
        """Test storing memories of events."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_manager = MemoryManager(Path(temp_dir))
            advisor = AdvisorWithMemory(
                name="Test Advisor",
                role=AdvisorRole.MILITARY,
                civilization_id="test_civ",
                personality=PersonalityProfile(),
                memory_manager=memory_manager
            )
            
            # Remember an event
            success = advisor.remember_event(
                event_type=MemoryType.DECISION,
                content="Approved military expansion",
                emotional_impact=0.7,
                current_turn=25,
                tags={"military", "expansion", "decision"}
            )
            
            assert success
            
            # Recall the memory
            memories = advisor.recall_memories_about(tags={"military"})
            assert len(memories) == 1
            assert memories[0].content == "Approved military expansion"
            assert memories[0].emotional_impact == 0.7
    
    def test_share_secret(self):
        """Test sharing secrets between advisors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_manager = MemoryManager(Path(temp_dir))
            
            advisor1 = AdvisorWithMemory(
                name="Advisor 1",
                role=AdvisorRole.MILITARY,
                civilization_id="test_civ",
                personality=PersonalityProfile(),
                memory_manager=memory_manager
            )
            
            advisor2 = AdvisorWithMemory(
                name="Advisor 2",
                role=AdvisorRole.DIPLOMATIC,
                civilization_id="test_civ",
                personality=PersonalityProfile(),
                memory_manager=memory_manager
            )
            
            # Share a secret
            success = advisor1.share_secret_with(
                advisor2.id,
                "The enemy is planning an attack next month",
                current_turn=30
            )
            
            assert success
            
            # Both advisors should have the secret
            advisor1_secrets = advisor1.recall_memories_about(tags={"secret"})
            advisor2_secrets = advisor2.recall_memories_about(tags={"secret"})
            
            assert len(advisor1_secrets) == 1
            assert len(advisor2_secrets) == 1
            
            # Check relationship update
            relationship = advisor1.get_relationship(advisor2.id)
            assert len(relationship.shared_secrets) > 0
            assert relationship.trust > 0.0
    
    def test_threat_assessment(self):
        """Test threat assessment from memories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_manager = MemoryManager(Path(temp_dir))
            advisor = AdvisorWithMemory(
                name="Test Advisor",
                role=AdvisorRole.SECURITY,
                civilization_id="test_civ",
                personality=PersonalityProfile(paranoia=0.8),
                memory_manager=memory_manager
            )
            
            # Add threatening memories
            advisor.remember_event(
                MemoryType.CONSPIRACY,
                "Overheard General plotting against the leader",
                emotional_impact=0.9,
                current_turn=10,
                tags={"conspiracy", "threat", "advisor_general"}
            )
            
            advisor.remember_event(
                MemoryType.INTELLIGENCE,
                "Spy network reports suspicious economic advisor meetings",
                emotional_impact=0.6,
                current_turn=12,
                tags={"intelligence", "threat", "advisor_economic"}
            )
            
            # Assess threats
            threats = advisor.assess_threat_from_memories(current_turn=15)
            
            assert "advisor_general" in threats
            assert "advisor_economic" in threats
            assert threats["advisor_general"] > threats["advisor_economic"]
    
    def test_memory_informed_decision(self):
        """Test decision making informed by memories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_manager = MemoryManager(Path(temp_dir))
            advisor = AdvisorWithMemory(
                name="Test Advisor",
                role=AdvisorRole.MILITARY,
                civilization_id="test_civ",
                personality=PersonalityProfile(pragmatism=0.8),
                memory_manager=memory_manager
            )
            
            # Add relevant memory
            advisor.remember_event(
                MemoryType.CRISIS,
                "Last naval expansion ended in disaster",
                emotional_impact=0.8,
                current_turn=5,
                tags={"military", "naval", "failure"}
            )
            
            # Decision options
            options = [
                {
                    "name": "Naval Expansion",
                    "base_value": 0.7,
                    "tags": ["military", "naval"],
                    "type": "aggressive"
                },
                {
                    "name": "Land Forces",
                    "base_value": 0.6,
                    "tags": ["military", "land"],
                    "type": "conservative"
                }
            ]
            
            context = {"tags": ["military"]}
            
            # Should prefer land forces due to bad naval memory
            decision = advisor.make_memory_informed_decision(options, context, current_turn=10)
            assert decision["name"] == "Land Forces"
    
    def test_relationship_updates_from_memories(self):
        """Test relationship updates based on memories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_manager = MemoryManager(Path(temp_dir))
            advisor = AdvisorWithMemory(
                name="Test Advisor",
                role=AdvisorRole.DIPLOMATIC,
                civilization_id="test_civ",
                personality=PersonalityProfile(),
                memory_manager=memory_manager
            )
            
            other_advisor_id = "other_advisor_123"
            
            # Create initial relationship
            relationship = advisor.get_relationship(other_advisor_id)
            initial_trust = relationship.trust
            
            # Add positive memory
            advisor.remember_event(
                MemoryType.RELATIONSHIP,
                "Economic advisor helped secure trade deal",
                emotional_impact=0.6,
                current_turn=20,
                tags={"relationship", "cooperation", other_advisor_id}
            )
            
            # Update relationships from memories
            advisor.update_relationships_from_memories(current_turn=21)
            
            # Trust should have increased
            updated_relationship = advisor.get_relationship(other_advisor_id)
            assert updated_relationship.trust > initial_trust


class TestAdvisorCouncil:
    """Test the advisor council management system."""
    
    def test_council_creation(self):
        """Test creating an advisor council."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_manager = MemoryManager(Path(temp_dir))
            
            council = AdvisorCouncil(
                civilization_id="test_civ",
                memory_manager=memory_manager
            )
            
            assert council.civilization_id == "test_civ"
            assert len(council.advisors) == 0
            assert council.current_turn == 0
    
    def test_add_remove_advisors(self):
        """Test adding and removing advisors from council."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_manager = MemoryManager(Path(temp_dir))
            council = AdvisorCouncil(civilization_id="test_civ")
            council.set_memory_manager(memory_manager)
            
            # Create advisor
            advisor = AdvisorWithMemory(
                name="Test Advisor",
                role=AdvisorRole.MILITARY,
                civilization_id="test_civ",
                personality=PersonalityProfile()
            )
            
            # Add to council
            council.add_advisor(advisor)
            assert len(council.advisors) == 1
            assert advisor.id in council.advisors
            assert advisor._memory_manager is memory_manager
            
            # Remove advisor
            success = council.remove_advisor(advisor.id, reason="dismissed")
            assert success
            assert advisor.status == AdvisorStatus.DISMISSED
    
    def test_council_dynamics_simulation(self):
        """Test simulating council political dynamics."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_manager = MemoryManager(Path(temp_dir))
            council = AdvisorCouncil(civilization_id="test_civ")
            council.set_memory_manager(memory_manager)
            
            # Create advisors with different personalities
            advisor1 = AdvisorWithMemory(
                name="Ambitious General",
                role=AdvisorRole.MILITARY,
                civilization_id="test_civ",
                personality=PersonalityProfile(
                    ambition=0.9,
                    loyalty=0.3,
                    paranoia=0.6
                )
            )
            
            advisor2 = AdvisorWithMemory(
                name="Scheming Diplomat",
                role=AdvisorRole.DIPLOMATIC,
                civilization_id="test_civ",
                personality=PersonalityProfile(
                    ambition=0.8,
                    loyalty=0.4,
                    charisma=0.9
                )
            )
            
            advisor3 = AdvisorWithMemory(
                name="Loyal Economist",
                role=AdvisorRole.ECONOMIC,
                civilization_id="test_civ",
                personality=PersonalityProfile(
                    ambition=0.2,
                    loyalty=0.9,
                    competence=0.8
                )
            )
            
            council.add_advisor(advisor1)
            council.add_advisor(advisor2)
            council.add_advisor(advisor3)
            
            # Simulate several turns
            for turn in range(5):
                results = council.simulate_council_dynamics()
                assert "conspiracies_formed" in results
                assert "relationships_changed" in results
            
            assert council.current_turn == 5
    
    def test_coup_risk_detection(self):
        """Test coup risk assessment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_manager = MemoryManager(Path(temp_dir))
            council = AdvisorCouncil(civilization_id="test_civ")
            council.set_memory_manager(memory_manager)
            
            # Create high-risk advisors
            advisor1 = AdvisorWithMemory(
                name="Disloyal General",
                role=AdvisorRole.MILITARY,
                civilization_id="test_civ",
                personality=PersonalityProfile(
                    ambition=0.9,
                    loyalty=0.1,
                    paranoia=0.8
                )
            )
            advisor1.loyalty_to_leader = 0.1
            advisor1.influence = 0.2
            
            advisor2 = AdvisorWithMemory(
                name="Plotting Spymaster",
                role=AdvisorRole.SECURITY,
                civilization_id="test_civ",
                personality=PersonalityProfile(
                    ambition=0.8,
                    loyalty=0.2,
                    paranoia=0.6
                )
            )
            advisor2.loyalty_to_leader = 0.2
            advisor2.influence = 0.3
            
            # Create relationship between conspirators
            relationship = advisor1.get_relationship(advisor2.id)
            relationship.trust = 0.8
            relationship.conspiracy_level = 0.7
            
            council.add_advisor(advisor1)
            council.add_advisor(advisor2)
            
            # Assess coup risk
            risk_assessment = council.detect_coup_risk()
            
            assert risk_assessment["risk_level"] in ["MEDIUM", "HIGH"]
            assert len(risk_assessment["potential_conspirators"]) >= 2
            assert len(risk_assessment["conspiracy_networks"]) > 0
    
    def test_loyalty_reporting(self):
        """Test loyalty level reporting."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_manager = MemoryManager(Path(temp_dir))
            council = AdvisorCouncil(civilization_id="test_civ")
            council.set_memory_manager(memory_manager)
            
            # Create advisors with different loyalties
            advisor1 = AdvisorWithMemory(
                name="Loyal Advisor",
                role=AdvisorRole.MILITARY,
                civilization_id="test_civ",
                personality=PersonalityProfile()
            )
            advisor1.loyalty_to_leader = 0.9
            
            advisor2 = AdvisorWithMemory(
                name="Disloyal Advisor",
                role=AdvisorRole.DIPLOMATIC,
                civilization_id="test_civ",
                personality=PersonalityProfile()
            )
            advisor2.loyalty_to_leader = 0.3
            
            council.add_advisor(advisor1)
            council.add_advisor(advisor2)
            
            # Get loyalty report
            loyalty_report = council.get_council_loyalty_report()
            
            assert len(loyalty_report) == 2
            assert loyalty_report[advisor1.id] == 0.9
            assert loyalty_report[advisor2.id] == 0.3


# Integration tests
class TestAdvisorMemoryIntegration:
    """Integration tests for advisor-memory system interaction."""
    
    def test_full_council_with_memory_lifecycle(self):
        """Test complete lifecycle of council with memory integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_manager = MemoryManager(Path(temp_dir))
            
            # Create council with realistic advisors
            council = AdvisorCouncil(civilization_id="empire1")
            council.set_memory_manager(memory_manager)
            
            # Create advisors with MemoryFactory data
            advisor_ids = ["emp1_military", "emp1_economic", "emp1_diplomatic"]
            
            for i, advisor_id in enumerate(advisor_ids):
                # Create advisor with varying personalities
                advisor = AdvisorWithMemory(
                    id=advisor_id,
                    name=f"Advisor {i+1}",
                    role=list(AdvisorRole)[i],
                    civilization_id="empire1",
                    personality=PersonalityProfile(
                        ambition=0.3 + i * 0.2,
                        loyalty=0.8 - i * 0.1,
                        competence=0.6 + i * 0.1
                    )
                )
                
                council.add_advisor(advisor)
                
                # Add some initial memories using MemoryFactory
                memories = MemoryFactory.create_memory_set(
                    advisor_id=advisor_id,
                    scenario=MemoryScenario.PEACEFUL_REIGN,
                    current_turn=0,
                    memory_count=10
                )
                
                for memory in memories:
                    memory_manager.store_memory(advisor_id, memory)
            
            # Simulate council operations over time
            for turn in range(1, 21):
                council.current_turn = turn
                
                # Each advisor remembers some events
                for advisor in council.advisors.values():
                    if advisor.status == AdvisorStatus.ACTIVE:
                        # Random events based on turn
                        if turn % 5 == 0:  # Major decision every 5 turns
                            advisor.remember_event(
                                MemoryType.DECISION,
                                f"Major policy decision at turn {turn}",
                                emotional_impact=0.6,
                                current_turn=turn,
                                tags={"policy", "decision", f"turn_{turn}"}
                            )
                        
                        if turn % 7 == 0:  # Crisis every 7 turns
                            advisor.remember_event(
                                MemoryType.CRISIS,
                                f"Crisis management at turn {turn}",
                                emotional_impact=0.8,
                                current_turn=turn,
                                tags={"crisis", f"turn_{turn}"}
                            )
                
                # Simulate council dynamics
                dynamics_result = council.simulate_council_dynamics()
                
                # Occasionally share secrets
                if turn % 10 == 0:
                    active_advisors = [a for a in council.advisors.values() 
                                     if a.status == AdvisorStatus.ACTIVE]
                    if len(active_advisors) >= 2:
                        advisor1, advisor2 = active_advisors[0], active_advisors[1]
                        advisor1.share_secret_with(
                            advisor2.id,
                            f"Secret intelligence from turn {turn}",
                            current_turn=turn
                        )
            
            # Final assessment
            final_loyalty = council.get_council_loyalty_report()
            coup_risk = council.detect_coup_risk()
            
            # Verify system state
            assert len(final_loyalty) > 0
            assert coup_risk["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
            
            # Check that advisors have accumulated memories
            for advisor in council.advisors.values():
                if advisor.status == AdvisorStatus.ACTIVE:
                    memories = advisor.recall_memories_about()
                    assert len(memories) >= 5  # Should have some memories remaining after decay
                    
                    # Check memory-informed threat assessment
                    threats = advisor.assess_threat_from_memories(current_turn=20)
                    assert isinstance(threats, dict)


if __name__ == "__main__":
    pytest.main([__file__])
