"""
Real-time Diplomatic Negotiations Interface

Provides live negotiation interface with multiple parties, real-time dynamics,
player intervention capabilities, and dynamic agreement terms with relationship impact tracking.
"""

import asyncio
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import statistics
from collections import defaultdict, Counter
import json

# Import dependencies
try:
    from llm.dialogue import MultiAdvisorDialogue
    from llm.advisors import AdvisorCouncil
    from llm.llm_providers import LLMManager
except ImportError:
    # Mock classes for testing
    class MultiAdvisorDialogue:
        pass
    class AdvisorCouncil:
        pass
    class LLMManager:
        pass

class NegotiationType(Enum):
    """Types of diplomatic negotiations."""
    TRADE_AGREEMENT = "trade_agreement"
    PEACE_TREATY = "peace_treaty"
    ALLIANCE = "alliance"
    TERRITORIAL_DISPUTE = "territorial_dispute"
    ECONOMIC_PARTNERSHIP = "economic_partnership"
    MILITARY_COOPERATION = "military_cooperation"
    CLIMATE_ACCORD = "climate_accord"
    CULTURAL_EXCHANGE = "cultural_exchange"
    RESOURCE_SHARING = "resource_sharing"
    BORDER_AGREEMENT = "border_agreement"

class NegotiationStage(Enum):
    """Stages of negotiation process."""
    PREPARATION = "preparation"
    OPENING_STATEMENTS = "opening_statements"
    PROPOSAL_EXCHANGE = "proposal_exchange"
    BARGAINING = "bargaining"
    COMPROMISE_SEEKING = "compromise_seeking"
    FINAL_TERMS = "final_terms"
    AGREEMENT_DRAFTING = "agreement_drafting"
    SIGNING = "signing"
    BREAKDOWN = "breakdown"

class NegotiationTactic(Enum):
    """Tactics used during negotiations."""
    COOPERATIVE = "cooperative"
    COMPETITIVE = "competitive"
    ACCOMMODATING = "accommodating"
    AVOIDING = "avoiding"
    COMPROMISING = "compromising"
    PRESSURE = "pressure"
    CHARM_OFFENSIVE = "charm_offensive"
    FAIT_ACCOMPLI = "fait_accompli"
    LINKAGE = "linkage"
    BRINKMANSHIP = "brinkmanship"

class PartyRole(Enum):
    """Roles in negotiation."""
    PRIMARY_NEGOTIATOR = "primary_negotiator"
    SECONDARY_PARTY = "secondary_party"
    MEDIATOR = "mediator"
    OBSERVER = "observer"
    SPOILER = "spoiler"

@dataclass
class NegotiationPosition:
    """Represents a party's position on specific issues."""
    party_id: str
    issue: str
    ideal_outcome: float  # 0.0 to 1.0
    minimum_acceptable: float  # 0.0 to 1.0
    current_offer: float  # 0.0 to 1.0
    flexibility: float  # How much they can move from ideal
    priority: float  # How important this issue is (0.0 to 1.0)
    red_lines: List[str] = field(default_factory=list)  # Non-negotiable points
    concessions_made: List[str] = field(default_factory=list)
    
    def calculate_satisfaction(self, final_outcome: float) -> float:
        """Calculate how satisfied the party is with the outcome."""
        if final_outcome < self.minimum_acceptable:
            return 0.0
        
        if final_outcome >= self.ideal_outcome:
            return 1.0
        
        # Linear interpolation between minimum and ideal
        range_size = self.ideal_outcome - self.minimum_acceptable
        position_in_range = final_outcome - self.minimum_acceptable
        return position_in_range / range_size

@dataclass
class NegotiationParty:
    """Represents a party in negotiations."""
    party_id: str
    name: str
    role: PartyRole
    negotiator_name: str
    power_level: float  # 0.0 to 1.0
    diplomatic_skill: float  # 0.0 to 1.0
    cooperation_tendency: float  # 0.0 to 1.0
    positions: Dict[str, NegotiationPosition] = field(default_factory=dict)
    relationships: Dict[str, float] = field(default_factory=dict)  # With other parties
    trust_levels: Dict[str, float] = field(default_factory=dict)  # Trust in other parties
    preferred_tactics: List[NegotiationTactic] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)  # Domestic/political constraints
    
    # Dynamic state during negotiations
    current_tactic: Optional[NegotiationTactic] = None
    frustration_level: float = 0.0
    satisfaction_level: float = 0.5
    walkaway_threshold: float = 0.2  # Below this satisfaction, they might leave
    momentum: float = 0.5  # Negotiation momentum
    
    def adjust_position(self, issue: str, new_offer: float, justification: str = ""):
        """Adjust position on an issue."""
        if issue in self.positions:
            position = self.positions[issue]
            old_offer = position.current_offer
            position.current_offer = max(
                position.minimum_acceptable,
                min(1.0, new_offer)
            )
            
            # Track concessions
            if abs(new_offer - position.ideal_outcome) > abs(old_offer - position.ideal_outcome):
                position.concessions_made.append(f"Moved from {old_offer:.2f} to {new_offer:.2f}: {justification}")
            
            return True
        return False

@dataclass
class NegotiationEvent:
    """Events that occur during negotiations."""
    timestamp: datetime
    stage: NegotiationStage
    event_type: str
    description: str
    parties_involved: List[str]
    impact_score: float  # -1.0 to 1.0
    consequences: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NegotiationOutcome:
    """Final outcome of negotiations."""
    success: bool
    agreement_reached: bool
    final_terms: Dict[str, float]
    satisfaction_scores: Dict[str, float]  # By party
    relationship_changes: Dict[Tuple[str, str], float]
    duration: timedelta
    breakdown_reason: Optional[str] = None
    implementation_likelihood: float = 0.5
    long_term_stability: float = 0.5

class RealTimeDiplomaticNegotiations:
    """
    Real-time diplomatic negotiations interface with live dynamics,
    player intervention, and adaptive agreement terms.
    """
    
    def __init__(self, llm_manager: LLMManager, advisor_council: AdvisorCouncil, 
                 dialogue_system: MultiAdvisorDialogue):
        self.llm_manager = llm_manager
        self.advisor_council = advisor_council
        self.dialogue_system = dialogue_system
        
        # Active negotiations state
        self.active_negotiations: Dict[str, Dict[str, Any]] = {}
        self.negotiation_history: List[Dict[str, Any]] = []
        
        # Real-time tracking
        self.live_sessions: Dict[str, Dict[str, Any]] = {}
        self.player_interventions: List[Dict[str, Any]] = []
        self.dynamic_adjustments: List[Dict[str, Any]] = []
        
        # Configuration
        self.intervention_cooldown = 30  # Seconds between player interventions
        self.auto_progression_interval = 45  # Seconds between automatic events
        self.maximum_session_duration = 3600  # 1 hour maximum
        
        # Analytics
        self.negotiation_analytics = {
            "total_sessions": 0,
            "success_rate": 0.0,
            "average_duration": 0.0,
            "player_intervention_rate": 0.0,
            "tactic_effectiveness": defaultdict(float)
        }
    
    async def initiate_negotiation(self, negotiation_type: NegotiationType, 
                                   parties: List[NegotiationParty],
                                   issues: Dict[str, Dict[str, Any]],
                                   context: Dict[str, Any] = None) -> str:
        """Start a new diplomatic negotiation session."""
        negotiation_id = f"negotiation_{int(time.time())}_{random.randint(1000, 9999)}"  # nosec B311 - Using random for game mechanics, not security
        session = {
            "id": negotiation_id,
            "type": negotiation_type,
            "parties": {party.party_id: party for party in parties},
            "issues": issues,
            "context": context or {},
            "stage": NegotiationStage.PREPARATION,
            "start_time": datetime.now(),
            "events": [],
            "current_proposals": {},
            "momentum": 0.5,
            "tension_level": 0.3,
            "progress_score": 0.0,
            "player_can_intervene": True,
            "last_intervention": None
        }
        
        # Set up initial positions for all parties
        await self._initialize_party_positions(session, issues)
        
        # Store session
        self.active_negotiations[negotiation_id] = session
        self.live_sessions[negotiation_id] = {
            "last_update": datetime.now(),
            "auto_progression_timer": self.auto_progression_interval,
            "player_interventions_count": 0
        }
        
        # Record initial event
        initial_event = NegotiationEvent(
            timestamp=datetime.now(),
            stage=NegotiationStage.PREPARATION,
            event_type="negotiation_initiated",
            description=f"Diplomatic negotiations for {negotiation_type.value} initiated",
            parties_involved=[party.party_id for party in parties],
            impact_score=0.0
        )
        session["events"].append(initial_event)
        
        # Start automatic progression
        asyncio.create_task(self._auto_progress_negotiation(negotiation_id))
        
        print(f"🤝 Initiated {negotiation_type.value} negotiations: {negotiation_id}")
        return negotiation_id
    
    async def _initialize_party_positions(self, session: Dict[str, Any], 
                                          issues: Dict[str, Dict[str, Any]]):
        """Initialize negotiation positions for all parties."""
        parties = session["parties"]
        
        for issue_name, issue_config in issues.items():
            for party_id, party in parties.items():
                # Generate realistic position based on party characteristics
                ideal = self._calculate_ideal_position(party, issue_name, issue_config)
                minimum = max(0.0, ideal - (party.diplomatic_skill * 0.4))
                flexibility = party.cooperation_tendency * 0.3
                priority = random.uniform(0.3, 1.0)  # nosec B311 - Using random for game mechanics, not security
                
                position = NegotiationPosition(
                    party_id=party_id,
                    issue=issue_name,
                    ideal_outcome=ideal,
                    minimum_acceptable=minimum,
                    current_offer=ideal,  # Start with ideal position
                    flexibility=flexibility,
                    priority=priority,
                    red_lines=issue_config.get("red_lines", [])
                )
                
                party.positions[issue_name] = position
    
    def _calculate_ideal_position(self, party: NegotiationParty, 
                                  issue_name: str, issue_config: Dict[str, Any]) -> float:
        """Calculate a party's ideal position on an issue."""
        # Base position influenced by party characteristics
        base_position = random.uniform(0.3, 0.9)  # nosec B311 - Using random for game mechanics, not security
        power_adjustment = (party.power_level - 0.5) * 0.2
        
        # Adjust based on issue type and party role
        role_adjustment = 0.0
        if party.role == PartyRole.PRIMARY_NEGOTIATOR:
            role_adjustment = 0.1
        elif party.role == PartyRole.MEDIATOR:
            role_adjustment = -0.1  # More moderate positions
        
        ideal = max(0.1, min(0.9, base_position + power_adjustment + role_adjustment))
        return ideal
    
    async def _auto_progress_negotiation(self, negotiation_id: str):
        """Automatically progress negotiation with realistic dynamics."""
        while negotiation_id in self.active_negotiations:
            try:
                session = self.active_negotiations[negotiation_id]
                live_session = self.live_sessions[negotiation_id]
                
                # Check if session should continue
                elapsed = datetime.now() - session["start_time"]
                if elapsed.total_seconds() > self.maximum_session_duration:
                    await self._conclude_negotiation(negotiation_id, "timeout")
                    break
                
                # Wait for progression interval
                await asyncio.sleep(self.auto_progression_interval)
                
                # Check if still active
                if negotiation_id not in self.active_negotiations:
                    break
                
                # Progress the negotiation
                await self._progress_negotiation_stage(negotiation_id)
                
                # Update live session
                live_session["last_update"] = datetime.now()
                
            except Exception as e:
                print(f"Error in auto-progression for {negotiation_id}: {e}")
                break
    
    async def _progress_negotiation_stage(self, negotiation_id: str):
        """Progress negotiation to next logical stage."""
        session = self.active_negotiations[negotiation_id]
        current_stage = session["stage"]
        parties = session["parties"]
        
        # Determine next stage based on current progress
        stage_progression = {
            NegotiationStage.PREPARATION: NegotiationStage.OPENING_STATEMENTS,
            NegotiationStage.OPENING_STATEMENTS: NegotiationStage.PROPOSAL_EXCHANGE,
            NegotiationStage.PROPOSAL_EXCHANGE: NegotiationStage.BARGAINING,
            NegotiationStage.BARGAINING: NegotiationStage.COMPROMISE_SEEKING,
            NegotiationStage.COMPROMISE_SEEKING: NegotiationStage.FINAL_TERMS,
            NegotiationStage.FINAL_TERMS: NegotiationStage.AGREEMENT_DRAFTING,
            NegotiationStage.AGREEMENT_DRAFTING: NegotiationStage.SIGNING
        }
        
        # Generate stage-appropriate events
        await self._generate_stage_events(negotiation_id, current_stage)
        
        # Check for breakdown conditions
        if await self._check_breakdown_conditions(negotiation_id):
            await self._conclude_negotiation(negotiation_id, "breakdown")
            return
        
        # Progress to next stage if appropriate
        if current_stage in stage_progression:
            next_stage = stage_progression[current_stage]
            session["stage"] = next_stage
            
            stage_event = NegotiationEvent(
                timestamp=datetime.now(),
                stage=next_stage,
                event_type="stage_progression",
                description=f"Negotiations progressed to {next_stage.value}",
                parties_involved=list(parties.keys()),
                impact_score=0.1
            )
            session["events"].append(stage_event)
            
            # Update progress score
            session["progress_score"] = min(1.0, session["progress_score"] + 0.15)
            
            print(f"📈 Negotiation {negotiation_id} progressed to: {next_stage.value}")
        elif current_stage == NegotiationStage.SIGNING:
            await self._conclude_negotiation(negotiation_id, "agreement")
    
    async def _generate_stage_events(self, negotiation_id: str, stage: NegotiationStage):
        """Generate realistic events for current negotiation stage."""
        session = self.active_negotiations[negotiation_id]
        parties = session["parties"]
        
        if stage == NegotiationStage.OPENING_STATEMENTS:
            await self._generate_opening_statements(negotiation_id)
        elif stage == NegotiationStage.PROPOSAL_EXCHANGE:
            await self._generate_proposal_exchanges(negotiation_id)
        elif stage == NegotiationStage.BARGAINING:
            await self._generate_bargaining_moves(negotiation_id)
        elif stage == NegotiationStage.COMPROMISE_SEEKING:
            await self._generate_compromise_attempts(negotiation_id)
        elif stage == NegotiationStage.FINAL_TERMS:
            await self._generate_final_negotiations(negotiation_id)
    
    async def _generate_opening_statements(self, negotiation_id: str):
        """Generate opening statements from parties."""
        session = self.active_negotiations[negotiation_id]
        parties = session["parties"]
        
        for party_id, party in parties.items():
            # Generate AI-driven opening statement
            statement_prompt = f"""
            Generate an opening statement for {party.name} ({party.negotiator_name}) 
            in {session['type'].value} negotiations.
            
            Party characteristics:
            - Power level: {party.power_level:.2f}
            - Diplomatic skill: {party.diplomatic_skill:.2f}
            - Cooperation tendency: {party.cooperation_tendency:.2f}
            - Role: {party.role.value}
            
            Keep the statement diplomatic, specific to the negotiation type,
            and reflective of their position strength.
            """
            
            try:
                response = await self.llm_manager.generate(
                    [{"role": "user", "content": statement_prompt}],
                    max_tokens=150,
                    temperature=0.7
                )
                statement = response.content.strip()
            except:
                statement = f"We look forward to productive negotiations that serve our mutual interests."
            
            # Create opening statement event
            opening_event = NegotiationEvent(
                timestamp=datetime.now(),
                stage=NegotiationStage.OPENING_STATEMENTS,
                event_type="opening_statement",
                description=f"{party.negotiator_name}: {statement}",
                parties_involved=[party_id],
                impact_score=0.05
            )
            session["events"].append(opening_event)
    
    async def _generate_proposal_exchanges(self, negotiation_id: str):
        """Generate proposal exchanges between parties."""
        session = self.active_negotiations[negotiation_id]
        parties = session["parties"]
        issues = session["issues"]
        
        # Randomly select a party to make a proposal
        proposing_party_id = random.choice(list(parties.keys()))  # nosec B311 - Using random for game mechanics, not security
        proposing_party = parties[proposing_party_id]
        
        # Select an issue to address
        issue_name = random.choice(list(issues.keys()))  # nosec B311 - Using random for game mechanics, not security
        
        if issue_name in proposing_party.positions:
            position = proposing_party.positions[issue_name]
            
            # Generate a proposal (slightly away from ideal toward compromise)
            proposal_value = position.ideal_outcome * 0.85 + 0.15 * random.uniform(0.3, 0.7)  # nosec B311 - Using random for game mechanics, not security
            proposal_value = max(position.minimum_acceptable, min(1.0, proposal_value))
            
            # Update party's current offer
            proposing_party.adjust_position(
                issue_name, 
                proposal_value,
                f"Initial proposal in {session['stage'].value} stage"
            )
            
            # Create proposal event
            proposal_event = NegotiationEvent(
                timestamp=datetime.now(),
                stage=session["stage"],
                event_type="proposal",
                description=f"{proposing_party.name} proposes {proposal_value:.2f} on {issue_name}",
                parties_involved=[proposing_party_id],
                impact_score=0.1,
                consequences={"issue": issue_name, "proposal": proposal_value}
            )
            session["events"].append(proposal_event)
            
            # Generate responses from other parties
            await self._generate_proposal_responses(negotiation_id, proposing_party_id, issue_name, proposal_value)
    
    async def _generate_proposal_responses(self, negotiation_id: str, proposing_party_id: str,
                                          issue_name: str, proposal_value: float):
        """Generate responses to proposals from other parties."""
        session = self.active_negotiations[negotiation_id]
        parties = session["parties"]
        
        for party_id, party in parties.items():
            if party_id == proposing_party_id:
                continue
            
            if issue_name not in party.positions:
                continue
            
            position = party.positions[issue_name]
            satisfaction = position.calculate_satisfaction(proposal_value)
            
            # Generate response based on satisfaction
            if satisfaction > 0.7:
                response_type = "positive"
                response = f"{party.name} expresses interest in the proposal"
                impact = 0.1
            elif satisfaction > 0.4:
                response_type = "conditional"
                response = f"{party.name} finds the proposal interesting but requests modifications"
                impact = 0.05
            else:
                response_type = "rejection"
                response = f"{party.name} considers the proposal insufficient"
                impact = -0.05
            
            # Update party satisfaction and tension
            party.satisfaction_level = (party.satisfaction_level + satisfaction) / 2
            if satisfaction < 0.3:
                party.frustration_level = min(1.0, party.frustration_level + 0.1)
            
            # Create response event
            response_event = NegotiationEvent(
                timestamp=datetime.now(),
                stage=session["stage"],
                event_type=f"response_{response_type}",
                description=response,
                parties_involved=[party_id],
                impact_score=impact
            )
            session["events"].append(response_event)
    
    async def _generate_bargaining_moves(self, negotiation_id: str):
        """Generate bargaining moves and counter-proposals."""
        session = self.active_negotiations[negotiation_id]
        parties = session["parties"]
        issues = session["issues"]
        
        # Select parties for bilateral bargaining
        party_ids = list(parties.keys())
        if len(party_ids) >= 2:
            bargaining_parties = random.sample(party_ids, 2)  # nosec B311 - Using random for game mechanics, not security
            party_a = parties[bargaining_parties[0]]
            party_b = parties[bargaining_parties[1]]
            
            # Select an issue for bargaining
            common_issues = set(party_a.positions.keys()) & set(party_b.positions.keys())
            if common_issues:
                issue = random.choice(list(common_issues))  # nosec B311 - Using random for game mechanics, not security
                await self._simulate_bilateral_bargaining(negotiation_id, party_a, party_b, issue)
    
    async def _simulate_bilateral_bargaining(self, negotiation_id: str,
                                           party_a: NegotiationParty, party_b: NegotiationParty,
                                           issue: str):
        """Simulate bilateral bargaining between two parties."""
        session = self.active_negotiations[negotiation_id]
        
        position_a = party_a.positions[issue]
        position_b = party_b.positions[issue]
        
        # Calculate potential compromise zone
        min_acceptable = max(position_a.minimum_acceptable, position_b.minimum_acceptable)
        max_acceptable = min(
            position_a.ideal_outcome + position_a.flexibility,
            position_b.ideal_outcome + position_b.flexibility
        )
        
        if min_acceptable <= max_acceptable:
            # Compromise is possible
            compromise_value = (min_acceptable + max_acceptable) / 2
            
            # Both parties adjust toward compromise
            adjustment_a = (compromise_value + position_a.current_offer) / 2
            adjustment_b = (compromise_value + position_b.current_offer) / 2
            
            party_a.adjust_position(issue, adjustment_a, "Bilateral bargaining adjustment")
            party_b.adjust_position(issue, adjustment_b, "Bilateral bargaining adjustment")
            
            # Create bargaining event
            bargaining_event = NegotiationEvent(
                timestamp=datetime.now(),
                stage=session["stage"],
                event_type="bilateral_bargaining",
                description=f"{party_a.name} and {party_b.name} engage in productive bargaining on {issue}",
                parties_involved=[party_a.party_id, party_b.party_id],
                impact_score=0.15,
                consequences={
                    "issue": issue,
                    "party_a_position": adjustment_a,
                    "party_b_position": adjustment_b
                }
            )
            session["events"].append(bargaining_event)
            
            # Increase momentum
            session["momentum"] = min(1.0, session["momentum"] + 0.1)
        else:
            # No compromise zone - tension increases
            party_a.frustration_level = min(1.0, party_a.frustration_level + 0.05)
            party_b.frustration_level = min(1.0, party_b.frustration_level + 0.05)
            session["tension_level"] = min(1.0, session["tension_level"] + 0.1)
            
            deadlock_event = NegotiationEvent(
                timestamp=datetime.now(),
                stage=session["stage"],
                event_type="deadlock",
                description=f"{party_a.name} and {party_b.name} reach deadlock on {issue}",
                parties_involved=[party_a.party_id, party_b.party_id],
                impact_score=-0.1
            )
            session["events"].append(deadlock_event)
    
    async def _generate_compromise_attempts(self, negotiation_id: str):
        """Generate compromise attempts and package deals."""
        session = self.active_negotiations[negotiation_id]
        parties = session["parties"]
        issues = session["issues"]
        
        # Attempt to create package deals
        if len(issues) >= 2:
            issue_names = list(issues.keys())
            package_issues = random.sample(issue_names, min(3, len(issue_names)))  # nosec B311 - Using random for game mechanics, not security
            for party_id, party in parties.items():
                if party.role == PartyRole.MEDIATOR or party.diplomatic_skill > 0.7:
                    # This party attempts to broker a package deal
                    await self._attempt_package_deal(negotiation_id, party, package_issues)
                    break
    
    async def _attempt_package_deal(self, negotiation_id: str, mediating_party: NegotiationParty,
                                   issues: List[str]):
        """Attempt to create a package deal across multiple issues."""
        session = self.active_negotiations[negotiation_id]
        parties = session["parties"]
        
        # Calculate potential package deal
        package_proposal = {}
        total_satisfaction = 0.0
        num_parties = len(parties)
        
        for issue in issues:
            # Find middle ground across all parties
            all_positions = []
            for party in parties.values():
                if issue in party.positions:
                    all_positions.append(party.positions[issue].current_offer)
            
            if all_positions:
                package_proposal[issue] = statistics.mean(all_positions)
        
        # Calculate overall satisfaction for all parties
        for party in parties.values():
            party_satisfaction = 0.0
            for issue, proposed_value in package_proposal.items():
                if issue in party.positions:
                    satisfaction = party.positions[issue].calculate_satisfaction(proposed_value)
                    party_satisfaction += satisfaction * party.positions[issue].priority
            
            total_satisfaction += party_satisfaction / len(package_proposal)
        
        average_satisfaction = total_satisfaction / num_parties
        
        if average_satisfaction > 0.6:
            # Package deal is promising
            package_event = NegotiationEvent(
                timestamp=datetime.now(),
                stage=session["stage"],
                event_type="package_deal_proposal",
                description=f"{mediating_party.name} proposes comprehensive package deal",
                parties_involved=list(parties.keys()),
                impact_score=0.2,
                consequences={
                    "package_proposal": package_proposal,
                    "average_satisfaction": average_satisfaction
                }
            )
            session["events"].append(package_event)
            
            # Update current proposals
            session["current_proposals"]["package_deal"] = package_proposal
            session["momentum"] = min(1.0, session["momentum"] + 0.15)
            
            print(f"📦 Package deal proposed in {negotiation_id}")
        else:
            # Package deal rejected
            rejection_event = NegotiationEvent(
                timestamp=datetime.now(),
                stage=session["stage"],
                event_type="package_deal_rejection",
                description="Package deal proposal receives insufficient support",
                parties_involved=list(parties.keys()),
                impact_score=-0.05
            )
            session["events"].append(rejection_event)
    
    async def _generate_final_negotiations(self, negotiation_id: str):
        """Generate final negotiation push toward agreement."""
        session = self.active_negotiations[negotiation_id]
        parties = session["parties"]
        
        # Each party makes final adjustments toward agreement
        for party in parties.values():
            if party.satisfaction_level > party.walkaway_threshold:
                # Party is motivated to reach agreement
                for issue, position in party.positions.items():
                    # Make final concession if possible
                    if position.flexibility > 0.1:
                        final_offer = position.current_offer + (position.flexibility * 0.5 * random.uniform(-1, 1))  # nosec B311 - Using random for game mechanics, not security
                        final_offer = max(position.minimum_acceptable, min(1.0, final_offer))
                        
                        party.adjust_position(issue, final_offer, "Final negotiation adjustment")
        
        # Generate final push event
        final_event = NegotiationEvent(
            timestamp=datetime.now(),
            stage=session["stage"],
            event_type="final_push",
            description="Parties make final adjustments to reach agreement",
            parties_involved=list(parties.keys()),
            impact_score=0.1
        )
        session["events"].append(final_event)
        
        session["progress_score"] = min(1.0, session["progress_score"] + 0.2)
    
    async def player_intervention(self, negotiation_id: str, intervention_type: str,
                                 target_issue: str = None, target_party: str = None,
                                 intervention_details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Allow player to intervene in ongoing negotiations."""
        if negotiation_id not in self.active_negotiations:
            return {"success": False, "error": "Negotiation not found"}
        
        session = self.active_negotiations[negotiation_id]
        live_session = self.live_sessions[negotiation_id]
        
        # Check intervention cooldown
        last_intervention = session.get("last_intervention")
        if last_intervention:
            time_since_last = (datetime.now() - last_intervention).total_seconds()
            if time_since_last < self.intervention_cooldown:
                return {
                    "success": False, 
                    "error": f"Intervention cooldown: {self.intervention_cooldown - time_since_last:.0f}s remaining"
                }
        
        # Process intervention
        result = await self._process_player_intervention(
            negotiation_id, intervention_type, target_issue, target_party, intervention_details or {}
        )
        
        # Update intervention tracking
        session["last_intervention"] = datetime.now()
        live_session["player_interventions_count"] += 1
        
        intervention_record = {
            "timestamp": datetime.now(),
            "type": intervention_type,
            "target_issue": target_issue,
            "target_party": target_party,
            "details": intervention_details,
            "result": result
        }
        self.player_interventions.append(intervention_record)
        
        print(f"🎯 Player intervention in {negotiation_id}: {intervention_type}")
        return result
    
    async def _process_player_intervention(self, negotiation_id: str, intervention_type: str,
                                          target_issue: str, target_party: str,
                                          details: Dict[str, Any]) -> Dict[str, Any]:
        """Process specific player intervention."""
        session = self.active_negotiations[negotiation_id]
        parties = session["parties"]
        
        if intervention_type == "diplomatic_pressure":
            return await self._apply_diplomatic_pressure(session, target_party, details)
        elif intervention_type == "propose_compromise":
            return await self._propose_player_compromise(session, target_issue, details)
        elif intervention_type == "provide_incentives":
            return await self._provide_negotiation_incentives(session, target_party, details)
        elif intervention_type == "mediate_dispute":
            return await self._mediate_party_dispute(session, details)
        elif intervention_type == "call_recess":
            return await self._call_negotiation_recess(session, details)
        elif intervention_type == "escalate_urgency":
            return await self._escalate_negotiation_urgency(session, details)
        else:
            return {"success": False, "error": f"Unknown intervention type: {intervention_type}"}
    
    async def _apply_diplomatic_pressure(self, session: Dict[str, Any], 
                                        target_party: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Apply diplomatic pressure to a specific party."""
        if target_party not in session["parties"]:
            return {"success": False, "error": "Target party not found"}
        
        party = session["parties"][target_party]
        pressure_type = details.get("pressure_type", "standard")
        pressure_intensity = details.get("intensity", 0.5)
        
        # Effect depends on party's power level and pressure type
        if pressure_type == "economic":
            effect_multiplier = 1.0 / (party.power_level + 0.5)
        elif pressure_type == "public":
            effect_multiplier = 1.0 / (party.diplomatic_skill + 0.5)
        else:
            effect_multiplier = 0.7
        
        total_effect = pressure_intensity * effect_multiplier
        
        # Adjust party's flexibility and cooperation
        for position in party.positions.values():
            position.flexibility = min(1.0, position.flexibility + (total_effect * 0.1))
        
        party.cooperation_tendency = min(1.0, party.cooperation_tendency + (total_effect * 0.05))
        
        # Create pressure event
        pressure_event = NegotiationEvent(
            timestamp=datetime.now(),
            stage=session["stage"],
            event_type="diplomatic_pressure",
            description=f"Diplomatic pressure applied to {party.name} ({pressure_type})",
            parties_involved=[target_party],
            impact_score=total_effect,
            consequences={"pressure_type": pressure_type, "effect": total_effect}
        )
        session["events"].append(pressure_event)
        
        return {
            "success": True,
            "effect": total_effect,
            "description": f"Applied {pressure_type} pressure to {party.name}"
        }
    
    async def _propose_player_compromise(self, session: Dict[str, Any], 
                                        target_issue: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Propose a player-designed compromise solution."""
        if target_issue not in session["issues"]:
            return {"success": False, "error": "Target issue not found"}
        
        proposed_value = details.get("proposed_value", 0.5)
        justification = details.get("justification", "Player-proposed compromise")
        
        # Calculate party reactions to the compromise
        reactions = {}
        total_satisfaction = 0.0
        
        for party_id, party in session["parties"].items():
            if target_issue in party.positions:
                position = party.positions[target_issue]
                satisfaction = position.calculate_satisfaction(proposed_value)
                reactions[party_id] = satisfaction
                total_satisfaction += satisfaction
        
        average_satisfaction = total_satisfaction / len(reactions) if reactions else 0.0
        
        # Create compromise proposal event
        compromise_event = NegotiationEvent(
            timestamp=datetime.now(),
            stage=session["stage"],
            event_type="player_compromise_proposal",
            description=f"Player proposes compromise on {target_issue}: {proposed_value:.2f}",
            parties_involved=list(session["parties"].keys()),
            impact_score=average_satisfaction * 0.2,
            consequences={
                "issue": target_issue,
                "proposed_value": proposed_value,
                "party_reactions": reactions,
                "average_satisfaction": average_satisfaction
            }
        )
        session["events"].append(compromise_event)
        
        # If compromise is well-received, update party positions
        if average_satisfaction > 0.6:
            for party_id, party in session["parties"].items():
                if target_issue in party.positions:
                    party.adjust_position(target_issue, proposed_value, f"Accepted player compromise: {justification}")
            
            session["momentum"] = min(1.0, session["momentum"] + 0.1)
        
        return {
            "success": True,
            "average_satisfaction": average_satisfaction,
            "party_reactions": reactions,
            "accepted": average_satisfaction > 0.6
        }
    
    async def _provide_negotiation_incentives(self, session: Dict[str, Any], 
                                             target_party: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Provide incentives to encourage agreement."""
        if target_party not in session["parties"]:
            return {"success": False, "error": "Target party not found"}
        
        party = session["parties"][target_party]
        incentive_type = details.get("incentive_type", "economic")
        incentive_value = details.get("value", 0.3)
        
        # Apply incentive effects
        if incentive_type == "economic":
            # Economic incentives increase flexibility
            for position in party.positions.values():
                position.flexibility = min(1.0, position.flexibility + incentive_value * 0.15)
        elif incentive_type == "political":
            # Political incentives increase cooperation
            party.cooperation_tendency = min(1.0, party.cooperation_tendency + incentive_value * 0.1)
        elif incentive_type == "security":
            # Security incentives reduce walkaway threshold
            party.walkaway_threshold = max(0.0, party.walkaway_threshold - incentive_value * 0.1)
        
        party.satisfaction_level = min(1.0, party.satisfaction_level + incentive_value * 0.2)
        
        # Create incentive event
        incentive_event = NegotiationEvent(
            timestamp=datetime.now(),
            stage=session["stage"],
            event_type="negotiation_incentives",
            description=f"{incentive_type.title()} incentives provided to {party.name}",
            parties_involved=[target_party],
            impact_score=incentive_value,
            consequences={"incentive_type": incentive_type, "value": incentive_value}
        )
        session["events"].append(incentive_event)
        
        return {
            "success": True,
            "incentive_applied": incentive_type,
            "effect_value": incentive_value,
            "party_satisfaction": party.satisfaction_level
        }
    
    async def _mediate_party_dispute(self, session: Dict[str, Any], 
                                    details: Dict[str, Any]) -> Dict[str, Any]:
        """Mediate disputes between parties."""
        disputing_parties = details.get("parties", list(session["parties"].keys())[:2])
        
        if len(disputing_parties) < 2:
            return {"success": False, "error": "Need at least 2 parties for mediation"}
        
        # Reduce tension between disputing parties
        for party_id in disputing_parties:
            if party_id in session["parties"]:
                party = session["parties"][party_id]
                party.frustration_level = max(0.0, party.frustration_level - 0.15)
                
                # Improve relationships with other parties
                for other_party_id in disputing_parties:
                    if other_party_id != party_id:
                        current_relationship = party.relationships.get(other_party_id, 0.5)
                        party.relationships[other_party_id] = min(1.0, current_relationship + 0.1)
        
        # Reduce overall tension
        session["tension_level"] = max(0.0, session["tension_level"] - 0.2)
        
        # Create mediation event
        mediation_event = NegotiationEvent(
            timestamp=datetime.now(),
            stage=session["stage"],
            event_type="mediation",
            description=f"Player mediates dispute between {', '.join(disputing_parties)}",
            parties_involved=disputing_parties,
            impact_score=0.15
        )
        session["events"].append(mediation_event)
        
        return {
            "success": True,
            "mediated_parties": disputing_parties,
            "tension_reduction": 0.2,
            "new_tension_level": session["tension_level"]
        }
    
    async def _call_negotiation_recess(self, session: Dict[str, Any], 
                                      details: Dict[str, Any]) -> Dict[str, Any]:
        """Call a recess to allow parties to regroup."""
        recess_duration = details.get("duration", 30)  # Minutes
        
        # Recess effects: reduce tension, allow reflection
        session["tension_level"] = max(0.0, session["tension_level"] - 0.1)
        
        for party in session["parties"].values():
            party.frustration_level = max(0.0, party.frustration_level - 0.1)
            
            # Parties may adjust positions during recess
            for position in party.positions.values():
                if random.random() < 0.3:  # nosec B311 - Using random for game mechanics, not security
                    adjustment = random.uniform(-0.05, 0.05)  # nosec B311 - Using random for game mechanics, not security
                    new_offer = max(position.minimum_acceptable, 
                                  min(1.0, position.current_offer + adjustment))
                    party.adjust_position(position.issue, new_offer, "Recess reflection")
        
        # Create recess event
        recess_event = NegotiationEvent(
            timestamp=datetime.now(),
            stage=session["stage"],
            event_type="negotiation_recess",
            description=f"Negotiation recess called for {recess_duration} minutes",
            parties_involved=list(session["parties"].keys()),
            impact_score=0.05
        )
        session["events"].append(recess_event)
        
        return {
            "success": True,
            "recess_duration": recess_duration,
            "tension_reduction": 0.1,
            "position_adjustments": "Parties may have adjusted positions during recess"
        }
    
    async def _escalate_negotiation_urgency(self, session: Dict[str, Any], 
                                           details: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate urgency to push toward resolution."""
        urgency_factor = details.get("urgency_factor", 0.5)
        reason = details.get("reason", "External pressures require swift resolution")
        
        # Urgency effects: increases pressure on all parties
        for party in session["parties"].values():
            # Increase willingness to compromise
            for position in party.positions.values():
                position.flexibility = min(1.0, position.flexibility + urgency_factor * 0.1)
            
            # Slight increase in frustration but also motivation
            party.frustration_level = min(1.0, party.frustration_level + urgency_factor * 0.05)
            
            # Lower walkaway threshold (more willing to accept less ideal outcomes)
            party.walkaway_threshold = max(0.0, party.walkaway_threshold - urgency_factor * 0.1)
        
        # Increase overall momentum
        session["momentum"] = min(1.0, session["momentum"] + urgency_factor * 0.15)
        
        # Create urgency event
        urgency_event = NegotiationEvent(
            timestamp=datetime.now(),
            stage=session["stage"],
            event_type="urgency_escalation",
            description=f"Negotiation urgency escalated: {reason}",
            parties_involved=list(session["parties"].keys()),
            impact_score=urgency_factor * 0.2
        )
        session["events"].append(urgency_event)
        
        return {
            "success": True,
            "urgency_factor": urgency_factor,
            "momentum_increase": urgency_factor * 0.15,
            "reason": reason
        }
    
    async def _check_breakdown_conditions(self, negotiation_id: str) -> bool:
        """Check if negotiations should break down."""
        session = self.active_negotiations[negotiation_id]
        parties = session["parties"]
        
        # Check if any party wants to walk away
        for party in parties.values():
            if party.satisfaction_level < party.walkaway_threshold:
                if party.frustration_level > 0.8:
                    return True
        
        # Check if tension is too high
        if session["tension_level"] > 0.8 and session["momentum"] < 0.2:
            return True
        
        # Check if no progress for too long
        if session["progress_score"] < 0.1 and len(session["events"]) > 10:
            return True
        
        return False
    
    async def _conclude_negotiation(self, negotiation_id: str, conclusion_type: str):
        """Conclude negotiations with final outcome."""
        if negotiation_id not in self.active_negotiations:
            return
        
        session = self.active_negotiations[negotiation_id]
        parties = session["parties"]
        
        # Calculate final outcome
        outcome = await self._calculate_final_outcome(session, conclusion_type)
        
        # Store outcome
        session["outcome"] = outcome
        session["conclusion_type"] = conclusion_type
        session["end_time"] = datetime.now()
        
        # Move to history
        self.negotiation_history.append(session)
        
        # Clean up active sessions
        del self.active_negotiations[negotiation_id]
        if negotiation_id in self.live_sessions:
            del self.live_sessions[negotiation_id]
        
        # Update analytics
        await self._update_negotiation_analytics(session, outcome)
        
        print(f"🏁 Negotiation {negotiation_id} concluded: {conclusion_type}")
        print(f"   Agreement reached: {outcome.agreement_reached}")
        print(f"   Duration: {outcome.duration}")
        
        return outcome
    
    async def _calculate_final_outcome(self, session: Dict[str, Any], 
                                      conclusion_type: str) -> NegotiationOutcome:
        """Calculate the final outcome of negotiations."""
        parties = session["parties"]
        issues = session["issues"]
        
        success = conclusion_type == "agreement"
        agreement_reached = success
        
        # Calculate final terms
        final_terms = {}
        satisfaction_scores = {}
        
        if success:
            # Agreement reached - calculate final terms
            for issue_name in issues.keys():
                # Average all party positions for final term
                positions = []
                for party in parties.values():
                    if issue_name in party.positions:
                        positions.append(party.positions[issue_name].current_offer)
                
                if positions:
                    final_terms[issue_name] = statistics.mean(positions)
        else:
            # No agreement - use status quo or breakdown values
            for issue_name in issues.keys():
                final_terms[issue_name] = 0.0  # No change from status quo
        
        # Calculate satisfaction scores
        for party_id, party in parties.items():
            if success:
                party_satisfaction = 0.0
                total_priority = 0.0
                
                for issue_name, final_value in final_terms.items():
                    if issue_name in party.positions:
                        position = party.positions[issue_name]
                        issue_satisfaction = position.calculate_satisfaction(final_value)
                        party_satisfaction += issue_satisfaction * position.priority
                        total_priority += position.priority
                
                satisfaction_scores[party_id] = party_satisfaction / total_priority if total_priority > 0 else 0.0
            else:
                satisfaction_scores[party_id] = 0.0
        
        # Calculate relationship changes
        relationship_changes = {}
        for party_id_a, party_a in parties.items():
            for party_id_b, party_b in parties.items():
                if party_id_a != party_id_b:
                    # Relationship change based on outcome satisfaction
                    if success:
                        # Successful negotiations generally improve relationships
                        change = (satisfaction_scores[party_id_a] + satisfaction_scores[party_id_b]) * 0.1
                    else:
                        # Failed negotiations may damage relationships
                        change = -0.05
                    
                    relationship_changes[(party_id_a, party_id_b)] = change
        
        # Calculate implementation likelihood and stability
        if success:
            avg_satisfaction = statistics.mean(satisfaction_scores.values())
            implementation_likelihood = min(1.0, avg_satisfaction * 1.2)
            long_term_stability = avg_satisfaction * session["momentum"]
        else:
            implementation_likelihood = 0.0
            long_term_stability = 0.0
        
        # Calculate duration
        duration = datetime.now() - session["start_time"]
        
        # Determine breakdown reason if applicable
        breakdown_reason = None
        if not success:
            if conclusion_type == "timeout":
                breakdown_reason = "Negotiations exceeded maximum duration"
            elif session["tension_level"] > 0.8:
                breakdown_reason = "Irreconcilable differences and high tension"
            elif any(p.satisfaction_level < p.walkaway_threshold for p in parties.values()):
                breakdown_reason = "Party satisfaction below walkaway threshold"
            else:
                breakdown_reason = "Insufficient progress toward agreement"
        
        return NegotiationOutcome(
            success=success,
            agreement_reached=agreement_reached,
            final_terms=final_terms,
            satisfaction_scores=satisfaction_scores,
            relationship_changes=relationship_changes,
            duration=duration,
            breakdown_reason=breakdown_reason,
            implementation_likelihood=implementation_likelihood,
            long_term_stability=long_term_stability
        )
    
    async def _update_negotiation_analytics(self, session: Dict[str, Any], 
                                           outcome: NegotiationOutcome):
        """Update analytics with completed negotiation data."""
        self.negotiation_analytics["total_sessions"] += 1
        
        # Update success rate
        if outcome.success:
            current_successes = self.negotiation_analytics["success_rate"] * (self.negotiation_analytics["total_sessions"] - 1)
            self.negotiation_analytics["success_rate"] = (current_successes + 1) / self.negotiation_analytics["total_sessions"]
        else:
            current_successes = self.negotiation_analytics["success_rate"] * (self.negotiation_analytics["total_sessions"] - 1)
            self.negotiation_analytics["success_rate"] = current_successes / self.negotiation_analytics["total_sessions"]
        
        # Update average duration
        current_avg_duration = self.negotiation_analytics["average_duration"] * (self.negotiation_analytics["total_sessions"] - 1)
        self.negotiation_analytics["average_duration"] = (current_avg_duration + outcome.duration.total_seconds()) / self.negotiation_analytics["total_sessions"]
        
        # Update player intervention rate
        live_session = self.live_sessions.get(session["id"], {})
        interventions_count = live_session.get("player_interventions_count", 0)
        if interventions_count > 0:
            current_intervention_sessions = self.negotiation_analytics["player_intervention_rate"] * (self.negotiation_analytics["total_sessions"] - 1)
            self.negotiation_analytics["player_intervention_rate"] = (current_intervention_sessions + 1) / self.negotiation_analytics["total_sessions"]
    
    def get_active_negotiations(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all active negotiations."""
        active_info = {}
        
        for negotiation_id, session in self.active_negotiations.items():
            live_session = self.live_sessions.get(negotiation_id, {})
            
            active_info[negotiation_id] = {
                "type": session["type"].value,
                "stage": session["stage"].value,
                "parties": [party.name for party in session["parties"].values()],
                "progress_score": session["progress_score"],
                "momentum": session["momentum"],
                "tension_level": session["tension_level"],
                "duration": (datetime.now() - session["start_time"]).total_seconds(),
                "events_count": len(session["events"]),
                "player_interventions": live_session.get("player_interventions_count", 0),
                "can_intervene": session.get("player_can_intervene", True)
            }
        
        return active_info
    
    def get_negotiation_status(self, negotiation_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a specific negotiation."""
        if negotiation_id not in self.active_negotiations:
            return None
        
        session = self.active_negotiations[negotiation_id]
        live_session = self.live_sessions.get(negotiation_id, {})
        parties = session["parties"]
        
        # Calculate current satisfaction levels
        party_status = {}
        for party_id, party in parties.items():
            party_status[party_id] = {
                "name": party.name,
                "role": party.role.value,
                "satisfaction_level": party.satisfaction_level,
                "frustration_level": party.frustration_level,
                "walkaway_threshold": party.walkaway_threshold,
                "current_tactic": party.current_tactic.value if party.current_tactic else None,
                "positions": {
                    issue: {
                        "current_offer": pos.current_offer,
                        "ideal_outcome": pos.ideal_outcome,
                        "minimum_acceptable": pos.minimum_acceptable,
                        "flexibility": pos.flexibility,
                        "priority": pos.priority
                    }
                    for issue, pos in party.positions.items()
                }
            }
        
        # Get recent events
        recent_events = session["events"][-5:] if session["events"] else []
        
        return {
            "negotiation_id": negotiation_id,
            "type": session["type"].value,
            "stage": session["stage"].value,
            "progress_score": session["progress_score"],
            "momentum": session["momentum"],
            "tension_level": session["tension_level"],
            "duration": (datetime.now() - session["start_time"]).total_seconds(),
            "party_status": party_status,
            "recent_events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "type": event.event_type,
                    "description": event.description,
                    "impact_score": event.impact_score
                }
                for event in recent_events
            ],
            "current_proposals": session.get("current_proposals", {}),
            "player_interventions": live_session.get("player_interventions_count", 0),
            "can_intervene": session.get("player_can_intervene", True),
            "intervention_cooldown_remaining": max(0, self.intervention_cooldown - (
                (datetime.now() - session.get("last_intervention", datetime.now() - timedelta(seconds=self.intervention_cooldown))).total_seconds()
            )) if session.get("last_intervention") else 0
        }
    
    def get_negotiation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get history of completed negotiations."""
        recent_history = self.negotiation_history[-limit:] if self.negotiation_history else []
        
        return [
            {
                "negotiation_id": session["id"],
                "type": session["type"].value,
                "conclusion_type": session["conclusion_type"],
                "duration": session["outcome"].duration.total_seconds(),
                "success": session["outcome"].success,
                "agreement_reached": session["outcome"].agreement_reached,
                "average_satisfaction": statistics.mean(session["outcome"].satisfaction_scores.values()) if session["outcome"].satisfaction_scores else 0.0,
                "parties": [party.name for party in session["parties"].values()],
                "final_terms": session["outcome"].final_terms
            }
            for session in reversed(recent_history)
        ]
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary."""
        return {
            "total_negotiations": self.negotiation_analytics["total_sessions"],
            "success_rate": self.negotiation_analytics["success_rate"],
            "average_duration_minutes": self.negotiation_analytics["average_duration"] / 60,
            "player_intervention_rate": self.negotiation_analytics["player_intervention_rate"],
            "active_negotiations": len(self.active_negotiations),
            "total_player_interventions": len(self.player_interventions),
            "intervention_types": Counter(intervention["type"] for intervention in self.player_interventions),
            "tactic_effectiveness": dict(self.negotiation_analytics["tactic_effectiveness"])
        }
    
    async def export_negotiation_data(self, negotiation_id: str = None) -> Dict[str, Any]:
        """Export comprehensive negotiation data."""
        if negotiation_id:
            # Export specific negotiation
            if negotiation_id in self.active_negotiations:
                session = self.active_negotiations[negotiation_id]
                return self._serialize_negotiation_session(session)
            else:
                # Check history
                for session in self.negotiation_history:
                    if session["id"] == negotiation_id:
                        return self._serialize_negotiation_session(session)
                return {"error": "Negotiation not found"}
        else:
            # Export all data
            return {
                "active_negotiations": [
                    self._serialize_negotiation_session(session)
                    for session in self.active_negotiations.values()
                ],
                "negotiation_history": [
                    self._serialize_negotiation_session(session)
                    for session in self.negotiation_history
                ],
                "player_interventions": self.player_interventions,
                "analytics": self.get_analytics_summary(),
                "export_timestamp": datetime.now().isoformat()
            }
    
    def _serialize_negotiation_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize negotiation session for export."""
        return {
            "id": session["id"],
            "type": session["type"].value,
            "stage": session["stage"].value,
            "start_time": session["start_time"].isoformat(),
            "end_time": session.get("end_time", datetime.now()).isoformat() if session.get("end_time") else None,
            "parties": [
                {
                    "party_id": party.party_id,
                    "name": party.name,
                    "role": party.role.value,
                    "negotiator_name": party.negotiator_name,
                    "final_satisfaction": party.satisfaction_level,
                    "final_frustration": party.frustration_level,
                    "positions": {
                        issue: {
                            "ideal_outcome": pos.ideal_outcome,
                            "minimum_acceptable": pos.minimum_acceptable,
                            "final_offer": pos.current_offer,
                            "concessions_made": pos.concessions_made
                        }
                        for issue, pos in party.positions.items()
                    }
                }
                for party in session["parties"].values()
            ],
            "events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "stage": event.stage.value,
                    "type": event.event_type,
                    "description": event.description,
                    "parties_involved": event.parties_involved,
                    "impact_score": event.impact_score,
                    "consequences": event.consequences
                }
                for event in session["events"]
            ],
            "outcome": {
                "success": session["outcome"].success,
                "agreement_reached": session["outcome"].agreement_reached,
                "final_terms": session["outcome"].final_terms,
                "satisfaction_scores": session["outcome"].satisfaction_scores,
                "duration_seconds": session["outcome"].duration.total_seconds(),
                "breakdown_reason": session["outcome"].breakdown_reason,
                "implementation_likelihood": session["outcome"].implementation_likelihood,
                "long_term_stability": session["outcome"].long_term_stability
            } if "outcome" in session else None,
            "metrics": {
                "progress_score": session["progress_score"],
                "momentum": session["momentum"],
                "tension_level": session["tension_level"],
                "events_count": len(session["events"])
            }
        }
