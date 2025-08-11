"""
Turn Synchronization System

This module handles turn-based game synchronization between the political
simulation engine and game engines, ensuring coordinated turn progression
and state consistency.
"""

import asyncio
import logging
import threading
import time
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict

from . import (
    BridgeMessage, MessageType, MessageHeader, EventPriority,
    MessageFactory, TurnState
)


class TurnPhase(Enum):
    """Phases within a single turn."""
    PLANNING = "planning"
    EXECUTION = "execution"
    RESOLUTION = "resolution"
    WAITING = "waiting"  # Waiting for game engine confirmation


class SyncStatus(Enum):
    """Turn synchronization status."""
    SYNCHRONIZED = "synchronized"
    WAITING_FOR_GAME_ENGINE = "waiting_for_game_engine"
    WAITING_FOR_POLITICAL_ENGINE = "waiting_for_political_engine"
    DESYNCHRONIZED = "desynchronized"
    ERROR = "error"


@dataclass
class TurnSyncState:
    """Complete turn synchronization state."""
    turn_number: int
    phase: TurnPhase
    sync_status: SyncStatus
    political_engine_ready: bool
    game_engine_ready: bool
    turn_start_time: Optional[datetime] = None
    phase_start_time: Optional[datetime] = None
    timeout_deadline: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['phase'] = self.phase.value
        data['sync_status'] = self.sync_status.value
        if self.turn_start_time:
            data['turn_start_time'] = self.turn_start_time.isoformat()
        if self.phase_start_time:
            data['phase_start_time'] = self.phase_start_time.isoformat()
        if self.timeout_deadline:
            data['timeout_deadline'] = self.timeout_deadline.isoformat()
        return data


class TurnSynchronizer:
    """
    Manages turn synchronization between political engine and game engine.
    
    Coordinates turn progression, phase transitions, and ensures both engines
    are synchronized before advancing to the next turn or phase.
    """
    
    def __init__(self,
                 turn_timeout: float = 300.0,  # 5 minutes default
                 phase_timeout: float = 60.0,   # 1 minute default
                 auto_advance: bool = False):
        """
        Initialize turn synchronizer.
        
        Args:
            turn_timeout: Maximum time allowed per turn (seconds)
            phase_timeout: Maximum time allowed per phase (seconds)  
            auto_advance: Whether to auto-advance turns when both engines ready
        """
        self.turn_timeout = turn_timeout
        self.phase_timeout = phase_timeout
        self.auto_advance = auto_advance
        
        # Current synchronization state
        self.current_state = TurnSyncState(
            turn_number=1,
            phase=TurnPhase.PLANNING,
            sync_status=SyncStatus.SYNCHRONIZED,
            political_engine_ready=True,
            game_engine_ready=False
        )
        
        # Turn history and recovery
        self.turn_history: List[TurnSyncState] = []
        self.rollback_states: Dict[int, TurnSyncState] = {}
        
        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = {}
        
        # Threading and async
        self.monitor_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Turn Synchronizer initialized")
    
    def start(self):
        """Start the turn synchronizer."""
        if self.running:
            return
        
        self.running = True
        self.current_state.turn_start_time = datetime.now()
        self.current_state.phase_start_time = datetime.now()
        self._update_timeout_deadline()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(
            target=self._run_monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()
        
        self.logger.info("Turn Synchronizer started")
        self._emit_event("synchronizer_started", {"state": self.current_state.to_dict()})
    
    def stop(self):
        """Stop the turn synchronizer."""
        self.running = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Turn Synchronizer stopped")
        self._emit_event("synchronizer_stopped", {})
    
    def _run_monitor_loop(self):
        """Main monitoring loop for turn synchronization."""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check for timeouts
                if (self.current_state.timeout_deadline and 
                    current_time > self.current_state.timeout_deadline):
                    self._handle_timeout()
                
                # Check for auto-advance conditions
                if (self.auto_advance and 
                    self.current_state.political_engine_ready and
                    self.current_state.game_engine_ready):
                    self._auto_advance_turn()
                
                # Update sync status
                self._update_sync_status()
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Monitor loop error: {e}")
                time.sleep(5)  # Brief pause on error
    
    def _update_timeout_deadline(self):
        """Update timeout deadline based on current phase."""
        if self.current_state.phase_start_time:
            if self.current_state.phase == TurnPhase.PLANNING:
                timeout = self.turn_timeout
            else:
                timeout = self.phase_timeout
            
            self.current_state.timeout_deadline = (
                self.current_state.phase_start_time + timedelta(seconds=timeout)
            )
    
    def _update_sync_status(self):
        """Update synchronization status based on engine readiness."""
        old_status = self.current_state.sync_status
        
        if self.current_state.political_engine_ready and self.current_state.game_engine_ready:
            self.current_state.sync_status = SyncStatus.SYNCHRONIZED
        elif not self.current_state.political_engine_ready:
            self.current_state.sync_status = SyncStatus.WAITING_FOR_POLITICAL_ENGINE
        elif not self.current_state.game_engine_ready:
            self.current_state.sync_status = SyncStatus.WAITING_FOR_GAME_ENGINE
        else:
            self.current_state.sync_status = SyncStatus.DESYNCHRONIZED
        
        # Emit event if status changed
        if old_status != self.current_state.sync_status:
            self._emit_event("sync_status_changed", {
                "old_status": old_status.value,
                "new_status": self.current_state.sync_status.value,
                "state": self.current_state.to_dict()
            })
    
    def _handle_timeout(self):
        """Handle turn or phase timeout."""
        self.logger.warning(f"Timeout occurred in turn {self.current_state.turn_number}, "
                           f"phase {self.current_state.phase.value}")
        
        # Force advance to next phase or turn
        if self.current_state.phase == TurnPhase.RESOLUTION:
            # Force turn advance
            self._force_advance_turn()
        else:
            # Force phase advance
            self._force_advance_phase()
        
        self._emit_event("timeout_occurred", {
            "turn": self.current_state.turn_number,
            "phase": self.current_state.phase.value,
            "state": self.current_state.to_dict()
        })
    
    def _auto_advance_turn(self):
        """Automatically advance turn when both engines are ready."""
        if self.current_state.sync_status == SyncStatus.SYNCHRONIZED:
            if self.current_state.phase == TurnPhase.RESOLUTION:
                self.advance_turn()
            else:
                self.advance_phase()
    
    def _force_advance_turn(self):
        """Force turn advancement regardless of engine readiness."""
        self.logger.warning(f"Forcing turn advance from turn {self.current_state.turn_number}")
        self.advance_turn(force=True)
    
    def _force_advance_phase(self):
        """Force phase advancement regardless of engine readiness."""
        self.logger.warning(f"Forcing phase advance from {self.current_state.phase.value}")
        self.advance_phase(force=True)
    
    # Public API methods
    def set_political_engine_ready(self, ready: bool):
        """Set political engine readiness state."""
        old_ready = self.current_state.political_engine_ready
        self.current_state.political_engine_ready = ready
        
        if old_ready != ready:
            self.logger.info(f"Political engine ready state changed: {ready}")
            self._emit_event("political_engine_ready_changed", {
                "ready": ready,
                "state": self.current_state.to_dict()
            })
    
    def set_game_engine_ready(self, ready: bool):
        """Set game engine readiness state."""
        old_ready = self.current_state.game_engine_ready
        self.current_state.game_engine_ready = ready
        
        if old_ready != ready:
            self.logger.info(f"Game engine ready state changed: {ready}")
            self._emit_event("game_engine_ready_changed", {
                "ready": ready,
                "state": self.current_state.to_dict()
            })
    
    def advance_phase(self, force: bool = False) -> bool:
        """
        Advance to next phase within current turn.
        
        Args:
            force: Force advancement regardless of readiness
            
        Returns:
            True if phase was advanced, False otherwise
        """
        if not force and self.current_state.sync_status != SyncStatus.SYNCHRONIZED:
            self.logger.warning("Cannot advance phase - engines not synchronized")
            return False
        
        # Save current state for potential rollback
        self.rollback_states[self.current_state.turn_number] = TurnSyncState(**asdict(self.current_state))
        
        # Determine next phase
        current_phase = self.current_state.phase
        if current_phase == TurnPhase.PLANNING:
            next_phase = TurnPhase.EXECUTION
        elif current_phase == TurnPhase.EXECUTION:
            next_phase = TurnPhase.RESOLUTION
        elif current_phase == TurnPhase.RESOLUTION:
            # Should advance turn instead
            return self.advance_turn(force)
        else:
            next_phase = TurnPhase.PLANNING
        
        # Update state
        self.current_state.phase = next_phase
        self.current_state.phase_start_time = datetime.now()
        self.current_state.political_engine_ready = False
        self.current_state.game_engine_ready = False
        self._update_timeout_deadline()
        
        self.logger.info(f"Advanced to phase {next_phase.value} in turn {self.current_state.turn_number}")
        
        self._emit_event("phase_advanced", {
            "turn": self.current_state.turn_number,
            "old_phase": current_phase.value,
            "new_phase": next_phase.value,
            "forced": force,
            "state": self.current_state.to_dict()
        })
        
        return True
    
    def advance_turn(self, force: bool = False) -> bool:
        """
        Advance to next turn.
        
        Args:
            force: Force advancement regardless of readiness
            
        Returns:
            True if turn was advanced, False otherwise
        """
        if not force and self.current_state.sync_status != SyncStatus.SYNCHRONIZED:
            self.logger.warning("Cannot advance turn - engines not synchronized")
            return False
        
        # Save current state to history
        self.turn_history.append(TurnSyncState(**asdict(self.current_state)))
        
        # Update to next turn
        old_turn = self.current_state.turn_number
        self.current_state.turn_number += 1
        self.current_state.phase = TurnPhase.PLANNING
        self.current_state.turn_start_time = datetime.now()
        self.current_state.phase_start_time = datetime.now()
        self.current_state.political_engine_ready = False
        self.current_state.game_engine_ready = False
        self._update_timeout_deadline()
        
        self.logger.info(f"Advanced from turn {old_turn} to turn {self.current_state.turn_number}")
        
        self._emit_event("turn_advanced", {
            "old_turn": old_turn,
            "new_turn": self.current_state.turn_number,
            "forced": force,
            "state": self.current_state.to_dict()
        })
        
        return True
    
    def rollback_turn(self, target_turn: int) -> bool:
        """
        Rollback to a previous turn state.
        
        Args:
            target_turn: Turn number to rollback to
            
        Returns:
            True if rollback was successful, False otherwise
        """
        if target_turn in self.rollback_states:
            old_turn = self.current_state.turn_number
            self.current_state = TurnSyncState(**asdict(self.rollback_states[target_turn]))
            
            self.logger.warning(f"Rolled back from turn {old_turn} to turn {target_turn}")
            
            self._emit_event("turn_rolled_back", {
                "old_turn": old_turn,
                "target_turn": target_turn,
                "state": self.current_state.to_dict()
            })
            
            return True
        else:
            self.logger.error(f"Cannot rollback to turn {target_turn} - state not found")
            return False
    
    def get_current_state(self) -> TurnSyncState:
        """Get current synchronization state."""
        return TurnSyncState(**asdict(self.current_state))
    
    def get_turn_history(self) -> List[TurnSyncState]:
        """Get turn history."""
        return [TurnSyncState(**asdict(state)) for state in self.turn_history]
    
    def create_turn_start_message(self) -> BridgeMessage:
        """Create turn start notification message."""
        header = MessageHeader(
            message_id=f"turn_start_{self.current_state.turn_number}",
            message_type=MessageType.TURN_START,
            timestamp=datetime.now(),
            sender="political_engine",
            recipient="game_engine",
            priority=EventPriority.HIGH
        )
        
        payload = {
            "turn_state": self.current_state.to_dict(),
            "turn_number": self.current_state.turn_number,
            "phase": self.current_state.phase.value,
            "timeout_deadline": self.current_state.timeout_deadline.isoformat() if self.current_state.timeout_deadline else None
        }
        
        return BridgeMessage(header=header, payload=payload)
    
    def create_turn_end_message(self) -> BridgeMessage:
        """Create turn end notification message."""
        header = MessageHeader(
            message_id=f"turn_end_{self.current_state.turn_number}",
            message_type=MessageType.TURN_END,
            timestamp=datetime.now(),
            sender="political_engine",
            recipient="game_engine",
            priority=EventPriority.HIGH
        )
        
        payload = {
            "completed_turn": self.current_state.turn_number,
            "next_turn": self.current_state.turn_number + 1,
            "turn_duration": (datetime.now() - self.current_state.turn_start_time).total_seconds() if self.current_state.turn_start_time else 0
        }
        
        return BridgeMessage(header=header, payload=payload)
    
    # Event system
    def subscribe_to_event(self, event_type: str, callback: Callable):
        """Subscribe to synchronizer events."""
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
    
    # Configuration
    def configure(self, 
                  turn_timeout: Optional[float] = None,
                  phase_timeout: Optional[float] = None,
                  auto_advance: Optional[bool] = None):
        """Update synchronizer configuration."""
        if turn_timeout is not None:
            self.turn_timeout = turn_timeout
        if phase_timeout is not None:
            self.phase_timeout = phase_timeout
        if auto_advance is not None:
            self.auto_advance = auto_advance
        
        # Update current timeout deadline
        self._update_timeout_deadline()
        
        self.logger.info("Turn synchronizer configuration updated")
        self._emit_event("configuration_updated", {
            "turn_timeout": self.turn_timeout,
            "phase_timeout": self.phase_timeout,
            "auto_advance": self.auto_advance
        })
