"""
AI-Driven Faction Dynamics System

This module implements sophisticated faction formation, alliance dynamics, and
AI-driven political group behavior that emerges from advisor interactions and
shared ideologies.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
from datetime import datetime
import asyncio
import json
import logging
import random
from collections import defaultdict

from .dialogue import MultiAdvisorDialogue, EmotionalState
from .conspiracy import ConspiracyGenerator, ConspiracyType
from .advisors import AdvisorRole, AdvisorCouncil, AdvisorAI, AdvisorPersonality
from .llm_providers import LLMManager, LLMMessage, LLMResponse


class IdeologyType(Enum):
    """Different political ideologies that can drive faction formation."""
    MILITARIST = "militarist"
    ECONOMIC_CONSERVATIVE = "economic_conservative"
    DIPLOMATIC_PROGRESSIVE = "diplomatic_progressive"
    POPULIST = "populist"
    TRADITIONALIST = "traditionalist"
    REFORMIST = "reformist"
    NATIONALIST = "nationalist"
    INTERNATIONALIST = "internationalist"


class FactionStatus(Enum):
    """Current status of political factions."""
    FORMING = "forming"
    ACTIVE = "active"
    DOMINANT = "dominant"
    DECLINING = "declining"
    DISSOLVED = "dissolved"
    UNDERGROUND = "underground"


class AllianceType(Enum):
    """Types of alliances between factions."""
    FORMAL_ALLIANCE = "formal_alliance"
    TEMPORARY_COOPERATION = "temporary_cooperation"
    NON_AGGRESSION = "non_aggression"
    RIVALRY = "rivalry"
    OPPOSITION = "opposition"
    HOSTILITY = "hostility"


@dataclass
class FactionIdeology:
    """Represents the ideological foundation of a political faction."""
    primary_ideology: IdeologyType
    secondary_ideologies: List[IdeologyType] = field(default_factory=list)
    core_beliefs: List[str] = field(default_factory=list)
    policy_priorities: List[str] = field(default_factory=list)
    opposed_ideologies: List[IdeologyType] = field(default_factory=list)
    flexibility_score: float = 0.5  # How willing to compromise (0.0-1.0)
    radicalism_level: float = 0.3   # How extreme the ideology (0.0-1.0)
    
    def calculate_ideological_distance(self, other: 'FactionIdeology') -> float:
        """Calculate ideological distance between two faction ideologies."""
        distance = 0.0
        
        # Primary ideology compatibility
        if self.primary_ideology == other.primary_ideology:
            distance -= 0.3
        elif other.primary_ideology in self.opposed_ideologies:
            distance += 0.5
        
        # Secondary ideology overlap
        overlap = len(set(self.secondary_ideologies) & set(other.secondary_ideologies))
        distance -= overlap * 0.1
        
        # Opposition check
        opposition = len(set(self.secondary_ideologies) & set(other.opposed_ideologies))
        distance += opposition * 0.2
        
        # Flexibility vs radicalism
        avg_flexibility = (self.flexibility_score + other.flexibility_score) / 2
        avg_radicalism = (self.radicalism_level + other.radicalism_level) / 2
        distance += avg_radicalism * 0.2 - avg_flexibility * 0.1
        
        return max(0.0, min(1.0, distance))


@dataclass
class FactionMember:
    """Represents a faction member with their role and commitment."""
    advisor_name: str
    role_in_faction: str
    commitment_level: float  # 0.0-1.0
    influence_level: float   # 0.0-1.0
    join_date: datetime = field(default_factory=datetime.now)
    recruitment_method: str = "unknown"
    contributions: List[str] = field(default_factory=list)
    
    def update_commitment(self, change: float, reason: str):
        """Update member commitment level."""
        old_commitment = self.commitment_level
        self.commitment_level = max(0.0, min(1.0, self.commitment_level + change))
        
        if abs(change) > 0.1:
            self.contributions.append(f"Commitment {'+' if change > 0 else ''}{change:.2f}: {reason}")


@dataclass
class FactionAlliance:
    """Represents an alliance or relationship between factions."""
    faction_a: str
    faction_b: str
    alliance_type: AllianceType
    strength: float  # 0.0-1.0
    formation_date: datetime = field(default_factory=datetime.now)
    terms: List[str] = field(default_factory=list)
    recent_interactions: List[str] = field(default_factory=list)
    
    def update_strength(self, change: float, reason: str):
        """Update alliance strength."""
        old_strength = self.strength
        self.strength = max(0.0, min(1.0, self.strength + change))
        self.recent_interactions.append(f"Strength {'+' if change > 0 else ''}{change:.2f}: {reason}")
        
        # Update alliance type based on new strength
        if self.strength > 0.8:
            self.alliance_type = AllianceType.FORMAL_ALLIANCE
        elif self.strength > 0.6:
            self.alliance_type = AllianceType.TEMPORARY_COOPERATION
        elif self.strength > 0.4:
            self.alliance_type = AllianceType.NON_AGGRESSION
        elif self.strength > 0.2:
            self.alliance_type = AllianceType.RIVALRY
        else:
            self.alliance_type = AllianceType.HOSTILITY


@dataclass
class PoliticalFaction:
    """Represents a political faction with members, ideology, and dynamics."""
    faction_id: str
    name: str
    ideology: FactionIdeology
    members: List[FactionMember] = field(default_factory=list)
    leader: Optional[str] = None
    status: FactionStatus = FactionStatus.FORMING
    formation_date: datetime = field(default_factory=datetime.now)
    manifesto: str = ""
    recent_actions: List[str] = field(default_factory=list)
    resources: Dict[str, float] = field(default_factory=lambda: {"influence": 0.0, "support": 0.0})
    
    def get_total_influence(self) -> float:
        """Calculate total faction influence from all members."""
        return sum(member.influence_level * member.commitment_level for member in self.members)
    
    def get_average_commitment(self) -> float:
        """Calculate average member commitment level."""
        if not self.members:
            return 0.0
        return sum(member.commitment_level for member in self.members) / len(self.members)
    
    def add_member(self, member: FactionMember):
        """Add a new member to the faction."""
        self.members.append(member)
        self.recent_actions.append(f"Recruited {member.advisor_name} as {member.role_in_faction}")
        
        # Update faction status based on membership
        if len(self.members) >= 3 and self.status == FactionStatus.FORMING:
            self.status = FactionStatus.ACTIVE
    
    def remove_member(self, advisor_name: str, reason: str = "Unknown"):
        """Remove a member from the faction."""
        self.members = [m for m in self.members if m.advisor_name != advisor_name]
        self.recent_actions.append(f"Lost member {advisor_name}: {reason}")
        
        # Update status if too few members
        if len(self.members) < 2 and self.status == FactionStatus.ACTIVE:
            self.status = FactionStatus.DECLINING


class FactionDynamicsManager:
    """Manages AI-driven faction formation, evolution, and alliance dynamics."""
    
    def __init__(self, llm_manager: LLMManager, dialogue_system: MultiAdvisorDialogue):
        self.llm_manager = llm_manager
        self.dialogue_system = dialogue_system
        self.active_factions: Dict[str, PoliticalFaction] = {}
        self.faction_alliances: Dict[Tuple[str, str], FactionAlliance] = {}
        self.ideology_trends: Dict[IdeologyType, float] = defaultdict(float)
        self.logger = logging.getLogger(__name__)
    
    async def analyze_faction_formation_conditions(self, game_state: Any) -> Dict[str, float]:
        """Analyze current conditions for faction formation."""
        conditions = {
            "political_instability": (100 - game_state.stability) / 100,
            "ideological_polarization": 0.0,
            "leadership_crisis": 0.0,
            "resource_competition": 0.0,
            "external_pressure": 0.0
        }
        
        # Analyze advisor emotional states for polarization
        polarization = 0.0
        leadership_crisis = 0.0
        
        for name in self.dialogue_system.advisor_council.advisors.keys():
            emotional_state = self.dialogue_system.get_advisor_emotional_state(name)
            intensity = emotional_state.get("intensity", 0.5)
            emotion = emotional_state.get("emotion", "calm")
            
            # High emotional intensity indicates polarization
            if intensity > 0.7:
                polarization += 0.1
            
            # Certain emotions indicate leadership crisis
            if emotion in ["angry", "disappointed", "suspicious"]:
                leadership_crisis += 0.1
        
        conditions["ideological_polarization"] = min(1.0, polarization)
        conditions["leadership_crisis"] = min(1.0, leadership_crisis)
        
        # Use LLM to analyze broader political conditions
        additional_conditions = await self._llm_analyze_faction_conditions(game_state, conditions)
        conditions.update(additional_conditions)
        
        return conditions
    
    async def _llm_analyze_faction_conditions(self, game_state: Any, base_conditions: Dict[str, float]) -> Dict[str, float]:
        """Use LLM to analyze faction formation conditions."""
        prompt = f"""Analyze the political conditions for faction formation:

CURRENT POLITICAL STATE:
- Political Power: {getattr(game_state, 'political_power', 100)}
- Stability: {getattr(game_state, 'stability', 75)}
- Legitimacy: {getattr(game_state, 'legitimacy', 70)}

BASIC CONDITIONS DETECTED:
{json.dumps(base_conditions, indent=2)}

Please analyze additional faction formation factors and return a JSON object with values 0.0-1.0:
{{
    "resource_competition": 0.0,
    "external_pressure": 0.0,
    "succession_uncertainty": 0.0,
    "policy_disagreements": 0.0
}}

Consider economic pressures, diplomatic tensions, military threats, and policy conflicts."""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a political analyst specializing in faction dynamics."),
                LLMMessage(role="user", content=prompt)
            ])
            
            # Parse LLM response
            conditions_data = json.loads(response.content)
            
            # Validate and clamp values
            additional_conditions = {}
            for key, value in conditions_data.items():
                if isinstance(value, (int, float)):
                    additional_conditions[key] = max(0.0, min(1.0, float(value)))
            
            return additional_conditions
            
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Failed to parse LLM faction analysis: {e}")
            return {
                "resource_competition": random.uniform(0.2, 0.6),  # nosec B311 - Using random for game mechanics, not security
                "external_pressure": random.uniform(0.1, 0.4),  # nosec B311 - Using random for game mechanics, not security
                "succession_uncertainty": random.uniform(0.0, 0.5),  # nosec B311 - Using random for game mechanics, not security
                "policy_disagreements": random.uniform(0.3, 0.7)  # nosec B311 - Using random for game mechanics, not security
            }
    
    async def generate_faction_ideology(self, founding_advisor: str, conditions: Dict[str, float]) -> FactionIdeology:
        """Generate a faction ideology based on founding advisor and conditions."""
        advisor = self.dialogue_system.advisor_council.advisors[founding_advisor]
        emotional_state = self.dialogue_system.get_advisor_emotional_state(founding_advisor)
        
        # Build context for LLM
        prompt = f"""Generate a political faction ideology for a faction founded by {advisor.personality.name}:

FOUNDING ADVISOR PROFILE:
- Name: {advisor.personality.name}
- Role: {advisor.role.value.title()} Advisor
- Background: {advisor.personality.background}
- Personality Traits: {', '.join(advisor.personality.personality_traits)}
- Communication Style: {advisor.personality.communication_style}
- Expertise: {', '.join(advisor.personality.expertise_areas)}

CURRENT EMOTIONAL STATE:
- Emotion: {emotional_state.get('emotion', 'calm')}
- Intensity: {emotional_state.get('intensity', 0.5):.1f}

POLITICAL CONDITIONS:
{json.dumps(conditions, indent=2)}

Generate a faction ideology that reflects the founder's personality and current political conditions.

Return JSON format:
{{
    "primary_ideology": "militarist|economic_conservative|diplomatic_progressive|populist|traditionalist|reformist|nationalist|internationalist",
    "secondary_ideologies": ["ideology1", "ideology2"],
    "core_beliefs": ["belief1", "belief2", "belief3"],
    "policy_priorities": ["priority1", "priority2", "priority3"],
    "opposed_ideologies": ["opposing_ideology1", "opposing_ideology2"],
    "flexibility_score": 0.0-1.0,
    "radicalism_level": 0.0-1.0
}}"""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a political scientist specializing in ideological analysis."),
                LLMMessage(role="user", content=prompt)
            ])
            
            ideology_data = json.loads(response.content)
            
            # Parse and validate ideology
            primary = IdeologyType(ideology_data.get("primary_ideology", "traditionalist"))
            secondary = [IdeologyType(i) for i in ideology_data.get("secondary_ideologies", []) 
                        if i in [e.value for e in IdeologyType]]
            opposed = [IdeologyType(i) for i in ideology_data.get("opposed_ideologies", [])
                      if i in [e.value for e in IdeologyType]]
            
            return FactionIdeology(
                primary_ideology=primary,
                secondary_ideologies=secondary,
                core_beliefs=ideology_data.get("core_beliefs", []),
                policy_priorities=ideology_data.get("policy_priorities", []),
                opposed_ideologies=opposed,
                flexibility_score=max(0.0, min(1.0, ideology_data.get("flexibility_score", 0.5))),
                radicalism_level=max(0.0, min(1.0, ideology_data.get("radicalism_level", 0.3)))
            )
            
        except (json.JSONDecodeError, ValueError, Exception) as e:
            self.logger.warning(f"Failed to parse LLM ideology generation: {e}")
            
            # Fallback ideology based on advisor role
            role_ideologies = {
                AdvisorRole.MILITARY: IdeologyType.MILITARIST,
                AdvisorRole.ECONOMIC: IdeologyType.ECONOMIC_CONSERVATIVE,
                AdvisorRole.DIPLOMATIC: IdeologyType.DIPLOMATIC_PROGRESSIVE,
                AdvisorRole.DOMESTIC: IdeologyType.POPULIST,
                AdvisorRole.INTELLIGENCE: IdeologyType.NATIONALIST
            }
            
            primary = role_ideologies.get(advisor.role, IdeologyType.TRADITIONALIST)
            
            return FactionIdeology(
                primary_ideology=primary,
                core_beliefs=["Strong leadership", "National interests", "Effective governance"],
                policy_priorities=["Stability", "Security", "Prosperity"],
                flexibility_score=0.5,
                radicalism_level=0.3
            )
    
    async def create_political_faction(self, founding_advisor: str, conditions: Dict[str, float]) -> PoliticalFaction:
        """Create a new political faction with AI-generated characteristics."""
        ideology = await self.generate_faction_ideology(founding_advisor, conditions)
        
        # Generate faction name and manifesto
        faction_name = await self._generate_faction_name(founding_advisor, ideology)
        manifesto = await self._generate_faction_manifesto(faction_name, ideology, conditions)
        
        # Create founding member
        founding_member = FactionMember(
            advisor_name=founding_advisor,
            role_in_faction="Founding Leader",
            commitment_level=0.9,
            influence_level=0.8,
            recruitment_method="Self-initiated"
        )
        
        faction = PoliticalFaction(
            faction_id=f"faction_{len(self.active_factions) + 1}_{founding_advisor.lower().replace(' ', '_')}",
            name=faction_name,
            ideology=ideology,
            members=[founding_member],
            leader=founding_advisor,
            manifesto=manifesto,
            status=FactionStatus.FORMING
        )
        
        self.active_factions[faction.faction_id] = faction
        self.logger.info(f"Created faction '{faction_name}' founded by {founding_advisor}")
        
        return faction
    
    async def _generate_faction_name(self, founder: str, ideology: FactionIdeology) -> str:
        """Generate a faction name using LLM."""
        prompt = f"""Generate a political faction name based on:

FOUNDER: {founder}
PRIMARY IDEOLOGY: {ideology.primary_ideology.value}
CORE BELIEFS: {', '.join(ideology.core_beliefs[:3])}

Generate a realistic faction name that sounds like a political movement or party.
Examples: "Progressive Unity Coalition", "National Security Alliance", "Economic Reform Movement"

Return only the faction name, no explanation."""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a political naming specialist."),
                LLMMessage(role="user", content=prompt)
            ])
            
            name = response.content.strip().strip('"').strip("'")
            return name if len(name) < 50 else f"{ideology.primary_ideology.value.title()} Coalition"
            
        except Exception as e:
            self.logger.warning(f"Failed to generate faction name: {e}")
            return f"{ideology.primary_ideology.value.title()} Alliance"
    
    async def _generate_faction_manifesto(self, faction_name: str, ideology: FactionIdeology, conditions: Dict[str, float]) -> str:
        """Generate a faction manifesto using LLM."""
        prompt = f"""Write a political faction manifesto for "{faction_name}":

FACTION IDEOLOGY:
- Primary: {ideology.primary_ideology.value}
- Core Beliefs: {', '.join(ideology.core_beliefs)}
- Policy Priorities: {', '.join(ideology.policy_priorities)}

CURRENT POLITICAL CONDITIONS:
{json.dumps(conditions, indent=2)}

Write a compelling 2-3 paragraph manifesto that addresses current conditions and outlines the faction's vision.
Style: Political, inspiring, addressing key concerns of the time."""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a political speechwriter and manifesto author."),
                LLMMessage(role="user", content=prompt)
            ])
            
            return response.content.strip()
            
        except Exception as e:
            self.logger.warning(f"Failed to generate manifesto: {e}")
            return f"The {faction_name} stands for {ideology.primary_ideology.value} principles and effective governance."
    
    async def evaluate_alliance_opportunities(self, faction: PoliticalFaction) -> List[Tuple[str, float]]:
        """Evaluate potential alliance opportunities for a faction."""
        opportunities = []
        
        for other_faction_id, other_faction in self.active_factions.items():
            if other_faction_id == faction.faction_id:
                continue
            
            # Calculate ideological compatibility
            ideological_distance = faction.ideology.calculate_ideological_distance(other_faction.ideology)
            compatibility = 1.0 - ideological_distance
            
            # Factor in current alliance status
            alliance_key = (min(faction.faction_id, other_faction_id), max(faction.faction_id, other_faction_id))
            existing_alliance = self.faction_alliances.get(alliance_key)
            
            if existing_alliance:
                # Already have relationship - consider strengthening
                if existing_alliance.alliance_type in [AllianceType.FORMAL_ALLIANCE, AllianceType.TEMPORARY_COOPERATION]:
                    compatibility *= 0.5  # Lower priority for existing allies
                elif existing_alliance.alliance_type in [AllianceType.RIVALRY, AllianceType.HOSTILITY]:
                    compatibility *= 0.1  # Very low chance to ally with enemies
            
            # Factor in relative power and influence
            power_balance = min(faction.get_total_influence(), other_faction.get_total_influence()) / max(
                faction.get_total_influence(), other_faction.get_total_influence(), 0.1
            )
            compatibility *= (0.5 + power_balance * 0.5)  # Prefer more balanced alliances
            
            if compatibility > 0.3:  # Minimum threshold for consideration
                opportunities.append((other_faction_id, compatibility))
        
        # Sort by compatibility score
        opportunities.sort(key=lambda x: x[1], reverse=True)
        return opportunities[:3]  # Return top 3 opportunities
    
    async def attempt_faction_alliance(self, faction_a_id: str, faction_b_id: str) -> Optional[FactionAlliance]:
        """Attempt to form an alliance between two factions."""
        faction_a = self.active_factions[faction_a_id]
        faction_b = self.active_factions[faction_b_id]
        
        # Use LLM to determine alliance terms and likelihood
        alliance_terms = await self._negotiate_alliance_terms(faction_a, faction_b)
        
        if alliance_terms.get("success", False):
            alliance_key = (min(faction_a_id, faction_b_id), max(faction_a_id, faction_b_id))
            
            alliance = FactionAlliance(
                faction_a=faction_a_id,
                faction_b=faction_b_id,
                alliance_type=AllianceType.TEMPORARY_COOPERATION,
                strength=alliance_terms.get("strength", 0.6),
                terms=alliance_terms.get("terms", [])
            )
            
            self.faction_alliances[alliance_key] = alliance
            
            # Update faction records
            faction_a.recent_actions.append(f"Formed alliance with {faction_b.name}")
            faction_b.recent_actions.append(f"Formed alliance with {faction_a.name}")
            
            self.logger.info(f"Alliance formed between {faction_a.name} and {faction_b.name}")
            return alliance
        
        return None
    
    async def _negotiate_alliance_terms(self, faction_a: PoliticalFaction, faction_b: PoliticalFaction) -> Dict[str, Any]:
        """Use LLM to negotiate alliance terms between factions."""
        prompt = f"""Negotiate alliance terms between two political factions:

FACTION A: {faction_a.name}
- Ideology: {faction_a.ideology.primary_ideology.value}
- Core Beliefs: {', '.join(faction_a.ideology.core_beliefs[:3])}
- Members: {len(faction_a.members)}
- Total Influence: {faction_a.get_total_influence():.2f}

FACTION B: {faction_b.name}
- Ideology: {faction_b.ideology.primary_ideology.value}
- Core Beliefs: {', '.join(faction_b.ideology.core_beliefs[:3])}
- Members: {len(faction_b.members)}
- Total Influence: {faction_b.get_total_influence():.2f}

Determine if these factions would form an alliance and what terms they would agree to.

Return JSON format:
{{
    "success": true/false,
    "strength": 0.0-1.0,
    "alliance_type": "temporary_cooperation|formal_alliance|non_aggression",
    "terms": ["term1", "term2", "term3"],
    "reasoning": "Brief explanation of outcome"
}}"""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a political negotiation specialist."),
                LLMMessage(role="user", content=prompt)
            ])
            
            return json.loads(response.content)
            
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Failed to negotiate alliance terms: {e}")
            
            # Simple fallback based on ideological compatibility
            ideological_distance = faction_a.ideology.calculate_ideological_distance(faction_b.ideology)
            success = ideological_distance < 0.6
            
            return {
                "success": success,
                "strength": 0.7 if success else 0.2,
                "alliance_type": "temporary_cooperation" if success else "rivalry",
                "terms": ["Mutual support", "Shared resources"] if success else [],
                "reasoning": "Ideological compatibility analysis"
            }
    
    async def process_faction_dynamics_turn(self, game_state: Any) -> Dict[str, Any]:
        """Process faction dynamics for one game turn."""
        results = {
            "new_factions": [],
            "new_alliances": [],
            "faction_changes": [],
            "dissolved_factions": []
        }
        
        # Analyze conditions for new faction formation
        conditions = await self.analyze_faction_formation_conditions(game_state)
        
        # Consider new faction formation
        formation_threshold = 0.6
        total_instability = sum(conditions.values()) / len(conditions)
        
        if total_instability > formation_threshold and len(self.active_factions) < 5:
            # Find advisors not in factions who might form new ones
            unaffiliated_advisors = []
            faction_members = set()
            for faction in self.active_factions.values():
                faction_members.update(member.advisor_name for member in faction.members)
            
            for advisor_name in self.dialogue_system.advisor_council.advisors.keys():
                if advisor_name not in faction_members:
                    emotional_state = self.dialogue_system.get_advisor_emotional_state(advisor_name)
                    if emotional_state.get("intensity", 0.5) > 0.7:  # High emotional intensity
                        unaffiliated_advisors.append(advisor_name)
            
            # Try to create new faction
            if unaffiliated_advisors and random.random() < 0.4:  # nosec B311 - Using random for game mechanics, not security
                founder = random.choice(unaffiliated_advisors)  # nosec B311 - Using random for game mechanics, not security
                new_faction = await self.create_political_faction(founder, conditions)
                results["new_factions"].append(new_faction.faction_id)
        
        # Process existing factions
        for faction in list(self.active_factions.values()):
            # Evaluate alliance opportunities
            if faction.status == FactionStatus.ACTIVE and random.random() < 0.3:  # nosec B311 - Using random for game mechanics, not security
                opportunities = await self.evaluate_alliance_opportunities(faction)
                
                if opportunities:
                    target_faction_id, compatibility = opportunities[0]
                    if compatibility > 0.6:  # High compatibility threshold
                        alliance = await self.attempt_faction_alliance(faction.faction_id, target_faction_id)
                        if alliance:
                            results["new_alliances"].append({
                                "factions": [faction.faction_id, target_faction_id],
                                "type": alliance.alliance_type.value,
                                "strength": alliance.strength
                            })
        
        return results
    
    def get_faction_summary(self, faction_id: str) -> Optional[Dict[str, Any]]:
        """Get a comprehensive summary of a faction."""
        faction = self.active_factions.get(faction_id)
        if not faction:
            return None
        
        # Get alliance information
        alliances = []
        for alliance_key, alliance in self.faction_alliances.items():
            if faction_id in alliance_key:
                other_faction_id = alliance.faction_b if alliance.faction_a == faction_id else alliance.faction_a
                other_faction = self.active_factions.get(other_faction_id)
                
                alliances.append({
                    "with": other_faction.name if other_faction else "Unknown",
                    "type": alliance.alliance_type.value,
                    "strength": alliance.strength
                })
        
        return {
            "faction_id": faction.faction_id,
            "name": faction.name,
            "ideology": faction.ideology.primary_ideology.value,
            "status": faction.status.value,
            "leader": faction.leader,
            "members": [
                {
                    "name": member.advisor_name,
                    "role": member.role_in_faction,
                    "commitment": member.commitment_level,
                    "influence": member.influence_level
                }
                for member in faction.members
            ],
            "total_influence": faction.get_total_influence(),
            "average_commitment": faction.get_average_commitment(),
            "alliances": alliances,
            "recent_actions": faction.recent_actions[-5:],  # Last 5 actions
            "manifesto": faction.manifesto
        }
    
    def get_all_factions_summary(self) -> Dict[str, Any]:
        """Get a summary of all active factions and their dynamics."""
        faction_summaries = {}
        for faction_id in self.active_factions:
            faction_summaries[faction_id] = self.get_faction_summary(faction_id)
        
        # Calculate overall political landscape
        total_factions = len(self.active_factions)
        active_alliances = len(self.faction_alliances)
        
        # Determine dominant ideology
        ideology_counts = defaultdict(int)
        for faction in self.active_factions.values():
            ideology_counts[faction.ideology.primary_ideology] += len(faction.members)
        
        dominant_ideology = max(ideology_counts.items(), key=lambda x: x[1]) if ideology_counts else None
        
        return {
            "total_factions": total_factions,
            "active_alliances": active_alliances,
            "dominant_ideology": dominant_ideology[0].value if dominant_ideology else None,
            "factions": faction_summaries,
            "political_fragmentation": min(1.0, total_factions / 5.0),  # 0.0-1.0 scale
            "alliance_density": active_alliances / max(1, total_factions * (total_factions - 1) // 2)
        }
