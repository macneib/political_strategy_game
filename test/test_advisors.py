"""
Tests for AI advisor system and personality implementations.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.llm.advisors import (
    AdvisorRole, AdvisorPersonality, ConversationMemory, 
    AdvisorAI, AdvisorCouncil
)
from src.llm.llm_providers import LLMMessage, LLMResponse, LLMProvider


class TestAdvisorPersonality:
    """Test advisor personality data structure."""
    
    def test_personality_creation(self):
        """Test creating advisor personality."""
        personality = AdvisorPersonality(
            name="Test Advisor",
            role=AdvisorRole.MILITARY,
            personality_traits=["Direct", "Strategic"],
            communication_style="Formal military briefing style",
            expertise_areas=["Defense", "Strategy"],
            background="Former general with 20 years experience"
        )
        
        assert personality.name == "Test Advisor"
        assert personality.role == AdvisorRole.MILITARY
        assert "Direct" in personality.personality_traits
        assert personality.expertise_areas == ["Defense", "Strategy"]


class TestConversationMemory:
    """Test conversation memory functionality."""
    
    def test_memory_initialization(self):
        """Test memory initialization."""
        memory = ConversationMemory()
        
        assert len(memory.messages) == 0
        assert len(memory.key_decisions) == 0
        assert memory.last_updated is None
    
    def test_add_message(self):
        """Test adding messages to memory."""
        memory = ConversationMemory()
        
        memory.add_message("user", "Test question")
        memory.add_message("assistant", "Test response")
        
        assert len(memory.messages) == 2
        assert memory.messages[0].role == "user"
        assert memory.messages[0].content == "Test question"
        assert memory.messages[1].role == "assistant"
        assert memory.last_updated is not None
    
    def test_message_limit(self):
        """Test message limit enforcement."""
        memory = ConversationMemory()
        
        # Add more than 20 messages
        for i in range(25):
            memory.add_message("user", f"Message {i}")
        
        # Should keep only last 20
        assert len(memory.messages) == 20
        assert memory.messages[0].content == "Message 5"  # First 5 should be dropped
        assert memory.messages[-1].content == "Message 24"
    
    def test_add_decision(self):
        """Test adding decisions to memory."""
        memory = ConversationMemory()
        
        memory.add_decision("Increase military spending")
        memory.add_decision("Form trade alliance")
        
        assert len(memory.key_decisions) == 2
        assert "Increase military spending" in memory.key_decisions
        assert memory.last_updated is not None
    
    def test_decision_limit(self):
        """Test decision limit enforcement."""
        memory = ConversationMemory()
        
        # Add more than 10 decisions
        for i in range(15):
            memory.add_decision(f"Decision {i}")
        
        # Should keep only last 10
        assert len(memory.key_decisions) == 10
        assert memory.key_decisions[0] == "Decision 5"  # First 5 should be dropped
        assert memory.key_decisions[-1] == "Decision 14"


class TestAdvisorAI:
    """Test AI advisor functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.personality = AdvisorPersonality(
            name="Test Military Advisor",
            role=AdvisorRole.MILITARY,
            personality_traits=["Direct", "Strategic"],
            communication_style="Military briefing style",
            expertise_areas=["Defense", "Strategy"],
            background="Former general"
        )
        
        self.mock_llm_manager = Mock()
    
    def test_advisor_initialization(self):
        """Test advisor AI initialization."""
        advisor = AdvisorAI(self.personality, self.mock_llm_manager)
        
        assert advisor.personality == self.personality
        assert advisor.llm_manager == self.mock_llm_manager
        assert isinstance(advisor.memory, ConversationMemory)
        assert len(advisor.system_prompt) > 0
    
    def test_system_prompt_creation(self):
        """Test system prompt contains personality elements."""
        advisor = AdvisorAI(self.personality, self.mock_llm_manager)
        
        prompt = advisor.system_prompt
        
        assert "Test Military Advisor" in prompt
        assert "military" in prompt.lower()
        assert "Direct, Strategic" in prompt
        assert "Former general" in prompt
    
    async def test_get_advice_success(self, mock_game_state):
        """Test successful advice generation."""
        # Mock successful LLM response
        mock_response = LLMResponse(
            content="Military advice: Strengthen border defenses immediately.",
            provider=LLMProvider.VLLM,
            model="test-model"
        )
        self.mock_llm_manager.generate = AsyncMock(return_value=mock_response)
        
        advisor = AdvisorAI(self.personality, self.mock_llm_manager)
        
        advice = await advisor.get_advice(mock_game_state, "Border security concerns")
        
        assert advice == "Military advice: Strengthen border defenses immediately."
        assert len(advisor.memory.messages) == 2  # user + assistant
    
    async def test_get_advice_llm_failure(self, mock_game_state):
        """Test advice generation when LLM fails."""
        # Mock LLM failure
        mock_response = LLMResponse(
            content="",
            provider=LLMProvider.VLLM,
            model="test-model",
            error="Connection failed"
        )
        self.mock_llm_manager.generate = AsyncMock(return_value=mock_response)
        
        advisor = AdvisorAI(self.personality, self.mock_llm_manager)
        
        advice = await advisor.get_advice(mock_game_state, "Test situation")
        
        # Should get fallback response
        assert "Test Military Advisor:" in advice
        assert len(advice) > 0
    
    async def test_get_advice_exception(self, mock_game_state):
        """Test advice generation when exception occurs."""
        # Mock exception
        self.mock_llm_manager.generate = AsyncMock(side_effect=Exception("Network error"))
        
        advisor = AdvisorAI(self.personality, self.mock_llm_manager)
        
        advice = await advisor.get_advice(mock_game_state, "Test situation")
        
        # Should get fallback response
        assert "Test Military Advisor:" in advice
        assert len(advice) > 0
    
    def test_filter_relevant_events(self):
        """Test filtering events relevant to advisor expertise."""
        advisor = AdvisorAI(self.personality, self.mock_llm_manager)
        
        # Create mock events
        military_event = Mock()
        military_event.title = "Military Border Conflict"
        military_event.description = "Army reports increased activity"
        
        economic_event = Mock()
        economic_event.title = "Trade Agreement Proposal"
        economic_event.description = "Economic partnership opportunity"
        
        mixed_event = Mock()
        mixed_event.title = "Defense Budget Allocation"
        mixed_event.description = "Military spending review needed"
        
        events = [military_event, economic_event, mixed_event]
        
        relevant = advisor._filter_relevant_events(events)
        
        # Military advisor should get military and defense-related events
        assert military_event in relevant
        assert mixed_event in relevant  # Contains "military" and "defense"
        assert economic_event not in relevant
    
    def test_record_decision(self):
        """Test recording player decisions."""
        advisor = AdvisorAI(self.personality, self.mock_llm_manager)
        
        advisor.record_decision("Increase defense spending by 15%")
        
        assert len(advisor.memory.key_decisions) == 1
        assert advisor.memory.key_decisions[0] == "Increase defense spending by 15%"
    
    def test_get_memory_summary(self):
        """Test getting memory summary."""
        advisor = AdvisorAI(self.personality, self.mock_llm_manager)
        
        # Add some memory data
        advisor.memory.add_message("user", "Test question")
        advisor.memory.add_message("assistant", "Test response")
        advisor.record_decision("Test decision")
        
        summary = advisor.get_memory_summary()
        
        assert summary["conversation_length"] == 2
        assert summary["key_decisions"] == 1
        assert summary["last_updated"] is not None
        assert len(summary["recent_decisions"]) == 1


class TestAdvisorCouncil:
    """Test advisor council functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm_manager = Mock()
    
    def test_council_initialization(self):
        """Test council initialization."""
        council = AdvisorCouncil(self.mock_llm_manager)
        
        assert len(council.advisors) == 5  # Default 5 advisors
        assert AdvisorRole.MILITARY in council.advisors
        assert AdvisorRole.ECONOMIC in council.advisors
        assert AdvisorRole.DIPLOMATIC in council.advisors
        assert AdvisorRole.DOMESTIC in council.advisors
        assert AdvisorRole.INTELLIGENCE in council.advisors
    
    def test_advisor_names(self):
        """Test advisor names are set correctly."""
        council = AdvisorCouncil(self.mock_llm_manager)
        
        names = council.get_advisor_names()
        
        assert names[AdvisorRole.MILITARY] == "General Marcus Steel"
        assert names[AdvisorRole.ECONOMIC] == "Dr. Elena Vasquez"
        assert names[AdvisorRole.DIPLOMATIC] == "Ambassador Chen Wei"
        assert names[AdvisorRole.DOMESTIC] == "Minister Sarah Thompson"
        assert names[AdvisorRole.INTELLIGENCE] == "Director Alex Morgan"
    
    async def test_get_single_advice(self, mock_game_state):
        """Test getting advice from single advisor."""
        # Mock successful response
        mock_response = LLMResponse(
            content="Economic analysis: Markets are stable.",
            provider=LLMProvider.VLLM,
            model="test-model"
        )
        self.mock_llm_manager.generate = AsyncMock(return_value=mock_response)
        
        council = AdvisorCouncil(self.mock_llm_manager)
        
        advice = await council.get_single_advice(
            AdvisorRole.ECONOMIC, 
            mock_game_state, 
            "Current market conditions"
        )
        
        assert advice == "Economic analysis: Markets are stable."
    
    async def test_get_single_advice_invalid_role(self, mock_game_state):
        """Test getting advice from invalid advisor role."""
        council = AdvisorCouncil(self.mock_llm_manager)
        
        # Remove an advisor to test invalid role
        del council.advisors[AdvisorRole.MILITARY]
        
        advice = await council.get_single_advice(
            AdvisorRole.MILITARY,
            mock_game_state,
            "Military situation"
        )
        
        assert "No advisor available" in advice
    
    async def test_get_council_advice_all(self, mock_game_state):
        """Test getting advice from all advisors."""
        # Mock successful responses
        mock_response = LLMResponse(
            content="Advisor response",
            provider=LLMProvider.VLLM,
            model="test-model"
        )
        self.mock_llm_manager.generate = AsyncMock(return_value=mock_response)
        
        council = AdvisorCouncil(self.mock_llm_manager)
        
        advice_dict = await council.get_council_advice(
            mock_game_state,
            "National crisis situation"
        )
        
        assert len(advice_dict) == 5  # All 5 advisors
        assert AdvisorRole.MILITARY in advice_dict
        assert AdvisorRole.ECONOMIC in advice_dict
        
        # All should have same mock response
        for advice in advice_dict.values():
            assert advice == "Advisor response"
    
    async def test_get_council_advice_specific_roles(self, mock_game_state):
        """Test getting advice from specific advisors only."""
        mock_response = LLMResponse(
            content="Specific advisor response",
            provider=LLMProvider.VLLM,
            model="test-model"
        )
        self.mock_llm_manager.generate = AsyncMock(return_value=mock_response)
        
        council = AdvisorCouncil(self.mock_llm_manager)
        
        specific_roles = [AdvisorRole.MILITARY, AdvisorRole.DIPLOMATIC]
        advice_dict = await council.get_council_advice(
            mock_game_state,
            "Foreign policy crisis",
            specific_roles=specific_roles
        )
        
        assert len(advice_dict) == 2
        assert AdvisorRole.MILITARY in advice_dict
        assert AdvisorRole.DIPLOMATIC in advice_dict
        assert AdvisorRole.ECONOMIC not in advice_dict
    
    async def test_get_council_advice_with_failure(self, mock_game_state):
        """Test council advice when some advisors fail."""
        # Mock one success and one failure
        call_count = 0
        
        async def mock_generate(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count <= 2:
                return LLMResponse(
                    content="Success response",
                    provider=LLMProvider.VLLM,
                    model="test-model"
                )
            else:
                raise Exception("Advisor failed")
        
        self.mock_llm_manager.generate = mock_generate
        
        council = AdvisorCouncil(self.mock_llm_manager)
        
        # Test with just 3 advisors to control the test
        specific_roles = [AdvisorRole.MILITARY, AdvisorRole.ECONOMIC, AdvisorRole.DIPLOMATIC]
        advice_dict = await council.get_council_advice(
            mock_game_state,
            "Test situation",
            specific_roles=specific_roles
        )
        
        # Should have responses for all roles, even failed ones
        assert len(advice_dict) == 3
        
        # First two should succeed, third should have failure message
        success_count = sum(1 for advice in advice_dict.values() if advice == "Success response")
        failure_count = sum(1 for advice in advice_dict.values() if "unavailable" in advice)
        
        assert success_count == 2
        assert failure_count == 1
    
    def test_record_decision_for_all(self):
        """Test recording decision for all advisors."""
        council = AdvisorCouncil(self.mock_llm_manager)
        
        decision = "Form military alliance with neighboring country"
        council.record_decision_for_all(decision)
        
        # All advisors should have the decision recorded
        for advisor in council.advisors.values():
            assert decision in advisor.memory.key_decisions
    
    def test_get_advisor_status(self):
        """Test getting advisor status."""
        # Mock LLM manager status
        self.mock_llm_manager.get_status.return_value = {
            "primary": {"provider": "vllm", "available": True, "model": "test-model"},
            "fallbacks": []
        }
        
        council = AdvisorCouncil(self.mock_llm_manager)
        
        # Add some memory to advisors
        for advisor in council.advisors.values():
            advisor.memory.add_message("user", "test")
            advisor.record_decision("test decision")
        
        status = council.get_advisor_status()
        
        assert "llm_status" in status
        assert "advisors" in status
        assert len(status["advisors"]) == 5
        
        # Check military advisor specifically
        military_status = status["advisors"]["military"]
        assert military_status["name"] == "General Marcus Steel"
        assert military_status["memory"]["conversation_length"] == 1
        assert military_status["memory"]["key_decisions"] == 1


if __name__ == "__main__":
    # Run tests with asyncio support
    pytest.main([__file__, "-v", "--tb=short"])
