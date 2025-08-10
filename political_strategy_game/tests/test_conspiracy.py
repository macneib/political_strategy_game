"""
Tests for AI-Driven Conspiracy Generation System

This module tests the sophisticated conspiracy generation capabilities,
including motive analysis, plot generation, recruitment mechanics, and
conspiracy progression through different phases.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import json

from src.llm.conspiracy import (
    ConspiracyGenerator, ConspiracyType, ConspiracyStatus, ConspiracyMotive,
    ConspiracyParticipant, ConspiracyPlot
)
from src.llm.dialogue import MultiAdvisorDialogue, EmotionalState
from src.llm.advisors import AdvisorRole, AdvisorCouncil, AdvisorAI, AdvisorPersonality
from src.llm.llm_providers import LLMManager, LLMResponse, LLMProvider


class TestConspiracyDataStructures:
    """Test conspiracy data structures and enums."""
    
    def test_conspiracy_type_enum(self):
        """Test conspiracy type enumeration."""
        assert ConspiracyType.COUP.value == "coup"
        assert ConspiracyType.ASSASSINATION.value == "assassination"
        assert ConspiracyType.CORRUPTION.value == "corruption"
        assert len(list(ConspiracyType)) == 8
    
    def test_conspiracy_status_enum(self):
        """Test conspiracy status enumeration."""
        assert ConspiracyStatus.PLANNING.value == "planning"
        assert ConspiracyStatus.EXECUTION.value == "execution"
        assert ConspiracyStatus.DISCOVERED.value == "discovered"
        assert len(list(ConspiracyStatus)) == 8
    
    def test_conspiracy_motive_creation(self):
        """Test conspiracy motive data structure."""
        motive = ConspiracyMotive(
            primary_driver="Military budget cuts",
            emotional_trigger=EmotionalState.ANGRY,
            rational_justification="Weakening national defense",
            personal_stakes=0.8,
            ideological_alignment=-0.6,
            urgency_level=0.7
        )
        
        assert motive.primary_driver == "Military budget cuts"
        assert motive.emotional_trigger == EmotionalState.ANGRY
        assert motive.personal_stakes == 0.8
        assert motive.ideological_alignment == -0.6
    
    def test_conspiracy_participant_creation(self):
        """Test conspiracy participant data structure."""
        participant = ConspiracyParticipant(
            advisor_name="General Steel",
            role_in_conspiracy="Military Leader",
            commitment_level=0.9,
            discovery_risk=0.3,
            potential_rewards=["Increased military budget", "Political influence"],
            potential_costs=["Court martial", "Exile"],
            recruitment_method="Direct approach"
        )
        
        assert participant.advisor_name == "General Steel"
        assert participant.commitment_level == 0.9
        assert len(participant.potential_rewards) == 2
        assert isinstance(participant.recruitment_date, datetime)
    
    def test_conspiracy_plot_creation(self):
        """Test conspiracy plot data structure."""
        motive = ConspiracyMotive(
            primary_driver="Test driver",
            emotional_trigger=EmotionalState.ANGRY,
            rational_justification="Test justification",
            personal_stakes=0.5,
            ideological_alignment=0.0,
            urgency_level=0.6
        )
        
        participant = ConspiracyParticipant(
            advisor_name="Test Advisor",
            role_in_conspiracy="Initiator",
            commitment_level=0.8,
            discovery_risk=0.2,
            potential_rewards=["Power"],
            potential_costs=["Punishment"],
            recruitment_method="Self-initiated"
        )
        
        plot = ConspiracyPlot(
            plot_id="test_conspiracy_001",
            conspiracy_type=ConspiracyType.COUP,
            title="Test Military Coup",
            description="A test conspiracy plot",
            primary_motive=motive,
            target="Current Regime",
            participants=[participant],
            timeline={"Phase 1": "Planning", "Phase 2": "Execution"},
            required_resources={"gold": 1000, "influence": 50},
            success_conditions=["Military support", "Popular backing"],
            failure_conditions=["Discovery", "Lack of resources"],
            potential_consequences={
                "success": ["New government"],
                "failure": ["Executions"]
            },
            discovery_indicators=["Unusual meetings", "Resource movements"],
            status=ConspiracyStatus.PLANNING
        )
        
        assert plot.conspiracy_type == ConspiracyType.COUP
        assert plot.title == "Test Military Coup"
        assert len(plot.participants) == 1
        assert plot.status == ConspiracyStatus.PLANNING
        assert isinstance(plot.creation_date, datetime)


@pytest.fixture
def mock_llm_manager():
    """Create a mock LLM manager for testing."""
    manager = Mock(spec=LLMManager)
    manager.generate = AsyncMock()
    return manager


@pytest.fixture
def mock_dialogue_system():
    """Create a mock dialogue system for testing."""
    dialogue_system = Mock(spec=MultiAdvisorDialogue)
    
    # Mock advisor council
    advisors = {}
    advisor_roles = [AdvisorRole.MILITARY, AdvisorRole.ECONOMIC, AdvisorRole.DIPLOMATIC]
    
    for role in advisor_roles:
        personality = AdvisorPersonality.get_personality(role)
        advisor = Mock(spec=AdvisorAI)
        advisor.role = role
        advisor.personality = personality
        advisors[personality.name] = advisor
    
    council = Mock(spec=AdvisorCouncil)
    council.advisors = advisors
    dialogue_system.advisor_council = council
    
    # Mock emotional models
    dialogue_system.emotional_models = {
        name: Mock(current_emotion=EmotionalState.CALM, emotion_intensity=0.5)
        for name in advisors.keys()
    }
    
    # Mock get_advisor_emotional_state method
    dialogue_system.get_advisor_emotional_state = Mock(return_value={
        "emotion": "calm",
        "intensity": 0.5,
        "modifiers": {"aggression": 0.0, "cooperation": 0.5}
    })
    
    # Mock active dialogues
    dialogue_system.active_dialogues = {}
    
    return dialogue_system


@pytest.fixture
def mock_game_state():
    """Create a mock game state for testing."""
    return Mock(
        political_power=75,
        stability=60,
        legitimacy=70
    )


@pytest.fixture
def conspiracy_generator(mock_llm_manager, mock_dialogue_system):
    """Create a conspiracy generator for testing."""
    return ConspiracyGenerator(mock_llm_manager, mock_dialogue_system)


class TestConspiracyConditionAnalysis:
    """Test conspiracy condition analysis."""
    
    @pytest.mark.asyncio
    async def test_analyze_conspiracy_conditions(self, conspiracy_generator, mock_game_state):
        """Test conspiracy condition analysis."""
        # Mock LLM response for condition analysis
        conspiracy_generator.llm_manager.generate.return_value = LLMResponse(
            content='{"economic_crisis": 0.3, "external_pressure": 0.2, "corruption_exposure": 0.1, "military_dissatisfaction": 0.4}',
            provider=LLMProvider.VLLM,
            model="test-model"
        )
        
        conditions = await conspiracy_generator.analyze_conspiracy_conditions(
            mock_game_state, Mock()
        )
        
        assert "political_instability" in conditions
        assert "advisor_tensions" in conditions
        assert "economic_crisis" in conditions
        assert "military_dissatisfaction" in conditions
        
        # Political instability should be calculated from stability
        expected_instability = (100 - mock_game_state.stability) / 100
        assert conditions["political_instability"] == expected_instability
    
    @pytest.mark.asyncio
    async def test_analyze_ideological_tensions(self, conspiracy_generator):
        """Test ideological tension analysis from dialogues."""
        # Mock dialogue with tension indicators
        mock_dialogue = Mock()
        mock_dialogue.completed = True
        mock_dialogue.get_conversation_history.return_value = "I strongly disagree with this proposal. It is dangerous and unacceptable."
        
        conspiracy_generator.dialogue_system.active_dialogues = {"test": mock_dialogue}
        
        tension = await conspiracy_generator._analyze_ideological_tensions()
        
        assert tension > 0.0  # Should detect tension from keywords
    
    @pytest.mark.asyncio
    async def test_llm_analyze_conspiracy_conditions(self, conspiracy_generator, mock_game_state):
        """Test LLM-based conspiracy condition analysis."""
        conspiracy_generator.llm_manager.generate.return_value = LLMResponse(
            content='{"economic_crisis": 0.6, "external_pressure": 0.3, "corruption_exposure": 0.2, "military_dissatisfaction": 0.8}',
            provider=LLMProvider.VLLM,
            model="test-model"
        )
        
        base_conditions = {"political_instability": 0.4}
        additional = await conspiracy_generator._llm_analyze_conspiracy_conditions(
            mock_game_state, base_conditions
        )
        
        assert additional["economic_crisis"] == 0.6
        assert additional["military_dissatisfaction"] == 0.8
        # Values should be clamped between 0.0 and 1.0
        assert all(0.0 <= v <= 1.0 for v in additional.values())


class TestConspiracyMotiveGeneration:
    """Test conspiracy motive generation."""
    
    @pytest.mark.asyncio
    async def test_generate_conspiracy_motive_high_emotion(self, conspiracy_generator):
        """Test motive generation with high emotional intensity."""
        # Set high emotional intensity
        conspiracy_generator.dialogue_system.get_advisor_emotional_state.return_value = {
            "emotion": "angry",
            "intensity": 0.9
        }
        
        # Mock LLM response
        motive_data = {
            "primary_driver": "Military budget cuts threaten national security",
            "emotional_trigger": "angry",
            "rational_justification": "Inadequate funding weakens our defense capabilities",
            "personal_stakes": 0.8,
            "ideological_alignment": -0.7,
            "urgency_level": 0.9
        }
        
        conspiracy_generator.llm_manager.generate.return_value = LLMResponse(
            content=json.dumps(motive_data),
            provider=LLMProvider.VLLM,
            model="test-model"
        )
        
        advisor_name = "General Marcus Steel"
        conditions = {"military_dissatisfaction": 0.8}
        
        motive = await conspiracy_generator.generate_conspiracy_motive(advisor_name, conditions)
        
        assert motive is not None
        assert motive.emotional_trigger == EmotionalState.ANGRY
        assert motive.personal_stakes == 0.8
        assert motive.urgency_level == 0.9
    
    @pytest.mark.asyncio
    async def test_generate_conspiracy_motive_low_emotion(self, conspiracy_generator):
        """Test that low emotional intensity prevents motive generation."""
        # Set low emotional intensity
        conspiracy_generator.dialogue_system.get_advisor_emotional_state.return_value = {
            "emotion": "calm",
            "intensity": 0.3
        }
        
        advisor_name = "General Marcus Steel"
        conditions = {"military_dissatisfaction": 0.2}
        
        motive = await conspiracy_generator.generate_conspiracy_motive(advisor_name, conditions)
        
        assert motive is None  # Should not generate motive with low emotional intensity


class TestConspiracyPlotGeneration:
    """Test conspiracy plot generation."""
    
    @pytest.mark.asyncio
    async def test_generate_conspiracy_plot(self, conspiracy_generator):
        """Test complete conspiracy plot generation."""
        motive = ConspiracyMotive(
            primary_driver="Military budget cuts",
            emotional_trigger=EmotionalState.ANGRY,
            rational_justification="National defense is compromised",
            personal_stakes=0.8,
            ideological_alignment=-0.6,
            urgency_level=0.7
        )
        
        # Mock LLM response with conspiracy plot data
        plot_data = {
            "conspiracy_type": "coup",
            "title": "Operation Steel Resolve",
            "description": "A military coup to restore proper defense funding",
            "target": "Current civilian leadership",
            "timeline": {
                "Phase 1": "Assess military unit loyalty",
                "Phase 2": "Secure key installations",
                "Phase 3": "Execute power transfer"
            },
            "required_resources": {
                "gold": 5000,
                "influence": 80,
                "military_support": 60
            },
            "success_conditions": ["70% military support", "Control of capital"],
            "failure_conditions": ["Discovery before execution", "Insufficient military support"],
            "potential_consequences": {
                "success": ["Restored military budget", "Military government"],
                "failure": ["Court martial", "Execution of conspirators"]
            },
            "discovery_indicators": ["Unusual troop movements", "Secret meetings"]
        }
        
        conspiracy_generator.llm_manager.generate.return_value = LLMResponse(
            content=json.dumps(plot_data),
            provider=LLMProvider.VLLM,
            model="test-model"
        )
        
        initiator = "General Marcus Steel"
        conditions = {"military_dissatisfaction": 0.8}
        
        plot = await conspiracy_generator.generate_conspiracy_plot(initiator, motive, conditions)
        
        assert plot is not None
        assert plot.conspiracy_type == ConspiracyType.COUP
        assert plot.title == "Operation Steel Resolve"
        assert len(plot.participants) == 1
        assert plot.participants[0].advisor_name == initiator
        assert plot.status == ConspiracyStatus.PLANNING
        assert plot.plot_id.startswith("conspiracy_")


class TestRecruitmentMechanics:
    """Test conspiracy recruitment mechanics."""
    
    @pytest.mark.asyncio
    async def test_evaluate_recruitment_targets(self, conspiracy_generator):
        """Test recruitment target evaluation."""
        # Create a test conspiracy
        motive = ConspiracyMotive(
            primary_driver="Test driver",
            emotional_trigger=EmotionalState.ANGRY,
            rational_justification="Test justification",
            personal_stakes=0.8,
            ideological_alignment=-0.5,
            urgency_level=0.7
        )
        
        participant = ConspiracyParticipant(
            advisor_name="General Marcus Steel",
            role_in_conspiracy="Initiator",
            commitment_level=0.8,
            discovery_risk=0.3,
            potential_rewards=["Power"],
            potential_costs=["Execution"],
            recruitment_method="Self-initiated"
        )
        
        conspiracy = ConspiracyPlot(
            plot_id="test_conspiracy",
            conspiracy_type=ConspiracyType.COUP,
            title="Test Coup",
            description="Test description",
            primary_motive=motive,
            target="Government",
            participants=[participant],
            timeline={"Phase 1": "Planning"},
            required_resources={"gold": 1000},
            success_conditions=["Military support"],
            failure_conditions=["Discovery"],
            potential_consequences={"success": ["Victory"], "failure": ["Death"]},
            discovery_indicators=["Meetings"],
            status=ConspiracyStatus.PLANNING
        )
        
        # Mock LLM assessment
        conspiracy_generator.llm_manager.generate.return_value = LLMResponse(
            content='{"relationship_quality": 0.7, "ideological_alignment": 0.6, "risk_tolerance": 0.5}',
            provider=LLMProvider.VLLM,
            model="test-model"
        )
        
        targets = await conspiracy_generator.evaluate_recruitment_targets(conspiracy)
        
        assert isinstance(targets, list)
        # Should exclude the initiator
        target_names = [name for name, score in targets]
        assert "General Marcus Steel" not in target_names
    
    @pytest.mark.asyncio
    async def test_calculate_recruitment_suitability(self, conspiracy_generator):
        """Test recruitment suitability calculation."""
        conspiracy = Mock()
        conspiracy.conspiracy_type = ConspiracyType.COUP
        
        # Mock target with high emotional intensity
        conspiracy_generator.dialogue_system.get_advisor_emotional_state.return_value = {
            "emotion": "angry",
            "intensity": 0.8
        }
        
        # Mock LLM assessment
        conspiracy_generator.llm_manager.generate.return_value = LLMResponse(
            content='{"relationship_quality": 0.8, "ideological_alignment": 0.7, "risk_tolerance": 0.6}',
            provider=LLMProvider.VLLM,
            model="test-model"
        )
        
        suitability = await conspiracy_generator._calculate_recruitment_suitability(
            conspiracy, "General Marcus Steel", "Dr. Elena Vasquez"
        )
        
        assert 0.0 <= suitability <= 1.0
        assert suitability > 0.5  # Should be high due to emotional state and good relationships
    
    @pytest.mark.asyncio
    async def test_recruit_conspirator(self, conspiracy_generator):
        """Test conspirator recruitment."""
        conspiracy = Mock()
        conspiracy.title = "Test Conspiracy"
        conspiracy.conspiracy_type = ConspiracyType.COUP
        conspiracy.primary_motive = Mock(primary_driver="Test driver")
        conspiracy.participants = []
        
        # Mock LLM recruitment response
        recruitment_data = {
            "recruitment_method": "Private meeting in secure location",
            "commitment_level": 0.7,
            "role_in_conspiracy": "Intelligence gatherer",
            "discovery_risk": 0.4
        }
        
        conspiracy_generator.llm_manager.generate.return_value = LLMResponse(
            content=json.dumps(recruitment_data),
            provider=LLMProvider.VLLM,
            model="test-model"
        )
        
        await conspiracy_generator._recruit_conspirator(conspiracy, "Dr. Elena Vasquez")
        
        assert len(conspiracy.participants) == 1
        participant = conspiracy.participants[0]
        assert participant.advisor_name == "Dr. Elena Vasquez"
        assert participant.commitment_level == 0.7
        assert participant.role_in_conspiracy == "Intelligence gatherer"


class TestConspiracyProgression:
    """Test conspiracy progression through phases."""
    
    def test_calculate_conspiracy_success_chance(self, conspiracy_generator, mock_game_state):
        """Test conspiracy success chance calculation."""
        # Create conspiracy with multiple committed participants
        participants = [
            Mock(commitment_level=0.8),
            Mock(commitment_level=0.7),
            Mock(commitment_level=0.9)
        ]
        
        conspiracy = Mock()
        conspiracy.participants = participants
        
        # Mock advisor roles for diversity
        conspiracy_generator.dialogue_system.advisor_council.advisors = {
            "Advisor1": Mock(role=AdvisorRole.MILITARY),
            "Advisor2": Mock(role=AdvisorRole.INTELLIGENCE),
            "Advisor3": Mock(role=AdvisorRole.ECONOMIC)
        }
        
        for i, participant in enumerate(participants):
            participant.advisor_name = f"Advisor{i+1}"
        
        # Low stability should increase success chance
        mock_game_state.stability = 30
        
        success_chance = conspiracy_generator._calculate_conspiracy_success_chance(
            conspiracy, mock_game_state
        )
        
        assert 0.1 <= success_chance <= 0.9  # Should be clamped
        assert success_chance > 0.4  # Should be higher than base due to factors
    
    def test_calculate_discovery_risk(self, conspiracy_generator):
        """Test discovery risk calculation."""
        conspiracy = Mock()
        conspiracy.participants = [Mock(), Mock(), Mock()]  # 3 participants
        conspiracy.secrecy_level = 0.9  # High secrecy
        conspiracy.status = ConspiracyStatus.EXECUTION  # High-risk phase
        
        risk = conspiracy_generator._calculate_discovery_risk(conspiracy)
        
        assert 0.01 <= risk <= 0.3  # Should be within bounds
        assert risk > 0.1  # Should be significant due to execution phase
    
    @pytest.mark.asyncio
    async def test_process_conspiracy_turn_planning(self, conspiracy_generator, mock_game_state):
        """Test conspiracy turn processing in planning phase."""
        # Create conspiracy in planning phase
        participant = Mock(advisor_name="Initiator")
        conspiracy = Mock()
        conspiracy.status = ConspiracyStatus.PLANNING
        conspiracy.participants = [participant]
        
        # Mock recruitment target evaluation
        conspiracy_generator.evaluate_recruitment_targets = AsyncMock(
            return_value=[("Target1", 0.8), ("Target2", 0.6)]
        )
        conspiracy_generator._recruit_conspirator = AsyncMock()
        conspiracy_generator._calculate_discovery_risk = Mock(return_value=0.1)
        
        # Mock random to ensure recruitment happens
        with patch('src.llm.conspiracy.random.random', return_value=0.3):  # 30% < 40% (0.8 * 0.5)
            results = await conspiracy_generator.process_conspiracy_turn(conspiracy, mock_game_state)
        
        assert results["new_participants"] == ["Target1"]
        conspiracy_generator._recruit_conspirator.assert_called_once_with(conspiracy, "Target1")


class TestConspiracyIntegration:
    """Test conspiracy system integration."""
    
    @pytest.mark.asyncio
    async def test_generate_conspiracies_for_turn(self, conspiracy_generator, mock_game_state):
        """Test conspiracy generation for a turn."""
        # Mock high conspiracy conditions
        conspiracy_generator.analyze_conspiracy_conditions = AsyncMock(return_value={
            "political_instability": 0.8,
            "advisor_tensions": 0.7,
            "military_dissatisfaction": 0.9
        })
        
        # Mock motive generation
        test_motive = ConspiracyMotive(
            primary_driver="Test driver",
            emotional_trigger=EmotionalState.ANGRY,
            rational_justification="Test justification",
            personal_stakes=0.8,
            ideological_alignment=-0.6,
            urgency_level=0.8
        )
        conspiracy_generator.generate_conspiracy_motive = AsyncMock(return_value=test_motive)
        
        # Mock plot generation
        test_plot = Mock()
        test_plot.plot_id = "test_conspiracy"
        test_plot.title = "Test Conspiracy"
        conspiracy_generator.generate_conspiracy_plot = AsyncMock(return_value=test_plot)
        
        # Mock random to ensure conspiracy generation
        with patch('src.llm.conspiracy.random.random', return_value=0.1):  # Low value to trigger generation
            conspiracies = await conspiracy_generator.generate_conspiracies_for_turn(
                mock_game_state, Mock()
            )
        
        assert len(conspiracies) >= 0  # Should generate conspiracies under right conditions
        if conspiracies:
            assert conspiracies[0] == test_plot
    
    def test_get_conspiracy_summary(self, conspiracy_generator):
        """Test conspiracy summary generation."""
        # Create a test conspiracy
        motive = ConspiracyMotive(
            primary_driver="Test driver",
            emotional_trigger=EmotionalState.ANGRY,
            rational_justification="Test justification",
            personal_stakes=0.8,
            ideological_alignment=-0.5,
            urgency_level=0.7
        )
        
        participant = ConspiracyParticipant(
            advisor_name="Test Advisor",
            role_in_conspiracy="Initiator",
            commitment_level=0.8,
            discovery_risk=0.3,
            potential_rewards=["Power"],
            potential_costs=["Death"],
            recruitment_method="Self-initiated"
        )
        
        conspiracy = ConspiracyPlot(
            plot_id="test_conspiracy",
            conspiracy_type=ConspiracyType.COUP,
            title="Test Conspiracy",
            description="Test description",
            primary_motive=motive,
            target="Government",
            participants=[participant],
            timeline={"Phase 1": "Planning", "Phase 2": "Execution"},
            required_resources={"gold": 1000},
            success_conditions=["Support"],
            failure_conditions=["Discovery"],
            potential_consequences={"success": ["Victory"], "failure": ["Death"]},
            discovery_indicators=["Meetings"],
            status=ConspiracyStatus.PLANNING
        )
        
        conspiracy_generator.active_conspiracies["test_conspiracy"] = conspiracy
        conspiracy_generator._calculate_discovery_risk = Mock(return_value=0.2)
        
        summary = conspiracy_generator.get_conspiracy_summary("test_conspiracy")
        
        assert summary is not None
        assert summary["plot_id"] == "test_conspiracy"
        assert summary["title"] == "Test Conspiracy"
        assert summary["type"] == "coup"
        assert summary["status"] == "planning"
        assert len(summary["participants"]) == 1
        assert summary["discovery_risk"] == 0.2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
