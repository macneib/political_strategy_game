"""
Tests for AI Advisor System
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.llm.advisors import (
    AdvisorRole, AdvisorPersonality, ConversationMemory, 
    AdvisorAI, AdvisorCouncil
)
from src.llm.llm_providers import LLMManager, LLMConfig, LLMProvider, LLMResponse


class MockGameState:
    """Mock game state for testing."""
    def __init__(self):
        self.political_power = 75
        self.stability = 60
        self.current_faction = None


class MockEvent:
    """Mock event for testing."""
    def __init__(self, title, description, event_type="random"):
        self.title = title
        self.description = description
        self.type = event_type


class TestAdvisorPersonality:
    """Test advisor personality definition."""
    
    def test_create_personality(self):
        """Test creating advisor personality."""
        personality = AdvisorPersonality(
            name="Test Advisor",
            role=AdvisorRole.MILITARY,
            personality_traits=["Direct", "Strategic"],
            communication_style="Military precision",
            expertise_areas=["Defense", "Strategy"],
            background="Former general"
        )
        
        assert personality.name == "Test Advisor"
        assert personality.role == AdvisorRole.MILITARY
        assert len(personality.personality_traits) == 2
        assert "Defense" in personality.expertise_areas


class TestConversationMemory:
    """Test conversation memory management."""
    
    def test_add_message(self):
        """Test adding messages to memory."""
        memory = ConversationMemory()
        memory.add_message("user", "Test message")
        
        assert len(memory.messages) == 1
        assert memory.messages[0].role == "user"
        assert memory.messages[0].content == "Test message"
        assert memory.last_updated is not None
    
    def test_message_limit(self):
        """Test message limit enforcement."""
        memory = ConversationMemory()
        
        # Add more than 20 messages
        for i in range(25):
            memory.add_message("user", f"Message {i}")
        
        # Should keep only last 20
        assert len(memory.messages) == 20
        assert memory.messages[0].content == "Message 5"
        assert memory.messages[-1].content == "Message 24"
    
    def test_add_decision(self):
        """Test adding decisions to memory."""
        memory = ConversationMemory()
        memory.add_decision("Increase military spending")
        
        assert len(memory.key_decisions) == 1
        assert memory.key_decisions[0] == "Increase military spending"
    
    def test_decision_limit(self):
        """Test decision limit enforcement."""
        memory = ConversationMemory()
        
        # Add more than 10 decisions
        for i in range(15):
            memory.add_decision(f"Decision {i}")
        
        # Should keep only last 10
        assert len(memory.key_decisions) == 10
        assert memory.key_decisions[0] == "Decision 5"


class TestAdvisorAI:
    """Test AI advisor functionality."""
    
    def create_mock_llm_manager(self, response_content="Test advice"):
        """Create a mock LLM manager."""
        mock_manager = Mock(spec=LLMManager)
        mock_response = LLMResponse(
            content=response_content,
            provider=LLMProvider.VLLM,
            model="test-model"
        )
        mock_manager.generate = AsyncMock(return_value=mock_response)
        return mock_manager
    
    def test_create_advisor(self):
        """Test creating an AI advisor."""
        personality = AdvisorPersonality(
            name="Test Military Advisor",
            role=AdvisorRole.MILITARY,
            personality_traits=["Strategic"],
            communication_style="Direct",
            expertise_areas=["Defense"],
            background="Military veteran"
        )
        
        mock_llm = self.create_mock_llm_manager()
        advisor = AdvisorAI(personality, mock_llm)
        
        assert advisor.personality.name == "Test Military Advisor"
        assert advisor.personality.role == AdvisorRole.MILITARY
        assert "strategic" in advisor.system_prompt.lower()
    
    def test_system_prompt_creation(self):
        """Test system prompt generation."""
        personality = AdvisorPersonality(
            name="Economic Advisor",
            role=AdvisorRole.ECONOMIC,
            personality_traits=["Analytical", "Data-driven"],
            communication_style="Precise with economic terminology",
            expertise_areas=["Trade", "Budget"],
            background="Former economics professor",
            catchphrases=["Numbers don't lie"]
        )
        
        mock_llm = self.create_mock_llm_manager()
        advisor = AdvisorAI(personality, mock_llm)
        
        prompt = advisor.system_prompt
        assert "Economic Advisor" in prompt
        assert "economic" in prompt.lower()
        assert "Analytical" in prompt
        assert "Numbers don't lie" in prompt
    
    @pytest.mark.asyncio
    async def test_get_advice(self):
        """Test getting advice from advisor."""
        personality = AdvisorPersonality(
            name="Test Advisor",
            role=AdvisorRole.DIPLOMATIC,
            personality_traits=["Patient"],
            communication_style="Diplomatic",
            expertise_areas=["Negotiation"],
            background="Career diplomat"
        )
        
        mock_llm = self.create_mock_llm_manager("We should pursue peaceful negotiations.")
        advisor = AdvisorAI(personality, mock_llm)
        
        game_state = MockGameState()
        advice = await advisor.get_advice(game_state, "Border dispute with neighbor")
        
        assert advice == "We should pursue peaceful negotiations."
        assert len(advisor.memory.messages) == 2  # User + assistant
    
    @pytest.mark.asyncio
    async def test_get_advice_with_error(self):
        """Test fallback when LLM fails."""
        personality = AdvisorPersonality(
            name="Test Advisor",
            role=AdvisorRole.MILITARY,
            personality_traits=["Direct"],
            communication_style="Military",
            expertise_areas=["Defense"],
            background="General"
        )
        
        mock_llm = Mock(spec=LLMManager)
        mock_response = LLMResponse(
            content="",
            provider=LLMProvider.VLLM,
            model="test",
            error="Connection failed"
        )
        mock_llm.generate = AsyncMock(return_value=mock_response)
        
        advisor = AdvisorAI(personality, mock_llm)
        game_state = MockGameState()
        advice = await advisor.get_advice(game_state, "Military crisis")
        
        # Should return fallback response
        assert "Test Advisor:" in advice
        assert len(advice) > 0
    
    def test_filter_relevant_events(self):
        """Test filtering events by advisor expertise."""
        personality = AdvisorPersonality(
            name="Military Advisor",
            role=AdvisorRole.MILITARY,
            personality_traits=["Strategic"],
            communication_style="Direct",
            expertise_areas=["Defense"],
            background="General"
        )
        
        mock_llm = self.create_mock_llm_manager()
        advisor = AdvisorAI(personality, mock_llm)
        
        events = [
            MockEvent("Military Exercise", "Annual military training", "military"),
            MockEvent("Trade Agreement", "New trade deal proposed", "economic"),
            MockEvent("Border Conflict", "Skirmish at border", "military"),
            MockEvent("Cultural Festival", "City celebrates heritage", "cultural")
        ]
        
        relevant = advisor._filter_relevant_events(events)
        
        # Should filter military-related events
        assert len(relevant) == 2
        assert all("military" in event.description.lower() or "border" in event.title.lower() 
                  for event in relevant)
    
    def test_record_decision(self):
        """Test recording player decisions."""
        personality = AdvisorPersonality(
            name="Test Advisor",
            role=AdvisorRole.ECONOMIC,
            personality_traits=["Analytical"],
            communication_style="Data-driven",
            expertise_areas=["Economics"],
            background="Economist"
        )
        
        mock_llm = self.create_mock_llm_manager()
        advisor = AdvisorAI(personality, mock_llm)
        
        advisor.record_decision("Increase trade tariffs")
        
        assert len(advisor.memory.key_decisions) == 1
        assert advisor.memory.key_decisions[0] == "Increase trade tariffs"
    
    def test_get_memory_summary(self):
        """Test getting memory summary."""
        personality = AdvisorPersonality(
            name="Test Advisor",
            role=AdvisorRole.DOMESTIC,
            personality_traits=["Empathetic"],
            communication_style="Caring",
            expertise_areas=["Social policy"],
            background="Former mayor"
        )
        
        mock_llm = self.create_mock_llm_manager()
        advisor = AdvisorAI(personality, mock_llm)
        
        # Add some memory
        advisor.memory.add_message("user", "Test message")
        advisor.record_decision("Test decision")
        
        summary = advisor.get_memory_summary()
        
        assert summary["conversation_length"] == 1
        assert summary["key_decisions"] == 1
        assert len(summary["recent_decisions"]) == 1


class TestAdvisorCouncil:
    """Test advisor council management."""
    
    def create_mock_llm_manager(self):
        """Create mock LLM manager for testing."""
        mock_manager = Mock(spec=LLMManager)
        mock_manager.get_status.return_value = {
            "primary": {"provider": "vllm", "available": True, "model": "test"},
            "fallbacks": []
        }
        return mock_manager
    
    def test_create_council(self):
        """Test creating advisor council."""
        mock_llm = self.create_mock_llm_manager()
        council = AdvisorCouncil(mock_llm)
        
        # Should have all default advisors
        assert len(council.advisors) == 5
        assert AdvisorRole.MILITARY in council.advisors
        assert AdvisorRole.ECONOMIC in council.advisors
        assert AdvisorRole.DIPLOMATIC in council.advisors
        assert AdvisorRole.DOMESTIC in council.advisors
        assert AdvisorRole.INTELLIGENCE in council.advisors
    
    def test_get_advisor_names(self):
        """Test getting advisor names."""
        mock_llm = self.create_mock_llm_manager()
        council = AdvisorCouncil(mock_llm)
        
        names = council.get_advisor_names()
        
        assert len(names) == 5
        assert AdvisorRole.MILITARY in names
        assert "Marcus" in names[AdvisorRole.MILITARY]
    
    @pytest.mark.asyncio
    async def test_get_single_advice(self):
        """Test getting advice from single advisor."""
        mock_llm = self.create_mock_llm_manager()
        
        # Mock the advisor's get_advice method
        with patch.object(AdvisorAI, 'get_advice', new_callable=AsyncMock) as mock_advice:
            mock_advice.return_value = "Military recommendation"
            
            council = AdvisorCouncil(mock_llm)
            game_state = MockGameState()
            
            advice = await council.get_single_advice(
                AdvisorRole.MILITARY, game_state, "Security situation"
            )
            
            assert advice == "Military recommendation"
            mock_advice.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_council_advice(self):
        """Test getting advice from multiple advisors."""
        mock_llm = self.create_mock_llm_manager()
        
        # Mock advisor advice generation
        with patch.object(AdvisorAI, 'get_advice', new_callable=AsyncMock) as mock_advice:
            mock_advice.return_value = "Test advice"
            
            council = AdvisorCouncil(mock_llm)
            game_state = MockGameState()
            
            # Get advice from specific roles
            advice_dict = await council.get_council_advice(
                game_state, 
                "Crisis situation",
                specific_roles=[AdvisorRole.MILITARY, AdvisorRole.ECONOMIC]
            )
            
            assert len(advice_dict) == 2
            assert AdvisorRole.MILITARY in advice_dict
            assert AdvisorRole.ECONOMIC in advice_dict
            assert advice_dict[AdvisorRole.MILITARY] == "Test advice"
    
    def test_record_decision_for_all(self):
        """Test recording decision across all advisors."""
        mock_llm = self.create_mock_llm_manager()
        council = AdvisorCouncil(mock_llm)
        
        decision = "Implement new policy"
        council.record_decision_for_all(decision)
        
        # Check that all advisors recorded the decision
        for advisor in council.advisors.values():
            assert decision in advisor.memory.key_decisions
    
    def test_get_advisor_status(self):
        """Test getting status of all advisors."""
        mock_llm = self.create_mock_llm_manager()
        council = AdvisorCouncil(mock_llm)
        
        status = council.get_advisor_status()
        
        assert "llm_status" in status
        assert "advisors" in status
        assert len(status["advisors"]) == 5
        
        # Check that each advisor has expected status fields
        for role_name, advisor_status in status["advisors"].items():
            assert "name" in advisor_status
            assert "memory" in advisor_status
