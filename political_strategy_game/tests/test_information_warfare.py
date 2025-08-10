"""
Tests for the Information Warfare system.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from src.llm.information_warfare import (
    InformationWarfareManager, PropagandaMessage, PropagandaCampaign,
    PropagandaType, PropagandaTarget, InformationSourceProfile, CredibilityLevel,
    InformationSource as InfoSourceEnum
)
from src.llm.dialogue import EmotionalState
from src.llm.llm_providers import LLMMessage, LLMResponse, LLMProvider


class TestPropagandaMessage:
    def test_message_creation(self):
        """Test creating a propaganda message."""
        message = PropagandaMessage(
            message_id="test_001",
            content="Test propaganda message",
            propaganda_type=PropagandaType.LEGITIMACY_BUILDING,
            target_audience=PropagandaTarget.GENERAL_POPULATION,
            emotional_appeal=EmotionalState.CONFIDENT,
            key_themes=["Unity", "Progress"],
            factual_basis=0.7,
            emotional_intensity=0.6,
            sophistication_level=0.5
        )
        
        assert message.message_id == "test_001"
        assert message.propaganda_type == PropagandaType.LEGITIMACY_BUILDING
        assert message.target_audience == PropagandaTarget.GENERAL_POPULATION
        assert message.emotional_appeal == EmotionalState.CONFIDENT
        assert "Unity" in message.key_themes
        assert message.factual_basis == 0.7
    
    def test_effectiveness_calculation(self):
        """Test calculating message effectiveness."""
        message = PropagandaMessage(
            message_id="test_001",
            content="Test message",
            propaganda_type=PropagandaType.LEGITIMACY_BUILDING,
            target_audience=PropagandaTarget.GENERAL_POPULATION,
            emotional_appeal=EmotionalState.CONFIDENT,
            factual_basis=0.8,
            sophistication_level=0.6
        )
        
        target_state = {
            "current_mood": "confident",
            "education_level": 0.6
        }
        
        effectiveness = message.calculate_effectiveness(target_state)
        assert 0.0 <= effectiveness <= 1.0
        
        # Should be higher with mood alignment
        assert effectiveness > 0.5


class TestPropagandaCampaign:
    def test_campaign_creation(self):
        """Test creating a propaganda campaign."""
        campaign = PropagandaCampaign(
            campaign_id="camp_001",
            name="Unity Campaign",
            orchestrator="General",
            objective="Build national unity",
            target_audience=PropagandaTarget.GENERAL_POPULATION,
            duration_turns=5
        )
        
        assert campaign.campaign_id == "camp_001"
        assert campaign.name == "Unity Campaign"
        assert campaign.orchestrator == "General"
        assert campaign.is_active()
    
    def test_adding_messages(self):
        """Test adding messages to campaign."""
        campaign = PropagandaCampaign(
            campaign_id="camp_001",
            name="Test Campaign",
            orchestrator="General",
            objective="Test objective",
            target_audience=PropagandaTarget.GENERAL_POPULATION
        )
        
        message = PropagandaMessage(
            message_id="msg_001",
            content="Test message",
            propaganda_type=PropagandaType.LEGITIMACY_BUILDING,
            target_audience=PropagandaTarget.GENERAL_POPULATION,
            emotional_appeal=EmotionalState.CONFIDENT
        )
        
        campaign.add_message(message)
        assert len(campaign.messages) == 1
        assert campaign.current_effectiveness > 0


class TestInformationSource:
    def test_source_creation(self):
        """Test creating an information source."""
        source = InformationSourceProfile(
            source_id="test_source",
            name="Test News Network",
            source_type=InfoSourceEnum.MERCHANT_NETWORKS,
            credibility=CredibilityLevel.CREDIBLE,
            bias_indicators=["Economic interests"]
        )
        
        assert source.source_id == "test_source"
        assert source.name == "Test News Network"
        assert source.credibility == CredibilityLevel.CREDIBLE
        assert "Economic interests" in source.bias_indicators
    
    def test_credibility_updates(self):
        """Test updating source credibility based on accuracy."""
        source = InformationSourceProfile(
            source_id="test_source",
            name="Test Source",
            source_type=InfoSourceEnum.POPULAR_RUMORS,
            credibility=CredibilityLevel.QUESTIONABLE
        )
        
        # Add several accurate claims
        for i in range(10):
            source.update_credibility(f"claim_{i}", True)
        
        assert source.credibility == CredibilityLevel.HIGHLY_CREDIBLE
        
        # Add several false claims
        for i in range(10):
            source.update_credibility(f"false_claim_{i}", False)
        
        assert source.credibility == CredibilityLevel.KNOWN_MISINFORMATION


class TestInformationWarfareManager:
    @pytest.fixture
    def mock_llm_manager(self):
        """Create a mock LLM manager."""
        llm_manager = Mock()
        llm_manager.generate = AsyncMock()
        return llm_manager
    
    @pytest.fixture
    def mock_dialogue_system(self):
        """Create a mock dialogue system."""
        dialogue_system = Mock()
        dialogue_system.advisor_council = Mock()
        dialogue_system.advisor_council.advisors = {
            "General": Mock(),
            "Diplomat": Mock(),
            "Spymaster": Mock()
        }
        dialogue_system.get_advisor_emotional_state = Mock(return_value={
            "emotion": "calm",
            "intensity": 0.5
        })
        return dialogue_system
    
    @pytest.fixture
    def warfare_manager(self, mock_llm_manager, mock_dialogue_system):
        """Create an information warfare manager."""
        return InformationWarfareManager(
            llm_manager=mock_llm_manager,
            dialogue_system=mock_dialogue_system
        )
    
    def test_initialization(self, warfare_manager):
        """Test manager initialization."""
        assert len(warfare_manager.information_sources) >= 4  # Default sources
        assert "official_proclamations" in warfare_manager.information_sources
        assert "merchant_gossip" in warfare_manager.information_sources
        assert warfare_manager.public_opinion is not None
        assert warfare_manager.narrative_themes is not None
    
    @pytest.mark.asyncio
    async def test_analyze_propaganda_opportunities(self, warfare_manager):
        """Test analyzing propaganda opportunities."""
        # Mock game state
        game_state = Mock()
        game_state.stability = 60
        game_state.legitimacy = 70
        game_state.political_power = 80
        
        # Mock LLM response
        warfare_manager.llm_manager.generate.return_value = LLMResponse(
            content='{"external_threats": 0.3, "economic_concerns": 0.4}',
            provider=LLMProvider.OPENAI,
            model="mock-model",
            usage={'input_tokens': 100, 'output_tokens': 50}
        )
        
        opportunities = await warfare_manager.analyze_propaganda_opportunities(game_state, "General")
        
        assert "political_instability" in opportunities
        assert "legitimacy_crisis" in opportunities
        assert "social_unrest" in opportunities
        assert opportunities["political_instability"] > 0  # Based on low stability
        assert 0.0 <= opportunities["political_instability"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_generate_propaganda_message(self, warfare_manager):
        """Test generating propaganda messages."""
        # Mock LLM response
        message_json = {
            "content": "Citizens unite for our glorious nation!",
            "propaganda_type": "unity_promotion",
            "emotional_appeal": "confident",
            "key_themes": ["Unity", "National Pride"],
            "factual_basis": 0.6,
            "emotional_intensity": 0.8,
            "sophistication_level": 0.5
        }
        
        warfare_manager.llm_manager.generate.return_value = LLMResponse(
            content=str(message_json).replace("'", '"'),
            provider=LLMProvider.OPENAI,
            model="mock-model",
            usage={'input_tokens': 200, 'output_tokens': 100}
        )
        
        message = await warfare_manager.generate_propaganda_message(
            campaign_objective="Build national unity",
            target_audience=PropagandaTarget.GENERAL_POPULATION,
            orchestrator="General",
            current_context={}
        )
        
        assert message.content is not None
        assert message.propaganda_type in PropagandaType
        assert message.target_audience == PropagandaTarget.GENERAL_POPULATION
        assert message.emotional_appeal in EmotionalState
        assert len(message.key_themes) >= 0
        assert 0.0 <= message.factual_basis <= 1.0
        assert 0.0 <= message.emotional_intensity <= 1.0
        assert 0.0 <= message.sophistication_level <= 1.0
    
    @pytest.mark.asyncio
    async def test_launch_propaganda_campaign(self, warfare_manager):
        """Test launching a propaganda campaign."""
        # Mock LLM responses
        warfare_manager.llm_manager.generate.side_effect = [
            # Opportunities analysis
            LLMResponse(
                content='{"external_threats": 0.2, "economic_concerns": 0.3}',
                provider=LLMProvider.OPENAI,
                model="mock-model",
                usage={'input_tokens': 100, 'output_tokens': 30}
            ),
            # Campaign name generation
            LLMResponse(
                content='National Unity Initiative',
                provider=LLMProvider.OPENAI,
                model="mock-model",
                usage={'input_tokens': 50, 'output_tokens': 10}
            ),
            # First message
            LLMResponse(
                content='{"content": "Message 1", "propaganda_type": "unity_promotion", "emotional_appeal": "confident", "key_themes": ["Unity"], "factual_basis": 0.7, "emotional_intensity": 0.6, "sophistication_level": 0.5}',
                provider=LLMProvider.OPENAI,
                model="mock-model",
                usage={'input_tokens': 200, 'output_tokens': 80}
            ),
            # Second message
            LLMResponse(
                content='{"content": "Message 2", "propaganda_type": "legitimacy_building", "emotional_appeal": "determined", "key_themes": ["Leadership"], "factual_basis": 0.8, "emotional_intensity": 0.5, "sophistication_level": 0.6}',
                provider=LLMProvider.OPENAI,
                model="mock-model",
                usage={'input_tokens': 200, 'output_tokens': 80}
            )
        ]
        
        campaign = await warfare_manager.launch_propaganda_campaign(
            orchestrator="General",
            objective="Build national unity",
            target_audience=PropagandaTarget.GENERAL_POPULATION,
            resource_investment={"influence": 50.0, "gold": 100.0},
            duration_turns=5
        )
        
        assert campaign.campaign_id in warfare_manager.active_campaigns
        assert campaign.orchestrator == "General"
        assert campaign.objective == "Build national unity"
        assert campaign.target_audience == PropagandaTarget.GENERAL_POPULATION
        assert len(campaign.messages) >= 2
        assert campaign.resource_investment["influence"] == 50.0
        assert campaign.resource_investment["gold"] == 100.0
        assert campaign.is_active()
    
    def test_detect_propaganda_campaign(self, warfare_manager):
        """Test detecting propaganda campaigns."""
        # Create a test campaign
        campaign = PropagandaCampaign(
            campaign_id="test_campaign",
            name="Test Campaign",
            orchestrator="General",
            objective="Test objective",
            target_audience=PropagandaTarget.GENERAL_POPULATION
        )
        
        # Add to active campaigns
        warfare_manager.active_campaigns["test_campaign"] = campaign
        
        # Mock advisor council to have Spymaster role
        spymaster = Mock()
        spymaster.role = Mock()
        spymaster.role.value = "intelligence"
        warfare_manager.dialogue_system.advisor_council.advisors["Spymaster"] = spymaster
        
        # Mock emotional state for suspicious advisor
        warfare_manager.dialogue_system.get_advisor_emotional_state.return_value = {
            "emotion": "suspicious",
            "intensity": 0.8
        }
        
        # Test detection (may need multiple attempts due to randomness)
        detection_found = False
        for _ in range(20):  # Try multiple times due to probability
            if warfare_manager.detect_propaganda_campaign("Spymaster", campaign):
                detection_found = True
                break
        
        # Should eventually detect (high probability with suspicious spymaster)
        assert detection_found or "Spymaster" in campaign.detected_by
    
    @pytest.mark.asyncio
    async def test_generate_counter_propaganda(self, warfare_manager):
        """Test generating counter-propaganda."""
        # Create original campaign
        original_campaign = PropagandaCampaign(
            campaign_id="original",
            name="Original Campaign",
            orchestrator="General",
            objective="Build support",
            target_audience=PropagandaTarget.GENERAL_POPULATION
        )
        
        original_message = PropagandaMessage(
            message_id="orig_msg",
            content="Support our glorious leader!",
            propaganda_type=PropagandaType.LEGITIMACY_BUILDING,
            target_audience=PropagandaTarget.GENERAL_POPULATION,
            emotional_appeal=EmotionalState.CONFIDENT
        )
        original_campaign.add_message(original_message)
        
        # Mock LLM response
        counter_json = {
            "content": "Question the claims being made!",
            "propaganda_type": "opposition_undermining",
            "emotional_appeal": "suspicious",
            "key_themes": ["Truth", "Skepticism"],
            "factual_basis": 0.8,
            "emotional_intensity": 0.7,
            "sophistication_level": 0.6
        }
        
        warfare_manager.llm_manager.generate.return_value = LLMResponse(
            content=str(counter_json).replace("'", '"'),
            provider=LLMProvider.OPENAI,
            model="mock-model",
            usage={'input_tokens': 150, 'output_tokens': 80}
        )
        
        counter_message = await warfare_manager.generate_counter_propaganda(
            original_campaign, "Diplomat"
        )
        
        assert counter_message.content is not None
        assert counter_message.propaganda_type == PropagandaType.OPPOSITION_UNDERMINING
        assert counter_message.target_audience == original_campaign.target_audience
        assert 0.0 <= counter_message.factual_basis <= 1.0
    
    def test_calculate_campaign_effectiveness(self, warfare_manager):
        """Test calculating campaign effectiveness."""
        # Create campaign with moderate resource investment
        campaign = PropagandaCampaign(
            campaign_id="test_campaign",
            name="Test Campaign",
            orchestrator="General",
            objective="Test objective",
            target_audience=PropagandaTarget.GENERAL_POPULATION,
            resource_investment={"influence": 30.0, "gold": 40.0}  # Lower investment
        )
        
        # Add effective message
        message = PropagandaMessage(
            message_id="test_msg",
            content="Test message",
            propaganda_type=PropagandaType.LEGITIMACY_BUILDING,
            target_audience=PropagandaTarget.GENERAL_POPULATION,
            emotional_appeal=EmotionalState.CONFIDENT,
            factual_basis=0.8
        )
        campaign.add_message(message)
        
        effectiveness = warfare_manager.calculate_campaign_effectiveness(campaign, 1)
        
        assert 0.0 <= effectiveness <= 1.0
        assert effectiveness > 0  # Should have some effectiveness
        
        # Test with detection penalty
        campaign.detected_by = ["Spymaster", "Diplomat"]
        reduced_effectiveness = warfare_manager.calculate_campaign_effectiveness(campaign, 1)
        assert reduced_effectiveness < effectiveness  # Should be reduced due to detection
    
    def test_process_information_warfare_turn(self, warfare_manager):
        """Test processing one turn of information warfare."""
        # Create an active campaign
        campaign = PropagandaCampaign(
            campaign_id="test_campaign",
            name="Test Campaign",
            orchestrator="General",
            objective="Build legitimacy",
            target_audience=PropagandaTarget.GENERAL_POPULATION
        )
        
        message = PropagandaMessage(
            message_id="test_msg",
            content="Test message",
            propaganda_type=PropagandaType.LEGITIMACY_BUILDING,
            target_audience=PropagandaTarget.GENERAL_POPULATION,
            emotional_appeal=EmotionalState.CONFIDENT,
            key_themes=["Legitimacy", "Stability"]
        )
        campaign.add_message(message)
        warfare_manager.active_campaigns["test_campaign"] = campaign
        
        # Mock game state
        game_state = Mock()
        
        results = warfare_manager.process_information_warfare_turn(game_state)
        
        assert "campaign_effects" in results
        assert "new_detections" in results
        assert "public_opinion_changes" in results
        assert "narrative_shifts" in results
        
        # Should have effects from the active campaign
        assert len(results["campaign_effects"]) > 0
        
        # Public opinion should be affected
        assert "Build legitimacy" in warfare_manager.public_opinion or len(warfare_manager.public_opinion) > 0
        
        # Narrative themes should be updated
        assert len(warfare_manager.narrative_themes) > 0
    
    def test_get_campaign_summary(self, warfare_manager):
        """Test getting campaign summary."""
        # Create campaign
        campaign = PropagandaCampaign(
            campaign_id="test_campaign",
            name="Test Campaign",
            orchestrator="General",
            objective="Test objective",
            target_audience=PropagandaTarget.GENERAL_POPULATION,
            resource_investment={"influence": 50.0}
        )
        
        message = PropagandaMessage(
            message_id="test_msg",
            content="Test message",
            propaganda_type=PropagandaType.LEGITIMACY_BUILDING,
            target_audience=PropagandaTarget.GENERAL_POPULATION,
            emotional_appeal=EmotionalState.CONFIDENT,
            key_themes=["Test Theme"]
        )
        campaign.add_message(message)
        warfare_manager.active_campaigns["test_campaign"] = campaign
        
        summary = warfare_manager.get_campaign_summary("test_campaign")
        
        assert summary is not None
        assert summary["campaign_id"] == "test_campaign"
        assert summary["name"] == "Test Campaign"
        assert summary["orchestrator"] == "General"
        assert summary["objective"] == "Test objective"
        assert summary["target_audience"] == "general_population"
        assert summary["is_active"] == True
        assert len(summary["messages"]) == 1
        assert summary["messages"][0]["content"] == "Test message"
        assert summary["resource_investment"]["influence"] == 50.0
    
    def test_get_information_warfare_summary(self, warfare_manager):
        """Test getting comprehensive warfare summary."""
        # Add some campaigns and state
        campaign = PropagandaCampaign(
            campaign_id="test_campaign",
            name="Test Campaign",
            orchestrator="General",
            objective="Test objective",
            target_audience=PropagandaTarget.GENERAL_POPULATION
        )
        warfare_manager.active_campaigns["test_campaign"] = campaign
        warfare_manager.public_opinion["Legitimacy"] = 0.3
        warfare_manager.narrative_themes["Unity"] = 0.8
        warfare_manager.counter_intelligence["Spymaster"] = ["test_campaign"]
        
        summary = warfare_manager.get_information_warfare_summary()
        
        assert "active_campaigns" in summary
        assert "campaigns" in summary
        assert "public_opinion" in summary
        assert "dominant_narratives" in summary
        assert "information_sources" in summary
        assert "counter_intelligence" in summary
        
        assert summary["active_campaigns"] >= 1
        assert "Legitimacy" in summary["public_opinion"]
        assert len(summary["dominant_narratives"]) > 0
        assert len(summary["information_sources"]) >= 4  # Default sources
        assert "Spymaster" in summary["counter_intelligence"]


if __name__ == "__main__":
    pytest.main([__file__])
