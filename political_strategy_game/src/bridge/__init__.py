"""
Game Engine Bridge - Core Data Structures and Message Types

This module defines the communication protocol and data structures for
interfacing between the political simulation engine and external game engines
like Unity or Godot.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import uuid


class MessageType(Enum):
    """Types of messages exchanged between political engine and game engine."""
    
    # Game State Messages
    FULL_STATE_SYNC = "full_state_sync"
    INCREMENTAL_UPDATE = "incremental_update"
    STATE_REQUEST = "state_request"
    
    # Event Messages
    POLITICAL_EVENT = "political_event"
    ADVISOR_ACTION = "advisor_action"
    CRISIS_EVENT = "crisis_event"
    CONSPIRACY_EVENT = "conspiracy_event"
    DIPLOMATIC_EVENT = "diplomatic_event"
    
    # Command Messages
    PLAYER_DECISION = "player_decision"
    ADVISOR_APPOINTMENT = "advisor_appointment"
    ADVISOR_DISMISSAL = "advisor_dismissal"
    TURN_ADVANCE = "turn_advance"
    
    # System Messages
    HANDSHAKE = "handshake"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    ACKNOWLEDGMENT = "acknowledgment"
    TURN_START = "turn_start"
    TURN_END = "turn_end"


class EventPriority(Enum):
    """Priority levels for event processing."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ConnectionStatus(Enum):
    """Status of the bridge connection."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


@dataclass
class MessageHeader:
    """Standard header for all bridge messages."""
    message_id: str
    message_type: MessageType
    timestamp: datetime
    sender: str  # "political_engine" or "game_engine"
    recipient: str
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = None  # For request-response patterns
    api_version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        data['priority'] = self.priority.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class BridgeMessage:
    """Complete message structure for bridge communication."""
    header: MessageHeader
    payload: Dict[str, Any]
    
    def to_json(self) -> str:
        """Serialize message to JSON string."""
        return json.dumps({
            'header': self.header.to_dict(),
            'payload': self.payload
        }, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BridgeMessage':
        """Deserialize message from JSON string."""
        data = json.loads(json_str)
        
        header_data = data['header']
        header = MessageHeader(
            message_id=header_data['message_id'],
            message_type=MessageType(header_data['message_type']),
            timestamp=datetime.fromisoformat(header_data['timestamp']),
            sender=header_data['sender'],
            recipient=header_data['recipient'],
            priority=EventPriority(header_data['priority']),
            correlation_id=header_data.get('correlation_id'),
            api_version=header_data.get('api_version', '1.0')
        )
        
        return cls(header=header, payload=data['payload'])


@dataclass
class TurnState:
    """Current turn state information."""
    turn_number: int
    civilization_id: str
    phase: str  # "planning", "execution", "resolution"
    time_remaining: Optional[float] = None  # seconds
    is_paused: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class AdvisorState:
    """Serializable advisor state for game engine."""
    advisor_id: str
    name: str
    role: str
    loyalty: float
    influence: float
    stress_level: float
    current_mood: str
    personality_traits: Dict[str, float]
    relationships: Dict[str, float]  # advisor_id -> relationship_strength
    current_activity: Optional[str] = None
    location: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class CivilizationState:
    """Serializable civilization state for game engine."""
    civilization_id: str
    name: str
    leader_name: str
    political_stability: float
    economic_strength: float
    military_power: float
    diplomatic_relations: Dict[str, float]  # civ_id -> relation_strength
    active_crises: List[str]  # crisis_ids
    active_conspiracies: List[str]  # conspiracy_ids
    recent_events: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class GameState:
    """Complete game state for synchronization."""
    turn_state: TurnState
    civilizations: List[CivilizationState]
    advisors: List[AdvisorState]
    global_events: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'turn_state': self.turn_state.to_dict(),
            'civilizations': [civ.to_dict() for civ in self.civilizations],
            'advisors': [advisor.to_dict() for advisor in self.advisors],
            'global_events': self.global_events,
            'metadata': self.metadata
        }


@dataclass
class PoliticalEvent:
    """Political event for notification to game engine."""
    event_id: str
    event_type: str
    civilization_id: str
    title: str
    description: str
    severity: str  # "minor", "moderate", "major", "critical"
    participants: List[str]  # advisor_ids or civ_ids
    consequences: Dict[str, Any]
    timestamp: datetime
    duration: Optional[int] = None  # turns
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class PlayerCommand:
    """Player command from game engine to political engine."""
    command_id: str
    command_type: str
    civilization_id: str
    parameters: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class MessageFactory:
    """Factory for creating standardized bridge messages."""
    
    @staticmethod
    def create_handshake(sender: str, api_version: str = "1.0") -> BridgeMessage:
        """Create handshake message for connection establishment."""
        header = MessageHeader(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.HANDSHAKE,
            timestamp=datetime.now(),
            sender=sender,
            recipient="bridge",
            priority=EventPriority.HIGH,
            api_version=api_version
        )
        
        payload = {
            "api_version": api_version,
            "capabilities": [
                "full_state_sync",
                "incremental_updates",
                "real_time_events",
                "turn_synchronization"
            ],
            "sender_info": {
                "type": sender,
                "version": "1.0.0"
            }
        }
        
        return BridgeMessage(header=header, payload=payload)
    
    @staticmethod
    def create_heartbeat(sender: str) -> BridgeMessage:
        """Create heartbeat message for connection monitoring."""
        header = MessageHeader(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.HEARTBEAT,
            timestamp=datetime.now(),
            sender=sender,
            recipient="bridge",
            priority=EventPriority.LOW
        )
        
        payload = {
            "status": "alive",
            "timestamp": datetime.now().isoformat(),
            "system_metrics": {
                "cpu_usage": 0.0,  # To be filled by monitoring system
                "memory_usage": 0.0,
                "active_connections": 0
            }
        }
        
        return BridgeMessage(header=header, payload=payload)
    
    @staticmethod
    def create_error(sender: str, error_code: str, error_message: str, 
                    correlation_id: Optional[str] = None) -> BridgeMessage:
        """Create error message for error reporting."""
        header = MessageHeader(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.ERROR,
            timestamp=datetime.now(),
            sender=sender,
            recipient="bridge",
            priority=EventPriority.HIGH,
            correlation_id=correlation_id
        )
        
        payload = {
            "error_code": error_code,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat(),
            "recovery_suggestions": []
        }
        
        return BridgeMessage(header=header, payload=payload)
    
    @staticmethod
    def create_game_state_sync(sender: str, game_state: GameState) -> BridgeMessage:
        """Create full game state synchronization message."""
        header = MessageHeader(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.FULL_STATE_SYNC,
            timestamp=datetime.now(),
            sender=sender,
            recipient="game_engine",
            priority=EventPriority.NORMAL
        )
        
        payload = {
            "game_state": game_state.to_dict(),
            "sync_timestamp": datetime.now().isoformat()
        }
        
        return BridgeMessage(header=header, payload=payload)
    
    @staticmethod
    def create_political_event(sender: str, event: PoliticalEvent) -> BridgeMessage:
        """Create political event notification message."""
        header = MessageHeader(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.POLITICAL_EVENT,
            timestamp=datetime.now(),
            sender=sender,
            recipient="game_engine",
            priority=EventPriority.NORMAL if event.severity in ["minor", "moderate"] else EventPriority.HIGH
        )
        
        payload = {
            "event": event.to_dict()
        }
        
        return BridgeMessage(header=header, payload=payload)


# Error codes for standardized error handling
class BridgeErrorCodes:
    """Standardized error codes for bridge communication."""
    
    # Connection errors
    CONNECTION_FAILED = "CONNECTION_FAILED"
    CONNECTION_TIMEOUT = "CONNECTION_TIMEOUT"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    
    # Protocol errors
    INVALID_MESSAGE_FORMAT = "INVALID_MESSAGE_FORMAT"
    UNSUPPORTED_API_VERSION = "UNSUPPORTED_API_VERSION"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    
    # State synchronization errors
    STATE_SYNC_FAILED = "STATE_SYNC_FAILED"
    STATE_VALIDATION_FAILED = "STATE_VALIDATION_FAILED"
    TURN_SYNC_ERROR = "TURN_SYNC_ERROR"
    
    # Processing errors
    COMMAND_PROCESSING_FAILED = "COMMAND_PROCESSING_FAILED"
    EVENT_DELIVERY_FAILED = "EVENT_DELIVERY_FAILED"
    PERFORMANCE_THRESHOLD_EXCEEDED = "PERFORMANCE_THRESHOLD_EXCEEDED"
