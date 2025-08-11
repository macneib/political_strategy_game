"""
Political Dashboard Visualization

This module implements a comprehensive political dashboard for displaying
key metrics, trends, and real-time political status information.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import statistics

from .base import (
    VisualizationComponent, VisualizationConfig, VisualizationUpdate,
    DataPoint, UpdateType, DataFormatter
)


class MetricType(Enum):
    """Types of political metrics for dashboard display."""
    LOYALTY_AVERAGE = "loyalty_average"
    INFLUENCE_DISTRIBUTION = "influence_distribution"
    FACTION_STRENGTH = "faction_strength"
    POLITICAL_STABILITY = "political_stability"
    DECISION_SUCCESS_RATE = "decision_success_rate"
    CRISIS_FREQUENCY = "crisis_frequency"
    RESOURCE_LEVELS = "resource_levels"
    DIPLOMATIC_RELATIONS = "diplomatic_relations"
    CULTURAL_COHESION = "cultural_cohesion"
    MILITARY_READINESS = "military_readiness"


class WidgetType(Enum):
    """Types of dashboard widgets."""
    GAUGE = "gauge"
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    HEATMAP = "heatmap"
    TABLE = "table"
    INDICATOR = "indicator"
    PROGRESS_BAR = "progress_bar"


@dataclass
class MetricValue:
    """Represents a metric value with metadata."""
    value: float
    timestamp: datetime
    trend: Optional[float] = None  # Rate of change
    status: str = "normal"  # normal, warning, critical
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DashboardWidget:
    """Represents a dashboard widget configuration."""
    widget_id: str
    title: str
    widget_type: WidgetType
    metric_type: MetricType
    position: Tuple[int, int]  # (row, column)
    size: Tuple[int, int]  # (width, height)
    config: Dict[str, Any]
    data: List[Any] = None
    last_update: Optional[datetime] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = []


class PoliticalDashboard(VisualizationComponent):
    """Comprehensive political dashboard visualization component."""
    
    def __init__(self, config: VisualizationConfig):
        super().__init__(config)
        
        # Dashboard layout
        self.grid_columns = config.layout_options.get('columns', 4)
        self.grid_rows = config.layout_options.get('rows', 6)
        self.widget_padding = config.layout_options.get('padding', 10)
        
        # Metrics storage
        self.metrics: Dict[MetricType, List[MetricValue]] = {}
        self.current_values: Dict[MetricType, MetricValue] = {}
        self.historical_data: Dict[MetricType, List[Tuple[datetime, float]]] = {}
        
        # Widgets
        self.widgets: Dict[str, DashboardWidget] = {}
        self.auto_refresh = config.layout_options.get('auto_refresh', True)
        self.refresh_interval = config.layout_options.get('refresh_interval', 5.0)  # seconds
        
        # Alerting
        self.alert_thresholds: Dict[MetricType, Dict[str, float]] = {}
        self.active_alerts: List[Dict[str, Any]] = []
        
        # Initialize default widgets
        self._initialize_default_widgets()
        self._initialize_alert_thresholds()
    
    def _initialize_default_widgets(self):
        """Initialize default dashboard widgets."""
        default_widgets = [
            # Top row - Key indicators
            DashboardWidget(
                widget_id="loyalty_gauge",
                title="Average Loyalty",
                widget_type=WidgetType.GAUGE,
                metric_type=MetricType.LOYALTY_AVERAGE,
                position=(0, 0),
                size=(1, 1),
                config={
                    "min_value": 0.0,
                    "max_value": 1.0,
                    "warning_threshold": 0.3,
                    "critical_threshold": 0.2,
                    "unit": "%"
                }
            ),
            DashboardWidget(
                widget_id="stability_gauge",
                title="Political Stability",
                widget_type=WidgetType.GAUGE,
                metric_type=MetricType.POLITICAL_STABILITY,
                position=(0, 1),
                size=(1, 1),
                config={
                    "min_value": 0.0,
                    "max_value": 1.0,
                    "warning_threshold": 0.4,
                    "critical_threshold": 0.3,
                    "unit": "%"
                }
            ),
            DashboardWidget(
                widget_id="military_indicator",
                title="Military Readiness",
                widget_type=WidgetType.INDICATOR,
                metric_type=MetricType.MILITARY_READINESS,
                position=(0, 2),
                size=(1, 1),
                config={
                    "thresholds": [
                        {"min": 0.8, "status": "high", "color": "green"},
                        {"min": 0.5, "status": "medium", "color": "yellow"},
                        {"min": 0.0, "status": "low", "color": "red"}
                    ]
                }
            ),
            DashboardWidget(
                widget_id="crisis_frequency",
                title="Crisis Events",
                widget_type=WidgetType.INDICATOR,
                metric_type=MetricType.CRISIS_FREQUENCY,
                position=(0, 3),
                size=(1, 1),
                config={
                    "format": "count",
                    "time_window": "24h"
                }
            ),
            
            # Second row - Trends
            DashboardWidget(
                widget_id="loyalty_trend",
                title="Loyalty Trend (24h)",
                widget_type=WidgetType.LINE_CHART,
                metric_type=MetricType.LOYALTY_AVERAGE,
                position=(1, 0),
                size=(2, 1),
                config={
                    "time_window": "24h",
                    "show_trend_line": True,
                    "y_axis_min": 0.0,
                    "y_axis_max": 1.0
                }
            ),
            DashboardWidget(
                widget_id="stability_trend",
                title="Stability Trend (24h)",
                widget_type=WidgetType.LINE_CHART,
                metric_type=MetricType.POLITICAL_STABILITY,
                position=(1, 2),
                size=(2, 1),
                config={
                    "time_window": "24h",
                    "show_trend_line": True,
                    "y_axis_min": 0.0,
                    "y_axis_max": 1.0
                }
            ),
            
            # Third row - Distributions
            DashboardWidget(
                widget_id="influence_distribution",
                title="Advisor Influence Distribution",
                widget_type=WidgetType.PIE_CHART,
                metric_type=MetricType.INFLUENCE_DISTRIBUTION,
                position=(2, 0),
                size=(2, 1),
                config={
                    "show_percentages": True,
                    "group_small_slices": True,
                    "small_slice_threshold": 0.05
                }
            ),
            DashboardWidget(
                widget_id="faction_strength",
                title="Faction Strength",
                widget_type=WidgetType.BAR_CHART,
                metric_type=MetricType.FACTION_STRENGTH,
                position=(2, 2),
                size=(2, 1),
                config={
                    "orientation": "horizontal",
                    "show_values": True,
                    "sort_by": "value"
                }
            ),
            
            # Fourth row - Resources and diplomacy
            DashboardWidget(
                widget_id="resource_levels",
                title="Resource Levels",
                widget_type=WidgetType.PROGRESS_BAR,
                metric_type=MetricType.RESOURCE_LEVELS,
                position=(3, 0),
                size=(2, 1),
                config={
                    "show_labels": True,
                    "stack_bars": False,
                    "color_coding": True
                }
            ),
            DashboardWidget(
                widget_id="diplomatic_relations",
                title="Diplomatic Relations",
                widget_type=WidgetType.HEATMAP,
                metric_type=MetricType.DIPLOMATIC_RELATIONS,
                position=(3, 2),
                size=(2, 1),
                config={
                    "color_scheme": "diverging",
                    "center_value": 0.5,
                    "show_values": True
                }
            ),
            
            # Fifth row - Decision analysis
            DashboardWidget(
                widget_id="decision_success",
                title="Decision Success Rate",
                widget_type=WidgetType.LINE_CHART,
                metric_type=MetricType.DECISION_SUCCESS_RATE,
                position=(4, 0),
                size=(4, 1),
                config={
                    "time_window": "7d",
                    "aggregation": "daily",
                    "show_moving_average": True,
                    "moving_average_window": 3
                }
            ),
            
            # Bottom row - Cultural metrics
            DashboardWidget(
                widget_id="cultural_cohesion",
                title="Cultural Cohesion",
                widget_type=WidgetType.GAUGE,
                metric_type=MetricType.CULTURAL_COHESION,
                position=(5, 0),
                size=(2, 1),
                config={
                    "min_value": 0.0,
                    "max_value": 1.0,
                    "warning_threshold": 0.4,
                    "critical_threshold": 0.3
                }
            ),
            DashboardWidget(
                widget_id="recent_events",
                title="Recent Political Events",
                widget_type=WidgetType.TABLE,
                metric_type=MetricType.CRISIS_FREQUENCY,
                position=(5, 2),
                size=(2, 1),
                config={
                    "max_rows": 5,
                    "columns": ["Time", "Event", "Severity"],
                    "time_window": "6h"
                }
            )
        ]
        
        for widget in default_widgets:
            self.widgets[widget.widget_id] = widget
    
    def _initialize_alert_thresholds(self):
        """Initialize alert thresholds for metrics."""
        self.alert_thresholds = {
            MetricType.LOYALTY_AVERAGE: {
                "critical": 0.2,
                "warning": 0.3,
                "trend_critical": -0.1  # 10% decrease per hour
            },
            MetricType.POLITICAL_STABILITY: {
                "critical": 0.3,
                "warning": 0.4,
                "trend_critical": -0.15
            },
            MetricType.CRISIS_FREQUENCY: {
                "warning": 3,  # 3 crises per hour
                "critical": 5
            },
            MetricType.MILITARY_READINESS: {
                "critical": 0.3,
                "warning": 0.5
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize the dashboard."""
        try:
            # Initialize metric storage
            for metric_type in MetricType:
                self.metrics[metric_type] = []
                self.historical_data[metric_type] = []
            
            self.is_active = True
            
            # Start auto-refresh if enabled
            if self.auto_refresh:
                asyncio.create_task(self._auto_refresh_loop())
            
            return True
        except Exception as e:
            print(f"Failed to initialize dashboard: {e}")
            return False
    
    async def update(self, update: VisualizationUpdate) -> bool:
        """Process an update to the dashboard."""
        try:
            if update.update_type == UpdateType.FULL_REFRESH:
                await self._full_refresh(update.data)
            elif update.update_type == UpdateType.INCREMENTAL_UPDATE:
                await self._incremental_update(update.data)
            elif update.update_type == UpdateType.REAL_TIME_EVENT:
                await self._process_real_time_event(update.data)
            
            self.last_update = update.timestamp
            
            # Update widgets with new data
            await self._update_widgets()
            
            # Check for alerts
            await self._check_alerts()
            
            # Notify subscribers
            await self.notify_subscribers({
                'type': 'dashboard_updated',
                'component_id': self.config.component_id,
                'timestamp': update.timestamp.isoformat(),
                'widgets_updated': len(self.widgets)
            })
            
            return True
            
        except Exception as e:
            print(f"Error updating dashboard: {e}")
            return False
    
    async def _full_refresh(self, data_points: List[DataPoint]):
        """Perform full refresh of dashboard data."""
        for point in data_points:
            await self._process_data_point(point)
    
    async def _incremental_update(self, data_points: List[DataPoint]):
        """Process incremental updates."""
        for point in data_points:
            await self._process_data_point(point)
    
    async def _process_real_time_event(self, data_points: List[DataPoint]):
        """Process real-time events."""
        for point in data_points:
            await self._process_data_point(point)
    
    async def _process_data_point(self, point: DataPoint):
        """Process a single data point and update relevant metrics."""
        if point.data_type == 'advisor_metrics':
            await self._update_advisor_metrics(point.value)
        elif point.data_type == 'political_stability':
            await self._update_stability_metric(point.value)
        elif point.data_type == 'military_status':
            await self._update_military_metric(point.value)
        elif point.data_type == 'resource_status':
            await self._update_resource_metrics(point.value)
        elif point.data_type == 'diplomatic_status':
            await self._update_diplomatic_metrics(point.value)
        elif point.data_type == 'cultural_metrics':
            await self._update_cultural_metrics(point.value)
        elif point.data_type == 'decision_results':
            await self._update_decision_metrics(point.value)
        elif point.data_type == 'crisis_event':
            await self._update_crisis_metrics(point.value)
    
    async def _update_advisor_metrics(self, data: Dict[str, Any]):
        """Update advisor-related metrics."""
        # Calculate average loyalty
        if 'advisors' in data:
            loyalties = [advisor.get('loyalty', 0.5) for advisor in data['advisors']]
            if loyalties:
                avg_loyalty = statistics.mean(loyalties)
                await self._store_metric(MetricType.LOYALTY_AVERAGE, avg_loyalty)
        
        # Calculate influence distribution
        if 'advisors' in data:
            influences = {}
            for advisor in data['advisors']:
                role = advisor.get('role', 'unknown')
                influence = advisor.get('influence', 0.0)
                influences[role] = influences.get(role, 0.0) + influence
            
            if influences:
                await self._store_metric(MetricType.INFLUENCE_DISTRIBUTION, influences)
    
    async def _update_stability_metric(self, data: Dict[str, Any]):
        """Update political stability metric."""
        stability = data.get('stability_score', 0.5)
        await self._store_metric(MetricType.POLITICAL_STABILITY, stability)
    
    async def _update_military_metric(self, data: Dict[str, Any]):
        """Update military readiness metric."""
        readiness = data.get('readiness_level', 0.5)
        await self._store_metric(MetricType.MILITARY_READINESS, readiness)
    
    async def _update_resource_metrics(self, data: Dict[str, Any]):
        """Update resource level metrics."""
        resources = data.get('resources', {})
        await self._store_metric(MetricType.RESOURCE_LEVELS, resources)
    
    async def _update_diplomatic_metrics(self, data: Dict[str, Any]):
        """Update diplomatic relation metrics."""
        relations = data.get('relations', {})
        await self._store_metric(MetricType.DIPLOMATIC_RELATIONS, relations)
    
    async def _update_cultural_metrics(self, data: Dict[str, Any]):
        """Update cultural cohesion metrics."""
        cohesion = data.get('cultural_cohesion', 0.5)
        await self._store_metric(MetricType.CULTURAL_COHESION, cohesion)
    
    async def _update_decision_metrics(self, data: Dict[str, Any]):
        """Update decision success rate metrics."""
        success_rate = data.get('success_rate', 0.5)
        await self._store_metric(MetricType.DECISION_SUCCESS_RATE, success_rate)
    
    async def _update_crisis_metrics(self, data: Dict[str, Any]):
        """Update crisis frequency metrics."""
        # Count crises in the last hour
        current_time = datetime.now()
        hour_ago = current_time - timedelta(hours=1)
        
        if MetricType.CRISIS_FREQUENCY in self.historical_data:
            recent_crises = [
                count for timestamp, count in self.historical_data[MetricType.CRISIS_FREQUENCY]
                if timestamp >= hour_ago
            ]
            crisis_count = len(recent_crises)
        else:
            crisis_count = 1  # Current crisis
        
        await self._store_metric(MetricType.CRISIS_FREQUENCY, crisis_count)
    
    async def _store_metric(self, metric_type: MetricType, value: Any):
        """Store a metric value with timestamp."""
        timestamp = datetime.now()
        
        # Calculate trend if we have historical data
        trend = None
        if metric_type in self.current_values and isinstance(value, (int, float)):
            previous_value = self.current_values[metric_type].value
            if isinstance(previous_value, (int, float)):
                time_diff = (timestamp - self.current_values[metric_type].timestamp).total_seconds()
                if time_diff > 0:
                    trend = (value - previous_value) / (time_diff / 3600)  # Per hour
        
        # Determine status based on thresholds
        status = "normal"
        if metric_type in self.alert_thresholds and isinstance(value, (int, float)):
            thresholds = self.alert_thresholds[metric_type]
            if value <= thresholds.get("critical", 0):
                status = "critical"
            elif value <= thresholds.get("warning", 0):
                status = "warning"
        
        # Create metric value
        metric_value = MetricValue(
            value=value,
            timestamp=timestamp,
            trend=trend,
            status=status
        )
        
        # Store current value
        self.current_values[metric_type] = metric_value
        
        # Add to historical data
        if metric_type not in self.historical_data:
            self.historical_data[metric_type] = []
        
        if isinstance(value, (int, float)):
            self.historical_data[metric_type].append((timestamp, value))
            
            # Keep only recent data (last 7 days)
            week_ago = timestamp - timedelta(days=7)
            self.historical_data[metric_type] = [
                (ts, val) for ts, val in self.historical_data[metric_type]
                if ts >= week_ago
            ]
    
    async def _update_widgets(self):
        """Update all widgets with current data."""
        for widget in self.widgets.values():
            await self._update_widget(widget)
    
    async def _update_widget(self, widget: DashboardWidget):
        """Update a specific widget with current data."""
        metric_type = widget.metric_type
        
        if metric_type not in self.current_values:
            return
        
        current_value = self.current_values[metric_type]
        
        if widget.widget_type == WidgetType.GAUGE:
            widget.data = {
                'value': current_value.value,
                'status': current_value.status,
                'trend': current_value.trend
            }
        
        elif widget.widget_type == WidgetType.LINE_CHART:
            time_window = widget.config.get('time_window', '24h')
            historical_data = self._get_historical_data(metric_type, time_window)
            widget.data = {
                'series': [{'name': widget.title, 'data': historical_data}],
                'current_value': current_value.value
            }
        
        elif widget.widget_type == WidgetType.PIE_CHART:
            if isinstance(current_value.value, dict):
                widget.data = {
                    'series': [
                        {'name': key, 'value': value}
                        for key, value in current_value.value.items()
                    ]
                }
        
        elif widget.widget_type == WidgetType.BAR_CHART:
            if isinstance(current_value.value, dict):
                widget.data = {
                    'categories': list(current_value.value.keys()),
                    'values': list(current_value.value.values())
                }
        
        elif widget.widget_type == WidgetType.HEATMAP:
            if isinstance(current_value.value, dict):
                widget.data = {'matrix': current_value.value}
        
        elif widget.widget_type == WidgetType.INDICATOR:
            widget.data = {
                'value': current_value.value,
                'status': current_value.status,
                'trend': current_value.trend,
                'formatted_value': self._format_value(current_value.value, widget.config)
            }
        
        elif widget.widget_type == WidgetType.PROGRESS_BAR:
            if isinstance(current_value.value, dict):
                widget.data = {
                    'bars': [
                        {
                            'name': key,
                            'value': value,
                            'max_value': widget.config.get('max_value', 1.0)
                        }
                        for key, value in current_value.value.items()
                    ]
                }
        
        widget.last_update = current_value.timestamp
    
    def _get_historical_data(self, metric_type: MetricType, time_window: str) -> List[Tuple[str, float]]:
        """Get historical data for a specific time window."""
        if metric_type not in self.historical_data:
            return []
        
        # Parse time window
        now = datetime.now()
        if time_window.endswith('h'):
            hours = int(time_window[:-1])
            start_time = now - timedelta(hours=hours)
        elif time_window.endswith('d'):
            days = int(time_window[:-1])
            start_time = now - timedelta(days=days)
        else:
            start_time = now - timedelta(hours=24)  # Default to 24h
        
        # Filter and format data
        filtered_data = [
            (timestamp.isoformat(), value)
            for timestamp, value in self.historical_data[metric_type]
            if timestamp >= start_time
        ]
        
        return filtered_data
    
    def _format_value(self, value: Any, config: Dict[str, Any]) -> str:
        """Format a value for display."""
        if isinstance(value, float):
            if config.get('format') == 'percentage':
                return f"{value * 100:.1f}%"
            elif config.get('format') == 'count':
                return f"{int(value)}"
            else:
                return f"{value:.2f}"
        elif isinstance(value, int):
            return str(value)
        else:
            return str(value)
    
    async def _check_alerts(self):
        """Check for alert conditions and manage active alerts."""
        new_alerts = []
        
        for metric_type, thresholds in self.alert_thresholds.items():
            if metric_type not in self.current_values:
                continue
            
            current_value = self.current_values[metric_type]
            
            # Check value thresholds
            if isinstance(current_value.value, (int, float)):
                if current_value.value <= thresholds.get("critical", 0):
                    new_alerts.append({
                        'type': 'critical',
                        'metric': metric_type.value,
                        'value': current_value.value,
                        'threshold': thresholds["critical"],
                        'message': f"{metric_type.value} is critically low: {current_value.value:.2f}",
                        'timestamp': current_value.timestamp.isoformat()
                    })
                elif current_value.value <= thresholds.get("warning", 0):
                    new_alerts.append({
                        'type': 'warning',
                        'metric': metric_type.value,
                        'value': current_value.value,
                        'threshold': thresholds["warning"],
                        'message': f"{metric_type.value} is low: {current_value.value:.2f}",
                        'timestamp': current_value.timestamp.isoformat()
                    })
            
            # Check trend thresholds
            if current_value.trend and "trend_critical" in thresholds:
                if current_value.trend <= thresholds["trend_critical"]:
                    new_alerts.append({
                        'type': 'trend_critical',
                        'metric': metric_type.value,
                        'trend': current_value.trend,
                        'threshold': thresholds["trend_critical"],
                        'message': f"{metric_type.value} is declining rapidly: {current_value.trend:.2f}/hour",
                        'timestamp': current_value.timestamp.isoformat()
                    })
        
        # Update active alerts
        self.active_alerts = new_alerts
        
        # Notify subscribers of alerts
        if new_alerts:
            await self.notify_subscribers({
                'type': 'alerts_updated',
                'alerts': new_alerts,
                'alert_count': len(new_alerts)
            })
    
    async def _auto_refresh_loop(self):
        """Auto-refresh loop for dashboard updates."""
        while self.is_active and self.auto_refresh:
            try:
                await asyncio.sleep(self.refresh_interval)
                await self._update_widgets()
                
                # Notify subscribers of refresh
                await self.notify_subscribers({
                    'type': 'dashboard_refreshed',
                    'timestamp': datetime.now().isoformat()
                })
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in dashboard auto-refresh: {e}")
    
    async def render(self) -> Dict[str, Any]:
        """Render the current dashboard state."""
        # Prepare widget data
        rendered_widgets = []
        for widget in self.widgets.values():
            rendered_widgets.append({
                'widget_id': widget.widget_id,
                'title': widget.title,
                'type': widget.widget_type.value,
                'position': widget.position,
                'size': widget.size,
                'config': widget.config,
                'data': widget.data,
                'last_update': widget.last_update.isoformat() if widget.last_update else None
            })
        
        return {
            'type': 'political_dashboard',
            'layout': {
                'columns': self.grid_columns,
                'rows': self.grid_rows,
                'padding': self.widget_padding
            },
            'widgets': rendered_widgets,
            'alerts': self.active_alerts,
            'config': {
                'auto_refresh': self.auto_refresh,
                'refresh_interval': self.refresh_interval
            },
            'metadata': {
                'total_widgets': len(self.widgets),
                'active_alerts': len(self.active_alerts),
                'last_update': self.last_update.isoformat() if self.last_update else None
            }
        }
    
    async def handle_interaction(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user interaction with the dashboard."""
        interaction_type = interaction.get('type')
        
        if interaction_type == 'widget_click':
            return await self._handle_widget_click(interaction)
        elif interaction_type == 'refresh_request':
            return await self._handle_refresh_request(interaction)
        elif interaction_type == 'alert_dismiss':
            return await self._handle_alert_dismiss(interaction)
        elif interaction_type == 'widget_configure':
            return await self._handle_widget_configure(interaction)
        elif interaction_type == 'export_data':
            return await self._handle_export_data(interaction)
        
        return {'status': 'unknown_interaction', 'type': interaction_type}
    
    async def _handle_widget_click(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle widget click interaction."""
        widget_id = interaction.get('widget_id')
        
        if widget_id and widget_id in self.widgets:
            widget = self.widgets[widget_id]
            
            return {
                'status': 'success',
                'widget_id': widget_id,
                'widget_data': {
                    'title': widget.title,
                    'type': widget.widget_type.value,
                    'current_data': widget.data,
                    'last_update': widget.last_update.isoformat() if widget.last_update else None
                }
            }
        
        return {'status': 'error', 'message': 'Widget not found'}
    
    async def _handle_refresh_request(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle manual refresh request."""
        widget_id = interaction.get('widget_id')
        
        if widget_id and widget_id in self.widgets:
            await self._update_widget(self.widgets[widget_id])
            return {'status': 'success', 'widget_id': widget_id}
        else:
            await self._update_widgets()
            return {'status': 'success', 'widgets_updated': len(self.widgets)}
    
    async def _handle_alert_dismiss(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle alert dismissal."""
        alert_index = interaction.get('alert_index')
        
        if alert_index is not None and 0 <= alert_index < len(self.active_alerts):
            dismissed_alert = self.active_alerts.pop(alert_index)
            
            return {
                'status': 'success',
                'dismissed_alert': dismissed_alert,
                'remaining_alerts': len(self.active_alerts)
            }
        
        return {'status': 'error', 'message': 'Invalid alert index'}
    
    async def _handle_widget_configure(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle widget configuration changes."""
        widget_id = interaction.get('widget_id')
        new_config = interaction.get('config', {})
        
        if widget_id and widget_id in self.widgets:
            widget = self.widgets[widget_id]
            widget.config.update(new_config)
            
            # Update widget with new configuration
            await self._update_widget(widget)
            
            return {
                'status': 'success',
                'widget_id': widget_id,
                'updated_config': widget.config
            }
        
        return {'status': 'error', 'message': 'Widget not found'}
    
    async def _handle_export_data(self, interaction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data export request."""
        export_format = interaction.get('format', 'json')
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'dashboard_config': {
                'layout': {
                    'columns': self.grid_columns,
                    'rows': self.grid_rows
                },
                'widgets': [
                    {
                        'widget_id': widget.widget_id,
                        'title': widget.title,
                        'type': widget.widget_type.value,
                        'metric_type': widget.metric_type.value,
                        'position': widget.position,
                        'size': widget.size,
                        'config': widget.config
                    }
                    for widget in self.widgets.values()
                ]
            },
            'current_metrics': {
                metric_type.value: {
                    'value': metric_value.value,
                    'timestamp': metric_value.timestamp.isoformat(),
                    'trend': metric_value.trend,
                    'status': metric_value.status
                }
                for metric_type, metric_value in self.current_values.items()
            },
            'historical_data': {
                metric_type.value: [
                    {'timestamp': ts.isoformat(), 'value': val}
                    for ts, val in data
                ]
                for metric_type, data in self.historical_data.items()
            },
            'active_alerts': self.active_alerts
        }
        
        if export_format == 'json':
            return {
                'status': 'success',
                'format': 'json',
                'data': export_data,
                'filename': f'political_dashboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            }
        
        return {'status': 'error', 'message': 'Unsupported export format'}
