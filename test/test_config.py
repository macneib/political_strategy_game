"""
Tests for LLM configuration and setup utilities.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from src.llm.config import (
    LLMConfigManager, VLLMServerHelper, create_llm_manager, setup_logging
)
from src.llm.llm_providers import LLMConfig, LLMProvider


class TestLLMConfigManager:
    """Test LLM configuration manager."""
    
    def test_default_vllm_config(self):
        """Test creating default vLLM configuration."""
        manager = LLMConfigManager()
        
        config = manager.get_default_vllm_config()
        
        assert config.provider == LLMProvider.VLLM
        assert config.model_name == "Qwen/Qwen2-1.5B-Instruct"
        assert config.base_url == "http://localhost:8000/v1"
        assert config.max_tokens == 512
        assert config.temperature == 0.7
    
    def test_default_vllm_config_custom_model(self):
        """Test creating default config with custom model."""
        manager = LLMConfigManager()
        
        custom_model = "microsoft/Phi-3-mini-4k-instruct"
        config = manager.get_default_vllm_config(custom_model)
        
        assert config.model_name == custom_model
        assert config.provider == LLMProvider.VLLM
    
    def test_get_recommended_models(self):
        """Test getting recommended models."""
        manager = LLMConfigManager()
        
        models = manager.get_recommended_models()
        
        assert "qwen2_0.5b" in models
        assert "qwen2_1.5b" in models
        assert "phi3_mini" in models
        assert "llama3.2_1b" in models
        assert "llama3.2_3b" in models
        
        # Check model structure
        qwen_model = models["qwen2_1.5b"]
        assert "name" in qwen_model
        assert "size" in qwen_model
        assert "memory" in qwen_model
        assert "description" in qwen_model
        assert "good_for" in qwen_model
        
        assert qwen_model["name"] == "Qwen/Qwen2-1.5B-Instruct"
    
    def test_save_config(self, temp_config_dir):
        """Test saving configuration to file."""
        config_path = temp_config_dir / "test_config.json"
        manager = LLMConfigManager(config_path)
        
        config = LLMConfig(
            provider=LLMProvider.VLLM,
            model_name="test-model",
            base_url="http://test:8000"
        )
        
        manager.save_config(config)
        
        assert config_path.exists()
        
        # Verify saved content
        with open(config_path) as f:
            saved_data = json.load(f)
        
        assert saved_data["provider"] == "vllm"  # Enum converted to string
        assert saved_data["model_name"] == "test-model"
        assert saved_data["base_url"] == "http://test:8000"
    
    def test_load_config(self, temp_config_dir):
        """Test loading configuration from file."""
        config_path = temp_config_dir / "test_config.json"
        
        # Create test config file
        test_config = {
            "provider": "vllm",
            "model_name": "test-model",
            "base_url": "http://test:8000",
            "api_key": "test-key",
            "max_tokens": 256,
            "temperature": 0.8,
            "top_p": 0.95,
            "timeout": 20
        }
        
        with open(config_path, 'w') as f:
            json.dump(test_config, f)
        
        manager = LLMConfigManager(config_path)
        config = manager.load_config()
        
        assert config is not None
        assert config.provider == LLMProvider.VLLM
        assert config.model_name == "test-model"
        assert config.base_url == "http://test:8000"
        assert config.max_tokens == 256
        assert config.temperature == 0.8
    
    def test_load_config_nonexistent(self, temp_config_dir):
        """Test loading config when file doesn't exist."""
        config_path = temp_config_dir / "nonexistent.json"
        manager = LLMConfigManager(config_path)
        
        config = manager.load_config()
        
        assert config is None
    
    def test_load_config_invalid_json(self, temp_config_dir):
        """Test loading config with invalid JSON."""
        config_path = temp_config_dir / "invalid.json"
        
        # Write invalid JSON
        with open(config_path, 'w') as f:
            f.write("{ invalid json }")
        
        manager = LLMConfigManager(config_path)
        config = manager.load_config()
        
        assert config is None
    
    def test_get_config_or_default_existing(self, temp_config_dir):
        """Test getting existing config."""
        config_path = temp_config_dir / "existing.json"
        
        # Create existing config
        existing_config = {
            "provider": "vllm",
            "model_name": "existing-model",
            "base_url": "http://existing:8000",
            "api_key": None,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            "timeout": 30
        }
        
        with open(config_path, 'w') as f:
            json.dump(existing_config, f)
        
        manager = LLMConfigManager(config_path)
        config = manager.get_config_or_default()
        
        assert config.model_name == "existing-model"
        assert config.base_url == "http://existing:8000"
    
    def test_get_config_or_default_new(self, temp_config_dir):
        """Test getting default config when none exists."""
        config_path = temp_config_dir / "new.json"
        manager = LLMConfigManager(config_path)
        
        config = manager.get_config_or_default("custom-model")
        
        assert config.model_name == "custom-model"
        assert config.provider == LLMProvider.VLLM
        
        # Should have saved the config
        assert config_path.exists()


class TestVLLMServerHelper:
    """Test vLLM server helper utilities."""
    
    def test_get_installation_instructions(self):
        """Test getting installation instructions."""
        instructions = VLLMServerHelper.get_installation_instructions()
        
        assert "uv" in instructions
        assert "vllm" in instructions
        assert "openai" in instructions
        assert "curl" in instructions
        assert "serve" in instructions
    
    def test_get_startup_command_basic(self):
        """Test generating basic startup command."""
        command = VLLMServerHelper.get_startup_command("test-model")
        
        expected = "uv run --with vllm vllm serve test-model --port 8000"
        assert command == expected
    
    def test_get_startup_command_custom_port(self):
        """Test startup command with custom port."""
        command = VLLMServerHelper.get_startup_command("test-model", port=9000)
        
        assert "--port 9000" in command
    
    def test_get_startup_command_with_options(self):
        """Test startup command with additional options."""
        command = VLLMServerHelper.get_startup_command(
            "test-model",
            gpu_memory_utilization=0.8,
            max_model_len=4096,
            trust_remote_code=True
        )
        
        assert "--gpu-memory-utilization 0.8" in command
        assert "--max-model-len 4096" in command
        assert "--trust-remote-code" in command
    
    def test_get_model_requirements_known(self):
        """Test getting requirements for known models."""
        reqs = VLLMServerHelper.get_model_requirements("Qwen/Qwen2-1.5B-Instruct")
        
        assert "memory" in reqs
        assert "disk" in reqs
        assert "GB" in reqs["memory"]
        assert "GB" in reqs["disk"]
    
    def test_get_model_requirements_unknown(self):
        """Test getting requirements for unknown models."""
        reqs = VLLMServerHelper.get_model_requirements("unknown/model")
        
        assert reqs["memory"] == "Unknown"
        assert reqs["disk"] == "Unknown"


class TestCreateLLMManager:
    """Test LLM manager creation utilities."""
    
    @patch('src.llm.config.LLMConfigManager')
    @patch('src.llm.config.LLMManager')
    def test_create_llm_manager_default(self, mock_manager_class, mock_config_manager_class):
        """Test creating LLM manager with defaults."""
        # Mock config manager
        mock_config_manager = Mock()
        mock_config = Mock()
        mock_config.provider = LLMProvider.VLLM
        mock_config.model_name = "test-model"
        mock_config_manager.get_config_or_default.return_value = mock_config
        mock_config_manager_class.return_value = mock_config_manager
        
        # Mock recommended models
        mock_config_manager.get_recommended_models.return_value = {
            "qwen2_0.5b": {"name": "Qwen/Qwen2-0.5B-Instruct"}
        }
        
        # Mock LLM manager
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        result = create_llm_manager()
        
        assert result == mock_manager
        mock_config_manager_class.assert_called_once()
        mock_manager_class.assert_called_once()
    
    @patch('src.llm.config.LLMConfigManager')
    @patch('src.llm.config.LLMManager')
    def test_create_llm_manager_custom_model(self, mock_manager_class, mock_config_manager_class):
        """Test creating LLM manager with custom model."""
        mock_config_manager = Mock()
        mock_config_manager_class.return_value = mock_config_manager
        
        create_llm_manager(model_name="custom-model")
        
        mock_config_manager.get_config_or_default.assert_called_once_with("custom-model")
    
    @patch('src.llm.config.LLMConfigManager')
    @patch('src.llm.config.LLMManager')
    def test_create_llm_manager_custom_path(self, mock_manager_class, mock_config_manager_class):
        """Test creating LLM manager with custom config path."""
        custom_path = Path("/custom/path")
        
        create_llm_manager(config_path=custom_path)
        
        mock_config_manager_class.assert_called_once_with(custom_path)


class TestSetupLogging:
    """Test logging setup."""
    
    @patch('src.llm.config.logging.basicConfig')
    @patch('src.llm.config.logging.getLogger')
    def test_setup_logging(self, mock_get_logger, mock_basic_config):
        """Test logging setup."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        setup_logging()
        
        mock_basic_config.assert_called_once()
        
        # Verify basic config was called with correct parameters
        call_args = mock_basic_config.call_args
        assert call_args[1]["level"] == 20  # logging.INFO = 20
        assert "format" in call_args[1]
        
        # Verify noise reduction for libraries
        assert mock_get_logger.call_count >= 2
        mock_logger.setLevel.assert_called()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
