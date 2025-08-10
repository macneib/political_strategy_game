"""
Interactive Conspiracy Management Interface

Provides real-time conspiracy detection alerts, investigation tools, and 
interactive management systems for players to discover and respond to
political conspiracies with AI advisor assistance.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum

from ..llm.conspiracy import ConspiracyGenerator, ConspiracyPlot, ConspiracyType, ConspiracyStatus
from ..llm.dialogue import MultiAdvisorDialogue, DialogueContext, DialogueType
from ..llm.advisors import AdvisorCouncil, AdvisorRole
from ..llm.llm_providers import LLMManager


class ThreatLevel(Enum):
    """Threat level classification for conspiracy alerts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SuspiciousActivity:
    """Represents a suspicious activity that might indicate conspiracy."""
    activity_type: str
    description: str
    participants: List[str]
    location: str
    timestamp: datetime
    suspicion_level: float  # 0.0 to 1.0


@dataclass
class ConspiracyThreat:
    """Represents a detected conspiracy threat."""
    threat_id: str
    conspiracy_type: str
    threat_level: ThreatLevel
    participants: List[str]
    description: str
    evidence_strength: float
    estimated_timeline: str


class InvestigationAction(Enum):
    """Types of investigation actions players can take."""
    GATHER_INTELLIGENCE = "gather_intelligence"
    INTERVIEW_SUBJECTS = "interview_subjects"
    ANALYZE_COMMUNICATIONS = "analyze_communications"
    SURVEILLANCE = "surveillance"
    CROSS_REFERENCE = "cross_reference"
    CONSULT_ADVISORS = "consult_advisors"
    DEPLOY_AGENTS = "deploy_agents"
    MONITOR_MOVEMENTS = "monitor_movements"


class ResponseAction(Enum):
    """Types of response actions for confirmed conspiracies."""
    ARREST_CONSPIRATORS = "arrest_conspirators"
    INFILTRATE_NETWORK = "infiltrate_network"
    COUNTER_INTELLIGENCE = "counter_intelligence"
    PUBLIC_EXPOSURE = "public_exposure"
    DIPLOMATIC_PRESSURE = "diplomatic_pressure"
    NEUTRALIZE_QUIETLY = "neutralize_quietly"
    TURN_CONSPIRATOR = "turn_conspirator"
    MONITOR_AND_WAIT = "monitor_and_wait"


@dataclass
class InvestigationStep:
    """Represents a step in a conspiracy investigation."""
    action_type: InvestigationAction
    target: str  # Who or what is being investigated
    evidence_gathered: List[str] = field(default_factory=list)
    confidence_level: float = 0.0  # 0.0 to 1.0
    resources_required: int = 1
    duration_hours: int = 24
    risk_level: float = 0.1  # 0.0 to 1.0
    completed: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConspiracyInvestigation:
    """Complete investigation case for a conspiracy threat."""
    threat_id: str
    conspiracy_threat: ConspiracyThreat
    investigation_steps: List[InvestigationStep] = field(default_factory=list)
    evidence_chain: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    status: str = "active"  # active, resolved, abandoned
    assigned_advisors: List[str] = field(default_factory=list)
    player_notes: str = ""
    created_timestamp: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ConspiracyAlert:
    """Real-time conspiracy detection alert for the player."""
    alert_id: str
    threat_level: ThreatLevel
    title: str
    description: str
    suspected_actors: List[str]
    urgency_score: float  # 0.0 to 1.0
    recommended_actions: List[InvestigationAction]
    time_sensitive: bool = False
    expires_at: Optional[datetime] = None
    acknowledged: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


class InteractiveConspiracyManager:
    """Interactive conspiracy detection and management system with AI advisor integration."""
    
    def __init__(self, llm_manager: LLMManager, advisor_council: AdvisorCouncil,
                 dialogue_system: MultiAdvisorDialogue, conspiracy_generator: ConspiracyGenerator):
        self.llm_manager = llm_manager
        self.advisor_council = advisor_council
        self.dialogue_system = dialogue_system
        self.conspiracy_generator = conspiracy_generator
        
        # Investigation management
        self.active_investigations: Dict[str, ConspiracyInvestigation] = {}
        self.pending_alerts: Dict[str, ConspiracyAlert] = {}
        self.completed_investigations: List[ConspiracyInvestigation] = []
        
        # Callback systems for UI updates
        self.alert_callbacks: List[Callable] = []
        self.investigation_callbacks: List[Callable] = []
        self.evidence_callbacks: List[Callable] = []
        
        # Player state tracking
        self.player_investigation_skills = {
            "intelligence_gathering": 0.5,
            "analysis": 0.5,
            "surveillance": 0.5,
            "interrogation": 0.5,
            "counter_intelligence": 0.5
        }
        
        # Alert monitoring
        self.alert_monitoring_active = False
        self.last_conspiracy_scan = datetime.now()
        
    def register_alert_callback(self, callback: Callable):
        """Register callback for new conspiracy alerts."""
        self.alert_callbacks.append(callback)
        
    def register_investigation_callback(self, callback: Callable):
        """Register callback for investigation updates."""
        self.investigation_callbacks.append(callback)
        
    def register_evidence_callback(self, callback: Callable):
        """Register callback for new evidence discoveries."""
        self.evidence_callbacks.append(callback)
        
    async def start_alert_monitoring(self):
        """Start continuous monitoring for conspiracy threats."""
        self.alert_monitoring_active = True
        asyncio.create_task(self._monitor_conspiracy_threats())
        
    async def stop_alert_monitoring(self):
        """Stop conspiracy threat monitoring."""
        self.alert_monitoring_active = False
        
    async def _monitor_conspiracy_threats(self):
        """Background task to monitor for new conspiracy threats."""
        while self.alert_monitoring_active:
            try:
                # Scan for new threats every 30 seconds (configurable)
                await asyncio.sleep(30)
                
                # Get recent activities (mock for testing)
                recent_activities = self._get_recent_suspicious_activities()
                
                # Check for new conspiracy threats
                new_threats = await self._detect_conspiracies_from_activities(recent_activities)
                
                # Process new threats into alerts
                for threat in new_threats:
                    if threat.threat_id not in self.active_investigations:
                        alert = await self._create_conspiracy_alert(threat)
                        self.pending_alerts[alert.alert_id] = alert
                        await self._notify_alert_callbacks(alert)
                        
                self.last_conspiracy_scan = datetime.now()
                
            except Exception as e:
                print(f"Error in conspiracy monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on error
                
    def _get_recent_suspicious_activities(self) -> List[SuspiciousActivity]:
        """Get recent suspicious activities for monitoring (mock implementation)."""
        # In a real implementation, this would query the game state for recent events
        # For testing, return mock activities
        return [
            SuspiciousActivity(
                activity_type="secret_meeting",
                description="Unscheduled private meeting between military officials",
                participants=["General Marcus Steel", "Unknown Military Contact"],
                location="Private venue outside capital",
                timestamp=datetime.now() - timedelta(hours=2),
                suspicion_level=0.7
            )
        ]
        
    async def _detect_conspiracies_from_activities(self, activities: List[SuspiciousActivity]) -> List[ConspiracyThreat]:
        """Analyze suspicious activities to detect potential conspiracy threats."""
        threats = []
        
        for activity in activities:
            if activity.suspicion_level > 0.6:  # High suspicion threshold
                # Convert to conspiracy threat
                threat_level = ThreatLevel.HIGH if activity.suspicion_level > 0.8 else ThreatLevel.MEDIUM
                
                threat = ConspiracyThreat(
                    threat_id=f"threat_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    conspiracy_type=activity.activity_type,
                    threat_level=threat_level,
                    participants=activity.participants,
                    description=f"Conspiracy suspected based on {activity.description}",
                    evidence_strength=activity.suspicion_level,
                    estimated_timeline="Unknown - requires investigation"
                )
                threats.append(threat)
                
        return threats
        
    async def _create_conspiracy_alert(self, threat: ConspiracyThreat) -> ConspiracyAlert:
        """Create a player-facing alert from a conspiracy threat."""
        alert_id = f"alert_{threat.threat_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Determine urgency and recommended actions based on threat level
        urgency_map = {
            ThreatLevel.LOW: 0.3,
            ThreatLevel.MEDIUM: 0.6,
            ThreatLevel.HIGH: 0.8,
            ThreatLevel.CRITICAL: 1.0
        }
        
        recommended_actions = []
        if threat.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            recommended_actions.extend([
                InvestigationAction.GATHER_INTELLIGENCE,
                InvestigationAction.CONSULT_ADVISORS,
                InvestigationAction.SURVEILLANCE
            ])
        else:
            recommended_actions.extend([
                InvestigationAction.ANALYZE_COMMUNICATIONS,
                InvestigationAction.MONITOR_MOVEMENTS
            ])
            
        # Check if time-sensitive
        time_sensitive = threat.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        expires_at = datetime.now() + timedelta(hours=24) if time_sensitive else None
        
        alert = ConspiracyAlert(
            alert_id=alert_id,
            threat_level=threat.threat_level,
            title=f"Conspiracy Detected: {threat.conspiracy_type}",
            description=f"Suspected conspiracy involving {len(threat.participants)} actors. {threat.description[:100]}...",
            suspected_actors=threat.participants,
            urgency_score=urgency_map[threat.threat_level],
            recommended_actions=recommended_actions,
            time_sensitive=time_sensitive,
            expires_at=expires_at
        )
        
        return alert
        
    async def _notify_alert_callbacks(self, alert: ConspiracyAlert):
        """Notify all registered alert callbacks."""
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                print(f"Error in alert callback: {e}")
                
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Player acknowledges a conspiracy alert."""
        if alert_id in self.pending_alerts:
            self.pending_alerts[alert_id].acknowledged = True
            return True
        return False
        
    async def start_investigation(self, alert_id: str, assigned_advisors: List[str] = None) -> str:
        """Start a formal investigation into a conspiracy alert."""
        if alert_id not in self.pending_alerts:
            raise ValueError(f"Alert {alert_id} not found")
            
        alert = self.pending_alerts[alert_id]
        
        # Create investigation from alert
        investigation = ConspiracyInvestigation(
            threat_id=alert.alert_id,
            conspiracy_threat=None,  # Will be populated from conspiracy detector
            assigned_advisors=assigned_advisors or [],
            status="active"
        )
        
        investigation_id = f"investigation_{len(self.active_investigations) + 1}"
        self.active_investigations[investigation_id] = investigation
        
        # Remove from pending alerts
        del self.pending_alerts[alert_id]
        
        # Notify callbacks
        await self._notify_investigation_callbacks("investigation_started", investigation_id, investigation)
        
        return investigation_id
        
    async def add_investigation_step(self, investigation_id: str, action: InvestigationAction, 
                                   target: str, resources: int = 1) -> InvestigationStep:
        """Add an investigation step to an active investigation."""
        if investigation_id not in self.active_investigations:
            raise ValueError(f"Investigation {investigation_id} not found")
            
        investigation = self.active_investigations[investigation_id]
        
        # Create investigation step
        step = InvestigationStep(
            action_type=action,
            target=target,
            resources_required=resources,
            duration_hours=self._get_action_duration(action),
            risk_level=self._get_action_risk(action)
        )
        
        investigation.investigation_steps.append(step)
        investigation.last_updated = datetime.now()
        
        # Start processing the step
        asyncio.create_task(self._process_investigation_step(investigation_id, len(investigation.investigation_steps) - 1))
        
        return step
        
    def _get_action_duration(self, action: InvestigationAction) -> int:
        """Get typical duration for an investigation action."""
        duration_map = {
            InvestigationAction.GATHER_INTELLIGENCE: 12,
            InvestigationAction.INTERVIEW_SUBJECTS: 8,
            InvestigationAction.ANALYZE_COMMUNICATIONS: 6,
            InvestigationAction.SURVEILLANCE: 24,
            InvestigationAction.CROSS_REFERENCE: 4,
            InvestigationAction.CONSULT_ADVISORS: 2,
            InvestigationAction.DEPLOY_AGENTS: 48,
            InvestigationAction.MONITOR_MOVEMENTS: 72
        }
        return duration_map.get(action, 12)
        
    def _get_action_risk(self, action: InvestigationAction) -> float:
        """Get risk level for an investigation action."""
        risk_map = {
            InvestigationAction.GATHER_INTELLIGENCE: 0.3,
            InvestigationAction.INTERVIEW_SUBJECTS: 0.5,
            InvestigationAction.ANALYZE_COMMUNICATIONS: 0.1,
            InvestigationAction.SURVEILLANCE: 0.4,
            InvestigationAction.CROSS_REFERENCE: 0.1,
            InvestigationAction.CONSULT_ADVISORS: 0.0,
            InvestigationAction.DEPLOY_AGENTS: 0.7,
            InvestigationAction.MONITOR_MOVEMENTS: 0.2
        }
        return risk_map.get(action, 0.3)
        
    async def _process_investigation_step(self, investigation_id: str, step_index: int):
        """Process an investigation step and generate results."""
        investigation = self.active_investigations[investigation_id]
        step = investigation.investigation_steps[step_index]
        
        # Simulate investigation delay (in real game would be actual time)
        await asyncio.sleep(2)  # Shortened for testing
        
        # Generate investigation results based on action type and player skills
        results = await self._generate_investigation_results(step, investigation)
        
        # Update step with results
        step.evidence_gathered = results["evidence"]
        step.confidence_level = results["confidence"]
        step.completed = True
        
        # Update investigation evidence chain
        investigation.evidence_chain.extend(results["evidence"])
        investigation.confidence_score = self._calculate_overall_confidence(investigation)
        investigation.last_updated = datetime.now()
        
        # Notify callbacks
        await self._notify_evidence_callbacks(investigation_id, results["evidence"])
        await self._notify_investigation_callbacks("step_completed", investigation_id, investigation)
        
    async def _generate_investigation_results(self, step: InvestigationStep, 
                                            investigation: ConspiracyInvestigation) -> Dict[str, Any]:
        """Generate realistic investigation results."""
        # Base success chance on player skills and action type
        skill_map = {
            InvestigationAction.GATHER_INTELLIGENCE: "intelligence_gathering",
            InvestigationAction.INTERVIEW_SUBJECTS: "interrogation",
            InvestigationAction.ANALYZE_COMMUNICATIONS: "analysis",
            InvestigationAction.SURVEILLANCE: "surveillance",
            InvestigationAction.CONSULT_ADVISORS: "analysis"
        }
        
        relevant_skill = skill_map.get(step.action_type, "intelligence_gathering")
        skill_level = self.player_investigation_skills[relevant_skill]
        
        # Calculate success probability
        base_success = 0.6
        skill_bonus = skill_level * 0.3
        risk_penalty = step.risk_level * 0.2
        success_chance = base_success + skill_bonus - risk_penalty
        
        # Generate results
        import random
        success = random.random() < success_chance
        
        if success:
            evidence = self._generate_evidence(step.action_type, step.target)
            confidence = min(0.9, skill_level + random.uniform(0.1, 0.3))
        else:
            evidence = ["Investigation inconclusive", "No actionable intelligence gathered"]
            confidence = max(0.1, random.uniform(0.1, 0.4))
            
        return {
            "evidence": evidence,
            "confidence": confidence,
            "success": success
        }
        
    def _generate_evidence(self, action_type: InvestigationAction, target: str) -> List[str]:
        """Generate realistic evidence based on investigation action."""
        evidence_templates = {
            InvestigationAction.GATHER_INTELLIGENCE: [
                f"Intelligence reports unusual activity involving {target}",
                f"Sources confirm {target} has been meeting with unknown contacts",
                f"Financial records show suspicious transactions linked to {target}"
            ],
            InvestigationAction.SURVEILLANCE: [
                f"Surveillance confirms {target} regular meetings at secure location",
                f"Communication patterns suggest coordination with other suspects",
                f"Movement analysis reveals attempts to avoid standard security protocols"
            ],
            InvestigationAction.ANALYZE_COMMUNICATIONS: [
                f"Communication analysis reveals coded language in {target} messages",
                f"Frequency analysis suggests coordinated communication schedule",
                f"Encryption patterns indicate operational security awareness"
            ]
        }
        
        templates = evidence_templates.get(action_type, ["Generic investigation evidence"])
        import random
        return [random.choice(templates)]
        
    def _calculate_overall_confidence(self, investigation: ConspiracyInvestigation) -> float:
        """Calculate overall confidence level for the investigation."""
        if not investigation.investigation_steps:
            return 0.0
            
        completed_steps = [s for s in investigation.investigation_steps if s.completed]
        if not completed_steps:
            return 0.0
            
        avg_confidence = sum(s.confidence_level for s in completed_steps) / len(completed_steps)
        step_bonus = min(0.2, len(completed_steps) * 0.05)  # Bonus for more investigation steps
        
        return min(1.0, avg_confidence + step_bonus)
        
    async def _notify_investigation_callbacks(self, event_type: str, investigation_id: str, 
                                            investigation: ConspiracyInvestigation):
        """Notify investigation update callbacks."""
        for callback in self.investigation_callbacks:
            try:
                await callback(event_type, investigation_id, investigation)
            except Exception as e:
                print(f"Error in investigation callback: {e}")
                
    async def _notify_evidence_callbacks(self, investigation_id: str, evidence: List[str]):
        """Notify evidence discovery callbacks."""
        for callback in self.evidence_callbacks:
            try:
                await callback(investigation_id, evidence)
            except Exception as e:
                print(f"Error in evidence callback: {e}")
                
    async def consult_advisors_on_investigation(self, investigation_id: str, 
                                              specific_question: str = "") -> Dict[str, str]:
        """Get AI advisor input on an investigation."""
        if investigation_id not in self.active_investigations:
            raise ValueError(f"Investigation {investigation_id} not found")
            
        investigation = self.active_investigations[investigation_id]
        
        # Create consultation context
        evidence_summary = "\n".join(investigation.evidence_chain[-5:])  # Last 5 pieces of evidence
        
        consultation_prompt = f"""
Investigation Consultation Request

INVESTIGATION SUMMARY:
- Status: {investigation.status}
- Confidence Level: {investigation.confidence_score:.2f}
- Evidence Gathered: {len(investigation.evidence_chain)} items
- Recent Evidence: {evidence_summary}

SPECIFIC QUESTION: {specific_question or "What should be the next investigation steps?"}

Please provide your professional assessment and recommendations.
"""

        # Get input from relevant advisors
        responses = {}
        
        # Intelligence advisor for analysis
        if "intelligence" in [role.value for role in [advisor.personality.role for advisor in self.advisor_council.advisors.values()]]:
            intelligence_response = await self._get_advisor_input("intelligence", consultation_prompt)
            responses["Intelligence Advisor"] = intelligence_response
            
        # Military advisor for security implications  
        if "military" in [role.value for role in [advisor.personality.role for advisor in self.advisor_council.advisors.values()]]:
            military_response = await self._get_advisor_input("military", consultation_prompt)
            responses["Military Advisor"] = military_response
            
        return responses
        
    async def _get_advisor_input(self, advisor_role: str, prompt: str) -> str:
        """Get input from a specific advisor role."""
        # Mock advisor response for testing
        responses = {
            "intelligence": "Based on the evidence pattern, I recommend expanding surveillance and cross-referencing with historical conspiracy patterns.",
            "military": "This conspiracy poses a significant security risk. Recommend immediate deployment of counter-intelligence measures."
        }
        return responses.get(advisor_role, "No specific guidance available.")
        
    async def propose_response_action(self, investigation_id: str, action: ResponseAction, 
                                    rationale: str = "") -> Dict[str, Any]:
        """Propose a response action based on investigation findings."""
        if investigation_id not in self.active_investigations:
            raise ValueError(f"Investigation {investigation_id} not found")
            
        investigation = self.active_investigations[investigation_id]
        
        # Calculate action feasibility based on evidence confidence
        feasibility = self._calculate_action_feasibility(action, investigation.confidence_score)
        
        # Get advisor opinions on the proposed action
        advisor_opinions = await self._get_advisor_opinions_on_action(action, investigation, rationale)
        
        response_proposal = {
            "action": action.value,
            "feasibility": feasibility,
            "confidence_required": self._get_action_confidence_threshold(action),
            "current_confidence": investigation.confidence_score,
            "advisor_opinions": advisor_opinions,
            "risks": self._get_action_risks(action),
            "potential_outcomes": self._get_action_outcomes(action),
            "recommended": feasibility > 0.6 and investigation.confidence_score > 0.7
        }
        
        return response_proposal
        
    def _calculate_action_feasibility(self, action: ResponseAction, confidence: float) -> float:
        """Calculate feasibility of a response action based on evidence confidence."""
        confidence_requirements = {
            ResponseAction.ARREST_CONSPIRATORS: 0.8,
            ResponseAction.PUBLIC_EXPOSURE: 0.9,
            ResponseAction.INFILTRATE_NETWORK: 0.6,
            ResponseAction.COUNTER_INTELLIGENCE: 0.7,
            ResponseAction.MONITOR_AND_WAIT: 0.3,
            ResponseAction.DIPLOMATIC_PRESSURE: 0.8
        }
        
        required_confidence = confidence_requirements.get(action, 0.7)
        return min(1.0, confidence / required_confidence)
        
    def _get_action_confidence_threshold(self, action: ResponseAction) -> float:
        """Get minimum confidence threshold for an action."""
        thresholds = {
            ResponseAction.ARREST_CONSPIRATORS: 0.8,
            ResponseAction.PUBLIC_EXPOSURE: 0.9,
            ResponseAction.INFILTRATE_NETWORK: 0.6,
            ResponseAction.COUNTER_INTELLIGENCE: 0.7,
            ResponseAction.MONITOR_AND_WAIT: 0.3,
            ResponseAction.DIPLOMATIC_PRESSURE: 0.8
        }
        return thresholds.get(action, 0.7)
        
    async def _get_advisor_opinions_on_action(self, action: ResponseAction, 
                                            investigation: ConspiracyInvestigation, 
                                            rationale: str) -> Dict[str, str]:
        """Get advisor opinions on a proposed response action."""
        # Mock advisor responses for testing
        opinions = {
            "Military Advisor": f"Action {action.value} is tactically sound given current intelligence.",
            "Intelligence Advisor": f"Recommend careful consideration of operational security implications.",
            "Diplomatic Advisor": f"Consider potential diplomatic ramifications of {action.value}."
        }
        return opinions
        
    def _get_action_risks(self, action: ResponseAction) -> List[str]:
        """Get potential risks for a response action."""
        risk_map = {
            ResponseAction.ARREST_CONSPIRATORS: [
                "May alert other conspiracy cells",
                "Requires strong legal justification",
                "Potential for public backlash if evidence is weak"
            ],
            ResponseAction.PUBLIC_EXPOSURE: [
                "Risk of causing panic",
                "May damage government credibility if wrong",
                "Could escalate conspiracy activities"
            ],
            ResponseAction.INFILTRATE_NETWORK: [
                "High risk to undercover operatives",
                "Long-term operation with uncertain outcomes",
                "May be discovered and compromise other operations"
            ]
        }
        return risk_map.get(action, ["General operational risks"])
        
    def _get_action_outcomes(self, action: ResponseAction) -> List[str]:
        """Get potential positive outcomes for a response action."""
        outcome_map = {
            ResponseAction.ARREST_CONSPIRATORS: [
                "Immediate neutralization of threat",
                "Prevents conspiracy execution",
                "Demonstrates government strength"
            ],
            ResponseAction.PUBLIC_EXPOSURE: [
                "Builds public trust through transparency",
                "Prevents future similar conspiracies",
                "Demonstrates effective intelligence capabilities"
            ],
            ResponseAction.INFILTRATE_NETWORK: [
                "Provides long-term intelligence advantage",
                "Potential to uncover larger conspiracy network",
                "Minimal immediate disruption to conspiracy plans"
            ]
        }
        return outcome_map.get(action, ["Addresses conspiracy threat"])
        
    def get_pending_alerts(self) -> List[ConspiracyAlert]:
        """Get all pending conspiracy alerts."""
        return list(self.pending_alerts.values())
        
    def get_active_investigations(self) -> List[ConspiracyInvestigation]:
        """Get all active investigations."""
        return list(self.active_investigations.values())
        
    def get_investigation_status(self, investigation_id: str) -> Optional[ConspiracyInvestigation]:
        """Get status of a specific investigation."""
        return self.active_investigations.get(investigation_id)
        
    async def close_investigation(self, investigation_id: str, resolution: str = "completed") -> bool:
        """Close an active investigation."""
        if investigation_id in self.active_investigations:
            investigation = self.active_investigations[investigation_id]
            investigation.status = resolution
            investigation.last_updated = datetime.now()
            
            # Move to completed investigations
            self.completed_investigations.append(investigation)
            del self.active_investigations[investigation_id]
            
            # Notify callbacks
            await self._notify_investigation_callbacks("investigation_closed", investigation_id, investigation)
            return True
        return False
