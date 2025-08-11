"""
Game Engine Bridge - Main Integration Module

This module provides the main GameEngineBridgeManager that integrates all
bridge components and provides a unified interface for game engine communication.
"""

import asyncio
import logging
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

from . import (
    GameState, CivilizationState, AdvisorState, TurnState, PoliticalEvent,
    MessageType, EventPriority
)
from .game_engine_bridge import GameEngineBridge
from .turn_synchronizer import TurnSynchronizer
from .state_serializer import GameStateSerializer
from .event_broadcaster import PoliticalEventBroadcaster, SubscriptionFilter
from .performance_profiler import PerformanceProfiler


class GameEngineBridgeManager:
    """
    Main bridge manager that coordinates all bridge components and provides
    a unified interface for game engine communication.
    """
    
    def __init__(self,
                 host: str = "localhost",
                 port: int = 8888,
                 auto_advance_turns: bool = False,
                 enable_performance_monitoring: bool = True):
        """
        Initialize the bridge manager.
        
        Args:
            host: Server host address
            port: Server port number
            auto_advance_turns: Whether to automatically advance turns
            enable_performance_monitoring: Whether to enable performance monitoring
        """
        self.host = host
        self.port = port
        self.auto_advance_turns = auto_advance_turns
        self.enable_performance_monitoring = enable_performance_monitoring
        
        # Initialize components
        self.bridge = GameEngineBridge(host=host, port=port)
        self.turn_synchronizer = TurnSynchronizer(auto_advance=auto_advance_turns)
        self.state_serializer = GameStateSerializer()
        self.event_broadcaster = PoliticalEventBroadcaster()
        
        if enable_performance_monitoring:
            self.performance_profiler = PerformanceProfiler()
        else:
            self.performance_profiler = None
        
        # State management
        self.current_game_state: Optional[GameState] = None
        self.connected_clients: Dict[str, Dict[str, Any]] = {}
        
        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = {}
        
        # Integration state
        self.running = False
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Setup component integration
        self._setup_component_integration()
        
        self.logger.info("Game Engine Bridge Manager initialized")
    
    def _setup_component_integration(self):
        """Set up integration between bridge components."""
        # Bridge event subscriptions
        self.bridge.subscribe_to_event("player_decision", self._handle_player_decision)
        self.bridge.subscribe_to_event("advisor_appointment", self._handle_advisor_appointment)
        self.bridge.subscribe_to_event("advisor_dismissal", self._handle_advisor_dismissal)
        self.bridge.subscribe_to_event("turn_advance", self._handle_turn_advance_request)
        self.bridge.subscribe_to_event("state_request", self._handle_state_request)
        
        # Turn synchronizer event subscriptions
        self.turn_synchronizer.subscribe_to_event("turn_advanced", self._handle_turn_advanced)
        self.turn_synchronizer.subscribe_to_event("phase_advanced", self._handle_phase_advanced)
        self.turn_synchronizer.subscribe_to_event("timeout_occurred", self._handle_turn_timeout)
        
        # Event broadcaster integration
        self.event_broadcaster.register_broadcast_callback(self._broadcast_event_message)
        
        # Performance profiler integration
        if self.performance_profiler:
            self.performance_profiler.register_alert_callback(self._handle_performance_alert)
    
    async def start(self):
        """Start the bridge manager and all components."""
        if self.running:
            return
        
        try:
            self.logger.info("Starting Game Engine Bridge Manager")
            
            # Start performance monitoring
            if self.performance_profiler:
                self.performance_profiler.start_monitoring()
            
            # Start event broadcaster
            self.event_broadcaster.start()
            
            # Start turn synchronizer
            self.turn_synchronizer.start()
            
            # Start main bridge server
            self.bridge.start()
            
            self.running = True
            
            self.logger.info("Game Engine Bridge Manager started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start Bridge Manager: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the bridge manager and all components."""
        self.logger.info("Stopping Game Engine Bridge Manager")
        
        self.running = False
        
        # Stop components in reverse order
        self.bridge.stop()
        self.turn_synchronizer.stop()
        self.event_broadcaster.stop()
        
        if self.performance_profiler:
            self.performance_profiler.stop_monitoring()
        
        self.logger.info("Game Engine Bridge Manager stopped")
    
    # Game state management
    def update_game_state(self, game_state: GameState):
        """
        Update the current game state and broadcast changes.
        
        Args:
            game_state: New game state
        """
        try:
            # Start performance timing
            if self.performance_profiler:
                self.performance_profiler.start_operation_timer("state_update")
            
            # Create incremental update if possible
            incremental_update = None
            if self.current_game_state:
                incremental_update = self.state_serializer.create_incremental_update(game_state)
            
            # Update current state
            self.current_game_state = game_state
            
            # Broadcast full state sync if no incremental update
            if incremental_update is None:
                self.bridge.queue_game_state_sync(game_state)
            else:
                # TODO: Implement incremental update broadcasting
                # For now, send full state
                self.bridge.queue_game_state_sync(game_state)
            
            # End performance timing
            if self.performance_profiler:
                duration = self.performance_profiler.end_operation_timer("state_update")
                if duration and duration > 1.0:  # Log slow updates
                    self.logger.warning(f"Slow state update: {duration:.2f}s")
            
            self.logger.debug("Game state updated and queued for broadcast")
            
        except Exception as e:
            self.logger.error(f"Failed to update game state: {e}")
    
    def broadcast_political_event(self, event: PoliticalEvent, priority: EventPriority = EventPriority.NORMAL):
        """
        Broadcast a political event to connected game engines.
        
        Args:
            event: Political event to broadcast
            priority: Event priority
        """
        try:
            # Performance tracking
            if self.performance_profiler:
                self.performance_profiler.increment_event_count()
            
            # Broadcast via event broadcaster
            self.event_broadcaster.broadcast_event(event, priority)
            
            self.logger.debug(f"Broadcasted political event: {event.event_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to broadcast political event: {e}")
    
    # Turn management
    def start_new_turn(self, turn_number: int):
        """
        Start a new turn.
        
        Args:
            turn_number: Turn number to start
        """
        try:
            # Start performance profiling for turn
            if self.performance_profiler:
                self.performance_profiler.start_turn_profiling(turn_number)
            
            # Update turn synchronizer
            if turn_number != self.turn_synchronizer.current_state.turn_number:
                # Force synchronizer to the correct turn
                self.turn_synchronizer.current_state.turn_number = turn_number
                self.turn_synchronizer.current_state.turn_start_time = datetime.now()
            
            # Reset engine readiness
            self.turn_synchronizer.set_political_engine_ready(False)
            self.turn_synchronizer.set_game_engine_ready(False)
            
            # Broadcast turn start
            turn_start_message = self.turn_synchronizer.create_turn_start_message()
            asyncio.create_task(self.bridge.broadcast_message(turn_start_message))
            
            self.logger.info(f"Started turn {turn_number}")
            
        except Exception as e:
            self.logger.error(f"Failed to start turn {turn_number}: {e}")
    
    def end_current_turn(self):
        """End the current turn."""
        try:
            current_turn = self.turn_synchronizer.current_state.turn_number
            
            # End performance profiling
            if self.performance_profiler:
                self.performance_profiler.end_turn_profiling()
            
            # Broadcast turn end
            turn_end_message = self.turn_synchronizer.create_turn_end_message()
            asyncio.create_task(self.bridge.broadcast_message(turn_end_message))
            
            self.logger.info(f"Ended turn {current_turn}")
            
        except Exception as e:
            self.logger.error(f"Failed to end current turn: {e}")
    
    def set_political_engine_ready(self, ready: bool = True):
        """Set political engine readiness for turn advancement."""
        self.turn_synchronizer.set_political_engine_ready(ready)
    
    def advance_turn(self):
        """Advance to the next turn."""
        success = self.turn_synchronizer.advance_turn()
        if success:
            self.start_new_turn(self.turn_synchronizer.current_state.turn_number)
        return success
    
    # Client management
    def subscribe_client_to_events(self, connection_id: str, filter: SubscriptionFilter) -> str:
        """
        Subscribe a client to political events.
        
        Args:
            connection_id: Client connection ID
            filter: Event subscription filter
            
        Returns:
            Subscription ID
        """
        return self.event_broadcaster.subscribe_to_events(connection_id, filter)
    
    def unsubscribe_client_from_events(self, subscription_id: str) -> bool:
        """
        Unsubscribe a client from political events.
        
        Args:
            subscription_id: Subscription ID to remove
            
        Returns:
            True if subscription was removed
        """
        return self.event_broadcaster.unsubscribe_from_events(subscription_id)
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get information about connected clients."""
        return {
            'connected_clients': len(self.bridge.connections),
            'active_subscriptions': len(self.event_broadcaster.subscriptions),
            'connection_details': dict(self.bridge.connections.keys())
        }
    
    # Event handlers
    def _handle_player_decision(self, data: Dict[str, Any]):
        """Handle player decision from game engine."""
        self.logger.info(f"Player decision received: {data}")
        self._emit_event("player_decision", data)
    
    def _handle_advisor_appointment(self, data: Dict[str, Any]):
        """Handle advisor appointment from game engine."""
        self.logger.info(f"Advisor appointment: {data}")
        self._emit_event("advisor_appointment", data)
    
    def _handle_advisor_dismissal(self, data: Dict[str, Any]):
        """Handle advisor dismissal from game engine."""
        self.logger.info(f"Advisor dismissal: {data}")
        self._emit_event("advisor_dismissal", data)
    
    def _handle_turn_advance_request(self, data: Dict[str, Any]):
        """Handle turn advance request from game engine."""
        self.logger.info(f"Turn advance requested: {data}")
        
        # Set game engine as ready
        self.turn_synchronizer.set_game_engine_ready(True)
        
        self._emit_event("turn_advance_request", data)
    
    def _handle_state_request(self, data: Dict[str, Any]):
        """Handle state request from game engine."""
        self.logger.info(f"State request: {data}")
        
        if self.current_game_state:
            # Send current state to requesting client
            connection_id = data.get("connection_id")
            if connection_id and connection_id in self.bridge.connections:
                message = self.bridge.create_game_state_sync("political_engine", self.current_game_state)
                websocket = self.bridge.connections[connection_id]
                asyncio.create_task(self.bridge._send_message(websocket, message))
        
        self._emit_event("state_request", data)
    
    def _handle_turn_advanced(self, data: Dict[str, Any]):
        """Handle turn advancement from synchronizer."""
        self.logger.info(f"Turn advanced: {data}")
        self._emit_event("turn_advanced", data)
    
    def _handle_phase_advanced(self, data: Dict[str, Any]):
        """Handle phase advancement from synchronizer."""
        self.logger.info(f"Phase advanced: {data}")
        self._emit_event("phase_advanced", data)
    
    def _handle_turn_timeout(self, data: Dict[str, Any]):
        """Handle turn timeout from synchronizer."""
        self.logger.warning(f"Turn timeout: {data}")
        self._emit_event("turn_timeout", data)
    
    def _handle_performance_alert(self, alert):
        """Handle performance alert from profiler."""
        self.logger.warning(f"Performance alert: {alert.description}")
        self._emit_event("performance_alert", {"alert": alert.to_dict()})
    
    def _broadcast_event_message(self, connection_id: str, message):
        """Broadcast event message via bridge."""
        try:
            if connection_id in self.bridge.connections:
                websocket = self.bridge.connections[connection_id]
                asyncio.create_task(self.bridge._send_message(websocket, message))
            else:
                # Broadcast to all connections
                asyncio.create_task(self.bridge.broadcast_message(message))
        except Exception as e:
            self.logger.error(f"Failed to broadcast event message: {e}")
    
    # Event system
    def subscribe_to_event(self, event_type: str, callback: Callable):
        """Subscribe to bridge manager events."""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)
    
    def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit event to subscribers."""
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Event callback error for {event_type}: {e}")
    
    # Status and monitoring
    def get_bridge_status(self) -> Dict[str, Any]:
        """Get comprehensive bridge status."""
        status = {
            'running': self.running,
            'bridge_status': self.bridge.get_connection_status().value,
            'connected_clients': len(self.bridge.connections),
            'turn_state': self.turn_synchronizer.get_current_state().to_dict(),
            'performance_metrics': self.bridge.get_performance_metrics()
        }
        
        if self.performance_profiler:
            status['performance_summary'] = self.performance_profiler.get_performance_summary()
            status['turn_performance'] = self.performance_profiler.get_turn_performance_analysis()
            status['active_alerts'] = self.performance_profiler.get_active_alerts()
        
        status['event_statistics'] = self.event_broadcaster.get_event_statistics()
        
        return status
    
    def get_diagnostics(self) -> Dict[str, Any]:
        """Get comprehensive diagnostics information."""
        diagnostics = {
            'bridge_manager': {
                'running': self.running,
                'host': self.host,
                'port': self.port,
                'auto_advance_turns': self.auto_advance_turns,
                'performance_monitoring_enabled': self.enable_performance_monitoring
            },
            'components': {
                'bridge': {
                    'status': self.bridge.get_connection_status().value,
                    'connections': len(self.bridge.connections),
                    'metrics': self.bridge.get_performance_metrics()
                },
                'turn_synchronizer': {
                    'current_state': self.turn_synchronizer.get_current_state().to_dict(),
                    'turn_history_count': len(self.turn_synchronizer.get_turn_history())
                },
                'event_broadcaster': {
                    'metrics': self.event_broadcaster.get_metrics(),
                    'statistics': self.event_broadcaster.get_event_statistics()
                }
            }
        }
        
        if self.performance_profiler:
            diagnostics['components']['performance_profiler'] = {
                'monitoring_active': self.performance_profiler.monitoring_active,
                'summary': self.performance_profiler.get_performance_summary(),
                'alerts': self.performance_profiler.get_active_alerts()
            }
        
        return diagnostics
