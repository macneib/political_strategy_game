"""
Test configuration and fixtures for the Political Strategy Game test suite.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_llm_manager():
    """Mock LLM manager for testing."""
    mock = Mock()
    mock.generate = AsyncMock(return_value=Mock(content="Mock response", role="assistant"))
    mock.get_available_providers = Mock(return_value=[])
    mock.get_status = Mock(return_value={"primary": {"provider": "none", "available": False}})
    return mock


@pytest.fixture
def mock_advisor_council():
    """Mock advisor council for testing."""
    mock = Mock()
    mock.get_council_advice = AsyncMock(return_value={})
    mock.get_single_advice = AsyncMock(return_value="Mock advice")
    mock.record_decision_for_all = Mock()
    mock.get_advisor_status = Mock(return_value={"llm_status": {}, "advisors": {}})
    mock.get_advisor_names = Mock(return_value={})
    return mock


@pytest.fixture
def mock_game_state():
    """Mock game state for testing."""
    class MockGameState:
        def __init__(self):
            self.political_power = 100
            self.stability = 75
            self.legitimacy = 70
            self.current_faction = None
    
    return MockGameState()


@pytest.fixture  
def mock_event():
    """Mock event for testing."""
    class MockEvent:
        def __init__(self):
            self.event_type = "test"
            self.description = "Test event"
            self.turn = 1
    
    return MockEvent()


@pytest.fixture
async def sample_llm_config():
    """Sample LLM configuration for testing."""
    from src.llm.llm_providers import LLMConfig, LLMProvider
    
    return LLMConfig(
        provider=LLMProvider.VLLM,
        model="test-model",
        base_url="http://localhost:8000/v1",
        api_key=None,
        max_tokens=100,
        temperature=0.7
    )

import pytest
import asyncio
import logging
from pathlib import Path
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, AsyncMock, patch

# Set up test logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_DATA_DIR.mkdir(exist_ok=True)

# Mock configurations for testing
MOCK_LLM_CONFIG = {
    "provider": "vllm",
    "model_name": "test-model",
    "base_url": "http://localhost:8000/v1",
    "api_key": "test-key",
    "max_tokens": 100,
    "temperature": 0.7,
    "timeout": 10
}

MOCK_ADVISOR_RESPONSE = "This is a test advisor response for testing purposes."


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_llm_manager():
    """Create a mock LLM manager for testing."""
    mock_manager = Mock()
    mock_manager.generate = AsyncMock(return_value=Mock(
        content=MOCK_ADVISOR_RESPONSE,
        provider="vllm",
        model="test-model",
        error=None
    ))
    mock_manager.get_available_providers.return_value = ["vllm"]
    mock_manager.get_status.return_value = {
        "primary": {"provider": "vllm", "available": True, "model": "test-model"},
        "fallbacks": []
    }
    return mock_manager


@pytest.fixture
def mock_game_state():
    """Create a mock game state for testing."""
    mock_state = Mock()
    mock_state.political_power = 75
    mock_state.stability = 80
    mock_state.current_faction = None
    return mock_state


@pytest.fixture
def sample_events():
    """Create sample events for testing."""
    events = []
    
    # Create mock event objects
    for i in range(3):
        event = Mock()
        event.title = f"Test Event {i+1}"
        event.description = f"Description for test event {i+1}"
        event.type = "test"
        events.append(event)
    
    return events


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary directory for config files."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


class MockVLLMProvider:
    """Mock vLLM provider for testing without actual LLM calls."""
    
    def __init__(self, config):
        self.config = config
    
    async def generate(self, messages, **kwargs):
        """Mock generate method."""
        from src.llm.llm_providers import LLMResponse, LLMProvider
        
        # Simulate processing delay
        await asyncio.sleep(0.01)
        
        return LLMResponse(
            content=MOCK_ADVISOR_RESPONSE,
            provider=LLMProvider.VLLM,
            model=self.config.model_name,
            usage={"prompt_tokens": 50, "completion_tokens": 20, "total_tokens": 70}
        )
    
    def is_available(self):
        """Mock availability check."""
        return True


@pytest.fixture
def mock_vllm_provider():
    """Create a mock vLLM provider."""
    from src.llm.llm_providers import LLMConfig, LLMProvider
    
    config = LLMConfig(
        provider=LLMProvider.VLLM,
        model_name="test-model",
        base_url="http://localhost:8000/v1"
    )
    return MockVLLMProvider(config)


# Patch decorators for common mocks
def mock_vllm_server(func):
    """Decorator to mock vLLM server availability."""
    return patch('src.llm.llm_providers.VLLMProvider.is_available', return_value=True)(func)


def mock_openai_client(func):
    """Decorator to mock OpenAI client."""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content=MOCK_ADVISOR_RESPONSE))]
    mock_response.usage = Mock(prompt_tokens=50, completion_tokens=20, total_tokens=70)
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    return patch('src.llm.llm_providers.openai.AsyncOpenAI', return_value=mock_client)(func)


# Test utilities
def assert_valid_advisor_response(response: str):
    """Assert that an advisor response is valid."""
    assert isinstance(response, str)
    assert len(response) > 0
    assert len(response) < 1000  # Reasonable length limit


def create_test_memory_data():
    """Create test memory data for advisor testing."""
    return {
        "messages": [
            {"role": "user", "content": "Test question 1"},
            {"role": "assistant", "content": "Test response 1"},
            {"role": "user", "content": "Test question 2"},
            {"role": "assistant", "content": "Test response 2"}
        ],
        "key_decisions": [
            "Increase military spending",
            "Form trade alliance with neighboring country"
        ]
    }
