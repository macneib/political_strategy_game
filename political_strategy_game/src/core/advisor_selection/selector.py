"""
Advisor Candidate Selector

Main selector class that coordinates all MCDA algorithms for advisor selection.
This is the primary interface for the advisor selection system.
"""

from typing import List, Dict, Optional

from .criteria import (
    SelectionCriterion, SelectionMethod, SelectionContext, SelectionCriteria,
    CandidateScore, SelectionHistory, get_default_role_criteria, get_default_context_weights
)
from .algorithms import MCDAAlgorithms
from ..agent_pool import Agent
from ..advisor import AdvisorRole


class AdvisorCandidateSelector:
    """
    Advanced Multi-Criteria Decision Analysis (MCDA) system for advisor candidate selection.
    
    Implements sophisticated algorithms including AHP, Fuzzy AHP, and TOPSIS for 
    comprehensive advisor evaluation and selection based on extensive research on
    MCDA methodologies for recommendation systems.
    """
    
    def __init__(self):
        # Core selection configuration
        self.default_method: SelectionMethod = SelectionMethod.FUZZY_AHP
        self.selection_history: List[SelectionHistory] = []
        self.bias_prevention_active: bool = True
        self.diversity_enforcement: bool = True
        
        # Criteria configuration
        self.role_specific_criteria: Dict[AdvisorRole, List[SelectionCriteria]] = {}
        self.context_specific_weights: Dict[SelectionContext, Dict[SelectionCriterion, float]] = {}
        
        # Performance tracking
        self.selection_accuracy: Dict[str, float] = {}
        self.method_performance: Dict[SelectionMethod, List[float]] = {}
        
        # Algorithm engine
        self._algorithms: MCDAAlgorithms = MCDAAlgorithms()
        
        # Initialize default configurations
        self._initialize_default_criteria()
        self._initialize_context_weights()
    
    def _initialize_default_criteria(self) -> None:
        """Initialize default selection criteria for each advisor role."""
        # Initialize criteria for all advisor roles
        for role in AdvisorRole:
            self.role_specific_criteria[role] = get_default_role_criteria(role)
    
    def _initialize_context_weights(self) -> None:
        """Initialize context-specific weight adjustments."""
        self.context_specific_weights = get_default_context_weights()
    
    def select_candidates(
        self,
        candidates: List[Agent],
        role: AdvisorRole,
        context: SelectionContext = SelectionContext.NORMAL_SUCCESSION,
        method: Optional[SelectionMethod] = None,
        num_candidates: int = 3,
        custom_criteria: Optional[List[SelectionCriteria]] = None
    ) -> List[CandidateScore]:
        """
        Select top advisor candidates using sophisticated MCDA algorithms.
        
        Args:
            candidates: List of potential candidate agents
            role: Advisor role to fill
            context: Selection context affecting criteria weights
            method: Selection method to use (defaults to FUZZY_AHP)
            num_candidates: Number of top candidates to return
            custom_criteria: Custom criteria to override defaults
            
        Returns:
            List of CandidateScore objects ranked by suitability
        """
        if not candidates:
            return []
        
        selection_method = method or self.default_method
        criteria = custom_criteria or self.role_specific_criteria.get(role, [])
        
        # Apply context-specific weight adjustments
        adjusted_criteria = self._apply_context_adjustments(criteria, context)
        
        # Filter candidates based on minimum thresholds
        qualified_candidates = self._filter_candidates(candidates, adjusted_criteria)
        
        if not qualified_candidates:
            return []
        
        # Calculate scores using selected method
        candidate_scores = self._calculate_candidate_scores(
            qualified_candidates, adjusted_criteria, selection_method, role, context
        )
        
        # Apply diversity enforcement if enabled
        if self.diversity_enforcement:
            candidate_scores = self._apply_diversity_adjustments(candidate_scores, candidates)
        
        # Sort and return top candidates
        candidate_scores.sort(key=lambda x: x.overall_score, reverse=True)
        
        # Assign ranks
        for i, score in enumerate(candidate_scores[:num_candidates]):
            score.rank_position = i + 1
        
        # Record selection history
        if candidate_scores:
            self._record_selection_decision(
                context, role, candidate_scores[0], selection_method, adjusted_criteria
            )
        
        return candidate_scores[:num_candidates]
    
    def _apply_context_adjustments(
        self, 
        criteria: List[SelectionCriteria], 
        context: SelectionContext
    ) -> List[SelectionCriteria]:
        """Apply context-specific weight adjustments to criteria."""
        adjusted_criteria = []
        context_weights = self.context_specific_weights.get(context, {})
        
        for criterion in criteria:
            adjusted_criterion = SelectionCriteria(
                criterion=criterion.criterion,
                weight=criterion.weight * context_weights.get(criterion.criterion, 1.0),
                threshold=criterion.threshold,
                preference_direction=criterion.preference_direction,
                fuzzy_tolerance=criterion.fuzzy_tolerance,
                context_multiplier=criterion.context_multiplier
            )
            adjusted_criteria.append(adjusted_criterion)
        
        # Normalize weights to sum to 1.0
        total_weight = sum(c.weight for c in adjusted_criteria)
        if total_weight > 0:
            for criterion in adjusted_criteria:
                criterion.weight /= total_weight
        
        return adjusted_criteria
    
    def _filter_candidates(
        self, 
        candidates: List[Agent], 
        criteria: List[SelectionCriteria]
    ) -> List[Agent]:
        """Filter candidates based on minimum threshold requirements."""
        qualified_candidates = []
        
        for candidate in candidates:
            meets_all_thresholds = True
            
            for criterion in criteria:
                candidate_value = self._get_candidate_criterion_value(candidate, criterion.criterion)
                if candidate_value < criterion.threshold:
                    meets_all_thresholds = False
                    break
            
            if meets_all_thresholds:
                qualified_candidates.append(candidate)
        
        return qualified_candidates
    
    def _get_candidate_criterion_value(self, candidate: Agent, criterion: SelectionCriterion) -> float:
        """Extract criterion value from candidate agent."""
        # Map selection criteria to agent attributes and metrics
        if criterion == SelectionCriterion.COMPETENCE:
            return candidate.performance_metrics.leadership_emergence_score if candidate.performance_metrics else 0.5
        elif criterion == SelectionCriterion.INTEGRITY:
            return candidate.personality_profile.core_traits.get('integrity', 0.5) if candidate.personality_profile else 0.5
        elif criterion == SelectionCriterion.LEADERSHIP:
            return candidate.personality_profile.core_traits.get('leadership', 0.5) if candidate.personality_profile else 0.5
        elif criterion == SelectionCriterion.CHARISMA:
            return candidate.personality_profile.core_traits.get('charisma', 0.5) if candidate.personality_profile else 0.5
        elif criterion == SelectionCriterion.WISDOM:
            return candidate.personality_profile.core_traits.get('wisdom', 0.5) if candidate.personality_profile else 0.5
        elif criterion == SelectionCriterion.INNOVATION:
            return candidate.personality_profile.core_traits.get('creativity', 0.5) if candidate.personality_profile else 0.5
        elif criterion == SelectionCriterion.RELIABILITY:
            return candidate.personality_profile.core_traits.get('reliability', 0.5) if candidate.personality_profile else 0.5
        elif criterion == SelectionCriterion.LOYALTY:
            return candidate.personality_profile.core_traits.get('loyalty', 0.5) if candidate.personality_profile else 0.5
        elif criterion == SelectionCriterion.PRAGMATISM:
            return 1.0 - candidate.personality_profile.core_traits.get('idealism', 0.5) if candidate.personality_profile else 0.5
        elif criterion == SelectionCriterion.VISION:
            return candidate.personality_profile.core_traits.get('vision', 0.5) if candidate.personality_profile else 0.5
        elif criterion == SelectionCriterion.EXPERIENCE:
            return min(1.0, candidate.age / 60.0) if hasattr(candidate, 'age') else 0.5
        elif criterion == SelectionCriterion.NETWORK_INFLUENCE:
            return candidate.social_network.social_influence_score if hasattr(candidate, 'social_network') else 0.5
        elif criterion == SelectionCriterion.ADAPTABILITY:
            return candidate.personality_profile.core_traits.get('adaptability', 0.5) if candidate.personality_profile else 0.5
        elif criterion == SelectionCriterion.CRISIS_MANAGEMENT:
            return candidate.personality_profile.core_traits.get('crisis_management', 0.5) if candidate.personality_profile else 0.5
        elif criterion == SelectionCriterion.STRATEGIC_THINKING:
            return candidate.personality_profile.core_traits.get('strategic_thinking', 0.5) if candidate.personality_profile else 0.5
        else:
            return 0.5  # Default value for unknown criteria
    
    def _calculate_candidate_scores(
        self,
        candidates: List[Agent],
        criteria: List[SelectionCriteria],
        method: SelectionMethod,
        role: AdvisorRole,
        context: SelectionContext
    ) -> List[CandidateScore]:
        """Calculate comprehensive scores for candidates using specified method."""
        
        if method == SelectionMethod.FUZZY_AHP:
            return self._algorithms.calculate_fuzzy_ahp_scores(
                candidates, criteria, role, context, self._get_candidate_criterion_value
            )
        elif method == SelectionMethod.AHP:
            return self._algorithms.calculate_ahp_scores(
                candidates, criteria, role, context, self._get_candidate_criterion_value
            )
        elif method == SelectionMethod.TOPSIS:
            return self._algorithms.calculate_topsis_scores(
                candidates, criteria, role, context, self._get_candidate_criterion_value
            )
        elif method == SelectionMethod.HYBRID_AHP_TOPSIS:
            return self._algorithms.calculate_hybrid_scores(
                candidates, criteria, role, context, self._get_candidate_criterion_value
            )
        elif method == SelectionMethod.WEIGHTED_SUM:
            return self._algorithms.calculate_weighted_sum_scores(
                candidates, criteria, role, context, self._get_candidate_criterion_value
            )
        else:
            # Default to Fuzzy AHP as recommended by research
            return self._algorithms.calculate_fuzzy_ahp_scores(
                candidates, criteria, role, context, self._get_candidate_criterion_value
            )
    
    def _apply_diversity_adjustments(
        self, 
        candidate_scores: List[CandidateScore], 
        all_candidates: List[Agent]
    ) -> List[CandidateScore]:
        """Apply diversity enforcement to promote balanced selection."""
        if not self.diversity_enforcement or len(candidate_scores) <= 1:
            return candidate_scores
        
        # Analyze diversity dimensions
        diversity_factors = self._analyze_diversity_factors(all_candidates)
        
        # Apply small adjustments to promote diversity
        for score in candidate_scores:
            candidate = next((c for c in all_candidates if c.id == score.agent_id), None)
            if candidate:
                diversity_bonus = self._calculate_diversity_bonus(candidate, diversity_factors)
                score.overall_score = min(1.0, score.overall_score + diversity_bonus)
        
        return candidate_scores
    
    def _analyze_diversity_factors(self, candidates: List[Agent]) -> Dict[str, List[any]]:
        """Analyze diversity factors in candidate pool."""
        factors = {
            'backgrounds': [],
            'ages': [],
            'regions': [],
            'specializations': []
        }
        
        for candidate in candidates:
            if hasattr(candidate, 'background'):
                factors['backgrounds'].append(candidate.background)
            if hasattr(candidate, 'age'):
                factors['ages'].append(candidate.age)
            if hasattr(candidate, 'region'):
                factors['regions'].append(candidate.region)
            if hasattr(candidate, 'specialization'):
                factors['specializations'].append(candidate.specialization)
        
        return factors
    
    def _calculate_diversity_bonus(self, candidate: Agent, diversity_factors: Dict[str, List[any]]) -> float:
        """Calculate small diversity bonus for underrepresented candidates."""
        bonus = 0.0
        max_bonus = 0.05  # Maximum 5% bonus
        
        # Check each diversity dimension
        dimensions_checked = 0
        underrepresented_count = 0
        
        for factor_name, values in diversity_factors.items():
            if not values:
                continue
            
            dimensions_checked += 1
            candidate_value = getattr(candidate, factor_name.rstrip('s'), None)
            
            if candidate_value and values:
                value_frequency = values.count(candidate_value) / len(values)
                if value_frequency < 0.3:  # Underrepresented if < 30% of pool
                    underrepresented_count += 1
        
        if dimensions_checked > 0:
            underrepresentation_ratio = underrepresented_count / dimensions_checked
            bonus = max_bonus * underrepresentation_ratio
        
        return bonus
    
    def _record_selection_decision(
        self,
        context: SelectionContext,
        role: AdvisorRole,
        selected_candidate: CandidateScore,
        method: SelectionMethod,
        criteria: List[SelectionCriteria]
    ) -> None:
        """Record selection decision for performance tracking."""
        criteria_weights = {c.criterion: c.weight for c in criteria}
        
        history_entry = SelectionHistory(
            turn=len(self.selection_history) + 1,
            context=context,
            role=role,
            selected_agent_id=selected_candidate.agent_id,
            selection_score=selected_candidate.overall_score,
            alternatives_count=len(criteria),  # Simplified
            method_used=method,
            criteria_weights=criteria_weights,
            outcome_success=None  # To be filled later
        )
        
        self.selection_history.append(history_entry)
    
    def evaluate_selection_performance(
        self, 
        agent_id: str, 
        performance_score: float,
        turn_offset: int = 0
    ) -> None:
        """Update selection history with actual performance outcomes."""
        # Find the most recent selection decision for this agent
        target_turn = len(self.selection_history) - turn_offset
        
        for history_entry in reversed(self.selection_history):
            if (history_entry.selected_agent_id == agent_id and 
                history_entry.turn <= target_turn and 
                history_entry.outcome_success is None):
                
                history_entry.outcome_success = performance_score
                
                # Update method performance tracking
                method = history_entry.method_used
                if method not in self.method_performance:
                    self.method_performance[method] = []
                
                self.method_performance[method].append(performance_score)
                break
    
    def get_method_performance_analysis(self) -> Dict[SelectionMethod, Dict[str, float]]:
        """Get performance analysis for different selection methods."""
        analysis = {}
        
        for method, scores in self.method_performance.items():
            if scores:
                analysis[method] = {
                    'average_performance': sum(scores) / len(scores),
                    'success_rate': sum(1 for s in scores if s >= 0.7) / len(scores),
                    'sample_size': len(scores),
                    'std_deviation': self._calculate_score_variance(scores) ** 0.5
                }
        
        return analysis
    
    def _calculate_score_variance(self, scores: List[float]) -> float:
        """Calculate variance of scores."""
        if not scores:
            return 0.0
        
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        return variance
    
    def optimize_criteria_weights(
        self, 
        role: AdvisorRole, 
        performance_feedback: List[tuple[str, float]]
    ) -> None:
        """Optimize criteria weights based on performance feedback."""
        if not performance_feedback:
            return
        
        # Find successful selections for this role
        successful_selections = []
        for agent_id, performance in performance_feedback:
            if performance >= 0.7:  # Consider 0.7+ as successful
                for history in self.selection_history:
                    if (history.selected_agent_id == agent_id and 
                        history.role == role and 
                        history.outcome_success and history.outcome_success >= 0.7):
                        successful_selections.append(history)
        
        if len(successful_selections) < 3:  # Need minimum samples
            return
        
        # Analyze successful criteria patterns
        criteria_performance = {}
        for selection in successful_selections:
            for criterion, weight in selection.criteria_weights.items():
                if criterion not in criteria_performance:
                    criteria_performance[criterion] = []
                criteria_performance[criterion].append((weight, selection.outcome_success))
        
        # Update criteria weights for this role
        if role in self.role_specific_criteria:
            for criterion_obj in self.role_specific_criteria[role]:
                if criterion_obj.criterion in criteria_performance:
                    performances = criteria_performance[criterion_obj.criterion]
                    # Simple optimization: increase weight if high-weight selections performed well
                    avg_performance = sum(perf for _, perf in performances) / len(performances)
                    if avg_performance > 0.8:
                        criterion_obj.weight = min(1.0, criterion_obj.weight * 1.1)  # 10% increase
                    elif avg_performance < 0.6:
                        criterion_obj.weight = max(0.05, criterion_obj.weight * 0.9)  # 10% decrease
            
            # Renormalize weights
            total_weight = sum(c.weight for c in self.role_specific_criteria[role])
            if total_weight > 0:
                for criterion_obj in self.role_specific_criteria[role]:
                    criterion_obj.weight /= total_weight
