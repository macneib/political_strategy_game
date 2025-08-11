"""
Political Strategy Game Visualization Framework

This module provides a comprehensive visualization framework for displaying
political data, advisor relationships, event timelines, and decision outcomes
from the political strategy game.
"""

from enum import Enum

# Import base classes first
from .base import (
    VisualizationComponent, VisualizationConfig, VisualizationUpdate,
    DataPoint, UpdateType, DataFormatter, RealTimeDataProvider, VisualizationManager
)

# Import all components for easy access
from .network_graph import AdvisorNetworkVisualization
from .timeline import EventTimelineVisualization
from .dashboard import PoliticalDashboard
from .memory_browser import MemoryBrowserVisualization
from .integrated_manager import IntegratedVisualizationManager, create_political_visualization_system


class VisualizationType(Enum):
    """Types of political visualizations available."""
    NETWORK_GRAPH = "network_graph"
    TIMELINE = "timeline"
    DASHBOARD = "dashboard"
    DECISION_INTERFACE = "decision_interface"
    MEMORY_BROWSER = "memory_browser"
    ANALYTICS_PANEL = "analytics_panel"


# Export all public classes and functions
__all__ = [
    # Base classes
    'VisualizationComponent', 'VisualizationConfig', 'VisualizationUpdate',
    'DataPoint', 'UpdateType', 'DataFormatter', 'RealTimeDataProvider',
    'VisualizationManager',
    
    # Enums
    'VisualizationType',
    
    # Visualization components
    'AdvisorNetworkVisualization', 'EventTimelineVisualization',
    'PoliticalDashboard', 'MemoryBrowserVisualization',
    
    # Integrated system
    'IntegratedVisualizationManager', 'create_political_visualization_system'
]
