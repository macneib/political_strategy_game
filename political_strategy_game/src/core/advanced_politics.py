"""
Advanced political mechanics for sophisticated internal civilization politics.

This module implements enhanced conspiracy networks, political parties/factions,
succession mechanics, information warfare, and political reform systems.
"""

from typing import Dict, List, Optional, Set, Any, Tuple
from enum import Enum
from pydantic import BaseModel, Field
import uuid
import random
from datetime import datetime

from .advisor import AdvisorRole, AdvisorStatus
from .memory import Memory, MemoryType, MemoryManager


class ConspiracyType(str, Enum):
    """Types of political conspiracies."""
    COUP_ATTEMPT = "coup_attempt"
    ASSASSINATION_PLOT = "assassination_plot"
    POLICY_SABOTAGE = "policy_sabotage"
    INFORMATION_LEAK = "information_leak"
    ECONOMIC_MANIPULATION = "economic_manipulation"
    FOREIGN_COLLUSION = "foreign_collusion"
    SUCCESSION_PLOT = "succession_plot"
    REFORM_RESISTANCE = "reform_resistance"


class ConspiracyStatus(str, Enum):
    """Status of a conspiracy."""
    FORMING = "forming"
    ACTIVE = "active"
    EXPOSED = "exposed"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    DISBANDED = "disbanded"


class FactionType(str, Enum):
    """Types of political factions."""
    CONSERVATIVE = "conservative"
    PROGRESSIVE = "progressive"
    MILITARIST = "militarist"
    MERCHANT = "merchant"
    RELIGIOUS = "religious"
    POPULIST = "populist"
    TECHNOCRAT = "technocrat"
    NATIONALIST = "nationalist"


class PoliticalIdeology(str, Enum):
    """Political ideologies that drive faction behavior."""
    AUTHORITARIANISM = "authoritarianism"
    LIBERALISM = "liberalism"
    TRADITIONALISM = "traditionalism"
    MODERNIZATION = "modernization"
    MILITARISM = "militarism"
    PACIFISM = "pacifism"
    CAPITALISM = "capitalism"
    SOCIALISM = "socialism"


class PropagandaType(str, Enum):
    """Types of propaganda and information warfare."""
    CHARACTER_ASSASSINATION = "character_assassination"
    POLICY_PROMOTION = "policy_promotion"
    FACTION_RECRUITMENT = "faction_recruitment"
    CONSPIRACY_MISDIRECTION = "conspiracy_misdirection"
    FOREIGN_THREAT_EMPHASIS = "foreign_threat_emphasis"
    ECONOMIC_SUCCESS_CLAIMS = "economic_success_claims"
    HISTORICAL_REVISIONISM = "historical_revisionism"
    LOYALTY_CAMPAIGNS = "loyalty_campaigns"


class SuccessionCrisisType(str, Enum):
    """Types of succession crises."""
    UNCLEAR_HEIR = "unclear_heir"
    DISPUTED_LEGITIMACY = "disputed_legitimacy"
    MULTIPLE_CLAIMANTS = "multiple_claimants"
    FOREIGN_INTERFERENCE = "foreign_interference"
    ADVISOR_COUP = "advisor_coup"
    POPULAR_UPRISING = "popular_uprising"


class ConspiracyNetwork(BaseModel):
    """A network of conspirators working toward a common goal."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conspiracy_type: ConspiracyType
    status: ConspiracyStatus = ConspiracyStatus.FORMING
    
    # Conspiracy membership
    leader_id: str  # Primary conspirator
    members: Set[str] = Field(default_factory=set)  # advisor IDs
    potential_recruits: Set[str] = Field(default_factory=set)
    
    # Conspiracy details
    target: Optional[str] = None  # Target of the conspiracy (advisor ID, policy, etc.)
    objective: str  # What the conspiracy aims to achieve
    formation_turn: int
    activation_turn: Optional[int] = None
    
    # Conspiracy strength and secrecy
    network_strength: float = Field(default=0.3, ge=0.0, le=1.0)
    secrecy_level: float = Field(default=0.8, ge=0.0, le=1.0)
    discovery_risk: float = Field(default=0.1, ge=0.0, le=1.0)
    
    # Resources and capabilities
    financial_resources: float = Field(default=100.0, ge=0.0)
    information_assets: Set[str] = Field(default_factory=set)
    external_support: Dict[str, float] = Field(default_factory=dict)  # civ_id -> support_level
    
    def add_member(self, advisor_id: str) -> bool:
        """Add a member to the conspiracy."""
        if advisor_id not in self.members and advisor_id != self.leader_id:
            self.members.add(advisor_id)
            # Remove from potential recruits if present
            self.potential_recruits.discard(advisor_id)
            # Increase network strength
            self.network_strength = min(1.0, self.network_strength + 0.1)
            # Slightly increase discovery risk
            self.discovery_risk = min(1.0, self.discovery_risk + 0.05)
            return True
        return False
    
    def remove_member(self, advisor_id: str) -> bool:
        """Remove a member from the conspiracy."""
        if advisor_id in self.members:
            self.members.remove(advisor_id)
            # Decrease network strength
            self.network_strength = max(0.0, self.network_strength - 0.15)
            # Increase discovery risk due to potential betrayal
            self.discovery_risk = min(1.0, self.discovery_risk + 0.2)
            return True
        return False
    
    def calculate_success_probability(self) -> float:
        """Calculate the probability of conspiracy success."""
        # Base probability from network strength
        base_prob = self.network_strength
        
        # Modify based on member count
        member_bonus = min(0.3, len(self.members) * 0.05)
        
        # Secrecy bonus
        secrecy_bonus = self.secrecy_level * 0.2
        
        # Discovery penalty
        discovery_penalty = self.discovery_risk * 0.4
        
        # External support bonus
        external_bonus = min(0.2, sum(self.external_support.values()) * 0.1)
        
        total_prob = base_prob + member_bonus + secrecy_bonus + external_bonus - discovery_penalty
        return max(0.0, min(1.0, total_prob))


class PoliticalFaction(BaseModel):
    """A political faction within the civilization."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    faction_type: FactionType
    ideology: PoliticalIdeology
    
    # Faction membership
    leader_id: Optional[str] = None  # Faction leader (advisor ID)
    members: Set[str] = Field(default_factory=set)  # advisor IDs
    supporters: Set[str] = Field(default_factory=set)  # citizen/population groups
    
    # Faction characteristics
    influence: float = Field(default=0.3, ge=0.0, le=1.0)
    popularity: float = Field(default=0.4, ge=0.0, le=1.0)
    cohesion: float = Field(default=0.6, ge=0.0, le=1.0)
    militancy: float = Field(default=0.2, ge=0.0, le=1.0)
    
    # Political positions
    policy_priorities: List[str] = Field(default_factory=list)
    opposed_policies: List[str] = Field(default_factory=list)
    reform_agenda: List[str] = Field(default_factory=list)
    
    # Resources and capabilities
    treasury: float = Field(default=500.0, ge=0.0)
    propaganda_effectiveness: float = Field(default=0.4, ge=0.0, le=1.0)
    intelligence_network: float = Field(default=0.2, ge=0.0, le=1.0)
    
    # Relationships with other factions
    allied_factions: Set[str] = Field(default_factory=set)  # faction IDs
    rival_factions: Set[str] = Field(default_factory=set)  # faction IDs
    
    def calculate_political_power(self) -> float:
        """Calculate the faction's current political power."""
        # Base power from influence and popularity
        base_power = (self.influence * 0.6) + (self.popularity * 0.4)
        
        # Member count bonus
        member_bonus = min(0.3, len(self.members) * 0.05)
        
        # Cohesion modifier
        cohesion_modifier = (self.cohesion - 0.5) * 0.2
        
        # Resource modifier
        resource_modifier = min(0.2, self.treasury / 1000.0 * 0.1)
        
        total_power = base_power + member_bonus + cohesion_modifier + resource_modifier
        return max(0.0, min(1.0, total_power))


class SuccessionCandidate(BaseModel):
    """A potential successor to leadership."""
    
    advisor_id: str
    legitimacy_score: float = Field(default=0.5, ge=0.0, le=1.0)
    support_base: Set[str] = Field(default_factory=set)  # supporter advisor IDs
    faction_backing: Set[str] = Field(default_factory=set)  # backing faction IDs
    
    # Succession qualifications
    bloodline_claim: float = Field(default=0.0, ge=0.0, le=1.0)
    appointed_heir: bool = Field(default=False)
    merit_score: float = Field(default=0.5, ge=0.0, le=1.0)
    popular_support: float = Field(default=0.3, ge=0.0, le=1.0)
    
    # Campaign resources
    campaign_funds: float = Field(default=0.0, ge=0.0)
    promises_made: List[str] = Field(default_factory=list)
    
    def calculate_succession_strength(self) -> float:
        """Calculate this candidate's strength in a succession contest."""
        # Base strength from legitimacy
        base_strength = self.legitimacy_score
        
        # Bloodline bonus
        bloodline_bonus = self.bloodline_claim * 0.3
        
        # Appointed heir bonus
        heir_bonus = 0.4 if self.appointed_heir else 0.0
        
        # Support base bonus
        support_bonus = min(0.3, len(self.support_base) * 0.05)
        
        # Faction backing bonus
        faction_bonus = min(0.2, len(self.faction_backing) * 0.1)
        
        # Popular support bonus
        popular_bonus = self.popular_support * 0.2
        
        total_strength = base_strength + bloodline_bonus + heir_bonus + support_bonus + faction_bonus + popular_bonus
        return max(0.0, min(1.0, total_strength))


class PropagandaCampaign(BaseModel):
    """A propaganda or information warfare campaign."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_type: PropagandaType
    sponsor_id: str  # advisor or faction ID sponsoring the campaign
    
    # Campaign details
    target: Optional[str] = None  # Target of the campaign
    message: str  # Core propaganda message
    duration_turns: int = Field(default=3, ge=1)
    turns_remaining: int = Field(default=3, ge=0)
    
    # Campaign effectiveness
    effectiveness: float = Field(default=0.5, ge=0.0, le=1.0)
    reach: float = Field(default=0.4, ge=0.0, le=1.0)  # How widely the message spreads
    credibility: float = Field(default=0.6, ge=0.0, le=1.0)
    
    # Resources invested
    funding: float = Field(default=100.0, ge=0.0)
    media_control: float = Field(default=0.3, ge=0.0, le=1.0)
    
    # Campaign effects
    target_opinion_change: float = Field(default=0.0)  # Change in target's standing
    public_opinion_change: float = Field(default=0.0)  # Change in general public opinion
    counter_campaigns: Set[str] = Field(default_factory=set)  # opposing campaign IDs


class PoliticalReform(BaseModel):
    """A proposed or enacted political reform."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    proposer_id: str  # advisor ID who proposed the reform
    
    # Reform characteristics
    reform_scope: str  # "constitutional", "administrative", "economic", "military"
    implementation_difficulty: float = Field(default=0.5, ge=0.0, le=1.0)
    public_support: float = Field(default=0.4, ge=0.0, le=1.0)
    elite_support: float = Field(default=0.3, ge=0.0, le=1.0)
    
    # Implementation details
    required_votes: int = Field(default=3)  # advisor votes needed
    current_votes: int = Field(default=0)
    opposition_strength: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Reform effects (if implemented)
    stability_impact: float = Field(default=0.0)
    legitimacy_impact: float = Field(default=0.0)
    economic_impact: float = Field(default=0.0)
    military_impact: float = Field(default=0.0)
    
    # Supporting and opposing factions
    supporting_factions: Set[str] = Field(default_factory=set)
    opposing_factions: Set[str] = Field(default_factory=set)


class AdvancedPoliticalManager(BaseModel):
    """Manager for advanced political mechanics."""
    
    civilization_id: str
    current_turn: int = Field(default=1)
    
    # Conspiracy tracking
    active_conspiracies: List[ConspiracyNetwork] = Field(default_factory=list)
    conspiracy_history: List[ConspiracyNetwork] = Field(default_factory=list)
    
    # Faction system
    political_factions: List[PoliticalFaction] = Field(default_factory=list)
    faction_relationships: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    
    # Succession system
    succession_candidates: List[SuccessionCandidate] = Field(default_factory=list)
    succession_crisis_active: bool = Field(default=False)
    succession_crisis_type: Optional[SuccessionCrisisType] = None
    
    # Information warfare
    active_propaganda: List[PropagandaCampaign] = Field(default_factory=list)
    information_environment: Dict[str, float] = Field(default_factory=dict)  # topic -> public_opinion
    
    # Political reforms
    proposed_reforms: List[PoliticalReform] = Field(default_factory=list)
    enacted_reforms: List[PoliticalReform] = Field(default_factory=list)
    
    # System state
    political_temperature: float = Field(default=0.4, ge=0.0, le=1.0)  # Overall political tension
    information_reliability: float = Field(default=0.7, ge=0.0, le=1.0)  # General information trustworthiness
    
    def create_faction(self, name: str, faction_type: FactionType, 
                      ideology: PoliticalIdeology, leader_id: Optional[str] = None) -> str:
        """Create a new political faction."""
        faction = PoliticalFaction(
            name=name,
            faction_type=faction_type,
            ideology=ideology,
            leader_id=leader_id
        )
        
        if leader_id:
            faction.members.add(leader_id)
        
        self.political_factions.append(faction)
        
        # Initialize faction relationships
        if faction.id not in self.faction_relationships:
            self.faction_relationships[faction.id] = {}
        
        return faction.id
    
    def join_faction(self, advisor_id: str, faction_id: str) -> bool:
        """Have an advisor join a political faction."""
        faction = self._find_faction(faction_id)
        if faction:
            faction.members.add(advisor_id)
            return True
        return False
    
    def form_conspiracy(self, leader_id: str, conspiracy_type: ConspiracyType,
                       objective: str, target: Optional[str] = None) -> str:
        """Form a new conspiracy."""
        conspiracy = ConspiracyNetwork(
            conspiracy_type=conspiracy_type,
            leader_id=leader_id,
            objective=objective,
            target=target,
            formation_turn=self.current_turn
        )
        
        self.active_conspiracies.append(conspiracy)
        return conspiracy.id
    
    def recruit_to_conspiracy(self, conspiracy_id: str, recruiter_id: str, 
                             target_id: str, advisor_relationships: Dict[str, Any]) -> bool:
        """Attempt to recruit an advisor to a conspiracy."""
        conspiracy = self._find_conspiracy(conspiracy_id)
        if not conspiracy or recruiter_id not in conspiracy.members and recruiter_id != conspiracy.leader_id:
            return False
        
        # Check if recruiter has a relationship with target
        if recruiter_id in advisor_relationships and target_id in advisor_relationships[recruiter_id]:
            relationship = advisor_relationships[recruiter_id][target_id]
            
            # Calculate recruitment probability based on relationship
            trust_factor = relationship.get('trust', 0.5)
            conspiracy_factor = relationship.get('conspiracy_level', 0.0)
            
            recruitment_prob = (trust_factor * 0.4) + (conspiracy_factor * 0.6)
            
            if random.random() < recruitment_prob:  # nosec B311 - Using random for game mechanics, not security
                return conspiracy.add_member(target_id)
        
        return False
    
    def launch_propaganda_campaign(self, sponsor_id: str, campaign_type: PropagandaType,
                                  message: str, target: Optional[str] = None,
                                  funding: float = 100.0) -> str:
        """Launch a propaganda campaign."""
        campaign = PropagandaCampaign(
            campaign_type=campaign_type,
            sponsor_id=sponsor_id,
            message=message,
            target=target,
            funding=funding
        )
        
        # Calculate effectiveness based on funding and sponsor influence
        base_effectiveness = min(1.0, funding / 200.0)
        campaign.effectiveness = base_effectiveness
        
        self.active_propaganda.append(campaign)
        return campaign.id
    
    def propose_reform(self, proposer_id: str, name: str, description: str,
                      reform_scope: str, required_votes: int = 3) -> str:
        """Propose a political reform."""
        reform = PoliticalReform(
            name=name,
            description=description,
            proposer_id=proposer_id,
            reform_scope=reform_scope,
            required_votes=required_votes
        )
        
        self.proposed_reforms.append(reform)
        return reform.id
    
    def vote_on_reform(self, reform_id: str, voter_id: str, support: bool) -> bool:
        """Cast a vote on a proposed reform."""
        reform = self._find_reform(reform_id)
        if reform and support:
            reform.current_votes += 1
            return True
        return False
    
    def trigger_succession_crisis(self, crisis_type: SuccessionCrisisType) -> bool:
        """Trigger a succession crisis."""
        if not self.succession_crisis_active:
            self.succession_crisis_active = True
            self.succession_crisis_type = crisis_type
            self.political_temperature = min(1.0, self.political_temperature + 0.3)
            return True
        return False
    
    def process_turn(self) -> Dict[str, Any]:
        """Process one turn of advanced political mechanics."""
        self.current_turn += 1
        results = {
            "conspiracies_detected": [],
            "conspiracies_activated": [],
            "propaganda_effects": [],
            "reforms_passed": [],
            "faction_changes": [],
            "succession_events": []
        }
        
        # Process conspiracies
        for conspiracy in self.active_conspiracies[:]:  # Copy list to avoid modification issues
            # Update discovery risk
            if len(conspiracy.members) > 3:
                conspiracy.discovery_risk = min(1.0, conspiracy.discovery_risk + 0.05)
            
            # Check for conspiracy detection
            if random.random() < conspiracy.discovery_risk:  # nosec B311 - Using random for game mechanics, not security
                conspiracy.status = ConspiracyStatus.EXPOSED
                results["conspiracies_detected"].append({
                    "id": conspiracy.id,
                    "type": conspiracy.conspiracy_type,
                    "leader": conspiracy.leader_id,
                    "members": list(conspiracy.members)
                })
                self._move_conspiracy_to_history(conspiracy)
            
            # Check for conspiracy activation
            elif (conspiracy.status == ConspiracyStatus.FORMING and 
                  len(conspiracy.members) >= 2 and 
                  conspiracy.network_strength > 0.5):
                conspiracy.status = ConspiracyStatus.ACTIVE
                conspiracy.activation_turn = self.current_turn
                results["conspiracies_activated"].append({
                    "id": conspiracy.id,
                    "type": conspiracy.conspiracy_type,
                    "strength": conspiracy.network_strength
                })
        
        # Process propaganda campaigns
        for campaign in self.active_propaganda[:]:
            campaign.turns_remaining -= 1
            
            # Apply propaganda effects
            if campaign.target:
                opinion_change = campaign.effectiveness * 0.1
                if campaign.target in self.information_environment:
                    self.information_environment[campaign.target] += opinion_change
                else:
                    self.information_environment[campaign.target] = opinion_change
                
                results["propaganda_effects"].append({
                    "campaign_id": campaign.id,
                    "target": campaign.target,
                    "opinion_change": opinion_change
                })
            
            # Propaganda degrades information reliability
            if campaign.campaign_type in [PropagandaType.CHARACTER_ASSASSINATION, 
                                        PropagandaType.CONSPIRACY_MISDIRECTION,
                                        PropagandaType.HISTORICAL_REVISIONISM]:
                self.information_reliability = max(0.0, self.information_reliability - 0.05)
            
            # Remove completed campaigns
            if campaign.turns_remaining <= 0:
                self.active_propaganda.remove(campaign)
        
        # Process political reforms
        for reform in self.proposed_reforms[:]:
            if reform.current_votes >= reform.required_votes:
                # Reform passes
                self.enacted_reforms.append(reform)
                self.proposed_reforms.remove(reform)
                results["reforms_passed"].append({
                    "id": reform.id,
                    "name": reform.name,
                    "impact": {
                        "stability": reform.stability_impact,
                        "legitimacy": reform.legitimacy_impact
                    }
                })
        
        # Update political temperature
        self._update_political_temperature()
        
        return results
    
    def _find_faction(self, faction_id: str) -> Optional[PoliticalFaction]:
        """Find a faction by ID."""
        for faction in self.political_factions:
            if faction.id == faction_id:
                return faction
        return None
    
    def _find_conspiracy(self, conspiracy_id: str) -> Optional[ConspiracyNetwork]:
        """Find an active conspiracy by ID."""
        for conspiracy in self.active_conspiracies:
            if conspiracy.id == conspiracy_id:
                return conspiracy
        return None
    
    def _find_reform(self, reform_id: str) -> Optional[PoliticalReform]:
        """Find a proposed reform by ID."""
        for reform in self.proposed_reforms:
            if reform.id == reform_id:
                return reform
        return None
    
    def _move_conspiracy_to_history(self, conspiracy: ConspiracyNetwork) -> None:
        """Move a conspiracy to historical records."""
        if conspiracy in self.active_conspiracies:
            self.active_conspiracies.remove(conspiracy)
        self.conspiracy_history.append(conspiracy)
    
    def _update_political_temperature(self) -> None:
        """Update the overall political temperature based on current events."""
        # Base decay
        self.political_temperature = max(0.0, self.political_temperature - 0.02)
        
        # Increase based on active conspiracies
        active_conspiracy_count = len([c for c in self.active_conspiracies if c.status == ConspiracyStatus.ACTIVE])
        self.political_temperature = min(1.0, self.political_temperature + (active_conspiracy_count * 0.05))
        
        # Increase based on succession crisis
        if self.succession_crisis_active:
            self.political_temperature = min(1.0, self.political_temperature + 0.1)
        
        # Increase based on propaganda campaigns
        propaganda_count = len(self.active_propaganda)
        self.political_temperature = min(1.0, self.political_temperature + (propaganda_count * 0.02))
    
    def get_political_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the political situation."""
        return {
            "civilization_id": self.civilization_id,
            "turn": self.current_turn,
            "political_temperature": self.political_temperature,
            "information_reliability": self.information_reliability,
            "factions": {
                "count": len(self.political_factions),
                "most_powerful": self._get_most_powerful_faction(),
                "total_members": sum(len(f.members) for f in self.political_factions)
            },
            "conspiracies": {
                "active": len(self.active_conspiracies),
                "forming": len([c for c in self.active_conspiracies if c.status == ConspiracyStatus.FORMING]),
                "active_status": len([c for c in self.active_conspiracies if c.status == ConspiracyStatus.ACTIVE])
            },
            "propaganda": {
                "active_campaigns": len(self.active_propaganda),
                "information_environment": dict(self.information_environment)
            },
            "reforms": {
                "proposed": len(self.proposed_reforms),
                "enacted": len(self.enacted_reforms)
            },
            "succession": {
                "crisis_active": self.succession_crisis_active,
                "crisis_type": self.succession_crisis_type,
                "candidates": len(self.succession_candidates)
            }
        }
    
    def _get_most_powerful_faction(self) -> Optional[Dict[str, Any]]:
        """Get information about the most powerful faction."""
        if not self.political_factions:
            return None
        
        most_powerful = max(self.political_factions, key=lambda f: f.calculate_political_power())
        return {
            "id": most_powerful.id,
            "name": most_powerful.name,
            "type": most_powerful.faction_type,
            "power": most_powerful.calculate_political_power(),
            "members": len(most_powerful.members)
        }
