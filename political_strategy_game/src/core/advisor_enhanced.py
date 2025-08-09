"""
Enhanced advisor system with memory integration.
"""

from typing import Dict, Optional, Set, List, Any
from enum import Enum
from pydantic import BaseModel, Field
import uuid

# Import memory classes directly
from .memory import MemoryManager, Memory, MemoryType

# Re-export existing classes from advisor.py
from .advisor import (
    AdvisorRole, AdvisorStatus, PersonalityProfile, Relationship, Advisor
)


class AdvisorWithMemory(Advisor):
    """Extended advisor class with memory system integration."""
    
    def __init__(self, memory_manager=None, **data):
        super().__init__(**data)
        self._memory_manager = memory_manager
        # Register with memory manager if provided
        if memory_manager and 'civilization_id' in data:
            memory_manager.register_advisor(data.get('id', self.id), data['civilization_id'])
    
    def set_memory_manager(self, memory_manager) -> None:
        """Set the memory manager for this advisor."""
        self._memory_manager = memory_manager
        # Register this advisor with the memory manager
        if memory_manager and hasattr(self, 'civilization_id'):
            memory_manager.register_advisor(self.id, self.civilization_id)
    
    def remember_event(self, event_type: MemoryType, content: str, 
                      emotional_impact: float, current_turn: int,
                      tags: Optional[Set[str]] = None) -> bool:
        """Store a memory of an event."""
        if not self._memory_manager:
            return False
        
        memory = Memory(
            advisor_id=self.id,
            event_type=event_type,
            content=content,
            emotional_impact=emotional_impact,
            created_turn=current_turn,
            last_accessed_turn=current_turn,
            tags=tags or set()
        )
        
        return self._memory_manager.store_memory(self.id, memory)
    
    def recall_memories_about(self, tags: Optional[Set[str]] = None) -> List[Memory]:
        """Recall memories matching criteria."""
        if not self._memory_manager:
            return []
        
        # Get all memories for this advisor
        all_memories = self._memory_manager.recall_memories(self.id, tags=tags)
        
        # Filter by reliability (minimum 0.1)
        return [m for m in all_memories if m.reliability >= 0.1]
    
    def share_secret_with(self, other_advisor_id: str, secret_content: str,
                         current_turn: int) -> bool:
        """Share a secret with another advisor."""
        if not self._memory_manager:
            return False
        
        # Create the secret memory
        secret_memory = Memory(
            advisor_id=self.id,
            event_type=MemoryType.INTELLIGENCE,
            content=secret_content,
            emotional_impact=0.7,  # Secrets are emotionally significant
            created_turn=current_turn,
            last_accessed_turn=current_turn,
            tags={"secret", "shared", other_advisor_id}
        )
        
        # Store for both advisors
        success1 = self._memory_manager.store_memory(self.id, secret_memory)
        success2 = self._memory_manager.transfer_memories(
            self.id, other_advisor_id, filter_tags={"secret"}
        )
        
        if success1 and success2:
            # Update relationship
            relationship = self.get_relationship(other_advisor_id)
            relationship.shared_secrets.add(secret_memory.id)
            relationship.trust = min(1.0, relationship.trust + 0.1)
            return True
        
        return False
    
    def assess_threat_from_memories(self, current_turn: int) -> Dict[str, float]:
        """Assess threats based on memories."""
        if not self._memory_manager:
            return {}
        
        # Recall memories about conspiracies and threats
        threat_memories = self.recall_memories_about(tags={"conspiracy", "threat", "betrayal"})
        
        threat_scores = {}
        for memory in threat_memories:
            # Recent memories are more concerning
            recency_factor = max(0.1, 1.0 - (current_turn - memory.created_turn) * 0.02)
            threat_level = memory.emotional_impact * memory.reliability * recency_factor
            
            # Extract potential threat sources from tags
            for tag in memory.tags:
                if tag.startswith("advisor_") or tag in [advisor_id for advisor_id in self.relationships.keys()]:
                    threat_scores[tag] = max(threat_scores.get(tag, 0.0), threat_level)
        
        return threat_scores
    
    def make_memory_informed_decision(self, options: List[Dict], context: Dict,
                                    current_turn: int) -> Dict:
        """Make a decision informed by relevant memories."""
        if not self._memory_manager or not options:
            return self.make_decision(options, context)
        
        # Recall relevant memories based on context
        context_tags = set(context.get('tags', []))
        relevant_memories = self.recall_memories_about(tags=context_tags)
        
        # Modify option scores based on memories
        scored_options = []
        for option in options:
            base_score = self._score_option(option, context)
            
            # Adjust score based on memories
            memory_adjustment = self._assess_option_with_memories(option, relevant_memories)
            final_score = max(0.0, min(1.0, base_score + memory_adjustment))
            
            scored_options.append((final_score, option))
        
        # Sort and return best option
        scored_options.sort(key=lambda x: x[0], reverse=True)
        return scored_options[0][1]
    
    def _assess_option_with_memories(self, option: Dict, memories: List[Memory]) -> float:
        """Assess how memories should modify an option's score."""
        adjustment = 0.0
        
        option_tags = set(option.get('tags', []))
        
        for memory in memories:
            # Check if memory is relevant to this option
            memory_tags = memory.tags or set()
            
            # Calculate overlap between option tags and memory tags
            tag_overlap = option_tags.intersection(memory_tags)
            if not tag_overlap:
                continue
            
            # Calculate memory impact based on overlap strength
            overlap_strength = len(tag_overlap) / len(option_tags) if option_tags else 0
            memory_impact = memory.emotional_impact * memory.reliability * overlap_strength
            
            # Check for failure or negative tags
            if "failure" in memory_tags or "disaster" in memory_tags:
                adjustment -= memory_impact * 0.4  # Strong negative impact for failures
            elif memory.event_type in [MemoryType.CRISIS, MemoryType.CONSPIRACY]:
                adjustment -= memory_impact * 0.3
            elif "success" in memory_tags or "benefit" in memory_tags:
                adjustment += memory_impact * 0.3
            elif memory.event_type in [MemoryType.DECISION, MemoryType.RELATIONSHIP]:
                # Neutral to slightly positive for regular decisions/relationships
                adjustment += memory_impact * 0.1
        
        return max(-0.5, min(0.5, adjustment))
    
    def update_relationships_from_memories(self, current_turn: int) -> None:
        """Update relationships based on recent memories."""
        if not self._memory_manager:
            return
        
        # Get recent relationship-relevant memories
        relationship_memories = self.recall_memories_about(tags={"relationship", "cooperation", "betrayal"})
        
        for memory in relationship_memories:
            # Skip very old memories
            if current_turn - memory.created_turn > 50:
                continue
            
            # Find which advisor this memory relates to
            for tag in memory.tags:
                if tag.startswith("advisor_") or tag in self.relationships:
                    advisor_id = tag.replace("advisor_", "") if tag.startswith("advisor_") else tag
                    
                    if advisor_id in self.relationships:
                        relationship = self.relationships[advisor_id]
                        
                        # Determine event type from memory content and tags
                        if any(word in memory.content.lower() for word in ["betrayed", "backstab", "deceived"]):
                            relationship.update_relationship(-memory.emotional_impact, "betrayal")
                        elif any(word in memory.content.lower() for word in ["cooperated", "helped", "supported"]):
                            relationship.update_relationship(memory.emotional_impact, "cooperation")
                        elif "conspiracy" in memory.tags:
                            relationship.conspiracy_level = min(1.0, 
                                relationship.conspiracy_level + memory.emotional_impact * 0.1)
    
    def advance_turn_with_memory(self, current_turn: int) -> None:
        """Advance turn with memory-informed updates."""
        # Standard turn advancement
        self.advance_turn(current_turn)
        
        # Memory-informed relationship updates
        self.update_relationships_from_memories(current_turn)
        
        # Decay memories in the memory manager
        if self._memory_manager:
            self._memory_manager.decay_memories(self.id, current_turn)
        
        # Update paranoia based on threat assessment
        threats = self.assess_threat_from_memories(current_turn)
        if threats:
            avg_threat = sum(threats.values()) / len(threats)
            if avg_threat > 0.5:
                self.personality.paranoia = min(1.0, self.personality.paranoia + 0.05)
            elif avg_threat < 0.2:
                self.personality.paranoia = max(0.0, self.personality.paranoia - 0.02)


class AdvisorCouncil(BaseModel):
    """Manages the full council of advisors with memory integration."""
    
    model_config = {"arbitrary_types_allowed": True}
    
    civilization_id: str
    advisors: Dict[str, AdvisorWithMemory] = Field(default_factory=dict)
    current_turn: int = Field(default=0)
    memory_manager: Optional[MemoryManager] = Field(default=None, exclude=True)
    
    def set_memory_manager(self, memory_manager: MemoryManager) -> None:
        """Set memory manager for all advisors."""
        self.memory_manager = memory_manager
        for advisor in self.advisors.values():
            advisor.set_memory_manager(memory_manager)
    
    def add_advisor(self, advisor: AdvisorWithMemory) -> None:
        """Add an advisor to the council."""
        advisor.civilization_id = self.civilization_id
        if self.memory_manager:
            advisor.set_memory_manager(self.memory_manager)
        self.advisors[advisor.id] = advisor
    
    def remove_advisor(self, advisor_id: str, reason: str = "dismissed") -> bool:
        """Remove an advisor from the council."""
        if advisor_id not in self.advisors:
            return False
        
        advisor = self.advisors[advisor_id]
        
        # Update status rather than removing entirely
        if reason == "executed":
            advisor.status = AdvisorStatus.EXECUTED
        elif reason == "imprisoned":
            advisor.status = AdvisorStatus.IMPRISONED
        else:
            advisor.status = AdvisorStatus.DISMISSED
        
        # Create memories for other advisors about this event
        if self.memory_manager:
            removal_memory = Memory(
                advisor_id="council",
                event_type=MemoryType.CRISIS if reason in ["executed", "imprisoned"] else MemoryType.DECISION,
                content=f"Advisor {advisor.name} was {reason}",
                emotional_impact=0.8 if reason in ["executed", "imprisoned"] else 0.4,
                created_turn=self.current_turn,
                last_accessed_turn=self.current_turn,
                tags={"advisor_removal", reason, advisor_id}
            )
            
            for other_advisor in self.advisors.values():
                if other_advisor.id != advisor_id and other_advisor.status == AdvisorStatus.ACTIVE:
                    self.memory_manager.store_memory(other_advisor.id, removal_memory)
        
        return True
    
    def simulate_council_dynamics(self) -> Dict[str, any]:
        """Simulate one turn of council political dynamics."""
        results = {
            "conspiracies_formed": [],
            "relationships_changed": [],
            "secrets_shared": [],
            "threats_detected": []
        }
        
        active_advisors = [a for a in self.advisors.values() if a.status == AdvisorStatus.ACTIVE]
        
        # Assess conspiracy potential
        for advisor in active_advisors:
            conspiracy_scores = advisor.assess_conspiracy_potential(active_advisors)
            
            for target_id, score in conspiracy_scores.items():
                if score > 0.7:  # High conspiracy potential
                    target_advisor = self.advisors.get(target_id)
                    if target_advisor:
                        # Form conspiracy
                        relationship = advisor.get_relationship(target_id)
                        relationship.conspiracy_level = max(relationship.conspiracy_level, score)
                        
                        results["conspiracies_formed"].append({
                            "advisor1": advisor.id,
                            "advisor2": target_id,
                            "conspiracy_level": score
                        })
        
        # Advance all advisors
        for advisor in active_advisors:
            advisor.advance_turn_with_memory(self.current_turn)
        
        self.current_turn += 1
        return results
    
    def get_council_loyalty_report(self) -> Dict[str, float]:
        """Get loyalty levels of all active advisors."""
        return {
            advisor.id: advisor.loyalty_to_leader 
            for advisor in self.advisors.values() 
            if advisor.status == AdvisorStatus.ACTIVE
        }
    
    def detect_coup_risk(self) -> Dict[str, any]:
        """Assess the risk of a coup from current advisors."""
        active_advisors = [a for a in self.advisors.values() if a.status == AdvisorStatus.ACTIVE]
        
        coup_motivations = {}
        potential_conspirators = []
        
        for advisor in active_advisors:
            motivation = advisor.calculate_coup_motivation()
            coup_motivations[advisor.id] = motivation
            
            if motivation >= 0.6:  # Changed from > to >=
                potential_conspirators.append(advisor.id)
        
        # Check for existing conspiracies among high-motivation advisors
        conspiracy_networks = []
        for advisor_id in potential_conspirators:
            advisor = self.advisors[advisor_id]
            for other_id in potential_conspirators:
                if other_id != advisor_id:
                    relationship = advisor.get_relationship(other_id)
                    if relationship.conspiracy_level > 0.5:
                        conspiracy_networks.append((advisor_id, other_id, relationship.conspiracy_level))
        
        risk_level = "LOW"
        if len(potential_conspirators) >= 3 and conspiracy_networks:
            risk_level = "HIGH"
        elif len(potential_conspirators) >= 2:
            risk_level = "MEDIUM"
        
        return {
            "risk_level": risk_level,
            "motivated_advisors": coup_motivations,
            "potential_conspirators": potential_conspirators,
            "conspiracy_networks": conspiracy_networks
        }
