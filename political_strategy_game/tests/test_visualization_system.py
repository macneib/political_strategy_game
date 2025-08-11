"""
Test suite for the Political Visualization System

Tests all visualization components and integration functionality.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import visualization components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from visualization import (
    VisualizationConfig, VisualizationUpdate, DataPoint, UpdateType,
    AdvisorNetworkVisualization, EventTimelineVisualization,
    PoliticalDashboard, MemoryBrowserVisualization,
    IntegratedVisualizationManager, create_political_visualization_system
)


class TestVisualizationComponents:
    """Test individual visualization components."""
    
    @pytest.fixture
    def basic_config(self):
        """Basic configuration for testing."""
        return VisualizationConfig(
            component_id="test_component",
            component_type="test",
            layout_options={'width': 800, 'height': 600},
            update_frequency=1.0,
            real_time_enabled=True
        )
    
    @pytest.fixture
    def sample_advisor_data(self):
        """Sample advisor data for testing."""
        return [
            DataPoint(
                data_type='advisor_relationships',
                value={
                    'advisors': [
                        {
                            'advisor_id': 'advisor_1',
                            'name': 'Military Commander',
                            'role': 'military',
                            'loyalty': 0.8,
                            'influence': 0.7,
                            'stress_level': 0.3,
                            'current_mood': 'confident'
                        },
                        {
                            'advisor_id': 'advisor_2',
                            'name': 'Economic Minister',
                            'role': 'economic',
                            'loyalty': 0.6,
                            'influence': 0.9,
                            'stress_level': 0.5,
                            'current_mood': 'concerned'
                        }
                    ],
                    'relationships': [
                        {
                            'source_id': 'advisor_1',
                            'target_id': 'advisor_2',
                            'strength': 0.4,
                            'type': 'professional'
                        }
                    ]
                },
                timestamp=datetime.now()
            )
        ]
    
    @pytest.fixture
    def sample_event_data(self):
        """Sample event data for testing."""
        return [
            DataPoint(
                data_type='political_events',
                value=[
                    {
                        'event_id': 'event_1',
                        'title': 'Trade Agreement Signed',
                        'category': 'diplomatic',
                        'severity': 0.3,
                        'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                        'participants': ['advisor_2'],
                        'description': 'Successfully negotiated trade agreement with neighboring nation',
                        'consequences': ['Increased economic stability']
                    },
                    {
                        'event_id': 'event_2',
                        'title': 'Military Exercise',
                        'category': 'military',
                        'severity': 0.6,
                        'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                        'participants': ['advisor_1'],
                        'description': 'Large-scale military exercise conducted',
                        'consequences': ['Improved military readiness']
                    }
                ],
                timestamp=datetime.now()
            )
        ]
    
    @pytest.mark.asyncio
    async def test_advisor_network_initialization(self, basic_config):
        """Test advisor network visualization initialization."""
        network = AdvisorNetworkVisualization(basic_config)
        assert await network.initialize()
        assert network.is_active
        await network.stop()
    
    @pytest.mark.asyncio
    async def test_advisor_network_update(self, basic_config, sample_advisor_data):
        """Test advisor network data updates."""
        network = AdvisorNetworkVisualization(basic_config)
        await network.initialize()
        
        update = VisualizationUpdate(
            update_type=UpdateType.FULL_REFRESH,
            data=sample_advisor_data,
            timestamp=datetime.now(),
            source="test"
        )
        
        assert await network.update(update)
        
        # Check that data was processed
        render_data = await network.render()
        assert render_data['type'] == 'network_graph'
        assert 'data' in render_data
        assert len(render_data['data']['nodes']) == 2
        assert len(render_data['data']['links']) == 1
        
        await network.stop()
    
    @pytest.mark.asyncio
    async def test_advisor_network_interaction(self, basic_config, sample_advisor_data):
        """Test advisor network user interactions."""
        network = AdvisorNetworkVisualization(basic_config)
        await network.initialize()
        
        # Add test data
        update = VisualizationUpdate(
            update_type=UpdateType.FULL_REFRESH,
            data=sample_advisor_data,
            timestamp=datetime.now(),
            source="test"
        )
        await network.update(update)
        
        # Test node click interaction
        interaction = {
            'type': 'node_click',
            'node_id': 'advisor_1'
        }
        
        result = await network.handle_interaction(interaction)
        assert result['status'] == 'success'
        assert result['node_id'] == 'advisor_1'
        
        await network.stop()
    
    @pytest.mark.asyncio
    async def test_event_timeline_initialization(self, basic_config):
        """Test event timeline visualization initialization."""
        timeline = EventTimelineVisualization(basic_config)
        assert await timeline.initialize()
        assert timeline.is_active
        await timeline.stop()
    
    @pytest.mark.asyncio
    async def test_event_timeline_update(self, basic_config, sample_event_data):
        """Test event timeline data updates."""
        timeline = EventTimelineVisualization(basic_config)
        await timeline.initialize()
        
        update = VisualizationUpdate(
            update_type=UpdateType.FULL_REFRESH,
            data=sample_event_data,
            timestamp=datetime.now(),
            source="test"
        )
        
        assert await timeline.update(update)
        
        # Check that data was processed
        render_data = await timeline.render()
        assert render_data['type'] == 'event_timeline'
        assert 'data' in render_data
        assert len(render_data['data']['events']) == 2
        
        await timeline.stop()
    
    @pytest.mark.asyncio
    async def test_political_dashboard_initialization(self, basic_config):
        """Test political dashboard initialization."""
        dashboard = PoliticalDashboard(basic_config)
        assert await dashboard.initialize()
        assert dashboard.is_active
        await dashboard.stop()
    
    @pytest.mark.asyncio
    async def test_political_dashboard_widgets(self, basic_config):
        """Test political dashboard widget creation and updates."""
        dashboard = PoliticalDashboard(basic_config)
        await dashboard.initialize()
        
        # Test that default widgets were created
        render_data = await dashboard.render()
        assert render_data['type'] == 'political_dashboard'
        assert len(render_data['widgets']) > 0
        
        # Find loyalty gauge widget
        loyalty_widget = None
        for widget in render_data['widgets']:
            if widget['widget_id'] == 'loyalty_gauge':
                loyalty_widget = widget
                break
        
        assert loyalty_widget is not None
        assert loyalty_widget['type'] == 'gauge'
        
        await dashboard.stop()
    
    @pytest.mark.asyncio
    async def test_memory_browser_initialization(self, basic_config):
        """Test memory browser visualization initialization."""
        browser = MemoryBrowserVisualization(basic_config)
        assert await browser.initialize()
        assert browser.is_active
        await browser.stop()
    
    @pytest.mark.asyncio
    async def test_memory_browser_search(self, basic_config):
        """Test memory browser search functionality."""
        browser = MemoryBrowserVisualization(basic_config)
        await browser.initialize()
        
        # Add sample memory
        memory_data = [
            DataPoint(
                data_type='advisor_memories',
                value=[
                    {
                        'memory_id': 'memory_1',
                        'advisor_id': 'advisor_1',
                        'title': 'Victory in Battle',
                        'content': 'Led troops to victory against overwhelming odds',
                        'memory_type': 'personal_experience',
                        'importance': 'high',
                        'emotional_tone': 'positive',
                        'timestamp': datetime.now().isoformat(),
                        'tags': ['battle', 'victory', 'leadership'],
                        'participants': ['advisor_1'],
                        'related_memories': [],
                        'metadata': {}
                    }
                ],
                timestamp=datetime.now()
            )
        ]
        
        update = VisualizationUpdate(
            update_type=UpdateType.FULL_REFRESH,
            data=memory_data,
            timestamp=datetime.now(),
            source="test"
        )
        
        await browser.update(update)
        
        # Test search
        search_interaction = {
            'type': 'search',
            'search_text': 'victory'
        }
        
        result = await browser.handle_interaction(search_interaction)
        assert result['status'] == 'success'
        assert result['results_count'] == 1
        
        await browser.stop()


class TestIntegratedVisualizationManager:
    """Test the integrated visualization manager."""
    
    @pytest.mark.asyncio
    async def test_manager_initialization(self):
        """Test manager initialization."""
        manager = IntegratedVisualizationManager()
        assert await manager.initialize()
        assert manager.is_initialized
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_component_creation(self):
        """Test creating components through the manager."""
        manager = IntegratedVisualizationManager()
        await manager.initialize()
        
        # Create advisor network component
        success = await manager.create_component(
            component_type='advisor_network',
            component_id='test_network',
            config={'layout_options': {'width': 800, 'height': 600}}
        )
        
        assert success
        assert 'test_network' in manager.components
        assert 'test_network' in manager.active_components
        
        # Test component state retrieval
        state = await manager.get_component_state('test_network')
        assert state is not None
        assert state['type'] == 'network_graph'
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_multiple_component_coordination(self):
        """Test coordination between multiple components."""
        manager = IntegratedVisualizationManager()
        await manager.initialize()
        
        # Create multiple components
        components = [
            ('advisor_network', 'network_1'),
            ('event_timeline', 'timeline_1'),
            ('political_dashboard', 'dashboard_1')
        ]
        
        for component_type, component_id in components:
            success = await manager.create_component(component_type, component_id)
            assert success
        
        # Test updating all components
        sample_data = [
            DataPoint(
                data_type='advisor_metrics',
                value={
                    'advisors': [
                        {
                            'advisor_id': 'advisor_1',
                            'loyalty': 0.8,
                            'influence': 0.7
                        }
                    ]
                },
                timestamp=datetime.now()
            )
        ]
        
        results = await manager.update_all_components(sample_data)
        assert len(results) > 0
        
        # Test getting all component states
        all_states = await manager.get_all_component_states()
        assert len(all_states) == 3
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_event_broadcasting(self):
        """Test event broadcasting to all components."""
        manager = IntegratedVisualizationManager()
        await manager.initialize()
        
        # Create a component
        await manager.create_component('advisor_network', 'test_network')
        
        # Broadcast an event
        event_data = {
            'event_type': 'advisor_selected',
            'advisor_id': 'advisor_1',
            'timestamp': datetime.now().isoformat()
        }
        
        # This should not raise an exception
        await manager.broadcast_event(event_data)
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_workspace_creation(self):
        """Test creating complete analysis workspace."""
        manager = IntegratedVisualizationManager()
        await manager.initialize()
        
        workspace_config = {
            'workspace_id': 'test_workspace',
            'components': ['advisor_network', 'event_timeline'],
            'advisor_network': {'layout_options': {'algorithm': 'force_directed'}},
            'event_timeline': {'layout_options': {'height': 400}}
        }
        
        created_components = await manager.create_analysis_workspace(workspace_config)
        
        assert len(created_components) == 2
        assert 'advisor_network' in created_components
        assert 'event_timeline' in created_components
        
        # Verify components were actually created
        for component_id in created_components.values():
            assert component_id in manager.active_components
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_data_export(self):
        """Test data export functionality."""
        manager = IntegratedVisualizationManager()
        await manager.initialize()
        
        # Create a component with some data
        await manager.create_component('advisor_network', 'test_network')
        
        # Test export
        export_config = {
            'type': 'all',
            'format': 'json',
            'components': ['test_network']
        }
        
        export_result = await manager.export_visualization_data(export_config)
        
        assert export_result['status'] == 'success'
        assert export_result['format'] == 'json'
        assert 'data' in export_result
        
        await manager.shutdown()


class TestVisualizationSystemIntegration:
    """Test complete system integration."""
    
    @pytest.mark.asyncio
    async def test_complete_system_creation(self):
        """Test creating a complete visualization system."""
        system_config = {
            'default_components': ['advisor_network', 'political_dashboard']
        }
        
        system = await create_political_visualization_system(config=system_config)
        
        assert system.is_initialized
        assert len(system.active_components) == 2
        
        # Test system status
        status = system.get_system_status()
        assert status['initialized']
        assert status['total_components'] == 2
        assert status['active_components'] == 2
        
        await system.shutdown()
    
    @pytest.mark.asyncio
    async def test_real_time_data_flow(self):
        """Test real-time data flow through the system."""
        system = await create_political_visualization_system()
        
        # Create components
        await system.create_component('advisor_network', 'network')
        await system.create_component('event_timeline', 'timeline')
        
        # Simulate real-time data updates
        for i in range(5):
            data_points = [
                DataPoint(
                    data_type='advisor_update',
                    value={
                        'advisor_id': f'advisor_{i}',
                        'loyalty': 0.5 + (i * 0.1),
                        'influence': 0.4 + (i * 0.1)
                    },
                    timestamp=datetime.now()
                )
            ]
            
            results = await system.update_all_components(data_points)
            assert len(results) > 0
            
            # Small delay to simulate real-time updates
            await asyncio.sleep(0.01)
        
        await system.shutdown()
    
    @pytest.mark.asyncio
    async def test_component_interaction_effects(self):
        """Test how interactions in one component affect others."""
        system = await create_political_visualization_system()
        
        # Create multiple components
        await system.create_component('advisor_network', 'network')
        await system.create_component('memory_browser', 'memory')
        
        # Simulate interaction in network component
        interaction = {
            'type': 'node_click',
            'node_id': 'advisor_1'
        }
        
        # Handle interaction (this tests cross-component effects)
        result = await system.handle_component_interaction('network', interaction)
        
        # The interaction should be handled even if the component has no data yet
        assert result is not None
        
        await system.shutdown()


# Mock game interface for testing
class MockGameInterface:
    """Mock game interface for testing visualization integration."""
    
    def __init__(self):
        self.visualization_callback = None
        self.event_callback = None
    
    async def register_visualization_callback(self, callback):
        """Register callback for visualization data."""
        self.visualization_callback = callback
    
    async def register_event_callback(self, callback):
        """Register callback for game events."""
        self.event_callback = callback
    
    async def send_test_data(self):
        """Send test data to visualization system."""
        if self.visualization_callback:
            test_data = {
                'advisor_metrics': {
                    'advisors': [
                        {'advisor_id': 'test_advisor', 'loyalty': 0.7, 'influence': 0.6}
                    ]
                }
            }
            await self.visualization_callback(test_data)
    
    async def send_test_event(self):
        """Send test event to visualization system."""
        if self.event_callback:
            test_event = {
                'event_type': 'political_crisis',
                'severity': 0.8,
                'affected_advisors': ['test_advisor']
            }
            await self.event_callback(test_event)


class TestGameIntegration:
    """Test integration with game interface."""
    
    @pytest.mark.asyncio
    async def test_game_interface_connection(self):
        """Test connecting to a mock game interface."""
        game_interface = MockGameInterface()
        
        system = await create_political_visualization_system(game_interface=game_interface)
        
        # Create a component to receive data
        await system.create_component('political_dashboard', 'dashboard')
        
        # Send test data through game interface
        await game_interface.send_test_data()
        
        # Verify data was received and processed
        # (In a real test, we'd verify the component state was updated)
        
        await system.shutdown()


if __name__ == "__main__":
    # Run basic tests
    async def run_basic_tests():
        """Run basic functionality tests."""
        print("Running basic visualization system tests...")
        
        # Test component creation
        manager = IntegratedVisualizationManager()
        await manager.initialize()
        
        # Create all component types
        component_types = ['advisor_network', 'event_timeline', 'political_dashboard', 'memory_browser']
        
        for i, component_type in enumerate(component_types):
            component_id = f"test_{component_type}_{i}"
            success = await manager.create_component(component_type, component_id)
            print(f"Created {component_type}: {'✓' if success else '✗'}")
        
        # Test system status
        status = manager.get_system_status()
        print(f"System initialized: {'✓' if status['initialized'] else '✗'}")
        print(f"Active components: {status['active_components']}")
        
        # Test data update
        sample_data = [
            DataPoint(
                data_type='advisor_metrics',
                value={'test': 'data'},
                timestamp=datetime.now()
            )
        ]
        
        results = await manager.update_all_components(sample_data)
        print(f"Data update results: {len(results)} components updated")
        
        await manager.shutdown()
        print("Basic tests completed successfully!")
    
    # Run the basic tests
    asyncio.run(run_basic_tests())
