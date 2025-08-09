"""
Memory factory for generating test data and realistic memory scenarios.
"""

import random
from typing import List, Set
from enum import Enum

from .memory import Memory, MemoryType, AdvisorMemory, MemoryBank


class MemoryScenario(str, Enum):
    """Predefined memory scenarios for testing."""
    PEACEFUL_REIGN = "peaceful_reign"
    CIVIL_UNREST = "civil_unrest"  
    EXTERNAL_WAR = "external_war"
    ECONOMIC_CRISIS = "economic_crisis"
    CORRUPTION_SCANDAL = "corruption_scandal"
    SUCCESSION_CRISIS = "succession_crisis"


class MemoryFactory:
    """Factory for creating realistic memory data for testing and scenarios."""
    
    # Sample memory templates for different scenarios
    MEMORY_TEMPLATES = {
        MemoryType.DECISION: [
            "Leader approved my proposal for {subject}",
            "Leader rejected my recommendation on {subject}",  
            "Council voted {vote_result} on the {subject} proposal",
            "I advised {action} regarding {subject}",
            "Leader chose {alternative} over my {subject} advice",
        ],
        MemoryType.CRISIS: [
            "The {crisis_type} crisis threatened our stability",
            "Emergency council convened during {crisis_type}",
            "I helped resolve the {crisis_type} situation",
            "My response to {crisis_type} was {response_type}",
            "The {crisis_type} crisis revealed {revelation}",
        ],
        MemoryType.CONSPIRACY: [
            "I suspect {advisor_name} is plotting something",
            "Overheard whispers about {conspiracy_subject}",
            "Secret meeting between {advisor_name} and {advisor_name2}",
            "Evidence suggests conspiracy against {target}",
            "I was approached to join a plot against {target}",
        ],
        MemoryType.COUP: [
            "Attempted coup by {faction} faction failed",
            "I supported the coup against {target}",
            "I remained loyal during the {faction} uprising",
            "Coup succeeded - new leadership established",
            "Warning signs of {faction} coup were ignored",
        ],
        MemoryType.APPOINTMENT: [
            "New advisor {advisor_name} appointed to {role}",
            "I recommended {advisor_name} for {role} position",
            "Opposed the appointment of {advisor_name}",
            "Ceremony welcoming {advisor_name} to council",
            "Former {role} advisor departed under suspicion",
        ],
        MemoryType.RELATIONSHIP: [
            "Built trust with {advisor_name} through {activity}",
            "Conflict with {advisor_name} over {subject}",
            "Alliance formed with {advisor_name} faction",
            "Betrayed by {advisor_name} in {situation}",
            "Reconciled with {advisor_name} after {event}",
        ],
        MemoryType.INTELLIGENCE: [
            "Learned {information} from {source}",
            "Intercepted message about {subject}",
            "Spy network reports {intelligence}",
            "Discovered secret about {target}",
            "Intelligence suggests {threat} is imminent",
        ],
    }
    
    SUBJECTS = [
        "taxation policy", "military expansion", "trade agreements", 
        "religious reforms", "infrastructure projects", "diplomatic missions",
        "border defenses", "agricultural subsidies", "judicial reforms",
        "education funding", "temple construction", "merchant regulations"
    ]
    
    CRISIS_TYPES = [
        "famine", "plague", "invasion", "rebellion", "natural disaster",
        "economic collapse", "religious schism", "succession dispute",
        "border conflict", "trade embargo", "civil war", "foreign intrigue"
    ]
    
    ADVISOR_NAMES = [
        "General Marcus", "Treasurer Elena", "Ambassador Chen", 
        "High Priest Amal", "Spymaster Vera", "Judge Hadrian",
        "Admiral Zara", "Scholar Dimitri", "Merchant Yasmin",
        "Engineer Kai", "Diplomat Rosa", "Cavalry Captain Bjorn"
    ]
    
    @classmethod
    def create_memory(cls, advisor_id: str, event_type: MemoryType, 
                     current_turn: int, **kwargs) -> Memory:
        """Create a single realistic memory."""
        template = random.choice(cls.MEMORY_TEMPLATES[event_type])
        
        # Fill in template variables
        content = cls._fill_template(template, **kwargs)
        
        # Generate realistic memory attributes
        emotional_impact = cls._generate_emotional_impact(event_type)
        reliability = random.uniform(0.7, 1.0)  # Start with good reliability
        decay_rate = cls._generate_decay_rate(event_type)
        created_turn = current_turn - random.randint(0, 20)  # Memory from recent past
        tags = cls._generate_tags(event_type, content)
        
        return Memory(
            advisor_id=advisor_id,
            event_type=event_type,
            content=content,
            emotional_impact=emotional_impact,
            reliability=reliability,
            decay_rate=decay_rate,
            created_turn=created_turn,
            last_accessed_turn=created_turn,
            tags=tags
        )
    
    @classmethod
    def create_memory_set(cls, advisor_id: str, scenario: MemoryScenario, 
                         current_turn: int, memory_count: int = 20) -> List[Memory]:
        """Create a set of related memories for a specific scenario."""
        memories = []
        
        # Define memory distributions for different scenarios
        distributions = {
            MemoryScenario.PEACEFUL_REIGN: {
                MemoryType.DECISION: 0.4,
                MemoryType.APPOINTMENT: 0.2,
                MemoryType.RELATIONSHIP: 0.3,
                MemoryType.INTELLIGENCE: 0.1,
            },
            MemoryScenario.CIVIL_UNREST: {
                MemoryType.CRISIS: 0.3,
                MemoryType.CONSPIRACY: 0.2,
                MemoryType.DECISION: 0.2,
                MemoryType.INTELLIGENCE: 0.2,
                MemoryType.RELATIONSHIP: 0.1,
            },
            MemoryScenario.EXTERNAL_WAR: {
                MemoryType.DECISION: 0.3,
                MemoryType.CRISIS: 0.3,
                MemoryType.INTELLIGENCE: 0.2,
                MemoryType.RELATIONSHIP: 0.2,
            },
            MemoryScenario.SUCCESSION_CRISIS: {
                MemoryType.CONSPIRACY: 0.3,
                MemoryType.COUP: 0.2,
                MemoryType.RELATIONSHIP: 0.2,
                MemoryType.DECISION: 0.2,
                MemoryType.INTELLIGENCE: 0.1,
            }
        }
        
        distribution = distributions.get(scenario, distributions[MemoryScenario.PEACEFUL_REIGN])
        
        for _ in range(memory_count):
            # Choose memory type based on scenario distribution
            event_type = cls._weighted_choice(distribution)
            memory = cls.create_memory(advisor_id, event_type, current_turn)
            memories.append(memory)
        
        return memories
    
    @classmethod
    def create_advisor_memory(cls, advisor_id: str, scenario: MemoryScenario,
                            current_turn: int, memory_count: int = 50) -> AdvisorMemory:
        """Create a complete AdvisorMemory with scenario-appropriate memories."""
        advisor_memory = AdvisorMemory(advisor_id=advisor_id)
        
        memories = cls.create_memory_set(advisor_id, scenario, current_turn, memory_count)
        for memory in memories:
            advisor_memory.add_memory(memory)
        
        return advisor_memory
    
    @classmethod
    def create_memory_bank(cls, civilization_id: str, advisor_ids: List[str],
                          scenario: MemoryScenario = MemoryScenario.PEACEFUL_REIGN,
                          current_turn: int = 100) -> MemoryBank:
        """Create a complete MemoryBank for testing with multiple advisors."""
        memory_bank = MemoryBank(civilization_id=civilization_id)
        
        for advisor_id in advisor_ids:
            advisor_memory = cls.create_advisor_memory(advisor_id, scenario, current_turn)
            memory_bank.advisor_memories[advisor_id] = advisor_memory
        
        # Add some shared memories that all advisors know
        shared_memory_count = random.randint(5, 15)
        for _ in range(shared_memory_count):
            event_type = random.choice(list(MemoryType))
            shared_memory = cls.create_memory("shared", event_type, current_turn)
            memory_bank.add_shared_memory(shared_memory)
        
        return memory_bank
    
    @classmethod
    def _fill_template(cls, template: str, **kwargs) -> str:
        """Fill memory template with appropriate values."""
        replacements = {
            "subject": random.choice(cls.SUBJECTS),
            "crisis_type": random.choice(cls.CRISIS_TYPES),
            "advisor_name": random.choice(cls.ADVISOR_NAMES),
            "advisor_name2": random.choice(cls.ADVISOR_NAMES),
            "vote_result": random.choice(["favorably", "unfavorably", "with conditions"]),
            "action": random.choice(["caution", "aggressive action", "diplomacy", "investigation"]),
            "alternative": random.choice(["military action", "diplomatic solution", "economic measures"]),
            "response_type": random.choice(["swift", "cautious", "decisive", "controversial"]),
            "revelation": random.choice(["corruption", "foreign influence", "internal treachery"]),
            "conspiracy_subject": random.choice(["regime change", "policy manipulation", "foreign deals"]),
            "target": random.choice(["the leader", "our faction", "rival advisors"]),
            "faction": random.choice(["military", "religious", "merchant", "noble"]),
            "role": random.choice(["military", "economic", "diplomatic", "intelligence"]),
            "activity": random.choice(["collaboration", "crisis management", "mutual support"]),
            "situation": random.choice(["council vote", "crisis response", "policy debate"]),
            "event": random.choice(["misunderstanding", "external pressure", "mutual compromise"]),
            "information": random.choice(["enemy troop movements", "trade route changes", "political shifts"]),
            "source": random.choice(["spy network", "diplomatic contacts", "merchant reports"]),
            "intelligence": random.choice(["invasion preparations", "internal unrest", "economic troubles"]),
            "threat": random.choice(["invasion", "coup", "economic crisis", "natural disaster"]),
        }
        
        # Add any additional kwargs
        replacements.update(kwargs)
        
        try:
            return template.format(**replacements)
        except KeyError:
            # If template has unfilled variables, return as-is
            return template
    
    @classmethod
    def _generate_emotional_impact(cls, event_type: MemoryType) -> float:
        """Generate realistic emotional impact based on event type."""
        impact_ranges = {
            MemoryType.DECISION: (0.2, 0.7),
            MemoryType.CRISIS: (0.6, 1.0),
            MemoryType.CONSPIRACY: (0.5, 0.9),
            MemoryType.COUP: (0.8, 1.0),
            MemoryType.APPOINTMENT: (0.3, 0.6),
            MemoryType.RELATIONSHIP: (0.4, 0.8),
            MemoryType.INTELLIGENCE: (0.3, 0.7),
        }
        
        min_impact, max_impact = impact_ranges.get(event_type, (0.3, 0.7))
        return random.uniform(min_impact, max_impact)
    
    @classmethod
    def _generate_decay_rate(cls, event_type: MemoryType) -> float:
        """Generate realistic decay rate based on event type."""
        # More significant events decay slower
        decay_ranges = {
            MemoryType.DECISION: (0.015, 0.03),
            MemoryType.CRISIS: (0.005, 0.015),  # Crises are memorable
            MemoryType.CONSPIRACY: (0.01, 0.02),
            MemoryType.COUP: (0.001, 0.01),  # Coups are very memorable
            MemoryType.APPOINTMENT: (0.02, 0.04),
            MemoryType.RELATIONSHIP: (0.01, 0.025),
            MemoryType.INTELLIGENCE: (0.025, 0.04),  # Intelligence fades quickly
        }
        
        min_decay, max_decay = decay_ranges.get(event_type, (0.015, 0.025))
        return random.uniform(min_decay, max_decay)
    
    @classmethod
    def _generate_tags(cls, event_type: MemoryType, content: str) -> Set[str]:
        """Generate relevant tags for a memory based on type and content."""
        tags = {event_type.value}
        
        # Add tags based on content keywords
        if any(word in content.lower() for word in ["military", "war", "invasion", "defense"]):
            tags.add("military")
        if any(word in content.lower() for word in ["economic", "trade", "taxation", "wealth"]):
            tags.add("economic")
        if any(word in content.lower() for word in ["diplomatic", "ambassador", "foreign"]):
            tags.add("diplomatic")
        if any(word in content.lower() for word in ["religious", "temple", "priest", "faith"]):
            tags.add("religious")
        if any(word in content.lower() for word in ["corruption", "scandal", "betrayal"]):
            tags.add("negative")
        if any(word in content.lower() for word in ["success", "victory", "triumph"]):
            tags.add("positive")
        
        return tags
    
    @classmethod
    def _weighted_choice(cls, weights: dict) -> MemoryType:
        """Choose a memory type based on weighted probabilities."""
        total = sum(weights.values())
        r = random.uniform(0, total)
        
        cumulative = 0
        for choice, weight in weights.items():
            cumulative += weight
            if r <= cumulative:
                return choice
        
        # Fallback
        return list(weights.keys())[0]
