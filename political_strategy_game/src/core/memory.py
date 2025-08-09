"""
Memory system for advisor historical knowledge with decay and manipulation.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field
import json
import uuid
from pathlib import Path


class MemoryType(str, Enum):
    """Types of memories advisors can have."""
    DECISION = "decision"
    CRISIS = "crisis"
    CONSPIRACY = "conspiracy"
    COUP = "coup"
    APPOINTMENT = "appointment"
    RELATIONSHIP = "relationship"
    INTELLIGENCE = "intelligence"


class Memory(BaseModel):
    """Individual memory record for an advisor."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    advisor_id: str
    event_type: MemoryType
    content: str
    emotional_impact: float = Field(ge=0.0, le=1.0)
    reliability: float = Field(default=1.0, ge=0.0, le=1.0)
    decay_rate: float = Field(default=0.02, ge=0.0, le=1.0)
    created_turn: int
    last_accessed_turn: int
    tags: Set[str] = Field(default_factory=set)
    source_advisor_id: Optional[str] = None  # Who told them this info
    
    def decay_memory(self, current_turn: int) -> None:
        """Apply decay to memory reliability based on time passed."""
        turns_passed = current_turn - self.last_accessed_turn
        decay_factor = (1.0 - self.decay_rate) ** turns_passed
        self.reliability = max(0.0, self.reliability * decay_factor)
    
    def access_memory(self, current_turn: int) -> None:
        """Mark memory as accessed, updating last access time."""
        self.last_accessed_turn = current_turn
        # Accessing memory slightly reinforces it
        self.reliability = min(1.0, self.reliability + 0.01)


class AdvisorMemory(BaseModel):
    """Complete memory collection for a single advisor."""
    
    advisor_id: str
    memories: List[Memory] = Field(default_factory=list)
    memory_capacity: int = Field(default=1000)  # Max memories before compression
    
    def add_memory(self, memory: Memory) -> None:
        """Add a new memory to the collection."""
        self.memories.append(memory)
        self._compress_if_needed()
    
    def recall_memories(self, tags: Optional[Set[str]] = None, 
                       event_type: Optional[MemoryType] = None,
                       min_reliability: float = 0.1) -> List[Memory]:
        """Retrieve memories matching criteria."""
        filtered_memories = []
        
        for memory in self.memories:
            # Skip unreliable memories
            if memory.reliability < min_reliability:
                continue
                
            # Filter by tags if specified
            if tags and not tags.intersection(memory.tags):
                continue
                
            # Filter by event type if specified
            if event_type and memory.event_type != event_type:
                continue
                
            filtered_memories.append(memory)
        
        # Sort by relevance (emotional impact + reliability)
        filtered_memories.sort(
            key=lambda m: m.emotional_impact * m.reliability, 
            reverse=True
        )
        
        return filtered_memories
    
    def decay_all_memories(self, current_turn: int) -> int:
        """Apply decay to all memories and return number of forgotten memories."""
        forgotten_count = 0
        remaining_memories = []
        
        for memory in self.memories:
            memory.decay_memory(current_turn)
            if memory.reliability > 0.01:  # Keep memories with minimal reliability
                remaining_memories.append(memory)
            else:
                forgotten_count += 1
        
        self.memories = remaining_memories
        return forgotten_count
    
    def _compress_if_needed(self) -> None:
        """Compress memory collection if it exceeds capacity."""
        if len(self.memories) <= self.memory_capacity:
            return
            
        # Sort by importance (emotional impact * reliability)
        self.memories.sort(
            key=lambda m: m.emotional_impact * m.reliability,
            reverse=True
        )
        
        # Keep only the most important memories
        self.memories = self.memories[:self.memory_capacity]


class MemoryBank(BaseModel):
    """Central memory storage for a civilization."""
    
    civilization_id: str
    advisor_memories: Dict[str, AdvisorMemory] = Field(default_factory=dict)
    shared_memories: List[Memory] = Field(default_factory=list)  # Public knowledge
    
    def get_advisor_memory(self, advisor_id: str) -> AdvisorMemory:
        """Get or create memory collection for an advisor."""
        if advisor_id not in self.advisor_memories:
            self.advisor_memories[advisor_id] = AdvisorMemory(advisor_id=advisor_id)
        return self.advisor_memories[advisor_id]
    
    def add_shared_memory(self, memory: Memory) -> None:
        """Add a memory that all advisors know about."""
        self.shared_memories.append(memory)
        
        # Also add to each advisor's personal memory
        for advisor_memory in self.advisor_memories.values():
            personal_memory = memory.model_copy()
            personal_memory.advisor_id = advisor_memory.advisor_id
            advisor_memory.add_memory(personal_memory)


class MemoryManager:
    """Manages memory persistence and operations across the game."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        self.memory_banks: Dict[str, MemoryBank] = {}
        # Map advisor IDs to civilization IDs for quick lookup
        self._advisor_to_civ_map: Dict[str, str] = {}
    
    def get_memory_bank(self, civilization_id: str) -> MemoryBank:
        """Get or load memory bank for a civilization."""
        if civilization_id not in self.memory_banks:
            self.memory_banks[civilization_id] = self._load_memory_bank(civilization_id)
        return self.memory_banks[civilization_id]
    
    def register_advisor(self, advisor_id: str, civilization_id: str) -> None:
        """Register an advisor as belonging to a specific civilization."""
        self._advisor_to_civ_map[advisor_id] = civilization_id
    
    def store_memory(self, advisor_id: str, memory: Memory) -> bool:
        """Store a memory for an advisor."""
        try:
            # Find which civilization this advisor belongs to
            civilization_id = self._find_civilization_for_advisor(advisor_id)
            if not civilization_id:
                # If we can't find the civilization, try to get it from the memory's advisor
                # For our implementation, we'll use a default civilization mapping
                print(f"Warning: Could not find civilization for advisor {advisor_id}, using default mapping")
                # Extract civilization from advisor if it follows pattern, otherwise use first part or default
                if hasattr(memory, 'civilization_id'):
                    civilization_id = memory.civilization_id
                else:
                    # For testing/simple cases, create a default civilization
                    civilization_id = "default_civ"
                
            memory_bank = self.get_memory_bank(civilization_id)
            advisor_memory = memory_bank.get_advisor_memory(advisor_id)
            advisor_memory.add_memory(memory)
            
            self._save_memory_bank(civilization_id, memory_bank)
            return True
        except Exception as e:
            print(f"Error storing memory: {e}")
            return False
    
    def recall_memories(self, advisor_id: str, tags: Optional[Set[str]] = None) -> List[Memory]:
        """Retrieve memories for an advisor."""
        civilization_id = self._find_civilization_for_advisor(advisor_id)
        if not civilization_id:
            return []
            
        memory_bank = self.get_memory_bank(civilization_id)
        advisor_memory = memory_bank.get_advisor_memory(advisor_id)
        return advisor_memory.recall_memories(tags=tags)
    
    def decay_memories(self, advisor_id: str, current_turn: int) -> int:
        """Apply decay to advisor's memories."""
        civilization_id = self._find_civilization_for_advisor(advisor_id)
        if not civilization_id:
            return 0
            
        memory_bank = self.get_memory_bank(civilization_id)
        advisor_memory = memory_bank.get_advisor_memory(advisor_id)
        forgotten_count = advisor_memory.decay_all_memories(current_turn)
        
        self._save_memory_bank(civilization_id, memory_bank)
        return forgotten_count
    
    def transfer_memories(self, from_advisor: str, to_advisor: str, 
                         filter_tags: Optional[Set[str]] = None) -> bool:
        """Transfer memories between advisors (for information sharing)."""
        try:
            from_memories = self.recall_memories(from_advisor, tags=filter_tags)
            
            for memory in from_memories:
                # Create new memory for recipient with reduced reliability
                transferred_memory = memory.model_copy()
                transferred_memory.id = str(uuid.uuid4())
                transferred_memory.advisor_id = to_advisor
                transferred_memory.reliability *= 0.8  # Information degrades in transfer
                transferred_memory.source_advisor_id = from_advisor
                
                self.store_memory(to_advisor, transferred_memory)
            
            return True
        except Exception as e:
            print(f"Error transferring memories: {e}")
            return False
    
    def _load_memory_bank(self, civilization_id: str) -> MemoryBank:
        """Load memory bank from disk."""
        file_path = self.data_dir / f"{civilization_id}_memories.json"
        
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Convert lists back to sets for tags
                for advisor_id, advisor_memory in data.get("advisor_memories", {}).items():
                    for memory in advisor_memory.get("memories", []):
                        if "tags" in memory and isinstance(memory["tags"], list):
                            memory["tags"] = set(memory["tags"])
                
                for memory in data.get("shared_memories", []):
                    if "tags" in memory and isinstance(memory["tags"], list):
                        memory["tags"] = set(memory["tags"])
                
                return MemoryBank.model_validate(data)
            except Exception as e:
                print(f"Error loading memory bank: {e}")
        
        # Create new memory bank if file doesn't exist or failed to load
        return MemoryBank(civilization_id=civilization_id)
    
    def _save_memory_bank(self, civilization_id: str, memory_bank: MemoryBank) -> None:
        """Save memory bank to disk."""
        file_path = self.data_dir / f"{civilization_id}_memories.json"
        
        try:
            # Convert to dict with proper set handling
            memory_data = memory_bank.model_dump()
            
            # Convert sets to lists for JSON serialization
            for advisor_id, advisor_memory in memory_data.get("advisor_memories", {}).items():
                for memory in advisor_memory.get("memories", []):
                    if "tags" in memory and isinstance(memory["tags"], set):
                        memory["tags"] = list(memory["tags"])
            
            for memory in memory_data.get("shared_memories", []):
                if "tags" in memory and isinstance(memory["tags"], set):
                    memory["tags"] = list(memory["tags"])
            
            with open(file_path, 'w') as f:
                json.dump(memory_data, f, indent=2)
        except Exception as e:
            print(f"Error saving memory bank: {e}")
    
    def _find_civilization_for_advisor(self, advisor_id: str) -> Optional[str]:
        """Find which civilization an advisor belongs to."""
        # Check our mapping first
        if advisor_id in self._advisor_to_civ_map:
            return self._advisor_to_civ_map[advisor_id]
        
        # Fallback: extract from advisor_id pattern (for legacy IDs)
        if "_" in advisor_id:
            civ_id = advisor_id.split("_")[0]
            # Register this mapping for future use
            self._advisor_to_civ_map[advisor_id] = civ_id
            return civ_id
        
        return None
