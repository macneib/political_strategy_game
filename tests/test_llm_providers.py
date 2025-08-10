"""
Tests for LLM Providers and Configuration
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import json

from src.llm.llm_providers import (
    LLMProvider, LLMMessage, LLMConfig, LLMResponse, 
    VLLMProvider, LLMManager
)
from src.llm.config import LLMConfigManager, create_llm_manager


class TestLLMMessage:
    """Test LLMMessage data class."""
    
    def test_create_message(self):
        """Test creating an LLM message."""
        message = LLMMessage(role="user", content="Hello, advisor!")
        assert message.role == "user"
        assert message.content == "Hello, advisor!"
    
    def test_to_dict(self):
        """Test converting message to dictionary."""
        message = LLMMessage(role="system", content="You are a helpful advisor.")
        result = message.to_dict()
        expected = {"role": "system", "content": "You are a helpful advisor."}
        assert result == expected


class TestLLMConfig:
    """Test LLM configuration."""
    
    def test_create_config(self):
        """Test creating LLM config."""
        config = LLMConfig(
            provider=LLMProvider.VLLM,
            model_name="test-model",
            base_url="http://localhost:8000/v1",
            max_tokens=256
        )
        assert config.provider == LLMProvider.VLLM
        assert config.model_name == "test-model"
        assert config.max_tokens == 256


class TestVLLMProvider:
    """Test vLLM provider."""
    
    def test_init_without_dependencies(self):
        """Test initialization when dependencies are not available."""
        config = LLMConfig(
            provider=LLMProvider.VLLM,
            model_name="test-model"
        )
        
        with patch('src.llm.llm_providers.openai', side_effect=ImportError):
            provider = VLLMProvider(config)
            assert provider.client is None
            assert not provider.is_available()
    
    def test_validate_messages(self):
        """Test message validation."""
        config = LLMConfig(provider=LLMProvider.VLLM, model_name="test")
        provider = VLLMProvider(config)
        
        # Valid messages
        valid_messages = [
            LLMMessage(role="system", content="You are helpful."),
            LLMMessage(role="user", content="Hello!")
        ]
        assert provider.validate_messages(valid_messages)
        
        # Invalid messages
        assert not provider.validate_messages([])
        assert not provider.validate_messages([LLMMessage(role="invalid", content="test")])
        assert not provider.validate_messages([LLMMessage(role="user", content="")])
    
    @pytest.mark.asyncio
    async def test_generate_without_client(self):
        """Test generation when client is not initialized."""
        config = LLMConfig(provider=LLMProvider.VLLM, model_name="test")
        provider = VLLMProvider(config)
        provider.client = None
        
        messages = [LLMMessage(role="user", content="Hello")]
        response = await provider.generate(messages)
        
        assert response.error == "vLLM client not initialized"
        assert response.content == ""
    
    @pytest.mark.asyncio
    async def test_generate_with_mock_client(self):
        """Test generation with mocked client."""
        config = LLMConfig(provider=LLMProvider.VLLM, model_name="test")
        provider = VLLMProvider(config)
        
        # Mock the client and response
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        
        mock_client.chat.completions.create.return_value = mock_response
        provider.client = mock_client
        
        messages = [LLMMessage(role="user", content="Hello")]
        response = await provider.generate(messages)
        
        assert response.error is None
        assert response.content == "Test response"
        assert response.usage["total_tokens"] == 15


class TestLLMManager:
    """Test LLM manager with fallback support."""
    
    def test_create_manager(self):
        """Test creating LLM manager."""
        config = LLMConfig(provider=LLMProvider.VLLM, model_name="test")
        manager = LLMManager(config)
        
        assert manager.primary_provider is not None
        assert len(manager.fallback_providers) == 0
    
    def test_create_manager_with_fallbacks(self):
        """Test creating manager with fallback providers."""
        primary_config = LLMConfig(provider=LLMProvider.VLLM, model_name="primary")
        fallback_config = LLMConfig(provider=LLMProvider.VLLM, model_name="fallback")
        
        manager = LLMManager(primary_config, [fallback_config])
        
        assert manager.primary_provider is not None
        assert len(manager.fallback_providers) == 1
    
    @pytest.mark.asyncio
    async def test_generate_with_unavailable_providers(self):
        """Test generation when all providers are unavailable."""
        config = LLMConfig(provider=LLMProvider.VLLM, model_name="test")
        manager = LLMManager(config)
        
        # Mock provider to be unavailable
        if manager.primary_provider:
            manager.primary_provider.is_available = Mock(return_value=False)
        
        messages = [LLMMessage(role="user", content="Hello")]
        response = await manager.generate(messages)
        
        assert response.error == "All LLM providers unavailable"
        assert "unable to provide a response" in response.content.lower()


class TestLLMConfigManager:
    """Test LLM configuration manager."""
    
    def test_get_default_config(self):
        """Test getting default vLLM config."""
        manager = LLMConfigManager()
        config = manager.get_default_vllm_config()
        
        assert config.provider == LLMProvider.VLLM
        assert config.base_url == "http://localhost:8000/v1"
        assert config.max_tokens == 512
    
    def test_get_recommended_models(self):
        """Test getting recommended models."""
        manager = LLMConfigManager()
        models = manager.get_recommended_models()
        
        assert "qwen2_1.5b" in models
        assert "phi3_mini" in models
        assert "name" in models["qwen2_1.5b"]
        assert "memory" in models["qwen2_1.5b"]
    
    def test_save_and_load_config(self, tmp_path):
        """Test saving and loading configuration."""
        config_path = tmp_path / "test_config.json"
        manager = LLMConfigManager(config_path)
        
        # Create and save config
        config = LLMConfig(
            provider=LLMProvider.VLLM,
            model_name="test-model",
            max_tokens=256
        )
        manager.save_config(config)
        
        # Load config
        loaded_config = manager.load_config()
        
        assert loaded_config is not None
        assert loaded_config.provider == LLMProvider.VLLM
        assert loaded_config.model_name == "test-model"
        assert loaded_config.max_tokens == 256
    
    def test_load_nonexistent_config(self, tmp_path):
        """Test loading config when file doesn't exist."""
        config_path = tmp_path / "nonexistent.json"
        manager = LLMConfigManager(config_path)
        
        config = manager.load_config()
        assert config is None
    
    def test_get_config_or_default(self, tmp_path):
        """Test getting config with fallback to default."""
        config_path = tmp_path / "test_config.json"
        manager = LLMConfigManager(config_path)
        
        # Should return default when no saved config exists
        config = manager.get_config_or_default("custom-model")
        assert config.model_name == "custom-model"
        
        # Should save the default config
        assert config_path.exists()


class TestLLMIntegration:
    """Integration tests for LLM functionality."""
    
    def test_create_llm_manager(self, tmp_path):
        """Test creating LLM manager through config function."""
        config_path = tmp_path / "config.json"
        manager = create_llm_manager(config_path, "test-model")
        
        assert manager is not None
        assert manager.primary_provider is not None
    
    @pytest.mark.asyncio 
    async def test_end_to_end_mock_workflow(self):
        """Test end-to-end workflow with mocked dependencies."""
        # Create config
        config = LLMConfig(
            provider=LLMProvider.VLLM,
            model_name="test-model"
        )
        
        # Create manager
        manager = LLMManager(config)
        
        # Test status reporting
        status = manager.get_status()
        assert "primary" in status
        assert "fallbacks" in status
        
        # Test provider availability check
        available = manager.get_available_providers()
        assert isinstance(available, list)
