"""
AI-Driven Conspiracy Generation System

This module implements sophisticated conspiracy plot generation using LLMs,
building on the existing conspiracy mechanics to create dynamic, realistic
political intrigue driven by advisor relationships and motivations.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple
from enum import Enum
import asyncio
import logging
import random
import json
from datetime import datetime

from .llm_providers import LLMManager, LLMMessage, LLMResponse, LLMProvider
from .advisors import AdvisorRole, AdvisorPersonality, AdvisorAI
from .dialogue import MultiAdvisorDialogue, EmotionalState, DialogueType


class ConspiracyType(Enum):
    """Types of conspiracies that can be generated."""
    COUP = "coup"
    ASSASSINATION = "assassination"
    CORRUPTION = "corruption"
    INFORMATION_LEAK = "information_leak"
    FOREIGN_INFILTRATION = "foreign_infiltration"
    ECONOMIC_MANIPULATION = "economic_manipulation"
    RELIGIOUS_UPRISING = "religious_uprising"
    MILITARY_DEFECTION = "military_defection"


class ConspiracyStatus(Enum):
    """Status of a conspiracy."""
    PLANNING = "planning"
    RECRUITING = "recruiting"
    PREPARATION = "preparation"
    EXECUTION = "execution"
    DISCOVERED = "discovered"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    DORMANT = "dormant"


@dataclass
class ConspiracyMotive:
    """Represents a conspiracy motive with emotional and rational components."""
    primary_driver: str
    emotional_trigger: EmotionalState
    rational_justification: str
    personal_stakes: float  # 0.0 to 1.0
    ideological_alignment: float  # -1.0 to 1.0 (opposition to support)
    urgency_level: float  # 0.0 to 1.0


@dataclass
class ConspiracyParticipant:
    """Represents a participant in a conspiracy."""
    advisor_name: str
    role_in_conspiracy: str
    commitment_level: float  # 0.0 to 1.0
    discovery_risk: float  # 0.0 to 1.0
    potential_rewards: List[str]
    potential_costs: List[str]
    recruitment_method: str
    recruitment_date: datetime = field(default_factory=datetime.now)


@dataclass
class ConspiracyPlot:
    """Represents a generated conspiracy plot."""
    plot_id: str
    conspiracy_type: ConspiracyType
    title: str
    description: str
    primary_motive: ConspiracyMotive
    target: Optional[str]  # Who or what is the target
    participants: List[ConspiracyParticipant]
    timeline: Dict[str, str]  # Phase -> Description
    required_resources: Dict[str, int]
    success_conditions: List[str]
    failure_conditions: List[str]
    potential_consequences: Dict[str, List[str]]  # Success/Failure -> consequences
    discovery_indicators: List[str]
    status: ConspiracyStatus
    creation_date: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)
    secrecy_level: float = 0.8  # 0.0 (public) to 1.0 (highly secret)
    

class ConspiracyGenerator:
    """
    AI-powered conspiracy generation system.
    
    Uses LLM capabilities to create realistic, context-aware conspiracies
    based on current political tensions, advisor relationships, and game state.
    """
    
    def __init__(self, llm_manager: LLMManager, dialogue_system: MultiAdvisorDialogue):
        self.llm_manager = llm_manager
        self.dialogue_system = dialogue_system
        self.active_conspiracies: Dict[str, ConspiracyPlot] = {}
        self.conspiracy_history: List[ConspiracyPlot] = []
        self.relationship_tensions: Dict[Tuple[str, str], float] = {}
        
        # Conspiracy generation parameters
        self.base_conspiracy_chance = 0.15  # 15% chance per turn
        self.emotional_trigger_threshold = 0.7  # Emotional intensity threshold
        self.political_instability_multiplier = 2.0  # Multiplier for unstable times
        
        self.logger = logging.getLogger(__name__)
    
    async def analyze_conspiracy_conditions(self, game_state: Any, 
                                           advisor_council: Any) -> Dict[str, float]:
        """
        Analyze current conditions for conspiracy formation.
        
        Returns a dictionary of conspiracy triggers and their strength.
        """
        conditions = {
            "political_instability": 0.0,
            "economic_crisis": 0.0,
            "advisor_tensions": 0.0,
            "external_pressure": 0.0,
            "succession_uncertainty": 0.0,
            "corruption_exposure": 0.0,
            "military_dissatisfaction": 0.0,
            "ideological_conflicts": 0.0
        }
        
        # Analyze political instability
        if hasattr(game_state, 'stability'):
            conditions["political_instability"] = max(0, (100 - game_state.stability) / 100)
        
        if hasattr(game_state, 'legitimacy'):
            conditions["succession_uncertainty"] = max(0, (100 - game_state.legitimacy) / 100)
        
        # Analyze advisor emotional states and relationships
        total_tension = 0.0
        tension_count = 0
        
        for advisor_name, emotional_model in self.dialogue_system.emotional_models.items():
            # High intensity negative emotions increase conspiracy likelihood
            if emotional_model.current_emotion in [EmotionalState.ANGRY, EmotionalState.SUSPICIOUS, 
                                                  EmotionalState.WORRIED]:
                total_tension += emotional_model.emotion_intensity
                tension_count += 1
        
        if tension_count > 0:
            conditions["advisor_tensions"] = total_tension / tension_count
        
        # Check for ideological conflicts through recent dialogue
        conditions["ideological_conflicts"] = await self._analyze_ideological_tensions()
        
        # Use LLM to analyze additional conspiracy triggers
        llm_analysis = await self._llm_analyze_conspiracy_conditions(game_state, conditions)
        conditions.update(llm_analysis)
        
        return conditions
    
    async def _analyze_ideological_tensions(self) -> float:
        """Analyze ideological tensions from recent advisor dialogues."""
        if not self.dialogue_system.active_dialogues:
            return 0.0
        
        tension_indicators = [
            "disagree", "oppose", "wrong", "misguided", "dangerous",
            "unacceptable", "cannot support", "strongly object"
        ]
        
        total_tension = 0.0
        dialogue_count = 0
        
        for dialogue in self.dialogue_system.active_dialogues.values():
            if dialogue.completed:
                conversation = dialogue.get_conversation_history().lower()
                tension_score = sum(1 for indicator in tension_indicators 
                                  if indicator in conversation)
                total_tension += min(tension_score / 10, 1.0)  # Normalize
                dialogue_count += 1
        
        return total_tension / max(dialogue_count, 1)
    
    async def _llm_analyze_conspiracy_conditions(self, game_state: Any, 
                                                base_conditions: Dict[str, float]) -> Dict[str, float]:
        """Use LLM to analyze additional conspiracy triggers."""
        try:
            prompt = f"""Analyze the current political situation for conspiracy formation potential.

CURRENT CONDITIONS:
- Political Stability: {getattr(game_state, 'stability', 'Unknown')}
- Legitimacy: {getattr(game_state, 'legitimacy', 'Unknown')}
- Political Power: {getattr(game_state, 'political_power', 'Unknown')}

EXISTING ANALYSIS:
{json.dumps(base_conditions, indent=2)}

ADDITIONAL FACTORS TO ANALYZE:
1. Economic crisis potential (resource shortages, trade disruption)
2. External pressure (foreign threats, diplomatic isolation)
3. Corruption exposure risk (scandals, investigations)
4. Military dissatisfaction (budget cuts, defeated campaigns)

Provide additional conspiracy trigger scores (0.0 to 1.0) for these factors.
Respond in JSON format:
{{
    "economic_crisis": 0.0-1.0,
    "external_pressure": 0.0-1.0,
    "corruption_exposure": 0.0-1.0,
    "military_dissatisfaction": 0.0-1.0
}}"""

            response = await self.llm_manager.generate([LLMMessage("user", prompt)])
            
            # Parse JSON response
            try:
                additional_conditions = json.loads(response.content)
                return {k: min(max(float(v), 0.0), 1.0) for k, v in additional_conditions.items()}
            except (json.JSONDecodeError, ValueError):
                self.logger.warning("Failed to parse LLM conspiracy analysis response")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error in LLM conspiracy analysis: {e}")
            return {}
    
    async def generate_conspiracy_motive(self, advisor_name: str, 
                                       conditions: Dict[str, float]) -> Optional[ConspiracyMotive]:
        """Generate a conspiracy motive for a specific advisor."""
        advisor_emotional = self.dialogue_system.get_advisor_emotional_state(advisor_name)
        
        # Skip if advisor is not emotionally triggered
        if advisor_emotional["intensity"] < self.emotional_trigger_threshold:
            return None
        
        # Use LLM to generate realistic motive based on advisor personality and conditions
        advisor = self.dialogue_system.advisor_council.advisors[advisor_name]
        personality = advisor.personality
        
        prompt = f"""Generate a conspiracy motive for {advisor_name}, {advisor.role.value.title()} Advisor.

ADVISOR PROFILE:
- Name: {personality.name}
- Role: {advisor.role.value}
- Personality: {', '.join(personality.personality_traits)}
- Background: {personality.background}
- Current Emotion: {advisor_emotional['emotion']} (intensity: {advisor_emotional['intensity']:.1f})

CURRENT POLITICAL CONDITIONS:
{json.dumps(conditions, indent=2)}

Generate a conspiracy motive that includes:
1. Primary emotional trigger
2. Rational justification
3. Personal stakes (0.0-1.0)
4. Ideological alignment with current regime (-1.0 to 1.0)
5. Urgency level (0.0-1.0)

The motive should be realistic and match the advisor's personality and expertise.
Respond in JSON format:
{{
    "primary_driver": "Brief description of what drives this conspiracy",
    "emotional_trigger": "{advisor_emotional['emotion']}",
    "rational_justification": "Logical reasoning the advisor would use",
    "personal_stakes": 0.0-1.0,
    "ideological_alignment": -1.0-1.0,
    "urgency_level": 0.0-1.0
}}"""

        try:
            response = await self.llm_manager.generate([LLMMessage("user", prompt)])
            motive_data = json.loads(response.content)
            
            return ConspiracyMotive(
                primary_driver=motive_data["primary_driver"],
                emotional_trigger=EmotionalState(advisor_emotional["emotion"]),
                rational_justification=motive_data["rational_justification"],
                personal_stakes=min(max(float(motive_data["personal_stakes"]), 0.0), 1.0),
                ideological_alignment=min(max(float(motive_data["ideological_alignment"]), -1.0), 1.0),
                urgency_level=min(max(float(motive_data["urgency_level"]), 0.0), 1.0)
            )
            
        except Exception as e:
            self.logger.error(f"Error generating conspiracy motive for {advisor_name}: {e}")
            return None
    
    async def generate_conspiracy_plot(self, initiator: str, motive: ConspiracyMotive,
                                     conditions: Dict[str, float]) -> Optional[ConspiracyPlot]:
        """Generate a complete conspiracy plot."""
        advisor = self.dialogue_system.advisor_council.advisors[initiator]
        
        # Use LLM to generate comprehensive conspiracy plot
        prompt = f"""Generate a detailed conspiracy plot initiated by {initiator}.

INITIATOR PROFILE:
- Name: {advisor.personality.name}
- Role: {advisor.role.value}
- Expertise: {', '.join(advisor.personality.expertise_areas)}

CONSPIRACY MOTIVE:
- Primary Driver: {motive.primary_driver}
- Emotional Trigger: {motive.emotional_trigger.value}
- Rational Justification: {motive.rational_justification}
- Personal Stakes: {motive.personal_stakes}
- Urgency: {motive.urgency_level}

POLITICAL CONDITIONS:
{json.dumps(conditions, indent=2)}

Generate a conspiracy plot that includes:
1. Conspiracy type from: {[t.value for t in ConspiracyType]}
2. Compelling title
3. Detailed description
4. Primary target
5. Timeline with 3-5 phases
6. Required resources
7. Success/failure conditions
8. Potential consequences
9. Discovery indicators

The plot should be:
- Realistic for the advisor's role and expertise
- Appropriate for current political conditions
- Achievable with available resources
- Consistent with the advisor's motivations

Respond in JSON format:
{{
    "conspiracy_type": "one of the valid types",
    "title": "Compelling conspiracy title",
    "description": "Detailed plot description",
    "target": "Primary target of the conspiracy",
    "timeline": {{
        "Phase 1": "Initial preparation phase",
        "Phase 2": "Recruitment and planning",
        "Phase 3": "Resource gathering",
        "Phase 4": "Execution phase",
        "Phase 5": "Aftermath management"
    }},
    "required_resources": {{
        "gold": 100,
        "influence": 50,
        "military_support": 25
    }},
    "success_conditions": ["condition 1", "condition 2"],
    "failure_conditions": ["condition 1", "condition 2"],
    "potential_consequences": {{
        "success": ["positive outcome 1", "positive outcome 2"],
        "failure": ["negative outcome 1", "negative outcome 2"]
    }},
    "discovery_indicators": ["indicator 1", "indicator 2"]
}}"""

        try:
            response = await self.llm_manager.generate([LLMMessage("user", prompt)])
            plot_data = json.loads(response.content)
            
            # Validate conspiracy type
            try:
                conspiracy_type = ConspiracyType(plot_data["conspiracy_type"])
            except ValueError:
                conspiracy_type = ConspiracyType.CORRUPTION  # Default fallback
            
            # Create initial participant (the initiator)
            initial_participant = ConspiracyParticipant(
                advisor_name=initiator,
                role_in_conspiracy="Initiator",
                commitment_level=motive.personal_stakes,
                discovery_risk=0.3,  # Initiators take on higher risk
                potential_rewards=["Political power", "Personal revenge", "Ideological goals"],
                potential_costs=["Execution", "Exile", "Loss of position"],
                recruitment_method="Self-initiated"
            )
            
            plot_id = f"conspiracy_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            
            return ConspiracyPlot(
                plot_id=plot_id,
                conspiracy_type=conspiracy_type,
                title=plot_data["title"],
                description=plot_data["description"],
                primary_motive=motive,
                target=plot_data.get("target"),
                participants=[initial_participant],
                timeline=plot_data["timeline"],
                required_resources=plot_data["required_resources"],
                success_conditions=plot_data["success_conditions"],
                failure_conditions=plot_data["failure_conditions"],
                potential_consequences=plot_data["potential_consequences"],
                discovery_indicators=plot_data["discovery_indicators"],
                status=ConspiracyStatus.PLANNING
            )
            
        except Exception as e:
            self.logger.error(f"Error generating conspiracy plot: {e}")
            return None
    
    async def evaluate_recruitment_targets(self, conspiracy: ConspiracyPlot) -> List[Tuple[str, float]]:
        """Evaluate potential recruitment targets for a conspiracy."""
        targets = []
        initiator = conspiracy.participants[0].advisor_name
        
        for advisor_name, advisor in self.dialogue_system.advisor_council.advisors.items():
            if advisor_name == initiator:
                continue
            
            # Calculate recruitment suitability
            suitability = await self._calculate_recruitment_suitability(
                conspiracy, initiator, advisor_name
            )
            
            if suitability > 0.3:  # Minimum threshold for consideration
                targets.append((advisor_name, suitability))
        
        # Sort by suitability score
        return sorted(targets, key=lambda x: x[1], reverse=True)
    
    async def _calculate_recruitment_suitability(self, conspiracy: ConspiracyPlot, 
                                               initiator: str, target: str) -> float:
        """Calculate how suitable a target is for recruitment."""
        target_emotional = self.dialogue_system.get_advisor_emotional_state(target)
        target_advisor = self.dialogue_system.advisor_council.advisors[target]
        
        # Base suitability factors
        factors = {
            "emotional_state": 0.0,
            "role_compatibility": 0.0,
            "relationship_quality": 0.0,
            "ideological_alignment": 0.0,
            "risk_tolerance": 0.0
        }
        
        # Emotional state factor (angry/suspicious advisors more likely to join)
        if target_emotional["emotion"] in ["angry", "suspicious", "worried"]:
            factors["emotional_state"] = target_emotional["intensity"]
        
        # Role compatibility (some roles work better together)
        role_synergies = {
            ConspiracyType.COUP: [AdvisorRole.MILITARY, AdvisorRole.INTELLIGENCE],
            ConspiracyType.ECONOMIC_MANIPULATION: [AdvisorRole.ECONOMIC, AdvisorRole.INTELLIGENCE],
            ConspiracyType.FOREIGN_INFILTRATION: [AdvisorRole.DIPLOMATIC, AdvisorRole.INTELLIGENCE],
            ConspiracyType.INFORMATION_LEAK: [AdvisorRole.INTELLIGENCE, AdvisorRole.DIPLOMATIC]
        }
        
        if conspiracy.conspiracy_type in role_synergies:
            if target_advisor.role in role_synergies[conspiracy.conspiracy_type]:
                factors["role_compatibility"] = 0.8
        
        # Use LLM to assess relationship and ideological alignment
        factors.update(await self._llm_assess_recruitment_factors(conspiracy, initiator, target))
        
        # Calculate weighted suitability score
        weights = {
            "emotional_state": 0.25,
            "role_compatibility": 0.20,
            "relationship_quality": 0.25,
            "ideological_alignment": 0.20,
            "risk_tolerance": 0.10
        }
        
        return sum(factors[factor] * weights[factor] for factor in factors)
    
    async def _llm_assess_recruitment_factors(self, conspiracy: ConspiracyPlot,
                                           initiator: str, target: str) -> Dict[str, float]:
        """Use LLM to assess recruitment factors."""
        try:
            initiator_advisor = self.dialogue_system.advisor_council.advisors[initiator]
            target_advisor = self.dialogue_system.advisor_council.advisors[target]
            
            # Get recent dialogue history between these advisors
            dialogue_history = ""
            for dialogue in self.dialogue_system.active_dialogues.values():
                if initiator in dialogue.context.participants and target in dialogue.context.participants:
                    dialogue_history += dialogue.get_conversation_history() + "\n"
            
            prompt = f"""Assess recruitment potential for conspiracy involvement.

CONSPIRACY DETAILS:
- Type: {conspiracy.conspiracy_type.value}
- Title: {conspiracy.title}
- Motive: {conspiracy.primary_motive.primary_driver}

INITIATOR: {initiator_advisor.personality.name}
- Role: {initiator_advisor.role.value}
- Traits: {', '.join(initiator_advisor.personality.personality_traits)}

TARGET: {target_advisor.personality.name}
- Role: {target_advisor.role.value}
- Traits: {', '.join(target_advisor.personality.personality_traits)}

RECENT INTERACTIONS:
{dialogue_history or "No recent direct interactions"}

Assess these factors (0.0 to 1.0):
1. Relationship quality between initiator and target
2. Ideological alignment with conspiracy goals
3. Risk tolerance for conspiracy participation

Respond in JSON format:
{{
    "relationship_quality": 0.0-1.0,
    "ideological_alignment": 0.0-1.0,
    "risk_tolerance": 0.0-1.0
}}"""

            response = await self.llm_manager.generate([LLMMessage("user", prompt)])
            return json.loads(response.content)
            
        except Exception as e:
            self.logger.error(f"Error in LLM recruitment assessment: {e}")
            return {"relationship_quality": 0.5, "ideological_alignment": 0.5, "risk_tolerance": 0.5}
    
    async def process_conspiracy_turn(self, conspiracy: ConspiracyPlot, 
                                    game_state: Any) -> Dict[str, Any]:
        """Process a turn for an active conspiracy."""
        results = {
            "status_change": False,
            "new_participants": [],
            "events": [],
            "discovery_risk": 0.0,
            "progress": 0.0
        }
        
        if conspiracy.status == ConspiracyStatus.PLANNING:
            # Attempt recruitment
            recruitment_targets = await self.evaluate_recruitment_targets(conspiracy)
            if recruitment_targets:
                target_name, suitability = recruitment_targets[0]
                if random.random() < suitability * 0.5:  # 50% max chance modified by suitability
                    await self._recruit_conspirator(conspiracy, target_name)
                    results["new_participants"].append(target_name)
            
            # Move to recruiting phase if we have enough participants
            if len(conspiracy.participants) >= 2:
                conspiracy.status = ConspiracyStatus.RECRUITING
                results["status_change"] = True
        
        elif conspiracy.status == ConspiracyStatus.RECRUITING:
            # Continue recruitment and move to preparation
            if len(conspiracy.participants) >= 3 or random.random() < 0.3:
                conspiracy.status = ConspiracyStatus.PREPARATION
                results["status_change"] = True
        
        elif conspiracy.status == ConspiracyStatus.PREPARATION:
            # Gather resources and prepare for execution
            results["progress"] = random.uniform(0.2, 0.4)
            if random.random() < 0.25:  # 25% chance to move to execution
                conspiracy.status = ConspiracyStatus.EXECUTION
                results["status_change"] = True
        
        elif conspiracy.status == ConspiracyStatus.EXECUTION:
            # Execute the conspiracy
            success_chance = self._calculate_conspiracy_success_chance(conspiracy, game_state)
            if random.random() < success_chance:
                conspiracy.status = ConspiracyStatus.SUCCESSFUL
                results["events"].append(f"Conspiracy '{conspiracy.title}' has succeeded!")
            else:
                conspiracy.status = ConspiracyStatus.FAILED
                results["events"].append(f"Conspiracy '{conspiracy.title}' has failed!")
            results["status_change"] = True
        
        # Calculate discovery risk
        results["discovery_risk"] = self._calculate_discovery_risk(conspiracy)
        
        # Check for discovery
        if random.random() < results["discovery_risk"]:
            conspiracy.status = ConspiracyStatus.DISCOVERED
            results["events"].append(f"Conspiracy '{conspiracy.title}' has been discovered!")
            results["status_change"] = True
        
        conspiracy.last_update = datetime.now()
        return results
    
    async def _recruit_conspirator(self, conspiracy: ConspiracyPlot, target_name: str):
        """Recruit a new conspirator to the conspiracy."""
        target_advisor = self.dialogue_system.advisor_council.advisors[target_name]
        
        # Generate recruitment approach using LLM
        prompt = f"""Generate a conspiracy recruitment approach.

CONSPIRACY: {conspiracy.title}
TYPE: {conspiracy.conspiracy_type.value}
MOTIVE: {conspiracy.primary_motive.primary_driver}

TARGET: {target_advisor.personality.name}
- Role: {target_advisor.role.value}
- Traits: {', '.join(target_advisor.personality.personality_traits)}

Generate:
1. Recruitment method used
2. Commitment level (0.0-1.0)
3. Role in conspiracy
4. Discovery risk (0.0-1.0)

Respond in JSON format:
{{
    "recruitment_method": "How they were recruited",
    "commitment_level": 0.0-1.0,
    "role_in_conspiracy": "Their role in the plot",
    "discovery_risk": 0.0-1.0
}}"""

        try:
            response = await self.llm_manager.generate([LLMMessage("user", prompt)])
            recruitment_data = json.loads(response.content)
            
            participant = ConspiracyParticipant(
                advisor_name=target_name,
                role_in_conspiracy=recruitment_data["role_in_conspiracy"],
                commitment_level=min(max(float(recruitment_data["commitment_level"]), 0.0), 1.0),
                discovery_risk=min(max(float(recruitment_data["discovery_risk"]), 0.0), 1.0),
                potential_rewards=["Increased influence", "Policy changes", "Personal advancement"],
                potential_costs=["Loss of position", "Reputation damage", "Punishment"],
                recruitment_method=recruitment_data["recruitment_method"]
            )
            
            conspiracy.participants.append(participant)
            
        except Exception as e:
            self.logger.error(f"Error recruiting conspirator {target_name}: {e}")
    
    def _calculate_conspiracy_success_chance(self, conspiracy: ConspiracyPlot, 
                                           game_state: Any) -> float:
        """Calculate the success chance of a conspiracy during execution."""
        base_chance = 0.4  # 40% base success rate
        
        # Factors that increase success chance
        participant_quality = sum(p.commitment_level for p in conspiracy.participants) / len(conspiracy.participants)
        role_diversity = len(set(self.dialogue_system.advisor_council.advisors[p.advisor_name].role 
                                for p in conspiracy.participants))
        
        # Political instability helps conspiracies
        instability_bonus = 0.0
        if hasattr(game_state, 'stability'):
            instability_bonus = max(0, (100 - game_state.stability) / 200)  # Up to 50% bonus
        
        success_chance = base_chance + (participant_quality * 0.3) + (role_diversity * 0.1) + instability_bonus
        
        return min(max(success_chance, 0.1), 0.9)  # Clamp between 10% and 90%
    
    def _calculate_discovery_risk(self, conspiracy: ConspiracyPlot) -> float:
        """Calculate the risk of conspiracy discovery."""
        base_risk = 0.05  # 5% base discovery risk per turn
        
        # More participants = higher risk
        participant_risk = len(conspiracy.participants) * 0.02
        
        # Higher secrecy level = lower risk
        secrecy_modifier = (1.0 - conspiracy.secrecy_level) * 0.1
        
        # Status affects risk
        status_modifiers = {
            ConspiracyStatus.PLANNING: 0.01,
            ConspiracyStatus.RECRUITING: 0.03,
            ConspiracyStatus.PREPARATION: 0.05,
            ConspiracyStatus.EXECUTION: 0.15
        }
        
        status_risk = status_modifiers.get(conspiracy.status, 0.0)
        
        total_risk = base_risk + participant_risk + secrecy_modifier + status_risk
        return min(max(total_risk, 0.01), 0.3)  # Clamp between 1% and 30%
    
    async def generate_conspiracies_for_turn(self, game_state: Any, 
                                           advisor_council: Any) -> List[ConspiracyPlot]:
        """Generate new conspiracies for the current turn."""
        new_conspiracies = []
        
        # Analyze conditions for conspiracy formation
        conditions = await self.analyze_conspiracy_conditions(game_state, advisor_council)
        
        # Calculate overall conspiracy likelihood
        avg_condition_score = sum(conditions.values()) / len(conditions)
        conspiracy_chance = self.base_conspiracy_chance * (1 + avg_condition_score)
        
        # Apply political instability multiplier
        if conditions.get("political_instability", 0) > 0.6:
            conspiracy_chance *= self.political_instability_multiplier
        
        # Check if a conspiracy should form this turn
        if random.random() < conspiracy_chance:
            # Select an advisor to initiate the conspiracy
            for advisor_name in self.dialogue_system.advisor_council.advisors:
                motive = await self.generate_conspiracy_motive(advisor_name, conditions)
                if motive and motive.urgency_level > 0.5:
                    conspiracy = await self.generate_conspiracy_plot(advisor_name, motive, conditions)
                    if conspiracy:
                        self.active_conspiracies[conspiracy.plot_id] = conspiracy
                        new_conspiracies.append(conspiracy)
                        self.logger.info(f"New conspiracy initiated: {conspiracy.title}")
                        break  # Only one conspiracy per turn
        
        return new_conspiracies
    
    def get_conspiracy_summary(self, plot_id: str) -> Optional[Dict[str, Any]]:
        """Get a comprehensive summary of a conspiracy."""
        conspiracy = self.active_conspiracies.get(plot_id)
        if not conspiracy:
            # Check historical conspiracies
            for historical in self.conspiracy_history:
                if historical.plot_id == plot_id:
                    conspiracy = historical
                    break
        
        if not conspiracy:
            return None
        
        return {
            "plot_id": conspiracy.plot_id,
            "title": conspiracy.title,
            "type": conspiracy.conspiracy_type.value,
            "status": conspiracy.status.value,
            "description": conspiracy.description,
            "target": conspiracy.target,
            "participants": [
                {
                    "name": p.advisor_name,
                    "role": p.role_in_conspiracy,
                    "commitment": p.commitment_level
                }
                for p in conspiracy.participants
            ],
            "current_phase": len([s for s in conspiracy.timeline.keys()]) - len(conspiracy.timeline) + \
                           (1 if conspiracy.status != ConspiracyStatus.PLANNING else 0),
            "discovery_risk": self._calculate_discovery_risk(conspiracy),
            "creation_date": conspiracy.creation_date.isoformat(),
            "last_update": conspiracy.last_update.isoformat()
        }
    
    def get_all_active_conspiracies(self) -> List[Dict[str, Any]]:
        """Get summaries of all active conspiracies."""
        return [self.get_conspiracy_summary(plot_id) for plot_id in self.active_conspiracies.keys()]
    
    async def process_all_conspiracies(self, game_state: Any) -> Dict[str, Any]:
        """Process all active conspiracies for the current turn."""
        results = {
            "conspiracy_events": [],
            "status_changes": [],
            "new_participants": [],
            "discovered_conspiracies": [],
            "completed_conspiracies": []
        }
        
        # Process each active conspiracy
        conspiracies_to_remove = []
        
        for plot_id, conspiracy in self.active_conspiracies.items():
            if conspiracy.status in [ConspiracyStatus.DISCOVERED, ConspiracyStatus.SUCCESSFUL, 
                                   ConspiracyStatus.FAILED]:
                continue
            
            turn_results = await self.process_conspiracy_turn(conspiracy, game_state)
            
            if turn_results["events"]:
                results["conspiracy_events"].extend(turn_results["events"])
            
            if turn_results["status_change"]:
                results["status_changes"].append({
                    "plot_id": plot_id,
                    "title": conspiracy.title,
                    "new_status": conspiracy.status.value
                })
            
            if turn_results["new_participants"]:
                results["new_participants"].extend([
                    {"conspiracy": conspiracy.title, "participant": name}
                    for name in turn_results["new_participants"]
                ])
            
            # Move completed conspiracies to history
            if conspiracy.status in [ConspiracyStatus.DISCOVERED, ConspiracyStatus.SUCCESSFUL, 
                                   ConspiracyStatus.FAILED]:
                conspiracies_to_remove.append(plot_id)
                results["completed_conspiracies"].append({
                    "title": conspiracy.title,
                    "status": conspiracy.status.value
                })
        
        # Move completed conspiracies to history
        for plot_id in conspiracies_to_remove:
            conspiracy = self.active_conspiracies.pop(plot_id)
            self.conspiracy_history.append(conspiracy)
        
        return results
