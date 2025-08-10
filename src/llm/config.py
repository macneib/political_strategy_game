"""
LLM Configuration and Setup Utilities

This module provides utilities for configuring and setting up LLM providers,
including vLLM server management and model recommendations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import asdict

from .llm_providers import LLMConfig, LLMProvider, LLMManager


class LLMConfigManager:
    """Manages LLM configuration and setup."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config/llm_config.json")
        self.logger = logging.getLogger("llm.config")
        
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def get_default_vllm_config(self, model_name: str = "Qwen/Qwen2-1.5B-Instruct") -> LLMConfig:
        """Get default vLLM configuration."""
        return LLMConfig(
            provider=LLMProvider.VLLM,
            model_name=model_name,
            base_url="http://localhost:8000/v1",
            api_key="token-abc123",  # vLLM doesn't require real API key
            max_tokens=512,
            temperature=0.7,
            top_p=0.9,
            timeout=30
        )
    
    def get_recommended_models(self) -> Dict[str, Dict[str, Any]]:
        """Get recommended small models for local deployment."""
        return {
            "qwen2_0.5b": {
                "name": "Qwen/Qwen2-0.5B-Instruct",
                "size": "0.5B parameters",
                "memory": "~1GB VRAM",
                "description": "Smallest Qwen2 model, very fast inference",
                "good_for": ["Quick responses", "Limited hardware", "Development/testing"]
            },
            "qwen2_1.5b": {
                "name": "Qwen/Qwen2-1.5B-Instruct",
                "size": "1.5B parameters", 
                "memory": "~3GB VRAM",
                "description": "Balanced Qwen2 model, good quality/speed tradeoff",
                "good_for": ["General use", "Moderate hardware", "Production ready"]
            },
            "phi3_mini": {
                "name": "microsoft/Phi-3-mini-4k-instruct",
                "size": "3.8B parameters",
                "memory": "~4GB VRAM",
                "description": "Microsoft's efficient small model",
                "good_for": ["High quality responses", "Good reasoning", "4K context"]
            },
            "llama3.2_1b": {
                "name": "meta-llama/Llama-3.2-1B-Instruct",
                "size": "1B parameters",
                "memory": "~2GB VRAM",
                "description": "Meta's small Llama model",
                "good_for": ["Fast inference", "Lightweight deployment", "Good general performance"]
            },
            "llama3.2_3b": {
                "name": "meta-llama/Llama-3.2-3B-Instruct",
                "size": "3B parameters",
                "memory": "~6GB VRAM",
                "description": "Larger Llama model with better capabilities",
                "good_for": ["Higher quality", "Complex reasoning", "Larger context"]
            }
        }
    
    def save_config(self, config: LLMConfig):
        """Save LLM configuration to file."""
        try:
            config_dict = asdict(config)
            # Convert enum to string for JSON serialization
            config_dict["provider"] = config.provider.value
            
            with open(self.config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            self.logger.info(f"Saved LLM config to {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def load_config(self) -> Optional[LLMConfig]:
        """Load LLM configuration from file."""
        try:
            if not self.config_path.exists():
                self.logger.info("No existing config found, using defaults")
                return None
            
            with open(self.config_path, 'r') as f:
                config_dict = json.load(f)
            
            # Convert string back to enum
            config_dict["provider"] = LLMProvider(config_dict["provider"])
            
            config = LLMConfig(**config_dict)
            self.logger.info(f"Loaded LLM config from {self.config_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return None
    
    def get_config_or_default(self, model_name: Optional[str] = None) -> LLMConfig:
        """Get saved config or create default."""
        config = self.load_config()
        if config is None:
            config = self.get_default_vllm_config(model_name or "Qwen/Qwen2-1.5B-Instruct")
            self.save_config(config)
        return config


class VLLMServerHelper:
    """Helper utilities for vLLM server management."""
    
    @staticmethod
    def get_installation_instructions() -> str:
        """Get vLLM installation instructions using uv."""
        return """
vLLM Installation Instructions (using uv):

1. Install uv (if not already installed):
   curl -LsSf https://astral.sh/uv/install.sh | sh

2. Install vLLM and dependencies:
   uv pip install vllm openai httpx

3. Start vLLM server with a small model:
   uv run --with vllm vllm serve Qwen/Qwen2-1.5B-Instruct --port 8000

4. Alternative: Install in virtual environment:
   uv venv --python 3.12 --seed
   source .venv/bin/activate
   uv pip install vllm openai httpx --torch-backend=auto

5. Test the server:
   curl http://localhost:8000/v1/models

For GPU acceleration, ensure you have CUDA drivers installed.
The server will automatically download the model on first use.

Quick run without installation:
   uv run --with vllm --with openai play_game.py
"""
    
    @staticmethod
    def get_startup_command(model_name: str, port: int = 8000, **kwargs) -> str:
        """Generate vLLM server startup command using uv."""
        base_cmd = f"uv run --with vllm vllm serve {model_name} --port {port}"
        
        # Add optional parameters
        if "gpu_memory_utilization" in kwargs:
            base_cmd += f" --gpu-memory-utilization {kwargs['gpu_memory_utilization']}"
        
        if "max_model_len" in kwargs:
            base_cmd += f" --max-model-len {kwargs['max_model_len']}"
        
        if "trust_remote_code" in kwargs and kwargs["trust_remote_code"]:
            base_cmd += " --trust-remote-code"
        
        return base_cmd
    
    @staticmethod
    def get_model_requirements(model_name: str) -> Dict[str, str]:
        """Get approximate requirements for a model."""
        # Rough estimates based on model size
        requirements = {
            "Qwen/Qwen2-0.5B-Instruct": {"memory": "1-2GB VRAM", "disk": "1GB"},
            "Qwen/Qwen2-1.5B-Instruct": {"memory": "2-3GB VRAM", "disk": "3GB"},
            "microsoft/Phi-3-mini-4k-instruct": {"memory": "4-6GB VRAM", "disk": "4GB"},
            "meta-llama/Llama-3.2-1B-Instruct": {"memory": "2-3GB VRAM", "disk": "2GB"},
            "meta-llama/Llama-3.2-3B-Instruct": {"memory": "4-6GB VRAM", "disk": "6GB"},
        }
        
        return requirements.get(model_name, {"memory": "Unknown", "disk": "Unknown"})


def create_llm_manager(config_path: Optional[Path] = None, 
                      model_name: Optional[str] = None) -> LLMManager:
    """Create and configure an LLM manager."""
    
    config_manager = LLMConfigManager(config_path)
    primary_config = config_manager.get_config_or_default(model_name)
    
    # Create fallback configurations for robustness
    fallback_configs = []
    
    # If primary is vLLM, add different models as fallbacks
    if primary_config.provider == LLMProvider.VLLM:
        recommended = config_manager.get_recommended_models()
        
        # Add smallest model as fallback if not already primary
        if primary_config.model_name != recommended["qwen2_0.5b"]["name"]:
            fallback_config = LLMConfig(
                provider=LLMProvider.VLLM,
                model_name=recommended["qwen2_0.5b"]["name"],
                base_url="http://localhost:8000/v1",
                api_key="token-abc123",
                max_tokens=256,  # Smaller for fallback
                temperature=0.7,
                timeout=15
            )
            fallback_configs.append(fallback_config)
    
    # Future: Add OpenAI fallback if API key is available
    # if os.getenv("OPENAI_API_KEY"):
    #     openai_config = LLMConfig(
    #         provider=LLMProvider.OPENAI,
    #         model_name="gpt-3.5-turbo",
    #         api_key=os.getenv("OPENAI_API_KEY")
    #     )
    #     fallback_configs.append(openai_config)
    
    return LLMManager(primary_config, fallback_configs)


def setup_logging():
    """Setup logging for LLM components."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Reduce noise from some libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
