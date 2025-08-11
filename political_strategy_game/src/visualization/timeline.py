"""
Event Timeline Visualization

This module implements interactive timeline visualization for displaying
political events, decision consequences, and temporal patterns in the game.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import bisect

from .base import (
    VisualizationComponent, VisualizationConfig, VisualizationUpdate,
    DataPoint, UpdateType, DataFormatter
)


class TimelineViewMode(Enum):
    """Timeline view modes for different temporal perspectives."""
    REAL_TIME = "real_time"
    GAME_TURNS = "game_turns"
    CHRONOLOGICAL = "chronological"
    COMPRESSED = "compressed"


class EventCategory(Enum):
    """Categories for timeline event classification."""
    POLITICAL = "political"
    MILITARY = "military"
    ECONOMIC = "economic"
    DIPLOMATIC = "diplomatic"
    CULTURAL = "cultural"
    CRISIS = "crisis"
    DECISION = "decision"
    CONSEQUENCE = "consequence"


class TimelineEvent:
    """Represents a single event on the timeline."""
    
    def __init__(self, event_id: str, timestamp: datetime, title: str,
                 category: EventCategory, severity: float = 0.5,
                 participants: List[str] = None, description: str = "",
                 consequences: List[str] = None, metadata: Dict[str, Any] = None):
        self.event_id = event_id
        self.timestamp = timestamp
        self.title = title
        self.category = category
        self.severity = severity  # 0.0 to 1.0
        self.participants = participants or []
        self.description = description
        self.consequences = consequences or []
        self.metadata = metadata or {}
        self.related_events = []  # Links to other events
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'title': self.title,
            'category': self.category.value,
            'severity': self.severity,
            'participants': self.participants,
            'description': self.description,
            'consequences': self.consequences,
            'metadata': self.metadata,
            'related_events': self.related_events
        }


class TimelineScale:
    """Manages temporal scaling and positioning for timeline visualization."""
    
    def __init__(self, start_time: datetime, end_time: datetime, width: int = 1000):
        self.start_time = start_time
        self.end_time = end_time
        self.width = width
        self.time_span = (end_time - start_time).total_seconds()
        
    def time_to_position(self, timestamp: datetime) -> float:
        """Convert timestamp to pixel position on timeline."""
        if self.time_span <= 0:
            return 0
        
        elapsed = (timestamp - self.start_time).total_seconds()
        position = (elapsed / self.time_span) * self.width
        return max(0, min(self.width, position))
    
    def position_to_time(self, position: float) -> datetime:
        """Convert pixel position to timestamp."""
        if self.width <= 0:
            return self.start_time
        
        time_fraction = position / self.width
        elapsed_seconds = time_fraction * self.time_span
        return self.start_time + timedelta(seconds=elapsed_seconds)
    
    def get_time_markers(self, max_markers: int = 10) -> List[Tuple[datetime, str]]:
        """Generate time markers for timeline axis."""
        markers = []
        
        if self.time_span <= 0:
            return markers
        
        # Determine appropriate time intervals
        if self.time_span < 3600:  # Less than 1 hour
            interval = max(300, self.time_span / max_markers)  # 5 min minimum
            format_str = "%H:%M"
        elif self.time_span < 86400:  # Less than 1 day
            interval = max(3600, self.time_span / max_markers)  # 1 hour minimum
            format_str = "%H:%M"
        elif self.time_span < 2592000:  # Less than 30 days
            interval = max(86400, self.time_span / max_markers)  # 1 day minimum
            format_str = "%m/%d"
        else:
            interval = max(2592000, self.time_span / max_markers)  # 30 days minimum
            format_str = "%Y/%m"
        
        current_time = self.start_time
        while current_time <= self.end_time:
            label = current_time.strftime(format_str)
            markers.append((current_time, label))
            current_time += timedelta(seconds=interval)
        
        return markers


class EventTimelineVisualization(VisualizationComponent):
    """Interactive event timeline visualization component."""
    
    def __init__(self, config: VisualizationConfig):
        super().__init__(config)
        self.events: List[TimelineEvent] = []
        self.events_by_id: Dict[str, TimelineEvent] = {}
        self.view_mode = TimelineViewMode.CHRONOLOGICAL
        self.timeline_scale = None
        
        # Configuration
        self.height = config.layout_options.get('height', 400)
        self.width = config.layout_options.get('width', 1000)
        self.lane_height = config.layout_options.get('lane_height', 60)
        self.show_consequences = config.layout_options.get('show_consequences', True)
        self.group_by_category = config.layout_options.get('group_by_category', False)
        
        # Filtering and interaction
        self.visible_categories = set(EventCategory)
        self.severity_filter = (0.0, 1.0)
        self.time_range_filter = None  # (start_time, end_time)
        self.selected_events = set()
        self.hovered_event = None
        
        # Animation state
        self.animation_enabled = config.layout_options.get('animation', True)
        self.auto_scroll_enabled = False
        self.highlight_recent_events = True
        
    async def initialize(self) -> bool:
        """Initialize the timeline visualization."""
        try:
            self.is_active = True
            return True
        except Exception as e:
            print(f"Failed to initialize timeline visualization: {e}")
            return False
    
    async def update(self, update: VisualizationUpdate) -> bool:
        """Process an update to the timeline visualization."""
        try:
            if update.update_type == UpdateType.FULL_REFRESH:
                await self._full_refresh(update.data)
            elif update.update_type == UpdateType.INCREMENTAL_UPDATE:
                await self._incremental_update(update.data)
            elif update.update_type == UpdateType.REAL_TIME_EVENT:
                await self._process_real_time_event(update.data)
            
            self.last_update = update.timestamp
            
            # Update timeline scale if needed
            await self._update_timeline_scale()
            
            # Notify subscribers
            await self.notify_subscribers({
                'type': 'timeline_updated',
                'component_id': self.config.component_id,
                'timestamp': update.timestamp.isoformat(),
                'event_count': len(self.events)
            })
            
            return True
            
        except Exception as e:
            print(f"Error updating timeline visualization: {e}")
            return False
    
    async def _full_refresh(self, data_points: List[DataPoint]):
        """Perform full refresh of timeline data."""
        new_events = []
        
        for point in data_points:
            if point.data_type == 'political_events':
                formatted_events = DataFormatter.format_political_events(point.value)
                for event_data in formatted_events:
                    event = self._create_timeline_event(event_data)
                    new_events.append(event)
        
        # Replace all events
        self.events = sorted(new_events, key=lambda e: e.timestamp)
        self.events_by_id = {event.event_id: event for event in self.events}
    
    async def _incremental_update(self, data_points: List[DataPoint]):
        """Process incremental updates to timeline data."""
        for point in data_points:
            if point.data_type == 'event_added':
                await self._add_event(point.value)
            elif point.data_type == 'event_updated':
                await self._update_event(point.value)
            elif point.data_type == 'event_removed':
                await self._remove_event(point.value['event_id'])
            elif point.data_type == 'consequence_added':
                await self._add_consequence(point.value)
    
    async def _process_real_time_event(self, data_points: List[DataPoint]):
        """Process real-time events for timeline animation."""
        for point in data_points:
            if point.data_type == 'live_event':
                await self._animate_new_event(point.value)
            elif point.data_type == 'event_highlight':
                await self._highlight_event(point.value)
    
    def _create_timeline_event(self, event_data: Dict[str, Any]) -> TimelineEvent:
        """Create TimelineEvent from data dictionary."""
        timestamp = datetime.fromisoformat(event_data['timestamp'])
        category = EventCategory(event_data.get('category', 'political'))
        
        return TimelineEvent(
            event_id=event_data['event_id'],
            timestamp=timestamp,
            title=event_data['title'],
            category=category,
            severity=event_data.get('severity', 0.5),
            participants=event_data.get('participants', []),
            description=event_data.get('description', ''),
            consequences=event_data.get('consequences', []),
            metadata=event_data.get('metadata', {})
        )
    
    async def _add_event(self, event_data: Dict[str, Any]):
        """Add new event to timeline."""
        event = self._create_timeline_event(event_data)
        
        # Insert event in chronological order
        insert_index = bisect.bisect_left(self.events, event, key=lambda e: e.timestamp)
        self.events.insert(insert_index, event)
        self.events_by_id[event.event_id] = event
        
        # Animate if enabled
        if self.animation_enabled:
            await self._animate_new_event(event_data)
    
    async def _update_event(self, event_data: Dict[str, Any]):
        """Update existing event."""
        event_id = event_data['event_id']
        
        if event_id in self.events_by_id:
            event = self.events_by_id[event_id]
            
            # Update event properties
            if 'title' in event_data:
                event.title = event_data['title']
            if 'description' in event_data:
                event.description = event_data['description']
            if 'severity' in event_data:
                event.severity = event_data['severity']
            if 'consequences' in event_data:
                event.consequences = event_data['consequences']
            if 'metadata' in event_data:
                event.metadata.update(event_data['metadata'])
    
    async def _remove_event(self, event_id: str):
        """Remove event from timeline."""
        if event_id in self.events_by_id:
            event = self.events_by_id[event_id]
            self.events.remove(event)
            del self.events_by_id[event_id]
            
            # Remove from selection if selected
            self.selected_events.discard(event_id)
    
    async def _add_consequence(self, consequence_data: Dict[str, Any]):
        """Add consequence to existing event."""
        event_id = consequence_data['event_id']
        consequence = consequence_data['consequence']
        
        if event_id in self.events_by_id:
            event = self.events_by_id[event_id]
            if consequence not in event.consequences:
                event.consequences.append(consequence)
    
    async def _update_timeline_scale(self):
        """Update timeline scale based on current events."""
        if not self.events:
            return
        
        # Determine time range
        if self.time_range_filter:
            start_time, end_time = self.time_range_filter
        else:
            start_time = min(event.timestamp for event in self.events)
            end_time = max(event.timestamp for event in self.events)
            
            # Add some padding
            time_span = end_time - start_time
            padding = time_span * 0.05  # 5% padding
            start_time -= padding
            end_time += padding
        
        self.timeline_scale = TimelineScale(start_time, end_time, self.width)
    
    def _get_event_lane(self, event: TimelineEvent) -> int:
        """Determine which lane an event should appear in to avoid overlaps."""
        if self.group_by_category:
            # Group by category
            category_lanes = {
                EventCategory.CRISIS: 0,
                EventCategory.POLITICAL: 1,
                EventCategory.MILITARY: 2,
                EventCategory.ECONOMIC: 3,
                EventCategory.DIPLOMATIC: 4,
                EventCategory.CULTURAL: 5,
                EventCategory.DECISION: 6,
                EventCategory.CONSEQUENCE: 7
            }
            return category_lanes.get(event.category, 0)
        else:
            # Simple collision detection
            if not self.timeline_scale:
                return 0
                
            event_position = self.timeline_scale.time_to_position(event.timestamp)
            lane_assignments = {}
            
            # Check for conflicts with other events
            for other_event in self.events:
                if other_event.event_id == event.event_id:
                    continue
                    
                other_position = self.timeline_scale.time_to_position(other_event.timestamp)
                if abs(event_position - other_position) < 50:  # Collision threshold
                    other_lane = lane_assignments.get(other_event.event_id, 0)
                    lane_assignments[event.event_id] = other_lane + 1
                    break
            
            return lane_assignments.get(event.event_id, 0)
    
    async def _animate_new_event(self, event_data: Dict[str, Any]):
        """Animate the appearance of a new event."""
        if self.animation_enabled:
            await self.notify_subscribers({
                'type': 'event_animation',
                'animation': 'appear',
                'event_id': event_data['event_id'],
                'duration': 1000
            })
    
    async def _highlight_event(self, event_data: Dict[str, Any]):
        """Highlight specific event temporarily."""
        await self.notify_subscribers({
            'type': 'event_highlight',
            'event_id': event_data['event_id'],
            'highlight_type': event_data.get('type', 'attention'),
            'duration': event_data.get('duration', 3000)
        })
    
    async def render(self) -> Dict[str, Any]:
        """Render the current timeline visualization state."""
        if not self.timeline_scale:
            await self._update_timeline_scale()
        
        # Apply filters and prepare events for rendering
        filtered_events = self._apply_filters()
        rendered_events = []
        
        for event in filtered_events:
            position = self.timeline_scale.time_to_position(event.timestamp)
            lane = self._get_event_lane(event)
            
            rendered_events.append({
                'event': event.to_dict(),
                'position': position,
                'lane': lane,
                'y_position': lane * self.lane_height
            })
        
        # Generate time markers
        time_markers = []
        if self.timeline_scale:
            markers = self.timeline_scale.get_time_markers()
            for timestamp, label in markers:
                position = self.timeline_scale.time_to_position(timestamp)
                time_markers.append({
                    'timestamp': timestamp.isoformat(),
                    'label': label,
                    'position': position
                })
        
        return {
            'type': 'event_timeline',
            'data': {
                'events': rendered_events,
                'time_markers': time_markers
            },
            'config': {
                'width': self.width,
                'height': self.height,
                'lane_height': self.lane_height,
                'view_mode': self.view_mode.value,
                'show_consequences': self.show_consequences,
                'group_by_category': self.group_by_category
            },
            'scale': {
                'start_time': self.timeline_scale.start_time.isoformat() if self.timeline_scale else None,
                'end_time': self.timeline_scale.end_time.isoformat() if self.timeline_scale else None,
                'time_span': self.timeline_scale.time_span if self.timeline_scale else 0
            },
            'interaction_state': {
                'selected_events': list(self.selected_events),
                'hovered_event': self.hovered_event,
                'visible_categories': [cat.value for cat in self.visible_categories]
            },
            'metadata': {
                'total_events': len(self.events),
                'visible_events': len(filtered_events),
                'time_range': self.time_range_filter,
                'last_update': self.last_update.isoformat() if self.last_update else None
            }
        }
    
    async def handle_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user interaction with the timeline."""
        interaction_type = interaction.get('type')
        
        if interaction_type == 'event_click':
            return await self._handle_event_click(interaction)
        elif interaction_type == 'event_hover':
            return await self._handle_event_hover(interaction)
        elif interaction_type == 'time_range_select':
            return await self._handle_time_range_select(interaction)
        elif interaction_type == 'filter_change':
            return await self._handle_filter_change(interaction)
        elif interaction_type == 'zoom':
            return await self._handle_zoom(interaction)
        elif interaction_type == 'pan':
            return await self._handle_pan(interaction)
        elif interaction_type == 'view_mode_change':
            return await self._handle_view_mode_change(interaction)
        
        return {'status': 'unknown_interaction', 'type': interaction_type}
    
    async def _handle_event_click(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle event click interaction."""
        event_id = interaction.get('event_id')
        
        if event_id and event_id in self.events_by_id:
            if event_id in self.selected_events:
                self.selected_events.remove(event_id)
                action = 'deselected'
            else:
                self.selected_events.add(event_id)
                action = 'selected'
            
            event = self.events_by_id[event_id]
            
            return {
                'status': 'success',
                'action': action,
                'event_id': event_id,
                'event_data': event.to_dict(),
                'selected_count': len(self.selected_events)
            }
        
        return {'status': 'error', 'message': 'Event not found'}
    
    async def _handle_event_hover(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle event hover interaction."""
        event_id = interaction.get('event_id')
        self.hovered_event = event_id
        
        if event_id and event_id in self.events_by_id:
            event = self.events_by_id[event_id]
            
            # Find related events
            related_events = []
            for related_id in event.related_events:
                if related_id in self.events_by_id:
                    related_events.append(self.events_by_id[related_id].to_dict())
            
            return {
                'status': 'success',
                'event_data': event.to_dict(),
                'related_events': related_events
            }
        
        return {'status': 'cleared'}
    
    async def _handle_time_range_select(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle time range selection."""
        start_time = interaction.get('start_time')
        end_time = interaction.get('end_time')
        
        if start_time and end_time:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            
            self.time_range_filter = (start_dt, end_dt)
            await self._update_timeline_scale()
            
            return {
                'status': 'success',
                'time_range': (start_time, end_time),
                'requires_refresh': True
            }
        
        return {'status': 'error', 'message': 'Invalid time range'}
    
    async def _handle_filter_change(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle filter changes."""
        if 'categories' in interaction:
            category_names = interaction['categories']
            self.visible_categories = {EventCategory(name) for name in category_names}
        
        if 'severity_range' in interaction:
            self.severity_filter = tuple(interaction['severity_range'])
        
        return {
            'status': 'success',
            'active_filters': {
                'categories': [cat.value for cat in self.visible_categories],
                'severity_range': self.severity_filter
            },
            'requires_refresh': True
        }
    
    async def _handle_zoom(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle timeline zoom."""
        zoom_factor = interaction.get('factor', 1.0)
        center_time = interaction.get('center_time')
        
        if center_time and self.timeline_scale:
            center_dt = datetime.fromisoformat(center_time)
            
            # Calculate new time range
            current_span = self.timeline_scale.time_span
            new_span = current_span / zoom_factor
            
            start_time = center_dt - timedelta(seconds=new_span / 2)
            end_time = center_dt + timedelta(seconds=new_span / 2)
            
            self.time_range_filter = (start_time, end_time)
            await self._update_timeline_scale()
            
            return {
                'status': 'success',
                'zoom_factor': zoom_factor,
                'new_time_range': (start_time.isoformat(), end_time.isoformat())
            }
        
        return {'status': 'error', 'message': 'Invalid zoom parameters'}
    
    async def _handle_pan(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle timeline panning."""
        direction = interaction.get('direction')  # 'left' or 'right'
        amount = interaction.get('amount', 0.1)  # Fraction of current view
        
        if direction and self.timeline_scale:
            current_span = self.timeline_scale.time_span
            shift_amount = current_span * amount
            
            if direction == 'left':
                shift_amount = -shift_amount
            
            start_time = self.timeline_scale.start_time + timedelta(seconds=shift_amount)
            end_time = self.timeline_scale.end_time + timedelta(seconds=shift_amount)
            
            self.time_range_filter = (start_time, end_time)
            await self._update_timeline_scale()
            
            return {
                'status': 'success',
                'direction': direction,
                'new_time_range': (start_time.isoformat(), end_time.isoformat())
            }
        
        return {'status': 'error', 'message': 'Invalid pan parameters'}
    
    async def _handle_view_mode_change(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle view mode change."""
        new_mode = interaction.get('mode')
        
        try:
            self.view_mode = TimelineViewMode(new_mode)
            return {
                'status': 'success',
                'new_mode': new_mode,
                'requires_refresh': True
            }
        except ValueError:
            return {'status': 'error', 'message': 'Invalid view mode'}
    
    def _apply_filters(self) -> List[TimelineEvent]:
        """Apply current filters to events."""
        filtered_events = []
        
        for event in self.events:
            # Category filter
            if event.category not in self.visible_categories:
                continue
            
            # Severity filter
            if not (self.severity_filter[0] <= event.severity <= self.severity_filter[1]):
                continue
            
            # Time range filter
            if self.time_range_filter:
                start_time, end_time = self.time_range_filter
                if not (start_time <= event.timestamp <= end_time):
                    continue
            
            filtered_events.append(event)
        
        return filtered_events
