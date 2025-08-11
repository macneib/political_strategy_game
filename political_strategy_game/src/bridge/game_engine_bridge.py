"""
Game Engine Bridge - Core Communication System

This module implements the main GameEngineBridge class that handles
bi-directional communication between the political simulation engine
and external game engines.
"""

import asyncio
import json
import logging
import time
import threading
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from queue import Queue, Empty
import websockets

from . import (
    BridgeMessage, MessageType, MessageHeader, EventPriority,
    ConnectionStatus, MessageFactory, BridgeErrorCodes,
    GameState, PoliticalEvent, PlayerCommand
)


class GameEngineBridge:
    """
    Main bridge class for communication between political engine and game engine.
    
    Provides:
    - WebSocket server for real-time communication
    - Message routing and handling
    - Connection management and health monitoring
    - Event broadcasting and command processing
    """
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 8888,
                 max_connections: int = 5,
                 heartbeat_interval: float = 30.0,
                 connection_timeout: float = 60.0):
        """
        Initialize the game engine bridge.
        
        Args:
            host: Server host address
            port: Server port number
            max_connections: Maximum concurrent connections
            heartbeat_interval: Seconds between heartbeat messages
            connection_timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.heartbeat_interval = heartbeat_interval
        self.connection_timeout = connection_timeout
        
        # Connection management
        self.connections: Dict[str, Any] = {}
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.last_heartbeat: Dict[str, datetime] = {}
        
        # Message handling
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.outbound_queue = Queue()
        self.inbound_queue = Queue()
        
        # Event system
        self.event_subscribers: Dict[str, List[Callable]] = {}
        
        # Performance monitoring
        self.performance_metrics = {
            "messages_sent": 0,
            "messages_received": 0,
            "average_latency": 0.0,
            "connection_count": 0,
            "errors": 0
        }
        
        # Threading
        self.server_thread: Optional[threading.Thread] = None
        self.processing_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize message handlers
        self._setup_message_handlers()
    
    def _setup_message_handlers(self):
        """Set up default message handlers."""
        self.message_handlers = {
            MessageType.HANDSHAKE: self._handle_handshake,
            MessageType.HEARTBEAT: self._handle_heartbeat,
            MessageType.PLAYER_DECISION: self._handle_player_decision,
            MessageType.ADVISOR_APPOINTMENT: self._handle_advisor_appointment,
            MessageType.ADVISOR_DISMISSAL: self._handle_advisor_dismissal,
            MessageType.TURN_ADVANCE: self._handle_turn_advance,
            MessageType.STATE_REQUEST: self._handle_state_request,
            MessageType.ERROR: self._handle_error,
            MessageType.ACKNOWLEDGMENT: self._handle_acknowledgment
        }
    
    async def start_server(self):
        """Start the WebSocket server."""
        try:
            self.logger.info(f"Starting Game Engine Bridge server on {self.host}:{self.port}")
            
            # Create a wrapper for the handler that properly handles arguments
            async def handler(websocket, path=None):
                return await self._handle_connection(websocket, path or "/")
            
            async with websockets.serve(
                handler,
                self.host,
                self.port,
                max_size=1024 * 1024,  # 1MB max message size
                ping_interval=self.heartbeat_interval,
                ping_timeout=self.connection_timeout
            ) as server:
                self.connection_status = ConnectionStatus.CONNECTED
                self.running = True
                
                # Start background tasks
                await asyncio.gather(
                    self._heartbeat_monitor(),
                    self._message_processor(),
                    self._performance_monitor()
                )
                
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            self.connection_status = ConnectionStatus.ERROR
            raise
    
    async def _handle_connection(self, websocket: Any, path: str):
        """Handle new WebSocket connection."""
        connection_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}:{int(time.time())}"
        
        if len(self.connections) >= self.max_connections:
            await websocket.close(code=1013, reason="Server at capacity")
            return
        
        self.connections[connection_id] = websocket
        self.last_heartbeat[connection_id] = datetime.now()
        self.performance_metrics["connection_count"] = len(self.connections)
        
        self.logger.info(f"New connection established: {connection_id}")
        
        try:
            # Send handshake
            handshake = MessageFactory.create_handshake("political_engine")
            await self._send_message(websocket, handshake)
            
            # Handle messages
            async for message in websocket:
                try:
                    bridge_message = BridgeMessage.from_json(message)
                    await self._process_message(connection_id, bridge_message)
                    self.performance_metrics["messages_received"] += 1
                    
                except json.JSONDecodeError as e:
                    error_msg = MessageFactory.create_error(
                        "political_engine",
                        BridgeErrorCodes.INVALID_MESSAGE_FORMAT,
                        f"Invalid JSON format: {e}"
                    )
                    await self._send_message(websocket, error_msg)
                    self.performance_metrics["errors"] += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
                    error_msg = MessageFactory.create_error(
                        "political_engine",
                        BridgeErrorCodes.COMMAND_PROCESSING_FAILED,
                        f"Message processing failed: {e}"
                    )
                    await self._send_message(websocket, error_msg)
                    self.performance_metrics["errors"] += 1
                    
        except Exception as e:
            if "ConnectionClosed" in str(type(e)):
                self.logger.info(f"Connection closed: {connection_id}")
            else:
                self.logger.error(f"WebSocket error for {connection_id}: {e}")
        finally:
            # Clean up connection
            if connection_id in self.connections:
                del self.connections[connection_id]
            if connection_id in self.last_heartbeat:
                del self.last_heartbeat[connection_id]
            self.performance_metrics["connection_count"] = len(self.connections)
    
    async def _send_message(self, websocket: Any, message: BridgeMessage):
        """Send message to specific WebSocket connection."""
        try:
            await websocket.send(message.to_json())
            self.performance_metrics["messages_sent"] += 1
        except Exception as e:
            if "ConnectionClosed" in str(type(e)):
                # Connection was closed, remove from active connections
                connection_id = None
            for conn_id, ws in self.connections.items():
                if ws == websocket:
                    connection_id = conn_id
                    break
            if connection_id:
                del self.connections[connection_id]
                if connection_id in self.last_heartbeat:
                    del self.last_heartbeat[connection_id]
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            self.performance_metrics["errors"] += 1
    
    async def broadcast_message(self, message: BridgeMessage, exclude_connections: List[str] = None):
        """Broadcast message to all connected clients."""
        exclude_connections = exclude_connections or []
        
        for connection_id, websocket in list(self.connections.items()):
            if connection_id not in exclude_connections:
                await self._send_message(websocket, message)
    
    async def _process_message(self, connection_id: str, message: BridgeMessage):
        """Process incoming message."""
        self.last_heartbeat[connection_id] = datetime.now()
        
        # Update performance metrics
        if message.header.correlation_id:
            # Calculate latency for request-response patterns
            # This is a simplified approach - full implementation would track request timestamps
            pass
        
        # Route message to appropriate handler
        message_type = message.header.message_type
        if message_type in self.message_handlers:
            try:
                await self.message_handlers[message_type](connection_id, message)
            except Exception as e:
                self.logger.error(f"Handler error for {message_type}: {e}")
                error_msg = MessageFactory.create_error(
                    "political_engine",
                    BridgeErrorCodes.COMMAND_PROCESSING_FAILED,
                    f"Handler failed: {e}",
                    correlation_id=message.header.message_id
                )
                websocket = self.connections.get(connection_id)
                if websocket:
                    await self._send_message(websocket, error_msg)
        else:
            self.logger.warning(f"No handler for message type: {message_type}")
    
    async def _heartbeat_monitor(self):
        """Monitor connection health via heartbeats."""
        while self.running:
            try:
                current_time = datetime.now()
                timeout_threshold = current_time - timedelta(seconds=self.connection_timeout)
                
                # Check for timed out connections
                timed_out_connections = []
                for connection_id, last_heartbeat in self.last_heartbeat.items():
                    if last_heartbeat < timeout_threshold:
                        timed_out_connections.append(connection_id)
                
                # Close timed out connections
                for connection_id in timed_out_connections:
                    websocket = self.connections.get(connection_id)
                    if websocket:
                        await websocket.close(code=1001, reason="Heartbeat timeout")
                        del self.connections[connection_id]
                        del self.last_heartbeat[connection_id]
                        self.logger.info(f"Connection {connection_id} timed out")
                
                # Send heartbeat to remaining connections
                heartbeat = MessageFactory.create_heartbeat("political_engine")
                await self.broadcast_message(heartbeat)
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"Heartbeat monitor error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def _message_processor(self):
        """Process queued outbound messages."""
        while self.running:
            try:
                # Process outbound queue
                try:
                    message = self.outbound_queue.get_nowait()
                    await self.broadcast_message(message)
                except Empty:
                    pass
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                self.logger.error(f"Message processor error: {e}")
                await asyncio.sleep(1)
    
    async def _performance_monitor(self):
        """Monitor and log performance metrics."""
        while self.running:
            try:
                await asyncio.sleep(60)  # Log metrics every minute
                
                self.logger.info(f"Bridge Performance Metrics: {self.performance_metrics}")
                
                # Reset counters for next period
                self.performance_metrics["messages_sent"] = 0
                self.performance_metrics["messages_received"] = 0
                self.performance_metrics["errors"] = 0
                
            except Exception as e:
                self.logger.error(f"Performance monitor error: {e}")
    
    # Message handlers
    async def _handle_handshake(self, connection_id: str, message: BridgeMessage):
        """Handle handshake message."""
        self.logger.info(f"Handshake received from {connection_id}")
        
        # Send acknowledgment
        ack = MessageFactory.create_handshake("political_engine")
        ack.header.correlation_id = message.header.message_id
        
        websocket = self.connections.get(connection_id)
        if websocket:
            await self._send_message(websocket, ack)
    
    async def _handle_heartbeat(self, connection_id: str, message: BridgeMessage):
        """Handle heartbeat message."""
        # Heartbeat handling is already done in _process_message
        pass
    
    async def _handle_player_decision(self, connection_id: str, message: BridgeMessage):
        """Handle player decision command."""
        self.logger.info(f"Player decision received: {message.payload}")
        
        # Emit event for political engine to process
        self._emit_event("player_decision", {
            "connection_id": connection_id,
            "decision": message.payload
        })
    
    async def _handle_advisor_appointment(self, connection_id: str, message: BridgeMessage):
        """Handle advisor appointment command."""
        self.logger.info(f"Advisor appointment: {message.payload}")
        
        self._emit_event("advisor_appointment", {
            "connection_id": connection_id,
            "appointment": message.payload
        })
    
    async def _handle_advisor_dismissal(self, connection_id: str, message: BridgeMessage):
        """Handle advisor dismissal command."""
        self.logger.info(f"Advisor dismissal: {message.payload}")
        
        self._emit_event("advisor_dismissal", {
            "connection_id": connection_id,
            "dismissal": message.payload
        })
    
    async def _handle_turn_advance(self, connection_id: str, message: BridgeMessage):
        """Handle turn advance command."""
        self.logger.info(f"Turn advance requested by {connection_id}")
        
        self._emit_event("turn_advance", {
            "connection_id": connection_id,
            "parameters": message.payload
        })
    
    async def _handle_state_request(self, connection_id: str, message: BridgeMessage):
        """Handle game state request."""
        self.logger.info(f"State request from {connection_id}")
        
        self._emit_event("state_request", {
            "connection_id": connection_id,
            "request_params": message.payload
        })
    
    async def _handle_error(self, connection_id: str, message: BridgeMessage):
        """Handle error message."""
        self.logger.error(f"Error from {connection_id}: {message.payload}")
    
    async def _handle_acknowledgment(self, connection_id: str, message: BridgeMessage):
        """Handle acknowledgment message."""
        # Log acknowledgment for correlation tracking
        pass
    
    # Event system
    def subscribe_to_event(self, event_type: str, callback: Callable):
        """Subscribe to bridge events."""
        if event_type not in self.event_subscribers:
            self.event_subscribers[event_type] = []
        self.event_subscribers[event_type].append(callback)
    
    def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit event to subscribers."""
        if event_type in self.event_subscribers:
            for callback in self.event_subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Event callback error: {e}")
    
    # Public API methods
    def queue_game_state_sync(self, game_state: GameState):
        """Queue full game state synchronization."""
        message = MessageFactory.create_game_state_sync("political_engine", game_state)
        self.outbound_queue.put(message)
    
    def queue_political_event(self, event: PoliticalEvent):
        """Queue political event for broadcast."""
        message = MessageFactory.create_political_event("political_engine", event)
        self.outbound_queue.put(message)
    
    def start(self):
        """Start the bridge server in a separate thread."""
        if self.running:
            return
        
        self.server_thread = threading.Thread(
            target=lambda: asyncio.run(self.start_server()),
            daemon=True
        )
        self.server_thread.start()
        
        # Wait for server to start
        max_wait = 10
        wait_time = 0
        while self.connection_status == ConnectionStatus.DISCONNECTED and wait_time < max_wait:
            time.sleep(0.5)
            wait_time += 0.5
        
        if self.connection_status == ConnectionStatus.CONNECTED:
            self.logger.info("Game Engine Bridge started successfully")
        else:
            self.logger.error("Failed to start Game Engine Bridge")
    
    def stop(self):
        """Stop the bridge server."""
        self.running = False
        self.connection_status = ConnectionStatus.DISCONNECTED
        
        # Close all connections (if we're in an event loop, schedule them)
        try:
            loop = asyncio.get_running_loop()
            for websocket in self.connections.values():
                asyncio.create_task(websocket.close())
        except RuntimeError:
            # No event loop running, can use asyncio.run
            for websocket in self.connections.values():
                asyncio.run(websocket.close())
        
        self.connections.clear()
        self.last_heartbeat.clear()
        
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)
        
        self.logger.info("Game Engine Bridge stopped")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.performance_metrics.copy()
    
    def get_connection_status(self) -> ConnectionStatus:
        """Get current connection status."""
        return self.connection_status
