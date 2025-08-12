"""
Dynamic Crisis Management System

Provides AI-generated political crisis scenarios with real-time management,
escalation dynamics, and interactive response coordination with advisor consultation.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import random

from llm.dialogue import MultiAdvisorDialogue, DialogueContext, DialogueType
from llm.advisors import AdvisorCouncil, AdvisorRole
from llm.llm_providers import LLMManager
from llm.emergent_storytelling import EmergentStorytellingManager, NarrativeThread, NarrativeType
from llm.information_warfare import InformationWarfareManager


class CrisisType(Enum):
    """Types of political crises that can occur."""
    ECONOMIC_COLLAPSE = "economic_collapse"
    MILITARY_THREAT = "military_threat"
    DIPLOMATIC_INCIDENT = "diplomatic_incident"
    NATURAL_DISASTER = "natural_disaster"
    CIVIL_UNREST = "civil_unrest"
    CORRUPTION_SCANDAL = "corruption_scandal"
    CYBER_ATTACK = "cyber_attack"
    REFUGEE_CRISIS = "refugee_crisis"
    ENERGY_CRISIS = "energy_crisis"
    PANDEMIC_OUTBREAK = "pandemic_outbreak"
    TERRORIST_ATTACK = "terrorist_attack"
    POLITICAL_ASSASSINATION = "political_assassination"


class CrisisUrgency(Enum):
    """Urgency levels for crisis management."""
    LOW = "low"           # Hours to respond
    MEDIUM = "medium"     # Minutes to hours
    HIGH = "high"         # Minutes to respond
    CRITICAL = "critical" # Immediate response required


class CrisisStatus(Enum):
    """Current status of a crisis."""
    EMERGING = "emerging"
    ACTIVE = "active"
    ESCALATING = "escalating"
    STABILIZING = "stabilizing"
    RESOLVED = "resolved"
    FAILED = "failed"


class ResponseType(Enum):
    """Types of crisis response actions."""
    IMMEDIATE_ACTION = "immediate_action"
    DIPLOMATIC_RESPONSE = "diplomatic_response"
    MILITARY_DEPLOYMENT = "military_deployment"
    ECONOMIC_INTERVENTION = "economic_intervention"
    PUBLIC_COMMUNICATION = "public_communication"
    EMERGENCY_LEGISLATION = "emergency_legislation"
    HUMANITARIAN_AID = "humanitarian_aid"
    INTELLIGENCE_OPERATION = "intelligence_operation"
    EVACUATION_ORDER = "evacuation_order"
    NEGOTIATE = "negotiate"


@dataclass
class CrisisEffect:
    """Represents the effect of a crisis on various game metrics."""
    political_stability: float = 0.0      # -1.0 to 1.0
    public_approval: float = 0.0          # -1.0 to 1.0
    economic_impact: float = 0.0          # -1.0 to 1.0
    international_standing: float = 0.0   # -1.0 to 1.0
    military_readiness: float = 0.0       # -1.0 to 1.0
    resource_cost: int = 0                # Resource points required
    casualties: int = 0                   # Human cost
    duration_hours: int = 24              # How long effects last


@dataclass
class ResponseOption:
    """Represents a possible response to a crisis."""
    response_id: str
    response_type: ResponseType
    title: str
    description: str
    requirements: Dict[str, Any]  # Resources, conditions needed
    success_probability: float    # 0.0 to 1.0
    time_required: int           # Hours to implement
    risk_level: float            # 0.0 to 1.0
    potential_effects: CrisisEffect
    advisor_recommendations: Dict[str, float]  # advisor_role -> support_level


@dataclass
class CrisisEvent:
    """Represents a dynamic political crisis."""
    crisis_id: str
    crisis_type: CrisisType
    title: str
    description: str
    urgency: CrisisUrgency
    status: CrisisStatus
    
    # Crisis progression
    escalation_level: float = 0.0      # 0.0 to 1.0
    time_pressure: float = 1.0         # Multiplier for urgency
    turns_remaining: Optional[int] = None
    
    # Effects and context
    current_effects: CrisisEffect = field(default_factory=CrisisEffect)
    background_context: str = ""
    affected_regions: List[str] = field(default_factory=list)
    key_actors: List[str] = field(default_factory=list)
    
    # Response management
    available_responses: List[ResponseOption] = field(default_factory=list)
    attempted_responses: List[str] = field(default_factory=list)
    response_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Narrative integration
    narrative_threads: List[str] = field(default_factory=list)
    media_attention: float = 0.5       # 0.0 to 1.0
    
    # Timestamps
    start_time: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)
    resolution_deadline: Optional[datetime] = None


@dataclass
class CrisisDecision:
    """Represents a player decision during crisis management."""
    decision_id: str
    crisis_id: str
    response_option_id: str
    rationale: str
    advisor_consultation: Dict[str, str]  # advisor -> their input
    timestamp: datetime = field(default_factory=datetime.now)


class DynamicCrisisManager:
    """AI-generated dynamic crisis management system with real-time escalation and response."""
    
    def __init__(self, llm_manager: LLMManager, advisor_council: AdvisorCouncil,
                 dialogue_system: MultiAdvisorDialogue, storytelling_manager: EmergentStorytellingManager,
                 information_warfare: InformationWarfareManager):
        self.llm_manager = llm_manager
        self.advisor_council = advisor_council
        self.dialogue_system = dialogue_system
        self.storytelling_manager = storytelling_manager
        self.information_warfare = information_warfare
        
        # Crisis tracking
        self.active_crises: Dict[str, CrisisEvent] = {}
        self.completed_crises: List[CrisisEvent] = []
        self.crisis_decisions: List[CrisisDecision] = []
        
        # Callback systems
        self.crisis_callbacks: List[Callable] = []
        self.escalation_callbacks: List[Callable] = []
        self.decision_callbacks: List[Callable] = []
        
        # Crisis generation parameters
        self.crisis_probability = 0.1  # Base probability per hour
        self.escalation_rate = 0.05    # How quickly crises escalate
        self.max_concurrent_crises = 3
        
        # Monitoring state
        self.monitoring_active = False
        self.last_crisis_check = datetime.now()
        
    def register_crisis_callback(self, callback: Callable):
        """Register callback for new crisis events."""
        self.crisis_callbacks.append(callback)
        
    def register_escalation_callback(self, callback: Callable):
        """Register callback for crisis escalation events."""
        self.escalation_callbacks.append(callback)
        
    def register_decision_callback(self, callback: Callable):
        """Register callback for crisis decision events."""
        self.decision_callbacks.append(callback)
        
    async def start_crisis_monitoring(self):
        """Start continuous monitoring and generation of crisis events."""
        self.monitoring_active = True
        asyncio.create_task(self._monitor_and_generate_crises())
        
    async def stop_crisis_monitoring(self):
        """Stop crisis monitoring and generation."""
        self.monitoring_active = False
        
    async def _monitor_and_generate_crises(self):
        """Background task to monitor existing crises and generate new ones."""
        while self.monitoring_active:
            try:
                # Monitor existing crises for escalation
                await self._update_existing_crises()
                
                # Check for new crisis generation
                if len(self.active_crises) < self.max_concurrent_crises:
                    await self._check_for_new_crisis()
                
                # Wait before next check (every 30 seconds for testing, could be longer)
                await asyncio.sleep(30)
                
            except Exception as e:
                print(f"Error in crisis monitoring: {e}")
                await asyncio.sleep(60)
                
    async def _update_existing_crises(self):
        """Update and potentially escalate existing crises."""
        for crisis_id, crisis in list(self.active_crises.items()):
            if crisis.status in [CrisisStatus.ACTIVE, CrisisStatus.ESCALATING]:
                # Check for escalation
                escalation_occurred = await self._check_crisis_escalation(crisis)
                
                if escalation_occurred:
                    await self._notify_escalation_callbacks(crisis)
                
                # Check for resolution deadline
                if crisis.resolution_deadline and datetime.now() > crisis.resolution_deadline:
                    await self._resolve_crisis_by_timeout(crisis)
                    
    async def _check_crisis_escalation(self, crisis: CrisisEvent) -> bool:
        """Check if a crisis should escalate."""
        time_since_update = (datetime.now() - crisis.last_update).total_seconds() / 3600
        
        # Calculate escalation probability
        base_escalation = self.escalation_rate * time_since_update
        urgency_multiplier = {"low": 0.5, "medium": 1.0, "high": 1.5, "critical": 2.0}[crisis.urgency.value]
        no_response_penalty = 0.2 if not crisis.attempted_responses else 0.0
        
        escalation_chance = base_escalation * urgency_multiplier + no_response_penalty
        
        if random.random() < escalation_chance and crisis.escalation_level < 1.0:  # nosec B311 - Using random for game mechanics, not security
            crisis.escalation_level = min(1.0, crisis.escalation_level + random.uniform(0.1, 0.3))  # nosec B311 - Using random for game mechanics, not security
            crisis.last_update = datetime.now()
            
            # Increase effects with escalation
            crisis.current_effects.political_stability -= 0.1
            crisis.current_effects.public_approval -= 0.05
            crisis.media_attention = min(1.0, crisis.media_attention + 0.2)
            
            # Update status
            if crisis.escalation_level > 0.7 and crisis.status != CrisisStatus.ESCALATING:
                crisis.status = CrisisStatus.ESCALATING
                
            return True
            
        return False
        
    async def _check_for_new_crisis(self):
        """Check if a new crisis should be generated."""
        time_since_last = (datetime.now() - self.last_crisis_check).total_seconds() / 3600
        crisis_chance = self.crisis_probability * time_since_last
        
        if random.random() < crisis_chance:  # nosec B311 - Using random for game mechanics, not security
            new_crisis = await self._generate_new_crisis()
            if new_crisis:
                self.active_crises[new_crisis.crisis_id] = new_crisis
                await self._notify_crisis_callbacks(new_crisis)
                
        self.last_crisis_check = datetime.now()
        
    async def _generate_new_crisis(self) -> Optional[CrisisEvent]:
        """Generate a new dynamic crisis using AI."""
        crisis_types = list(CrisisType)
        crisis_type = random.choice(crisis_types)  # nosec B311 - Using random for game mechanics, not security
        crisis_details = await self._ai_generate_crisis_details(crisis_type)
        
        if not crisis_details:
            return None
            
        crisis_id = f"crisis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{crisis_type.value}"
        
        # Determine urgency based on crisis type
        urgency_map = {
            CrisisType.TERRORIST_ATTACK: CrisisUrgency.CRITICAL,
            CrisisType.MILITARY_THREAT: CrisisUrgency.HIGH,
            CrisisType.CYBER_ATTACK: CrisisUrgency.HIGH,
            CrisisType.NATURAL_DISASTER: CrisisUrgency.HIGH,
            CrisisType.CIVIL_UNREST: CrisisUrgency.MEDIUM,
            CrisisType.ECONOMIC_COLLAPSE: CrisisUrgency.MEDIUM,
            CrisisType.CORRUPTION_SCANDAL: CrisisUrgency.LOW
        }
        
        urgency = urgency_map.get(crisis_type, CrisisUrgency.MEDIUM)
        
        # Set resolution deadline based on urgency
        deadline_hours = {"critical": 2, "high": 12, "medium": 48, "low": 168}[urgency.value]
        resolution_deadline = datetime.now() + timedelta(hours=deadline_hours)
        
        crisis = CrisisEvent(
            crisis_id=crisis_id,
            crisis_type=crisis_type,
            title=crisis_details["title"],
            description=crisis_details["description"],
            urgency=urgency,
            status=CrisisStatus.EMERGING,
            background_context=crisis_details.get("background", ""),
            affected_regions=crisis_details.get("regions", []),
            key_actors=crisis_details.get("actors", []),
            resolution_deadline=resolution_deadline,
            media_attention=random.uniform(0.3, 0.8)  # nosec B311 - Using random for game mechanics, not security
        )
        
        # Generate initial response options
        crisis.available_responses = await self._generate_response_options(crisis)
        
        # Create narrative threads for storytelling integration
        if crisis.crisis_type in [CrisisType.CORRUPTION_SCANDAL, CrisisType.POLITICAL_ASSASSINATION]:
            narrative_thread = await self._create_crisis_narrative(crisis)
            if narrative_thread:
                crisis.narrative_threads.append(narrative_thread)
        
        return crisis
        
    async def _ai_generate_crisis_details(self, crisis_type: CrisisType) -> Optional[Dict[str, Any]]:
        """Use AI to generate realistic crisis details."""
        crisis_templates = {
            CrisisType.ECONOMIC_COLLAPSE: {
                "title": "Economic Market Volatility Crisis",
                "description": "Major financial markets experiencing severe instability with widespread economic implications",
                "background": "Triggered by international market pressures and domestic policy uncertainties",
                "regions": ["Capital District", "Major Cities"],
                "actors": ["Finance Minister", "Central Bank Governor", "Business Leaders"]
            },
            CrisisType.DIPLOMATIC_INCIDENT: {
                "title": "International Diplomatic Crisis",
                "description": "Serious diplomatic incident threatening international relations and regional stability", 
                "background": "Escalating tensions with neighboring countries over trade and territorial disputes",
                "regions": ["Border Regions", "Embassy District"],
                "actors": ["Foreign Minister", "Ambassador", "International Leaders"]
            },
            CrisisType.CIVIL_UNREST: {
                "title": "Public Demonstration Crisis",
                "description": "Large-scale civil unrest with public demonstrations affecting government operations",
                "background": "Public frustration over recent policy decisions has reached a tipping point",
                "regions": ["Capital City", "Urban Centers"],
                "actors": ["Protest Leaders", "Police Chief", "Civil Rights Groups"]
            },
            CrisisType.CYBER_ATTACK: {
                "title": "Critical Infrastructure Cyber Attack",
                "description": "Sophisticated cyber attack targeting government systems and critical infrastructure",
                "background": "State-sponsored hackers have breached multiple government networks",
                "regions": ["National Infrastructure", "Government Facilities"],
                "actors": ["IT Director", "National Security Advisor", "Foreign Intelligence"]
            }
        }
        
        return crisis_templates.get(crisis_type, {
            "title": f"Developing {crisis_type.value.replace('_', ' ').title()} Crisis",
            "description": f"A {crisis_type.value.replace('_', ' ')} situation requiring immediate government attention",
            "background": "Situation developing rapidly with potential for significant impact",
            "regions": ["Affected Area"],
            "actors": ["Government Officials", "Local Authorities"]
        })
        
    async def _generate_response_options(self, crisis: CrisisEvent) -> List[ResponseOption]:
        """Generate appropriate response options for a crisis."""
        base_responses = []
        
        # Generate crisis-specific responses
        if crisis.crisis_type == CrisisType.ECONOMIC_COLLAPSE:
            base_responses.extend([
                ResponseOption(
                    response_id="economic_stimulus",
                    response_type=ResponseType.ECONOMIC_INTERVENTION,
                    title="Emergency Economic Stimulus",
                    description="Deploy emergency financial measures to stabilize markets",
                    requirements={"economic_resources": 500, "legislative_support": 0.6},
                    success_probability=0.7,
                    time_required=6,
                    risk_level=0.3,
                    potential_effects=CrisisEffect(economic_impact=0.4, resource_cost=500),
                    advisor_recommendations={"economic": 0.9, "diplomatic": 0.5}
                ),
                ResponseOption(
                    response_id="market_intervention",
                    response_type=ResponseType.IMMEDIATE_ACTION,
                    title="Direct Market Intervention",
                    description="Government intervention in financial markets to prevent collapse",
                    requirements={"economic_resources": 800, "emergency_powers": True},
                    success_probability=0.8,
                    time_required=2,
                    risk_level=0.6,
                    potential_effects=CrisisEffect(economic_impact=0.6, political_stability=-0.2, resource_cost=800),
                    advisor_recommendations={"economic": 0.8, "military": 0.3}
                )
            ])
            
        elif crisis.crisis_type == CrisisType.CIVIL_UNREST:
            base_responses.extend([
                ResponseOption(
                    response_id="peaceful_dialogue",
                    response_type=ResponseType.DIPLOMATIC_RESPONSE,
                    title="Open Dialogue with Protesters",
                    description="Initiate peaceful negotiations with protest leaders",
                    requirements={"diplomatic_influence": 0.7},
                    success_probability=0.6,
                    time_required=8,
                    risk_level=0.2,
                    potential_effects=CrisisEffect(public_approval=0.3, political_stability=0.2),
                    advisor_recommendations={"diplomatic": 0.9, "domestic": 0.8}
                ),
                ResponseOption(
                    response_id="security_response",
                    response_type=ResponseType.MILITARY_DEPLOYMENT,
                    title="Enhanced Security Measures",
                    description="Deploy security forces to maintain order and protect infrastructure",
                    requirements={"military_resources": 300, "security_authorization": True},
                    success_probability=0.8,
                    time_required=2,
                    risk_level=0.7,
                    potential_effects=CrisisEffect(political_stability=0.3, public_approval=-0.4, casualties=10),
                    advisor_recommendations={"military": 0.8, "diplomatic": 0.2}
                )
            ])
            
        # Add universal responses available for all crises
        base_responses.extend([
            ResponseOption(
                response_id="public_address",
                response_type=ResponseType.PUBLIC_COMMUNICATION,
                title="Presidential Address to Nation",
                description="Address the public directly to provide leadership and reassurance",
                requirements={"public_trust": 0.4},
                success_probability=0.5,
                time_required=1,
                risk_level=0.3,
                potential_effects=CrisisEffect(public_approval=0.2, political_stability=0.1),
                advisor_recommendations={"domestic": 0.7, "diplomatic": 0.6}
            ),
            ResponseOption(
                response_id="advisor_consultation",
                response_type=ResponseType.IMMEDIATE_ACTION,
                title="Emergency Advisor Council Meeting",
                description="Convene all advisors for comprehensive crisis analysis and recommendations",
                requirements={},
                success_probability=0.9,
                time_required=1,
                risk_level=0.1,
                potential_effects=CrisisEffect(political_stability=0.1),
                advisor_recommendations={"intelligence": 0.9, "military": 0.8, "diplomatic": 0.8}
            )
        ])
        
        return base_responses
        
    async def _create_crisis_narrative(self, crisis: CrisisEvent) -> Optional[str]:
        """Create narrative threads for crisis storytelling integration."""
        narrative_prompt = f"""
        Crisis Narrative Generation:
        Type: {crisis.crisis_type.value}
        Title: {crisis.title}
        Context: {crisis.description}
        
        Create a compelling narrative thread that can evolve based on player responses.
        """
        
        # Use storytelling manager to create narrative
        narrative_thread = NarrativeThread(
            thread_id=f"crisis_narrative_{crisis.crisis_id}",
            narrative_type=NarrativeType.POLITICAL_INTRIGUE,
            title=f"The {crisis.title} Saga",
            description=f"Political drama surrounding {crisis.description}",
            main_characters=crisis.key_actors,
            plot_points=[],
            current_momentum=0.8,  # High momentum for crisis narratives
            emotional_tone="tense"
        )
        
        # Register with storytelling manager
        thread_id = await self.storytelling_manager.create_narrative_thread(
            narrative_thread.narrative_type,
            narrative_thread.title,
            {"crisis_context": crisis.description, "characters": crisis.key_actors}
        )
        
        return thread_id
        
    async def get_crisis_advisor_consultation(self, crisis_id: str, specific_question: str = "") -> Dict[str, str]:
        """Get AI advisor input on crisis management."""
        if crisis_id not in self.active_crises:
            raise ValueError(f"Crisis {crisis_id} not found")
            
        crisis = self.active_crises[crisis_id]
        
        consultation_prompt = f"""
        CRISIS CONSULTATION REQUEST
        
        Crisis Type: {crisis.crisis_type.value}
        Title: {crisis.title}
        Status: {crisis.status.value}
        Urgency: {crisis.urgency.value}
        Escalation Level: {crisis.escalation_level:.2f}
        
        Description: {crisis.description}
        Background: {crisis.background_context}
        
        Current Effects:
        - Political Stability: {crisis.current_effects.political_stability:.2f}
        - Public Approval: {crisis.current_effects.public_approval:.2f}
        - Economic Impact: {crisis.current_effects.economic_impact:.2f}
        
        Available Responses: {len(crisis.available_responses)} options
        Previous Attempts: {crisis.attempted_responses}
        
        Specific Question: {specific_question or "What is your recommended response strategy?"}
        
        Please provide your professional assessment and strategic recommendations.
        """
        
        # Get input from relevant advisors
        responses = {}
        
        # Get input from all advisor roles
        advisor_roles = ["military", "economic", "diplomatic", "domestic", "intelligence"]
        
        for role in advisor_roles:
            advisor_response = await self._get_crisis_advisor_input(role, consultation_prompt, crisis)
            responses[f"{role.title()} Advisor"] = advisor_response
            
        return responses
        
    async def _get_crisis_advisor_input(self, advisor_role: str, prompt: str, crisis: CrisisEvent) -> str:
        """Get input from a specific advisor role on crisis management."""
        # Mock responses based on advisor expertise and crisis type
        role_responses = {
            "military": {
                CrisisType.MILITARY_THREAT: "Immediate military readiness required. Deploy defensive measures and coordinate with intelligence.",
                CrisisType.CIVIL_UNREST: "Recommend measured security response. Avoid escalation but maintain order.",
                CrisisType.CYBER_ATTACK: "Coordinate with cyber defense units. Implement emergency protocols.",
                "default": "Assess security implications and prepare contingency measures."
            },
            "economic": {
                CrisisType.ECONOMIC_COLLAPSE: "Emergency fiscal measures needed. Consider market intervention and stimulus.",
                CrisisType.CIVIL_UNREST: "Monitor economic disruption. Prepare business continuity measures.",
                CrisisType.CYBER_ATTACK: "Assess financial system vulnerabilities. Protect critical economic infrastructure.",
                "default": "Evaluate economic impact and prepare mitigation strategies."
            },
            "diplomatic": {
                CrisisType.DIPLOMATIC_INCIDENT: "Immediate diplomatic engagement required. Explore negotiated solutions.",
                CrisisType.MILITARY_THREAT: "Seek diplomatic resolution while preparing defensive measures.",
                CrisisType.CIVIL_UNREST: "Public communication crucial. Consider mediation with protest leaders.",
                "default": "Explore diplomatic solutions and manage international perceptions."
            },
            "domestic": {
                CrisisType.CIVIL_UNREST: "Address underlying public concerns. Transparent communication essential.",
                CrisisType.CORRUPTION_SCANDAL: "Rebuild public trust through accountability and reform.",
                CrisisType.NATURAL_DISASTER: "Coordinate humanitarian response and public safety measures.",
                "default": "Focus on public welfare and domestic stability."
            },
            "intelligence": {
                CrisisType.CYBER_ATTACK: "Investigate attack vectors and attribution. Coordinate with security agencies.",
                CrisisType.TERRORIST_ATTACK: "Assess threat levels and implement security protocols.",
                CrisisType.CORRUPTION_SCANDAL: "Investigate extent of corruption and identify responsible parties.",
                "default": "Gather intelligence on crisis dynamics and threat assessment."
            }
        }
        
        role_specific = role_responses.get(advisor_role, {})
        response = role_specific.get(crisis.crisis_type, role_specific.get("default", "Situation requires careful analysis and measured response."))
        
        return response
        
    async def implement_crisis_response(self, crisis_id: str, response_option_id: str, 
                                      rationale: str = "") -> Dict[str, Any]:
        """Implement a chosen response to a crisis."""
        if crisis_id not in self.active_crises:
            raise ValueError(f"Crisis {crisis_id} not found")
            
        crisis = self.active_crises[crisis_id]
        
        # Find the response option
        response_option = None
        for option in crisis.available_responses:
            if option.response_id == response_option_id:
                response_option = option
                break
                
        if not response_option:
            raise ValueError(f"Response option {response_option_id} not found")
            
        # Check requirements
        requirements_met = await self._check_response_requirements(response_option)
        
        if not requirements_met["can_implement"]:
            return {
                "success": False,
                "reason": "Requirements not met",
                "missing_requirements": requirements_met["missing"],
                "effects": {}
            }
            
        # Get advisor consultation on this specific response
        advisor_input = await self.get_crisis_advisor_consultation(
            crisis_id, 
            f"What are the implications of implementing {response_option.title}?"
        )
        
        # Create decision record
        decision = CrisisDecision(
            decision_id=f"decision_{len(self.crisis_decisions) + 1}",
            crisis_id=crisis_id,
            response_option_id=response_option_id,
            rationale=rationale,
            advisor_consultation=advisor_input
        )
        
        self.crisis_decisions.append(decision)
        
        # Calculate response success
        success_roll = random.random()  # nosec B311 - Using random for game mechanics, not security
        response_succeeded = success_roll < response_option.success_probability
        
        # Apply effects
        effects = await self._apply_response_effects(crisis, response_option, response_succeeded)
        
        # Update crisis state
        crisis.attempted_responses.append(response_option_id)
        crisis.response_history.append({
            "response": response_option.title,
            "success": response_succeeded,
            "timestamp": datetime.now().isoformat(),
            "effects": effects
        })
        crisis.last_update = datetime.now()
        
        # Check if crisis is resolved
        if effects.get("crisis_resolved", False):
            crisis.status = CrisisStatus.RESOLVED
            await self._resolve_crisis(crisis)
            
        # Notify callbacks
        await self._notify_decision_callbacks(decision, response_succeeded, effects)
        
        result = {
            "success": response_succeeded,
            "effects": effects,
            "advisor_input": advisor_input,
            "crisis_status": crisis.status.value,
            "escalation_level": crisis.escalation_level
        }
        
        return result
        
    async def _check_response_requirements(self, response_option: ResponseOption) -> Dict[str, Any]:
        """Check if requirements for a response option are met."""
        # Simplified requirement checking for testing
        # In a real game, this would check actual game state
        
        missing = []
        can_implement = True
        
        for requirement, value in response_option.requirements.items():
            if requirement == "economic_resources" and value > 500:
                missing.append(f"Insufficient economic resources (need {value})")
                can_implement = False
            elif requirement == "military_resources" and value > 400:
                missing.append(f"Insufficient military resources (need {value})")
                can_implement = False
            elif requirement == "public_trust" and value > 0.8:
                missing.append(f"Insufficient public trust (need {value:.1f})")
                can_implement = False
                
        return {
            "can_implement": can_implement,
            "missing": missing
        }
        
    async def _apply_response_effects(self, crisis: CrisisEvent, response_option: ResponseOption, 
                                    success: bool) -> Dict[str, Any]:
        """Apply the effects of a crisis response."""
        effects = {}
        
        if success:
            # Apply positive effects
            crisis.escalation_level = max(0.0, crisis.escalation_level - 0.3)
            effects["escalation_reduction"] = 0.3
            
            # Apply response-specific effects
            if response_option.potential_effects.political_stability > 0:
                effects["political_stability_gain"] = response_option.potential_effects.political_stability
                
            if response_option.potential_effects.public_approval > 0:
                effects["public_approval_gain"] = response_option.potential_effects.public_approval
                
            # Check if crisis is resolved
            if crisis.escalation_level <= 0.2 and crisis.status != CrisisStatus.RESOLVED:
                crisis.status = CrisisStatus.STABILIZING
                effects["crisis_stabilized"] = True
                
            if crisis.escalation_level <= 0.0:
                effects["crisis_resolved"] = True
                
        else:
            # Apply negative effects for failed response
            crisis.escalation_level = min(1.0, crisis.escalation_level + 0.2)
            effects["escalation_increase"] = 0.2
            effects["response_failed"] = True
            
            # Potential for crisis to escalate status
            if crisis.escalation_level > 0.8:
                crisis.status = CrisisStatus.ESCALATING
                
        # Apply resource costs regardless of success
        if response_option.potential_effects.resource_cost > 0:
            effects["resource_cost"] = response_option.potential_effects.resource_cost
            
        # Apply casualties if any
        if response_option.potential_effects.casualties > 0:
            casualties = response_option.potential_effects.casualties
            if not success:
                casualties *= 2  # Double casualties on failure
            effects["casualties"] = casualties
            
        return effects
        
    async def _resolve_crisis(self, crisis: CrisisEvent):
        """Resolve a completed crisis."""
        # Move to completed crises
        self.completed_crises.append(crisis)
        del self.active_crises[crisis.crisis_id]
        
        # Generate final narrative if applicable
        if crisis.narrative_threads:
            for thread_id in crisis.narrative_threads:
                await self._conclude_crisis_narrative(thread_id, crisis)
                
    async def _conclude_crisis_narrative(self, thread_id: str, crisis: CrisisEvent):
        """Conclude narrative threads related to resolved crisis."""
        # Add final plot point to narrative
        resolution_outcome = "successfully resolved" if crisis.status == CrisisStatus.RESOLVED else "concluded"
        
        await self.storytelling_manager.add_plot_point(
            thread_id,
            f"Crisis Resolution: The {crisis.title} was {resolution_outcome} through decisive leadership."
        )
        
    async def _resolve_crisis_by_timeout(self, crisis: CrisisEvent):
        """Resolve crisis that has reached its deadline without resolution."""
        # Crisis fails due to inaction
        crisis.status = CrisisStatus.FAILED
        crisis.escalation_level = 1.0
        
        # Apply severe negative effects
        crisis.current_effects.political_stability -= 0.5
        crisis.current_effects.public_approval -= 0.4
        crisis.current_effects.international_standing -= 0.3
        
        await self._resolve_crisis(crisis)
        
    async def _notify_crisis_callbacks(self, crisis: CrisisEvent):
        """Notify all registered crisis callbacks."""
        for callback in self.crisis_callbacks:
            try:
                await callback(crisis)
            except Exception as e:
                print(f"Error in crisis callback: {e}")
                
    async def _notify_escalation_callbacks(self, crisis: CrisisEvent):
        """Notify all registered escalation callbacks."""
        for callback in self.escalation_callbacks:
            try:
                await callback(crisis)
            except Exception as e:
                print(f"Error in escalation callback: {e}")
                
    async def _notify_decision_callbacks(self, decision: CrisisDecision, success: bool, effects: Dict[str, Any]):
        """Notify all registered decision callbacks."""
        for callback in self.decision_callbacks:
            try:
                await callback(decision, success, effects)
            except Exception as e:
                print(f"Error in decision callback: {e}")
                
    def get_active_crises(self) -> List[CrisisEvent]:
        """Get all currently active crises."""
        return list(self.active_crises.values())
        
    def get_crisis_status(self, crisis_id: str) -> Optional[CrisisEvent]:
        """Get status of a specific crisis."""
        return self.active_crises.get(crisis_id)
        
    def get_crisis_history(self) -> List[CrisisEvent]:
        """Get history of completed crises."""
        return self.completed_crises.copy()
        
    def get_crisis_decisions(self, crisis_id: str = None) -> List[CrisisDecision]:
        """Get crisis decision history, optionally filtered by crisis."""
        if crisis_id:
            return [d for d in self.crisis_decisions if d.crisis_id == crisis_id]
        return self.crisis_decisions.copy()
        
    async def force_crisis_generation(self, crisis_type: CrisisType = None) -> Optional[str]:
        """Force generation of a crisis for testing purposes."""
        if crisis_type:
            # Generate specific crisis type
            crisis_details = await self._ai_generate_crisis_details(crisis_type)
            if crisis_details:
                crisis_id = f"forced_crisis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                crisis = CrisisEvent(
                    crisis_id=crisis_id,
                    crisis_type=crisis_type,
                    title=crisis_details["title"],
                    description=crisis_details["description"],
                    urgency=CrisisUrgency.HIGH,
                    status=CrisisStatus.EMERGING
                )
                
                crisis.available_responses = await self._generate_response_options(crisis)
                self.active_crises[crisis_id] = crisis
                await self._notify_crisis_callbacks(crisis)
                return crisis_id
        else:
            # Generate random crisis
            new_crisis = await self._generate_new_crisis()
            if new_crisis:
                self.active_crises[new_crisis.crisis_id] = new_crisis
                await self._notify_crisis_callbacks(new_crisis)
                return new_crisis.crisis_id
                
        return None
