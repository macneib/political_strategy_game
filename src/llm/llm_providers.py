"""
LLM Abstraction Layer for AI-Enhanced Advisors

This module provides a unified interface for interacting with different LLM providers,
including local vLLM servers and remote APIs (OpenAI, Claude, Gemini).

The abstraction layer allows the game to switch between different LLM backends
without changing the core advisor logic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union
from enum import Enum
import asyncio
import logging


class LLMProvider(Enum):
    """Supported LLM providers."""
    VLLM = "vllm"
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"


@dataclass
class LLMMessage:
    """Represents a message in the conversation."""
    role: str  # "system", "user", "assistant"
    content: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {"role": self.role, "content": self.content}


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    provider: LLMProvider
    model_name: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    timeout: int = 30


@dataclass
class LLMResponse:
    """Response from LLM provider."""
    content: str
    provider: LLMProvider
    model: str
    usage: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class LLMProvider_Base(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.logger = logging.getLogger(f"llm.{config.provider.value}")
    
    @abstractmethod
    async def generate(
        self, 
        messages: List[LLMMessage], 
        **kwargs
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass
    
    def validate_messages(self, messages: List[LLMMessage]) -> bool:
        """Validate message format."""
        if not messages:
            return False
        
        for msg in messages:
            if not isinstance(msg, LLMMessage):
                return False
            if msg.role not in ["system", "user", "assistant"]:
                return False
            if not msg.content.strip():
                return False
        
        return True


class VLLMProvider(LLMProvider_Base):
    """vLLM local server provider."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the vLLM client."""
        try:
            import openai
            base_url = self.config.base_url or "http://localhost:8000/v1"
            self.client = openai.AsyncOpenAI(
                base_url=base_url,
                api_key=self.config.api_key or "token-abc123"  # vLLM doesn't require real API key
            )
            self.logger.info(f"Initialized vLLM client with base_url: {base_url}")
        except ImportError:
            self.logger.error("OpenAI package not installed. Run: pip install openai")
            self.client = None
        except Exception as e:
            self.logger.error(f"Failed to initialize vLLM client: {e}")
            self.client = None
    
    async def generate(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Generate response using vLLM server."""
        if not self.client:
            return LLMResponse(
                content="",
                provider=LLMProvider.VLLM,
                model=self.config.model_name,
                error="vLLM client not initialized"
            )
        
        if not self.validate_messages(messages):
            return LLMResponse(
                content="",
                provider=LLMProvider.VLLM,
                model=self.config.model_name,
                error="Invalid message format"
            )
        
        try:
            # Convert messages to OpenAI format
            openai_messages = [msg.to_dict() for msg in messages]
            
            # Merge config with kwargs
            generation_params = {
                "model": self.config.model_name,
                "messages": openai_messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", self.config.top_p),
            }
            
            # Make API call
            response = await self.client.chat.completions.create(**generation_params)
            
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            }
            
            return LLMResponse(
                content=content,
                provider=LLMProvider.VLLM,
                model=self.config.model_name,
                usage=usage
            )
            
        except Exception as e:
            self.logger.error(f"vLLM generation failed: {e}")
            return LLMResponse(
                content="",
                provider=LLMProvider.VLLM,
                model=self.config.model_name,
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if vLLM server is available."""
        if not self.client:
            return False
        
        try:
            import httpx
            import asyncio
            
            async def check_health():
                base_url = self.config.base_url or "http://localhost:8000"
                timeout = httpx.Timeout(5.0)
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(f"{base_url}/health")
                    return response.status_code == 200
            
            # Run async check in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(check_health())
            loop.close()
            return result
            
        except Exception as e:
            self.logger.debug(f"vLLM health check failed: {e}")
            return False


class OpenAIProvider(LLMProvider_Base):
    """OpenAI API provider (for future use)."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client."""
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=self.config.api_key)
            self.logger.info("Initialized OpenAI client")
        except ImportError:
            self.logger.error("OpenAI package not installed. Run: pip install openai")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {e}")
    
    async def generate(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Generate response using OpenAI API."""
        if not self.client:
            return LLMResponse(
                content="",
                provider=LLMProvider.OPENAI,
                model=self.config.model_name,
                error="OpenAI client not initialized or API key missing"
            )
        
        if not self.validate_messages(messages):
            return LLMResponse(
                content="",
                provider=LLMProvider.OPENAI,
                model=self.config.model_name,
                error="Invalid message format"
            )
        
        try:
            openai_messages = [msg.to_dict() for msg in messages]
            
            generation_params = {
                "model": self.config.model_name,
                "messages": openai_messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", self.config.top_p),
            }
            
            response = await self.client.chat.completions.create(**generation_params)
            
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            
            return LLMResponse(
                content=content,
                provider=LLMProvider.OPENAI,
                model=self.config.model_name,
                usage=usage
            )
            
        except Exception as e:
            self.logger.error(f"OpenAI generation failed: {e}")
            return LLMResponse(
                content="",
                provider=LLMProvider.OPENAI,
                model=self.config.model_name,
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available."""
        return self.client is not None and self.config.api_key is not None


class LLMManager:
    """Manages multiple LLM providers with fallback support."""
    
    def __init__(self, primary_config: LLMConfig, fallback_configs: Optional[List[LLMConfig]] = None):
        self.primary_provider = self._create_provider(primary_config)
        self.fallback_providers = []
        
        if fallback_configs:
            for config in fallback_configs:
                provider = self._create_provider(config)
                if provider:
                    self.fallback_providers.append(provider)
        
        self.logger = logging.getLogger("llm.manager")
    
    def _create_provider(self, config: LLMConfig) -> Optional[LLMProvider_Base]:
        """Create provider instance based on config."""
        provider_map = {
            LLMProvider.VLLM: VLLMProvider,
            LLMProvider.OPENAI: OpenAIProvider,
            # Add other providers here as implemented
        }
        
        provider_class = provider_map.get(config.provider)
        if not provider_class:
            self.logger.error(f"Unsupported provider: {config.provider}")
            return None
        
        try:
            return provider_class(config)
        except Exception as e:
            self.logger.error(f"Failed to create {config.provider} provider: {e}")
            return None
    
    async def generate(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Generate response with automatic fallback."""
        # Try primary provider first
        if self.primary_provider and self.primary_provider.is_available():
            response = await self.primary_provider.generate(messages, **kwargs)
            if not response.error:
                return response
            else:
                self.logger.warning(f"Primary provider failed: {response.error}")
        
        # Try fallback providers
        for provider in self.fallback_providers:
            if provider.is_available():
                self.logger.info(f"Trying fallback provider: {provider.config.provider}")
                response = await provider.generate(messages, **kwargs)
                if not response.error:
                    return response
                else:
                    self.logger.warning(f"Fallback provider failed: {response.error}")
        
        # All providers failed
        return LLMResponse(
            content="I apologize, but I'm currently unable to provide a response due to technical difficulties.",
            provider=self.primary_provider.config.provider if self.primary_provider else LLMProvider.VLLM,
            model="fallback",
            error="All LLM providers unavailable"
        )
    
    def get_available_providers(self) -> List[LLMProvider]:
        """Get list of available providers."""
        available = []
        
        if self.primary_provider and self.primary_provider.is_available():
            available.append(self.primary_provider.config.provider)
        
        for provider in self.fallback_providers:
            if provider.is_available():
                available.append(provider.config.provider)
        
        return available
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all providers."""
        status = {
            "primary": {
                "provider": self.primary_provider.config.provider.value if self.primary_provider else None,
                "available": self.primary_provider.is_available() if self.primary_provider else False,
                "model": self.primary_provider.config.model_name if self.primary_provider else None
            },
            "fallbacks": []
        }
        
        for provider in self.fallback_providers:
            status["fallbacks"].append({
                "provider": provider.config.provider.value,
                "available": provider.is_available(),
                "model": provider.config.model_name
            })
        
        return status
