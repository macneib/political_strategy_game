#!/usr/bin/env python3
"""
Simple test to isolate the LLM caching issue
"""

import asyncio
from unittest.mock import Mock, AsyncMock
from src.performance.optimization_manager import PerformanceOptimizationManager, OptimizationConfig
from src.llm.llm_providers import LLMMessage, LLMResponse, LLMProvider


async def test_simple_llm_caching():
    """Test LLM caching without batch processing."""
    print("Testing simple LLM caching...")
    
    # Create config with batch processing disabled
    config = OptimizationConfig(
        enable_memory_pooling=False,
        enable_llm_batching=False,  # Disable batch processing
        enable_concurrent_processing=False
    )
    
    # Create optimization manager
    manager = PerformanceOptimizationManager(config)
    
    # Create mock LLM manager
    mock_llm = Mock()
    mock_llm.generate = AsyncMock(return_value=LLMResponse(
        content="test response",
        provider=LLMProvider.OPENAI,
        model="test"
    ))
    
    print("Registering LLM manager...")
    manager.register_llm_manager(mock_llm)
    
    print("Starting optimization (without background tasks)...")
    # Don't start the full optimization (which starts background tasks)
    manager.running = True
    
    try:
        # Test direct caching
        messages = [LLMMessage(role="user", content="cache test")]
        
        print("Making first LLM call...")
        response1 = await mock_llm.generate(messages)
        print(f"First response: {response1.content}")
        
        print("Making second LLM call (should use cache)...")
        response2 = await mock_llm.generate(messages)
        print(f"Second response: {response2.content}")
        
        # Check cache stats
        report = manager.get_optimization_report()
        cache_stats = report["llm_cache_stats"]
        print(f"Cache stats: {cache_stats}")
        print(f"Cache hit rate: {cache_stats['hit_rate']}")
        
        if cache_stats["hit_rate"] > 0:
            print("✅ LLM caching working correctly!")
        else:
            print("❌ LLM caching not working")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        manager.running = False
        print("Test completed")


if __name__ == "__main__":
    asyncio.run(test_simple_llm_caching())
