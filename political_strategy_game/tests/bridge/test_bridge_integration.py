"""
Integration tests for the Game Engine Bridge system.
"""

import asyncio
import json
import pytest
import time
import threading
import websockets
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.bridge import (
    MessageType, GameState, CivilizationState, AdvisorState, 
    TurnState, PoliticalEvent, EventPriority
)
from src.bridge.event_broadcaster import SubscriptionFilter, EventCategory
from src.bridge.bridge_manager import GameEngineBridgeManager
from src.bridge.game_engine_bridge import GameEngineBridge
from src.bridge.turn_synchronizer import TurnSynchronizer
from src.bridge.state_serializer import GameStateSerializer
from src.bridge.event_broadcaster import PoliticalEventBroadcaster
from src.bridge.performance_profiler import PerformanceProfiler


@pytest.fixture
def sample_game_state():
    """Create a sample game state for testing."""
    turn_state = TurnState(
        turn_number=1,
        civilization_id="test_civ",
        phase="planning"
    )
    
    civilization = CivilizationState(
        civilization_id="test_civ",
        name="Test Civilization",
        leader_name="Test Leader",
        political_stability=0.8,
        economic_strength=0.7,
        military_power=0.6,
        diplomatic_relations={"ally_civ": 0.9, "enemy_civ": -0.5},
        active_crises=["crisis_1"],
        active_conspiracies=["conspiracy_1"],
        recent_events=[]
    )
    
    advisor = AdvisorState(
        advisor_id="advisor_1",
        name="Test Advisor",
        role="military",
        loyalty=0.9,
        influence=0.8,
        stress_level=0.3,
        current_mood="confident",
        personality_traits={"aggressive": 0.7, "cautious": 0.3},
        relationships={"advisor_2": 0.6}
    )
    
    return GameState(
        turn_state=turn_state,
        civilizations=[civilization],
        advisors=[advisor],
        global_events=[],
        metadata={"test": True}
    )


@pytest.fixture
def sample_political_event():
    """Create a sample political event for testing."""
    return PoliticalEvent(
        event_id="event_1",
        event_type="advisor_loyalty_change",
        civilization_id="test_civ",
        title="Advisor Loyalty Changed",
        description="An advisor's loyalty has shifted due to recent events",
        severity="moderate",
        participants=["advisor_1"],
        consequences={"loyalty_change": -0.1},
        timestamp=datetime.now()
    )


class TestGameEngineBridge:
    """Test the core game engine bridge functionality."""
    
    @pytest.mark.asyncio
    async def test_bridge_startup_shutdown(self):
        """Test bridge startup and shutdown."""
        bridge = GameEngineBridge(port=8889)  # Use different port for testing
        
        # Start bridge in background thread
        start_task = asyncio.create_task(bridge.start_server())
        await asyncio.sleep(0.5)  # Give it time to start
        
        assert bridge.connection_status.value in ["connected", "connecting"]
        
        # Stop bridge
        bridge.stop()
        start_task.cancel()
        
        try:
            await start_task
        except asyncio.CancelledError:
            pass
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection to bridge."""
        bridge = GameEngineBridge(port=8890)
        bridge.start()
        
        await asyncio.sleep(0.5)  # Give bridge time to start
        
        try:
            # Connect via WebSocket
            uri = "ws://localhost:8890"
            async with websockets.connect(uri) as websocket:
                # Should receive handshake
                response = await websocket.recv()
                message_data = json.loads(response)
                
                assert message_data['header']['message_type'] == MessageType.HANDSHAKE.value
                assert message_data['payload']['api_version'] == "1.0"
                
        finally:
            bridge.stop()


class TestTurnSynchronizer:
    """Test turn synchronization functionality."""
    
    def test_turn_synchronizer_initialization(self):
        """Test turn synchronizer initialization."""
        sync = TurnSynchronizer()
        
        assert sync.current_state.turn_number == 1
        assert sync.current_state.phase.value == "planning"
        assert sync.current_state.political_engine_ready == True
        assert sync.current_state.game_engine_ready == False
    
    def test_turn_advancement(self):
        """Test turn advancement logic."""
        sync = TurnSynchronizer(auto_advance=False)
        sync.start()
        
        try:
            # Set both engines ready
            sync.set_political_engine_ready(True)
            sync.set_game_engine_ready(True)
            
            # Advance turn
            success = sync.advance_turn()
            assert success == True
            assert sync.current_state.turn_number == 2
            
            # Check that readiness was reset
            assert sync.current_state.political_engine_ready == False
            assert sync.current_state.game_engine_ready == False
            
        finally:
            sync.stop()
    
    def test_phase_advancement(self):
        """Test phase advancement logic."""
        sync = TurnSynchronizer()
        sync.start()
        
        try:
            # Set both engines ready
            sync.set_political_engine_ready(True)
            sync.set_game_engine_ready(True)
            
            # Advance phase
            success = sync.advance_phase()
            assert success == True
            assert sync.current_state.phase.value == "execution"
            
        finally:
            sync.stop()


class TestStateSerializer:
    """Test game state serialization functionality."""
    
    def test_full_state_serialization(self, sample_game_state):
        """Test full state serialization and deserialization."""
        serializer = GameStateSerializer()
        
        # Serialize state
        serialized = serializer.serialize_full_state(sample_game_state)
        
        assert 'metadata' in serialized
        assert 'state' in serialized
        assert serialized['metadata']['incremental'] == False
        
        # Deserialize state
        deserialized = serializer.deserialize_full_state(serialized)
        
        assert deserialized.turn_state.turn_number == sample_game_state.turn_state.turn_number
        assert len(deserialized.civilizations) == len(sample_game_state.civilizations)
        assert len(deserialized.advisors) == len(sample_game_state.advisors)
    
    def test_incremental_update(self, sample_game_state):
        """Test incremental state update generation."""
        serializer = GameStateSerializer()
        
        # Set initial state
        serializer.serialize_full_state(sample_game_state)
        
        # Modify state
        modified_state = sample_game_state
        modified_state.advisors[0].loyalty = 0.5  # Change loyalty
        modified_state.turn_state.turn_number = 2  # Change turn
        
        # Create incremental update
        update = serializer.create_incremental_update(modified_state)
        
        assert update is not None
        assert len(update.changes) > 0
        assert update.metadata.incremental == True
        
        # Apply update to original state
        updated_state = serializer.apply_incremental_update(sample_game_state, update)
        assert updated_state.advisors[0].loyalty == 0.5
        assert updated_state.turn_state.turn_number == 2
    
    def test_state_validation(self, sample_game_state):
        """Test game state validation."""
        serializer = GameStateSerializer()
        
        # Valid state should have no errors
        errors = serializer.validate_state(sample_game_state)
        assert len(errors) == 0
        
        # Invalid state should have errors
        invalid_state = sample_game_state
        invalid_state.advisors[0].loyalty = 2.0  # Invalid loyalty > 1.0
        
        errors = serializer.validate_state(invalid_state)
        assert len(errors) > 0


class TestEventBroadcaster:
    """Test political event broadcasting functionality."""
    
    def test_event_broadcaster_initialization(self):
        """Test event broadcaster initialization."""
        broadcaster = PoliticalEventBroadcaster()
        
        assert broadcaster.max_event_history == 10000
        assert broadcaster.batch_size == 10
        assert len(broadcaster.event_history) == 0
    
    def test_event_subscription(self):
        """Test event subscription and filtering."""
        broadcaster = PoliticalEventBroadcaster()
        
        # Create subscription filter
        filter = SubscriptionFilter(
            categories=[EventCategory.ADVISOR],
            severities=["moderate", "major"],
            civilizations=["test_civ"]
        )
        
        # Subscribe
        sub_id = broadcaster.subscribe_to_events("client_1", filter)
        assert sub_id is not None
        assert len(broadcaster.subscriptions) == 1
        
        # Unsubscribe
        success = broadcaster.unsubscribe_from_events(sub_id)
        assert success == True
        assert len(broadcaster.subscriptions) == 0
    
    def test_event_filtering(self, sample_political_event):
        """Test event filtering logic."""
        filter = SubscriptionFilter(
            severities=["moderate"],
            civilizations=["test_civ"]
        )
        
        # Event should match filter
        assert filter.matches(sample_political_event) == True
        
        # Event should not match different filter
        strict_filter = SubscriptionFilter(
            severities=["critical"],
            civilizations=["other_civ"]
        )
        assert strict_filter.matches(sample_political_event) == False


class TestPerformanceProfiler:
    """Test performance profiling functionality."""
    
    def test_profiler_initialization(self):
        """Test performance profiler initialization."""
        profiler = PerformanceProfiler()
        
        assert profiler.measurement_interval == 1.0
        assert profiler.history_size == 1000
        assert len(profiler.alert_thresholds) > 0
    
    def test_turn_profiling(self):
        """Test turn performance profiling."""
        profiler = PerformanceProfiler()
        
        # Start turn profiling
        profiler.start_turn_profiling(1)
        assert profiler.current_turn_profile is not None
        assert profiler.current_turn_profile.turn_number == 1
        
        # Add some data
        profiler.record_phase_duration("planning", 2.5)
        profiler.increment_event_count(5)
        profiler.increment_message_count(10)
        
        # End turn profiling
        time.sleep(0.1)  # Brief delay to ensure duration > 0
        profiler.end_turn_profiling()
        
        assert len(profiler.turn_profiles) == 1
        assert profiler.turn_profiles[0].phase_durations["planning"] == 2.5
        assert profiler.turn_profiles[0].event_count == 5
        assert profiler.turn_profiles[0].message_count == 10
    
    def test_operation_timing(self):
        """Test operation timing functionality."""
        profiler = PerformanceProfiler()
        
        # Time an operation
        profiler.start_operation_timer("test_operation")
        time.sleep(0.1)
        duration = profiler.end_operation_timer("test_operation")
        
        assert duration is not None
        assert duration >= 0.1
        
        # Get operation statistics
        stats = profiler.get_operation_stats("test_operation")
        assert stats['count'] == 1
        assert stats['mean'] >= 0.1


class TestBridgeManagerIntegration:
    """Test the complete bridge manager integration."""
    
    @pytest.mark.asyncio
    async def test_bridge_manager_lifecycle(self):
        """Test bridge manager complete lifecycle."""
        manager = GameEngineBridgeManager(
            port=8891,
            enable_performance_monitoring=True
        )
        
        try:
            # Start manager
            await manager.start()
            assert manager.running == True
            
            # Check status
            status = manager.get_bridge_status()
            assert 'running' in status
            assert status['running'] == True
            
            # Get diagnostics
            diagnostics = manager.get_diagnostics()
            assert 'bridge_manager' in diagnostics
            assert 'components' in diagnostics
            
        finally:
            await manager.stop()
            assert manager.running == False
    
    @pytest.mark.asyncio 
    async def test_game_state_update(self, sample_game_state):
        """Test game state update through bridge manager."""
        manager = GameEngineBridgeManager(port=8892)
        
        try:
            await manager.start()
            
            # Update game state
            manager.update_game_state(sample_game_state)
            assert manager.current_game_state is not None
            assert manager.current_game_state.turn_state.turn_number == 1
            
        finally:
            await manager.stop()
    
    @pytest.mark.asyncio
    async def test_political_event_broadcast(self, sample_political_event):
        """Test political event broadcasting through bridge manager."""
        manager = GameEngineBridgeManager(port=8893)
        
        try:
            await manager.start()
            
            # Broadcast event
            manager.broadcast_political_event(sample_political_event, EventPriority.HIGH)
            
            # Check that event was processed
            await asyncio.sleep(0.1)  # Give event time to process
            
            # Verify event is in broadcaster history
            assert len(manager.event_broadcaster.event_history) > 0
            assert manager.event_broadcaster.event_history[0].event_id == sample_political_event.event_id
            
        finally:
            await manager.stop()
    
    @pytest.mark.asyncio
    async def test_turn_management(self):
        """Test turn management through bridge manager."""
        manager = GameEngineBridgeManager(port=8894)
        
        try:
            await manager.start()
            
            # Start new turn
            manager.start_new_turn(5)
            assert manager.turn_synchronizer.current_state.turn_number == 5
            
            # Set political engine ready
            manager.set_political_engine_ready(True)
            assert manager.turn_synchronizer.current_state.political_engine_ready == True
            
            # End turn
            manager.end_current_turn()
            
        finally:
            await manager.stop()


class TestWebSocketClientSimulation:
    """Test bridge functionality with simulated WebSocket clients."""
    
    @pytest.mark.asyncio
    async def test_client_connection_and_messaging(self):
        """Test client connection and basic messaging."""
        manager = GameEngineBridgeManager(port=8895)
        
        try:
            await manager.start()
            await asyncio.sleep(0.5)  # Give bridge time to start
            
            # Connect as client
            uri = "ws://localhost:8895"
            async with websockets.connect(uri) as websocket:
                # Should receive handshake
                handshake_response = await websocket.recv()
                handshake_data = json.loads(handshake_response)
                
                assert handshake_data['header']['message_type'] == MessageType.HANDSHAKE.value
                
                # Send heartbeat
                heartbeat_message = {
                    'header': {
                        'message_id': 'test_heartbeat',
                        'message_type': MessageType.HEARTBEAT.value,
                        'timestamp': datetime.now().isoformat(),
                        'sender': 'game_engine',
                        'recipient': 'political_engine',
                        'priority': EventPriority.LOW.value,
                        'api_version': '1.0'
                    },
                    'payload': {
                        'status': 'alive',
                        'timestamp': datetime.now().isoformat()
                    }
                }
                
                await websocket.send(json.dumps(heartbeat_message))
                
                # Wait briefly for processing
                await asyncio.sleep(0.1)
                
        finally:
            await manager.stop()


if __name__ == "__main__":
    # Run specific tests for debugging
    pytest.main([__file__, "-v", "-s"])
