"""
Demo Game Engine Client

This script demonstrates how a game engine would interact with the
Political Strategy Game bridge system. It shows connection management,
state synchronization, event handling, and turn coordination.
"""

import asyncio
import json
import logging
import time
import websockets
from datetime import datetime
from typing import Dict, Any, Optional

from src.bridge import (
    MessageType, EventPriority, BridgeMessage, MessageFactory, 
    SubscriptionFilter, EventCategory
)


class DemoGameEngineClient:
    """
    Demo client that simulates a game engine connecting to the
    political simulation bridge.
    """
    
    def __init__(self, server_uri: str = "ws://localhost:8888", client_name: str = "Demo Game Engine"):
        """
        Initialize demo client.
        
        Args:
            server_uri: WebSocket URI of the bridge server
            client_name: Name of this client
        """
        self.server_uri = server_uri
        self.client_name = client_name
        
        # Connection state
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connected = False
        self.running = False
        
        # Game state
        self.current_turn = 1
        self.game_state: Optional[Dict[str, Any]] = None
        self.received_events = []
        
        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "events_received": 0,
            "state_updates": 0,
            "connection_time": None
        }
        
        # Logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"DemoClient-{client_name}")
    
    async def connect(self):
        """Connect to the bridge server."""
        try:
            self.logger.info(f"Connecting to bridge server at {self.server_uri}")
            
            self.websocket = await websockets.connect(self.server_uri)
            self.connected = True
            self.stats["connection_time"] = datetime.now()
            
            self.logger.info("Connected to bridge server")
            
            # Handle incoming messages
            await self._handle_messages()
            
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            self.connected = False
            raise
    
    async def _handle_messages(self):
        """Handle incoming messages from the bridge."""
        try:
            async for message in self.websocket:
                try:
                    bridge_message = BridgeMessage.from_json(message)
                    await self._process_message(bridge_message)
                    self.stats["messages_received"] += 1
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON received: {e}")
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            self.logger.info("Connection closed by server")
            self.connected = False
        except Exception as e:
            self.logger.error(f"Message handling error: {e}")
            self.connected = False
    
    async def _process_message(self, message: BridgeMessage):
        """Process a received bridge message."""
        message_type = message.header.message_type
        
        self.logger.debug(f"Received {message_type.value} message")
        
        if message_type == MessageType.HANDSHAKE:
            await self._handle_handshake(message)
        elif message_type == MessageType.HEARTBEAT:
            await self._handle_heartbeat(message)
        elif message_type == MessageType.FULL_STATE_SYNC:
            await self._handle_state_sync(message)
        elif message_type == MessageType.POLITICAL_EVENT:
            await self._handle_political_event(message)
        elif message_type == MessageType.TURN_START:
            await self._handle_turn_start(message)
        elif message_type == MessageType.TURN_END:
            await self._handle_turn_end(message)
        elif message_type == MessageType.ERROR:
            await self._handle_error(message)
        else:
            self.logger.warning(f"Unhandled message type: {message_type}")
    
    async def _handle_handshake(self, message: BridgeMessage):
        """Handle handshake message."""
        self.logger.info("Received handshake from bridge")
        
        # Send handshake response
        response = MessageFactory.create_handshake("game_engine")
        response.header.correlation_id = message.header.message_id
        
        await self._send_message(response)
        
        # Subscribe to events
        await self._subscribe_to_events()
        
        # Request initial state
        await self._request_game_state()
    
    async def _handle_heartbeat(self, message: BridgeMessage):
        """Handle heartbeat message."""
        # Respond with heartbeat
        response = MessageFactory.create_heartbeat("game_engine")
        await self._send_message(response)
    
    async def _handle_state_sync(self, message: BridgeMessage):
        """Handle game state synchronization."""
        self.logger.info("Received game state update")
        
        if 'game_state' in message.payload:
            self.game_state = message.payload['game_state']
            self.stats["state_updates"] += 1
            
            # Log some interesting state information
            if 'turn_state' in self.game_state:
                turn_info = self.game_state['turn_state']
                self.logger.info(f"Turn {turn_info['turn_number']}, Phase: {turn_info['phase']}")
            
            if 'civilizations' in self.game_state:
                civ_count = len(self.game_state['civilizations'])
                self.logger.info(f"Tracking {civ_count} civilizations")
            
            if 'advisors' in self.game_state:
                advisor_count = len(self.game_state['advisors'])
                self.logger.info(f"Tracking {advisor_count} advisors")
    
    async def _handle_political_event(self, message: BridgeMessage):
        """Handle political event notification."""
        if 'event_batch' in message.payload:
            # Batch of events
            batch = message.payload['event_batch']
            events = batch['events']
            self.logger.info(f"Received event batch with {len(events)} events")
            
            for event in events:
                self._process_political_event(event)
                self.received_events.append(event)
        elif 'event' in message.payload:
            # Single event
            event = message.payload['event']
            self._process_political_event(event)
            self.received_events.append(event)
        
        self.stats["events_received"] += 1
    
    def _process_political_event(self, event: Dict[str, Any]):
        """Process a single political event."""
        self.logger.info(f"Political Event: {event['title']} ({event['severity']})")
        self.logger.info(f"  Description: {event['description']}")
        self.logger.info(f"  Participants: {', '.join(event['participants'])}")
        
        # Simulate game engine response to event
        if event['severity'] in ['major', 'critical']:
            self.logger.warning(f"High severity event detected: {event['title']}")
    
    async def _handle_turn_start(self, message: BridgeMessage):
        """Handle turn start notification."""
        turn_data = message.payload
        self.current_turn = turn_data['turn_number']
        
        self.logger.info(f"=== TURN {self.current_turn} STARTED ===")
        self.logger.info(f"Phase: {turn_data['phase']}")
        
        # Simulate game engine turn processing
        await self._simulate_turn_processing()
        
        # Signal ready for turn advancement
        await self._signal_turn_ready()
    
    async def _handle_turn_end(self, message: BridgeMessage):
        """Handle turn end notification."""
        turn_data = message.payload
        completed_turn = turn_data['completed_turn']
        
        self.logger.info(f"=== TURN {completed_turn} ENDED ===")
        self.logger.info(f"Duration: {turn_data.get('turn_duration', 0):.2f} seconds")
    
    async def _handle_error(self, message: BridgeMessage):
        """Handle error message."""
        error_info = message.payload
        self.logger.error(f"Bridge Error: {error_info['error_code']} - {error_info['error_message']}")
    
    async def _send_message(self, message: BridgeMessage):
        """Send message to bridge."""
        if self.websocket and self.connected:
            try:
                await self.websocket.send(message.to_json())
                self.stats["messages_sent"] += 1
            except Exception as e:
                self.logger.error(f"Failed to send message: {e}")
    
    async def _subscribe_to_events(self):
        """Subscribe to political events."""
        # Create subscription for all events
        subscription_message = {
            'header': {
                'message_id': f'subscribe_{int(time.time())}',
                'message_type': 'EVENT_SUBSCRIPTION',
                'timestamp': datetime.now().isoformat(),
                'sender': 'game_engine',
                'recipient': 'political_engine',
                'priority': EventPriority.NORMAL.value,
                'api_version': '1.0'
            },
            'payload': {
                'subscription_type': 'all_events',
                'filter': {
                    'categories': ['advisor', 'crisis', 'conspiracy', 'diplomatic'],
                    'severities': ['minor', 'moderate', 'major', 'critical']
                }
            }
        }
        
        # Note: This would need to be properly implemented in the bridge
        self.logger.info("Subscribed to political events")
    
    async def _request_game_state(self):
        """Request current game state."""
        request_message = {
            'header': {
                'message_id': f'state_req_{int(time.time())}',
                'message_type': MessageType.STATE_REQUEST.value,
                'timestamp': datetime.now().isoformat(),
                'sender': 'game_engine',
                'recipient': 'political_engine',
                'priority': EventPriority.NORMAL.value,
                'api_version': '1.0'
            },
            'payload': {
                'request_type': 'full_state'
            }
        }
        
        message = BridgeMessage.from_json(json.dumps(request_message))
        await self._send_message(message)
        
        self.logger.info("Requested game state")
    
    async def _simulate_turn_processing(self):
        """Simulate game engine turn processing."""
        self.logger.info("Processing turn...")
        
        # Simulate some processing time
        await asyncio.sleep(1.0)
        
        # Simulate making some game decisions
        await self._make_sample_decisions()
        
        self.logger.info("Turn processing complete")
    
    async def _make_sample_decisions(self):
        """Make sample decisions to demonstrate interaction."""
        decisions = [
            {
                'type': 'advisor_appointment',
                'advisor_id': 'new_advisor_1',
                'role': 'economic',
                'reason': 'Need economic expertise'
            },
            {
                'type': 'policy_decision',
                'policy': 'military_expansion',
                'intensity': 0.7,
                'reason': 'Response to external threats'
            },
            {
                'type': 'diplomatic_action',
                'target_civilization': 'neighbor_civ',
                'action': 'trade_agreement',
                'terms': {'duration': 10, 'trade_bonus': 0.15}
            }
        ]
        
        for decision in decisions:
            await self._send_player_decision(decision)
            await asyncio.sleep(0.2)  # Small delay between decisions
    
    async def _send_player_decision(self, decision: Dict[str, Any]):
        """Send a player decision to the bridge."""
        decision_message = {
            'header': {
                'message_id': f'decision_{int(time.time())}',
                'message_type': MessageType.PLAYER_DECISION.value,
                'timestamp': datetime.now().isoformat(),
                'sender': 'game_engine',
                'recipient': 'political_engine',
                'priority': EventPriority.NORMAL.value,
                'api_version': '1.0'
            },
            'payload': {
                'decision': decision,
                'player_id': 'demo_player',
                'civilization_id': 'player_civ'
            }
        }
        
        message = BridgeMessage.from_json(json.dumps(decision_message))
        await self._send_message(message)
        
        self.logger.info(f"Sent decision: {decision['type']}")
    
    async def _signal_turn_ready(self):
        """Signal that the game engine is ready for turn advancement."""
        ready_message = {
            'header': {
                'message_id': f'turn_ready_{int(time.time())}',
                'message_type': MessageType.TURN_ADVANCE.value,
                'timestamp': datetime.now().isoformat(),
                'sender': 'game_engine',
                'recipient': 'political_engine',
                'priority': EventPriority.HIGH.value,
                'api_version': '1.0'
            },
            'payload': {
                'ready': True,
                'turn_number': self.current_turn
            }
        }
        
        message = BridgeMessage.from_json(json.dumps(ready_message))
        await self._send_message(message)
        
        self.logger.info(f"Signaled ready for turn {self.current_turn} advancement")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get client statistics."""
        stats = self.stats.copy()
        stats.update({
            'connected': self.connected,
            'current_turn': self.current_turn,
            'events_received': len(self.received_events),
            'has_game_state': self.game_state is not None
        })
        
        if stats['connection_time']:
            stats['uptime_seconds'] = (datetime.now() - stats['connection_time']).total_seconds()
        
        return stats
    
    def print_status_report(self):
        """Print a status report of the client."""
        print("\n" + "="*60)
        print(f"DEMO GAME ENGINE CLIENT STATUS - {self.client_name}")
        print("="*60)
        
        stats = self.get_statistics()
        
        print(f"Connection Status: {'Connected' if stats['connected'] else 'Disconnected'}")
        print(f"Current Turn: {stats['current_turn']}")
        print(f"Messages Sent: {stats['messages_sent']}")
        print(f"Messages Received: {stats['messages_received']}")
        print(f"Events Received: {stats['events_received']}")
        print(f"State Updates: {stats['state_updates']}")
        
        if 'uptime_seconds' in stats:
            print(f"Uptime: {stats['uptime_seconds']:.1f} seconds")
        
        print(f"Has Game State: {'Yes' if stats['has_game_state'] else 'No'}")
        
        if self.received_events:
            print(f"\nRecent Events ({len(self.received_events)} total):")
            for event in self.received_events[-5:]:  # Show last 5 events
                print(f"  - {event['title']} ({event['severity']})")
        
        print("="*60)
    
    async def disconnect(self):
        """Disconnect from the bridge server."""
        if self.websocket:
            await self.websocket.close()
        self.connected = False
        self.logger.info("Disconnected from bridge server")


async def run_demo():
    """Run the demo client."""
    print("\n🎮 POLITICAL STRATEGY GAME - BRIDGE DEMO CLIENT 🎮")
    print("="*60)
    print("This demo shows how a game engine connects to the political")
    print("simulation bridge and interacts with the political systems.")
    print("="*60)
    
    client = DemoGameEngineClient()
    
    try:
        print("\n🔌 Connecting to bridge server...")
        await client.connect()
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("\n💡 Make sure the bridge server is running first!")
        print("   Run: python -m src.bridge.demo_server")
    finally:
        if client.connected:
            await client.disconnect()
        
        # Print final statistics
        client.print_status_report()


if __name__ == "__main__":
    # Run the demo
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\n👋 Demo client shutting down...")
    
    print("\n✨ Demo complete! Check the bridge server logs for full details.")
