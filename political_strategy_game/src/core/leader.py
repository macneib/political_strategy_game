"""
Leader class representing the head of a civilization with their own personality and agenda.
"""

from typing import Dict, List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field
import uuid

from .advisor import Advisor, AdvisorRole, PersonalityProfile


class LeadershipStyle(str, Enum):
    """Different leadership approaches that affect advisor interactions."""
    AUTHORITARIAN = "authoritarian"    # Makes decisions with minimal input
    COLLABORATIVE = "collaborative"    # Seeks consensus among advisors
    DELEGATIVE = "delegative"         # Gives advisors significant autonomy
    MICROMANAGING = "micromanaging"   # Closely controls all decisions
    CHARISMATIC = "charismatic"       # Relies on personal charm and vision
    PRAGMATIC = "pragmatic"           # Focuses on practical results


class Leader(BaseModel):
    """The head of state for a civilization with their own political dynamics."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    civilization_id: str
    personality: PersonalityProfile
    leadership_style: LeadershipStyle
    
    # Political metrics
    legitimacy: float = Field(default=0.7, ge=0.0, le=1.0,
                             description="How legitimate the population sees their rule")
    paranoia_level: float = Field(default=0.0, ge=0.0, le=1.0,
                                 description="Current level of paranoia about threats")
    popularity: float = Field(default=0.5, ge=0.0, le=1.0,
                             description="Public approval rating")
    
    # Relationships with advisors
    advisor_trust: Dict[str, float] = Field(default_factory=dict)
    advisor_influence_on_leader: Dict[str, float] = Field(default_factory=dict)
    
    # Historical tracking
    turns_in_power: int = Field(default=0)
    came_to_power_by: str = Field(default="inheritance",
                                 description="How they became leader")
    major_decisions: List[str] = Field(default_factory=list)
    
    # Information management
    information_filters: Dict[str, float] = Field(default_factory=dict,
                                                 description="How much info to share with each advisor")
    disinformation_campaigns: Set[str] = Field(default_factory=set,
                                              description="Active propaganda efforts")
    
    def get_advisor_trust(self, advisor_id: str) -> float:
        """Get trust level for a specific advisor."""
        return self.advisor_trust.get(advisor_id, 0.5)
    
    def update_advisor_trust(self, advisor_id: str, trust_change: float, 
                           reason: str) -> None:
        """Update trust in an advisor based on recent events."""
        current_trust = self.get_advisor_trust(advisor_id)
        
        # Paranoid leaders lose trust faster
        if self.personality.paranoia > 0.6 and trust_change < 0:
            trust_change *= 1.5
        
        # Loyal leaders regain trust slower
        if self.personality.loyalty > 0.7 and trust_change > 0:
            trust_change *= 0.8
        
        new_trust = max(0.0, min(1.0, current_trust + trust_change))
        self.advisor_trust[advisor_id] = new_trust
        
        # Record the decision that led to this change
        self.major_decisions.append(f"Trust change for advisor {advisor_id}: {reason}")
    
    def decide_advisor_appointment(self, candidates: List[Advisor], 
                                 role: AdvisorRole) -> Optional[str]:
        """Choose which advisor to appoint to a role."""
        if not candidates:
            return None
        
        best_candidate = None
        best_score = -1.0
        
        for candidate in candidates:
            score = self._score_advisor_candidate(candidate, role)
            if score > best_score:
                best_score = score
                best_candidate = candidate.id
        
        return best_candidate
    
    def _score_advisor_candidate(self, advisor: Advisor, role: AdvisorRole) -> float:
        """Score an advisor candidate for appointment."""
        base_score = advisor.personality.competence
        
        # Prefer advisors with complementary or similar personality
        personality_score = self._assess_personality_fit(advisor.personality)
        base_score += personality_score * 0.3
        
        # Trust factor
        trust_factor = self.get_advisor_trust(advisor.id)
        base_score += trust_factor * 0.4
        
        # Leadership style preferences
        if self.leadership_style == LeadershipStyle.AUTHORITARIAN:
            # Prefer loyal, less ambitious advisors
            base_score += advisor.personality.loyalty * 0.3
            base_score -= advisor.personality.ambition * 0.2
        elif self.leadership_style == LeadershipStyle.COLLABORATIVE:
            # Prefer charismatic, less corrupt advisors
            base_score += advisor.personality.charisma * 0.2
            base_score -= advisor.personality.corruption * 0.3
        elif self.leadership_style == LeadershipStyle.DELEGATIVE:
            # Prefer competent, ambitious advisors
            base_score += advisor.personality.competence * 0.3
            base_score += advisor.personality.ambition * 0.1
        
        return max(0.0, min(1.0, base_score))
    
    def _assess_personality_fit(self, advisor_personality: PersonalityProfile) -> float:
        """Assess how well an advisor's personality fits with the leader."""
        compatibility = self.personality.compatibility_score(advisor_personality)
        
        # Some leadership styles prefer different personality types
        if self.leadership_style == LeadershipStyle.CHARISMATIC:
            # Charismatic leaders like other charismatic people
            compatibility += advisor_personality.charisma * 0.2
        elif self.leadership_style == LeadershipStyle.AUTHORITARIAN:
            # Authoritarian leaders prefer less ambitious subordinates
            compatibility -= advisor_personality.ambition * 0.3
        
        return compatibility
    
    def process_advisor_recommendations(self, recommendations: List[Dict]) -> Dict:
        """Process recommendations from advisors and make a decision."""
        if not recommendations:
            return {"action": "maintain_status_quo", "confidence": 0.5}
        
        # Weight recommendations by advisor trust and influence
        weighted_recommendations = []
        
        for rec in recommendations:
            advisor_id = rec.get('advisor_id')
            trust = self.get_advisor_trust(advisor_id)
            influence = self.advisor_influence_on_leader.get(advisor_id, 0.5)
            
            weight = (trust * 0.6 + influence * 0.4)
            weighted_recommendations.append((weight, rec))
        
        # Sort by weight
        weighted_recommendations.sort(key=lambda x: x[0], reverse=True)
        
        # Leadership style affects decision making
        if self.leadership_style == LeadershipStyle.AUTHORITARIAN:
            # Make decision based on personal judgment, less advisor input
            return self._make_personal_decision(recommendations)
        elif self.leadership_style == LeadershipStyle.COLLABORATIVE:
            # Try to find consensus among trusted advisors
            return self._find_consensus_decision(weighted_recommendations)
        else:
            # Default to highest weighted recommendation
            if weighted_recommendations:
                return weighted_recommendations[0][1]
            return {"action": "maintain_status_quo", "confidence": 0.5}
    
    def _make_personal_decision(self, recommendations: List[Dict]) -> Dict:
        """Make decision based on leader's personality with minimal advisor input."""
        # Simplified decision making based on personality
        if self.personality.ambition > 0.7:
            # Ambitious leaders prefer aggressive options
            for rec in recommendations:
                if rec.get('type') == 'aggressive':
                    return rec
        
        if self.personality.pragmatism > 0.7:
            # Pragmatic leaders choose the most practical option
            for rec in recommendations:
                if rec.get('practicality', 0) > 0.6:
                    return rec
        
        # Default to first recommendation
        return recommendations[0] if recommendations else {"action": "maintain_status_quo"}
    
    def _find_consensus_decision(self, weighted_recommendations: List[tuple]) -> Dict:
        """Try to find a decision that most trusted advisors support."""
        if not weighted_recommendations:
            return {"action": "maintain_status_quo", "confidence": 0.5}
        
        # For now, return the highest weighted recommendation
        # In a more complex system, this would analyze overlapping recommendations
        return weighted_recommendations[0][1]
    
    def detect_threats(self, advisors: List[Advisor]) -> Dict[str, float]:
        """Assess threats from advisors based on their behavior and loyalty."""
        threats = {}
        
        for advisor in advisors:
            threat_level = 0.0
            
            # Low loyalty is a threat indicator
            advisor_loyalty = advisor.loyalty_to_leader
            if advisor_loyalty < 0.3:
                threat_level += (0.3 - advisor_loyalty) * 2
            
            # High ambition combined with low loyalty is dangerous
            if advisor.personality.ambition > 0.6 and advisor_loyalty < 0.5:
                threat_level += advisor.personality.ambition * 0.5
            
            # High influence without loyalty is concerning
            if advisor.influence > 0.6 and advisor_loyalty < 0.6:
                threat_level += advisor.influence * 0.4
            
            # Check for conspiracy indicators in relationships
            conspiracy_risk = 0.0
            for relationship in advisor.relationships.values():
                if relationship.conspiracy_level > 0.3:
                    conspiracy_risk += relationship.conspiracy_level * 0.3
            
            threat_level += min(0.4, conspiracy_risk)
            
            # Paranoid leaders see higher threats
            if self.personality.paranoia > 0.5:
                threat_level *= (1.0 + self.personality.paranoia * 0.5)
            
            threats[advisor.id] = min(1.0, threat_level)
        
        return threats
    
    def manage_information_sharing(self, advisor_id: str, information_sensitivity: float) -> bool:
        """Decide whether to share sensitive information with an advisor."""
        trust_level = self.get_advisor_trust(advisor_id)
        
        # Information filter affects how much is shared
        filter_level = self.information_filters.get(advisor_id, 0.0)
        effective_threshold = information_sensitivity + filter_level
        
        # Paranoid leaders share less
        if self.personality.paranoia > 0.5:
            effective_threshold *= (1.0 + self.personality.paranoia * 0.3)
        
        return trust_level > effective_threshold
    
    def advance_turn(self, current_turn: int) -> None:
        """Advance leader state by one turn."""
        self.turns_in_power += 1
        
        # Paranoia can increase over time if there are threats
        if self.personality.paranoia > 0.3:
            self.paranoia_level = min(1.0, self.paranoia_level + 0.01)
        
        # Popularity slowly decays without positive events
        self.popularity = max(0.0, self.popularity - 0.005)
