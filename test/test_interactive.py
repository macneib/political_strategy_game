"""
Tests for interactive game interface.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from src.game.interactive import GameSession, InteractiveGameCLI


class TestGameSession:
    """Test game session functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.player_name = "Test Player"
        self.civilization_name = "Test Empire"
    
    def test_session_creation(self):
        """Test creating a game session."""
        session = GameSession(self.player_name, self.civilization_name)
        
        assert session.player_name == self.player_name
        assert session.civilization_name == self.civilization_name
        assert session.current_turn == 1
        assert session.political_power == 100
        assert session.stability == 75
        assert session.legitimacy == 70
    
    @patch('src.game.interactive.create_llm_manager')
    @patch('src.game.interactive.AdvisorCouncil')
    @patch('src.game.interactive.PoliticalStrategyGame')
    @patch('src.game.interactive.GAME_DEPENDENCIES_AVAILABLE', True)
    async def test_session_initialization_success(self, mock_game, mock_council, mock_llm):
        """Test successful session initialization."""
        # Mock components
        mock_llm_manager = Mock()
        mock_llm.return_value = mock_llm_manager
        
        mock_advisor_council = Mock()
        mock_council.return_value = mock_advisor_council
        
        mock_strategy_game = Mock()
        mock_strategy_game.create_sample_civilization.return_value = "test-civ-id"
        mock_strategy_game.civilizations = {"test-civ-id": Mock()}
        mock_game.return_value = mock_strategy_game
        
        session = GameSession(self.player_name, self.civilization_name)
        
        await session.initialize()
        
        assert session.llm_manager == mock_llm_manager
        assert session.advisor_council == mock_advisor_council
        assert session.game == mock_strategy_game
        assert session.civilization is not None
    
    @patch('src.game.interactive.GAME_DEPENDENCIES_AVAILABLE', False)
    async def test_session_initialization_no_dependencies(self):
        """Test session initialization without game dependencies."""
        session = GameSession(self.player_name, self.civilization_name)
        
        with pytest.raises(RuntimeError, match="Game dependencies not available"):
            await session.initialize()
    
    def test_get_simple_game_state(self):
        """Test getting simplified game state."""
        session = GameSession(self.player_name, self.civilization_name)
        session.political_power = 85
        session.stability = 90
        
        game_state = session.get_simple_game_state()
        
        assert game_state.political_power == 85
        assert game_state.stability == 90
        assert game_state.current_faction is None
    
    @patch('src.game.interactive.create_llm_manager')
    @patch('src.game.interactive.AdvisorCouncil')
    async def test_get_advisor_recommendations(self, mock_council, mock_llm):
        """Test getting advisor recommendations."""
        # Mock advisor council
        mock_advisor_council = Mock()
        mock_advice_dict = {
            Mock(value="military"): "Military advice here",
            Mock(value="economic"): "Economic advice here"
        }
        mock_advisor_council.get_council_advice = AsyncMock(return_value=mock_advice_dict)
        mock_advisor_council.get_advisor_names.return_value = {
            list(mock_advice_dict.keys())[0]: "General Steel",
            list(mock_advice_dict.keys())[1]: "Dr. Vasquez"
        }
        mock_council.return_value = mock_advisor_council
        
        session = GameSession(self.player_name, self.civilization_name)
        session.advisor_council = mock_advisor_council
        
        recommendations = await session.get_advisor_recommendations("Test situation")
        
        assert len(recommendations) == 2
        assert "General Steel" in recommendations or "Dr. Vasquez" in recommendations
        mock_advisor_council.get_council_advice.assert_called_once()
    
    @patch('src.game.interactive.create_llm_manager')
    @patch('src.game.interactive.AdvisorCouncil')
    async def test_get_single_advisor_advice(self, mock_council, mock_llm):
        """Test getting advice from single advisor."""
        # Mock advisor council
        mock_advisor_council = Mock()
        mock_advisor_council.get_single_advice = AsyncMock(return_value="Single advisor response")
        mock_council.return_value = mock_advisor_council
        
        session = GameSession(self.player_name, self.civilization_name)
        session.advisor_council = mock_advisor_council
        
        advice = await session.get_single_advisor_advice("military", "Test situation")
        
        assert advice == "Single advisor response"
        mock_advisor_council.get_single_advice.assert_called_once()
    
    def test_get_single_advisor_advice_invalid_role(self):
        """Test getting advice with invalid advisor role."""
        session = GameSession(self.player_name, self.civilization_name)
        
        # Use asyncio.run since we need to test an async function
        async def test_invalid():
            return await session.get_single_advisor_advice("invalid", "Test situation")
        
        result = asyncio.run(test_invalid())
        assert "Unknown advisor role" in result
    
    @patch('src.game.interactive.create_llm_manager')
    @patch('src.game.interactive.AdvisorCouncil')
    def test_record_decision(self, mock_council, mock_llm):
        """Test recording a decision."""
        mock_advisor_council = Mock()
        mock_council.return_value = mock_advisor_council
        
        session = GameSession(self.player_name, self.civilization_name)
        session.advisor_council = mock_advisor_council
        
        decision = "Increase defense spending"
        session.record_decision(decision)
        
        mock_advisor_council.record_decision_for_all.assert_called_once_with(decision)
        assert len(session.recent_events) == 1
        assert decision in session.recent_events[0].description
    
    def test_record_decision_limit(self):
        """Test that recent events are limited."""
        session = GameSession(self.player_name, self.civilization_name)
        # Mock the advisor council
        session.advisor_council = Mock()
        session.advisor_council.record_decision_for_all = Mock()
        
        # Add more than 10 decisions
        for i in range(15):
            session.record_decision(f"Decision {i}")
        
        # Should keep only last 10
        assert len(session.recent_events) == 10
        assert "Decision 14" in session.recent_events[-1].description
        assert "Decision 5" in session.recent_events[0].description
    
    def test_advance_turn(self):
        """Test advancing to next turn."""
        session = GameSession(self.player_name, self.civilization_name)
        initial_turn = session.current_turn
        initial_power = session.political_power
        initial_stability = session.stability
        
        session.advance_turn()
        
        assert session.current_turn == initial_turn + 1
        # Values should change (randomized) but stay within bounds
        assert 0 <= session.political_power <= 100
        assert 0 <= session.stability <= 100
    
    @patch('src.game.interactive.create_llm_manager')
    @patch('src.game.interactive.AdvisorCouncil')
    def test_get_status(self, mock_council, mock_llm):
        """Test getting game status."""
        mock_advisor_council = Mock()
        mock_advisor_council.get_advisor_status.return_value = {"test": "status"}
        mock_council.return_value = mock_advisor_council
        
        session = GameSession(self.player_name, self.civilization_name)
        session.advisor_council = mock_advisor_council
        session.current_turn = 5
        
        status = session.get_status()
        
        assert status["player"] == self.player_name
        assert status["civilization"] == self.civilization_name
        assert status["turn"] == 5
        assert status["political_power"] == 100
        assert status["advisor_status"] == {"test": "status"}


class TestInteractiveGameCLI:
    """Test interactive game CLI functionality."""
    
    def test_cli_creation(self):
        """Test creating CLI instance."""
        cli = InteractiveGameCLI()
        
        assert cli.session is None
        assert cli.running is True
    
    @patch('src.game.interactive.create_llm_manager')
    @patch('builtins.input', side_effect=['y'])  # Mock user input to continue without LLM
    async def test_check_llm_setup_no_providers(self, mock_input, mock_create_llm):
        """Test LLM setup check when no providers available."""
        mock_llm_manager = Mock()
        mock_llm_manager.get_available_providers.return_value = []
        mock_create_llm.return_value = mock_llm_manager
        
        cli = InteractiveGameCLI()
        
        result = await cli.check_llm_setup()
        
        assert result is True  # User chose to continue
    
    @patch('src.game.interactive.create_llm_manager')
    @patch('builtins.input', side_effect=['n'])  # Mock user input to exit
    async def test_check_llm_setup_no_providers_exit(self, mock_input, mock_create_llm):
        """Test LLM setup check when user chooses to exit."""
        mock_llm_manager = Mock()
        mock_llm_manager.get_available_providers.return_value = []
        mock_create_llm.return_value = mock_llm_manager
        
        cli = InteractiveGameCLI()
        
        result = await cli.check_llm_setup()
        
        assert result is False  # User chose to exit
    
    @patch('src.game.interactive.create_llm_manager')
    async def test_check_llm_setup_providers_available(self, mock_create_llm):
        """Test LLM setup check when providers are available."""
        from src.llm.llm_providers import LLMProvider
        
        mock_llm_manager = Mock()
        mock_llm_manager.get_available_providers.return_value = [LLMProvider.VLLM]
        mock_create_llm.return_value = mock_llm_manager
        
        cli = InteractiveGameCLI()
        
        result = await cli.check_llm_setup()
        
        assert result is True
    
    @patch('src.game.interactive.GameSession')
    @patch('builtins.input', side_effect=['Test Player', 'Test Empire'])
    async def test_initialize_session_success(self, mock_input, mock_session_class):
        """Test successful session initialization."""
        mock_session = Mock()
        mock_session.initialize = AsyncMock()
        mock_session_class.return_value = mock_session
        
        cli = InteractiveGameCLI()
        
        await cli.initialize_session()
        
        assert cli.session == mock_session
        mock_session.initialize.assert_called_once()
    
    @patch('src.game.interactive.GameSession')
    @patch('builtins.input', side_effect=['Test Player', 'Test Empire'])
    async def test_initialize_session_failure(self, mock_input, mock_session_class):
        """Test session initialization with failure."""
        mock_session = Mock()
        mock_session.initialize = AsyncMock(side_effect=Exception("Init failed"))
        mock_session_class.return_value = mock_session
        
        cli = InteractiveGameCLI()
        
        await cli.initialize_session()
        
        # Should still set session even on failure
        assert cli.session is not None
    
    @patch('builtins.input', return_value='0')  # Exit choice
    @patch('builtins.print')
    async def test_show_main_menu_exit(self, mock_print, mock_input):
        """Test main menu with exit choice."""
        cli = InteractiveGameCLI()
        cli.session = Mock()
        cli.session.civilization_name = "Test Empire"
        cli.session.current_turn = 1
        cli.session.get_status.return_value = {
            'political_power': 100,
            'stability': 75,
            'legitimacy': 70
        }
        
        await cli.show_main_menu()
        
        assert cli.running is False
    
    @patch('builtins.input', return_value='999')  # Invalid choice
    @patch('builtins.print')
    async def test_show_main_menu_invalid_choice(self, mock_print, mock_input):
        """Test main menu with invalid choice."""
        cli = InteractiveGameCLI()
        cli.session = Mock()
        cli.session.civilization_name = "Test Empire"
        cli.session.current_turn = 1
        cli.session.get_status.return_value = {
            'political_power': 100,
            'stability': 75,
            'legitimacy': 70
        }
        
        await cli.show_main_menu()
        
        # Should print error message and continue running
        assert cli.running is True
    
    @patch('builtins.input', side_effect=['Test situation', 'n'])  # Situation + no decision recording
    @patch('builtins.print')
    async def test_consult_advisors(self, mock_print, mock_input):
        """Test consulting advisors."""
        cli = InteractiveGameCLI()
        cli.session = Mock()
        cli.session.get_advisor_recommendations = AsyncMock(return_value={
            "General Steel": "Military advice here",
            "Dr. Vasquez": "Economic advice here"
        })
        
        await cli.consult_advisors()
        
        cli.session.get_advisor_recommendations.assert_called_once_with("Test situation")
    
    @patch('builtins.input', side_effect=[''])  # Empty situation
    @patch('builtins.print')
    async def test_consult_advisors_empty_situation(self, mock_print, mock_input):
        """Test consulting advisors with empty situation."""
        cli = InteractiveGameCLI()
        cli.session = Mock()
        
        await cli.consult_advisors()
        
        # Should not call advisor recommendations
        cli.session.get_advisor_recommendations.assert_not_called()
    
    @patch('builtins.input', side_effect=['1', 'Military decision', 'y'])  # Military + decision + confirm
    @patch('builtins.print')
    async def test_make_decision(self, mock_print, mock_input):
        """Test making a policy decision."""
        cli = InteractiveGameCLI()
        cli.session = Mock()
        cli.session.get_single_advisor_advice = AsyncMock(return_value="Military advisor response")
        cli.session.record_decision = Mock()
        cli.session.political_power = 100
        cli.session.stability = 75
        cli.session.legitimacy = 70
        
        await cli.make_decision()
        
        cli.session.get_single_advisor_advice.assert_called_once()
        cli.session.record_decision.assert_called_once()
    
    @patch('builtins.input', side_effect=['999'])  # Invalid category
    @patch('builtins.print')
    async def test_make_decision_invalid_category(self, mock_print, mock_input):
        """Test making decision with invalid category."""
        cli = InteractiveGameCLI()
        cli.session = Mock()
        
        await cli.make_decision()
        
        # Should not proceed to advisor consultation
        cli.session.get_single_advisor_advice.assert_not_called()
    
    @patch('builtins.print')
    async def test_show_advisor_status(self, mock_print):
        """Test showing advisor status."""
        cli = InteractiveGameCLI()
        cli.session = Mock()
        cli.session.advisor_council.get_advisor_status.return_value = {
            "llm_status": {"primary": {"provider": "vllm", "available": True}},
            "advisors": {"military": {"name": "General Steel", "memory": {"conversation_length": 5}}}
        }
        
        await cli.show_advisor_status()
        
        cli.session.advisor_council.get_advisor_status.assert_called_once()
    
    @patch('builtins.print')
    async def test_advance_turn(self, mock_print):
        """Test advancing turn."""
        cli = InteractiveGameCLI()
        cli.session = Mock()
        cli.session.current_turn = 1
        cli.session.advance_turn = Mock()
        cli.session.get_status.return_value = {
            'turn': 2,
            'political_power': 105,
            'stability': 78
        }
        cli.session.recent_events = []
        
        await cli.advance_turn()
        
        cli.session.advance_turn.assert_called_once()
    
    @patch('builtins.print')
    async def test_save_and_exit(self, mock_print):
        """Test saving and exiting game."""
        cli = InteractiveGameCLI()
        cli.session = Mock()
        cli.session.get_status.return_value = {
            'player': 'Test Player',
            'civilization': 'Test Empire',
            'turn': 5
        }
        
        await cli.save_and_exit()
        
        assert cli.running is False


if __name__ == "__main__":
    # Run tests with asyncio support
    pytest.main([__file__, "-v", "--tb=short"])
