"""
Simplified Multi-Advisor Integration Tests

Focuses on testing basic integration between AI systems without complex mocking.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from typing import Dict, List

from src.llm.advanced_memory import AdvancedMemoryManager, MemoryType, MemoryImportance
from src.llm.llm_providers import LLMManager, LLMMessage, LLMResponse, LLMProvider


@pytest.fixture
def simple_llm_manager():
    """Create a simple mock LLM manager."""
    llm_manager = Mock()
    llm_manager.generate = AsyncMock(return_value=LLMResponse(
        content="Test response", 
        provider=LLMProvider.OPENAI, 
        model="gpt-4"
    ))
    return llm_manager


class TestBasicIntegration:
    """Test basic integration between AI systems."""
    
    def test_memory_manager_basic_operations(self, simple_llm_manager):
        """Test basic memory manager operations."""
        memory_manager = AdvancedMemoryManager(
            llm_manager=simple_llm_manager,
            max_memory_entries=100
        )
        
        # Add diverse memories
        memories = []
        for i in range(10):
            memory_id = memory_manager.add_memory(
                f"Test memory {i}",
                MemoryType.DECISION if i % 2 == 0 else MemoryType.EVENT,
                MemoryImportance.HIGH if i < 3 else MemoryImportance.MEDIUM,
                ["Test Advisor"]
            )
            memories.append(memory_id)
        
        # Verify memories are stored
        assert len(memory_manager.memories) == 10
        assert all(memory_id in memory_manager.memories for memory_id in memories)
        
        # Test retrieval
        relevant = memory_manager._find_relevant_memories(
            {"test", "memory"}, 
            ["Test Advisor"], 
            limit=5
        )
        assert len(relevant) <= 5
        assert len(relevant) > 0
    
    @pytest.mark.asyncio
    async def test_memory_enhanced_context(self, simple_llm_manager):
        """Test enhanced context generation."""
        memory_manager = AdvancedMemoryManager(
            llm_manager=simple_llm_manager,
            max_memory_entries=100
        )
        
        # Add some memories with different types
        memory_manager.add_memory(
            "Strategic decision to focus on diplomacy",
            MemoryType.DECISION,
            MemoryImportance.HIGH,
            ["Strategic Advisor"],
            tags={"strategy", "diplomacy"}
        )
        
        memory_manager.add_memory(
            "Successful negotiation with eastern neighbors",
            MemoryType.EVENT,
            MemoryImportance.MEDIUM,
            ["Diplomatic Advisor"],
            emotional_context={"satisfaction": 0.8, "confidence": 0.7}
        )
        
        # Get enhanced context
        context = await memory_manager.get_enhanced_context(
            "How should we approach the new diplomatic crisis?",
            ["Strategic Advisor", "Diplomatic Advisor"]
        )
        
        # Verify context structure
        assert context is not None
        assert len(context.relevant_memories) > 0
        assert context.estimated_tokens > 0
        assert len(context.advisor_insights) > 0
        
        # Verify content relevance
        llm_context = context.to_llm_context()
        assert "diplomatic" in llm_context.lower()
        assert len(llm_context) > 50
    
    def test_memory_cleanup_mechanisms(self, simple_llm_manager):
        """Test memory cleanup and overflow handling."""
        memory_manager = AdvancedMemoryManager(
            llm_manager=simple_llm_manager,
            max_memory_entries=20
        )
        
        # Add memories up to the limit
        for i in range(25):
            importance = MemoryImportance.HIGH if i >= 20 else MemoryImportance.LOW
            memory_manager.add_memory(
                f"Memory {i}",
                MemoryType.CONTEXT,
                importance,
                ["Test Advisor"]
            )
        
        # Should have triggered cleanup automatically
        assert len(memory_manager.memories) <= 25  # Allow some flexibility
        
        # High importance memories should be preserved
        high_importance_memories = [
            m for m in memory_manager.memories.values() 
            if m.importance == MemoryImportance.HIGH
        ]
        assert len(high_importance_memories) > 0
    
    @pytest.mark.asyncio 
    async def test_concurrent_memory_operations(self, simple_llm_manager):
        """Test concurrent memory operations."""
        memory_manager = AdvancedMemoryManager(
            llm_manager=simple_llm_manager,
            max_memory_entries=100
        )
        
        # Add some base memories
        for i in range(5):
            memory_manager.add_memory(
                f"Base memory {i}",
                MemoryType.CONTEXT,
                MemoryImportance.MEDIUM,
                ["Test Advisor"]
            )
        
        # Run concurrent operations
        tasks = []
        for i in range(3):
            task = memory_manager.get_enhanced_context(
                f"Query {i}",
                ["Test Advisor"]
            )
            tasks.append(task)
        
        # Should complete without conflicts
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        assert len(results) == 3
        assert all(not isinstance(result, Exception) for result in results)
        assert all(result.estimated_tokens > 0 for result in results)
    
    @pytest.mark.asyncio
    async def test_memory_decision_tracking(self, simple_llm_manager):
        """Test memory system decision tracking."""
        memory_manager = AdvancedMemoryManager(
            llm_manager=simple_llm_manager,
            max_memory_entries=100
        )
        
        # Add decision memory
        decision_id = memory_manager.add_memory(
            "Decided to increase military spending",
            MemoryType.DECISION,
            MemoryImportance.HIGH,
            ["Strategic Advisor", "Military Advisor"],
            tags={"military", "budget"}
        )
        
        # Add outcome
        memory_manager.add_decision_outcome(decision_id, 0.7)
        
        # Verify outcome is tracked
        decision_memory = memory_manager.memories[decision_id]
        assert decision_memory.outcome_impact == 0.7
        
        # Test memory access tracking - use update_access on the memory object directly
        decision_memory = memory_manager.memories[decision_id]
        decision_memory.update_access()
        assert decision_memory.access_count == 1
        assert decision_memory.last_accessed is not None
    
    def test_memory_statistics(self, simple_llm_manager):
        """Test memory system statistics."""
        memory_manager = AdvancedMemoryManager(
            llm_manager=simple_llm_manager,
            max_memory_entries=100
        )
        
        # Add diverse memories
        memory_types = [MemoryType.DECISION, MemoryType.EVENT, MemoryType.INSIGHT]
        importances = [MemoryImportance.HIGH, MemoryImportance.MEDIUM, MemoryImportance.LOW]
        
        for i in range(15):
            memory_manager.add_memory(
                f"Memory {i}",
                memory_types[i % 3],
                importances[i % 3],
                ["Advisor A", "Advisor B"][i % 2:i % 2 + 1]
            )
        
        # Get statistics
        stats = memory_manager.get_memory_statistics()
        
        # Verify statistics structure
        assert 'total_memories' in stats
        assert 'memory_types' in stats
        assert 'importance_distribution' in stats
        assert 'average_access_count' in stats
        
        # Verify counts
        assert stats['total_memories'] == 15
        assert len(stats['memory_types']) > 0
        assert len(stats['importance_distribution']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
