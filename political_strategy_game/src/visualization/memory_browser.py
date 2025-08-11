"""
Memory Browser Visualization

This module implements an interactive browser for exploring advisor memories,
decision history, and political knowledge networks.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import json

from .base import (
    VisualizationComponent, VisualizationConfig, VisualizationUpdate,
    DataPoint, UpdateType, DataFormatter
)


class MemoryType(Enum):
    """Types of memories that can be browsed."""
    PERSONAL_EXPERIENCE = "personal_experience"
    POLITICAL_EVENT = "political_event"
    DECISION_OUTCOME = "decision_outcome"
    RELATIONSHIP_MEMORY = "relationship_memory"
    CULTURAL_KNOWLEDGE = "cultural_knowledge"
    STRATEGIC_INSIGHT = "strategic_insight"
    CRISIS_RESPONSE = "crisis_response"
    DIPLOMATIC_ENCOUNTER = "diplomatic_encounter"


class MemoryImportance(Enum):
    """Importance levels for memory entries."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MemoryEmotion(Enum):
    """Emotional associations with memories."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CONFLICTED = "conflicted"
    INTENSE = "intense"


@dataclass
class MemoryEntry:
    """Represents a single memory entry."""
    memory_id: str
    advisor_id: str
    title: str
    content: str
    memory_type: MemoryType
    importance: MemoryImportance
    emotional_tone: MemoryEmotion
    timestamp: datetime
    tags: List[str]
    participants: List[str]
    related_memories: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory entry to dictionary."""
        return {
            'memory_id': self.memory_id,
            'advisor_id': self.advisor_id,
            'title': self.title,
            'content': self.content,
            'memory_type': self.memory_type.value,
            'importance': self.importance.value,
            'emotional_tone': self.emotional_tone.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags,
            'participants': self.participants,
            'related_memories': self.related_memories,
            'metadata': self.metadata
        }


@dataclass
class MemorySearchFilter:
    """Filter settings for memory search."""
    advisor_ids: Set[str] = None
    memory_types: Set[MemoryType] = None
    importance_levels: Set[MemoryImportance] = None
    emotional_tones: Set[MemoryEmotion] = None
    tags: Set[str] = None
    participants: Set[str] = None
    date_range: Tuple[datetime, datetime] = None
    search_text: str = ""
    
    def __post_init__(self):
        if self.advisor_ids is None:
            self.advisor_ids = set()
        if self.memory_types is None:
            self.memory_types = set(MemoryType)
        if self.importance_levels is None:
            self.importance_levels = set(MemoryImportance)
        if self.emotional_tones is None:
            self.emotional_tones = set(MemoryEmotion)
        if self.tags is None:
            self.tags = set()
        if self.participants is None:
            self.participants = set()


class MemoryGraph:
    """Represents relationships between memories."""
    
    def __init__(self):
        self.nodes: Dict[str, MemoryEntry] = {}
        self.edges: List[Dict[str, Any]] = []
        self.clusters: Dict[str, List[str]] = {}
    
    def add_memory(self, memory: MemoryEntry):
        """Add a memory to the graph."""
        self.nodes[memory.memory_id] = memory
        
        # Create edges to related memories
        for related_id in memory.related_memories:
            if related_id in self.nodes:
                self.edges.append({
                    'source': memory.memory_id,
                    'target': related_id,
                    'type': 'related',
                    'strength': 0.5
                })
    
    def find_memory_clusters(self) -> Dict[str, List[str]]:
        """Find clusters of related memories."""
        clusters = {}
        visited = set()
        
        def dfs(memory_id: str, cluster_id: str):
            if memory_id in visited:
                return
            
            visited.add(memory_id)
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(memory_id)
            
            # Find connected memories
            for edge in self.edges:
                if edge['source'] == memory_id and edge['target'] not in visited:
                    dfs(edge['target'], cluster_id)
                elif edge['target'] == memory_id and edge['source'] not in visited:
                    dfs(edge['source'], cluster_id)
        
        cluster_counter = 0
        for memory_id in self.nodes:
            if memory_id not in visited:
                dfs(memory_id, f"cluster_{cluster_counter}")
                cluster_counter += 1
        
        self.clusters = clusters
        return clusters
    
    def get_memory_connections(self, memory_id: str) -> List[str]:
        """Get all memories connected to a specific memory."""
        connections = []
        
        for edge in self.edges:
            if edge['source'] == memory_id:
                connections.append(edge['target'])
            elif edge['target'] == memory_id:
                connections.append(edge['source'])
        
        return connections


class MemoryBrowserVisualization(VisualizationComponent):
    """Interactive memory browser visualization component."""
    
    def __init__(self, config: VisualizationConfig):
        super().__init__(config)
        
        # Memory storage
        self.memories: Dict[str, MemoryEntry] = {}
        self.memory_graph = MemoryGraph()
        
        # Search and filtering
        self.search_filter = MemorySearchFilter()
        self.search_results: List[str] = []
        self.selected_memories: Set[str] = set()
        
        # Display configuration
        self.view_mode = config.layout_options.get('view_mode', 'list')  # list, graph, timeline
        self.memories_per_page = config.layout_options.get('page_size', 20)
        self.current_page = 0
        self.sort_by = config.layout_options.get('sort_by', 'timestamp')  # timestamp, importance, relevance
        self.sort_order = config.layout_options.get('sort_order', 'desc')  # asc, desc
        
        # Graph visualization settings
        self.show_clusters = config.layout_options.get('show_clusters', True)
        self.cluster_layout = config.layout_options.get('cluster_layout', 'force_directed')
        self.edge_thickness_by_strength = config.layout_options.get('edge_thickness', True)
        
        # Timeline settings
        self.timeline_grouping = config.layout_options.get('timeline_grouping', 'day')  # hour, day, week
        
        # Content analysis
        self.highlight_keywords = config.layout_options.get('highlight_keywords', True)
        self.extract_entities = config.layout_options.get('extract_entities', True)
    
    async def initialize(self) -> bool:
        """Initialize the memory browser."""
        try:
            self.is_active = True
            return True
        except Exception as e:
            print(f"Failed to initialize memory browser: {e}")
            return False
    
    async def update(self, update: VisualizationUpdate) -> bool:
        """Process an update to the memory browser."""
        try:
            if update.update_type == UpdateType.FULL_REFRESH:
                await self._full_refresh(update.data)
            elif update.update_type == UpdateType.INCREMENTAL_UPDATE:
                await self._incremental_update(update.data)
            elif update.update_type == UpdateType.REAL_TIME_EVENT:
                await self._process_real_time_event(update.data)
            
            self.last_update = update.timestamp
            
            # Refresh search results if needed
            await self._refresh_search_results()
            
            # Notify subscribers
            await self.notify_subscribers({
                'type': 'memory_browser_updated',
                'component_id': self.config.component_id,
                'timestamp': update.timestamp.isoformat(),
                'total_memories': len(self.memories)
            })
            
            return True
            
        except Exception as e:
            print(f"Error updating memory browser: {e}")
            return False
    
    async def _full_refresh(self, data_points: List[DataPoint]):
        """Perform full refresh of memory data."""
        new_memories = {}
        
        for point in data_points:
            if point.data_type == 'advisor_memories':
                formatted_memories = DataFormatter.format_advisor_memories(point.value)
                for memory_data in formatted_memories:
                    memory = self._create_memory_entry(memory_data)
                    new_memories[memory.memory_id] = memory
        
        # Replace all memories
        self.memories = new_memories
        
        # Rebuild memory graph
        self.memory_graph = MemoryGraph()
        for memory in self.memories.values():
            self.memory_graph.add_memory(memory)
        
        # Update clusters
        self.memory_graph.find_memory_clusters()
    
    async def _incremental_update(self, data_points: List[DataPoint]):
        """Process incremental updates to memory data."""
        for point in data_points:
            if point.data_type == 'memory_added':
                await self._add_memory(point.value)
            elif point.data_type == 'memory_updated':
                await self._update_memory(point.value)
            elif point.data_type == 'memory_removed':
                await self._remove_memory(point.value['memory_id'])
            elif point.data_type == 'memory_relationship_added':
                await self._add_memory_relationship(point.value)
    
    async def _process_real_time_event(self, data_points: List[DataPoint]):
        """Process real-time events."""
        for point in data_points:
            if point.data_type == 'new_memory_formed':
                await self._animate_new_memory(point.value)
            elif point.data_type == 'memory_recalled':
                await self._highlight_memory_recall(point.value)
    
    def _create_memory_entry(self, memory_data: Dict[str, Any]) -> MemoryEntry:
        """Create MemoryEntry from data dictionary."""
        timestamp = datetime.fromisoformat(memory_data['timestamp'])
        memory_type = MemoryType(memory_data.get('memory_type', 'personal_experience'))
        importance = MemoryImportance(memory_data.get('importance', 'medium'))
        emotional_tone = MemoryEmotion(memory_data.get('emotional_tone', 'neutral'))
        
        return MemoryEntry(
            memory_id=memory_data['memory_id'],
            advisor_id=memory_data['advisor_id'],
            title=memory_data['title'],
            content=memory_data['content'],
            memory_type=memory_type,
            importance=importance,
            emotional_tone=emotional_tone,
            timestamp=timestamp,
            tags=memory_data.get('tags', []),
            participants=memory_data.get('participants', []),
            related_memories=memory_data.get('related_memories', []),
            metadata=memory_data.get('metadata', {})
        )
    
    async def _add_memory(self, memory_data: Dict[str, Any]):
        """Add new memory to browser."""
        memory = self._create_memory_entry(memory_data)
        self.memories[memory.memory_id] = memory
        self.memory_graph.add_memory(memory)
    
    async def _update_memory(self, memory_data: Dict[str, Any]):
        """Update existing memory."""
        memory_id = memory_data['memory_id']
        
        if memory_id in self.memories:
            # Update memory properties
            memory = self.memories[memory_id]
            
            if 'title' in memory_data:
                memory.title = memory_data['title']
            if 'content' in memory_data:
                memory.content = memory_data['content']
            if 'tags' in memory_data:
                memory.tags = memory_data['tags']
            if 'importance' in memory_data:
                memory.importance = MemoryImportance(memory_data['importance'])
            if 'related_memories' in memory_data:
                memory.related_memories = memory_data['related_memories']
            if 'metadata' in memory_data:
                memory.metadata.update(memory_data['metadata'])
            
            # Update graph
            self.memory_graph.add_memory(memory)
    
    async def _remove_memory(self, memory_id: str):
        """Remove memory from browser."""
        if memory_id in self.memories:
            del self.memories[memory_id]
            
            # Remove from graph
            if memory_id in self.memory_graph.nodes:
                del self.memory_graph.nodes[memory_id]
                
                # Remove related edges
                self.memory_graph.edges = [
                    edge for edge in self.memory_graph.edges
                    if edge['source'] != memory_id and edge['target'] != memory_id
                ]
            
            # Remove from selection
            self.selected_memories.discard(memory_id)
    
    async def _add_memory_relationship(self, relationship_data: Dict[str, Any]):
        """Add relationship between memories."""
        source_id = relationship_data['source_memory_id']
        target_id = relationship_data['target_memory_id']
        relationship_type = relationship_data.get('relationship_type', 'related')
        strength = relationship_data.get('strength', 0.5)
        
        # Add edge to graph
        self.memory_graph.edges.append({
            'source': source_id,
            'target': target_id,
            'type': relationship_type,
            'strength': strength
        })
        
        # Update related memories lists
        if source_id in self.memories and target_id not in self.memories[source_id].related_memories:
            self.memories[source_id].related_memories.append(target_id)
        if target_id in self.memories and source_id not in self.memories[target_id].related_memories:
            self.memories[target_id].related_memories.append(source_id)
    
    async def _animate_new_memory(self, memory_data: Dict[str, Any]):
        """Animate the formation of a new memory."""
        await self.notify_subscribers({
            'type': 'memory_animation',
            'animation': 'formation',
            'memory_id': memory_data['memory_id'],
            'advisor_id': memory_data['advisor_id'],
            'duration': 1500
        })
    
    async def _highlight_memory_recall(self, recall_data: Dict[str, Any]):
        """Highlight memory being recalled."""
        await self.notify_subscribers({
            'type': 'memory_highlight',
            'memory_id': recall_data['memory_id'],
            'recall_context': recall_data.get('context', ''),
            'duration': 2000
        })
    
    async def _refresh_search_results(self):
        """Refresh search results based on current filter."""
        self.search_results = self._apply_search_filter()
    
    def _apply_search_filter(self) -> List[str]:
        """Apply current search filter and return matching memory IDs."""
        results = []
        
        for memory_id, memory in self.memories.items():
            # Check advisor filter
            if self.search_filter.advisor_ids and memory.advisor_id not in self.search_filter.advisor_ids:
                continue
            
            # Check memory type filter
            if memory.memory_type not in self.search_filter.memory_types:
                continue
            
            # Check importance filter
            if memory.importance not in self.search_filter.importance_levels:
                continue
            
            # Check emotional tone filter
            if memory.emotional_tone not in self.search_filter.emotional_tones:
                continue
            
            # Check tags filter
            if self.search_filter.tags:
                if not any(tag in memory.tags for tag in self.search_filter.tags):
                    continue
            
            # Check participants filter
            if self.search_filter.participants:
                if not any(participant in memory.participants for participant in self.search_filter.participants):
                    continue
            
            # Check date range filter
            if self.search_filter.date_range:
                start_date, end_date = self.search_filter.date_range
                if not (start_date <= memory.timestamp <= end_date):
                    continue
            
            # Check text search
            if self.search_filter.search_text:
                search_text = self.search_filter.search_text.lower()
                searchable_text = f"{memory.title} {memory.content} {' '.join(memory.tags)}".lower()
                if search_text not in searchable_text:
                    continue
            
            results.append(memory_id)
        
        # Sort results
        results.sort(key=lambda mid: self._get_sort_value(self.memories[mid]), 
                    reverse=(self.sort_order == 'desc'))
        
        return results
    
    def _get_sort_value(self, memory: MemoryEntry) -> Any:
        """Get sort value for a memory based on current sort criteria."""
        if self.sort_by == 'timestamp':
            return memory.timestamp
        elif self.sort_by == 'importance':
            importance_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
            return importance_order.get(memory.importance.value, 0)
        elif self.sort_by == 'relevance':
            # Simple relevance based on search text match quality
            if not self.search_filter.search_text:
                return 0
            
            search_text = self.search_filter.search_text.lower()
            title_matches = search_text in memory.title.lower()
            content_matches = search_text in memory.content.lower()
            tag_matches = any(search_text in tag.lower() for tag in memory.tags)
            
            score = 0
            if title_matches:
                score += 3
            if content_matches:
                score += 2
            if tag_matches:
                score += 1
            
            return score
        
        return memory.timestamp
    
    def _get_paginated_results(self) -> List[str]:
        """Get current page of search results."""
        start_index = self.current_page * self.memories_per_page
        end_index = start_index + self.memories_per_page
        return self.search_results[start_index:end_index]
    
    async def render(self) -> Dict[str, Any]:
        """Render the current memory browser state."""
        if self.view_mode == 'list':
            return await self._render_list_view()
        elif self.view_mode == 'graph':
            return await self._render_graph_view()
        elif self.view_mode == 'timeline':
            return await self._render_timeline_view()
        else:
            return {'error': 'Unknown view mode'}
    
    async def _render_list_view(self) -> Dict[str, Any]:
        """Render list view of memories."""
        paginated_results = self._get_paginated_results()
        
        memories_data = []
        for memory_id in paginated_results:
            memory = self.memories[memory_id]
            memories_data.append({
                'memory': memory.to_dict(),
                'is_selected': memory_id in self.selected_memories,
                'connection_count': len(self.memory_graph.get_memory_connections(memory_id))
            })
        
        return {
            'type': 'memory_list',
            'data': {
                'memories': memories_data,
                'pagination': {
                    'current_page': self.current_page,
                    'total_pages': (len(self.search_results) + self.memories_per_page - 1) // self.memories_per_page,
                    'total_results': len(self.search_results),
                    'page_size': self.memories_per_page
                }
            },
            'config': {
                'sort_by': self.sort_by,
                'sort_order': self.sort_order,
                'highlight_keywords': self.highlight_keywords
            },
            'filter': {
                'advisor_ids': list(self.search_filter.advisor_ids),
                'memory_types': [mt.value for mt in self.search_filter.memory_types],
                'importance_levels': [il.value for il in self.search_filter.importance_levels],
                'emotional_tones': [et.value for et in self.search_filter.emotional_tones],
                'search_text': self.search_filter.search_text
            },
            'metadata': {
                'total_memories': len(self.memories),
                'filtered_memories': len(self.search_results),
                'selected_memories': len(self.selected_memories)
            }
        }
    
    async def _render_graph_view(self) -> Dict[str, Any]:
        """Render graph view of memory relationships."""
        # Get filtered memories for graph
        filtered_memory_ids = set(self.search_results)
        
        # Prepare nodes
        nodes = []
        for memory_id in filtered_memory_ids:
            memory = self.memories[memory_id]
            nodes.append({
                'id': memory_id,
                'title': memory.title,
                'memory_type': memory.memory_type.value,
                'importance': memory.importance.value,
                'emotional_tone': memory.emotional_tone.value,
                'advisor_id': memory.advisor_id,
                'timestamp': memory.timestamp.isoformat(),
                'is_selected': memory_id in self.selected_memories
            })
        
        # Prepare edges (only between filtered memories)
        edges = []
        for edge in self.memory_graph.edges:
            if edge['source'] in filtered_memory_ids and edge['target'] in filtered_memory_ids:
                edges.append(edge)
        
        # Get clusters
        clusters = {}
        if self.show_clusters:
            all_clusters = self.memory_graph.find_memory_clusters()
            for cluster_id, cluster_memory_ids in all_clusters.items():
                filtered_cluster = [mid for mid in cluster_memory_ids if mid in filtered_memory_ids]
                if len(filtered_cluster) > 1:
                    clusters[cluster_id] = filtered_cluster
        
        return {
            'type': 'memory_graph',
            'data': {
                'nodes': nodes,
                'edges': edges,
                'clusters': clusters
            },
            'config': {
                'show_clusters': self.show_clusters,
                'cluster_layout': self.cluster_layout,
                'edge_thickness_by_strength': self.edge_thickness_by_strength
            },
            'metadata': {
                'visible_nodes': len(nodes),
                'visible_edges': len(edges),
                'cluster_count': len(clusters)
            }
        }
    
    async def _render_timeline_view(self) -> Dict[str, Any]:
        """Render timeline view of memories."""
        # Group memories by time period
        grouped_memories = {}
        
        for memory_id in self.search_results:
            memory = self.memories[memory_id]
            
            # Determine time group
            if self.timeline_grouping == 'hour':
                time_group = memory.timestamp.strftime('%Y-%m-%d %H:00')
            elif self.timeline_grouping == 'day':
                time_group = memory.timestamp.strftime('%Y-%m-%d')
            elif self.timeline_grouping == 'week':
                # Get start of week
                week_start = memory.timestamp - timedelta(days=memory.timestamp.weekday())
                time_group = week_start.strftime('%Y-%m-%d (Week)')
            else:
                time_group = memory.timestamp.strftime('%Y-%m-%d')
            
            if time_group not in grouped_memories:
                grouped_memories[time_group] = []
            
            grouped_memories[time_group].append({
                'memory': memory.to_dict(),
                'is_selected': memory_id in self.selected_memories
            })
        
        # Sort groups chronologically
        sorted_groups = sorted(grouped_memories.items())
        
        return {
            'type': 'memory_timeline',
            'data': {
                'timeline_groups': [
                    {
                        'time_period': time_group,
                        'memories': memories,
                        'memory_count': len(memories)
                    }
                    for time_group, memories in sorted_groups
                ]
            },
            'config': {
                'grouping': self.timeline_grouping,
                'highlight_keywords': self.highlight_keywords
            },
            'metadata': {
                'time_periods': len(sorted_groups),
                'total_memories': len(self.search_results)
            }
        }
    
    async def handle_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user interaction with the memory browser."""
        interaction_type = interaction.get('type')
        
        if interaction_type == 'memory_select':
            return await self._handle_memory_select(interaction)
        elif interaction_type == 'search':
            return await self._handle_search(interaction)
        elif interaction_type == 'filter_change':
            return await self._handle_filter_change(interaction)
        elif interaction_type == 'sort_change':
            return await self._handle_sort_change(interaction)
        elif interaction_type == 'view_mode_change':
            return await self._handle_view_mode_change(interaction)
        elif interaction_type == 'page_change':
            return await self._handle_page_change(interaction)
        elif interaction_type == 'memory_details':
            return await self._handle_memory_details(interaction)
        elif interaction_type == 'export_memories':
            return await self._handle_export_memories(interaction)
        
        return {'status': 'unknown_interaction', 'type': interaction_type}
    
    async def _handle_memory_select(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle memory selection."""
        memory_id = interaction.get('memory_id')
        action = interaction.get('action', 'toggle')  # toggle, select, deselect
        
        if memory_id and memory_id in self.memories:
            if action == 'select':
                self.selected_memories.add(memory_id)
            elif action == 'deselect':
                self.selected_memories.discard(memory_id)
            else:  # toggle
                if memory_id in self.selected_memories:
                    self.selected_memories.remove(memory_id)
                else:
                    self.selected_memories.add(memory_id)
            
            return {
                'status': 'success',
                'memory_id': memory_id,
                'selected': memory_id in self.selected_memories,
                'total_selected': len(self.selected_memories)
            }
        
        return {'status': 'error', 'message': 'Memory not found'}
    
    async def _handle_search(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search text update."""
        search_text = interaction.get('search_text', '')
        self.search_filter.search_text = search_text
        
        await self._refresh_search_results()
        self.current_page = 0  # Reset to first page
        
        return {
            'status': 'success',
            'search_text': search_text,
            'results_count': len(self.search_results),
            'requires_refresh': True
        }
    
    async def _handle_filter_change(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle filter changes."""
        filter_updates = interaction.get('filters', {})
        
        if 'advisor_ids' in filter_updates:
            self.search_filter.advisor_ids = set(filter_updates['advisor_ids'])
        
        if 'memory_types' in filter_updates:
            self.search_filter.memory_types = {MemoryType(mt) for mt in filter_updates['memory_types']}
        
        if 'importance_levels' in filter_updates:
            self.search_filter.importance_levels = {MemoryImportance(il) for il in filter_updates['importance_levels']}
        
        if 'emotional_tones' in filter_updates:
            self.search_filter.emotional_tones = {MemoryEmotion(et) for et in filter_updates['emotional_tones']}
        
        if 'date_range' in filter_updates:
            start_date = datetime.fromisoformat(filter_updates['date_range']['start'])
            end_date = datetime.fromisoformat(filter_updates['date_range']['end'])
            self.search_filter.date_range = (start_date, end_date)
        
        await self._refresh_search_results()
        self.current_page = 0  # Reset to first page
        
        return {
            'status': 'success',
            'results_count': len(self.search_results),
            'requires_refresh': True
        }
    
    async def _handle_sort_change(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sort criteria change."""
        if 'sort_by' in interaction:
            self.sort_by = interaction['sort_by']
        
        if 'sort_order' in interaction:
            self.sort_order = interaction['sort_order']
        
        await self._refresh_search_results()
        
        return {
            'status': 'success',
            'sort_by': self.sort_by,
            'sort_order': self.sort_order,
            'requires_refresh': True
        }
    
    async def _handle_view_mode_change(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle view mode change."""
        new_mode = interaction.get('view_mode')
        
        if new_mode in ['list', 'graph', 'timeline']:
            self.view_mode = new_mode
            return {
                'status': 'success',
                'view_mode': new_mode,
                'requires_refresh': True
            }
        
        return {'status': 'error', 'message': 'Invalid view mode'}
    
    async def _handle_page_change(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle page navigation."""
        new_page = interaction.get('page', 0)
        max_page = (len(self.search_results) + self.memories_per_page - 1) // self.memories_per_page - 1
        
        if 0 <= new_page <= max_page:
            self.current_page = new_page
            return {
                'status': 'success',
                'current_page': new_page,
                'requires_refresh': True
            }
        
        return {'status': 'error', 'message': 'Invalid page number'}
    
    async def _handle_memory_details(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request for detailed memory information."""
        memory_id = interaction.get('memory_id')
        
        if memory_id and memory_id in self.memories:
            memory = self.memories[memory_id]
            related_memories = []
            
            # Get related memory details
            for related_id in memory.related_memories:
                if related_id in self.memories:
                    related_memories.append(self.memories[related_id].to_dict())
            
            # Get memory connections from graph
            connections = self.memory_graph.get_memory_connections(memory_id)
            
            return {
                'status': 'success',
                'memory': memory.to_dict(),
                'related_memories': related_memories,
                'connection_count': len(connections),
                'connections': connections
            }
        
        return {'status': 'error', 'message': 'Memory not found'}
    
    async def _handle_export_memories(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle memory export request."""
        export_format = interaction.get('format', 'json')
        memory_ids = interaction.get('memory_ids', list(self.selected_memories))
        
        if not memory_ids:
            memory_ids = self.search_results
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'export_config': {
                'format': export_format,
                'memory_count': len(memory_ids),
                'view_mode': self.view_mode,
                'filters': {
                    'search_text': self.search_filter.search_text,
                    'memory_types': [mt.value for mt in self.search_filter.memory_types],
                    'importance_levels': [il.value for il in self.search_filter.importance_levels]
                }
            },
            'memories': [
                self.memories[memory_id].to_dict()
                for memory_id in memory_ids
                if memory_id in self.memories
            ]
        }
        
        if export_format == 'json':
            return {
                'status': 'success',
                'format': 'json',
                'data': export_data,
                'filename': f'memory_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            }
        
        return {'status': 'error', 'message': 'Unsupported export format'}
