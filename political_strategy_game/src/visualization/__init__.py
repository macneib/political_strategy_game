"""
Political Strategy Game Visualization Framework

This module provides a comprehensive visualization framework for displaying
political data, advisor relationships, event timelines, and decision outcomes
from the political strategy game.
"""

# Import base classes first
from .base import (
    VisualizationComponent, VisualizationConfig, VisualizationUpdate,
    DataPoint, UpdateType, DataFormatter, RealTimeDataProvider, VisualizationManager
)

# Import all components for easy access
from .network_graph import AdvisorNetworkVisualization
from .timeline import EventTimelineVisualization
from .dashboard import PoliticalDashboard
from .memory_browser import MemoryBrowserVisualization
from .integrated_manager import IntegratedVisualizationManager, create_political_visualization_system

# Export all public classes and functions
__all__ = [
    # Core framework classes
    'VisualizationComponent',
    'VisualizationConfig', 
    'VisualizationUpdate',
    'DataPoint',
    'UpdateType',
    'DataFormatter',
    'RealTimeDataProvider',
    'VisualizationManager',
    
    # Specific visualization components
    'AdvisorNetworkVisualization',
    'EventTimelineVisualization', 
    'PoliticalDashboard',
    'MemoryBrowserVisualization',
    'IntegratedVisualizationManager',
    
    # Convenience functions
    'create_political_visualization_system'
]

# Import base classes first
from .base import (
    VisualizationComponent, VisualizationConfig, VisualizationUpdate,
    DataPoint, UpdateType, DataFormatter, RealTimeDataProvider, VisualizationManager
)

# Import all components for easy access
from .network_graph import AdvisorNetworkVisualization
from .timeline import EventTimelineVisualization
from .dashboard import PoliticalDashboard
from .memory_browser import MemoryBrowserVisualization
from .integrated_manager import IntegratedVisualizationManager, create_political_visualization_system

# Export all public classes and functions
__all__ = [
    # Core framework classes
    'VisualizationComponent',
    'VisualizationConfig', 
    'VisualizationUpdate',
    'DataPoint',
    'UpdateType',
    'DataFormatter',
    'RealTimeDataProvider',
    'VisualizationManager',
    
    # Specific visualization components
    'AdvisorNetworkVisualization',
    'EventTimelineVisualization', 
    'PoliticalDashboard',
    'MemoryBrowserVisualization',
    'IntegratedVisualizationManager',
    
    # Convenience functions
    'create_political_visualization_system'
]

import asyncio
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass

from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import uuid
from abc import ABC, abstractmethod

# Export main visualization components
# Export all public classes and functions
__all__ = [
    # Core framework classes
    'VisualizationComponent',
    'VisualizationConfig', 
    'VisualizationUpdate',
    'DataPoint',
    'UpdateType',
    'DataFormatter',
    'RealTimeDataProvider',
    'VisualizationManager',
    
    # Specific visualization components
    'AdvisorNetworkVisualization',
    'EventTimelineVisualization', 
    'PoliticalDashboard',
    'MemoryBrowserVisualization',
    'IntegratedVisualizationManager',
    
    # Convenience functions
    'create_political_visualization_system'
]

# Import all components for easy access
from .network_graph import AdvisorNetworkVisualization
from .timeline import EventTimelineVisualization
from .dashboard import PoliticalDashboard
from .memory_browser import MemoryBrowserVisualization
from .integrated_manager import IntegratedVisualizationManager, create_political_visualization_system


class VisualizationType(Enum):
    """Types of political visualizations available."""
    NETWORK_GRAPH = "network_graph"
    TIMELINE = "timeline"
    DASHBOARD = "dashboard"
    DECISION_INTERFACE = "decision_interface"
    MEMORY_BROWSER = "memory_browser"
    ANALYTICS_PANEL = "analytics_panel"


class UpdateType(Enum):
    """Types of data updates for visualization components."""
    FULL_REFRESH = "full_refresh"
    INCREMENTAL_UPDATE = "incremental_update"
    REAL_TIME_EVENT = "real_time_event"
    USER_INTERACTION = "user_interaction"


@dataclass
class VisualizationConfig:
    """Configuration for visualization components."""
    component_id: str
    visualization_type: VisualizationType
    refresh_interval: float = 1.0  # seconds
    auto_update: bool = True
    interactive: bool = True
    theme: str = "default"
    layout_options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.layout_options is None:
            self.layout_options = {}


# Import DataPoint from base module to avoid conflicts
from .base import DataPoint


@dataclass
class VisualizationUpdate:
    """Update message for visualization components."""
    update_id: str
    component_id: str
    update_type: UpdateType
    timestamp: datetime
    data: List[DataPoint]
    source: str = "political_engine"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'update_id': self.update_id,
            'component_id': self.component_id,
            'update_type': self.update_type.value,
            'timestamp': self.timestamp.isoformat(),
            'data': [point.to_dict() for point in self.data],
            'source': self.source
        }


class VisualizationComponent(ABC):
    """Abstract base class for all visualization components."""
    
    def __init__(self, config: VisualizationConfig):
        self.config = config
        self.last_update = datetime.now()
        self.is_active = False
        self.subscribers: List[Callable] = []
        self.data_cache: Dict[str, Any] = {}
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the visualization component."""
        pass
    
    @abstractmethod
    async def update(self, update: VisualizationUpdate) -> bool:
        """Process an update to the visualization."""
        pass
    
    @abstractmethod
    async def render(self) -> Dict[str, Any]:
        """Render the current visualization state."""
        pass
    
    @abstractmethod
    async def handle_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user interaction with the visualization."""
        pass
    
    def subscribe(self, callback: Callable):
        """Subscribe to visualization updates."""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable):
        """Unsubscribe from visualization updates."""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    async def notify_subscribers(self, event: Dict[str, Any]):
        """Notify all subscribers of visualization events."""
        for callback in self.subscribers:
            try:
                await callback(event)
            except Exception as e:
                # Log error but continue with other subscribers
                print(f"Error notifying subscriber: {e}")


class DataFormatter:
    """Formats political simulation data for visualization consumption."""
    
    @staticmethod
    def format_advisor_relationships(advisors: List[Any]) -> List[Dict[str, Any]]:
        """Format advisor relationship data for network visualization."""
        nodes = []
        links = []
        
        for advisor in advisors:
            nodes.append({
                'id': advisor.advisor_id,
                'name': advisor.name,
                'role': advisor.role,
                'loyalty': advisor.loyalty,
                'influence': advisor.influence,
                'stress_level': advisor.stress_level,
                'mood': advisor.current_mood,
                'group': advisor.role,  # For visual grouping
                'metadata': {
                    'personality_traits': advisor.personality_traits,
                    'current_activity': advisor.current_activity,
                    'location': advisor.location
                }
            })
            
            # Create relationship links
            for target_id, strength in advisor.relationships.items():
                if target_id != advisor.advisor_id:  # Avoid self-links
                    links.append({
                        'source': advisor.advisor_id,
                        'target': target_id,
                        'strength': strength,
                        'type': 'relationship'
                    })
        
        return {
            'nodes': nodes,
            'links': links,
            'metadata': {
                'total_advisors': len(nodes),
                'total_relationships': len(links),
                'timestamp': datetime.now().isoformat()
            }
        }
    
    @staticmethod
    def format_political_events(events: List[Any]) -> List[Dict[str, Any]]:
        """Format political events for timeline visualization."""
        formatted_events = []
        
        for event in events:
            formatted_events.append({
                'id': event.event_id,
                'title': event.title,
                'description': event.description,
                'type': event.event_type,
                'severity': event.severity,
                'timestamp': event.timestamp.isoformat(),
                'civilization_id': event.civilization_id,
                'participants': event.participants,
                'consequences': event.consequences,
                'duration': event.duration,
                'category': event.event_type,  # For filtering
                'impact_score': DataFormatter._calculate_event_impact(event)
            })
        
        return sorted(formatted_events, key=lambda x: x['timestamp'], reverse=True)
    
    @staticmethod
    def format_political_status(civilization: Any) -> Dict[str, Any]:
        """Format civilization political status for dashboard display."""
        return {
            'civilization_id': civilization.civilization_id,
            'name': civilization.name,
            'leader_name': civilization.leader_name,
            'political_stability': civilization.political_stability,
            'economic_strength': civilization.economic_strength,
            'military_power': civilization.military_power,
            'coup_probability': DataFormatter._calculate_coup_probability(civilization),
            'faction_strength': DataFormatter._analyze_faction_strength(civilization),
            'active_crises': len(civilization.active_crises),
            'active_conspiracies': len(civilization.active_conspiracies),
            'diplomatic_score': sum(civilization.diplomatic_relations.values()) / len(civilization.diplomatic_relations) if civilization.diplomatic_relations else 0,
            'threat_level': DataFormatter._assess_threat_level(civilization),
            'stability_trend': DataFormatter._calculate_stability_trend(civilization),
            'last_updated': datetime.now().isoformat()
        }
    
    @staticmethod
    def format_advisor_memories(advisor: Any, memory_manager: Any) -> Dict[str, Any]:
        """Format advisor memories for browser interface."""
        memories = memory_manager.recall_memories_by_advisor(advisor.advisor_id)
        
        formatted_memories = []
        for memory in memories:
            formatted_memories.append({
                'id': memory.memory_id,
                'content': memory.content,
                'memory_type': memory.memory_type,
                'importance': memory.importance,
                'reliability': memory.reliability,
                'emotional_impact': memory.emotional_impact,
                'timestamp': memory.timestamp.isoformat(),
                'access_count': memory.access_count,
                'last_accessed': memory.last_accessed.isoformat() if memory.last_accessed else None,
                'tags': memory.tags,
                'related_memories': [m.memory_id for m in memory_manager.find_related_memories(memory.memory_id)]
            })
        
        return {
            'advisor_id': advisor.advisor_id,
            'advisor_name': advisor.name,
            'memories': formatted_memories,
            'memory_stats': {
                'total_memories': len(formatted_memories),
                'average_importance': sum(m['importance'] for m in formatted_memories) / len(formatted_memories) if formatted_memories else 0,
                'average_reliability': sum(m['reliability'] for m in formatted_memories) / len(formatted_memories) if formatted_memories else 0,
                'most_accessed': max(formatted_memories, key=lambda m: m['access_count']) if formatted_memories else None
            },
            'last_updated': datetime.now().isoformat()
        }
    
    @staticmethod
    def _calculate_event_impact(event: Any) -> float:
        """Calculate numerical impact score for event."""
        severity_scores = {'minor': 1, 'moderate': 2, 'major': 3, 'critical': 4}
        base_score = severity_scores.get(event.severity, 1)
        participant_modifier = len(event.participants) * 0.1
        return min(base_score + participant_modifier, 5.0)
    
    @staticmethod
    def _calculate_coup_probability(civilization: Any) -> float:
        """Calculate coup probability based on political factors."""
        # Simple formula - can be enhanced with more sophisticated analysis
        instability = 1.0 - civilization.political_stability
        crisis_factor = len(civilization.active_crises) * 0.1
        conspiracy_factor = len(civilization.active_conspiracies) * 0.15
        
        coup_probability = (instability + crisis_factor + conspiracy_factor) / 3.0
        return min(coup_probability, 1.0)
    
    @staticmethod
    def _analyze_faction_strength(civilization: Any) -> Dict[str, float]:
        """Analyze relative strength of political factions."""
        # This would be enhanced with actual faction data
        return {
            'loyalists': 0.6,
            'moderates': 0.25,
            'rebels': 0.15
        }
    
    @staticmethod
    def _assess_threat_level(civilization: Any) -> str:
        """Assess overall threat level for the civilization."""
        coup_prob = DataFormatter._calculate_coup_probability(civilization)
        
        if coup_prob >= 0.8:
            return "CRITICAL"
        elif coup_prob >= 0.6:
            return "HIGH"
        elif coup_prob >= 0.4:
            return "MODERATE"
        elif coup_prob >= 0.2:
            return "LOW"
        else:
            return "MINIMAL"
    
    @staticmethod
    def _calculate_stability_trend(civilization: Any) -> str:
        """Calculate stability trend direction."""
        # This would analyze historical stability data
        # For now, return based on current factors
        active_issues = len(civilization.active_crises) + len(civilization.active_conspiracies)
        
        if active_issues == 0:
            return "IMPROVING"
        elif active_issues <= 2:
            return "STABLE"
        else:
            return "DECLINING"


class RealTimeDataProvider:
    """Provides real-time data updates for visualization components."""
    
    def __init__(self):
        self.components: Dict[str, VisualizationComponent] = {}
        self.update_queue: List[VisualizationUpdate] = []
        self.is_running = False
        self.update_callbacks: Dict[str, List[Callable]] = {}
    
    def register_component(self, component: VisualizationComponent):
        """Register a visualization component for updates."""
        self.components[component.config.component_id] = component
        self.update_callbacks[component.config.component_id] = []
    
    def unregister_component(self, component_id: str):
        """Unregister a visualization component."""
        if component_id in self.components:
            del self.components[component_id]
        if component_id in self.update_callbacks:
            del self.update_callbacks[component_id]
    
    async def send_update(self, update: VisualizationUpdate):
        """Send update to specific component or all components."""
        if update.component_id in self.components:
            component = self.components[update.component_id]
            await component.update(update)
        else:
            # Broadcast to all components
            for component in self.components.values():
                await component.update(update)
    
    def create_update(self, component_id: str, data_points: List[DataPoint], 
                     update_type: UpdateType = UpdateType.INCREMENTAL_UPDATE) -> VisualizationUpdate:
        """Create a visualization update message."""
        return VisualizationUpdate(
            update_id=str(uuid.uuid4()),
            component_id=component_id,
            update_type=update_type,
            timestamp=datetime.now(),
            data=data_points
        )
    
    async def start_real_time_updates(self):
        """Start processing real-time updates."""
        self.is_running = True
        # This would typically run in a background task
        # Processing updates from the game engine
    
    async def stop_real_time_updates(self):
        """Stop processing real-time updates."""
        self.is_running = False


class VisualizationManager:
    """Main manager for all political visualization systems."""
    
    def __init__(self):
        self.components: Dict[str, VisualizationComponent] = {}
        self.data_provider = RealTimeDataProvider()
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the visualization manager."""
        await self.data_provider.start_real_time_updates()
        self.is_initialized = True
    
    def add_component(self, component: VisualizationComponent):
        """Add a visualization component to the manager."""
        self.components[component.config.component_id] = component
        self.data_provider.register_component(component)
    
    def remove_component(self, component_id: str):
        """Remove a visualization component from the manager."""
        if component_id in self.components:
            del self.components[component_id]
        self.data_provider.unregister_component(component_id)
    
    async def update_all(self, data_source: Any):
        """Update all visualization components with new data."""
        for component in self.components.values():
            if component.config.auto_update:
                # Create appropriate update based on component type
                update = await self._create_component_update(component, data_source)
                if update:
                    await component.update(update)
    
    async def _create_component_update(self, component: VisualizationComponent, 
                                     data_source: Any) -> Optional[VisualizationUpdate]:
        """Create appropriate update for specific component type."""
        # This would be implemented based on component type
        # For now, return None - will be implemented in specific components
        return None
    
    def get_component_states(self) -> Dict[str, Dict[str, Any]]:
        """Get current state of all visualization components."""
        states = {}
        for component_id, component in self.components.items():
            try:
                # This would call render() asynchronously in practice
                states[component_id] = {
                    'type': component.config.visualization_type.value,
                    'last_update': component.last_update.isoformat() if component.last_update else None,
                    'is_active': component.is_active,
                    'config': asdict(component.config)
                }
            except Exception as e:
                states[component_id] = {'error': str(e)}
        
        return states
