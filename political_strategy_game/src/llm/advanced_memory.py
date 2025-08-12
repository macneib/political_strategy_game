"""
Advanced Memory Integration for LLM Context

This module provides sophisticated memory management to enhance LLM context
with relevant historical information, patterns, and insights for improved
decision-making and consistency in the political strategy game.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
from datetime import datetime, timedelta
import json
import asyncio
import logging
from collections import defaultdict, Counter
import hashlib

from .llm_providers import LLMManager, LLMMessage, LLMResponse
from .advisors import AdvisorRole, AdvisorAI


class MemoryType(Enum):
    """Types of memory stored in the system."""
    DECISION = "decision"
    EVENT = "event" 
    PATTERN = "pattern"
    CONTEXT = "context"
    INSIGHT = "insight"
    RELATIONSHIP = "relationship"
    STRATEGY = "strategy"
    OUTCOME = "outcome"


class MemoryImportance(Enum):
    """Importance levels for memory entries."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class ContextRelevance(Enum):
    """Relevance levels for context retrieval."""
    ESSENTIAL = "essential"
    HIGHLY_RELEVANT = "highly_relevant"
    RELEVANT = "relevant"
    SOMEWHAT_RELEVANT = "somewhat_relevant"
    TANGENTIALLY_RELATED = "tangentially_related"


@dataclass
class MemoryEntry:
    """A single memory entry with metadata and content."""
    memory_id: str
    content: str
    memory_type: MemoryType
    importance: MemoryImportance
    timestamp: datetime
    associated_advisors: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    context_keywords: Set[str] = field(default_factory=set)
    related_decisions: List[str] = field(default_factory=list)
    emotional_context: Dict[str, float] = field(default_factory=dict)
    outcome_impact: Optional[float] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    decay_factor: float = 1.0
    
    def calculate_relevance_score(self, query_keywords: Set[str], 
                                current_advisors: List[str],
                                time_weight: float = 0.3) -> float:
        """Calculate relevance score for this memory entry."""
        # Keyword similarity
        keyword_overlap = len(self.context_keywords.intersection(query_keywords))
        keyword_score = keyword_overlap / max(len(query_keywords), 1) if query_keywords else 0.0
        
        # Advisor relevance
        advisor_overlap = len(set(self.associated_advisors).intersection(set(current_advisors)))
        advisor_score = advisor_overlap / max(len(current_advisors), 1) if current_advisors else 0.0
        
        # Temporal relevance (more recent = higher score)
        time_delta = datetime.now() - self.timestamp
        time_score = max(0.1, 1.0 - (time_delta.days / 30.0))  # Decay over 30 days
        
        # Importance and access patterns
        importance_weights = {
            MemoryImportance.CRITICAL: 1.0,
            MemoryImportance.HIGH: 0.8,
            MemoryImportance.MEDIUM: 0.6,
            MemoryImportance.LOW: 0.4,
            MemoryImportance.MINIMAL: 0.2
        }
        importance_score = importance_weights.get(self.importance, 0.5)
        
        # Access frequency (but with diminishing returns)
        access_score = min(1.0, self.access_count / 10.0)
        
        # Combine scores with weights
        total_score = (
            keyword_score * 0.3 +
            advisor_score * 0.2 +
            time_score * time_weight +
            importance_score * 0.2 +
            access_score * 0.1
        ) * self.decay_factor
        
        return min(1.0, total_score)
    
    def update_access(self):
        """Update access tracking."""
        self.access_count += 1
        self.last_accessed = datetime.now()
    
    def apply_decay(self, decay_rate: float = 0.95):
        """Apply time-based decay to memory importance."""
        self.decay_factor *= decay_rate


@dataclass  
class ContextPackage:
    """A package of contextual information for LLM queries."""
    query_context: str
    relevant_memories: List[MemoryEntry]
    historical_patterns: List[str]
    advisor_insights: Dict[str, str]
    decision_precedents: List[str]
    estimated_tokens: int
    relevance_scores: Dict[str, float]
    
    def to_llm_context(self, max_tokens: int = 1500) -> str:
        """Convert to formatted LLM context string."""
        context_parts = []
        
        # Add query context
        if self.query_context:
            context_parts.append(f"CURRENT CONTEXT:\n{self.query_context}\n")
        
        # Add high-relevance memories
        if self.relevant_memories:
            high_relevance_memories = [m for m in self.relevant_memories[:5]]
            if high_relevance_memories:
                context_parts.append("RELEVANT HISTORICAL CONTEXT:")
                for memory in high_relevance_memories:
                    context_parts.append(f"- {memory.content}")
                context_parts.append("")
        
        # Add patterns
        if self.historical_patterns:
            context_parts.append("IDENTIFIED PATTERNS:")
            for pattern in self.historical_patterns[:3]:
                context_parts.append(f"- {pattern}")
            context_parts.append("")
        
        # Add advisor insights
        if self.advisor_insights:
            context_parts.append("ADVISOR INSIGHTS:")
            for advisor, insight in list(self.advisor_insights.items())[:3]:
                context_parts.append(f"- {advisor}: {insight}")
            context_parts.append("")
        
        # Add decision precedents
        if self.decision_precedents:
            context_parts.append("RELEVANT PRECEDENTS:")
            for precedent in self.decision_precedents[:3]:
                context_parts.append(f"- {precedent}")
            context_parts.append("")
        
        # Join and trim to token limit (rough approximation)
        full_context = "\n".join(context_parts)
        
        # Rough token estimation (4 characters per token)
        if len(full_context) > max_tokens * 4:
            # Trim content while keeping structure
            trimmed_parts = []
            current_length = 0
            
            for part in context_parts:
                if current_length + len(part) <= max_tokens * 4:
                    trimmed_parts.append(part)
                    current_length += len(part)
                else:
                    trimmed_parts.append("... (context truncated for token limit)")
                    break
            
            full_context = "\n".join(trimmed_parts)
        
        return full_context


class AdvancedMemoryManager:
    """Advanced memory management system for enhanced LLM context."""
    
    def __init__(self, llm_manager: LLMManager, max_memory_entries: int = 10000):
        self.llm_manager = llm_manager
        self.max_memory_entries = max_memory_entries
        self.logger = logging.getLogger("memory_manager")
        
        # Memory storage
        self.memories: Dict[str, MemoryEntry] = {}
        self.memory_index: Dict[str, Set[str]] = defaultdict(set)  # keyword -> memory_ids
        self.advisor_memories: Dict[str, Set[str]] = defaultdict(set)  # advisor -> memory_ids
        self.temporal_index: Dict[str, Set[str]] = defaultdict(set)  # date -> memory_ids
        
        # Pattern recognition
        self.identified_patterns: List[str] = []
        self.pattern_confidence: Dict[str, float] = {}
        
        # Context optimization
        self.context_cache: Dict[str, ContextPackage] = {}
        self.cache_timeout = timedelta(hours=1)
        
        # Memory maintenance
        self.last_cleanup = datetime.now()
        self.cleanup_interval = timedelta(hours=6)
        
        self.logger.info("Advanced Memory Manager initialized")
    
    def add_memory(self, content: str, memory_type: MemoryType, 
                  importance: MemoryImportance, associated_advisors: List[str] = None,
                  tags: Set[str] = None, emotional_context: Dict[str, float] = None) -> str:
        """Add a new memory entry."""
        memory_id = self._generate_memory_id(content)
        
        # Extract keywords from content
        keywords = self._extract_keywords(content)
        
        memory = MemoryEntry(
            memory_id=memory_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            timestamp=datetime.now(),
            associated_advisors=associated_advisors or [],
            tags=tags or set(),
            context_keywords=keywords,
            emotional_context=emotional_context or {}
        )
        
        # Store memory
        self.memories[memory_id] = memory
        
        # Update indexes
        for keyword in keywords:
            self.memory_index[keyword.lower()].add(memory_id)
        
        for advisor in memory.associated_advisors:
            self.advisor_memories[advisor].add(memory_id)
        
        date_key = memory.timestamp.strftime("%Y-%m-%d")
        self.temporal_index[date_key].add(memory_id)
        
        # Trigger cleanup if needed
        if len(self.memories) > self.max_memory_entries:
            self._cleanup_old_memories()
        
        self.logger.debug(f"Added memory {memory_id}: {content[:50]}...")
        return memory_id
    
    async def get_enhanced_context(self, query: str, current_advisors: List[str],
                                 context_type: str = "general", 
                                 max_context_tokens: int = 1500) -> ContextPackage:
        """Get enhanced context for LLM query."""
        # Check cache first
        cache_key = hashlib.md5(f"{query}_{context_type}_{','.join(sorted(current_advisors))}".encode(), usedforsecurity=False).hexdigest()  # nosec B324 - MD5 used for cache key, not security
        
        if cache_key in self.context_cache:
            cached_context = self.context_cache[cache_key]
            if datetime.now() - cached_context.relevant_memories[0].timestamp < self.cache_timeout:
                return cached_context
        
        # Extract query keywords
        query_keywords = self._extract_keywords(query)
        
        # Find relevant memories
        relevant_memories = self._find_relevant_memories(
            query_keywords, current_advisors, limit=10
        )
        
        # Get historical patterns
        patterns = await self._identify_contextual_patterns(query, relevant_memories)
        
        # Get advisor-specific insights
        advisor_insights = await self._get_advisor_insights(
            query, current_advisors, relevant_memories
        )
        
        # Find decision precedents
        precedents = self._find_decision_precedents(query_keywords, relevant_memories)
        
        # Calculate relevance scores
        relevance_scores = {
            memory.memory_id: memory.calculate_relevance_score(query_keywords, current_advisors)
            for memory in relevant_memories
        }
        
        # Estimate token usage
        estimated_tokens = self._estimate_context_tokens(
            query, relevant_memories, patterns, advisor_insights, precedents
        )
        
        # Create context package
        context_package = ContextPackage(
            query_context=query,
            relevant_memories=relevant_memories,
            historical_patterns=patterns,
            advisor_insights=advisor_insights,
            decision_precedents=precedents,
            estimated_tokens=estimated_tokens,
            relevance_scores=relevance_scores
        )
        
        # Cache result
        self.context_cache[cache_key] = context_package
        
        # Update memory access tracking
        for memory in relevant_memories:
            memory.update_access()
        
        return context_package
    
    def _generate_memory_id(self, content: str) -> str:
        """Generate unique memory ID."""
        timestamp = datetime.now().isoformat()
        content_hash = hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()[:8]  # nosec B324 - MD5 used for content hash, not security
        return f"mem_{timestamp}_{content_hash}"
    
    def _extract_keywords(self, content: str) -> Set[str]:
        """Extract important keywords from content."""
        # Simple keyword extraction - could be enhanced with NLP
        words = content.lower().split()
        
        # Filter out common words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'a', 'an', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'we', 'they', 'our', 'their'
        }
        
        # Extract meaningful words (3+ characters, not stop words)
        keywords = {
            word.strip('.,!?;:"()[]{}')
            for word in words
            if len(word) >= 3 and word not in stop_words
        }
        
        # Add common political/strategy terms that might be important
        important_terms = {
            'military', 'diplomatic', 'economic', 'political', 'strategy', 'policy',
            'decision', 'alliance', 'conflict', 'negotiation', 'power', 'influence',
            'faction', 'advisor', 'council', 'stability', 'legitimacy', 'resources'
        }
        
        keywords.update(word for word in important_terms if word in content.lower())
        
        return keywords
    
    def _find_relevant_memories(self, query_keywords: Set[str], 
                              current_advisors: List[str], limit: int = 10) -> List[MemoryEntry]:
        """Find memories relevant to the query."""
        candidate_memory_ids = set()
        
        # Find memories by keyword overlap
        for keyword in query_keywords:
            candidate_memory_ids.update(self.memory_index.get(keyword.lower(), set()))
        
        # Find memories by advisor association
        for advisor in current_advisors:
            candidate_memory_ids.update(self.advisor_memories.get(advisor, set()))
        
        # Score and rank memories
        scored_memories = []
        for memory_id in candidate_memory_ids:
            if memory_id in self.memories:
                memory = self.memories[memory_id]
                score = memory.calculate_relevance_score(query_keywords, current_advisors)
                scored_memories.append((score, memory))
        
        # Sort by relevance and return top results
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for score, memory in scored_memories[:limit]]
    
    async def _identify_contextual_patterns(self, query: str, 
                                          relevant_memories: List[MemoryEntry]) -> List[str]:
        """Use LLM to identify patterns in relevant memories."""
        if not relevant_memories:
            return []
        
        # Prepare memory content for analysis
        memory_contents = [memory.content for memory in relevant_memories[:5]]
        
        prompt = f"""Analyze the following historical information and identify patterns relevant to the current query.

CURRENT QUERY: {query}

HISTORICAL INFORMATION:
{chr(10).join(f"- {content}" for content in memory_contents)}

Identify 2-3 key patterns, trends, or recurring themes that could inform decision-making. Focus on:
1. Strategic patterns
2. Outcome patterns
3. Behavioral patterns

Return each pattern as a concise statement (one sentence each)."""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="user", content=prompt)
            ], max_tokens=300, temperature=0.7)
            
            if response.content:
                # Extract patterns from response
                patterns = [
                    line.strip().lstrip('123456789.- ')
                    for line in response.content.split('\n')
                    if line.strip() and len(line.strip()) > 10
                ]
                
                return patterns[:3]  # Limit to 3 patterns
                
        except Exception as e:
            self.logger.error(f"Failed to identify patterns: {e}")
        
        return []
    
    async def _get_advisor_insights(self, query: str, current_advisors: List[str],
                                  relevant_memories: List[MemoryEntry]) -> Dict[str, str]:
        """Get advisor-specific insights from memory."""
        insights = {}
        
        for advisor in current_advisors[:3]:  # Limit to 3 advisors
            # Find memories specifically associated with this advisor
            advisor_memories = [
                memory for memory in relevant_memories
                if advisor in memory.associated_advisors
            ]
            
            if advisor_memories:
                memory_content = "\n".join([f"- {memory.content}" for memory in advisor_memories[:3]])
                
                prompt = f"""Based on historical context for {advisor}, provide a brief insight relevant to the current query.

QUERY: {query}

HISTORICAL CONTEXT FOR {advisor}:
{memory_content}

Provide one concise insight (1-2 sentences) that {advisor} would find relevant based on this history."""
                
                try:
                    response = await self.llm_manager.generate([
                        LLMMessage(role="user", content=prompt)
                    ], max_tokens=100, temperature=0.6)
                    
                    if response.content:
                        insights[advisor] = response.content.strip()
                        
                except Exception as e:
                    self.logger.error(f"Failed to get insight for {advisor}: {e}")
        
        return insights
    
    def _find_decision_precedents(self, query_keywords: Set[str], 
                                relevant_memories: List[MemoryEntry]) -> List[str]:
        """Find decision precedents from memory."""
        decision_memories = [
            memory for memory in relevant_memories
            if memory.memory_type == MemoryType.DECISION and memory.outcome_impact is not None
        ]
        
        # Sort by outcome impact and recency
        decision_memories.sort(
            key=lambda m: (m.outcome_impact or 0.0, m.timestamp),
            reverse=True
        )
        
        precedents = []
        for memory in decision_memories[:3]:
            if memory.outcome_impact and memory.outcome_impact > 0.5:
                precedents.append(f"Previous decision: {memory.content} (Impact: {memory.outcome_impact:.1f})")
        
        return precedents
    
    def _estimate_context_tokens(self, query: str, memories: List[MemoryEntry],
                               patterns: List[str], insights: Dict[str, str],
                               precedents: List[str]) -> int:
        """Estimate token usage for context package."""
        # Rough estimation: 1 token ≈ 4 characters
        total_chars = len(query)
        
        total_chars += sum(len(memory.content) for memory in memories[:5])
        total_chars += sum(len(pattern) for pattern in patterns)
        total_chars += sum(len(insight) for insight in insights.values())
        total_chars += sum(len(precedent) for precedent in precedents)
        
        # Add formatting overhead
        total_chars += 200
        
        return total_chars // 4
    
    def add_decision_outcome(self, memory_id: str, outcome_impact: float):
        """Add outcome information to a decision memory."""
        if memory_id in self.memories:
            self.memories[memory_id].outcome_impact = outcome_impact
            self.logger.debug(f"Updated outcome for memory {memory_id}: {outcome_impact}")
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory system statistics."""
        total_memories = len(self.memories)
        
        # Count by type (convert enum keys to string values)
        type_counts = Counter(memory.memory_type.value for memory in self.memories.values())
        
        # Count by importance (convert enum keys to string values)
        importance_counts = Counter(memory.importance.value for memory in self.memories.values())
        
        # Calculate average relevance scores
        recent_memories = [
            memory for memory in self.memories.values()
            if datetime.now() - memory.timestamp < timedelta(days=7)
        ]
        
        avg_access_count = sum(memory.access_count for memory in self.memories.values()) / max(total_memories, 1)
        
        return {
            "total_memories": total_memories,
            "recent_memories_7d": len(recent_memories),
            "memory_types": dict(type_counts),
            "importance_distribution": dict(importance_counts),
            "average_access_count": avg_access_count,
            "unique_keywords": len(self.memory_index),
            "cached_contexts": len(self.context_cache),
            "last_cleanup": self.last_cleanup.isoformat()
        }
    
    def _cleanup_old_memories(self):
        """Clean up old and low-relevance memories."""
        # Apply decay to all memories
        for memory in self.memories.values():
            days_old = (datetime.now() - memory.timestamp).days
            decay_rate = max(0.5, 1.0 - (days_old / 100.0))  # Stronger decay for older memories
            memory.apply_decay(decay_rate)
        
        # Remove memories with very low decay factors or minimal importance
        memories_to_remove = [
            memory_id for memory_id, memory in self.memories.items()
            if (memory.decay_factor < 0.1 and memory.importance == MemoryImportance.MINIMAL) or
               (datetime.now() - memory.timestamp).days > 90
        ]
        
        # Keep the most important memories even if old
        if len(self.memories) - len(memories_to_remove) < self.max_memory_entries * 0.8:
            # Sort by importance and recency, keep top ones
            sorted_memories = sorted(
                self.memories.items(),
                key=lambda x: (x[1].importance.value, x[1].timestamp),
                reverse=True
            )
            
            keep_count = int(self.max_memory_entries * 0.8)
            memories_to_keep = {memory_id for memory_id, memory in sorted_memories[:keep_count]}
            memories_to_remove = [
                memory_id for memory_id in self.memories.keys()
                if memory_id not in memories_to_keep
            ]
        
        # Remove selected memories
        for memory_id in memories_to_remove[:len(memories_to_remove)//2]:  # Remove only half at a time
            self._remove_memory(memory_id)
        
        # Clear old cache entries
        current_time = datetime.now()
        old_cache_keys = [
            key for key, context in self.context_cache.items()
            if current_time - context.relevant_memories[0].timestamp > self.cache_timeout
        ]
        
        for key in old_cache_keys:
            del self.context_cache[key]
        
        self.last_cleanup = datetime.now()
        self.logger.info(f"Memory cleanup completed. Removed {len(memories_to_remove)//2} memories")
    
    def _remove_memory(self, memory_id: str):
        """Remove a memory and update all indexes."""
        if memory_id not in self.memories:
            return
        
        memory = self.memories[memory_id]
        
        # Remove from keyword index
        for keyword in memory.context_keywords:
            self.memory_index[keyword.lower()].discard(memory_id)
            if not self.memory_index[keyword.lower()]:
                del self.memory_index[keyword.lower()]
        
        # Remove from advisor index
        for advisor in memory.associated_advisors:
            self.advisor_memories[advisor].discard(memory_id)
            if not self.advisor_memories[advisor]:
                del self.advisor_memories[advisor]
        
        # Remove from temporal index
        date_key = memory.timestamp.strftime("%Y-%m-%d")
        self.temporal_index[date_key].discard(memory_id)
        if not self.temporal_index[date_key]:
            del self.temporal_index[date_key]
        
        # Remove the memory itself
        del self.memories[memory_id]


# Integration helper functions
def create_memory_manager(llm_manager: LLMManager) -> AdvancedMemoryManager:
    """Create and configure a memory manager."""
    return AdvancedMemoryManager(llm_manager, max_memory_entries=10000)


def add_decision_memory(memory_manager: AdvancedMemoryManager, 
                      decision: str, advisors: List[str],
                      importance: MemoryImportance = MemoryImportance.MEDIUM) -> str:
    """Helper to add decision memory."""
    return memory_manager.add_memory(
        content=f"Decision made: {decision}",
        memory_type=MemoryType.DECISION,
        importance=importance,
        associated_advisors=advisors,
        tags={"decision", "strategy"}
    )


def add_event_memory(memory_manager: AdvancedMemoryManager,
                    event: str, advisors: List[str], emotional_impact: Dict[str, float] = None,
                    importance: MemoryImportance = MemoryImportance.MEDIUM) -> str:
    """Helper to add event memory."""
    return memory_manager.add_memory(
        content=f"Event occurred: {event}",
        memory_type=MemoryType.EVENT,
        importance=importance,
        associated_advisors=advisors,
        emotional_context=emotional_impact or {},
        tags={"event", "historical"}
    )
