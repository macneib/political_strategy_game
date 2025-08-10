"""
Tests for LLM providers module.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch

from src.llm.llm_providers import (
    LLMMessage, LLMResponse, LLMConfig, LLMProvider,
    VLLMProvider, OpenAIProvider, LLMManager
)


class TestLLMMessage:
    """Test LLM message functionality."""
    
    def test_message_creation(self):
        """Test creating an LLM message."""
        message = LLMMessage(role="user", content="Hello, world!")
        
        assert message.role == "user"
        assert message.content == "Hello, world!"
    
    def test_message_to_dict(self):
        """Test converting message to dictionary."""
        message = LLMMessage(role="assistant", content="Hi there!")
        message_dict = message.to_dict()
        
        expected = {"role": "assistant", "content": "Hi there!"}
        assert message_dict == expected


class TestLLMConfig:
    """Test LLM configuration."""
    
    def test_config_creation(self):
        """Test creating LLM configuration."""
        config = LLMConfig(
            provider=LLMProvider.VLLM,
            model_name="test-model",
            base_url="http://localhost:8000/v1",
            api_key="test-key",
            max_tokens=100,
            temperature=0.7
        )
        
        assert config.provider == LLMProvider.VLLM
        assert config.model == "test-model"
        assert config.base_url == "http://localhost:8000/v1"
        assert config.api_key == "test-key"
        assert config.max_tokens == 100
        assert config.temperature == 0.7


class TestVLLMProvider:
    """Test VLLM provider functionality."""
    
    @patch('openai.AsyncOpenAI')
    def test_provider_initialization(self, mock_openai):
        """Test VLLM provider initialization."""
        config = LLMConfig(
            provider=LLMProvider.VLLM,
            model_name="test-model",
            base_url="http://localhost:8000/v1"
        )
        
        provider = VLLMProvider(config)
        
        assert provider.config == config
        mock_openai.assert_called_once()
    
    def test_validate_messages_valid(self):
        """Test message validation with valid messages."""
        config = LLMConfig(provider=LLMProvider.VLLM, model_name="test-model")
        provider = VLLMProvider(config)
        
        messages = [
            LLMMessage(role="system", content="You are a helpful assistant"),
            LLMMessage(role="user", content="Hello")
        ]
        
        assert provider._validate_messages(messages) is True
    
    def test_validate_messages_invalid(self):
        """Test message validation with invalid messages."""
        config = LLMConfig(provider=LLMProvider.VLLM, model_name="test-model")
        provider = VLLMProvider(config)
        
        # Empty content
        invalid_messages = [LLMMessage(role="user", content="")]
        assert provider._validate_messages(invalid_messages) is False
        
        # Invalid role  
        invalid_messages = [LLMMessage(role="invalid", content="Hello")]
        assert provider._validate_messages(invalid_messages) is False
    
    @patch('openai.AsyncOpenAI')
    async def test_generate_success(self, mock_openai):
        """Test successful generation."""
        # Mock OpenAI client and response
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Generated response"
        mock_message.role = "assistant"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        config = LLMConfig(provider=LLMProvider.VLLM, model_name="test-model")
        provider = VLLMProvider(config)
        
        messages = [LLMMessage(role="user", content="Hello")]
        response = await provider.generate(messages)
        
        assert response.content == "Generated response"
        assert response.role == "assistant"
    
    @patch('openai.AsyncOpenAI')
    async def test_generate_failure(self, mock_openai):
        """Test generation with API failure."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
        
        config = LLMConfig(provider=LLMProvider.VLLM, model_name="test-model")
        provider = VLLMProvider(config)
        
        messages = [LLMMessage(role="user", content="Hello")]
        response = await provider.generate(messages)
        
        assert response.content == "Error: API Error"
        assert response.role == "assistant"
    
    @patch('openai.AsyncOpenAI')
    async def test_generate_invalid_messages(self, mock_openai):
        """Test generation with invalid messages."""
        config = LLMConfig(provider=LLMProvider.VLLM, model_name="test-model")
        provider = VLLMProvider(config)
        
        invalid_messages = [LLMMessage(role="user", content="")]
        response = await provider.generate(invalid_messages)
        
        assert "Invalid messages" in response.content
        assert response.role == "assistant"


class TestOpenAIProvider:
    """Test OpenAI provider functionality."""
    
    @patch('openai.AsyncOpenAI')
    def test_provider_initialization(self, mock_openai):
        """Test OpenAI provider initialization."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-3.5-turbo",
            api_key="test-key"
        )
        
        provider = OpenAIProvider(config)
        
        assert provider.config == config
        mock_openai.assert_called_once()
    
    def test_is_available_with_key(self):
        """Test availability check with API key."""
        with patch('openai.AsyncOpenAI'):
            config = LLMConfig(
                provider=LLMProvider.OPENAI,
                model_name="gpt-3.5-turbo",
                api_key="test-key"
            )
            provider = OpenAIProvider(config)
            
            assert provider.is_available() is True
    
    def test_is_available_without_key(self):
        """Test availability check without API key."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-3.5-turbo"
        )
        provider = OpenAIProvider(config)
        
        assert provider.is_available() is False


class TestLLMManager:
    """Test LLM manager functionality."""
    
    def test_manager_initialization(self):
        """Test LLM manager initialization."""
        primary_config = LLMConfig(provider=LLMProvider.VLLM, model_name="test-model")
        fallback_configs = [
            LLMConfig(provider=LLMProvider.OPENAI, model_name="gpt-3.5-turbo", api_key="test")
        ]
        
        manager = LLMManager(primary_config, fallback_configs)
        
        assert manager.primary_config == primary_config
        assert manager.fallback_configs == fallback_configs
    
    @patch('openai.AsyncOpenAI')
    async def test_generate_primary_success(self, mock_openai):
        """Test successful generation with primary provider."""
        # Mock primary provider success
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Primary response"
        mock_message.role = "assistant"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        primary_config = LLMConfig(provider=LLMProvider.VLLM, model_name="test-model")
        manager = LLMManager(primary_config)
        
        messages = [LLMMessage(role="user", content="Hello")]
        response = await manager.generate(messages)
        
        assert response.content == "Primary response"
    
    @patch('openai.AsyncOpenAI')
    async def test_generate_fallback(self, mock_openai):
        """Test fallback when primary provider fails."""
        # Mock primary failure, fallback success
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # First call fails (primary), second succeeds (fallback)
        mock_client.chat.completions.create = AsyncMock(
            side_effect=[Exception("Primary failed"), self._create_mock_response("Fallback response")]
        )
        
        primary_config = LLMConfig(provider=LLMProvider.VLLM, model_name="test-model")
        fallback_config = LLMConfig(provider=LLMProvider.OPENAI, model_name="gpt-3.5-turbo", api_key="test")
        manager = LLMManager(primary_config, [fallback_config])
        
        messages = [LLMMessage(role="user", content="Hello")]
        response = await manager.generate(messages)
        
        assert response.content == "Fallback response"
    
    @patch('openai.AsyncOpenAI')
    async def test_generate_all_fail(self, mock_openai):
        """Test when all providers fail."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(side_effect=Exception("All failed"))
        
        primary_config = LLMConfig(provider=LLMProvider.VLLM, model_name="test-model")
        fallback_config = LLMConfig(provider=LLMProvider.OPENAI, model_name="gpt-3.5-turbo", api_key="test")
        manager = LLMManager(primary_config, [fallback_config])
        
        messages = [LLMMessage(role="user", content="Hello")]
        response = await manager.generate(messages)
        
        assert "failed to generate response" in response.content.lower()
    
    def test_get_available_providers(self):
        """Test getting available providers."""
        primary_config = LLMConfig(provider=LLMProvider.VLLM, model_name="test-model")
        manager = LLMManager(primary_config)
        
        providers = manager.get_available_providers()
        assert LLMProvider.VLLM in providers
    
    def test_get_status(self):
        """Test getting manager status."""
        primary_config = LLMConfig(provider=LLMProvider.VLLM, model_name="test-model")
        manager = LLMManager(primary_config)
        
        status = manager.get_status()
        assert "primary" in status
        assert status["primary"]["provider"] == "vllm"
    
    def _create_mock_response(self, content: str):
        """Helper to create mock OpenAI response."""
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = content
        mock_message.role = "assistant"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        return mock_response


if __name__ == "__main__":
    # Run tests with asyncio support
    pytest.main([__file__, "-v", "--tb=short"])
