"""
Integrated Visualization Manager

This module provides a unified interface for managing all visualization components
and coordinating data flow between the political strategy game and visualizations.
"""

import asyncio
from typing import Dict, List, Optional, Any, Type
from datetime import datetime
import json

from .base import (
    VisualizationComponent, VisualizationConfig, VisualizationUpdate,
    DataPoint, UpdateType, VisualizationManager, RealTimeDataProvider
)
from .network_graph import AdvisorNetworkVisualization
from .timeline import EventTimelineVisualization
from .dashboard import PoliticalDashboard
from .memory_browser import MemoryBrowserVisualization


class IntegratedVisualizationManager:
    """
    Manages all visualization components and provides a unified interface
    for the political strategy game to display real-time political data.
    """
    
    def __init__(self):
        self.components: Dict[str, VisualizationComponent] = {}
        self.data_provider: Optional[RealTimeDataProvider] = None
        self.base_manager: Optional[VisualizationManager] = None
        
        # Component registry
        self.component_types: Dict[str, Type[VisualizationComponent]] = {
            'advisor_network': AdvisorNetworkVisualization,
            'event_timeline': EventTimelineVisualization,
            'political_dashboard': PoliticalDashboard,
            'memory_browser': MemoryBrowserVisualization
        }
        
        # Cross-component data sharing
        self.shared_data: Dict[str, Any] = {}
        self.data_subscriptions: Dict[str, List[str]] = {}  # data_type -> component_ids
        
        # Event coordination
        self.event_queue: List[Dict[str, Any]] = []
        self.processing_events = False
        
        # Export capabilities
        self.export_handlers: Dict[str, callable] = {}
        
        # Integration status
        self.is_initialized = False
        self.active_components = set()
    
    async def initialize(self, game_interface: Any = None) -> bool:
        """
        Initialize the integrated visualization manager.
        
        Args:
            game_interface: Interface to the political strategy game
            
        Returns:
            True if initialization successful
        """
        try:
            # Initialize base manager
            self.base_manager = VisualizationManager()
            await self.base_manager.initialize()
            
            # Initialize data provider if game interface available
            if game_interface:
                self.data_provider = RealTimeDataProvider()
                await self.data_provider.initialize()
                
                # Connect to game interface
                await self._connect_game_interface(game_interface)
            
            # Initialize export handlers
            self._initialize_export_handlers()
            
            self.is_initialized = True
            print("Integrated visualization manager initialized successfully")
            return True
            
        except Exception as e:
            print(f"Failed to initialize integrated visualization manager: {e}")
            return False
    
    async def create_component(self, component_type: str, component_id: str, 
                             config: Dict[str, Any] = None) -> bool:
        """
        Create and register a visualization component.
        
        Args:
            component_type: Type of component to create
            component_id: Unique identifier for the component
            config: Configuration parameters for the component
            
        Returns:
            True if component created successfully
        """
        if component_type not in self.component_types:
            print(f"Unknown component type: {component_type}")
            return False
        
        if component_id in self.components:
            print(f"Component with ID {component_id} already exists")
            return False
        
        try:
            # Create configuration
            if config is None:
                config = {}
            
            vis_config = VisualizationConfig(
                component_id=component_id,
                component_type=component_type,
                layout_options=config.get('layout_options', {}),
                update_frequency=config.get('update_frequency', 1.0),
                real_time_enabled=config.get('real_time_enabled', True)
            )
            
            # Create component instance
            component_class = self.component_types[component_type]
            component = component_class(vis_config)
            
            # Initialize component
            if await component.initialize():
                self.components[component_id] = component
                self.active_components.add(component_id)
                
                # Subscribe component to relevant data
                await self._setup_component_subscriptions(component_id, component_type)
                
                print(f"Created {component_type} component: {component_id}")
                return True
            else:
                print(f"Failed to initialize {component_type} component: {component_id}")
                return False
                
        except Exception as e:
            print(f"Error creating component {component_id}: {e}")
            return False
    
    async def remove_component(self, component_id: str) -> bool:
        """
        Remove a visualization component.
        
        Args:
            component_id: ID of component to remove
            
        Returns:
            True if component removed successfully
        """
        if component_id not in self.components:
            return False
        
        try:
            # Stop component
            component = self.components[component_id]
            await component.stop()
            
            # Remove from registry
            del self.components[component_id]
            self.active_components.discard(component_id)
            
            # Remove data subscriptions
            for data_type, subscribers in self.data_subscriptions.items():
                if component_id in subscribers:
                    subscribers.remove(component_id)
            
            print(f"Removed component: {component_id}")
            return True
            
        except Exception as e:
            print(f"Error removing component {component_id}: {e}")
            return False
    
    async def update_all_components(self, data_points: List[DataPoint]) -> Dict[str, bool]:
        """
        Update all active components with new data.
        
        Args:
            data_points: List of data points to process
            
        Returns:
            Dictionary mapping component IDs to update success status
        """
        results = {}
        timestamp = datetime.now()
        
        # Group data points by type for efficient distribution
        data_by_type = {}
        for point in data_points:
            if point.data_type not in data_by_type:
                data_by_type[point.data_type] = []
            data_by_type[point.data_type].append(point)
        
        # Update shared data
        await self._update_shared_data(data_by_type)
        
        # Send updates to subscribed components
        for data_type, points in data_by_type.items():
            if data_type in self.data_subscriptions:
                for component_id in self.data_subscriptions[data_type]:
                    if component_id in self.active_components:
                        component = self.components[component_id]
                        
                        update = VisualizationUpdate(
                            update_type=UpdateType.INCREMENTAL_UPDATE,
                            data=points,
                            timestamp=timestamp,
                            source="integrated_manager"
                        )
                        
                        try:
                            success = await component.update(update)
                            results[component_id] = success
                        except Exception as e:
                            print(f"Error updating component {component_id}: {e}")
                            results[component_id] = False
        
        return results
    
    async def broadcast_event(self, event_data: Dict[str, Any]) -> None:
        """
        Broadcast an event to all relevant components.
        
        Args:
            event_data: Event data to broadcast
        """
        event_type = event_data.get('event_type', 'unknown')
        timestamp = datetime.now()
        
        # Create event data point
        event_point = DataPoint(
            data_type='real_time_event',
            value=event_data,
            timestamp=timestamp
        )
        
        # Send to all active components
        update = VisualizationUpdate(
            update_type=UpdateType.REAL_TIME_EVENT,
            data=[event_point],
            timestamp=timestamp,
            source="event_broadcast"
        )
        
        for component_id in self.active_components:
            component = self.components[component_id]
            try:
                await component.update(update)
            except Exception as e:
                print(f"Error broadcasting event to {component_id}: {e}")
    
    async def get_component_state(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current state of a visualization component.
        
        Args:
            component_id: ID of component to query
            
        Returns:
            Component state data or None if component not found
        """
        if component_id not in self.components:
            return None
        
        try:
            component = self.components[component_id]
            return await component.render()
        except Exception as e:
            print(f"Error getting state for component {component_id}: {e}")
            return None
    
    async def get_all_component_states(self) -> Dict[str, Any]:
        """
        Get current states of all active components.
        
        Returns:
            Dictionary mapping component IDs to their state data
        """
        states = {}
        
        for component_id in self.active_components:
            state = await self.get_component_state(component_id)
            if state:
                states[component_id] = state
        
        return states
    
    async def handle_component_interaction(self, component_id: str, 
                                         interaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle user interaction with a specific component.
        
        Args:
            component_id: ID of component receiving interaction
            interaction: Interaction data
            
        Returns:
            Interaction response or None if component not found
        """
        if component_id not in self.components:
            return {'status': 'error', 'message': 'Component not found'}
        
        try:
            component = self.components[component_id]
            result = await component.handle_interaction(interaction)
            
            # Check if interaction affects other components
            await self._handle_cross_component_effects(component_id, interaction, result)
            
            return result
            
        except Exception as e:
            print(f"Error handling interaction for {component_id}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def export_visualization_data(self, export_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export data from visualization components.
        
        Args:
            export_config: Export configuration
            
        Returns:
            Export result data
        """
        export_type = export_config.get('type', 'all')
        export_format = export_config.get('format', 'json')
        component_ids = export_config.get('components', list(self.active_components))
        
        if export_type in self.export_handlers:
            return await self.export_handlers[export_type](component_ids, export_format)
        else:
            return await self._default_export(component_ids, export_format)
    
    async def create_dashboard_layout(self, layout_config: Dict[str, Any]) -> str:
        """
        Create a pre-configured dashboard layout.
        
        Args:
            layout_config: Dashboard layout configuration
            
        Returns:
            Dashboard component ID
        """
        dashboard_id = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create dashboard component
        success = await self.create_component(
            component_type='political_dashboard',
            component_id=dashboard_id,
            config=layout_config
        )
        
        if success:
            return dashboard_id
        else:
            raise Exception("Failed to create dashboard layout")
    
    async def create_analysis_workspace(self, analysis_config: Dict[str, Any]) -> Dict[str, str]:
        """
        Create a complete analysis workspace with multiple components.
        
        Args:
            analysis_config: Analysis workspace configuration
            
        Returns:
            Dictionary mapping component types to their IDs
        """
        workspace_id = analysis_config.get('workspace_id', f"workspace_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        components_to_create = analysis_config.get('components', ['advisor_network', 'event_timeline', 'political_dashboard'])
        
        created_components = {}
        
        for component_type in components_to_create:
            component_id = f"{workspace_id}_{component_type}"
            component_config = analysis_config.get(component_type, {})
            
            success = await self.create_component(
                component_type=component_type,
                component_id=component_id,
                config=component_config
            )
            
            if success:
                created_components[component_type] = component_id
            else:
                print(f"Failed to create {component_type} component in workspace")
        
        return created_components
    
    async def _connect_game_interface(self, game_interface: Any) -> None:
        """Connect to the political strategy game interface."""
        # Set up data callbacks
        if hasattr(game_interface, 'register_visualization_callback'):
            await game_interface.register_visualization_callback(self._handle_game_data)
        
        # Set up event callbacks
        if hasattr(game_interface, 'register_event_callback'):
            await game_interface.register_event_callback(self._handle_game_event)
        
        print("Connected to game interface")
    
    async def _handle_game_data(self, data: Dict[str, Any]) -> None:
        """Handle data received from the game interface."""
        # Convert game data to data points
        data_points = []
        
        for data_type, value in data.items():
            point = DataPoint(
                data_type=data_type,
                value=value,
                timestamp=datetime.now()
            )
            data_points.append(point)
        
        # Update components
        await self.update_all_components(data_points)
    
    async def _handle_game_event(self, event: Dict[str, Any]) -> None:
        """Handle events received from the game interface."""
        await self.broadcast_event(event)
    
    async def _setup_component_subscriptions(self, component_id: str, component_type: str) -> None:
        """Set up data subscriptions for a component."""
        # Define which data types each component type subscribes to
        subscriptions = {
            'advisor_network': [
                'advisor_relationships', 'advisor_update', 'relationship_update',
                'advisor_added', 'advisor_removed', 'relationship_change',
                'loyalty_change', 'political_event'
            ],
            'event_timeline': [
                'political_events', 'event_added', 'event_updated', 'event_removed',
                'consequence_added', 'live_event', 'event_highlight'
            ],
            'political_dashboard': [
                'advisor_metrics', 'political_stability', 'military_status',
                'resource_status', 'diplomatic_status', 'cultural_metrics',
                'decision_results', 'crisis_event'
            ],
            'memory_browser': [
                'advisor_memories', 'memory_added', 'memory_updated', 'memory_removed',
                'memory_relationship_added', 'new_memory_formed', 'memory_recalled'
            ]
        }
        
        if component_type in subscriptions:
            for data_type in subscriptions[component_type]:
                if data_type not in self.data_subscriptions:
                    self.data_subscriptions[data_type] = []
                self.data_subscriptions[data_type].append(component_id)
    
    async def _update_shared_data(self, data_by_type: Dict[str, List[DataPoint]]) -> None:
        """Update shared data that can be accessed by all components."""
        for data_type, points in data_by_type.items():
            if data_type not in self.shared_data:
                self.shared_data[data_type] = []
            
            # Add new points and maintain reasonable history
            for point in points:
                self.shared_data[data_type].append({
                    'value': point.value,
                    'timestamp': point.timestamp.isoformat()
                })
            
            # Keep only recent data (last 1000 points)
            if len(self.shared_data[data_type]) > 1000:
                self.shared_data[data_type] = self.shared_data[data_type][-1000:]
    
    async def _handle_cross_component_effects(self, source_component: str, 
                                            interaction: Dict[str, Any], 
                                            result: Dict[str, Any]) -> None:
        """Handle effects of interactions that may affect other components."""
        interaction_type = interaction.get('type')
        
        # Example: Selection in one component highlights related data in others
        if interaction_type == 'node_click' and 'node_id' in result:
            # Broadcast selection event to other components
            await self.broadcast_event({
                'event_type': 'advisor_selected',
                'advisor_id': result['node_id'],
                'source_component': source_component
            })
        
        elif interaction_type == 'time_range_select':
            # Broadcast time range change to timeline-aware components
            await self.broadcast_event({
                'event_type': 'time_range_changed',
                'time_range': interaction.get('time_range'),
                'source_component': source_component
            })
    
    def _initialize_export_handlers(self) -> None:
        """Initialize export handlers for different export types."""
        self.export_handlers = {
            'network_data': self._export_network_data,
            'timeline_data': self._export_timeline_data,
            'dashboard_data': self._export_dashboard_data,
            'memory_data': self._export_memory_data,
            'complete_analysis': self._export_complete_analysis
        }
    
    async def _default_export(self, component_ids: List[str], export_format: str) -> Dict[str, Any]:
        """Default export handler for all component data."""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'export_format': export_format,
            'component_count': len(component_ids),
            'components': {}
        }
        
        for component_id in component_ids:
            if component_id in self.components:
                component_state = await self.get_component_state(component_id)
                if component_state:
                    export_data['components'][component_id] = component_state
        
        return {
            'status': 'success',
            'format': export_format,
            'data': export_data,
            'filename': f'visualization_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{export_format}'
        }
    
    async def _export_network_data(self, component_ids: List[str], export_format: str) -> Dict[str, Any]:
        """Export network visualization data."""
        network_components = [cid for cid in component_ids if 'network' in cid.lower()]
        
        if not network_components:
            return {'status': 'error', 'message': 'No network components found'}
        
        return await self._default_export(network_components, export_format)
    
    async def _export_timeline_data(self, component_ids: List[str], export_format: str) -> Dict[str, Any]:
        """Export timeline visualization data."""
        timeline_components = [cid for cid in component_ids if 'timeline' in cid.lower()]
        
        if not timeline_components:
            return {'status': 'error', 'message': 'No timeline components found'}
        
        return await self._default_export(timeline_components, export_format)
    
    async def _export_dashboard_data(self, component_ids: List[str], export_format: str) -> Dict[str, Any]:
        """Export dashboard visualization data."""
        dashboard_components = [cid for cid in component_ids if 'dashboard' in cid.lower()]
        
        if not dashboard_components:
            return {'status': 'error', 'message': 'No dashboard components found'}
        
        return await self._default_export(dashboard_components, export_format)
    
    async def _export_memory_data(self, component_ids: List[str], export_format: str) -> Dict[str, Any]:
        """Export memory browser data."""
        memory_components = [cid for cid in component_ids if 'memory' in cid.lower()]
        
        if not memory_components:
            return {'status': 'error', 'message': 'No memory components found'}
        
        return await self._default_export(memory_components, export_format)
    
    async def _export_complete_analysis(self, component_ids: List[str], export_format: str) -> Dict[str, Any]:
        """Export complete analysis including all component data and relationships."""
        complete_data = await self._default_export(component_ids, export_format)
        
        # Add cross-component analysis
        complete_data['data']['analysis'] = {
            'shared_data': self.shared_data,
            'data_subscriptions': self.data_subscriptions,
            'component_relationships': await self._analyze_component_relationships()
        }
        
        return complete_data
    
    async def _analyze_component_relationships(self) -> Dict[str, Any]:
        """Analyze relationships between components."""
        relationships = {
            'data_flow': {},
            'interaction_patterns': {},
            'temporal_correlations': {}
        }
        
        # Analyze data flow between components
        for data_type, subscribers in self.data_subscriptions.items():
            if len(subscribers) > 1:
                relationships['data_flow'][data_type] = subscribers
        
        return relationships
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current status of the visualization system."""
        return {
            'initialized': self.is_initialized,
            'total_components': len(self.components),
            'active_components': len(self.active_components),
            'component_types': list(self.component_types.keys()),
            'data_subscriptions': len(self.data_subscriptions),
            'shared_data_types': len(self.shared_data),
            'has_data_provider': self.data_provider is not None,
            'has_base_manager': self.base_manager is not None
        }
    
    async def shutdown(self) -> None:
        """Shutdown the visualization manager and all components."""
        print("Shutting down integrated visualization manager...")
        
        # Stop all components
        for component_id in list(self.active_components):
            await self.remove_component(component_id)
        
        # Stop data provider
        if self.data_provider:
            await self.data_provider.stop()
        
        # Stop base manager
        if self.base_manager:
            await self.base_manager.stop()
        
        self.is_initialized = False
        print("Visualization manager shutdown complete")


# Convenience function for easy initialization
async def create_political_visualization_system(game_interface: Any = None, 
                                              config: Dict[str, Any] = None) -> IntegratedVisualizationManager:
    """
    Create and initialize a complete political visualization system.
    
    Args:
        game_interface: Interface to the political strategy game
        config: System configuration
        
    Returns:
        Initialized IntegratedVisualizationManager
    """
    manager = IntegratedVisualizationManager()
    
    if await manager.initialize(game_interface):
        # Create default components if specified in config
        if config and 'default_components' in config:
            for component_type in config['default_components']:
                component_id = f"default_{component_type}"
                await manager.create_component(component_type, component_id)
        
        return manager
    else:
        raise Exception("Failed to initialize political visualization system")
