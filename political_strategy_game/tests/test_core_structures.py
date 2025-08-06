"""
Tests for core data structures.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_import_core_modules():
    """Test that core modules can be imported."""
    try:
        from core.advisor import Advisor, PersonalityProfile, AdvisorRole
        from core.leader import Leader, LeadershipStyle
        from core.memory import Memory, MemoryManager, MemoryType
        from core.political_event import PoliticalEvent, EventType
        from core.civilization import Civilization
        assert True  # If we get here, imports worked
    except ImportError as e:
        pytest.fail(f"Failed to import core modules: {e}")

def test_personality_profile_creation():
    """Test creating a personality profile with default values."""
    try:
        from core.advisor import PersonalityProfile
        
        # Test with defaults
        personality = PersonalityProfile()
        assert 0.0 <= personality.ambition <= 1.0
        assert 0.0 <= personality.loyalty <= 1.0
        assert personality.ideology == "pragmatic"
        
        # Test with custom values
        custom_personality = PersonalityProfile(
            ambition=0.8,
            loyalty=0.3,
            ideology="militaristic"
        )
        assert custom_personality.ambition == 0.8
        assert custom_personality.loyalty == 0.3
        assert custom_personality.ideology == "militaristic"
        
    except ImportError:
        pytest.skip("Pydantic not available - skipping personality tests")

def test_advisor_creation():
    """Test creating an advisor with basic properties."""
    try:
        from core.advisor import Advisor, PersonalityProfile, AdvisorRole
        
        personality = PersonalityProfile(ambition=0.7, loyalty=0.5)
        
        advisor = Advisor(
            name="Test General",
            role=AdvisorRole.MILITARY,
            civilization_id="test_civ",
            personality=personality
        )
        
        assert advisor.name == "Test General"
        assert advisor.role == AdvisorRole.MILITARY
        assert advisor.civilization_id == "test_civ"
        assert advisor.personality.ambition == 0.7
        assert 0.0 <= advisor.influence <= 1.0
        assert 0.0 <= advisor.loyalty_to_leader <= 1.0
        
    except ImportError:
        pytest.skip("Dependencies not available - skipping advisor tests")

def test_leader_creation():
    """Test creating a leader with basic properties."""
    try:
        from core.leader import Leader, LeadershipStyle, PersonalityProfile
        
        personality = PersonalityProfile(ambition=0.9, charisma=0.8)
        
        leader = Leader(
            name="Test Emperor",
            civilization_id="test_civ",
            personality=personality,
            leadership_style=LeadershipStyle.AUTHORITARIAN
        )
        
        assert leader.name == "Test Emperor"
        assert leader.civilization_id == "test_civ"
        assert leader.leadership_style == LeadershipStyle.AUTHORITARIAN
        assert 0.0 <= leader.legitimacy <= 1.0
        assert 0.0 <= leader.popularity <= 1.0
        
    except ImportError:
        pytest.skip("Dependencies not available - skipping leader tests")

def test_memory_creation():
    """Test creating a memory object."""
    try:
        from core.memory import Memory, MemoryType
        
        memory = Memory(
            advisor_id="advisor_001",
            event_type=MemoryType.DECISION,
            content="Leader chose to declare war despite my advice",
            emotional_impact=0.8,
            created_turn=45,
            last_accessed_turn=45,
            tags={"war", "betrayal"}
        )
        
        assert memory.advisor_id == "advisor_001"
        assert memory.event_type == MemoryType.DECISION
        assert memory.emotional_impact == 0.8
        assert "war" in memory.tags
        assert "betrayal" in memory.tags
        
    except ImportError:
        pytest.skip("Dependencies not available - skipping memory tests")

def test_political_event_creation():
    """Test creating a political event."""
    try:
        from core.political_event import PoliticalEvent, EventType, EventSeverity
        
        event = PoliticalEvent(
            type=EventType.DECISION,
            severity=EventSeverity.MAJOR,
            civilization_id="test_civ",
            turn_occurred=10,
            title="War Declaration",
            description="Leader declared war on neighboring empire",
            participants=["leader_001", "advisor_001", "advisor_002"]
        )
        
        assert event.type == EventType.DECISION
        assert event.severity == EventSeverity.MAJOR
        assert event.title == "War Declaration"
        assert len(event.participants) == 3
        
    except ImportError:
        pytest.skip("Dependencies not available - skipping event tests")

def test_data_structure_integration():
    """Test that data structures work together."""
    try:
        from core.advisor import Advisor, PersonalityProfile, AdvisorRole
        from core.leader import Leader, LeadershipStyle
        from core.civilization import Civilization
        
        # Create a simple civilization with leader and advisor
        leader_personality = PersonalityProfile(ambition=0.8, charisma=0.7)
        leader = Leader(
            name="Test King",
            civilization_id="test_civ",
            personality=leader_personality,
            leadership_style=LeadershipStyle.COLLABORATIVE
        )
        
        advisor_personality = PersonalityProfile(ambition=0.6, loyalty=0.8)
        advisor = Advisor(
            name="Test Advisor",
            role=AdvisorRole.DIPLOMATIC,
            civilization_id="test_civ",
            personality=advisor_personality
        )
        
        civilization = Civilization(
            name="Test Empire",
            leader=leader
        )
        
        # Test adding advisor
        success = civilization.add_advisor(advisor)
        assert success
        assert advisor.id in civilization.advisors
        
        # Test getting active advisors
        active_advisors = civilization.get_active_advisors()
        assert len(active_advisors) == 1
        assert active_advisors[0].name == "Test Advisor"
        
    except ImportError:
        pytest.skip("Dependencies not available - skipping integration tests")

if __name__ == "__main__":
    # Run tests directly
    test_import_core_modules()
    print("✓ Core module imports successful")
    
    test_personality_profile_creation()
    print("✓ Personality profile creation successful")
    
    test_advisor_creation()
    print("✓ Advisor creation successful")
    
    test_leader_creation()
    print("✓ Leader creation successful")
    
    test_memory_creation()
    print("✓ Memory creation successful")
    
    test_political_event_creation()
    print("✓ Political event creation successful")
    
    test_data_structure_integration()
    print("✓ Data structure integration successful")
    
    print("\nAll basic tests passed! ✅")
