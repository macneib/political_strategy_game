"""
Advisor Relationship Network Visualization

This module implements interactive network graph visualization for displaying
advisor relationships, influence networks, and political faction dynamics.
"""

import asyncio
import math
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json

from .base import (
    VisualizationComponent, VisualizationConfig, VisualizationUpdate,
    DataPoint, UpdateType, DataFormatter
)


class NetworkLayout:
    """Network layout algorithms for advisor relationship visualization."""
    
    @staticmethod
    def force_directed_layout(nodes: List[Dict], links: List[Dict], 
                            width: int = 800, height: int = 600,
                            iterations: int = 100) -> Dict[str, Dict[str, float]]:
        """
        Calculate force-directed layout positions for network nodes.
        
        Args:
            nodes: List of node data dictionaries
            links: List of link/edge data dictionaries
            width: Canvas width for positioning
            height: Canvas height for positioning
            iterations: Number of simulation iterations
            
        Returns:
            Dictionary mapping node IDs to {x, y} positions
        """
        positions = {}
        velocities = {}
        
        # Initialize random positions
        for node in nodes:
            node_id = node['id']
            positions[node_id] = {
                'x': width * 0.5 + (0.5 - hash(node_id) % 100 / 100.0) * 100,
                'y': height * 0.5 + (0.5 - hash(node_id) % 79 / 79.0) * 100
            }
            velocities[node_id] = {'x': 0, 'y': 0}
        
        # Force simulation parameters
        repulsion_strength = 1000
        attraction_strength = 0.1
        damping = 0.9
        min_distance = 30
        
        for iteration in range(iterations):
            forces = {node_id: {'x': 0, 'y': 0} for node_id in positions}
            
            # Calculate repulsion forces between all nodes
            for i, node1 in enumerate(nodes):
                for j, node2 in enumerate(nodes):
                    if i != j:
                        id1, id2 = node1['id'], node2['id']
                        pos1, pos2 = positions[id1], positions[id2]
                        
                        dx = pos1['x'] - pos2['x']
                        dy = pos1['y'] - pos2['y']
                        distance = max(math.sqrt(dx*dx + dy*dy), min_distance)
                        
                        force = repulsion_strength / (distance * distance)
                        forces[id1]['x'] += force * dx / distance
                        forces[id1]['y'] += force * dy / distance
            
            # Calculate attraction forces for connected nodes
            for link in links:
                source_id = link['source']
                target_id = link['target']
                
                if source_id in positions and target_id in positions:
                    pos1, pos2 = positions[source_id], positions[target_id]
                    
                    dx = pos2['x'] - pos1['x']
                    dy = pos2['y'] - pos1['y']
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    # Attraction force proportional to relationship strength
                    strength = link.get('strength', 0.5)
                    force = attraction_strength * strength * distance
                    
                    forces[source_id]['x'] += force * dx / distance
                    forces[source_id]['y'] += force * dy / distance
                    forces[target_id]['x'] -= force * dx / distance
                    forces[target_id]['y'] -= force * dy / distance
            
            # Update positions based on forces
            for node_id in positions:
                velocities[node_id]['x'] = (velocities[node_id]['x'] + forces[node_id]['x']) * damping
                velocities[node_id]['y'] = (velocities[node_id]['y'] + forces[node_id]['y']) * damping
                
                positions[node_id]['x'] += velocities[node_id]['x']
                positions[node_id]['y'] += velocities[node_id]['y']
                
                # Keep nodes within bounds
                positions[node_id]['x'] = max(50, min(width - 50, positions[node_id]['x']))
                positions[node_id]['y'] = max(50, min(height - 50, positions[node_id]['y']))
        
        return positions
    
    @staticmethod
    def hierarchical_layout(nodes: List[Dict], links: List[Dict],
                          width: int = 800, height: int = 600) -> Dict[str, Dict[str, float]]:
        """
        Calculate hierarchical layout based on advisor roles and influence.
        
        Args:
            nodes: List of node data dictionaries
            links: List of link/edge data dictionaries
            width: Canvas width for positioning
            height: Canvas height for positioning
            
        Returns:
            Dictionary mapping node IDs to {x, y} positions
        """
        positions = {}
        
        # Group nodes by role
        role_groups = {}
        for node in nodes:
            role = node.get('role', 'unknown')
            if role not in role_groups:
                role_groups[role] = []
            role_groups[role].append(node)
        
        # Define role hierarchy (influence on positioning)
        role_hierarchy = {
            'leader': 0,
            'military': 1,
            'economic': 1,
            'diplomatic': 1,
            'intelligence': 2,
            'cultural': 2,
            'advisor': 3,
            'unknown': 4
        }
        
        # Calculate positions
        y_levels = len(set(role_hierarchy.values()))
        level_height = height / (y_levels + 1)
        
        for role, group_nodes in role_groups.items():
            level = role_hierarchy.get(role, 4)
            y_position = level_height * (level + 1)
            
            # Arrange nodes in this level horizontally
            group_width = width / (len(group_nodes) + 1)
            
            for i, node in enumerate(group_nodes):
                x_position = group_width * (i + 1)
                
                # Add some influence-based adjustment
                influence = node.get('influence', 0.5)
                x_adjustment = (influence - 0.5) * 100  # Spread high influence nodes
                
                positions[node['id']] = {
                    'x': max(50, min(width - 50, x_position + x_adjustment)),
                    'y': y_position
                }
        
        return positions
    
    @staticmethod
    def circular_layout(nodes: List[Dict], width: int = 800, height: int = 600) -> Dict[str, Dict[str, float]]:
        """
        Calculate circular layout with advisor groupings.
        
        Args:
            nodes: List of node data dictionaries
            width: Canvas width for positioning
            height: Canvas height for positioning
            
        Returns:
            Dictionary mapping node IDs to {x, y} positions
        """
        positions = {}
        center_x, center_y = width / 2, height / 2
        radius = min(width, height) * 0.3
        
        # Sort nodes by influence for better positioning
        sorted_nodes = sorted(nodes, key=lambda n: n.get('influence', 0), reverse=True)
        
        angle_step = 2 * math.pi / len(sorted_nodes)
        
        for i, node in enumerate(sorted_nodes):
            angle = i * angle_step
            
            # Vary radius based on influence
            influence = node.get('influence', 0.5)
            node_radius = radius * (0.7 + 0.3 * influence)
            
            x = center_x + node_radius * math.cos(angle)
            y = center_y + node_radius * math.sin(angle)
            
            positions[node['id']] = {'x': x, 'y': y}
        
        return positions


class AdvisorNetworkVisualization(VisualizationComponent):
    """Interactive advisor relationship network visualization component."""
    
    def __init__(self, config: VisualizationConfig):
        super().__init__(config)
        self.network_data = {'nodes': [], 'links': []}
        self.node_positions = {}
        self.layout_algorithm = config.layout_options.get('algorithm', 'force_directed')
        self.show_labels = config.layout_options.get('show_labels', True)
        self.highlight_factions = config.layout_options.get('highlight_factions', True)
        self.animation_enabled = config.layout_options.get('animation', True)
        
        # Interaction state
        self.selected_nodes = set()
        self.hovered_node = None
        self.filter_settings = {
            'min_influence': 0.0,
            'min_relationship_strength': 0.0,
            'roles': set(),
            'loyalty_range': (0.0, 1.0)
        }
    
    async def initialize(self) -> bool:
        """Initialize the network visualization."""
        try:
            self.is_active = True
            return True
        except Exception as e:
            print(f"Failed to initialize network visualization: {e}")
            return False
    
    async def update(self, update: VisualizationUpdate) -> bool:
        """Process an update to the network visualization."""
        try:
            if update.update_type == UpdateType.FULL_REFRESH:
                await self._full_refresh(update.data)
            elif update.update_type == UpdateType.INCREMENTAL_UPDATE:
                await self._incremental_update(update.data)
            elif update.update_type == UpdateType.REAL_TIME_EVENT:
                await self._process_real_time_event(update.data)
            
            self.last_update = update.timestamp
            
            # Notify subscribers of the update
            await self.notify_subscribers({
                'type': 'network_updated',
                'component_id': self.config.component_id,
                'timestamp': update.timestamp.isoformat(),
                'node_count': len(self.network_data['nodes']),
                'link_count': len(self.network_data['links'])
            })
            
            return True
            
        except Exception as e:
            print(f"Error updating network visualization: {e}")
            return False
    
    async def _full_refresh(self, data_points: List[DataPoint]):
        """Perform full refresh of network data."""
        for point in data_points:
            if point.data_type == 'advisor_relationships':
                formatted_data = DataFormatter.format_advisor_relationships(point.value)
                self.network_data = formatted_data
                
                # Recalculate layout
                await self._calculate_layout()
                break
    
    async def _incremental_update(self, data_points: List[DataPoint]):
        """Process incremental updates to network data."""
        layout_changed = False
        
        for point in data_points:
            if point.data_type == 'advisor_update':
                self._update_advisor_node(point.value)
            elif point.data_type == 'relationship_update':
                self._update_relationship_link(point.value)
                layout_changed = True
            elif point.data_type == 'advisor_added':
                self._add_advisor_node(point.value)
                layout_changed = True
            elif point.data_type == 'advisor_removed':
                self._remove_advisor_node(point.value['advisor_id'])
                layout_changed = True
        
        # Recalculate layout if structure changed
        if layout_changed:
            await self._calculate_layout()
    
    async def _process_real_time_event(self, data_points: List[DataPoint]):
        """Process real-time events affecting the network."""
        for point in data_points:
            if point.data_type == 'relationship_change':
                await self._animate_relationship_change(point.value)
            elif point.data_type == 'loyalty_change':
                await self._animate_loyalty_change(point.value)
            elif point.data_type == 'political_event':
                await self._highlight_event_participants(point.value)
    
    def _update_advisor_node(self, advisor_data: Dict[str, Any]):
        """Update existing advisor node data."""
        advisor_id = advisor_data['advisor_id']
        
        for node in self.network_data['nodes']:
            if node['id'] == advisor_id:
                node.update({
                    'loyalty': advisor_data.get('loyalty', node['loyalty']),
                    'influence': advisor_data.get('influence', node['influence']),
                    'stress_level': advisor_data.get('stress_level', node['stress_level']),
                    'mood': advisor_data.get('current_mood', node['mood'])
                })
                break
    
    def _update_relationship_link(self, relationship_data: Dict[str, Any]):
        """Update relationship link strength."""
        source_id = relationship_data['source_id']
        target_id = relationship_data['target_id']
        new_strength = relationship_data['strength']
        
        for link in self.network_data['links']:
            if (link['source'] == source_id and link['target'] == target_id) or \
               (link['source'] == target_id and link['target'] == source_id):
                link['strength'] = new_strength
                break
        else:
            # Add new relationship link
            self.network_data['links'].append({
                'source': source_id,
                'target': target_id,
                'strength': new_strength,
                'type': 'relationship'
            })
    
    def _add_advisor_node(self, advisor_data: Dict[str, Any]):
        """Add new advisor node to the network."""
        new_node = {
            'id': advisor_data['advisor_id'],
            'name': advisor_data['name'],
            'role': advisor_data['role'],
            'loyalty': advisor_data['loyalty'],
            'influence': advisor_data['influence'],
            'stress_level': advisor_data.get('stress_level', 0.5),
            'mood': advisor_data.get('current_mood', 'neutral'),
            'group': advisor_data['role']
        }
        
        self.network_data['nodes'].append(new_node)
    
    def _remove_advisor_node(self, advisor_id: str):
        """Remove advisor node and related links."""
        # Remove node
        self.network_data['nodes'] = [
            node for node in self.network_data['nodes'] 
            if node['id'] != advisor_id
        ]
        
        # Remove related links
        self.network_data['links'] = [
            link for link in self.network_data['links']
            if link['source'] != advisor_id and link['target'] != advisor_id
        ]
    
    async def _calculate_layout(self):
        """Calculate node positions based on selected layout algorithm."""
        if not self.network_data['nodes']:
            return
        
        width = self.config.layout_options.get('width', 800)
        height = self.config.layout_options.get('height', 600)
        
        if self.layout_algorithm == 'force_directed':
            self.node_positions = NetworkLayout.force_directed_layout(
                self.network_data['nodes'], self.network_data['links'], width, height
            )
        elif self.layout_algorithm == 'hierarchical':
            self.node_positions = NetworkLayout.hierarchical_layout(
                self.network_data['nodes'], self.network_data['links'], width, height
            )
        elif self.layout_algorithm == 'circular':
            self.node_positions = NetworkLayout.circular_layout(
                self.network_data['nodes'], width, height
            )
    
    async def _animate_relationship_change(self, change_data: Dict[str, Any]):
        """Animate relationship strength changes."""
        if self.animation_enabled:
            # This would trigger visual animation in the frontend
            await self.notify_subscribers({
                'type': 'relationship_animation',
                'source': change_data['source_id'],
                'target': change_data['target_id'],
                'old_strength': change_data['old_strength'],
                'new_strength': change_data['new_strength'],
                'duration': 1000  # milliseconds
            })
    
    async def _animate_loyalty_change(self, change_data: Dict[str, Any]):
        """Animate loyalty changes."""
        if self.animation_enabled:
            await self.notify_subscribers({
                'type': 'loyalty_animation',
                'advisor_id': change_data['advisor_id'],
                'old_loyalty': change_data['old_loyalty'],
                'new_loyalty': change_data['new_loyalty'],
                'duration': 800
            })
    
    async def _highlight_event_participants(self, event_data: Dict[str, Any]):
        """Highlight advisors involved in political events."""
        await self.notify_subscribers({
            'type': 'event_highlight',
            'participants': event_data['participants'],
            'event_type': event_data['event_type'],
            'severity': event_data['severity'],
            'duration': 3000  # milliseconds
        })
    
    async def render(self) -> Dict[str, Any]:
        """Render the current network visualization state."""
        # Apply filters
        filtered_nodes = self._apply_node_filters(self.network_data['nodes'])
        filtered_links = self._apply_link_filters(self.network_data['links'], filtered_nodes)
        
        return {
            'type': 'network_graph',
            'data': {
                'nodes': filtered_nodes,
                'links': filtered_links,
                'positions': self.node_positions
            },
            'config': {
                'layout_algorithm': self.layout_algorithm,
                'show_labels': self.show_labels,
                'highlight_factions': self.highlight_factions,
                'animation_enabled': self.animation_enabled
            },
            'interaction_state': {
                'selected_nodes': list(self.selected_nodes),
                'hovered_node': self.hovered_node
            },
            'metadata': {
                'total_nodes': len(self.network_data['nodes']),
                'visible_nodes': len(filtered_nodes),
                'total_links': len(self.network_data['links']),
                'visible_links': len(filtered_links),
                'last_update': self.last_update.isoformat()
            }
        }
    
    async def handle_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user interaction with the network visualization."""
        interaction_type = interaction.get('type')
        
        if interaction_type == 'node_click':
            return await self._handle_node_click(interaction)
        elif interaction_type == 'node_hover':
            return await self._handle_node_hover(interaction)
        elif interaction_type == 'filter_change':
            return await self._handle_filter_change(interaction)
        elif interaction_type == 'layout_change':
            return await self._handle_layout_change(interaction)
        elif interaction_type == 'export_request':
            return await self._handle_export_request(interaction)
        
        return {'status': 'unknown_interaction', 'type': interaction_type}
    
    async def _handle_node_click(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle node click interaction."""
        node_id = interaction.get('node_id')
        
        if node_id:
            if node_id in self.selected_nodes:
                self.selected_nodes.remove(node_id)
                action = 'deselected'
            else:
                self.selected_nodes.add(node_id)
                action = 'selected'
            
            # Get detailed node information
            node_data = next((node for node in self.network_data['nodes'] if node['id'] == node_id), None)
            
            return {
                'status': 'success',
                'action': action,
                'node_id': node_id,
                'node_data': node_data,
                'selected_count': len(self.selected_nodes)
            }
        
        return {'status': 'error', 'message': 'No node_id provided'}
    
    async def _handle_node_hover(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle node hover interaction."""
        node_id = interaction.get('node_id')
        self.hovered_node = node_id
        
        if node_id:
            # Get node details and connected relationships
            node_data = next((node for node in self.network_data['nodes'] if node['id'] == node_id), None)
            connected_links = [
                link for link in self.network_data['links'] 
                if link['source'] == node_id or link['target'] == node_id
            ]
            
            return {
                'status': 'success',
                'node_data': node_data,
                'connected_relationships': len(connected_links),
                'relationships': connected_links
            }
        
        return {'status': 'cleared'}
    
    async def _handle_filter_change(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle filter setting changes."""
        filter_updates = interaction.get('filters', {})
        self.filter_settings.update(filter_updates)
        
        return {
            'status': 'success',
            'active_filters': self.filter_settings,
            'requires_refresh': True
        }
    
    async def _handle_layout_change(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle layout algorithm change."""
        new_algorithm = interaction.get('algorithm')
        
        if new_algorithm in ['force_directed', 'hierarchical', 'circular']:
            self.layout_algorithm = new_algorithm
            await self._calculate_layout()
            
            return {
                'status': 'success',
                'new_algorithm': new_algorithm,
                'positions': self.node_positions
            }
        
        return {'status': 'error', 'message': 'Invalid layout algorithm'}
    
    async def _handle_export_request(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data export request."""
        export_format = interaction.get('format', 'json')
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'network_data': self.network_data,
            'positions': self.node_positions,
            'filter_settings': self.filter_settings,
            'metadata': {
                'component_id': self.config.component_id,
                'layout_algorithm': self.layout_algorithm
            }
        }
        
        if export_format == 'json':
            return {
                'status': 'success',
                'format': 'json',
                'data': export_data,
                'filename': f'advisor_network_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            }
        
        return {'status': 'error', 'message': 'Unsupported export format'}
    
    def _apply_node_filters(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply current filter settings to nodes."""
        filtered_nodes = []
        
        for node in nodes:
            # Apply influence filter
            if node.get('influence', 0) < self.filter_settings['min_influence']:
                continue
            
            # Apply loyalty range filter
            loyalty = node.get('loyalty', 0.5)
            if not (self.filter_settings['loyalty_range'][0] <= loyalty <= self.filter_settings['loyalty_range'][1]):
                continue
            
            # Apply role filter
            if self.filter_settings['roles'] and node.get('role') not in self.filter_settings['roles']:
                continue
            
            filtered_nodes.append(node)
        
        return filtered_nodes
    
    def _apply_link_filters(self, links: List[Dict[str, Any]], filtered_nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply current filter settings to links."""
        node_ids = {node['id'] for node in filtered_nodes}
        filtered_links = []
        
        for link in links:
            # Only include links between visible nodes
            if link['source'] not in node_ids or link['target'] not in node_ids:
                continue
            
            # Apply relationship strength filter
            if link.get('strength', 0) < self.filter_settings['min_relationship_strength']:
                continue
            
            filtered_links.append(link)
        
        return filtered_links
