"""
Performance Profiling and Monitoring System

This module provides comprehensive performance monitoring for the game engine bridge,
including turn processing time tracking, memory usage monitoring, and performance
optimization recommendations.
"""

import asyncio
import logging
import psutil
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics


@dataclass
class PerformanceMetric:
    """Individual performance metric measurement."""
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class TurnPerformanceProfile:
    """Performance profile for a single turn."""
    turn_number: int
    start_time: datetime
    end_time: datetime
    total_duration: float  # seconds
    phase_durations: Dict[str, float]  # phase -> seconds
    memory_usage: Dict[str, float]  # metric -> MB
    cpu_usage: float  # percentage
    event_count: int
    message_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        return data


@dataclass
class PerformanceAlert:
    """Performance alert for threshold violations."""
    alert_id: str
    metric_name: str
    threshold_value: float
    actual_value: float
    severity: str  # "warning", "error", "critical"
    timestamp: datetime
    description: str
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class PerformanceProfiler:
    """
    Comprehensive performance monitoring and profiling system for the
    game engine bridge and political simulation components.
    """
    
    def __init__(self,
                 measurement_interval: float = 1.0,
                 history_size: int = 1000,
                 alert_thresholds: Optional[Dict[str, float]] = None):
        """
        Initialize performance profiler.
        
        Args:
            measurement_interval: Seconds between performance measurements
            history_size: Number of measurements to keep in history
            alert_thresholds: Performance thresholds for alerts
        """
        self.measurement_interval = measurement_interval
        self.history_size = history_size
        self.alert_thresholds = alert_thresholds or self._default_thresholds()
        
        # Metric storage
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=history_size))
        self.turn_profiles: List[TurnPerformanceProfile] = []
        self.current_turn_profile: Optional[TurnPerformanceProfile] = None
        
        # Alert system
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.alert_history: List[PerformanceAlert] = []
        self.alert_callbacks: List[Callable] = []
        
        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Performance tracking
        self.operation_timers: Dict[str, datetime] = {}
        self.operation_durations: Dict[str, List[float]] = defaultdict(list)
        
        # System monitoring
        self.process = psutil.Process()
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("Performance Profiler initialized")
    
    def _default_thresholds(self) -> Dict[str, float]:
        """Default performance alert thresholds."""
        return {
            'cpu_usage_percent': 80.0,
            'memory_usage_mb': 512.0,
            'turn_duration_seconds': 10.0,
            'message_latency_ms': 100.0,
            'event_processing_delay_ms': 50.0,
            'state_serialization_time_ms': 1000.0,
            'websocket_connection_count': 100
        }
    
    def start_monitoring(self):
        """Start performance monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()
        
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_active = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Check for threshold violations
                self._check_alert_thresholds()
                
                # Clean up old data
                self._cleanup_old_data()
                
                time.sleep(self.measurement_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(5)  # Brief pause on error
    
    def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            timestamp = datetime.now()
            
            # CPU usage
            cpu_percent = self.process.cpu_percent()
            self._record_metric("cpu_usage_percent", cpu_percent, "percent", timestamp)
            
            # Memory usage
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
            self._record_metric("memory_usage_mb", memory_mb, "MB", timestamp)
            
            # Virtual memory
            vmemory_mb = memory_info.vms / (1024 * 1024)
            self._record_metric("virtual_memory_mb", vmemory_mb, "MB", timestamp)
            
            # Thread count
            thread_count = self.process.num_threads()
            self._record_metric("thread_count", thread_count, "count", timestamp)
            
            # File descriptor count (Unix systems)
            try:
                fd_count = self.process.num_fds()
                self._record_metric("file_descriptor_count", fd_count, "count", timestamp)
            except AttributeError:
                # Windows doesn't have num_fds
                pass
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
    
    def _record_metric(self, name: str, value: float, unit: str, timestamp: datetime, context: Optional[Dict] = None):
        """Record a performance metric."""
        metric = PerformanceMetric(
            metric_name=name,
            value=value,
            unit=unit,
            timestamp=timestamp,
            context=context or {}
        )
        
        self.metrics_history[name].append(metric)
    
    def _check_alert_thresholds(self):
        """Check metrics against alert thresholds."""
        for metric_name, threshold in self.alert_thresholds.items():
            if metric_name in self.metrics_history:
                recent_metrics = list(self.metrics_history[metric_name])
                if recent_metrics:
                    latest_metric = recent_metrics[-1]
                    
                    if latest_metric.value > threshold:
                        self._trigger_alert(metric_name, threshold, latest_metric.value)
                    else:
                        # Clear existing alert if value is now below threshold
                        self._clear_alert(metric_name)
    
    def _trigger_alert(self, metric_name: str, threshold: float, actual_value: float):
        """Trigger performance alert."""
        alert_id = f"alert_{metric_name}_{int(time.time())}"
        
        # Don't create duplicate alerts
        if metric_name in self.active_alerts:
            # Update existing alert
            self.active_alerts[metric_name].actual_value = actual_value
            self.active_alerts[metric_name].timestamp = datetime.now()
            return
        
        # Determine severity
        severity = "warning"
        if actual_value > threshold * 2:
            severity = "critical"
        elif actual_value > threshold * 1.5:
            severity = "error"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metric_name, actual_value, threshold)
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            metric_name=metric_name,
            threshold_value=threshold,
            actual_value=actual_value,
            severity=severity,
            timestamp=datetime.now(),
            description=f"{metric_name} exceeded threshold: {actual_value:.2f} > {threshold:.2f}",
            recommendations=recommendations
        )
        
        self.active_alerts[metric_name] = alert
        self.alert_history.append(alert)
        
        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback error: {e}")
        
        self.logger.warning(f"Performance alert: {alert.description}")
    
    def _clear_alert(self, metric_name: str):
        """Clear active alert for metric."""
        if metric_name in self.active_alerts:
            del self.active_alerts[metric_name]
    
    def _generate_recommendations(self, metric_name: str, actual_value: float, threshold: float) -> List[str]:
        """Generate optimization recommendations for metric."""
        recommendations = []
        
        if metric_name == "cpu_usage_percent":
            recommendations.extend([
                "Consider reducing LLM query frequency",
                "Implement request batching for advisor updates",
                "Use async processing for non-critical operations",
                "Profile and optimize hot code paths"
            ])
        elif metric_name == "memory_usage_mb":
            recommendations.extend([
                "Clear old state history more frequently",
                "Reduce memory cache sizes",
                "Implement memory pooling for large objects",
                "Check for memory leaks in event handlers"
            ])
        elif metric_name == "turn_duration_seconds":
            recommendations.extend([
                "Parallelize independent advisor processing",
                "Cache expensive calculations",
                "Reduce complexity of political simulations",
                "Implement turn time limits"
            ])
        elif metric_name == "message_latency_ms":
            recommendations.extend([
                "Optimize message serialization",
                "Implement message compression",
                "Use connection pooling",
                "Reduce message payload sizes"
            ])
        
        return recommendations
    
    def _cleanup_old_data(self):
        """Clean up old performance data."""
        # Trim turn profiles
        if len(self.turn_profiles) > self.history_size:
            self.turn_profiles = self.turn_profiles[-self.history_size:]
        
        # Trim alert history
        if len(self.alert_history) > self.history_size:
            self.alert_history = self.alert_history[-self.history_size:]
    
    # Turn profiling methods
    def start_turn_profiling(self, turn_number: int):
        """Start profiling a new turn."""
        if self.current_turn_profile:
            self.logger.warning(f"Starting new turn profile while turn {self.current_turn_profile.turn_number} is active")
        
        self.current_turn_profile = TurnPerformanceProfile(
            turn_number=turn_number,
            start_time=datetime.now(),
            end_time=datetime.now(),  # Will be updated
            total_duration=0.0,
            phase_durations={},
            memory_usage={},
            cpu_usage=0.0,
            event_count=0,
            message_count=0
        )
        
        self.logger.debug(f"Started profiling turn {turn_number}")
    
    def end_turn_profiling(self):
        """End current turn profiling."""
        if not self.current_turn_profile:
            self.logger.warning("No active turn profile to end")
            return
        
        end_time = datetime.now()
        self.current_turn_profile.end_time = end_time
        self.current_turn_profile.total_duration = (
            end_time - self.current_turn_profile.start_time
        ).total_seconds()
        
        # Record final metrics
        self.current_turn_profile.memory_usage = self._get_current_memory_usage()
        self.current_turn_profile.cpu_usage = self.process.cpu_percent()
        
        # Add to history
        self.turn_profiles.append(self.current_turn_profile)
        
        # Check turn duration threshold
        if self.current_turn_profile.total_duration > self.alert_thresholds.get('turn_duration_seconds', 10.0):
            self._record_metric(
                "turn_duration_seconds",
                self.current_turn_profile.total_duration,
                "seconds",
                end_time,
                {"turn_number": self.current_turn_profile.turn_number}
            )
        
        self.logger.debug(f"Ended profiling turn {self.current_turn_profile.turn_number}, "
                         f"duration: {self.current_turn_profile.total_duration:.2f}s")
        
        self.current_turn_profile = None
    
    def record_phase_duration(self, phase_name: str, duration: float):
        """Record duration for a turn phase."""
        if self.current_turn_profile:
            self.current_turn_profile.phase_durations[phase_name] = duration
    
    def increment_event_count(self, count: int = 1):
        """Increment event count for current turn."""
        if self.current_turn_profile:
            self.current_turn_profile.event_count += count
    
    def increment_message_count(self, count: int = 1):
        """Increment message count for current turn."""
        if self.current_turn_profile:
            self.current_turn_profile.message_count += count
    
    # Operation timing methods
    def start_operation_timer(self, operation_name: str):
        """Start timing an operation."""
        self.operation_timers[operation_name] = datetime.now()
    
    def end_operation_timer(self, operation_name: str) -> Optional[float]:
        """End timing an operation and return duration."""
        if operation_name in self.operation_timers:
            start_time = self.operation_timers[operation_name]
            duration = (datetime.now() - start_time).total_seconds()
            
            self.operation_durations[operation_name].append(duration)
            
            # Keep only recent measurements
            if len(self.operation_durations[operation_name]) > 100:
                self.operation_durations[operation_name] = self.operation_durations[operation_name][-100:]
            
            del self.operation_timers[operation_name]
            return duration
        
        return None
    
    def get_operation_stats(self, operation_name: str) -> Dict[str, float]:
        """Get statistics for an operation."""
        if operation_name not in self.operation_durations or not self.operation_durations[operation_name]:
            return {}
        
        durations = self.operation_durations[operation_name]
        return {
            'count': len(durations),
            'min': min(durations),
            'max': max(durations),
            'mean': statistics.mean(durations),
            'median': statistics.median(durations),
            'std_dev': statistics.stdev(durations) if len(durations) > 1 else 0.0
        }
    
    # Analysis and reporting methods
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        summary = {
            'monitoring_active': self.monitoring_active,
            'measurement_interval': self.measurement_interval,
            'active_alerts': len(self.active_alerts),
            'total_alerts': len(self.alert_history),
            'turn_profiles': len(self.turn_profiles),
            'metrics_collected': sum(len(history) for history in self.metrics_history.values())
        }
        
        # Recent performance statistics
        if self.metrics_history:
            recent_window = datetime.now() - timedelta(minutes=5)
            
            for metric_name, history in self.metrics_history.items():
                recent_values = [
                    m.value for m in history 
                    if m.timestamp >= recent_window
                ]
                
                if recent_values:
                    summary[f'recent_{metric_name}'] = {
                        'current': recent_values[-1],
                        'min': min(recent_values),
                        'max': max(recent_values),
                        'mean': statistics.mean(recent_values)
                    }
        
        return summary
    
    def get_turn_performance_analysis(self) -> Dict[str, Any]:
        """Analyze turn performance trends."""
        if not self.turn_profiles:
            return {}
        
        recent_turns = self.turn_profiles[-20:]  # Last 20 turns
        
        durations = [t.total_duration for t in recent_turns]
        event_counts = [t.event_count for t in recent_turns]
        message_counts = [t.message_count for t in recent_turns]
        
        analysis = {
            'turn_count': len(recent_turns),
            'duration_stats': {
                'min': min(durations),
                'max': max(durations),
                'mean': statistics.mean(durations),
                'median': statistics.median(durations)
            },
            'event_stats': {
                'min': min(event_counts),
                'max': max(event_counts),
                'mean': statistics.mean(event_counts)
            },
            'message_stats': {
                'min': min(message_counts),
                'max': max(message_counts),
                'mean': statistics.mean(message_counts)
            }
        }
        
        # Trend analysis
        if len(durations) >= 2:
            # Simple linear trend
            recent_half = durations[len(durations)//2:]
            earlier_half = durations[:len(durations)//2]
            
            if statistics.mean(recent_half) > statistics.mean(earlier_half) * 1.1:
                analysis['trend'] = 'degrading'
            elif statistics.mean(recent_half) < statistics.mean(earlier_half) * 0.9:
                analysis['trend'] = 'improving'
            else:
                analysis['trend'] = 'stable'
        
        return analysis
    
    def _get_current_memory_usage(self) -> Dict[str, float]:
        """Get current detailed memory usage."""
        try:
            memory_info = self.process.memory_info()
            return {
                'rss_mb': memory_info.rss / (1024 * 1024),
                'vms_mb': memory_info.vms / (1024 * 1024)
            }
        except Exception as e:
            self.logger.error(f"Failed to get memory usage: {e}")
            return {}
    
    # Configuration and callbacks
    def set_alert_threshold(self, metric_name: str, threshold: float):
        """Set alert threshold for a metric."""
        self.alert_thresholds[metric_name] = threshold
        self.logger.info(f"Set alert threshold for {metric_name}: {threshold}")
    
    def register_alert_callback(self, callback: Callable):
        """Register callback for performance alerts."""
        self.alert_callbacks.append(callback)
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active performance alerts."""
        return [alert.to_dict() for alert in self.active_alerts.values()]
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent performance alerts."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            alert.to_dict() for alert in self.alert_history
            if alert.timestamp >= cutoff
        ]
