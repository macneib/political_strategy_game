#!/usr/bin/env python3
"""
Core Game State Management System

This module implements the central game state management system that coordinates
all game systems and provides the foundation for era progression, save/load,
and cross-system communication.
"""

from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import asyncio
from dataclasses import dataclass

from .civilization import Civilization
from .technology_tree import TechnologyEra
from .events import EventManager, PoliticalEvent
from .resources import ResourceManager

# Import bridge components - make optional for now
try:
    from src.bridge.event_broadcaster import EventBroadcaster
except ImportError:
    # Fallback if bridge components aren't available
    EventBroadcaster = None


class GamePhase(str, Enum):
    """Current phase of the game."""
    INITIALIZATION = "initialization"
    ACTIVE_PLAY = "active_play"
    ERA_TRANSITION = "era_transition"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class VictoryCondition(str, Enum):
    """Available victory conditions."""
    CONQUEST = "conquest"
    CULTURAL = "cultural"
    DIPLOMATIC = "diplomatic"
    TECHNOLOGICAL = "technological"
    ECONOMIC = "economic"
    GREAT_FILTER_MASTERY = "great_filter_mastery"


@dataclass
class EraTransitionMetrics:
    """Metrics for evaluating era transition readiness."""
    
    technology_advancement: float = 0.0
    cultural_development: float = 0.0
    population_growth: float = 0.0
    political_stability: float = 0.0
    resource_security: float = 0.0
    
    def calculate_overall_readiness(self) -> float:
        """Calculate overall era transition readiness."""
        weights = {
            'technology_advancement': 0.3,
            'cultural_development': 0.2,
            'population_growth': 0.2,
            'political_stability': 0.15,
            'resource_security': 0.15
        }
        
        total_score = (
            self.technology_advancement * weights['technology_advancement'] +
            self.cultural_development * weights['cultural_development'] +
            self.population_growth * weights['population_growth'] +
            self.political_stability * weights['political_stability'] +
            self.resource_security * weights['resource_security']
        )
        
        return min(1.0, total_score)


class EraState(BaseModel):
    """State information for a specific era."""
    
    era: TechnologyEra
    start_turn: int
    start_year: int
    current_year: int
    
    # Era progression tracking
    transition_metrics: EraTransitionMetrics = Field(default_factory=EraTransitionMetrics)
    advancement_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    transition_ready: bool = Field(default=False)
    
    # Era-specific unlocks
    available_technologies: Set[str] = Field(default_factory=set)
    available_buildings: Set[str] = Field(default_factory=set)
    available_units: Set[str] = Field(default_factory=set)
    victory_conditions: Set[VictoryCondition] = Field(default_factory=set)
    
    # Historical events in this era
    significant_events: List[str] = Field(default_factory=list)
    era_achievements: List[str] = Field(default_factory=list)


class GameState(BaseModel):
    """Central game state coordinating all systems."""
    
    # Core game identification
    game_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    game_name: str = Field(default="New Political Strategy Game")
    creation_timestamp: datetime = Field(default_factory=datetime.now)
    last_save_timestamp: Optional[datetime] = Field(default=None)
    
    # Game progression
    current_turn: int = Field(default=1)
    current_phase: GamePhase = Field(default=GamePhase.INITIALIZATION)
    current_era: TechnologyEra = Field(default=TechnologyEra.ANCIENT)
    
    # Era management
    era_states: Dict[TechnologyEra, EraState] = Field(default_factory=dict)
    era_transition_queue: List[TechnologyEra] = Field(default_factory=list)
    
    # Civilization management
    civilizations: Dict[str, Civilization] = Field(default_factory=dict)
    active_civilization_id: Optional[str] = Field(default=None)
    
    # Victory and game end conditions
    victory_conditions_enabled: Set[VictoryCondition] = Field(default_factory=set)
    game_over: bool = Field(default=False)
    winner_civilization_id: Optional[str] = Field(default=None)
    victory_type: Optional[VictoryCondition] = Field(default=None)
    
    # System integration
    event_history: List[Dict[str, Any]] = Field(default_factory=list)
    global_modifiers: Dict[str, float] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class GameStateManager:
    """Central manager for coordinating all game systems."""
    
    def __init__(self, event_broadcaster: Optional[Any] = None):
        self.state = GameState()
        self.event_broadcaster = event_broadcaster or (EventBroadcaster() if EventBroadcaster else None)
        self.system_managers: Dict[str, Any] = {}
        self.era_config = self._load_era_configurations()
        
        # Subscribe to important events
        self._setup_event_subscriptions()
        
    def initialize_game(self, game_config: Dict[str, Any]) -> None:
        """Initialize a new game with the specified configuration."""
        self.state.game_name = game_config.get('name', 'New Game')
        
        # Initialize starting era
        starting_era = TechnologyEra(game_config.get('starting_era', 'ancient'))
        self._initialize_era(starting_era)
        self.state.current_era = starting_era
        
        # Set up victory conditions
        victory_conditions = game_config.get('victory_conditions', ['conquest', 'cultural'])
        self.state.victory_conditions_enabled = {
            VictoryCondition(vc) for vc in victory_conditions
        }
        
        # Initialize civilizations
        for civ_config in game_config.get('civilizations', []):
            self._create_civilization(civ_config)
            
        # Set active civilization
        if self.state.civilizations:
            self.state.active_civilization_id = list(self.state.civilizations.keys())[0]
            
        self.state.current_phase = GamePhase.ACTIVE_PLAY
        
        # Broadcast game initialization
        self._broadcast_event('game_initialized', {
            'game_id': self.state.game_id,
            'starting_era': starting_era.value,
            'civilizations': list(self.state.civilizations.keys())
        })
        
    def advance_turn(self) -> Dict[str, Any]:
        """Advance the game by one turn and process all systems."""
        if self.state.current_phase != GamePhase.ACTIVE_PLAY:
            raise ValueError(f"Cannot advance turn in phase: {self.state.current_phase}")
            
        self.state.current_turn += 1
        
        # Update current year based on era
        current_era_state = self.state.era_states[self.state.current_era]
        years_per_turn = self._calculate_years_per_turn(self.state.current_era)
        current_era_state.current_year += years_per_turn
        
        turn_results = {
            'turn': self.state.current_turn,
            'year': current_era_state.current_year,
            'era': self.state.current_era.value,
            'events': [],
            'era_transition': None
        }
        
        # Process each civilization's turn
        for civ_id, civilization in self.state.civilizations.items():
            civ_results = self._process_civilization_turn(civilization)
            turn_results['events'].extend(civ_results.get('events', []))
            
        # Check for era transition
        era_transition = self._check_era_transition()
        if era_transition:
            turn_results['era_transition'] = era_transition
            
        # Check victory conditions
        victory_check = self._check_victory_conditions()
        if victory_check:
            turn_results['victory'] = victory_check
            
        # Broadcast turn completion
        self._broadcast_event('turn_completed', turn_results)
        
        return turn_results
        
    def check_era_transition_readiness(self, civilization_id: str) -> EraTransitionMetrics:
        """Check if a civilization is ready for era transition."""
        civilization = self.state.civilizations[civilization_id]
        current_era_state = self.state.era_states[self.state.current_era]
        
        metrics = EraTransitionMetrics()
        
        # Evaluate technology advancement
        if hasattr(civilization, 'technology_manager'):
            tech_progress = civilization.technology_manager.get_era_completion_percentage(
                self.state.current_era
            )
            metrics.technology_advancement = tech_progress
            
        # Evaluate cultural development
        if hasattr(civilization, 'culture_level'):
            metrics.cultural_development = min(1.0, civilization.culture_level / 100.0)
            
        # Evaluate population growth
        if hasattr(civilization, 'population_manager'):
            pop_growth = civilization.population_manager.get_growth_rate()
            metrics.population_growth = min(1.0, max(0.0, pop_growth))
            
        # Evaluate political stability
        stability_score = self._calculate_stability_score(civilization)
        metrics.political_stability = stability_score
        
        # Evaluate resource security
        resource_score = self._calculate_resource_security(civilization)
        metrics.resource_security = resource_score
        
        # Update era state with current metrics
        current_era_state.transition_metrics = metrics
        current_era_state.transition_ready = (
            metrics.calculate_overall_readiness() >= current_era_state.advancement_threshold
        )
        
        return metrics
        
    def trigger_era_transition(self, new_era: TechnologyEra) -> Dict[str, Any]:
        """Trigger transition to a new era."""
        if self.state.current_phase != GamePhase.ACTIVE_PLAY:
            raise ValueError("Cannot transition era outside of active play")
            
        old_era = self.state.current_era
        
        # Set transition phase
        self.state.current_phase = GamePhase.ERA_TRANSITION
        
        # Broadcast era transition start
        self._broadcast_event('era_transition_starting', {
            'old_era': old_era.value,
            'new_era': new_era.value,
            'turn': self.state.current_turn
        })
        
        # Initialize new era
        self._initialize_era(new_era)
        
        # Update all civilizations for new era
        transition_results = {}
        for civ_id, civilization in self.state.civilizations.items():
            civ_transition = self._apply_era_transition_to_civilization(
                civilization, old_era, new_era
            )
            transition_results[civ_id] = civ_transition
            
        # Update current era
        self.state.current_era = new_era
        self.state.current_phase = GamePhase.ACTIVE_PLAY
        
        # Broadcast era transition completion
        self._broadcast_event('era_transition_complete', {
            'new_era': new_era.value,
            'turn': self.state.current_turn,
            'civilization_results': transition_results
        })
        
        return {
            'old_era': old_era.value,
            'new_era': new_era.value,
            'civilization_results': transition_results
        }
        
    def get_available_eras(self) -> List[TechnologyEra]:
        """Get list of eras available for transition."""
        current_index = list(TechnologyEra).index(self.state.current_era)
        available = []
        
        # Can transition to next era if ready
        if current_index < len(TechnologyEra) - 1:
            next_era = list(TechnologyEra)[current_index + 1]
            available.append(next_era)
            
        return available
        
    def register_system_manager(self, system_name: str, manager: Any) -> None:
        """Register a system manager for coordination."""
        self.system_managers[system_name] = manager
        
        # Notify manager of current game state
        if hasattr(manager, 'on_game_state_update'):
            manager.on_game_state_update(self.state)
            
    def _initialize_era(self, era: TechnologyEra) -> None:
        """Initialize state for a specific era."""
        era_config = self.era_config[era]
        
        era_state = EraState(
            era=era,
            start_turn=self.state.current_turn,
            start_year=era_config['start_year'],
            current_year=era_config['start_year']
        )
        
        # Set era-specific unlocks
        era_state.available_technologies = set(era_config.get('technologies', []))
        era_state.available_buildings = set(era_config.get('buildings', []))
        era_state.available_units = set(era_config.get('units', []))
        era_state.victory_conditions = {
            VictoryCondition(vc) for vc in era_config.get('victory_conditions', [])
        }
        
        self.state.era_states[era] = era_state
        
    def _load_era_configurations(self) -> Dict[TechnologyEra, Dict[str, Any]]:
        """Load era configuration data."""
        # This would typically load from JSON files
        return {
            TechnologyEra.ANCIENT: {
                'start_year': -4000,
                'end_year': -500,
                'years_per_turn': 50,
                'technologies': ['stone_tools', 'agriculture', 'animal_husbandry'],
                'buildings': ['settlement', 'granary', 'barracks'],
                'units': ['warrior', 'settler', 'worker'],
                'victory_conditions': ['conquest', 'cultural']
            },
            TechnologyEra.CLASSICAL: {
                'start_year': -500,
                'end_year': 500,
                'years_per_turn': 25,
                'technologies': ['iron_working', 'philosophy', 'engineering'],
                'buildings': ['library', 'forum', 'aqueduct'],
                'units': ['legionary', 'catapult', 'galley'],
                'victory_conditions': ['conquest', 'cultural', 'diplomatic']
            },
            TechnologyEra.MEDIEVAL: {
                'start_year': 500,
                'end_year': 1450,
                'years_per_turn': 20,
                'technologies': ['feudalism', 'theology', 'navigation'],
                'buildings': ['castle', 'cathedral', 'market'],
                'units': ['knight', 'crossbow', 'caravel'],
                'victory_conditions': ['conquest', 'cultural', 'diplomatic', 'economic']
            }
        }
        
    def _calculate_years_per_turn(self, era: TechnologyEra) -> int:
        """Calculate how many years pass per turn in the given era."""
        return self.era_config[era]['years_per_turn']
        
    def _process_civilization_turn(self, civilization: Civilization) -> Dict[str, Any]:
        """Process one turn for a civilization."""
        results = {'events': [], 'changes': {}}
        
        # Process advisor actions
        if hasattr(civilization, 'advisor_council') and civilization.advisor_council:
            # Note: advisor_council.process_turn() would need to be implemented
            # For now, just note that advisors exist
            results['changes']['advisors'] = {'active_advisors': len(civilization.advisors)}
            
        # Process resource management
        if hasattr(civilization, 'resource_manager') and civilization.resource_manager:
            resource_results = civilization.resource_manager.update_resources(1)
            results['changes']['resources'] = resource_results
            
        # Process events
        if hasattr(civilization, 'event_manager') and civilization.event_manager:
            # Note: event_manager.process_turn() would need to be implemented
            # For now, use existing event processing
            pending_events = getattr(civilization, 'pending_events', [])
            results['events'].extend([{'event': event.id} for event in pending_events[:3]])
            
        return results
        
    def _check_era_transition(self) -> Optional[Dict[str, Any]]:
        """Check if any civilization is ready for era transition."""
        for civ_id, civilization in self.state.civilizations.items():
            metrics = self.check_era_transition_readiness(civ_id)
            
            if metrics.calculate_overall_readiness() >= 0.8:
                available_eras = self.get_available_eras()
                if available_eras:
                    return {
                        'civilization_id': civ_id,
                        'current_era': self.state.current_era.value,
                        'available_eras': [era.value for era in available_eras],
                        'readiness_score': metrics.calculate_overall_readiness()
                    }
                    
        return None
        
    def _check_victory_conditions(self) -> Optional[Dict[str, Any]]:
        """Check if any civilization has achieved victory."""
        # Implementation would check each enabled victory condition
        # This is a placeholder for the victory system
        return None
        
    def _calculate_stability_score(self, civilization: Civilization) -> float:
        """Calculate political stability score for era transition."""
        if hasattr(civilization, 'political_state'):
            stability_map = {
                'stable': 1.0,
                'tense': 0.7,
                'unstable': 0.4,
                'crisis': 0.2,
                'collapse': 0.0
            }
            return stability_map.get(civilization.political_state.stability.value, 0.5)
        return 0.5
        
    def _calculate_resource_security(self, civilization: Civilization) -> float:
        """Calculate resource security score for era transition."""
        if hasattr(civilization, 'resource_manager') and civilization.resource_manager:
            # Calculate security based on multiple factors
            summary = civilization.resource_manager.get_resource_summary()
            
            # Economic security (30% weight)
            economic_score = 0.0
            if summary['economic']['treasury'] > 500:
                economic_score += 0.4
            if summary['economic']['net_income'] > 0:
                economic_score += 0.3
            if summary['economic']['stability'] > 0.7:
                economic_score += 0.3
                
            # Military security (25% weight)  
            military_score = 0.0
            if summary['military']['morale'] > 0.6:
                military_score += 0.4
            if summary['military']['strength'] > 0.5:
                military_score += 0.3
            if summary['military']['active_conflicts'] == 0:  # This is already a count
                military_score += 0.3
                
            # Technology security (20% weight)
            tech_score = 0.0
            tech_levels = summary['technology']['tech_levels']
            avg_tech_level = sum(tech_levels.values()) / len(tech_levels)
            tech_score = avg_tech_level
            
            # Event stability (25% weight)
            event_score = 1.0 if summary['active_events'] == 0 else max(0.0, 1.0 - summary['active_events'] * 0.2)
            
            # Weighted average
            total_score = (economic_score * 0.3 + military_score * 0.25 + 
                          tech_score * 0.2 + event_score * 0.25)
            
            return min(1.0, total_score)
        return 0.5
        
    def _apply_era_transition_to_civilization(self, civilization: Civilization, 
                                           old_era: TechnologyEra, 
                                           new_era: TechnologyEra) -> Dict[str, Any]:
        """Apply era transition effects to a civilization."""
        results = {
            'technology_unlocks': [],
            'building_unlocks': [],
            'unit_unlocks': [],
            'bonuses_applied': []
        }
        
        new_era_state = self.state.era_states[new_era]
        
        # Unlock new technologies
        if hasattr(civilization, 'technology_manager'):
            for tech in new_era_state.available_technologies:
                civilization.technology_manager.unlock_technology(tech)
                results['technology_unlocks'].append(tech)
                
        # Apply era transition bonuses
        # This would include population growth, cultural advancement, etc.
        
        return results
        
    def _create_civilization(self, civ_config: Dict[str, Any]) -> str:
        """Create a new civilization from configuration."""
        from .leader import Leader, LeadershipStyle
        from .advisor import PersonalityProfile
        
        civ_id = str(uuid.uuid4())
        civ_name = civ_config.get('name', 'Unknown Civilization')
        
        # Create a basic leader for the civilization
        leader = Leader(
            name=civ_config.get('leader_name', f'Leader of {civ_name}'),
            civilization_id=civ_id,
            personality=PersonalityProfile(
                openness=0.5,
                conscientiousness=0.6,
                extraversion=0.5,
                agreeableness=0.5,
                neuroticism=0.3
            ),
            leadership_style=LeadershipStyle(civ_config.get('leadership_style', 'collaborative'))
        )
        
        # Create the civilization
        civilization = Civilization(
            id=civ_id,
            name=civ_name,
            leader=leader,
            current_turn=self.state.current_turn
        )
        
        self.state.civilizations[civ_id] = civilization
        
        return civ_id
        
    def _setup_event_subscriptions(self) -> None:
        """Set up event subscriptions for cross-system coordination."""
        # Subscribe to events from other systems
        pass
        
    def _broadcast_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Broadcast an event to all interested systems."""
        if self.event_broadcaster:
            self.event_broadcaster.broadcast(event_type, data)
            
        # Add to event history
        self.state.event_history.append({
            'type': event_type,
            'data': data,
            'turn': self.state.current_turn,
            'timestamp': datetime.now()
        })
