"""
Advisor Selection System

A modular Multi-Criteria Decision Analysis (MCDA) system for advisor candidate selection.
Provides sophisticated algorithms including Fuzzy AHP, AHP, TOPSIS, and hybrid approaches
for comprehensive advisor evaluation and selection.
"""

from .criteria import (
    SelectionCriterion,
    SelectionMethod,
    SelectionContext,
    CandidateFilterType,
    SelectionCriteria,
    CandidateScore,
    SelectionHistory,
    get_default_role_criteria,
    get_default_context_weights
)

from .algorithms import MCDAAlgorithms

from .selector import AdvisorCandidateSelector

__all__ = [
    # Enums and criteria
    'SelectionCriterion',
    'SelectionMethod',
    'SelectionContext',
    'CandidateFilterType',
    
    # Data classes
    'SelectionCriteria',
    'CandidateScore',
    'SelectionHistory',
    
    # Algorithm engine
    'MCDAAlgorithms',
    
    # Main selector
    'AdvisorCandidateSelector',
    
    # Helper functions
    'get_default_role_criteria',
    'get_default_context_weights'
]

from .criteria import (
    SelectionCriterion,
    SelectionMethod, 
    SelectionContext,
    CandidateFilterType,
    SelectionCriteria,
    CandidateScore,
    SelectionHistory,
    get_default_role_criteria,
    get_default_context_weights
)

from .algorithms import MCDAAlgorithms

from .selector import AdvisorCandidateSelector

__all__ = [
    # Enums and criteria
    'SelectionCriterion',
    'SelectionMethod',
    'SelectionContext',
    'CandidateFilterType',
    
    # Data classes
    'SelectionCriteria',
    'CandidateScore',
    'SelectionHistory',
    
    # Algorithm engine
    'MCDAAlgorithms',
    
    # Main selector
    'AdvisorCandidateSelector',
    
    # Helper functions
    'get_default_role_criteria',
    'get_default_context_weights'
]
