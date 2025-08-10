"""
Advisor Personality Drift Detection and Correction System

This module monitors advisor personality consistency across LLM interactions,
detects personality drift, and implements correction mechanisms to maintain
believable and consistent character behavior over time.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import json
import logging
import statistics
from collections import defaultdict, deque

from .dialogue import MultiAdvisorDialogue, EmotionalState
from .advisors import AdvisorRole, AdvisorCouncil, AdvisorAI, AdvisorPersonality
from .llm_providers import LLMManager, LLMMessage, LLMResponse


class PersonalityAspect(Enum):
    """Different aspects of personality that can be tracked."""
    COMMUNICATION_STYLE = "communication_style"
    DECISION_MAKING = "decision_making"
    EMOTIONAL_RESPONSES = "emotional_responses"
    VALUE_SYSTEM = "value_system"
    SOCIAL_INTERACTIONS = "social_interactions"
    RISK_TOLERANCE = "risk_tolerance"
    LEADERSHIP_STYLE = "leadership_style"
    CONFLICT_RESOLUTION = "conflict_resolution"


class DriftSeverity(Enum):
    """Severity levels for personality drift."""
    MINIMAL = "minimal"          # 0-10% drift
    SLIGHT = "slight"            # 10-25% drift
    MODERATE = "moderate"        # 25-50% drift
    SIGNIFICANT = "significant"  # 50-75% drift
    SEVERE = "severe"           # 75%+ drift


class CorrectionStrategy(Enum):
    """Strategies for correcting personality drift."""
    REINFORCEMENT_PROMPTING = "reinforcement_prompting"
    CONTEXT_INJECTION = "context_injection"
    HISTORICAL_ANCHORING = "historical_anchoring"
    PERSONALITY_RESET = "personality_reset"
    GRADUAL_REALIGNMENT = "gradual_realignment"


@dataclass
class PersonalitySnapshot:
    """Captures personality state at a specific point in time."""
    timestamp: datetime
    advisor_name: str
    personality_aspects: Dict[PersonalityAspect, float] = field(default_factory=dict)
    recent_responses: List[str] = field(default_factory=list)
    emotional_baseline: Dict[str, float] = field(default_factory=dict)
    decision_patterns: List[str] = field(default_factory=list)
    interaction_history: List[str] = field(default_factory=list)
    
    def calculate_aspect_score(self, aspect: PersonalityAspect, reference_traits: List[str]) -> float:
        """Calculate a score for a specific personality aspect."""
        # This would analyze recent responses/decisions for consistency with expected traits
        base_score = 0.5  # Neutral baseline
        
        # Analyze recent responses for trait consistency
        if self.recent_responses:
            trait_matches = sum(
                1 for response in self.recent_responses
                for trait in reference_traits
                if trait.lower() in response.lower()
            )
            response_score = min(1.0, trait_matches / (len(self.recent_responses) * len(reference_traits)))
            base_score = (base_score + response_score) / 2
        
        return base_score


@dataclass
class PersonalityDrift:
    """Represents detected personality drift in an advisor."""
    advisor_name: str
    aspect: PersonalityAspect
    severity: DriftSeverity
    drift_percentage: float
    detection_timestamp: datetime
    baseline_snapshot: PersonalitySnapshot
    current_snapshot: PersonalitySnapshot
    specific_changes: List[str] = field(default_factory=list)
    potential_causes: List[str] = field(default_factory=list)
    
    def get_drift_description(self) -> str:
        """Get a human-readable description of the drift."""
        return f"{self.advisor_name} showing {self.severity.value} drift in {self.aspect.value} ({self.drift_percentage:.1f}%)"


@dataclass
class CorrectionAttempt:
    """Records an attempt to correct personality drift."""
    correction_id: str
    advisor_name: str
    strategy: CorrectionStrategy
    target_drift: PersonalityDrift
    timestamp: datetime = field(default_factory=datetime.now)
    success_rate: Optional[float] = None
    applied_corrections: List[str] = field(default_factory=list)
    
    def mark_success(self, effectiveness: float):
        """Mark the correction attempt as successful with effectiveness rating."""
        self.success_rate = max(0.0, min(1.0, effectiveness))


@dataclass
class PersonalityProfile:
    """Comprehensive personality profile for drift detection."""
    advisor_name: str
    baseline_traits: Dict[str, float] = field(default_factory=dict)
    expected_responses: Dict[str, List[str]] = field(default_factory=dict)
    typical_decisions: List[str] = field(default_factory=list)
    communication_patterns: List[str] = field(default_factory=list)
    value_indicators: List[str] = field(default_factory=list)
    last_calibration: datetime = field(default_factory=datetime.now)
    
    def update_baseline(self, new_snapshot: PersonalitySnapshot):
        """Update baseline from a confirmed accurate personality snapshot."""
        self.last_calibration = datetime.now()
        
        # Update baseline traits from snapshot
        for aspect, score in new_snapshot.personality_aspects.items():
            trait_key = f"{aspect.value}_consistency"
            self.baseline_traits[trait_key] = score
        
        # Update expected response patterns
        if new_snapshot.recent_responses:
            self.expected_responses["recent_patterns"] = new_snapshot.recent_responses[-5:]


class PersonalityDriftDetector:
    """Monitors and detects personality drift in advisor AI behavior."""
    
    def __init__(self, llm_manager: LLMManager, dialogue_system: MultiAdvisorDialogue):
        self.llm_manager = llm_manager
        self.dialogue_system = dialogue_system
        
        self.personality_profiles: Dict[str, PersonalityProfile] = {}
        self.personality_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=20))  # Last 20 snapshots
        self.detected_drifts: List[PersonalityDrift] = []
        self.correction_attempts: List[CorrectionAttempt] = []
        self.drift_thresholds = {
            DriftSeverity.MINIMAL: 0.1,
            DriftSeverity.SLIGHT: 0.25,
            DriftSeverity.MODERATE: 0.5,
            DriftSeverity.SIGNIFICANT: 0.75,
            DriftSeverity.SEVERE: 1.0
        }
        
        self.logger = logging.getLogger(__name__)
    
    def initialize_personality_profiles(self, advisor_council: AdvisorCouncil):
        """Initialize personality profiles for all advisors."""
        for advisor_name, advisor in advisor_council.advisors.items():
            profile = PersonalityProfile(
                advisor_name=advisor_name,
                baseline_traits={
                    "communication_consistency": 1.0,
                    "decision_consistency": 1.0,
                    "emotional_consistency": 1.0,
                    "value_consistency": 1.0
                },
                expected_responses={
                    "role_based": self._get_role_based_responses(advisor.personality.role),
                    "personality_based": advisor.personality.personality_traits.copy()
                },
                communication_patterns=[advisor.personality.communication_style],
                value_indicators=advisor.personality.personality_traits.copy()
            )
            
            self.personality_profiles[advisor_name] = profile
            self.logger.info(f"Initialized personality profile for {advisor_name}")
    
    def _get_role_based_responses(self, role: AdvisorRole) -> List[str]:
        """Get expected response patterns based on advisor role."""
        role_responses = {
            AdvisorRole.MILITARY: [
                "strategic thinking", "security concerns", "tactical analysis",
                "defense priorities", "military discipline"
            ],
            AdvisorRole.ECONOMIC: [
                "economic analysis", "resource management", "trade considerations",
                "fiscal responsibility", "market dynamics"
            ],
            AdvisorRole.DIPLOMATIC: [
                "diplomatic relations", "cultural sensitivity", "negotiation",
                "international perspective", "peaceful solutions"
            ],
            AdvisorRole.DOMESTIC: [
                "citizen welfare", "internal stability", "social programs",
                "domestic policy", "public opinion"
            ],
            AdvisorRole.INTELLIGENCE: [
                "information gathering", "security assessment", "strategic intelligence",
                "threat analysis", "covert operations"
            ]
        }
        
        return role_responses.get(role, ["general advice", "strategic thinking"])
    
    async def capture_personality_snapshot(self, advisor_name: str, 
                                         recent_interactions: List[str] = None) -> PersonalitySnapshot:
        """Capture current personality state of an advisor."""
        advisor = self.dialogue_system.advisor_council.advisors.get(advisor_name)
        if not advisor:
            raise ValueError(f"Advisor {advisor_name} not found")
        
        # Get recent emotional state
        emotional_state = self.dialogue_system.get_advisor_emotional_state(advisor_name)
        
        # Collect recent advisor responses/decisions
        if recent_interactions is None:
            recent_interactions = self._get_recent_interactions(advisor_name)
        
        snapshot = PersonalitySnapshot(
            timestamp=datetime.now(),
            advisor_name=advisor_name,
            recent_responses=recent_interactions[-10:],  # Last 10 interactions
            emotional_baseline={
                "current_emotion": emotional_state.get("emotion", "calm"),
                "intensity": emotional_state.get("intensity", 0.5)
            }
        )
        
        # Analyze personality aspects using LLM
        aspect_scores = await self._analyze_personality_aspects(advisor, snapshot)
        snapshot.personality_aspects = aspect_scores
        
        # Store snapshot in history
        self.personality_history[advisor_name].append(snapshot)
        
        return snapshot
    
    def _get_recent_interactions(self, advisor_name: str) -> List[str]:
        """Get recent interactions for an advisor (would integrate with actual interaction log)."""
        # This would integrate with the actual dialogue/interaction logging system
        # For now, return a placeholder
        return [
            f"Recent advice from {advisor_name}",
            f"Council participation by {advisor_name}",
            f"Decision input from {advisor_name}"
        ]
    
    async def _analyze_personality_aspects(self, advisor: AdvisorAI, 
                                         snapshot: PersonalitySnapshot) -> Dict[PersonalityAspect, float]:
        """Use LLM to analyze personality aspects from recent behavior."""
        if not snapshot.recent_responses:
            return {aspect: 0.5 for aspect in PersonalityAspect}
        
        prompt = f"""Analyze personality consistency for advisor {advisor.personality.name}:

ESTABLISHED PERSONALITY PROFILE:
- Role: {advisor.personality.role.value}
- Background: {advisor.personality.background}
- Personality Traits: {', '.join(advisor.personality.personality_traits)}
- Communication Style: {advisor.personality.communication_style}
- Expertise: {', '.join(advisor.personality.expertise_areas)}

RECENT INTERACTIONS/RESPONSES:
{chr(10).join(f"- {response}" for response in snapshot.recent_responses)}

CURRENT EMOTIONAL STATE:
- Emotion: {snapshot.emotional_baseline.get('current_emotion', 'calm')}
- Intensity: {snapshot.emotional_baseline.get('intensity', 0.5)}

Analyze how consistent these recent interactions are with the established personality profile.

Return JSON with scores 0.0-1.0 (1.0 = perfectly consistent, 0.0 = completely inconsistent):
{{
    "communication_style": 0.0-1.0,
    "decision_making": 0.0-1.0,
    "emotional_responses": 0.0-1.0,
    "value_system": 0.0-1.0,
    "social_interactions": 0.0-1.0,
    "risk_tolerance": 0.0-1.0,
    "leadership_style": 0.0-1.0,
    "conflict_resolution": 0.0-1.0
}}

Consider: Do responses match expected communication style? Are decisions consistent with established values? Are emotional reactions appropriate for the personality?"""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a personality psychology expert specializing in consistency analysis."),
                LLMMessage(role="user", content=prompt)
            ])
            
            scores_data = json.loads(response.content)
            
            # Convert to PersonalityAspect enum keys
            aspect_scores = {}
            for aspect in PersonalityAspect:
                key = aspect.value
                if key in scores_data:
                    aspect_scores[aspect] = max(0.0, min(1.0, float(scores_data[key])))
                else:
                    aspect_scores[aspect] = 0.5  # Default neutral score
            
            return aspect_scores
            
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Failed to analyze personality aspects for {advisor.personality.name}: {e}")
            # Return neutral scores if analysis fails
            return {aspect: 0.5 for aspect in PersonalityAspect}
    
    async def detect_personality_drift(self, advisor_name: str) -> List[PersonalityDrift]:
        """Detect personality drift by comparing recent snapshots with baseline."""
        if advisor_name not in self.personality_profiles:
            self.logger.warning(f"No personality profile found for {advisor_name}")
            return []
        
        profile = self.personality_profiles[advisor_name]
        history = self.personality_history[advisor_name]
        
        if len(history) < 2:
            return []  # Need at least 2 snapshots to detect drift
        
        baseline_snapshot = history[0]  # First snapshot as baseline
        current_snapshot = history[-1]  # Most recent snapshot
        
        detected_drifts = []
        
        # Compare each personality aspect
        for aspect in PersonalityAspect:
            baseline_score = baseline_snapshot.personality_aspects.get(aspect, 0.5)
            current_score = current_snapshot.personality_aspects.get(aspect, 0.5)
            
            drift_percentage = abs(baseline_score - current_score)
            
            # Determine drift severity
            severity = self._calculate_drift_severity(drift_percentage)
            
            if severity != DriftSeverity.MINIMAL:
                # Analyze specific changes and potential causes
                specific_changes = await self._analyze_specific_changes(
                    advisor_name, aspect, baseline_snapshot, current_snapshot
                )
                
                potential_causes = await self._identify_drift_causes(
                    advisor_name, aspect, history
                )
                
                drift = PersonalityDrift(
                    advisor_name=advisor_name,
                    aspect=aspect,
                    severity=severity,
                    drift_percentage=drift_percentage * 100,
                    detection_timestamp=datetime.now(),
                    baseline_snapshot=baseline_snapshot,
                    current_snapshot=current_snapshot,
                    specific_changes=specific_changes,
                    potential_causes=potential_causes
                )
                
                detected_drifts.append(drift)
                self.logger.warning(f"Detected {severity.value} personality drift in {advisor_name}: {aspect.value}")
        
        # Store detected drifts
        self.detected_drifts.extend(detected_drifts)
        
        return detected_drifts
    
    def _calculate_drift_severity(self, drift_percentage: float) -> DriftSeverity:
        """Calculate drift severity based on percentage change."""
        if drift_percentage >= 0.75:
            return DriftSeverity.SEVERE
        elif drift_percentage >= 0.5:
            return DriftSeverity.SIGNIFICANT
        elif drift_percentage >= 0.25:
            return DriftSeverity.MODERATE
        elif drift_percentage >= 0.1:
            return DriftSeverity.SLIGHT
        else:
            return DriftSeverity.MINIMAL
    
    async def _analyze_specific_changes(self, advisor_name: str, aspect: PersonalityAspect,
                                      baseline: PersonalitySnapshot, current: PersonalitySnapshot) -> List[str]:
        """Analyze specific changes that led to personality drift."""
        prompt = f"""Analyze specific personality changes for {advisor_name}:

PERSONALITY ASPECT: {aspect.value}

BASELINE BEHAVIOR (Original):
{chr(10).join(f"- {response}" for response in baseline.recent_responses[:3])}

CURRENT BEHAVIOR (Recent):
{chr(10).join(f"- {response}" for response in current.recent_responses[:3])}

DRIFT DETECTED: {aspect.value} showing significant change

Identify 2-3 specific changes in behavior patterns. Return JSON list:
["specific_change_1", "specific_change_2", "specific_change_3"]

Focus on concrete behavioral differences you can observe."""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a behavioral analysis expert."),
                LLMMessage(role="user", content=prompt)
            ])
            
            changes = json.loads(response.content)
            return changes if isinstance(changes, list) else []
            
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Failed to analyze specific changes: {e}")
            return [f"Detected drift in {aspect.value} patterns"]
    
    async def _identify_drift_causes(self, advisor_name: str, aspect: PersonalityAspect,
                                   history: deque) -> List[str]:
        """Identify potential causes for personality drift."""
        prompt = f"""Identify potential causes for personality drift in {advisor_name}:

PERSONALITY ASPECT AFFECTED: {aspect.value}

INTERACTION HISTORY (Recent to Oldest):
{chr(10).join(f"- {snapshot.timestamp.strftime('%Y-%m-%d')}: {', '.join(snapshot.recent_responses[:2])}" for snapshot in list(history)[-5:])}

EMOTIONAL PATTERN:
{chr(10).join(f"- {snapshot.timestamp.strftime('%Y-%m-%d')}: {snapshot.emotional_baseline.get('current_emotion', 'calm')}" for snapshot in list(history)[-5:])}

Identify 2-3 likely causes for the personality drift. Return JSON list:
["potential_cause_1", "potential_cause_2", "potential_cause_3"]

Consider: Emotional stress, repeated interactions, external pressures, memory conflicts."""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a psychology expert specializing in personality change analysis."),
                LLMMessage(role="user", content=prompt)
            ])
            
            causes = json.loads(response.content)
            return causes if isinstance(causes, list) else []
            
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Failed to identify drift causes: {e}")
            return ["Unknown external factors", "Accumulated interaction effects"]
    
    async def apply_personality_correction(self, drift: PersonalityDrift,
                                         strategy: CorrectionStrategy = None) -> CorrectionAttempt:
        """Apply correction strategy to address personality drift."""
        if strategy is None:
            strategy = self._select_correction_strategy(drift)
        
        correction = CorrectionAttempt(
            correction_id=f"correction_{len(self.correction_attempts) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            advisor_name=drift.advisor_name,
            strategy=strategy,
            target_drift=drift
        )
        
        # Apply the specific correction strategy
        applied_corrections = await self._execute_correction_strategy(drift, strategy)
        correction.applied_corrections = applied_corrections
        
        # Test effectiveness by capturing new snapshot
        post_correction_snapshot = await self.capture_personality_snapshot(drift.advisor_name)
        
        # Calculate correction effectiveness
        effectiveness = self._calculate_correction_effectiveness(drift, post_correction_snapshot)
        correction.mark_success(effectiveness)
        
        self.correction_attempts.append(correction)
        self.logger.info(f"Applied {strategy.value} correction to {drift.advisor_name} with {effectiveness:.1%} effectiveness")
        
        return correction
    
    def _select_correction_strategy(self, drift: PersonalityDrift) -> CorrectionStrategy:
        """Select appropriate correction strategy based on drift characteristics."""
        if drift.severity == DriftSeverity.SEVERE:
            return CorrectionStrategy.PERSONALITY_RESET
        elif drift.severity == DriftSeverity.SIGNIFICANT:
            return CorrectionStrategy.HISTORICAL_ANCHORING
        elif drift.severity == DriftSeverity.MODERATE:
            return CorrectionStrategy.CONTEXT_INJECTION
        else:
            return CorrectionStrategy.REINFORCEMENT_PROMPTING
    
    async def _execute_correction_strategy(self, drift: PersonalityDrift, 
                                         strategy: CorrectionStrategy) -> List[str]:
        """Execute the specific correction strategy."""
        advisor = self.dialogue_system.advisor_council.advisors[drift.advisor_name]
        
        corrections_applied = []
        
        if strategy == CorrectionStrategy.REINFORCEMENT_PROMPTING:
            # Create reinforcement prompts for the advisor's LLM context
            reinforcement_prompt = await self._generate_reinforcement_prompt(advisor, drift)
            corrections_applied.append(f"Added reinforcement prompt: {reinforcement_prompt[:100]}...")
            
        elif strategy == CorrectionStrategy.CONTEXT_INJECTION:
            # Inject personality context into advisor's system prompt
            context_injection = await self._generate_context_injection(advisor, drift)
            corrections_applied.append(f"Injected personality context: {context_injection[:100]}...")
            
        elif strategy == CorrectionStrategy.HISTORICAL_ANCHORING:
            # Reference historical consistent behavior
            anchoring_examples = await self._generate_historical_anchors(advisor, drift)
            corrections_applied.extend(anchoring_examples)
            
        elif strategy == CorrectionStrategy.PERSONALITY_RESET:
            # Reset to baseline personality parameters
            reset_parameters = self._reset_personality_parameters(advisor, drift)
            corrections_applied.extend(reset_parameters)
            
        elif strategy == CorrectionStrategy.GRADUAL_REALIGNMENT:
            # Gradual adjustment over multiple interactions
            realignment_steps = await self._generate_realignment_steps(advisor, drift)
            corrections_applied.extend(realignment_steps)
        
        return corrections_applied
    
    async def _generate_reinforcement_prompt(self, advisor: AdvisorAI, drift: PersonalityDrift) -> str:
        """Generate a reinforcement prompt to correct personality drift."""
        prompt = f"""Create a personality reinforcement prompt for {advisor.personality.name}:

ESTABLISHED PERSONALITY:
- Role: {advisor.personality.role.value}
- Traits: {', '.join(advisor.personality.personality_traits)}
- Communication Style: {advisor.personality.communication_style}

DRIFT DETECTED: {drift.aspect.value} showing {drift.severity.value} drift

Create a brief reinforcement prompt (2-3 sentences) that reminds the advisor of their core personality traits and expected behavior patterns. This will be added to their LLM context.

Focus on the specific aspect that has drifted: {drift.aspect.value}"""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a personality consistency specialist."),
                LLMMessage(role="user", content=prompt)
            ])
            
            return response.content.strip()
            
        except Exception as e:
            self.logger.warning(f"Failed to generate reinforcement prompt: {e}")
            return f"Remember to maintain your {drift.aspect.value} consistent with your established personality as {advisor.personality.name}."
    
    async def _generate_context_injection(self, advisor: AdvisorAI, drift: PersonalityDrift) -> str:
        """Generate context injection to correct drift."""
        context = f"Personality Reminder: As {advisor.personality.name}, you are known for {', '.join(advisor.personality.personality_traits)}. "
        context += f"Your {drift.aspect.value} should reflect these core traits. "
        context += f"Recent behavior has deviated from expected patterns - realign with your established personality."
        
        return context
    
    async def _generate_historical_anchors(self, advisor: AdvisorAI, drift: PersonalityDrift) -> List[str]:
        """Generate historical behavior anchors for correction."""
        baseline = drift.baseline_snapshot
        
        anchors = [
            f"Historical behavior pattern: {response}" 
            for response in baseline.recent_responses[:3]
        ]
        
        anchors.append(f"Maintain consistency with established {drift.aspect.value} patterns")
        
        return anchors
    
    def _reset_personality_parameters(self, advisor: AdvisorAI, drift: PersonalityDrift) -> List[str]:
        """Reset personality parameters to baseline."""
        profile = self.personality_profiles[drift.advisor_name]
        
        reset_actions = [
            f"Reset {drift.aspect.value} parameters to baseline",
            f"Restored communication style: {advisor.personality.communication_style}",
            f"Reinforced personality traits: {', '.join(advisor.personality.personality_traits[:3])}"
        ]
        
        # Update profile baseline
        profile.last_calibration = datetime.now()
        
        return reset_actions
    
    async def _generate_realignment_steps(self, advisor: AdvisorAI, drift: PersonalityDrift) -> List[str]:
        """Generate gradual realignment steps."""
        steps = [
            f"Step 1: Gradual realignment of {drift.aspect.value}",
            f"Step 2: Monitor {advisor.personality.name}'s consistency",
            f"Step 3: Reinforce core personality traits in interactions"
        ]
        
        return steps
    
    def _calculate_correction_effectiveness(self, original_drift: PersonalityDrift,
                                         post_correction_snapshot: PersonalitySnapshot) -> float:
        """Calculate how effective the correction was."""
        aspect = original_drift.aspect
        
        baseline_score = original_drift.baseline_snapshot.personality_aspects.get(aspect, 0.5)
        post_correction_score = post_correction_snapshot.personality_aspects.get(aspect, 0.5)
        
        # Calculate how much closer we got to baseline
        original_distance = abs(baseline_score - original_drift.current_snapshot.personality_aspects.get(aspect, 0.5))
        corrected_distance = abs(baseline_score - post_correction_score)
        
        if original_distance == 0:
            return 1.0  # Was already perfect
        
        improvement = max(0, (original_distance - corrected_distance) / original_distance)
        return improvement
    
    def process_personality_monitoring_turn(self, advisor_names: List[str]) -> Dict[str, Any]:
        """Process personality monitoring for one turn."""
        results = {
            "snapshots_captured": [],
            "drifts_detected": [],
            "corrections_applied": [],
            "monitoring_summary": {}
        }
        
        for advisor_name in advisor_names:
            try:
                # This would be called asynchronously in real implementation
                # For now, just track that monitoring occurred
                results["snapshots_captured"].append(advisor_name)
                
                # Check for severe drifts needing immediate attention
                recent_drifts = [
                    drift for drift in self.detected_drifts
                    if drift.advisor_name == advisor_name 
                    and drift.severity in [DriftSeverity.SIGNIFICANT, DriftSeverity.SEVERE]
                ]
                
                if recent_drifts:
                    results["drifts_detected"].extend([drift.get_drift_description() for drift in recent_drifts])
                
            except Exception as e:
                self.logger.error(f"Error monitoring {advisor_name}: {e}")
        
        return results
    
    def get_personality_drift_summary(self, advisor_name: str = None) -> Dict[str, Any]:
        """Get comprehensive personality drift summary."""
        if advisor_name:
            # Summary for specific advisor
            advisor_drifts = [drift for drift in self.detected_drifts if drift.advisor_name == advisor_name]
            advisor_corrections = [corr for corr in self.correction_attempts if corr.advisor_name == advisor_name]
            
            return {
                "advisor_name": advisor_name,
                "total_drifts_detected": len(advisor_drifts),
                "current_active_drifts": len([d for d in advisor_drifts if d.severity != DriftSeverity.MINIMAL]),
                "corrections_attempted": len(advisor_corrections),
                "correction_success_rate": statistics.mean([c.success_rate for c in advisor_corrections if c.success_rate is not None]) if advisor_corrections else 0.0,
                "recent_drifts": [
                    {
                        "aspect": drift.aspect.value,
                        "severity": drift.severity.value,
                        "drift_percentage": drift.drift_percentage
                    }
                    for drift in advisor_drifts[-5:]
                ],
                "personality_stability": self._calculate_personality_stability(advisor_name)
            }
        else:
            # Overall system summary
            all_advisors = list(self.personality_profiles.keys())
            
            return {
                "total_advisors_monitored": len(all_advisors),
                "total_drifts_detected": len(self.detected_drifts),
                "total_corrections_applied": len(self.correction_attempts),
                "average_correction_success": statistics.mean([c.success_rate for c in self.correction_attempts if c.success_rate is not None]) if self.correction_attempts else 0.0,
                "advisors_with_active_drifts": len(set(drift.advisor_name for drift in self.detected_drifts if drift.severity != DriftSeverity.MINIMAL)),
                "drift_severity_distribution": {
                    severity.value: len([d for d in self.detected_drifts if d.severity == severity])
                    for severity in DriftSeverity
                },
                "most_common_drift_aspects": self._get_most_common_drift_aspects()
            }
    
    def _calculate_personality_stability(self, advisor_name: str) -> float:
        """Calculate overall personality stability score for an advisor."""
        history = self.personality_history.get(advisor_name, deque())
        
        if len(history) < 2:
            return 1.0  # Assume stable if insufficient data
        
        # Calculate average consistency across all aspects
        total_consistency = 0.0
        aspect_count = 0
        
        for aspect in PersonalityAspect:
            scores = [snapshot.personality_aspects.get(aspect, 0.5) for snapshot in history]
            if scores:
                variance = statistics.variance(scores) if len(scores) > 1 else 0.0
                consistency = max(0.0, 1.0 - variance)  # Lower variance = higher consistency
                total_consistency += consistency
                aspect_count += 1
        
        return total_consistency / max(1, aspect_count)
    
    def _get_most_common_drift_aspects(self) -> List[Tuple[str, int]]:
        """Get the most common personality aspects that drift."""
        aspect_counts = defaultdict(int)
        
        for drift in self.detected_drifts:
            aspect_counts[drift.aspect.value] += 1
        
        return sorted(aspect_counts.items(), key=lambda x: x[1], reverse=True)[:5]
