"""
AI-Driven Information Warfare System

This module implements sophisticated information warfare mechanics including
LLM-generated propaganda campaigns, misinformation detect        self.active_campaigns: Dict[str, PropagandaCampaign] = {}
        self.information_sources: Dict[str, InformationSourceProfile] = {}
        self.public_opinion: Dict[str, float] = defaultdict(float)  # Topic -> opinion score, and narrative
control systems for political manipulation and public opinion influence.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import json
import logging
import random
from collections import defaultdict

from .dialogue import MultiAdvisorDialogue, EmotionalState
from .faction_dynamics import FactionDynamicsManager, PoliticalFaction
from .advisors import AdvisorRole, AdvisorCouncil, AdvisorAI, AdvisorPersonality
from .llm_providers import LLMManager, LLMMessage, LLMResponse


class PropagandaType(Enum):
    """Types of propaganda campaigns."""
    LEGITIMACY_BUILDING = "legitimacy_building"
    OPPOSITION_UNDERMINING = "opposition_undermining"
    FEAR_MONGERING = "fear_mongering"
    UNITY_PROMOTION = "unity_promotion"
    SCAPEGOATING = "scapegoating"
    VICTORY_CLAIMS = "victory_claims"
    REFORM_ADVOCACY = "reform_advocacy"
    TRADITION_APPEAL = "tradition_appeal"


class PropagandaTarget(Enum):
    """Target audiences for propaganda."""
    GENERAL_POPULATION = "general_population"
    MILITARY = "military"
    NOBILITY = "nobility"
    MERCHANTS = "merchants"
    SCHOLARS = "scholars"
    FOREIGN_POWERS = "foreign_powers"
    SPECIFIC_FACTION = "specific_faction"
    RIVAL_ADVISORS = "rival_advisors"


class InformationSource(Enum):
    """Sources of information in the political system."""
    OFFICIAL_GOVERNMENT = "official_government"
    ADVISOR_COUNCIL = "advisor_council"
    FACTION_LEADERSHIP = "faction_leadership"
    INTELLIGENCE_NETWORKS = "intelligence_networks"
    FOREIGN_DIPLOMATS = "foreign_diplomats"
    POPULAR_RUMORS = "popular_rumors"
    MERCHANT_NETWORKS = "merchant_networks"
    ANONYMOUS = "anonymous"


class CredibilityLevel(Enum):
    """Credibility levels for information sources."""
    HIGHLY_CREDIBLE = "highly_credible"
    CREDIBLE = "credible"
    QUESTIONABLE = "questionable"
    UNRELIABLE = "unreliable"
    KNOWN_MISINFORMATION = "known_misinformation"


@dataclass
class PropagandaMessage:
    """Represents a propaganda message with content and targeting."""
    message_id: str
    content: str
    propaganda_type: PropagandaType
    target_audience: PropagandaTarget
    emotional_appeal: EmotionalState
    key_themes: List[str] = field(default_factory=list)
    factual_basis: float = 0.5  # 0.0-1.0, how much truth vs manipulation
    emotional_intensity: float = 0.5  # 0.0-1.0, emotional manipulation level
    sophistication_level: float = 0.5  # 0.0-1.0, complexity of arguments
    creation_date: datetime = field(default_factory=datetime.now)
    
    def calculate_effectiveness(self, target_state: Dict[str, Any]) -> float:
        """Calculate message effectiveness against target."""
        effectiveness = 0.5  # Base effectiveness
        
        # Emotional alignment bonus
        if self.emotional_appeal.value in str(target_state.get("current_mood", "")):
            effectiveness += 0.2
        
        # Factual basis affects long-term credibility
        effectiveness += (self.factual_basis - 0.5) * 0.3
        
        # Sophistication vs target education level
        target_sophistication = target_state.get("education_level", 0.5)
        sophistication_match = 1.0 - abs(self.sophistication_level - target_sophistication)
        effectiveness += sophistication_match * 0.2
        
        return max(0.0, min(1.0, effectiveness))


@dataclass
class PropagandaCampaign:
    """Represents a coordinated propaganda campaign."""
    campaign_id: str
    name: str
    orchestrator: str  # Advisor or faction running the campaign
    objective: str
    target_audience: PropagandaTarget
    messages: List[PropagandaMessage] = field(default_factory=list)
    start_date: datetime = field(default_factory=datetime.now)
    duration_turns: int = 5
    resource_investment: Dict[str, float] = field(default_factory=lambda: {"influence": 0.0, "gold": 0.0})
    success_metrics: Dict[str, float] = field(default_factory=dict)
    current_effectiveness: float = 0.0
    detected_by: List[str] = field(default_factory=list)  # Who has detected this campaign
    
    def add_message(self, message: PropagandaMessage):
        """Add a message to the campaign."""
        self.messages.append(message)
        
        # Update campaign effectiveness
        if self.messages:
            self.current_effectiveness = sum(
                msg.calculate_effectiveness({"current_mood": "neutral", "education_level": 0.5})
                for msg in self.messages
            ) / len(self.messages)
    
    def is_active(self) -> bool:
        """Check if campaign is still active."""
        elapsed = datetime.now() - self.start_date
        return elapsed.days < self.duration_turns


@dataclass
class InformationSourceProfile:
    """Represents a source of information with credibility tracking."""
    source_id: str
    name: str
    source_type: InformationSource
    credibility: CredibilityLevel
    bias_indicators: List[str] = field(default_factory=list)
    verification_history: List[Tuple[str, bool]] = field(default_factory=list)  # (claim, verified)
    influence_network: List[str] = field(default_factory=list)
    recent_claims: List[str] = field(default_factory=list)
    
    def update_credibility(self, claim: str, verified: bool):
        """Update source credibility based on verification."""
        self.verification_history.append((claim, verified))
        
        # Calculate new credibility based on recent accuracy
        recent_verifications = self.verification_history[-10:]  # Last 10 claims
        if recent_verifications:
            accuracy_rate = sum(verified for _, verified in recent_verifications) / len(recent_verifications)
            
            if accuracy_rate > 0.8:
                self.credibility = CredibilityLevel.HIGHLY_CREDIBLE
            elif accuracy_rate > 0.6:
                self.credibility = CredibilityLevel.CREDIBLE
            elif accuracy_rate > 0.4:
                self.credibility = CredibilityLevel.QUESTIONABLE
            elif accuracy_rate > 0.2:
                self.credibility = CredibilityLevel.UNRELIABLE
            else:
                self.credibility = CredibilityLevel.KNOWN_MISINFORMATION


class InformationWarfareManager:
    """Manages AI-driven information warfare, propaganda, and narrative control."""
    
    def __init__(self, llm_manager: LLMManager, dialogue_system: MultiAdvisorDialogue, 
                 faction_manager: Optional[FactionDynamicsManager] = None):
        self.llm_manager = llm_manager
        self.dialogue_system = dialogue_system
        self.faction_manager = faction_manager
        self.active_campaigns: Dict[str, PropagandaCampaign] = {}
        self.information_sources: Dict[str, InformationSource] = {}
        self.public_opinion: Dict[str, float] = defaultdict(float)  # Topic -> opinion score
        self.narrative_themes: Dict[str, float] = defaultdict(float)  # Active narrative themes
        self.counter_intelligence: Dict[str, List[str]] = defaultdict(list)  # Detected campaigns per advisor
        self.logger = logging.getLogger(__name__)
        
        # Initialize default information sources
        self._initialize_information_sources()
    
    def _initialize_information_sources(self):
        """Initialize default information sources in the political system."""
        default_sources = [
            InformationSourceProfile(
                source_id="official_proclamations",
                name="Official Government Proclamations",
                source_type=InformationSource.OFFICIAL_GOVERNMENT,
                credibility=CredibilityLevel.CREDIBLE
            ),
            InformationSourceProfile(
                source_id="council_announcements",
                name="Advisor Council Announcements",
                source_type=InformationSource.ADVISOR_COUNCIL,
                credibility=CredibilityLevel.CREDIBLE
            ),
            InformationSourceProfile(
                source_id="merchant_gossip",
                name="Merchant Network Gossip",
                source_type=InformationSource.MERCHANT_NETWORKS,
                credibility=CredibilityLevel.QUESTIONABLE,
                bias_indicators=["Economic interests", "Trade concerns"]
            ),
            InformationSourceProfile(
                source_id="street_rumors",
                name="Popular Street Rumors",
                source_type=InformationSource.POPULAR_RUMORS,
                credibility=CredibilityLevel.UNRELIABLE,
                bias_indicators=["Emotional", "Unverified", "Sensationalized"]
            )
        ]
        
        for source in default_sources:
            self.information_sources[source.source_id] = source
    
    async def analyze_propaganda_opportunities(self, game_state: Any, orchestrator: str) -> Dict[str, float]:
        """Analyze current opportunities for propaganda campaigns."""
        opportunities = {
            "political_instability": (100 - game_state.stability) / 100,
            "legitimacy_crisis": (100 - game_state.legitimacy) / 100,
            "external_threats": 0.0,
            "economic_concerns": 0.0,
            "social_unrest": 0.0,
            "factional_conflicts": 0.0
        }
        
        # Analyze advisor emotional states for social tension
        emotional_tension = 0.0
        for name in self.dialogue_system.advisor_council.advisors.keys():
            emotional_state = self.dialogue_system.get_advisor_emotional_state(name)
            intensity = emotional_state.get("intensity", 0.5)
            emotion = emotional_state.get("emotion", "calm")
            
            if emotion in ["angry", "worried", "suspicious"] and intensity > 0.6:
                emotional_tension += 0.1
        
        opportunities["social_unrest"] = min(1.0, emotional_tension)
        
        # Analyze factional conflicts if faction manager available
        if self.faction_manager:
            faction_summary = self.faction_manager.get_all_factions_summary()
            opportunities["factional_conflicts"] = faction_summary.get("political_fragmentation", 0.0)
        
        # Use LLM to analyze additional propaganda opportunities
        additional_opportunities = await self._llm_analyze_propaganda_opportunities(game_state, orchestrator, opportunities)
        opportunities.update(additional_opportunities)
        
        return opportunities
    
    async def _llm_analyze_propaganda_opportunities(self, game_state: Any, orchestrator: str, 
                                                   base_opportunities: Dict[str, float]) -> Dict[str, float]:
        """Use LLM to analyze propaganda opportunities."""
        advisor = self.dialogue_system.advisor_council.advisors.get(orchestrator)
        
        prompt = f"""Analyze propaganda opportunities for {orchestrator}:

ADVISOR PROFILE:
- Name: {advisor.personality.name if advisor else orchestrator}
- Role: {advisor.role.value.title() if advisor else 'Unknown'} Advisor
- Background: {advisor.personality.background if advisor else 'Unknown'}

CURRENT POLITICAL STATE:
- Political Power: {getattr(game_state, 'political_power', 100)}
- Stability: {getattr(game_state, 'stability', 75)}
- Legitimacy: {getattr(game_state, 'legitimacy', 70)}

BASIC OPPORTUNITIES DETECTED:
{json.dumps(base_opportunities, indent=2)}

Analyze additional propaganda opportunities from this advisor's perspective.

Return JSON with values 0.0-1.0:
{{
    "external_threats": 0.0,
    "economic_concerns": 0.0,
    "succession_uncertainty": 0.0,
    "reform_resistance": 0.0,
    "foreign_influence": 0.0
}}"""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a propaganda analysis specialist."),
                LLMMessage(role="user", content=prompt)
            ])
            
            opportunities_data = json.loads(response.content)
            
            # Validate and clamp values
            additional_opportunities = {}
            for key, value in opportunities_data.items():
                if isinstance(value, (int, float)):
                    additional_opportunities[key] = max(0.0, min(1.0, float(value)))
            
            return additional_opportunities
            
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Failed to parse LLM propaganda analysis: {e}")
            return {
                "external_threats": random.uniform(0.1, 0.4),
                "economic_concerns": random.uniform(0.2, 0.6),
                "succession_uncertainty": random.uniform(0.0, 0.3),
                "reform_resistance": random.uniform(0.1, 0.5),
                "foreign_influence": random.uniform(0.0, 0.3)
            }
    
    async def generate_propaganda_message(self, campaign_objective: str, target_audience: PropagandaTarget,
                                        orchestrator: str, current_context: Dict[str, Any]) -> PropagandaMessage:
        """Generate a propaganda message using LLM."""
        advisor = self.dialogue_system.advisor_council.advisors.get(orchestrator)
        
        prompt = f"""Generate a propaganda message for a political campaign:

ORCHESTRATOR: {orchestrator}
ADVISOR PROFILE: {advisor.personality.name if advisor else 'Unknown'} - {advisor.role.value if advisor else 'Unknown'} Advisor
CAMPAIGN OBJECTIVE: {campaign_objective}
TARGET AUDIENCE: {target_audience.value}

CURRENT POLITICAL CONTEXT:
{json.dumps(current_context, indent=2)}

PROPAGANDA TYPES TO CHOOSE FROM:
- legitimacy_building: Build support for current leadership
- opposition_undermining: Discredit political opponents
- fear_mongering: Create fear of external/internal threats
- unity_promotion: Encourage national/factional unity
- scapegoating: Blame problems on specific groups
- victory_claims: Celebrate achievements and successes
- reform_advocacy: Promote specific policy changes
- tradition_appeal: Appeal to traditional values

Generate a propaganda message that is:
1. Appropriate for the target audience
2. Advances the campaign objective
3. Reflects the orchestrator's perspective and expertise
4. Uses psychological persuasion techniques

Return JSON format:
{{
    "content": "The actual propaganda message text",
    "propaganda_type": "one of the types above",
    "emotional_appeal": "angry|worried|confident|excited|determined|calm",
    "key_themes": ["theme1", "theme2", "theme3"],
    "factual_basis": 0.0-1.0,
    "emotional_intensity": 0.0-1.0,
    "sophistication_level": 0.0-1.0
}}"""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a political messaging and propaganda specialist."),
                LLMMessage(role="user", content=prompt)
            ])
            
            message_data = json.loads(response.content)
            
            # Create propaganda message
            message = PropagandaMessage(
                message_id=f"msg_{len(self.active_campaigns) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                content=message_data.get("content", "Default message"),
                propaganda_type=PropagandaType(message_data.get("propaganda_type", "legitimacy_building")),
                target_audience=target_audience,
                emotional_appeal=EmotionalState(message_data.get("emotional_appeal", "calm")),
                key_themes=message_data.get("key_themes", []),
                factual_basis=max(0.0, min(1.0, message_data.get("factual_basis", 0.5))),
                emotional_intensity=max(0.0, min(1.0, message_data.get("emotional_intensity", 0.5))),
                sophistication_level=max(0.0, min(1.0, message_data.get("sophistication_level", 0.5)))
            )
            
            return message
            
        except (json.JSONDecodeError, ValueError, Exception) as e:
            self.logger.warning(f"Failed to generate propaganda message: {e}")
            
            # Fallback message generation
            return PropagandaMessage(
                message_id=f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                content=f"Citizens, {orchestrator} speaks to the {target_audience.value.replace('_', ' ')} about {campaign_objective}.",
                propaganda_type=PropagandaType.LEGITIMACY_BUILDING,
                target_audience=target_audience,
                emotional_appeal=EmotionalState.CONFIDENT,
                key_themes=["Leadership", "Stability", "Progress"],
                factual_basis=0.6,
                emotional_intensity=0.4,
                sophistication_level=0.5
            )
    
    async def launch_propaganda_campaign(self, orchestrator: str, objective: str, 
                                       target_audience: PropagandaTarget, 
                                       resource_investment: Dict[str, float],
                                       duration_turns: int = 5) -> PropagandaCampaign:
        """Launch a new propaganda campaign."""
        # Analyze current context (mock game state for now)
        # game_state would be passed from the actual game system
        class MockGameState:
            def __init__(self):
                self.political_power = 100
                self.stability = 75  
                self.legitimacy = 70
        
        game_state = MockGameState()
        opportunities = await self.analyze_propaganda_opportunities(game_state, orchestrator)
        
        # Generate campaign name
        campaign_name = await self._generate_campaign_name(objective, target_audience, orchestrator)
        
        # Create campaign
        campaign = PropagandaCampaign(
            campaign_id=f"campaign_{len(self.active_campaigns) + 1}_{orchestrator.lower().replace(' ', '_')}",
            name=campaign_name,
            orchestrator=orchestrator,
            objective=objective,
            target_audience=target_audience,
            duration_turns=duration_turns,
            resource_investment=resource_investment
        )
        
        # Generate initial propaganda messages
        current_context = {
            "opportunities": opportunities,
            "public_opinion": dict(self.public_opinion),
            "active_themes": dict(self.narrative_themes)
        }
        
        # Generate 2-3 initial messages
        for i in range(random.randint(2, 3)):
            message = await self.generate_propaganda_message(
                objective, target_audience, orchestrator, current_context
            )
            campaign.add_message(message)
        
        self.active_campaigns[campaign.campaign_id] = campaign
        self.logger.info(f"Launched propaganda campaign '{campaign_name}' by {orchestrator}")
        
        return campaign
    
    async def _generate_campaign_name(self, objective: str, target_audience: PropagandaTarget, orchestrator: str) -> str:
        """Generate a campaign name using LLM."""
        prompt = f"""Generate a name for a propaganda campaign:

OBJECTIVE: {objective}
TARGET AUDIENCE: {target_audience.value}
ORCHESTRATOR: {orchestrator}

Generate a realistic campaign name that sounds like a political or public relations initiative.
Examples: "National Unity Initiative", "Stability and Progress Campaign", "Truth and Transparency Project"

Return only the campaign name, no explanation."""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a political campaign naming specialist."),
                LLMMessage(role="user", content=prompt)
            ])
            
            name = response.content.strip().strip('"').strip("'")
            return name if len(name) < 60 else f"{objective} Campaign"
            
        except Exception as e:
            self.logger.warning(f"Failed to generate campaign name: {e}")
            return f"{objective} Initiative"
    
    def detect_propaganda_campaign(self, detector: str, campaign: PropagandaCampaign) -> bool:
        """Attempt to detect a propaganda campaign."""
        detection_chance = 0.3  # Base detection chance
        
        # Intelligence advisors are better at detection
        detector_advisor = self.dialogue_system.advisor_council.advisors.get(detector)
        if detector_advisor and detector_advisor.role == AdvisorRole.INTELLIGENCE:
            detection_chance += 0.3
        
        # Emotional state affects detection ability
        emotional_state = self.dialogue_system.get_advisor_emotional_state(detector)
        if emotional_state.get("emotion") == "suspicious":
            detection_chance += emotional_state.get("intensity", 0.5) * 0.2
        
        # Campaign sophistication affects detection difficulty
        avg_sophistication = sum(msg.sophistication_level for msg in campaign.messages) / max(1, len(campaign.messages))
        detection_chance -= avg_sophistication * 0.2
        
        # Resource investment affects visibility
        total_investment = sum(campaign.resource_investment.values())
        if total_investment > 100:  # High-resource campaigns are more visible
            detection_chance += 0.2
        
        detected = random.random() < detection_chance
        
        if detected and detector not in campaign.detected_by:
            campaign.detected_by.append(detector)
            self.counter_intelligence[detector].append(campaign.campaign_id)
            self.logger.info(f"{detector} detected propaganda campaign '{campaign.name}'")
        
        return detected
    
    async def generate_counter_propaganda(self, original_campaign: PropagandaCampaign, 
                                        counter_orchestrator: str) -> PropagandaMessage:
        """Generate counter-propaganda to oppose an existing campaign."""
        prompt = f"""Generate counter-propaganda to oppose an existing campaign:

ORIGINAL CAMPAIGN: {original_campaign.name}
ORIGINAL OBJECTIVE: {original_campaign.objective}
ORIGINAL MESSAGES: {[msg.content for msg in original_campaign.messages[:2]]}

COUNTER-ORCHESTRATOR: {counter_orchestrator}

Generate a counter-propaganda message that:
1. Undermines the original campaign's credibility
2. Presents alternative narrative or facts
3. Appeals to same target audience with opposing message
4. Uses appropriate tone for the counter-orchestrator

Return JSON format similar to propaganda message generation."""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a counter-propaganda specialist."),
                LLMMessage(role="user", content=prompt)
            ])
            
            message_data = json.loads(response.content)
            
            return PropagandaMessage(
                message_id=f"counter_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                content=message_data.get("content", f"Counter-message by {counter_orchestrator}"),
                propaganda_type=PropagandaType.OPPOSITION_UNDERMINING,
                target_audience=original_campaign.target_audience,
                emotional_appeal=EmotionalState(message_data.get("emotional_appeal", "confident")),
                key_themes=message_data.get("key_themes", ["Truth", "Transparency"]),
                factual_basis=max(0.0, min(1.0, message_data.get("factual_basis", 0.7))),
                emotional_intensity=max(0.0, min(1.0, message_data.get("emotional_intensity", 0.6))),
                sophistication_level=max(0.0, min(1.0, message_data.get("sophistication_level", 0.6)))
            )
            
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Failed to generate counter-propaganda: {e}")
            
            return PropagandaMessage(
                message_id=f"counter_fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                content=f"{counter_orchestrator} challenges the claims made in recent campaigns.",
                propaganda_type=PropagandaType.OPPOSITION_UNDERMINING,
                target_audience=original_campaign.target_audience,
                emotional_appeal=EmotionalState.CONFIDENT,
                key_themes=["Truth", "Alternative perspective"],
                factual_basis=0.7,
                emotional_intensity=0.5,
                sophistication_level=0.6
            )
    
    def calculate_campaign_effectiveness(self, campaign: PropagandaCampaign, current_turn: int) -> float:
        """Calculate the current effectiveness of a propaganda campaign."""
        if not campaign.is_active():
            return 0.0
        
        base_effectiveness = campaign.current_effectiveness
        
        # Resource investment multiplier
        total_investment = sum(campaign.resource_investment.values())
        resource_multiplier = min(2.0, 1.0 + total_investment / 100)
        
        # Detection penalty
        detection_penalty = len(campaign.detected_by) * 0.2
        
        # Time decay (campaigns lose effectiveness over time)
        turns_active = (datetime.now() - campaign.start_date).days
        time_decay = max(0.1, 1.0 - (turns_active * 0.1))
        
        # Competing campaigns reduce effectiveness
        competing_campaigns = [
            c for c in self.active_campaigns.values()
            if c.target_audience == campaign.target_audience and c.campaign_id != campaign.campaign_id and c.is_active()
        ]
        competition_penalty = len(competing_campaigns) * 0.15
        
        final_effectiveness = base_effectiveness * resource_multiplier * time_decay
        final_effectiveness -= detection_penalty + competition_penalty
        
        return max(0.0, min(1.0, final_effectiveness))
    
    def process_information_warfare_turn(self, game_state: Any) -> Dict[str, Any]:
        """Process information warfare dynamics for one turn."""
        results = {
            "campaign_effects": [],
            "new_detections": [],
            "public_opinion_changes": {},
            "narrative_shifts": {}
        }
        
        # Process active campaigns
        for campaign in list(self.active_campaigns.values()):
            if campaign.is_active():
                # Calculate effectiveness
                effectiveness = self.calculate_campaign_effectiveness(campaign, 1)
                
                # Apply public opinion effects
                opinion_change = effectiveness * 0.1  # Max 10% opinion change per turn
                target_topic = campaign.objective
                
                # Determine campaign type from messages
                if campaign.messages:
                    campaign_propaganda_type = campaign.messages[0].propaganda_type  # Use first message's type
                    
                    if campaign_propaganda_type in [PropagandaType.LEGITIMACY_BUILDING, PropagandaType.UNITY_PROMOTION]:
                        self.public_opinion[target_topic] += opinion_change
                    elif campaign_propaganda_type in [PropagandaType.OPPOSITION_UNDERMINING, PropagandaType.SCAPEGOATING]:
                        self.public_opinion[target_topic] -= opinion_change
                
                results["campaign_effects"].append({
                    "campaign": campaign.name,
                    "effectiveness": effectiveness,
                    "opinion_change": opinion_change,
                    "target": target_topic
                })
                
                # Update narrative themes
                if campaign.messages:
                    for theme in campaign.messages[0].key_themes:
                        self.narrative_themes[theme] += effectiveness * 0.05
                
                # Detection attempts by other advisors
                for advisor_name in self.dialogue_system.advisor_council.advisors.keys():
                    if advisor_name != campaign.orchestrator:
                        if self.detect_propaganda_campaign(advisor_name, campaign):
                            results["new_detections"].append({
                                "detector": advisor_name,
                                "campaign": campaign.name
                            })
            else:
                # Remove inactive campaigns
                if campaign.campaign_id in self.active_campaigns:
                    del self.active_campaigns[campaign.campaign_id]
        
        # Normalize public opinion values
        for topic in self.public_opinion:
            self.public_opinion[topic] = max(-1.0, min(1.0, self.public_opinion[topic]))
        
        # Decay narrative themes over time
        for theme in self.narrative_themes:
            self.narrative_themes[theme] *= 0.95  # 5% decay per turn
        
        results["public_opinion_changes"] = dict(self.public_opinion)
        results["narrative_shifts"] = dict(self.narrative_themes)
        
        return results
    
    def get_campaign_summary(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a specific propaganda campaign."""
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign:
            return None
        
        return {
            "campaign_id": campaign.campaign_id,
            "name": campaign.name,
            "orchestrator": campaign.orchestrator,
            "objective": campaign.objective,
            "target_audience": campaign.target_audience.value,
            "start_date": campaign.start_date.isoformat(),
            "duration_turns": campaign.duration_turns,
            "is_active": campaign.is_active(),
            "messages": [
                {
                    "content": msg.content,
                    "type": msg.propaganda_type.value,
                    "emotional_appeal": msg.emotional_appeal.value,
                    "themes": msg.key_themes,
                    "factual_basis": msg.factual_basis
                }
                for msg in campaign.messages
            ],
            "effectiveness": self.calculate_campaign_effectiveness(campaign, 1),
            "detected_by": campaign.detected_by,
            "resource_investment": campaign.resource_investment
        }
    
    def get_information_warfare_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of information warfare state."""
        active_campaigns_summary = {}
        for campaign_id in self.active_campaigns:
            summary = self.get_campaign_summary(campaign_id)
            if summary and summary["is_active"]:
                active_campaigns_summary[campaign_id] = summary
        
        return {
            "active_campaigns": len(active_campaigns_summary),
            "campaigns": active_campaigns_summary,
            "public_opinion": dict(self.public_opinion),
            "dominant_narratives": sorted(
                self.narrative_themes.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5],
            "information_sources": {
                source_id: {
                    "name": source.name,
                    "type": source.source_type.value,
                    "credibility": source.credibility.value,
                    "bias_indicators": source.bias_indicators
                }
                for source_id, source in self.information_sources.items()
            },
            "counter_intelligence": {
                advisor: campaigns for advisor, campaigns in self.counter_intelligence.items() if campaigns
            }
        }
