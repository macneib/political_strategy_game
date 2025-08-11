"""
Player Decision Impact Tracking System

Tracks player decisions across all game systems, builds reputation and relationships,
and creates adaptive consequences based on player behavior patterns and choices.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics
from collections import defaultdict, Counter

from llm.dialogue import MultiAdvisorDialogue
from llm.advisors import AdvisorCouncil
from llm.llm_providers import LLMManager


class DecisionDomain(Enum):
    """Domains where player decisions can be made."""
    MILITARY = "military"
    ECONOMIC = "economic"
    DIPLOMATIC = "diplomatic"
    DOMESTIC = "domestic"
    INTELLIGENCE = "intelligence"
    CRISIS_MANAGEMENT = "crisis_management"
    COUNCIL_MEETINGS = "council_meetings"
    CONSPIRACY_RESPONSE = "conspiracy_response"
    RESOURCE_ALLOCATION = "resource_allocation"
    POLITICAL_REFORM = "political_reform"


class DecisionType(Enum):
    """Types of decisions that can be tracked."""
    POLICY_ADOPTION = "policy_adoption"
    CRISIS_RESPONSE = "crisis_response"
    ADVISOR_SUPPORT = "advisor_support"
    ADVISOR_CHALLENGE = "advisor_challenge"
    RESOURCE_INVESTMENT = "resource_investment"
    DIPLOMATIC_ACTION = "diplomatic_action"
    MILITARY_DEPLOYMENT = "military_deployment"
    INTELLIGENCE_OPERATION = "intelligence_operation"
    PUBLIC_COMMUNICATION = "public_communication"
    REFORM_INITIATIVE = "reform_initiative"
    CONSPIRACY_INVESTIGATION = "conspiracy_investigation"
    INTERVENTION_COUNCIL = "intervention_council"


class ReputationDimension(Enum):
    """Different dimensions of player reputation."""
    DECISIVENESS = "decisiveness"        # How quickly/confidently decisions are made
    PRAGMATISM = "pragmatism"           # Practical vs idealistic choices
    AGGRESSION = "aggression"           # Military/forceful vs peaceful approaches
    TRANSPARENCY = "transparency"       # Open vs secretive governance
    POPULISM = "populism"              # People-focused vs elite-focused decisions
    INNOVATION = "innovation"          # Traditional vs progressive approaches
    COLLABORATION = "collaboration"    # Consensus-building vs authoritarian
    RISK_TOLERANCE = "risk_tolerance"  # Conservative vs bold decision-making


class ImpactScope(Enum):
    """Scope of decision impacts."""
    IMMEDIATE = "immediate"        # Effects within hours/days
    SHORT_TERM = "short_term"     # Effects within weeks
    MEDIUM_TERM = "medium_term"   # Effects within months
    LONG_TERM = "long_term"       # Effects over years
    PERMANENT = "permanent"       # Lasting structural changes


@dataclass
class DecisionContext:
    """Context information when a decision was made."""
    game_turn: int
    active_crises: List[str]
    advisor_recommendations: Dict[str, str]  # advisor -> recommendation
    available_resources: Dict[str, float]
    public_approval: float
    political_stability: float
    time_pressure: float  # 0.0 to 1.0, how urgent the decision was
    alternatives_considered: int  # Number of options player had


@dataclass
class DecisionOutcome:
    """Outcome and effects of a player decision."""
    success: bool
    immediate_effects: Dict[str, float]  # metric -> change value
    public_reaction: str  # Description of how public reacted
    advisor_reactions: Dict[str, str]    # advisor -> reaction
    unintended_consequences: List[str]   # Unexpected results
    resource_changes: Dict[str, float]   # Resource impacts
    reputation_changes: Dict[ReputationDimension, float]  # Reputation shifts


@dataclass
class PlayerDecision:
    """Represents a tracked player decision with full context and outcomes."""
    decision_id: str
    domain: DecisionDomain
    decision_type: DecisionType
    title: str
    description: str
    chosen_option: str
    
    # Decision context
    context: DecisionContext
    rationale: str  # Player's stated reasoning
    advisor_consultation: bool  # Whether player consulted advisors
    
    # Decision outcomes
    outcome: Optional[DecisionOutcome] = None
    long_term_tracked: bool = False
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: str = ""
    complexity_score: float = 0.5  # 0.0 to 1.0, how complex the decision was


@dataclass
class PlayerReputation:
    """Player's reputation across different dimensions."""
    dimensions: Dict[ReputationDimension, float] = field(default_factory=dict)
    confidence_levels: Dict[ReputationDimension, float] = field(default_factory=dict)  # How certain we are
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Initialize reputation dimensions with neutral values."""
        for dimension in ReputationDimension:
            if dimension not in self.dimensions:
                self.dimensions[dimension] = 0.0  # -1.0 to 1.0 scale
                self.confidence_levels[dimension] = 0.0  # 0.0 to 1.0 scale


@dataclass
class BehaviorPattern:
    """Identified behavior pattern in player decisions."""
    pattern_id: str
    pattern_type: str
    description: str
    confidence: float  # How certain we are about this pattern
    decisions_supporting: List[str]  # Decision IDs that support this pattern
    first_observed: datetime
    last_reinforced: datetime
    strength: float = 0.5  # How strong this pattern is (0.0 to 1.0)


@dataclass
class AdvisorRelationship:
    """Tracks player's relationship with each advisor."""
    advisor_name: str
    trust_level: float = 0.0        # -1.0 to 1.0
    influence_level: float = 0.5    # 0.0 to 1.0, how much player follows their advice
    support_frequency: float = 0.5  # How often player supports this advisor
    challenge_frequency: float = 0.0 # How often player challenges this advisor
    consultation_frequency: float = 0.5  # How often player seeks their input
    last_interaction: Optional[datetime] = None
    relationship_trend: str = "stable"  # "improving", "declining", "stable"


class PlayerDecisionTracker:
    """Comprehensive system for tracking player decisions and building adaptive responses."""
    
    def __init__(self, llm_manager: LLMManager, advisor_council: AdvisorCouncil,
                 dialogue_system: MultiAdvisorDialogue):
        self.llm_manager = llm_manager
        self.advisor_council = advisor_council
        self.dialogue_system = dialogue_system
        
        # Decision tracking
        self.decisions: List[PlayerDecision] = []
        self.decision_lookup: Dict[str, PlayerDecision] = {}
        self.decisions_by_domain: Dict[DecisionDomain, List[str]] = defaultdict(list)
        self.decisions_by_type: Dict[DecisionType, List[str]] = defaultdict(list)
        
        # Player profile
        self.player_reputation: PlayerReputation = PlayerReputation()
        self.behavior_patterns: List[BehaviorPattern] = []
        self.advisor_relationships: Dict[str, AdvisorRelationship] = {}
        
        # Impact tracking
        self.pending_impacts: Dict[str, List[Dict[str, Any]]] = defaultdict(list)  # decision_id -> future impacts
        self.cumulative_effects: Dict[str, float] = defaultdict(float)  # metric -> cumulative change
        
        # Analysis state
        self.last_pattern_analysis: datetime = datetime.now()
        self.last_reputation_update: datetime = datetime.now()
        self.analysis_callbacks: List[Callable] = []
        
        # Configuration
        self.reputation_decay_rate = 0.02  # How much reputation fades over time
        self.pattern_confidence_threshold = 0.7
        self.min_decisions_for_pattern = 3
        
        # Initialize advisor relationships
        self._initialize_advisor_relationships()
        
    def _initialize_advisor_relationships(self):
        """Initialize relationship tracking for all advisors."""
        for advisor_name in self.advisor_council.advisors.keys():
            self.advisor_relationships[advisor_name] = AdvisorRelationship(
                advisor_name=advisor_name
            )
    
    def register_analysis_callback(self, callback: Callable):
        """Register callback for when analysis updates are available."""
        self.analysis_callbacks.append(callback)
        
    async def track_decision(self, decision: PlayerDecision) -> str:
        """Track a new player decision and begin impact monitoring."""
        # Assign decision ID if not provided
        if not decision.decision_id:
            decision.decision_id = f"decision_{len(self.decisions) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store decision
        self.decisions.append(decision)
        self.decision_lookup[decision.decision_id] = decision
        self.decisions_by_domain[decision.domain].append(decision.decision_id)
        self.decisions_by_type[decision.decision_type].append(decision.decision_id)
        
        # Update advisor relationships
        await self._update_advisor_relationships(decision)
        
        # Schedule impact tracking
        await self._schedule_impact_tracking(decision)
        
        # Immediate analysis updates
        await self._update_reputation_from_decision(decision)
        await self._check_for_new_patterns(decision)
        
        # Notify callbacks
        await self._notify_analysis_callbacks("decision_tracked", {
            "decision_id": decision.decision_id,
            "domain": decision.domain.value,
            "type": decision.decision_type.value
        })
        
        return decision.decision_id
        
    async def record_decision_outcome(self, decision_id: str, outcome: DecisionOutcome):
        """Record the outcome of a tracked decision."""
        if decision_id not in self.decision_lookup:
            raise ValueError(f"Decision {decision_id} not found")
            
        decision = self.decision_lookup[decision_id]
        decision.outcome = outcome
        
        # Update cumulative effects
        for metric, change in outcome.immediate_effects.items():
            self.cumulative_effects[metric] += change
            
        # Update reputation based on outcome
        for dimension, change in outcome.reputation_changes.items():
            current = self.player_reputation.dimensions[dimension]
            self.player_reputation.dimensions[dimension] = max(-1.0, min(1.0, current + change))
            # Increase confidence in this dimension
            confidence = self.player_reputation.confidence_levels[dimension]
            self.player_reputation.confidence_levels[dimension] = min(1.0, confidence + 0.1)
            
        # Update advisor relationships based on their reactions
        await self._update_advisor_relationships_from_outcome(decision, outcome)
        
        # Trigger pattern analysis
        await self._analyze_patterns_if_needed()
        
        # Notify callbacks
        await self._notify_analysis_callbacks("outcome_recorded", {
            "decision_id": decision_id,
            "success": outcome.success,
            "effects": len(outcome.immediate_effects)
        })
        
    async def _update_advisor_relationships(self, decision: PlayerDecision):
        """Update advisor relationships based on a decision."""
        context = decision.context
        
        # Track consultation behavior
        if decision.advisor_consultation:
            for advisor_name in self.advisor_relationships.keys():
                relationship = self.advisor_relationships[advisor_name]
                relationship.consultation_frequency = min(1.0, relationship.consultation_frequency + 0.05)
                relationship.last_interaction = decision.timestamp
                
        # Track support/challenge behavior
        if decision.decision_type == DecisionType.ADVISOR_SUPPORT:
            # Extract which advisor was supported (would need to be in decision data)
            target_advisor = self._extract_target_advisor(decision, "support")
            if target_advisor and target_advisor in self.advisor_relationships:
                relationship = self.advisor_relationships[target_advisor]
                relationship.support_frequency = min(1.0, relationship.support_frequency + 0.1)
                relationship.trust_level = min(1.0, relationship.trust_level + 0.05)
                relationship.relationship_trend = "improving"
                
        elif decision.decision_type == DecisionType.ADVISOR_CHALLENGE:
            target_advisor = self._extract_target_advisor(decision, "challenge")
            if target_advisor and target_advisor in self.advisor_relationships:
                relationship = self.advisor_relationships[target_advisor]
                relationship.challenge_frequency = min(1.0, relationship.challenge_frequency + 0.1)
                relationship.trust_level = max(-1.0, relationship.trust_level - 0.05)
                relationship.relationship_trend = "declining"
                
        # Track influence based on following recommendations
        for advisor_name, recommendation in context.advisor_recommendations.items():
            if advisor_name in self.advisor_relationships:
                relationship = self.advisor_relationships[advisor_name]
                # Simple heuristic: if decision aligns with recommendation, increase influence
                alignment_score = self._calculate_decision_alignment(decision, recommendation)
                influence_change = alignment_score * 0.02
                relationship.influence_level = max(0.0, min(1.0, relationship.influence_level + influence_change))
                
    async def _update_advisor_relationships_from_outcome(self, decision: PlayerDecision, outcome: DecisionOutcome):
        """Update advisor relationships based on decision outcomes."""
        for advisor_name, reaction in outcome.advisor_reactions.items():
            if advisor_name in self.advisor_relationships:
                relationship = self.advisor_relationships[advisor_name]
                
                # Analyze reaction sentiment (simplified)
                if "pleased" in reaction.lower() or "good" in reaction.lower():
                    relationship.trust_level = min(1.0, relationship.trust_level + 0.03)
                elif "concerned" in reaction.lower() or "disagree" in reaction.lower():
                    relationship.trust_level = max(-1.0, relationship.trust_level - 0.03)
                    
    def _extract_target_advisor(self, decision: PlayerDecision, action_type: str) -> Optional[str]:
        """Extract which advisor was targeted by a support/challenge action."""
        # This would need to be implemented based on how decision data is structured
        # For now, return a placeholder that could be extracted from decision description
        description_lower = decision.description.lower()
        
        for advisor_name in self.advisor_relationships.keys():
            if advisor_name.lower() in description_lower:
                return advisor_name
                
        return None
        
    def _calculate_decision_alignment(self, decision: PlayerDecision, recommendation: str) -> float:
        """Calculate how well a decision aligns with an advisor's recommendation."""
        # Simplified alignment calculation - in practice this would be more sophisticated
        decision_text = f"{decision.title} {decision.description} {decision.chosen_option}".lower()
        recommendation_lower = recommendation.lower()
        
        # Look for common words/themes
        common_words = ["military", "economic", "diplomatic", "immediate", "careful", "aggressive", "peaceful"]
        alignment_score = 0.0
        
        for word in common_words:
            if word in decision_text and word in recommendation_lower:
                alignment_score += 0.1
                
        return min(1.0, alignment_score)
        
    async def _schedule_impact_tracking(self, decision: PlayerDecision):
        """Schedule future impact tracking for a decision."""
        # Define potential future impacts based on decision type and domain
        future_impacts = []
        
        if decision.domain == DecisionDomain.MILITARY:
            future_impacts.extend([
                {"delay_hours": 24, "impact_type": "military_readiness", "check_function": "check_military_impact"},
                {"delay_hours": 168, "impact_type": "public_opinion", "check_function": "check_public_reaction"}
            ])
        elif decision.domain == DecisionDomain.ECONOMIC:
            future_impacts.extend([
                {"delay_hours": 72, "impact_type": "economic_indicators", "check_function": "check_economic_impact"},
                {"delay_hours": 720, "impact_type": "long_term_growth", "check_function": "check_economic_trends"}
            ])
        elif decision.domain == DecisionDomain.DIPLOMATIC:
            future_impacts.extend([
                {"delay_hours": 48, "impact_type": "international_relations", "check_function": "check_diplomatic_impact"},
                {"delay_hours": 336, "impact_type": "treaty_implications", "check_function": "check_treaty_effects"}
            ])
            
        # Add universal impacts
        future_impacts.extend([
            {"delay_hours": 168, "impact_type": "advisor_trust", "check_function": "check_advisor_trust_evolution"},
            {"delay_hours": 720, "impact_type": "reputation_crystallization", "check_function": "check_reputation_stability"}
        ])
        
        # Schedule these impacts
        for impact in future_impacts:
            impact["decision_id"] = decision.decision_id
            impact["scheduled_time"] = decision.timestamp + timedelta(hours=impact["delay_hours"])
            self.pending_impacts[decision.decision_id].append(impact)
            
    async def _update_reputation_from_decision(self, decision: PlayerDecision):
        """Update player reputation based on a new decision."""
        context = decision.context
        
        # Decisiveness: Quick decisions under pressure increase this
        if context.time_pressure > 0.7:
            current = self.player_reputation.dimensions[ReputationDimension.DECISIVENESS]
            self.player_reputation.dimensions[ReputationDimension.DECISIVENESS] = min(1.0, current + 0.05)
            
        # Collaboration: Consulting advisors increases this
        if decision.advisor_consultation:
            current = self.player_reputation.dimensions[ReputationDimension.COLLABORATION]
            self.player_reputation.dimensions[ReputationDimension.COLLABORATION] = min(1.0, current + 0.03)
            
        # Risk tolerance: High-risk decisions increase this
        complexity_threshold = 0.7
        if decision.complexity_score > complexity_threshold:
            current = self.player_reputation.dimensions[ReputationDimension.RISK_TOLERANCE]
            self.player_reputation.dimensions[ReputationDimension.RISK_TOLERANCE] = min(1.0, current + 0.04)
            
        # Domain-specific reputation updates
        if decision.domain == DecisionDomain.MILITARY:
            if "peaceful" in decision.chosen_option.lower() or "diplomatic" in decision.chosen_option.lower():
                current = self.player_reputation.dimensions[ReputationDimension.AGGRESSION]
                self.player_reputation.dimensions[ReputationDimension.AGGRESSION] = max(-1.0, current - 0.02)
            else:
                current = self.player_reputation.dimensions[ReputationDimension.AGGRESSION]
                self.player_reputation.dimensions[ReputationDimension.AGGRESSION] = min(1.0, current + 0.02)
                
        self.player_reputation.last_updated = datetime.now()
        
    async def _check_for_new_patterns(self, decision: PlayerDecision):
        """Check if new behavioral patterns emerge from this decision."""
        # Only analyze if we have enough decisions
        if len(self.decisions) < self.min_decisions_for_pattern:
            return
            
        # Check for domain preference patterns
        domain_counts = Counter()
        recent_decisions = self.decisions[-10:]  # Look at last 10 decisions
        
        for recent_decision in recent_decisions:
            domain_counts[recent_decision.domain] += 1
            
        # Check if player strongly favors certain domains
        total_recent = len(recent_decisions)
        for domain, count in domain_counts.items():
            preference_ratio = count / total_recent
            
            if preference_ratio > 0.6:  # 60% or more decisions in this domain
                pattern_id = f"domain_preference_{domain.value}"
                
                # Check if this pattern already exists
                existing_pattern = next((p for p in self.behavior_patterns if p.pattern_id == pattern_id), None)
                
                if existing_pattern:
                    existing_pattern.strength = min(1.0, existing_pattern.strength + 0.1)
                    existing_pattern.last_reinforced = datetime.now()
                    existing_pattern.decisions_supporting.append(decision.decision_id)
                else:
                    # Create new pattern
                    new_pattern = BehaviorPattern(
                        pattern_id=pattern_id,
                        pattern_type="domain_preference",
                        description=f"Player shows strong preference for {domain.value} decisions",
                        confidence=preference_ratio,
                        decisions_supporting=[decision.decision_id],
                        first_observed=datetime.now(),
                        last_reinforced=datetime.now(),
                        strength=preference_ratio
                    )
                    self.behavior_patterns.append(new_pattern)
                    
        # Check for advisor consultation patterns
        consultation_decisions = [d for d in recent_decisions if d.advisor_consultation]
        if len(consultation_decisions) / total_recent > 0.8:
            self._update_or_create_pattern(
                "high_consultation",
                "consultation_behavior",
                "Player consistently seeks advisor input before decisions",
                len(consultation_decisions) / total_recent,
                decision.decision_id
            )
        elif len(consultation_decisions) / total_recent < 0.2:
            self._update_or_create_pattern(
                "low_consultation",
                "consultation_behavior", 
                "Player tends to make decisions independently",
                1.0 - (len(consultation_decisions) / total_recent),
                decision.decision_id
            )
            
    def _update_or_create_pattern(self, pattern_id: str, pattern_type: str, description: str, 
                                confidence: float, decision_id: str):
        """Update existing pattern or create new one."""
        existing_pattern = next((p for p in self.behavior_patterns if p.pattern_id == pattern_id), None)
        
        if existing_pattern:
            existing_pattern.confidence = min(1.0, (existing_pattern.confidence + confidence) / 2)
            existing_pattern.strength = min(1.0, existing_pattern.strength + 0.05)
            existing_pattern.last_reinforced = datetime.now()
            existing_pattern.decisions_supporting.append(decision_id)
        else:
            new_pattern = BehaviorPattern(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                description=description,
                confidence=confidence,
                decisions_supporting=[decision_id],
                first_observed=datetime.now(),
                last_reinforced=datetime.now(),
                strength=confidence
            )
            self.behavior_patterns.append(new_pattern)
            
    async def _analyze_patterns_if_needed(self):
        """Perform pattern analysis if enough time has passed."""
        time_since_last = (datetime.now() - self.last_pattern_analysis).total_seconds()
        
        if time_since_last > 3600:  # Analyze every hour
            await self._comprehensive_pattern_analysis()
            self.last_pattern_analysis = datetime.now()
            
    async def _comprehensive_pattern_analysis(self):
        """Perform comprehensive analysis of all decision patterns."""
        if len(self.decisions) < 5:
            return
            
        # Analyze decision timing patterns
        await self._analyze_timing_patterns()
        
        # Analyze risk-taking patterns  
        await self._analyze_risk_patterns()
        
        # Analyze consistency patterns
        await self._analyze_consistency_patterns()
        
        # Clean up weak patterns
        self._clean_weak_patterns()
        
    async def _analyze_timing_patterns(self):
        """Analyze patterns in decision timing and urgency response."""
        urgent_decisions = [d for d in self.decisions if d.context.time_pressure > 0.7]
        total_decisions = len(self.decisions)
        
        if len(urgent_decisions) / total_decisions > 0.6:
            self._update_or_create_pattern(
                "crisis_oriented",
                "timing_preference",
                "Player tends to make more decisions under high pressure",
                len(urgent_decisions) / total_decisions,
                self.decisions[-1].decision_id if self.decisions else ""
            )
            
    async def _analyze_risk_patterns(self):
        """Analyze patterns in risk-taking behavior."""
        high_risk_decisions = [d for d in self.decisions if d.complexity_score > 0.7]
        total_decisions = len(self.decisions)
        
        if len(high_risk_decisions) / total_decisions > 0.5:
            self._update_or_create_pattern(
                "high_risk_taker",
                "risk_behavior",
                "Player frequently chooses complex, high-risk options",
                len(high_risk_decisions) / total_decisions,
                self.decisions[-1].decision_id if self.decisions else ""
            )
            
    async def _analyze_consistency_patterns(self):
        """Analyze consistency in decision-making across similar situations."""
        # Group decisions by similar contexts
        similar_contexts = defaultdict(list)
        
        for decision in self.decisions:
            # Create a simple context key based on domain and urgency
            context_key = f"{decision.domain.value}_{decision.context.time_pressure:.1f}"
            similar_contexts[context_key].append(decision)
            
        # Look for consistent patterns within similar contexts
        for context_key, context_decisions in similar_contexts.items():
            if len(context_decisions) >= 3:
                # Check if player consistently chooses similar types of responses
                decision_types = [d.decision_type for d in context_decisions]
                most_common_type = Counter(decision_types).most_common(1)[0]
                consistency_ratio = most_common_type[1] / len(context_decisions)
                
                if consistency_ratio > 0.7:
                    self._update_or_create_pattern(
                        f"consistent_{context_key}",
                        "consistency",
                        f"Player consistently chooses {most_common_type[0].value} in {context_key} situations",
                        consistency_ratio,
                        context_decisions[-1].decision_id
                    )
                    
    def _clean_weak_patterns(self):
        """Remove patterns with low confidence or strength."""
        self.behavior_patterns = [
            p for p in self.behavior_patterns 
            if p.confidence > 0.3 and p.strength > 0.2
        ]
        
    async def process_pending_impacts(self):
        """Process any pending impact checks that are due."""
        current_time = datetime.now()
        completed_impacts = []
        
        for decision_id, impacts in self.pending_impacts.items():
            for impact in impacts:
                if current_time >= impact["scheduled_time"]:
                    await self._process_impact_check(decision_id, impact)
                    completed_impacts.append((decision_id, impact))
                    
        # Remove completed impacts
        for decision_id, impact in completed_impacts:
            self.pending_impacts[decision_id].remove(impact)
            if not self.pending_impacts[decision_id]:
                del self.pending_impacts[decision_id]
                
    async def _process_impact_check(self, decision_id: str, impact: Dict[str, Any]):
        """Process a specific impact check for a decision."""
        decision = self.decision_lookup[decision_id]
        impact_type = impact["impact_type"]
        
        # Simulate impact assessment (in real implementation, this would check actual game state)
        impact_result = {
            "decision_id": decision_id,
            "impact_type": impact_type,
            "severity": 0.5,  # Would be calculated based on actual effects
            "description": f"{impact_type} effects from {decision.title}",
            "timestamp": datetime.now()
        }
        
        # Store long-term impact
        if not decision.long_term_tracked:
            decision.long_term_tracked = True
            
        # Notify callbacks about long-term impact
        await self._notify_analysis_callbacks("long_term_impact", impact_result)
        
    async def get_player_profile(self) -> Dict[str, Any]:
        """Get comprehensive player profile based on tracked decisions."""
        # Decay reputation over time
        await self._apply_reputation_decay()
        
        profile = {
            "total_decisions": len(self.decisions),
            "decisions_by_domain": {domain.value: len(decisions) for domain, decisions in self.decisions_by_domain.items()},
            "reputation": {dim.value: score for dim, score in self.player_reputation.dimensions.items()},
            "reputation_confidence": {dim.value: conf for dim, conf in self.player_reputation.confidence_levels.items()},
            "behavior_patterns": [
                {
                    "type": pattern.pattern_type,
                    "description": pattern.description,
                    "strength": pattern.strength,
                    "confidence": pattern.confidence
                }
                for pattern in self.behavior_patterns
                if pattern.confidence > self.pattern_confidence_threshold
            ],
            "advisor_relationships": {
                name: {
                    "trust": rel.trust_level,
                    "influence": rel.influence_level,
                    "support_frequency": rel.support_frequency,
                    "consultation_frequency": rel.consultation_frequency,
                    "trend": rel.relationship_trend
                }
                for name, rel in self.advisor_relationships.items()
            },
            "decision_trends": await self._calculate_decision_trends(),
            "cumulative_effects": dict(self.cumulative_effects)
        }
        
        return profile
        
    async def _apply_reputation_decay(self):
        """Apply gradual decay to reputation scores over time."""
        time_since_update = (datetime.now() - self.player_reputation.last_updated).total_seconds() / 86400  # days
        
        if time_since_update > 1.0:  # Apply decay if more than a day has passed
            decay_factor = self.reputation_decay_rate * time_since_update
            
            for dimension in ReputationDimension:
                current_score = self.player_reputation.dimensions[dimension]
                # Decay towards neutral (0.0)
                if current_score > 0:
                    self.player_reputation.dimensions[dimension] = max(0.0, current_score - decay_factor)
                elif current_score < 0:
                    self.player_reputation.dimensions[dimension] = min(0.0, current_score + decay_factor)
                    
                # Also decay confidence
                current_confidence = self.player_reputation.confidence_levels[dimension]
                self.player_reputation.confidence_levels[dimension] = max(0.0, current_confidence - decay_factor * 0.5)
                
            self.player_reputation.last_updated = datetime.now()
            
    async def _calculate_decision_trends(self) -> Dict[str, Any]:
        """Calculate trends in decision-making over time."""
        if len(self.decisions) < 3:
            return {"insufficient_data": True}
            
        recent_decisions = self.decisions[-10:]  # Last 10 decisions
        older_decisions = self.decisions[-20:-10] if len(self.decisions) >= 20 else []
        
        trends = {}
        
        # Consultation trend
        recent_consultation_rate = sum(1 for d in recent_decisions if d.advisor_consultation) / len(recent_decisions)
        if older_decisions:
            older_consultation_rate = sum(1 for d in older_decisions if d.advisor_consultation) / len(older_decisions)
            trends["consultation_trend"] = "increasing" if recent_consultation_rate > older_consultation_rate else "decreasing"
        else:
            trends["consultation_trend"] = "stable"
            
        # Complexity trend
        recent_complexity = statistics.mean([d.complexity_score for d in recent_decisions])
        if older_decisions:
            older_complexity = statistics.mean([d.complexity_score for d in older_decisions])
            trends["complexity_trend"] = "increasing" if recent_complexity > older_complexity else "decreasing"
        else:
            trends["complexity_trend"] = "stable"
            
        # Time pressure trend
        recent_pressure = statistics.mean([d.context.time_pressure for d in recent_decisions])
        if older_decisions:
            older_pressure = statistics.mean([d.context.time_pressure for d in older_decisions])
            trends["urgency_trend"] = "increasing" if recent_pressure > older_pressure else "decreasing"
        else:
            trends["urgency_trend"] = "stable"
            
        return trends
        
    async def get_adaptive_ai_recommendations(self, current_situation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI recommendations adapted to player's behavior patterns."""
        profile = await self.get_player_profile()
        
        recommendations = {
            "advisor_suggestions": [],
            "decision_approach": "",
            "risk_assessment": "",
            "consultation_recommendation": ""
        }
        
        # Adapt recommendations based on player patterns
        high_collaboration = profile["reputation"].get("collaboration", 0.0) > 0.5
        high_risk_tolerance = profile["reputation"].get("risk_tolerance", 0.0) > 0.5
        high_decisiveness = profile["reputation"].get("decisiveness", 0.0) > 0.5
        
        # Advisor suggestions based on relationship strength
        trusted_advisors = [
            name for name, rel in profile["advisor_relationships"].items()
            if rel["trust"] > 0.3 and rel["influence"] > 0.5
        ]
        
        if trusted_advisors:
            recommendations["advisor_suggestions"] = [
                f"Consider consulting {advisor} - they have strong influence with you"
                for advisor in trusted_advisors[:3]
            ]
        
        # Decision approach based on patterns
        if high_collaboration and not high_decisiveness:
            recommendations["decision_approach"] = "Take time to build consensus - your collaborative style is valued"
        elif high_decisiveness and not high_collaboration:
            recommendations["decision_approach"] = "Your decisive leadership is recognized - trust your instincts"
        else:
            recommendations["decision_approach"] = "Balance speed and consultation based on the situation"
            
        # Risk assessment based on tolerance
        if high_risk_tolerance:
            recommendations["risk_assessment"] = "Your bold approach has been noted - consider if this situation calls for your characteristic risk-taking"
        else:
            recommendations["risk_assessment"] = "Your careful approach has served you well - maintain prudent decision-making"
            
        # Consultation recommendation
        consultation_rate = sum(1 for d in self.decisions if d.advisor_consultation) / max(1, len(self.decisions))
        if consultation_rate > 0.7:
            recommendations["consultation_recommendation"] = "You consistently seek input - advisors expect to be consulted"
        elif consultation_rate < 0.3:
            recommendations["consultation_recommendation"] = "You often decide independently - advisors may feel underutilized"
        else:
            recommendations["consultation_recommendation"] = "Your balanced consultation approach is appropriate"
            
        return recommendations
        
    async def _notify_analysis_callbacks(self, update_type: str, data: Dict[str, Any]):
        """Notify all registered analysis callbacks."""
        update_data = {
            "update_type": update_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        for callback in self.analysis_callbacks:
            try:
                await callback(update_data)
            except Exception as e:
                print(f"Error in analysis callback: {e}")
                
    def get_decision_history(self, domain: Optional[DecisionDomain] = None, 
                           limit: Optional[int] = None) -> List[PlayerDecision]:
        """Get decision history, optionally filtered by domain."""
        decisions = self.decisions
        
        if domain:
            decision_ids = self.decisions_by_domain.get(domain, [])
            decisions = [self.decision_lookup[did] for did in decision_ids]
            
        if limit:
            decisions = decisions[-limit:]
            
        return decisions
        
    def get_reputation_summary(self) -> Dict[str, str]:
        """Get human-readable reputation summary."""
        summary = {}
        
        for dimension, score in self.player_reputation.dimensions.items():
            confidence = self.player_reputation.confidence_levels[dimension]
            
            if confidence < 0.3:
                summary[dimension.value] = "Unknown - insufficient data"
            elif score > 0.5:
                summary[dimension.value] = f"High {dimension.value}"
            elif score < -0.5:
                summary[dimension.value] = f"Low {dimension.value}"
            else:
                summary[dimension.value] = f"Moderate {dimension.value}"
                
        return summary
        
    async def export_player_data(self) -> Dict[str, Any]:
        """Export all player data for persistence or analysis."""
        return {
            "decisions": [
                {
                    "id": d.decision_id,
                    "domain": d.domain.value,
                    "type": d.decision_type.value,
                    "title": d.title,
                    "timestamp": d.timestamp.isoformat(),
                    "outcome_success": d.outcome.success if d.outcome else None
                }
                for d in self.decisions
            ],
            "reputation": {
                "dimensions": {k.value: v for k, v in self.player_reputation.dimensions.items()},
                "confidence": {k.value: v for k, v in self.player_reputation.confidence_levels.items()}
            },
            "patterns": [
                {
                    "type": p.pattern_type,
                    "description": p.description,
                    "strength": p.strength,
                    "confidence": p.confidence
                }
                for p in self.behavior_patterns
            ],
            "advisor_relationships": {
                name: {
                    "trust": rel.trust_level,
                    "influence": rel.influence_level,
                    "trend": rel.relationship_trend
                }
                for name, rel in self.advisor_relationships.items()
            }
        }
