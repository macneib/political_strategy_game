"""
Political Event Broadcasting System

This module handles real-time broadcasting of political events to game engines,
including event filtering, subscription management, and event replay capabilities.
"""

import asyncio
import logging
import threading
import time
from typing import Dict, List, Optional, Callable, Any, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from queue import Queue, Empty, PriorityQueue
from collections import defaultdict

from . import (
    BridgeMessage, MessageType, MessageHeader, EventPriority,
    MessageFactory, PoliticalEvent
)


class EventCategory(Enum):
    """Categories of political events."""
    ADVISOR = "advisor"
    CRISIS = "crisis"
    CONSPIRACY = "conspiracy"
    DIPLOMATIC = "diplomatic"
    ECONOMIC = "economic"
    MILITARY = "military"
    SOCIAL = "social"
    SYSTEM = "system"


class SubscriptionFilter:
    """Event subscription filter configuration."""
    
    def __init__(self,
                 categories: Optional[List[EventCategory]] = None,
                 severities: Optional[List[str]] = None,
                 civilizations: Optional[List[str]] = None,
                 participants: Optional[List[str]] = None,
                 keywords: Optional[List[str]] = None):
        """
        Initialize subscription filter.
        
        Args:
            categories: Event categories to include
            severities: Event severities to include ("minor", "moderate", "major", "critical")
            civilizations: Civilization IDs to include
            participants: Participant IDs to include (advisor/civilization IDs)
            keywords: Keywords to match in event titles/descriptions
        """
        self.categories = categories or []
        self.severities = severities or []
        self.civilizations = civilizations or []
        self.participants = participants or []
        self.keywords = keywords or []
    
    def matches(self, event: PoliticalEvent) -> bool:
        """Check if event matches this filter."""
        # Check categories
        if self.categories:
            event_category = self._determine_event_category(event)
            if event_category not in self.categories:
                return False
        
        # Check severities
        if self.severities and event.severity not in self.severities:
            return False
        
        # Check civilizations
        if self.civilizations and event.civilization_id not in self.civilizations:
            return False
        
        # Check participants
        if self.participants:
            if not any(p in event.participants for p in self.participants):
                return False
        
        # Check keywords
        if self.keywords:
            text = f"{event.title} {event.description}".lower()
            if not any(keyword.lower() in text for keyword in self.keywords):
                return False
        
        return True
    
    def _determine_event_category(self, event: PoliticalEvent) -> EventCategory:
        """Determine event category from event type."""
        event_type = event.event_type.lower()
        
        if "advisor" in event_type or "loyalty" in event_type:
            return EventCategory.ADVISOR
        elif "crisis" in event_type or "emergency" in event_type:
            return EventCategory.CRISIS
        elif "conspiracy" in event_type or "coup" in event_type:
            return EventCategory.CONSPIRACY
        elif "diplomatic" in event_type or "negotiation" in event_type:
            return EventCategory.DIPLOMATIC
        elif "economic" in event_type or "trade" in event_type:
            return EventCategory.ECONOMIC
        elif "military" in event_type or "war" in event_type:
            return EventCategory.MILITARY
        elif "social" in event_type or "public" in event_type:
            return EventCategory.SOCIAL
        else:
            return EventCategory.SYSTEM


@dataclass
class EventSubscription:
    """Event subscription configuration."""
    subscription_id: str
    connection_id: str
    filter: SubscriptionFilter
    created_at: datetime
    last_event_at: Optional[datetime] = None
    event_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        if self.last_event_at:
            data['last_event_at'] = self.last_event_at.isoformat()
        return data


@dataclass
class EventBatch:
    """Batch of events for efficient transmission."""
    batch_id: str
    events: List[PoliticalEvent]
    timestamp: datetime
    priority: EventPriority
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'batch_id': self.batch_id,
            'events': [event.to_dict() for event in self.events],
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority.value,
            'event_count': len(self.events)
        }


class PoliticalEventBroadcaster:
    """
    Manages real-time broadcasting of political events to game engines
    with subscription filtering and event replay capabilities.
    """
    
    def __init__(self,
                 max_event_history: int = 10000,
                 batch_size: int = 10,
                 batch_timeout: float = 5.0,
                 replay_buffer_hours: int = 24):
        """
        Initialize event broadcaster.
        
        Args:
            max_event_history: Maximum events to keep in history
            batch_size: Maximum events per batch
            batch_timeout: Maximum time to wait before sending incomplete batch
            replay_buffer_hours: Hours of events to keep for replay
        """
        self.max_event_history = max_event_history
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.replay_buffer_hours = replay_buffer_hours
        
        # Event storage
        self.event_history: List[PoliticalEvent] = []
        self.event_queue = PriorityQueue()
        
        # Subscription management
        self.subscriptions: Dict[str, EventSubscription] = {}
        self.connection_subscriptions: Dict[str, List[str]] = defaultdict(list)
        
        # Batching
        self.pending_batches: Dict[str, List[PoliticalEvent]] = defaultdict(list)
        self.last_batch_time: Dict[str, datetime] = {}
        
        # Broadcasting
        self.broadcast_callbacks: List[Callable] = []
        
        # Threading
        self.processor_thread: Optional[threading.Thread] = None
        self.batcher_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Performance metrics
        self.metrics = {
            "events_processed": 0,
            "events_broadcasted": 0,
            "active_subscriptions": 0,
            "batches_sent": 0,
            "replay_requests": 0
        }
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Political Event Broadcaster initialized")
    
    def start(self):
        """Start the event broadcaster."""
        if self.running:
            return
        
        self.running = True
        
        # Start processing threads
        self.processor_thread = threading.Thread(
            target=self._run_event_processor,
            daemon=True
        )
        self.processor_thread.start()
        
        self.batcher_thread = threading.Thread(
            target=self._run_batch_processor,
            daemon=True
        )
        self.batcher_thread.start()
        
        self.logger.info("Political Event Broadcaster started")
    
    def stop(self):
        """Stop the event broadcaster."""
        self.running = False
        
        # Wait for threads to finish
        if self.processor_thread and self.processor_thread.is_alive():
            self.processor_thread.join(timeout=5)
        
        if self.batcher_thread and self.batcher_thread.is_alive():
            self.batcher_thread.join(timeout=5)
        
        self.logger.info("Political Event Broadcaster stopped")
    
    def _run_event_processor(self):
        """Main event processing loop."""
        while self.running:
            try:
                # Process events from queue
                try:
                    priority, timestamp, event = self.event_queue.get(timeout=1)
                    self._process_event(event)
                    self.metrics["events_processed"] += 1
                except Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"Event processing error: {e}")
                
            except Exception as e:
                self.logger.error(f"Event processor loop error: {e}")
                time.sleep(1)
    
    def _run_batch_processor(self):
        """Batch processing loop for timed batch sends."""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check for timed-out batches
                for connection_id in list(self.pending_batches.keys()):
                    last_batch = self.last_batch_time.get(connection_id, current_time)
                    if (current_time - last_batch).total_seconds() >= self.batch_timeout:
                        if self.pending_batches[connection_id]:
                            self._send_batch(connection_id)
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Batch processor loop error: {e}")
                time.sleep(5)
    
    def _process_event(self, event: PoliticalEvent):
        """Process a single political event."""
        try:
            # Add to history
            self.event_history.append(event)
            self._trim_event_history()
            
            # Find matching subscriptions
            matching_subscriptions = self._find_matching_subscriptions(event)
            
            # Add to batches for matching connections
            for subscription in matching_subscriptions:
                connection_id = subscription.connection_id
                self.pending_batches[connection_id].append(event)
                
                # Update subscription stats
                subscription.last_event_at = datetime.now()
                subscription.event_count += 1
                
                # Send batch if full
                if len(self.pending_batches[connection_id]) >= self.batch_size:
                    self._send_batch(connection_id)
            
            self.logger.debug(f"Processed event {event.event_id} for {len(matching_subscriptions)} subscriptions")
            
        except Exception as e:
            self.logger.error(f"Failed to process event {event.event_id}: {e}")
    
    def _find_matching_subscriptions(self, event: PoliticalEvent) -> List[EventSubscription]:
        """Find subscriptions that match the given event."""
        matching = []
        
        for subscription in self.subscriptions.values():
            if subscription.filter.matches(event):
                matching.append(subscription)
        
        return matching
    
    def _send_batch(self, connection_id: str):
        """Send pending batch for connection."""
        if connection_id not in self.pending_batches or not self.pending_batches[connection_id]:
            return
        
        try:
            events = self.pending_batches[connection_id].copy()
            self.pending_batches[connection_id].clear()
            self.last_batch_time[connection_id] = datetime.now()
            
            # Determine batch priority
            priority = EventPriority.LOW
            for event in events:
                if event.severity in ["major", "critical"]:
                    priority = EventPriority.HIGH
                    break
                elif event.severity == "moderate":
                    priority = EventPriority.NORMAL
            
            # Create batch
            batch = EventBatch(
                batch_id=f"batch_{connection_id}_{int(time.time())}",
                events=events,
                timestamp=datetime.now(),
                priority=priority
            )
            
            # Broadcast batch
            self._broadcast_batch(connection_id, batch)
            self.metrics["batches_sent"] += 1
            self.metrics["events_broadcasted"] += len(events)
            
            self.logger.debug(f"Sent batch {batch.batch_id} with {len(events)} events to {connection_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to send batch for {connection_id}: {e}")
    
    def _broadcast_batch(self, connection_id: str, batch: EventBatch):
        """Broadcast event batch to connection."""
        # Create bridge message
        header = MessageHeader(
            message_id=batch.batch_id,
            message_type=MessageType.POLITICAL_EVENT,
            timestamp=batch.timestamp,
            sender="political_engine",
            recipient=connection_id,
            priority=batch.priority
        )
        
        payload = {
            'event_batch': batch.to_dict(),
            'is_batch': True
        }
        
        message = BridgeMessage(header=header, payload=payload)
        
        # Send via registered callbacks
        for callback in self.broadcast_callbacks:
            try:
                callback(connection_id, message)
            except Exception as e:
                self.logger.error(f"Broadcast callback error: {e}")
    
    def _trim_event_history(self):
        """Trim event history to maximum size."""
        if len(self.event_history) > self.max_event_history:
            # Keep most recent events
            self.event_history = self.event_history[-self.max_event_history:]
    
    # Public API methods
    def broadcast_event(self, event: PoliticalEvent, priority: EventPriority = EventPriority.NORMAL):
        """
        Broadcast political event to all matching subscribers.
        
        Args:
            event: Political event to broadcast
            priority: Event priority for processing order
        """
        try:
            # Add to processing queue
            timestamp = datetime.now()
            self.event_queue.put((priority.value, timestamp, event))
            
            self.logger.debug(f"Queued event {event.event_id} for broadcasting")
            
        except Exception as e:
            self.logger.error(f"Failed to queue event for broadcasting: {e}")
    
    def subscribe_to_events(self, connection_id: str, filter: SubscriptionFilter) -> str:
        """
        Subscribe connection to events matching filter.
        
        Args:
            connection_id: ID of the connection to subscribe
            filter: Event filter configuration
            
        Returns:
            Subscription ID
        """
        subscription_id = f"sub_{connection_id}_{int(time.time())}"
        
        subscription = EventSubscription(
            subscription_id=subscription_id,
            connection_id=connection_id,
            filter=filter,
            created_at=datetime.now()
        )
        
        self.subscriptions[subscription_id] = subscription
        self.connection_subscriptions[connection_id].append(subscription_id)
        self.metrics["active_subscriptions"] = len(self.subscriptions)
        
        self.logger.info(f"Created event subscription {subscription_id} for connection {connection_id}")
        return subscription_id
    
    def unsubscribe_from_events(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.
        
        Args:
            subscription_id: Subscription ID to remove
            
        Returns:
            True if subscription was found and removed
        """
        if subscription_id in self.subscriptions:
            subscription = self.subscriptions[subscription_id]
            connection_id = subscription.connection_id
            
            # Remove from subscriptions
            del self.subscriptions[subscription_id]
            
            # Remove from connection mapping
            if connection_id in self.connection_subscriptions:
                if subscription_id in self.connection_subscriptions[connection_id]:
                    self.connection_subscriptions[connection_id].remove(subscription_id)
                
                # Clean up empty connection entries
                if not self.connection_subscriptions[connection_id]:
                    del self.connection_subscriptions[connection_id]
            
            self.metrics["active_subscriptions"] = len(self.subscriptions)
            
            self.logger.info(f"Removed event subscription {subscription_id}")
            return True
        
        return False
    
    def unsubscribe_connection(self, connection_id: str):
        """
        Remove all subscriptions for a connection.
        
        Args:
            connection_id: Connection ID to unsubscribe
        """
        if connection_id in self.connection_subscriptions:
            subscription_ids = self.connection_subscriptions[connection_id].copy()
            
            for subscription_id in subscription_ids:
                self.unsubscribe_from_events(subscription_id)
            
            # Clean up pending batches
            if connection_id in self.pending_batches:
                del self.pending_batches[connection_id]
            if connection_id in self.last_batch_time:
                del self.last_batch_time[connection_id]
            
            self.logger.info(f"Removed all subscriptions for connection {connection_id}")
    
    def replay_events(self, connection_id: str, 
                     start_time: datetime, 
                     end_time: Optional[datetime] = None,
                     filter: Optional[SubscriptionFilter] = None) -> List[PoliticalEvent]:
        """
        Replay historical events for a connection.
        
        Args:
            connection_id: Connection requesting replay
            start_time: Start time for event replay
            end_time: End time for event replay (default: now)
            filter: Optional filter for replayed events
            
        Returns:
            List of matching historical events
        """
        try:
            end_time = end_time or datetime.now()
            
            # Check replay buffer limit
            buffer_start = datetime.now() - timedelta(hours=self.replay_buffer_hours)
            if start_time < buffer_start:
                start_time = buffer_start
                self.logger.warning(f"Replay start time adjusted to buffer limit: {buffer_start}")
            
            # Filter events by time
            matching_events = []
            for event in self.event_history:
                if start_time <= event.timestamp <= end_time:
                    if filter is None or filter.matches(event):
                        matching_events.append(event)
            
            self.metrics["replay_requests"] += 1
            
            self.logger.info(f"Replaying {len(matching_events)} events for {connection_id}")
            return matching_events
            
        except Exception as e:
            self.logger.error(f"Failed to replay events for {connection_id}: {e}")
            return []
    
    def get_subscription_info(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a subscription."""
        if subscription_id in self.subscriptions:
            return self.subscriptions[subscription_id].to_dict()
        return None
    
    def get_connection_subscriptions(self, connection_id: str) -> List[Dict[str, Any]]:
        """Get all subscriptions for a connection."""
        if connection_id in self.connection_subscriptions:
            subscription_ids = self.connection_subscriptions[connection_id]
            return [
                self.subscriptions[sub_id].to_dict()
                for sub_id in subscription_ids
                if sub_id in self.subscriptions
            ]
        return []
    
    def register_broadcast_callback(self, callback: Callable):
        """Register callback for event broadcasting."""
        self.broadcast_callbacks.append(callback)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get broadcasting metrics."""
        return self.metrics.copy()
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get event history statistics."""
        if not self.event_history:
            return {}
        
        # Count events by category and severity
        category_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        civilization_counts = defaultdict(int)
        
        recent_events = [
            e for e in self.event_history
            if (datetime.now() - e.timestamp).total_seconds() < 3600  # Last hour
        ]
        
        for event in self.event_history:
            # Determine category
            subscription_filter = SubscriptionFilter()
            category = subscription_filter._determine_event_category(event)
            category_counts[category.value] += 1
            
            severity_counts[event.severity] += 1
            civilization_counts[event.civilization_id] += 1
        
        return {
            'total_events': len(self.event_history),
            'recent_events': len(recent_events),
            'category_distribution': dict(category_counts),
            'severity_distribution': dict(severity_counts),
            'civilization_distribution': dict(civilization_counts),
            'oldest_event': self.event_history[0].timestamp.isoformat() if self.event_history else None,
            'newest_event': self.event_history[-1].timestamp.isoformat() if self.event_history else None
        }
