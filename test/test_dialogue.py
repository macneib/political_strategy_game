"""
Tests for Advanced Multi-Advisor Dialogue System

This module tests the sophisticated advisor-to-advisor interactions,
emotional modeling, and dialogue management capabilities.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.llm.dialogue import (
    MultiAdvisorDialogue, AdvisorEmotionalModel, DialogueContext, DialogueSession,
    DialogueTurn, DialogueType, EmotionalState
)
from src.llm.advisors import AdvisorRole, AdvisorCouncil, AdvisorAI, AdvisorPersonality
from src.llm.llm_providers import LLMManager, LLMResponse, LLMProvider


class TestAdvisorEmotionalModel:
    """Test advisor emotional state modeling."""
    
    def test_emotional_model_initialization(self):
        """Test emotional model initialization."""
        model = AdvisorEmotionalModel("General Steel")
        
        assert model.advisor_name == "General Steel"
        assert model.current_emotion == EmotionalState.CALM
        assert model.emotion_intensity == 0.5
        assert len(model.emotion_history) == 0
    
    def test_emotion_update(self):
        """Test emotion state updates."""
        model = AdvisorEmotionalModel("Dr. Vasquez")
        
        # Update emotion
        model.update_emotion(EmotionalState.WORRIED, 0.8, "Economic crisis")
        
        assert model.current_emotion == EmotionalState.WORRIED
        assert model.emotion_intensity == 0.8
        assert len(model.emotion_history) == 1
        
        # Check emotion history
        prev_emotion, prev_intensity, timestamp = model.emotion_history[0]
        assert prev_emotion == EmotionalState.CALM
        assert prev_intensity == 0.5
    
    def test_emotion_modifiers(self):
        """Test emotion-based behavioral modifiers."""
        model = AdvisorEmotionalModel("Ambassador Chen")
        
        # Test angry emotion modifiers
        model.update_emotion(EmotionalState.ANGRY, 1.0, "Diplomatic insult")
        modifiers = model.get_emotion_modifier()
        
        assert modifiers["aggression"] > 0.5
        assert modifiers["cooperation"] < 0
        assert modifiers["suspicion"] > 0
    
    def test_emotional_contagion(self):
        """Test emotional contagion between advisors."""
        model = AdvisorEmotionalModel("Minister Thompson")
        initial_emotion = model.current_emotion
        
        # Test contagion from angry advisor
        model.emotional_contagion(EmotionalState.ANGRY, 0.8)  # Strong relationship
        
        # Should have some effect due to strong relationship
        assert model.emotion_intensity != 0.5 or model.current_emotion != initial_emotion


class TestDialogueStructures:
    """Test dialogue data structures."""
    
    def test_dialogue_context_creation(self):
        """Test dialogue context initialization."""
        context = DialogueContext(
            dialogue_type=DialogueType.COUNCIL_MEETING,
            topic="Budget allocation",
            participants=["General Steel", "Dr. Vasquez"],
            game_state=Mock(political_power=85, stability=70)
        )
        
        assert context.dialogue_type == DialogueType.COUNCIL_MEETING
        assert context.topic == "Budget allocation"
        assert len(context.participants) == 2
        assert context.turn_number == 1
        assert context.max_turns == 10
    
    def test_dialogue_turn_creation(self):
        """Test dialogue turn structure."""
        turn = DialogueTurn(
            speaker="General Steel",
            content="We must increase military spending immediately.",
            turn_number=1,
            emotional_tone=EmotionalState.CONFIDENT
        )
        
        assert turn.speaker == "General Steel"
        assert "military spending" in turn.content
        assert turn.emotional_tone == EmotionalState.CONFIDENT
        assert isinstance(turn.timestamp, datetime)
    
    def test_dialogue_session_management(self):
        """Test dialogue session operations."""
        context = DialogueContext(
            dialogue_type=DialogueType.PRIVATE_CONVERSATION,
            topic="Alliance discussion",
            participants=["Dr. Vasquez", "Ambassador Chen"],
            game_state=Mock(),
            max_turns=5
        )
        
        session = DialogueSession("test_session", context)
        
        # Add turns and check completion
        for i in range(5):
            turn = DialogueTurn(
                speaker=context.participants[i % 2],
                content=f"Response {i+1}",
                turn_number=i+1
            )
            session.add_turn(turn)
        
        assert session.completed
        assert len(session.turns) == 5
    
    def test_conversation_history(self):
        """Test conversation history formatting."""
        context = DialogueContext(
            dialogue_type=DialogueType.COUNCIL_MEETING,
            topic="Test topic",
            participants=["Speaker1", "Speaker2"],
            game_state=Mock()
        )
        
        session = DialogueSession("test", context)
        
        # Add some turns
        turn1 = DialogueTurn("Speaker1", "First message", 1, emotional_tone=EmotionalState.CONFIDENT)
        turn2 = DialogueTurn("Speaker2", "Second message", 2, emotional_tone=EmotionalState.WORRIED)
        
        session.add_turn(turn1)
        session.add_turn(turn2)
        
        history = session.get_conversation_history()
        
        assert "Speaker1 [confident]: First message" in history
        assert "Speaker2 [worried]: Second message" in history


@pytest.fixture
def mock_llm_manager():
    """Create a mock LLM manager for testing."""
    manager = Mock(spec=LLMManager)
    manager.generate = AsyncMock()
    return manager


@pytest.fixture
def mock_advisor_council():
    """Create a mock advisor council for testing."""
    council = Mock(spec=AdvisorCouncil)
    
    # Create mock advisors
    advisors = {}
    advisor_roles = [AdvisorRole.MILITARY, AdvisorRole.ECONOMIC, AdvisorRole.DIPLOMATIC]
    
    for role in advisor_roles:
        personality = AdvisorPersonality.get_personality(role)
        advisor = Mock(spec=AdvisorAI)
        advisor.role = role
        advisor.personality = personality
        advisors[personality.name] = advisor
    
    council.advisors = advisors
    return council


@pytest.fixture
def mock_game_state():
    """Create a mock game state for testing."""
    return Mock(
        political_power=100,
        stability=75,
        legitimacy=80,
        current_faction=None
    )


class TestMultiAdvisorDialogue:
    """Test the main multi-advisor dialogue system."""
    
    @pytest.fixture
    def dialogue_system(self, mock_llm_manager, mock_advisor_council):
        """Create a dialogue system for testing."""
        return MultiAdvisorDialogue(mock_llm_manager, mock_advisor_council)
    
    def test_dialogue_system_initialization(self, dialogue_system, mock_advisor_council):
        """Test dialogue system initialization."""
        assert dialogue_system.llm_manager is not None
        assert dialogue_system.advisor_council == mock_advisor_council
        assert len(dialogue_system.active_dialogues) == 0
        assert len(dialogue_system.emotional_models) == len(mock_advisor_council.advisors)
    
    @pytest.mark.asyncio
    async def test_council_meeting_initiation(self, dialogue_system, mock_game_state):
        """Test initiating a council meeting."""
        # Mock LLM responses
        dialogue_system.llm_manager.generate.return_value = LLMResponse(
            content="I believe we should focus on economic stability first.",
            provider=LLMProvider.VLLM,
            model="test-model"
        )
        
        topic = "Budget allocation for next quarter"
        session = await dialogue_system.initiate_council_meeting(topic, mock_game_state)
        
        assert session is not None
        assert session.context.dialogue_type == DialogueType.COUNCIL_MEETING
        assert session.context.topic == topic
        assert session.dialogue_id in dialogue_system.active_dialogues
        assert session.completed
    
    @pytest.mark.asyncio
    async def test_private_conversation(self, dialogue_system, mock_game_state):
        """Test private conversation between two advisors."""
        # Mock LLM responses
        dialogue_system.llm_manager.generate.return_value = LLMResponse(
            content="I agree with your assessment of the situation.",
            provider=LLMProvider.VLLM,
            model="test-model"
        )
        
        participant1 = "General Marcus Steel"
        participant2 = "Dr. Elena Vasquez"
        topic = "Military budget concerns"
        
        session = await dialogue_system.initiate_private_conversation(
            participant1, participant2, topic, mock_game_state
        )
        
        assert session is not None
        assert session.context.dialogue_type == DialogueType.PRIVATE_CONVERSATION
        assert len(session.context.participants) == 2
        assert participant1 in session.context.participants
        assert participant2 in session.context.participants
    
    def test_emotional_state_retrieval(self, dialogue_system):
        """Test retrieving advisor emotional states."""
        advisor_name = list(dialogue_system.emotional_models.keys())[0]
        
        # Update emotion
        dialogue_system.emotional_models[advisor_name].update_emotion(
            EmotionalState.CONFIDENT, 0.8, "Test update"
        )
        
        state = dialogue_system.get_advisor_emotional_state(advisor_name)
        
        assert state["emotion"] == "confident"
        assert state["intensity"] == 0.8
        assert "modifiers" in state
    
    def test_dialogue_prompt_building(self, dialogue_system, mock_game_state):
        """Test dialogue prompt construction."""
        # Create a test session
        context = DialogueContext(
            dialogue_type=DialogueType.COUNCIL_MEETING,
            topic="Military expansion",
            participants=["General Marcus Steel"],
            game_state=mock_game_state
        )
        
        session = DialogueSession("test", context)
        
        # Add some conversation history
        turn = DialogueTurn("Dr. Elena Vasquez", "We cannot afford this expansion", 1)
        session.add_turn(turn)
        
        advisor_name = "General Marcus Steel"
        emotion_modifiers = {"aggression": 0.2, "confidence": 0.8}
        
        prompt = dialogue_system._build_dialogue_prompt(session, advisor_name, emotion_modifiers)
        
        assert advisor_name in prompt
        assert "Military expansion" in prompt
        assert "cannot afford this expansion" in prompt
        assert "confidence" in prompt or "aggression" in prompt
    
    def test_emotional_tone_analysis(self, dialogue_system):
        """Test emotional tone analysis from responses."""
        test_cases = [
            ("I am absolutely furious about this decision!", EmotionalState.ANGRY),
            ("I'm quite worried about the economic implications.", EmotionalState.WORRIED),
            ("This seems suspicious to me.", EmotionalState.SUSPICIOUS),
            ("I'm confident this will work perfectly.", EmotionalState.CONFIDENT),
            ("This is a normal statement.", EmotionalState.CALM)
        ]
        
        for response, expected_emotion in test_cases:
            analyzed_emotion = dialogue_system._analyze_emotional_tone(response)
            if expected_emotion != EmotionalState.CALM:
                assert analyzed_emotion == expected_emotion
    
    def test_relationship_change_calculation(self, dialogue_system, mock_game_state):
        """Test relationship change calculation from dialogue."""
        context = DialogueContext(
            dialogue_type=DialogueType.COUNCIL_MEETING,
            topic="Test topic",
            participants=["Advisor1", "Advisor2"],
            game_state=mock_game_state
        )
        
        session = DialogueSession("test", context)
        
        # Add supportive turn
        turn1 = DialogueTurn("Advisor1", "I completely agree with Advisor2's assessment", 1)
        session.add_turn(turn1)
        
        # Add critical turn
        turn2 = DialogueTurn("Advisor1", "Advisor2 is completely wrong about this", 2)
        session.add_turn(turn2)
        
        change = dialogue_system._calculate_relationship_change(session, "Advisor1", "Advisor2")
        
        # Should be neutral or slightly negative due to mixed messages
        assert -0.5 <= change <= 0.5
    
    def test_consensus_analysis(self, dialogue_system, mock_game_state):
        """Test consensus detection in dialogue."""
        context = DialogueContext(
            dialogue_type=DialogueType.COUNCIL_MEETING,
            topic="Test consensus",
            participants=["Advisor1", "Advisor2"],
            game_state=mock_game_state
        )
        
        session = DialogueSession("test", context)
        
        # Add agreeable turns
        turn1 = DialogueTurn("Advisor1", "I agree with this proposal", 1)
        turn2 = DialogueTurn("Advisor2", "Yes, we have reached consensus", 2)
        
        session.add_turn(turn1)
        session.add_turn(turn2)
        
        consensus = dialogue_system._analyze_consensus(session)
        assert consensus is True
    
    def test_dialogue_summary(self, dialogue_system, mock_game_state):
        """Test dialogue summary generation."""
        context = DialogueContext(
            dialogue_type=DialogueType.PRIVATE_CONVERSATION,
            topic="Test summary",
            participants=["Advisor1", "Advisor2"],
            game_state=mock_game_state
        )
        
        session = DialogueSession("test_summary", context)
        session.completed = True
        session.outcomes = {"consensus_reached": True}
        dialogue_system.active_dialogues["test_summary"] = session
        
        summary = dialogue_system.get_dialogue_summary("test_summary")
        
        assert summary is not None
        assert summary["dialogue_id"] == "test_summary"
        assert summary["type"] == "private_conversation"
        assert summary["topic"] == "Test summary"
        assert summary["completed"] is True


class TestDialogueIntegration:
    """Test integration with existing advisor systems."""
    
    @pytest.mark.asyncio
    async def test_integration_with_advisor_council(self, mock_llm_manager):
        """Test integration with real advisor council structure."""
        # Create a more realistic advisor council setup
        advisors = {}
        for role in [AdvisorRole.MILITARY, AdvisorRole.ECONOMIC]:
            personality = AdvisorPersonality.get_personality(role)
            advisor = Mock(spec=AdvisorAI)
            advisor.role = role
            advisor.personality = personality
            advisors[personality.name] = advisor
        
        council = Mock(spec=AdvisorCouncil)
        council.advisors = advisors
        
        # Mock LLM responses
        mock_llm_manager.generate.return_value = LLMResponse(
            content="We need to balance military and economic priorities.",
            provider=LLMProvider.VLLM,
            model="test-model"
        )
        
        dialogue_system = MultiAdvisorDialogue(mock_llm_manager, council)
        
        # Test that emotional models are created for all advisors
        assert len(dialogue_system.emotional_models) == len(advisors)
        
        # Test council meeting with real advisor names
        game_state = Mock(political_power=90, stability=80)
        session = await dialogue_system.initiate_council_meeting(
            "Resource allocation", game_state
        )
        
        assert session is not None
        assert session.completed
    
    def test_emotional_model_persistence(self, mock_llm_manager, mock_advisor_council):
        """Test that emotional models persist across dialogue sessions."""
        dialogue_system = MultiAdvisorDialogue(mock_llm_manager, mock_advisor_council)
        
        advisor_name = list(dialogue_system.emotional_models.keys())[0]
        
        # Update emotion
        original_emotion = EmotionalState.WORRIED
        dialogue_system.emotional_models[advisor_name].update_emotion(
            original_emotion, 0.9, "Test persistence"
        )
        
        # Check that emotion persists
        state = dialogue_system.get_advisor_emotional_state(advisor_name)
        assert state["emotion"] == original_emotion.value
        assert state["intensity"] == 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
