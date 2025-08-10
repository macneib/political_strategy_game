#!/usr/bin/env python3
"""
Simple test runner for LLM functionality without external dependencies.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_llm_message():
    """Test LLM message creation and conversion."""
    from src.llm.llm_providers import LLMMessage
    
    print("Testing LLM Message...")
    
    # Test message creation
    message = LLMMessage(role="user", content="Hello, advisor!")
    assert message.role == "user"
    assert message.content == "Hello, advisor!"
    print("✅ Message creation works")
    
    # Test to_dict conversion
    result = message.to_dict()
    expected = {"role": "user", "content": "Hello, advisor!"}
    assert result == expected
    print("✅ Message to_dict conversion works")


def test_llm_config():
    """Test LLM configuration."""
    from src.llm.llm_providers import LLMConfig, LLMProvider
    
    print("\nTesting LLM Config...")
    
    config = LLMConfig(
        provider=LLMProvider.VLLM,
        model_name="test-model",
        base_url="http://localhost:8000/v1",
        max_tokens=256
    )
    
    assert config.provider == LLMProvider.VLLM
    assert config.model_name == "test-model"
    assert config.max_tokens == 256
    print("✅ LLM config creation works")


def test_advisor_personality():
    """Test advisor personality creation."""
    from src.llm.advisors import AdvisorPersonality, AdvisorRole
    
    print("\nTesting Advisor Personality...")
    
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
    print("✅ Advisor personality creation works")


def test_conversation_memory():
    """Test conversation memory management."""
    from src.llm.advisors import ConversationMemory
    
    print("\nTesting Conversation Memory...")
    
    memory = ConversationMemory()
    memory.add_message("user", "Test message")
    
    assert len(memory.messages) == 1
    assert memory.messages[0].role == "user"
    assert memory.messages[0].content == "Test message"
    assert memory.last_updated is not None
    print("✅ Memory message addition works")
    
    # Test decision recording
    memory.add_decision("Increase military spending")
    assert len(memory.key_decisions) == 1
    assert memory.key_decisions[0] == "Increase military spending"
    print("✅ Memory decision recording works")


def test_config_manager():
    """Test configuration manager."""
    from src.llm.config import LLMConfigManager
    
    print("\nTesting Config Manager...")
    
    manager = LLMConfigManager()
    
    # Test default config
    config = manager.get_default_vllm_config()
    assert config.base_url == "http://localhost:8000/v1"
    assert config.max_tokens == 512
    print("✅ Default config generation works")
    
    # Test recommended models
    models = manager.get_recommended_models()
    assert "qwen2_1.5b" in models
    assert "phi3_mini" in models
    print("✅ Recommended models listing works")


def test_llm_manager_creation():
    """Test LLM manager creation."""
    from src.llm.config import create_llm_manager
    
    print("\nTesting LLM Manager Creation...")
    
    manager = create_llm_manager(model_name="test-model")
    assert manager is not None
    assert manager.primary_provider is not None
    print("✅ LLM manager creation works")
    
    # Test status reporting
    status = manager.get_status()
    assert "primary" in status
    assert "fallbacks" in status
    print("✅ Status reporting works")


async def test_advisor_council():
    """Test advisor council creation."""
    from src.llm.advisors import AdvisorCouncil
    from src.llm.config import create_llm_manager
    
    print("\nTesting Advisor Council...")
    
    llm_manager = create_llm_manager()
    council = AdvisorCouncil(llm_manager)
    
    # Should have all default advisors
    assert len(council.advisors) == 5
    print("✅ Advisor council creation works")
    
    # Test advisor names
    names = council.get_advisor_names()
    assert len(names) == 5
    print("✅ Advisor name mapping works")
    
    # Test status
    status = council.get_advisor_status()
    assert "llm_status" in status
    assert "advisors" in status
    print("✅ Council status reporting works")


def main():
    """Run all tests."""
    print("🧪 Running LLM Implementation Tests")
    print("=" * 40)
    
    try:
        # Synchronous tests
        test_llm_message()
        test_llm_config()
        test_advisor_personality()
        test_conversation_memory()
        test_config_manager()
        test_llm_manager_creation()
        
        # Async tests
        print("\n🔄 Running async tests...")
        asyncio.run(test_advisor_council())
        
        print("\n" + "=" * 40)
        print("🎉 All tests passed! LLM implementation is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
