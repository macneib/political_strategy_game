"""
Base classes and interfaces for the visualization framework.
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass


class UpdateType(Enum):
    """Types of visualization updates."""
    FULL_REFRESH = "full_refresh"
    INCREMENTAL_UPDATE = "incremental_update"
    REAL_TIME_EVENT = "real_time_event"


@dataclass
class DataPoint:
    """Represents a single data point for visualization."""
    data_type: str
    value: Any
    timestamp: datetime


@dataclass
class VisualizationConfig:
    """Configuration for a visualization component."""
    component_id: str
    component_type: str
    layout_options: Dict[str, Any]
    update_frequency: float = 1.0  # Updates per second
    real_time_enabled: bool = True


@dataclass
class VisualizationUpdate:
    """Represents an update to a visualization component."""
    update_type: UpdateType
    data: List[DataPoint]
    timestamp: datetime
    source: str = "unknown"


class VisualizationComponent(ABC):
    """Abstract base class for all visualization components."""
    
    def __init__(self, config: VisualizationConfig):
        self.config = config
        self.is_active = False
        self.last_update: Optional[datetime] = None
        self.subscribers: List[Callable] = []
    
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
    
    async def stop(self):
        """Stop the visualization component."""
        self.is_active = False
    
    async def subscribe(self, callback: Callable):
        """Subscribe to visualization updates."""
        self.subscribers.append(callback)
    
    async def unsubscribe(self, callback: Callable):
        """Unsubscribe from visualization updates."""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    async def notify_subscribers(self, data: Dict[str, Any]):
        """Notify all subscribers of updates."""
        for callback in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                print(f"Error notifying subscriber: {e}")


class DataFormatter:
    """Utility class for formatting data for visualizations."""
    
    @staticmethod
    def format_advisor_relationships(data: Dict[str, Any]) -> Dict[str, Any]:
        """Format advisor relationship data for network visualization."""
        advisors = data.get('advisors', [])
        relationships = data.get('relationships', [])
        
        # Format nodes
        nodes = []
        for advisor in advisors:
            nodes.append({
                'id': advisor['advisor_id'],
                'name': advisor['name'],
                'role': advisor['role'],
                'loyalty': advisor['loyalty'],
                'influence': advisor['influence'],
                'stress_level': advisor.get('stress_level', 0.5),
                'mood': advisor.get('current_mood', 'neutral'),
                'group': advisor['role']
            })
        
        # Format links
        links = []
        for rel in relationships:
            links.append({
                'source': rel['source_id'],
                'target': rel['target_id'],
                'strength': rel['strength'],
                'type': rel.get('type', 'relationship')
            })
        
        return {'nodes': nodes, 'links': links}
    
    @staticmethod
    def format_political_events(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format political event data for timeline visualization."""
        formatted_events = []
        
        for event in data:
            formatted_events.append({
                'event_id': event['event_id'],
                'title': event['title'],
                'category': event['category'],
                'severity': event['severity'],
                'timestamp': event['timestamp'],
                'participants': event.get('participants', []),
                'description': event.get('description', ''),
                'consequences': event.get('consequences', []),
                'metadata': event.get('metadata', {})
            })
        
        return formatted_events
    
    @staticmethod
    def format_advisor_memories(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format advisor memory data for memory browser."""
        formatted_memories = []
        
        for memory in data:
            formatted_memories.append({
                'memory_id': memory['memory_id'],
                'advisor_id': memory['advisor_id'],
                'title': memory['title'],
                'content': memory['content'],
                'memory_type': memory.get('memory_type', 'personal_experience'),
                'importance': memory.get('importance', 'medium'),
                'emotional_tone': memory.get('emotional_tone', 'neutral'),
                'timestamp': memory['timestamp'],
                'tags': memory.get('tags', []),
                'participants': memory.get('participants', []),
                'related_memories': memory.get('related_memories', []),
                'metadata': memory.get('metadata', {})
            })
        
        return formatted_memories


class RealTimeDataProvider:
    """Provides real-time data updates to visualization components."""
    
    def __init__(self):
        self.is_active = False
        self.subscribers: Dict[str, List[Callable]] = {}
        self.data_buffer: List[DataPoint] = []
        self.update_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize the data provider."""
        self.is_active = True
        self.update_task = asyncio.create_task(self._update_loop())
    
    async def stop(self):
        """Stop the data provider."""
        self.is_active = False
        if self.update_task:
            self.update_task.cancel()
    
    async def subscribe(self, data_type: str, callback: Callable):
        """Subscribe to specific data type updates."""
        if data_type not in self.subscribers:
            self.subscribers[data_type] = []
        self.subscribers[data_type].append(callback)
    
    async def publish_data(self, data_point: DataPoint):
        """Publish a data point to subscribers."""
        self.data_buffer.append(data_point)
        
        # Notify subscribers immediately for real-time data
        if data_point.data_type in self.subscribers:
            for callback in self.subscribers[data_point.data_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data_point)
                    else:
                        callback(data_point)
                except Exception as e:
                    print(f"Error notifying data subscriber: {e}")
    
    async def _update_loop(self):
        """Background update loop for periodic data processing."""
        while self.is_active:
            try:
                # Process buffered data
                if self.data_buffer:
                    # Group by data type and send batched updates
                    grouped_data = {}
                    for point in self.data_buffer:
                        if point.data_type not in grouped_data:
                            grouped_data[point.data_type] = []
                        grouped_data[point.data_type].append(point)
                    
                    # Clear buffer
                    self.data_buffer.clear()
                    
                    # Send grouped updates
                    for data_type, points in grouped_data.items():
                        if data_type in self.subscribers:
                            for callback in self.subscribers[data_type]:
                                try:
                                    if asyncio.iscoroutinefunction(callback):
                                        await callback(points)
                                    else:
                                        callback(points)
                                except Exception as e:
                                    print(f"Error in batch update: {e}")
                
                await asyncio.sleep(0.1)  # 100ms update cycle
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in data provider update loop: {e}")


class VisualizationManager:
    """Manages multiple visualization components."""
    
    def __init__(self):
        self.components: Dict[str, VisualizationComponent] = {}
        self.data_provider: Optional[RealTimeDataProvider] = None
        self.is_active = False
    
    async def initialize(self):
        """Initialize the visualization manager."""
        self.data_provider = RealTimeDataProvider()
        await self.data_provider.initialize()
        self.is_active = True
    
    async def stop(self):
        """Stop the visualization manager."""
        self.is_active = False
        
        # Stop all components
        for component in self.components.values():
            await component.stop()
        
        # Stop data provider
        if self.data_provider:
            await self.data_provider.stop()
    
    async def add_component(self, component: VisualizationComponent) -> bool:
        """Add a visualization component."""
        try:
            if await component.initialize():
                self.components[component.config.component_id] = component
                return True
            return False
        except Exception as e:
            print(f"Error adding component: {e}")
            return False
    
    async def remove_component(self, component_id: str) -> bool:
        """Remove a visualization component."""
        if component_id in self.components:
            await self.components[component_id].stop()
            del self.components[component_id]
            return True
        return False
    
    async def update_component(self, component_id: str, update: VisualizationUpdate) -> bool:
        """Update a specific component."""
        if component_id in self.components:
            try:
                return await self.components[component_id].update(update)
            except Exception as e:
                print(f"Error updating component {component_id}: {e}")
                return False
        return False
    
    async def broadcast_update(self, update: VisualizationUpdate) -> Dict[str, bool]:
        """Broadcast an update to all components."""
        results = {}
        for component_id, component in self.components.items():
            try:
                results[component_id] = await component.update(update)
            except Exception as e:
                print(f"Error broadcasting to {component_id}: {e}")
                results[component_id] = False
        return results
    
    async def get_component_state(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state of a component."""
        if component_id in self.components:
            try:
                return await self.components[component_id].render()
            except Exception as e:
                print(f"Error getting component state: {e}")
                return None
        return None
    
    async def handle_component_interaction(self, component_id: str, interaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle interaction with a specific component."""
        if component_id in self.components:
            try:
                return await self.components[component_id].handle_interaction(interaction)
            except Exception as e:
                print(f"Error handling interaction: {e}")
                return {'status': 'error', 'message': str(e)}
        return {'status': 'error', 'message': 'Component not found'}
