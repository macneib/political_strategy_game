"""
Game State Serialization System

This module handles serialization and deserialization of political simulation
state for communication with game engines, including incremental updates
and state validation.
"""

import json
import logging
import hashlib
import gzip
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from copy import deepcopy

from . import GameState, CivilizationState, AdvisorState, TurnState


@dataclass
class SerializationMetadata:
    """Metadata for state serialization."""
    timestamp: datetime
    version: str
    checksum: str
    compression: bool
    incremental: bool
    base_version: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class StateChange:
    """Represents a change in game state."""
    path: str  # JSON path to changed field
    old_value: Any
    new_value: Any
    change_type: str  # "added", "modified", "removed"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


@dataclass
class IncrementalUpdate:
    """Incremental state update containing only changes."""
    base_checksum: str
    changes: List[StateChange]
    metadata: SerializationMetadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'base_checksum': self.base_checksum,
            'changes': [change.to_dict() for change in self.changes],
            'metadata': self.metadata.to_dict()
        }


class GameStateSerializer:
    """
    Handles serialization, deserialization, and incremental updates
    of political simulation game state.
    """
    
    def __init__(self, 
                 compress_state: bool = True,
                 track_changes: bool = True,
                 max_history: int = 100):
        """
        Initialize game state serializer.
        
        Args:
            compress_state: Whether to compress serialized state
            track_changes: Whether to track state changes for incremental updates
            max_history: Maximum number of state versions to keep in history
        """
        self.compress_state = compress_state
        self.track_changes = track_changes
        self.max_history = max_history
        
        # State tracking
        self.state_history: List[Tuple[str, GameState]] = []  # (checksum, state)
        self.current_state: Optional[GameState] = None
        self.current_checksum: Optional[str] = None
        
        # Change tracking
        self.tracked_fields: Set[str] = {
            'turn_state.turn_number',
            'turn_state.phase',
            'advisors.*.loyalty',
            'advisors.*.influence',
            'advisors.*.stress_level',
            'advisors.*.current_mood',
            'advisors.*.relationships.*',
            'civilizations.*.political_stability',
            'civilizations.*.economic_strength',
            'civilizations.*.military_power',
            'civilizations.*.diplomatic_relations.*',
            'civilizations.*.active_crises',
            'civilizations.*.active_conspiracies',
            'global_events'
        }
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Game State Serializer initialized")
    
    def serialize_full_state(self, game_state: GameState) -> Dict[str, Any]:
        """
        Serialize complete game state to dictionary.
        
        Args:
            game_state: Complete game state to serialize
            
        Returns:
            Serialized state with metadata
        """
        try:
            # Convert state to dictionary
            state_dict = game_state.to_dict()
            
            # Calculate checksum
            checksum = self._calculate_checksum(state_dict)
            
            # Create metadata
            metadata = SerializationMetadata(
                timestamp=datetime.now(),
                version="1.0",
                checksum=checksum,
                compression=self.compress_state,
                incremental=False
            )
            
            # Prepare serialized state
            serialized = {
                'metadata': metadata.to_dict(),
                'state': state_dict
            }
            
            # Update tracking
            if self.track_changes:
                self._update_state_tracking(checksum, game_state)
            
            self.logger.debug(f"Serialized full state with checksum: {checksum}")
            return serialized
            
        except Exception as e:
            self.logger.error(f"Failed to serialize full state: {e}")
            raise
    
    def serialize_full_state_json(self, game_state: GameState) -> str:
        """
        Serialize complete game state to JSON string.
        
        Args:
            game_state: Complete game state to serialize
            
        Returns:
            JSON string representation
        """
        serialized = self.serialize_full_state(game_state)
        json_str = json.dumps(serialized, indent=2)
        
        if self.compress_state:
            # Compress JSON string
            compressed = gzip.compress(json_str.encode('utf-8'))
            # Return base64 encoded compressed data with metadata
            import base64
            return base64.b64encode(compressed).decode('utf-8')
        
        return json_str
    
    def create_incremental_update(self, new_state: GameState) -> Optional[IncrementalUpdate]:
        """
        Create incremental update from current state to new state.
        
        Args:
            new_state: New game state to compare against current
            
        Returns:
            Incremental update or None if no changes
        """
        if not self.track_changes or not self.current_state:
            self.logger.warning("Cannot create incremental update - change tracking disabled or no current state")
            return None
        
        try:
            # Calculate new state checksum
            new_state_dict = new_state.to_dict()
            new_checksum = self._calculate_checksum(new_state_dict)
            
            # Find changes
            changes = self._detect_changes(self.current_state, new_state)
            
            if not changes:
                self.logger.debug("No changes detected for incremental update")
                return None
            
            # Create metadata
            metadata = SerializationMetadata(
                timestamp=datetime.now(),
                version="1.0",
                checksum=new_checksum,
                compression=False,
                incremental=True,
                base_version=self.current_checksum
            )
            
            # Create incremental update
            update = IncrementalUpdate(
                base_checksum=self.current_checksum,
                changes=changes,
                metadata=metadata
            )
            
            # Update tracking
            self._update_state_tracking(new_checksum, new_state)
            
            self.logger.debug(f"Created incremental update with {len(changes)} changes")
            return update
            
        except Exception as e:
            self.logger.error(f"Failed to create incremental update: {e}")
            raise
    
    def serialize_incremental_update(self, update: IncrementalUpdate) -> str:
        """
        Serialize incremental update to JSON string.
        
        Args:
            update: Incremental update to serialize
            
        Returns:
            JSON string representation
        """
        return json.dumps(update.to_dict(), indent=2)
    
    def deserialize_full_state(self, serialized_data: Dict[str, Any]) -> GameState:
        """
        Deserialize complete game state from dictionary.
        
        Args:
            serialized_data: Serialized state data
            
        Returns:
            Reconstructed game state
        """
        try:
            # Extract state data
            state_data = serialized_data['state']
            metadata = serialized_data['metadata']
            
            # Validate checksum if present
            if 'checksum' in metadata:
                calculated_checksum = self._calculate_checksum(state_data)
                if calculated_checksum != metadata['checksum']:
                    raise ValueError(f"Checksum mismatch: expected {metadata['checksum']}, got {calculated_checksum}")
            
            # Reconstruct state objects
            turn_state = TurnState(**state_data['turn_state'])
            
            civilizations = [
                CivilizationState(**civ_data)
                for civ_data in state_data['civilizations']
            ]
            
            advisors = [
                AdvisorState(**advisor_data)
                for advisor_data in state_data['advisors']
            ]
            
            game_state = GameState(
                turn_state=turn_state,
                civilizations=civilizations,
                advisors=advisors,
                global_events=state_data['global_events'],
                metadata=state_data['metadata']
            )
            
            self.logger.debug("Successfully deserialized full state")
            return game_state
            
        except Exception as e:
            self.logger.error(f"Failed to deserialize full state: {e}")
            raise
    
    def deserialize_full_state_json(self, json_data: str) -> GameState:
        """
        Deserialize complete game state from JSON string.
        
        Args:
            json_data: JSON string or compressed data
            
        Returns:
            Reconstructed game state
        """
        try:
            # Check if data is compressed (base64 encoded)
            if self._is_base64(json_data):
                import base64
                # Decode and decompress
                compressed_data = base64.b64decode(json_data)
                json_data = gzip.decompress(compressed_data).decode('utf-8')
            
            # Parse JSON
            serialized_data = json.loads(json_data)
            return self.deserialize_full_state(serialized_data)
            
        except Exception as e:
            self.logger.error(f"Failed to deserialize JSON state: {e}")
            raise
    
    def apply_incremental_update(self, base_state: GameState, update: IncrementalUpdate) -> GameState:
        """
        Apply incremental update to base state.
        
        Args:
            base_state: Base game state
            update: Incremental update to apply
            
        Returns:
            Updated game state
        """
        try:
            # Validate base state checksum
            base_dict = base_state.to_dict()
            base_checksum = self._calculate_checksum(base_dict)
            
            if base_checksum != update.base_checksum:
                raise ValueError(f"Base state checksum mismatch: expected {update.base_checksum}, got {base_checksum}")
            
            # Apply changes
            updated_dict = deepcopy(base_dict)
            
            for change in update.changes:
                self._apply_change(updated_dict, change)
            
            # Reconstruct game state
            updated_state = self.deserialize_full_state({'state': updated_dict, 'metadata': {}})
            
            # Validate final checksum
            final_checksum = self._calculate_checksum(updated_dict)
            if final_checksum != update.metadata.checksum:
                raise ValueError(f"Final state checksum mismatch: expected {update.metadata.checksum}, got {final_checksum}")
            
            self.logger.debug(f"Successfully applied incremental update with {len(update.changes)} changes")
            return updated_state
            
        except Exception as e:
            self.logger.error(f"Failed to apply incremental update: {e}")
            raise
    
    def validate_state(self, game_state: GameState) -> List[str]:
        """
        Validate game state for consistency and completeness.
        
        Args:
            game_state: Game state to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        try:
            # Validate turn state
            if game_state.turn_state.turn_number < 1:
                errors.append("Turn number must be >= 1")
            
            # Validate civilizations
            civ_ids = set()
            for civ in game_state.civilizations:
                if civ.civilization_id in civ_ids:
                    errors.append(f"Duplicate civilization ID: {civ.civilization_id}")
                civ_ids.add(civ.civilization_id)
                
                # Validate stability values
                if not 0.0 <= civ.political_stability <= 1.0:
                    errors.append(f"Invalid political stability for {civ.civilization_id}: {civ.political_stability}")
            
            # Validate advisors
            advisor_ids = set()
            for advisor in game_state.advisors:
                if advisor.advisor_id in advisor_ids:
                    errors.append(f"Duplicate advisor ID: {advisor.advisor_id}")
                advisor_ids.add(advisor.advisor_id)
                
                # Validate loyalty values
                if not 0.0 <= advisor.loyalty <= 1.0:
                    errors.append(f"Invalid loyalty for {advisor.advisor_id}: {advisor.loyalty}")
                
                # Validate relationships
                for rel_id, rel_value in advisor.relationships.items():
                    if rel_id not in advisor_ids and rel_id != advisor.advisor_id:
                        # Allow forward references
                        pass
                    if not -1.0 <= rel_value <= 1.0:
                        errors.append(f"Invalid relationship value for {advisor.advisor_id}->{rel_id}: {rel_value}")
            
            self.logger.debug(f"State validation completed with {len(errors)} errors")
            
        except Exception as e:
            errors.append(f"Validation error: {e}")
            self.logger.error(f"State validation failed: {e}")
        
        return errors
    
    def get_state_statistics(self, game_state: GameState) -> Dict[str, Any]:
        """
        Get statistics about the game state.
        
        Args:
            game_state: Game state to analyze
            
        Returns:
            Dictionary of statistics
        """
        try:
            state_dict = game_state.to_dict()
            
            stats = {
                'turn_number': game_state.turn_state.turn_number,
                'civilization_count': len(game_state.civilizations),
                'advisor_count': len(game_state.advisors),
                'global_event_count': len(game_state.global_events),
                'total_crises': sum(len(civ.active_crises) for civ in game_state.civilizations),
                'total_conspiracies': sum(len(civ.active_conspiracies) for civ in game_state.civilizations),
                'serialized_size_bytes': len(json.dumps(state_dict)),
                'checksum': self._calculate_checksum(state_dict),
                'timestamp': datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to calculate state statistics: {e}")
            return {}
    
    # Private helper methods
    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate SHA-256 checksum of serialized data."""
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def _update_state_tracking(self, checksum: str, state: GameState):
        """Update internal state tracking."""
        self.current_state = deepcopy(state)
        self.current_checksum = checksum
        
        # Add to history
        self.state_history.append((checksum, deepcopy(state)))
        
        # Trim history if too long
        if len(self.state_history) > self.max_history:
            self.state_history = self.state_history[-self.max_history:]
    
    def _detect_changes(self, old_state: GameState, new_state: GameState) -> List[StateChange]:
        """Detect changes between two game states."""
        changes = []
        
        try:
            old_dict = old_state.to_dict()
            new_dict = new_state.to_dict()
            
            # Compare dictionaries recursively
            self._compare_dicts(old_dict, new_dict, "", changes)
            
        except Exception as e:
            self.logger.error(f"Failed to detect changes: {e}")
        
        return changes
    
    def _compare_dicts(self, old_dict: Dict, new_dict: Dict, path: str, changes: List[StateChange]):
        """Recursively compare dictionaries and record changes."""
        # Check for removed keys
        for key in old_dict:
            key_path = f"{path}.{key}" if path else key
            if key not in new_dict:
                changes.append(StateChange(
                    path=key_path,
                    old_value=old_dict[key],
                    new_value=None,
                    change_type="removed"
                ))
        
        # Check for added or modified keys
        for key in new_dict:
            key_path = f"{path}.{key}" if path else key
            if key not in old_dict:
                changes.append(StateChange(
                    path=key_path,
                    old_value=None,
                    new_value=new_dict[key],
                    change_type="added"
                ))
            elif old_dict[key] != new_dict[key]:
                if isinstance(old_dict[key], dict) and isinstance(new_dict[key], dict):
                    # Recursively compare nested dictionaries
                    self._compare_dicts(old_dict[key], new_dict[key], key_path, changes)
                else:
                    changes.append(StateChange(
                        path=key_path,
                        old_value=old_dict[key],
                        new_value=new_dict[key],
                        change_type="modified"
                    ))
    
    def _apply_change(self, data_dict: Dict, change: StateChange):
        """Apply a single change to a dictionary."""
        path_parts = change.path.split('.')
        
        # Navigate to parent object
        current = data_dict
        for part in path_parts[:-1]:
            if part.isdigit():
                # Array index
                current = current[int(part)]
            else:
                current = current[part]
        
        # Apply change
        final_key = path_parts[-1]
        if change.change_type == "removed":
            if final_key in current:
                del current[final_key]
        elif change.change_type in ["added", "modified"]:
            if final_key.isdigit():
                # Array index
                current[int(final_key)] = change.new_value
            else:
                current[final_key] = change.new_value
    
    def _is_base64(self, data: str) -> bool:
        """Check if string is base64 encoded."""
        try:
            import base64
            if len(data) % 4 != 0:
                return False
            base64.b64decode(data, validate=True)
            return True
        except Exception:
            return False
