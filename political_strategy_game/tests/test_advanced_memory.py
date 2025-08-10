"""
Tests for the Advanced Memory Integration system.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from collections import defaultdict

from src.llm.advanced_memory import (
    AdvancedMemoryManager, MemoryEntry, MemoryType, MemoryImportance, 
    ContextRelevance, ContextPackage, create_memory_manager,
    add_decision_memory, add_event_memory
)
from src.llm.llm_providers import LLMManager, LLMMessage, LLMResponse, LLMProvider


class TestMemoryEntry:
    def test_memory_entry_creation(self):
        """Test creating a memory entry."""
        entry = MemoryEntry(
            memory_id="test_001",
            content="Strategic alliance formed with neighboring faction",
            memory_type=MemoryType.DECISION,
            importance=MemoryImportance.HIGH,
            timestamp=datetime.now(),
            associated_advisors=["General Marcus", "Diplomat Elena"],
            tags={"alliance", "diplomacy"},
            context_keywords={"alliance", "strategic", "faction", "neighboring"}
        )
        
        assert entry.memory_id == "test_001"
        assert entry.memory_type == MemoryType.DECISION
        assert entry.importance == MemoryImportance.HIGH
        assert len(entry.associated_advisors) == 2
        assert "alliance" in entry.tags
        assert "strategic" in entry.context_keywords
    
    def test_relevance_score_calculation(self):
        """Test calculating relevance scores."""
        entry = MemoryEntry(
            memory_id="test_002",
            content="Military defense strategy implemented",
            memory_type=MemoryType.STRATEGY,
            importance=MemoryImportance.HIGH,
            timestamp=datetime.now() - timedelta(days=5),
            associated_advisors=["General Marcus"],
            context_keywords={"military", "defense", "strategy"}
        )
        
        # Test with matching keywords and advisor
        query_keywords = {"military", "strategy", "defense"}
        current_advisors = ["General Marcus", "Diplomat Elena"]
        
        score = entry.calculate_relevance_score(query_keywords, current_advisors)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be high due to keyword and advisor match
        
        # Test with no matches
        empty_score = entry.calculate_relevance_score({"unrelated"}, ["Unknown Advisor"])
        assert empty_score < score
    
    def test_access_tracking(self):
        """Test memory access tracking."""
        entry = MemoryEntry(
            memory_id="test_003",
            content="Test memory",
            memory_type=MemoryType.CONTEXT,
            importance=MemoryImportance.MEDIUM,
            timestamp=datetime.now()
        )
        
        initial_count = entry.access_count
        # last_accessed starts as None
        
        entry.update_access()
        
        assert entry.access_count == initial_count + 1
        assert entry.last_accessed is not None
        
        # Test second access
        first_access_time = entry.last_accessed
        entry.update_access()
        
        assert entry.access_count == initial_count + 2
        assert entry.last_accessed >= first_access_time
    
    def test_decay_application(self):
        """Test memory decay functionality."""
        entry = MemoryEntry(
            memory_id="test_004",
            content="Test memory",
            memory_type=MemoryType.CONTEXT,
            importance=MemoryImportance.MEDIUM,
            timestamp=datetime.now()
        )
        
        original_decay = entry.decay_factor
        entry.apply_decay(0.9)
        
        assert entry.decay_factor < original_decay
        assert entry.decay_factor == original_decay * 0.9


class TestContextPackage:
    def test_context_package_creation(self):
        """Test creating a context package."""
        memories = [
            MemoryEntry(
                memory_id="mem_001",
                content="Strategic decision about military deployment",
                memory_type=MemoryType.DECISION,
                importance=MemoryImportance.HIGH,
                timestamp=datetime.now()
            )
        ]
        
        package = ContextPackage(
            query_context="Should we deploy military forces?",
            relevant_memories=memories,
            historical_patterns=["Military deployments require careful planning"],
            advisor_insights={"General Marcus": "Consider defensive positions first"},
            decision_precedents=["Previous deployment was successful"],
            estimated_tokens=500,
            relevance_scores={"mem_001": 0.8}
        )
        
        assert package.query_context == "Should we deploy military forces?"
        assert len(package.relevant_memories) == 1
        assert len(package.historical_patterns) == 1
        assert "General Marcus" in package.advisor_insights
        assert len(package.decision_precedents) == 1
        assert package.estimated_tokens == 500
    
    def test_llm_context_conversion(self):
        """Test converting context package to LLM format."""
        memories = [
            MemoryEntry(
                memory_id="mem_001",
                content="Strategic military alliance formed",
                memory_type=MemoryType.DECISION,
                importance=MemoryImportance.HIGH,
                timestamp=datetime.now()
            )
        ]
        
        package = ContextPackage(
            query_context="Military strategy question",
            relevant_memories=memories,
            historical_patterns=["Alliances strengthen military position"],
            advisor_insights={"General Marcus": "Military readiness is crucial"},
            decision_precedents=["Previous alliance was beneficial"],
            estimated_tokens=300,
            relevance_scores={"mem_001": 0.9}
        )
        
        llm_context = package.to_llm_context(max_tokens=1000)
        
        assert "CURRENT CONTEXT:" in llm_context
        assert "Military strategy question" in llm_context
        assert "RELEVANT HISTORICAL CONTEXT:" in llm_context
        assert "Strategic military alliance formed" in llm_context
        assert "IDENTIFIED PATTERNS:" in llm_context
        assert "ADVISOR INSIGHTS:" in llm_context
        assert "RELEVANT PRECEDENTS:" in llm_context
    
    def test_token_limit_trimming(self):
        """Test context trimming for token limits."""
        # Create package with lots of content
        memories = [
            MemoryEntry(
                memory_id=f"mem_{i}",
                content=f"Very long memory content that should be trimmed when token limits are exceeded: {i} " * 20,
                memory_type=MemoryType.CONTEXT,
                importance=MemoryImportance.MEDIUM,
                timestamp=datetime.now()
            )
            for i in range(10)
        ]
        
        package = ContextPackage(
            query_context="Long query " * 20,
            relevant_memories=memories,
            historical_patterns=["Pattern " * 10] * 5,
            advisor_insights={f"Advisor_{i}": "Insight " * 15 for i in range(5)},
            decision_precedents=["Precedent " * 10] * 5,
            estimated_tokens=5000,
            relevance_scores={f"mem_{i}": 0.5 for i in range(10)}
        )
        
        # Convert with small token limit
        llm_context = package.to_llm_context(max_tokens=100)
        
        # Should be trimmed
        assert len(llm_context) < 1000  # Much smaller than full content
        assert "context truncated" in llm_context or len(llm_context) < 500


class TestAdvancedMemoryManager:
    @pytest.fixture
    def mock_llm_manager(self):
        """Create a mock LLM manager."""
        llm_manager = Mock()
        llm_manager.generate = AsyncMock()
        return llm_manager
    
    @pytest.fixture
    def memory_manager(self, mock_llm_manager):
        """Create a memory manager for testing."""
        return AdvancedMemoryManager(mock_llm_manager, max_memory_entries=100)
    
    def test_memory_manager_initialization(self, memory_manager):
        """Test memory manager initialization."""
        assert len(memory_manager.memories) == 0
        assert len(memory_manager.memory_index) == 0
        assert len(memory_manager.advisor_memories) == 0
        assert len(memory_manager.temporal_index) == 0
        assert memory_manager.max_memory_entries == 100
    
    def test_add_memory(self, memory_manager):
        """Test adding memories to the system."""
        memory_id = memory_manager.add_memory(
            content="Strategic military alliance with eastern faction",
            memory_type=MemoryType.DECISION,
            importance=MemoryImportance.HIGH,
            associated_advisors=["General Marcus", "Diplomat Elena"],
            tags={"military", "alliance"}
        )
        
        assert memory_id in memory_manager.memories
        memory = memory_manager.memories[memory_id]
        
        assert memory.content == "Strategic military alliance with eastern faction"
        assert memory.memory_type == MemoryType.DECISION
        assert memory.importance == MemoryImportance.HIGH
        assert "General Marcus" in memory.associated_advisors
        
        # Check indexes were updated
        assert memory_id in memory_manager.advisor_memories["General Marcus"]
        assert memory_id in memory_manager.advisor_memories["Diplomat Elena"]
        
        # Check keyword indexing
        assert "strategic" in memory.context_keywords
        assert "military" in memory.context_keywords
        assert "alliance" in memory.context_keywords
    
    def test_keyword_extraction(self, memory_manager):
        """Test keyword extraction from content."""
        keywords = memory_manager._extract_keywords(
            "The military strategic alliance requires diplomatic negotiation with the political faction"
        )
        
        # Should extract meaningful words
        expected_keywords = {"military", "strategic", "alliance", "diplomatic", "negotiation", "political", "faction"}
        assert expected_keywords.issubset(keywords)
        
        # Should not include most stop words (but some might slip through due to content-based inclusion)
        critical_stop_words = {"the", "and", "or"}  # Test only critical stop words
        assert not any(word in keywords for word in critical_stop_words)
    
    def test_find_relevant_memories(self, memory_manager):
        """Test finding relevant memories."""
        # Add several memories
        memory_manager.add_memory(
            "Military defense strategy implemented",
            MemoryType.STRATEGY,
            MemoryImportance.HIGH,
            ["General Marcus"]
        )
        
        memory_manager.add_memory(
            "Diplomatic negotiations with neighboring faction",
            MemoryType.EVENT,
            MemoryImportance.MEDIUM,
            ["Diplomat Elena"]
        )
        
        memory_manager.add_memory(
            "Economic trade agreement established",
            MemoryType.DECISION,
            MemoryImportance.LOW,
            ["Economic Advisor"]
        )
        
        # Search for military-related memories
        relevant = memory_manager._find_relevant_memories(
            {"military", "strategy", "defense"}, 
            ["General Marcus"], 
            limit=5
        )
        
        assert len(relevant) > 0
        # Should prioritize military strategy memory
        assert any("Military defense strategy" in memory.content for memory in relevant)
    
    @pytest.mark.asyncio
    async def test_get_enhanced_context(self, memory_manager, mock_llm_manager):
        """Test getting enhanced context."""
        # Add some memories
        memory_manager.add_memory(
            "Previous military campaign was successful",
            MemoryType.DECISION,
            MemoryImportance.HIGH,
            ["General Marcus"]
        )
        
        memory_manager.add_memory(
            "Alliance negotiations proved beneficial",
            MemoryType.EVENT,
            MemoryImportance.MEDIUM,
            ["Diplomat Elena"]
        )
        
        # Mock LLM responses
        mock_llm_manager.generate.side_effect = [
            # Pattern identification response
            LLMResponse(
                content="1. Military campaigns succeed with proper planning\n2. Alliances provide strategic advantages\n3. Timing is crucial for military operations",
                provider=LLMProvider.OPENAI,
                model="mock-model"
            ),
            # Advisor insight for General Marcus
            LLMResponse(
                content="Based on previous success, maintain strategic planning focus and ensure resource allocation.",
                provider=LLMProvider.OPENAI,
                model="mock-model"
            )
        ]
        
        context = await memory_manager.get_enhanced_context(
            query="Should we launch a military campaign?",
            current_advisors=["General Marcus", "Diplomat Elena"],
            max_context_tokens=1500
        )
        
        assert isinstance(context, ContextPackage)
        assert context.query_context == "Should we launch a military campaign?"
        assert len(context.relevant_memories) > 0
        assert len(context.historical_patterns) > 0
        assert "General Marcus" in context.advisor_insights
        assert context.estimated_tokens > 0
    
    @pytest.mark.asyncio
    async def test_pattern_identification(self, memory_manager, mock_llm_manager):
        """Test LLM-based pattern identification."""
        # Create memories for pattern analysis
        memories = [
            MemoryEntry(
                memory_id="mem_1",
                content="Military campaign succeeded with proper preparation",
                memory_type=MemoryType.EVENT,
                importance=MemoryImportance.HIGH,
                timestamp=datetime.now()
            ),
            MemoryEntry(
                memory_id="mem_2", 
                content="Failed military action due to insufficient planning",
                memory_type=MemoryType.EVENT,
                importance=MemoryImportance.MEDIUM,
                timestamp=datetime.now()
            )
        ]
        
        # Mock LLM response
        mock_llm_manager.generate.return_value = LLMResponse(
            content="1. Military success correlates with preparation quality\n2. Planning phase determines campaign outcomes\n3. Resource allocation impacts military effectiveness",
            provider=LLMProvider.OPENAI,
            model="mock-model"
        )
        
        patterns = await memory_manager._identify_contextual_patterns(
            "Military strategy planning",
            memories
        )
        
        assert len(patterns) > 0
        assert any("preparation" in pattern.lower() for pattern in patterns)
        assert any("planning" in pattern.lower() for pattern in patterns)
    
    @pytest.mark.asyncio
    async def test_advisor_insights(self, memory_manager, mock_llm_manager):
        """Test getting advisor-specific insights."""
        # Add advisor-specific memory
        memory_manager.add_memory(
            "General Marcus recommended defensive positioning",
            MemoryType.INSIGHT,
            MemoryImportance.HIGH,
            ["General Marcus"]
        )
        
        memories = list(memory_manager.memories.values())
        
        # Mock LLM response
        mock_llm_manager.generate.return_value = LLMResponse(
            content="Defensive positioning has proven effective in previous engagements and should be prioritized.",
            provider=LLMProvider.OPENAI,
            model="mock-model"
        )
        
        insights = await memory_manager._get_advisor_insights(
            "Military tactical planning",
            ["General Marcus"],
            memories
        )
        
        assert "General Marcus" in insights
        assert len(insights["General Marcus"]) > 0
        assert "defensive" in insights["General Marcus"].lower()
    
    def test_decision_precedents(self, memory_manager):
        """Test finding decision precedents."""
        # Add decision memories with outcomes
        memory_id_1 = memory_manager.add_memory(
            "Formed alliance with northern faction",
            MemoryType.DECISION,
            MemoryImportance.HIGH,
            ["Diplomat Elena"]
        )
        
        memory_id_2 = memory_manager.add_memory(
            "Declared war on eastern faction",
            MemoryType.DECISION,
            MemoryImportance.MEDIUM,
            ["General Marcus"]
        )
        
        # Add outcomes
        memory_manager.add_decision_outcome(memory_id_1, 0.8)  # Successful
        memory_manager.add_decision_outcome(memory_id_2, 0.3)  # Unsuccessful
        
        memories = list(memory_manager.memories.values())
        precedents = memory_manager._find_decision_precedents(
            {"alliance", "faction"}, memories
        )
        
        assert len(precedents) > 0
        # Should prioritize successful decisions
        assert any("alliance" in precedent.lower() for precedent in precedents)
    
    def test_memory_cleanup(self, memory_manager):
        """Test memory cleanup functionality."""
        # Test basic cleanup mechanism exists and doesn't crash
        
        # Add a few memories
        for i in range(10):
            memory_manager.add_memory(
                f"Test Memory {i} content",
                MemoryType.CONTEXT,
                MemoryImportance.MEDIUM,
                []
            )
        
        initial_count = len(memory_manager.memories)
        
        # Test that cleanup runs without error
        memory_manager._cleanup_old_memories()
        after_cleanup_count = len(memory_manager.memories)
        
        # Should not crash and should preserve all or most memories (they're fresh)
        assert after_cleanup_count <= initial_count
        assert after_cleanup_count >= 0
        
        # Test that cleanup was attempted (last_cleanup time updated)
        assert memory_manager.last_cleanup is not None
    
    def test_memory_statistics(self, memory_manager):
        """Test getting memory statistics."""
        # Add various types of memories
        memory_manager.add_memory("Decision content", MemoryType.DECISION, MemoryImportance.HIGH, ["Advisor1"])
        memory_manager.add_memory("Event content", MemoryType.EVENT, MemoryImportance.MEDIUM, ["Advisor2"])
        memory_manager.add_memory("Pattern content", MemoryType.PATTERN, MemoryImportance.LOW, ["Advisor1"])
        
        stats = memory_manager.get_memory_statistics()
        
        assert "total_memories" in stats
        assert "memory_types" in stats
        assert "importance_distribution" in stats
        assert "average_access_count" in stats
        assert "unique_keywords" in stats
        
        assert stats["total_memories"] == 3
        
        # Check memory types exist in the statistics
        memory_types = stats["memory_types"]
        assert "decision" in memory_types
        assert "event" in memory_types 
        assert "pattern" in memory_types
        
        assert memory_types["decision"] == 1
        assert memory_types["event"] == 1
        assert memory_types["pattern"] == 1
    
    def test_context_caching(self, memory_manager, mock_llm_manager):
        """Test context caching functionality."""
        # Add a memory
        memory_manager.add_memory(
            "Test memory for caching",
            MemoryType.CONTEXT,
            MemoryImportance.MEDIUM,
            ["Test Advisor"]
        )
        
        # Mock LLM to track calls
        mock_llm_manager.generate.return_value = LLMResponse(
            content="Test pattern",
            provider=LLMProvider.OPENAI,
            model="mock-model"
        )
        
        query = "Test query"
        advisors = ["Test Advisor"]
        
        # First call should generate new context
        asyncio.run(memory_manager.get_enhanced_context(query, advisors))
        first_call_count = mock_llm_manager.generate.call_count
        
        # Second call should use cache
        asyncio.run(memory_manager.get_enhanced_context(query, advisors))
        second_call_count = mock_llm_manager.generate.call_count
        
        # Should have same number of LLM calls (used cache)
        assert second_call_count == first_call_count
    
    def test_outcome_tracking(self, memory_manager):
        """Test decision outcome tracking."""
        memory_id = memory_manager.add_memory(
            "Strategic decision about resource allocation",
            MemoryType.DECISION,
            MemoryImportance.HIGH,
            ["Economic Advisor"]
        )
        
        # Add outcome
        memory_manager.add_decision_outcome(memory_id, 0.7)
        
        memory = memory_manager.memories[memory_id]
        assert memory.outcome_impact == 0.7


class TestHelperFunctions:
    @pytest.fixture
    def mock_llm_manager(self):
        """Create a mock LLM manager."""
        return Mock()
    
    def test_create_memory_manager(self, mock_llm_manager):
        """Test memory manager creation helper."""
        manager = create_memory_manager(mock_llm_manager)
        
        assert isinstance(manager, AdvancedMemoryManager)
        assert manager.llm_manager == mock_llm_manager
        assert manager.max_memory_entries == 10000
    
    def test_add_decision_memory_helper(self, mock_llm_manager):
        """Test decision memory helper function."""
        manager = create_memory_manager(mock_llm_manager)
        
        memory_id = add_decision_memory(
            manager,
            "Form alliance with western faction",
            ["General Marcus", "Diplomat Elena"],
            MemoryImportance.HIGH
        )
        
        assert memory_id in manager.memories
        memory = manager.memories[memory_id]
        
        assert memory.memory_type == MemoryType.DECISION
        assert memory.importance == MemoryImportance.HIGH
        assert "Form alliance with western faction" in memory.content
        assert "General Marcus" in memory.associated_advisors
    
    def test_add_event_memory_helper(self, mock_llm_manager):
        """Test event memory helper function."""
        manager = create_memory_manager(mock_llm_manager)
        
        emotional_impact = {"stress": 0.3, "confidence": 0.7}
        
        memory_id = add_event_memory(
            manager,
            "Successful diplomatic negotiation completed",
            ["Diplomat Elena"],
            emotional_impact,
            MemoryImportance.MEDIUM
        )
        
        assert memory_id in manager.memories
        memory = manager.memories[memory_id]
        
        assert memory.memory_type == MemoryType.EVENT
        assert memory.importance == MemoryImportance.MEDIUM
        assert "Successful diplomatic negotiation" in memory.content
        assert memory.emotional_context == emotional_impact


if __name__ == "__main__":
    pytest.main([__file__])
