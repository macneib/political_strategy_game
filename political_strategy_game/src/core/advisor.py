"""
Advisor personality system with traits, relationships, and decision-making.
"""

from typing import Dict, Optional, Set, List
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class AdvisorRole(str, Enum):
    """Different advisor roles in the government."""
    MILITARY = "military"
    ECONOMIC = "economic"
    DIPLOMATIC = "diplomatic"
    CULTURAL = "cultural"
    RELIGIOUS = "religious"
    SECURITY = "security"
    SCIENTIFIC = "scientific"


class AdvisorStatus(str, Enum):
    """Current status of an advisor."""
    ACTIVE = "active"
    DISMISSED = "dismissed"
    EXECUTED = "executed"
    RETIRED = "retired"
    IMPRISONED = "imprisoned"


class PersonalityProfile(BaseModel):
    """Personality traits that influence advisor behavior."""
    
    ambition: float = Field(default=0.5, ge=0.0, le=1.0, 
                           description="Drive for personal power and advancement")
    loyalty: float = Field(default=0.5, ge=0.0, le=1.0,
                          description="Dedication to current leader")
    ideology: str = Field(default="pragmatic",
                         description="Political/philosophical belief system")
    corruption: float = Field(default=0.0, ge=0.0, le=1.0,
                             description="Willingness to engage in corrupt practices")
    pragmatism: float = Field(default=0.5, ge=0.0, le=1.0,
                             description="Focus on practical vs idealistic solutions")
    paranoia: float = Field(default=0.0, ge=0.0, le=1.0,
                           description="Suspicion and fear of threats")
    charisma: float = Field(default=0.5, ge=0.0, le=1.0,
                           description="Ability to influence others")
    competence: float = Field(default=0.5, ge=0.0, le=1.0,
                             description="Skill and effectiveness in their role")
    
    def compatibility_score(self, other: 'PersonalityProfile') -> float:
        """Calculate compatibility between two personalities (0.0 to 1.0)."""
        # Factors that create compatibility
        ideology_match = 1.0 if self.ideology == other.ideology else 0.5
        pragmatism_match = 1.0 - abs(self.pragmatism - other.pragmatism)
        corruption_match = 1.0 - abs(self.corruption - other.corruption)
        
        # Factors that create conflict
        ambition_conflict = abs(self.ambition - other.ambition) * 0.5
        paranoia_factor = (self.paranoia + other.paranoia) * 0.3
        
        base_compatibility = (ideology_match + pragmatism_match + corruption_match) / 3
        conflict_penalty = ambition_conflict + paranoia_factor
        
        return max(0.0, min(1.0, base_compatibility - conflict_penalty))


class Relationship(BaseModel):
    """Relationship between two advisors."""
    
    advisor_id: str
    target_advisor_id: str
    trust: float = Field(default=0.0, ge=-1.0, le=1.0,
                        description="Trust level (-1 distrust, +1 full trust)")
    influence: float = Field(default=0.0, ge=0.0, le=1.0,
                            description="How much influence target has over advisor")
    conspiracy_level: float = Field(default=0.0, ge=0.0, le=1.0,
                                   description="Level of active conspiracy together")
    shared_secrets: Set[str] = Field(default_factory=set,
                                    description="Memory IDs of shared secret information")
    
    def update_relationship(self, event_impact: float, event_type: str) -> None:
        """Update relationship based on a political event."""
        if event_type in ["betrayal", "exposure"]:
            self.trust = max(-1.0, self.trust - abs(event_impact))
            self.conspiracy_level *= 0.5  # Reduce conspiracy after betrayal
        elif event_type in ["cooperation", "mutual_benefit"]:
            self.trust = min(1.0, self.trust + event_impact * 0.5)
            if self.trust > 0.7:
                self.conspiracy_level = min(1.0, self.conspiracy_level + 0.1)
        elif event_type == "conflict":
            self.trust = max(-1.0, self.trust - event_impact * 0.3)
            self.influence *= 0.9
    
    def decay_relationship(self, decay_rate: float = 0.01) -> None:
        """Apply natural decay to relationship over time."""
        # Trust slowly decays toward neutral without interaction
        if self.trust > 0:
            self.trust = max(0.0, self.trust - decay_rate)
        elif self.trust < 0:
            self.trust = min(0.0, self.trust + decay_rate)
        
        # Conspiracy levels decay without active reinforcement
        self.conspiracy_level = max(0.0, self.conspiracy_level - decay_rate * 2)


class Advisor(BaseModel):
    """Core advisor class with personality, relationships, and game state."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: AdvisorRole
    civilization_id: str
    personality: PersonalityProfile
    status: AdvisorStatus = AdvisorStatus.ACTIVE
    
    # Political metrics
    influence: float = Field(default=0.5, ge=0.0, le=1.0,
                            description="Current political influence in government")
    loyalty_to_leader: float = Field(default=0.5, ge=0.0, le=1.0,
                                    description="Loyalty to current leader")
    public_support: float = Field(default=0.5, ge=0.0, le=1.0,
                                 description="Support from the population")
    
    # Relationships with other advisors
    relationships: Dict[str, Relationship] = Field(default_factory=dict)
    
    # Historical tracking
    turns_in_office: int = Field(default=0)
    appointed_by_leader: Optional[str] = None
    appointment_turn: int = Field(default=0)
    
    # Current agenda and goals
    current_goals: Set[str] = Field(default_factory=set)
    secret_agenda: Optional[str] = None
    
    def get_relationship(self, other_advisor_id: str) -> Relationship:
        """Get relationship with another advisor, creating if needed."""
        if other_advisor_id not in self.relationships:
            self.relationships[other_advisor_id] = Relationship(
                advisor_id=self.id,
                target_advisor_id=other_advisor_id
            )
        return self.relationships[other_advisor_id]
    
    def update_loyalty(self, leader_action_impact: float, event_context: str) -> None:
        """Update loyalty based on leader's actions."""
        # Personality affects how loyalty changes
        loyalty_change = leader_action_impact
        
        # Ambitious advisors are less loyal overall
        if self.personality.ambition > 0.7:
            loyalty_change *= 0.7
        
        # Pragmatic advisors adjust loyalty based on success
        if self.personality.pragmatism > 0.6:
            if "success" in event_context:
                loyalty_change *= 1.2
            elif "failure" in event_context:
                loyalty_change *= 0.8
        
        # Ideological advisors have stronger reactions
        if self.personality.pragmatism < 0.4:
            loyalty_change *= 1.5
        
        self.loyalty_to_leader = max(0.0, min(1.0, 
                                             self.loyalty_to_leader + loyalty_change))
    
    def calculate_coup_motivation(self) -> float:
        """Calculate how motivated this advisor is to participate in a coup."""
        base_motivation = 0.0
        
        # Low loyalty increases coup motivation
        if self.loyalty_to_leader < 0.3:
            base_motivation += (0.3 - self.loyalty_to_leader) * 2
        
        # High ambition increases motivation
        base_motivation += self.personality.ambition * 0.5
        
        # Paranoia can increase motivation if advisor feels threatened
        if self.personality.paranoia > 0.6:
            base_motivation += (self.personality.paranoia - 0.6) * 0.8
        
        # Low influence creates motivation for change
        if self.influence < 0.3:
            base_motivation += (0.3 - self.influence) * 0.7
        
        return min(1.0, base_motivation)
    
    def assess_conspiracy_potential(self, other_advisors: List['Advisor']) -> Dict[str, float]:
        """Assess potential for conspiracy with other advisors."""
        conspiracy_scores = {}
        
        for other in other_advisors:
            if other.id == self.id or other.status != AdvisorStatus.ACTIVE:
                continue
                
            relationship = self.get_relationship(other.id)
            other_motivation = other.calculate_coup_motivation()
            my_motivation = self.calculate_coup_motivation()
            
            # Base score from mutual motivation
            base_score = (my_motivation + other_motivation) / 2
            
            # Modify by relationship trust
            trust_factor = max(0.0, relationship.trust)
            base_score *= (0.3 + trust_factor * 0.7)  # Require some trust
            
            # Personality compatibility
            compatibility = self.personality.compatibility_score(other.personality)
            base_score *= compatibility
            
            # Existing conspiracy level
            base_score = max(base_score, relationship.conspiracy_level)
            
            conspiracy_scores[other.id] = min(1.0, base_score)
        
        return conspiracy_scores
    
    def make_decision(self, options: List[Dict], context: Dict) -> Dict:
        """Make a decision based on personality and context."""
        if not options:
            return {}
        
        # Score each option based on personality
        scored_options = []
        for option in options:
            score = self._score_option(option, context)
            scored_options.append((score, option))
        
        # Sort by score and add some randomness
        scored_options.sort(key=lambda x: x[0], reverse=True)
        
        # Pragmatic advisors choose the highest scoring option
        if self.personality.pragmatism > 0.7:
            return scored_options[0][1]
        
        # Less pragmatic advisors might choose based on ideology
        # This is a simplified version - would be expanded with specific logic
        return scored_options[0][1]
    
    def _score_option(self, option: Dict, context: Dict) -> float:
        """Score a decision option based on personality."""
        base_score = option.get('base_value', 0.5)
        
        # Modify based on personality traits
        if option.get('type') == 'aggressive' and self.personality.ambition > 0.6:
            base_score += 0.2
        
        if option.get('type') == 'cooperative' and self.personality.loyalty > 0.7:
            base_score += 0.3
        
        if option.get('risk_level', 0) > 0.5 and self.personality.paranoia > 0.6:
            base_score -= 0.3
        
        # Consider alignment with current goals
        if self.current_goals.intersection(set(option.get('tags', []))):
            base_score += 0.2
        
        return max(0.0, min(1.0, base_score))
    
    def advance_turn(self, current_turn: int) -> None:
        """Advance advisor state by one turn."""
        self.turns_in_office += 1
        
        # Decay relationships naturally
        for relationship in self.relationships.values():
            relationship.decay_relationship()
        
        # Slight influence change based on competence
        competence_factor = (self.personality.competence - 0.5) * 0.01
        self.influence = max(0.0, min(1.0, self.influence + competence_factor))
