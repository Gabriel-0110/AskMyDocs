"""
Performance monitoring utilities for the RAG system.
Provides tools for tracking timing, memory usage, and system metrics.
"""

import time
import logging
import asyncio
import psutil
from typing import Dict, Any, Optional, List, Callable
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from collections import defaultdict
import threading
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Individual performance metric."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimingResult:
    """Result from timing operations."""
    operation: str
    duration_ms: float
    start_time: datetime
    end_time: datetime
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """Comprehensive performance monitoring for the RAG system."""
    
    def __init__(self, max_metrics: int = 10000):
        """Initialize the performance monitor."""
        self.max_metrics = max_metrics
        self.metrics: List[PerformanceMetric] = []
        self.timing_results: List[TimingResult] = []
        self.operation_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'errors': 0,
            'success_rate': 1.0
        })
        self._lock = threading.Lock()
        
        # System monitoring
        self.process = psutil.Process()
        self.start_memory = self.get_memory_usage()
        self.start_time = datetime.now()
    
    def add_metric(self, name: str, value: float, unit: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a performance metric."""
        with self._lock:
            metric = PerformanceMetric(
                name=name,
                value=value,
                unit=unit,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
            
            self.metrics.append(metric)
            
            # Trim old metrics if needed
            if len(self.metrics) > self.max_metrics:
                self.metrics = self.metrics[-self.max_metrics:]
    
    def record_timing(self, operation: str, duration_ms: float, success: bool = True, 
                     error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Record timing result for an operation."""
        with self._lock:
            now = datetime.now()
            start_time = now - timedelta(milliseconds=duration_ms)
            
            result = TimingResult(
                operation=operation,
                duration_ms=duration_ms,
                start_time=start_time,
                end_time=now,
                success=success,
                error=error,
                metadata=metadata or {}
            )
            
            self.timing_results.append(result)
            
            # Update operation statistics
            stats = self.operation_stats[operation]
            stats['count'] += 1
            stats['total_time'] += duration_ms
            stats['min_time'] = min(stats['min_time'], duration_ms)
            stats['max_time'] = max(stats['max_time'], duration_ms)
            
            if not success:
                stats['errors'] += 1
            
            stats['success_rate'] = (stats['count'] - stats['errors']) / stats['count']
            
            # Trim old results if needed
            if len(self.timing_results) > self.max_metrics:
                self.timing_results = self.timing_results[-self.max_metrics:]
    
    @contextmanager
    def time_operation(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        """Context manager for timing operations."""
        start_time = time.time()
        error = None
        success = True
        
        try:
            yield
        except Exception as e:
            error = str(e)
            success = False
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self.record_timing(operation, duration_ms, success, error, metadata)
    
    @asynccontextmanager
    async def async_time_operation(self, operation: str, metadata: Optional[Dict[str, Any]] = None):
        """Async context manager for timing operations."""
        start_time = time.time()
        error = None
        success = True
        
        try:
            yield
        except Exception as e:
            error = str(e)
            success = False
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self.record_timing(operation, duration_ms, success, error, metadata)
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage."""
        try:
            memory_info = self.process.memory_info()
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
                'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
                'percent': self.process.memory_percent(),
                'available_mb': psutil.virtual_memory().available / 1024 / 1024
            }
        except Exception as e:
            logger.warning(f"Error getting memory usage: {str(e)}")
            return {}
    
    def get_cpu_usage(self) -> Dict[str, float]:
        """Get current CPU usage."""
        try:
            return {
                'process_percent': self.process.cpu_percent(),
                'system_percent': psutil.cpu_percent(interval=0.1),
                'cpu_count': psutil.cpu_count()
            }
        except Exception as e:
            logger.warning(f"Error getting CPU usage: {str(e)}")
            return {}
    
    def get_operation_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for operations."""
        with self._lock:
            if operation:
                stats = self.operation_stats.get(operation, {})
                if stats.get('count', 0) > 0:
                    stats['avg_time'] = stats['total_time'] / stats['count']
                return stats
            else:
                result = {}
                for op, stats in self.operation_stats.items():
                    if stats['count'] > 0:
                        stats_copy = stats.copy()
                        stats_copy['avg_time'] = stats['total_time'] / stats['count']
                        result[op] = stats_copy
                return result
    
    def get_recent_metrics(self, minutes: int = 5) -> List[PerformanceMetric]:
        """Get metrics from the last N minutes."""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [m for m in self.metrics if m.timestamp >= cutoff]
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        current_memory = self.get_memory_usage()
        cpu_usage = self.get_cpu_usage()
        uptime = datetime.now() - self.start_time
        
        with self._lock:
            total_operations = sum(stats['count'] for stats in self.operation_stats.values())
            total_errors = sum(stats['errors'] for stats in self.operation_stats.values())
            overall_success_rate = (total_operations - total_errors) / max(1, total_operations)
        
        return {
            'uptime_seconds': uptime.total_seconds(),
            'memory': current_memory,
            'memory_growth_mb': current_memory.get('rss_mb', 0) - self.start_memory.get('rss_mb', 0),
            'cpu': cpu_usage,
            'operations': {
                'total': total_operations,
                'errors': total_errors,
                'success_rate': overall_success_rate
            },
            'metrics_count': len(self.metrics),
            'timing_results_count': len(self.timing_results)
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        system_stats = self.get_system_stats()
        operation_stats = self.get_operation_stats()
        recent_metrics = self.get_recent_metrics(5)
        
        # Analyze performance trends
        trends = self._analyze_trends()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system': system_stats,
            'operations': operation_stats,
            'recent_metrics_count': len(recent_metrics),
            'trends': trends,
            'recommendations': self._generate_recommendations(system_stats, operation_stats)
        }
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze performance trends."""
        trends = {}
        
        # Analyze timing trends for each operation
        for operation, stats in self.operation_stats.items():
            if stats['count'] < 2:
                continue
            
            # Get recent timings for this operation
            recent_timings = [
                r.duration_ms for r in self.timing_results[-100:]  # Last 100 results
                if r.operation == operation
            ]
            
            if len(recent_timings) >= 2:
                # Simple trend analysis
                mid_point = len(recent_timings) // 2
                first_half_avg = sum(recent_timings[:mid_point]) / mid_point
                second_half_avg = sum(recent_timings[mid_point:]) / (len(recent_timings) - mid_point)
                
                trend_direction = 'improving' if second_half_avg < first_half_avg else 'degrading'
                trend_magnitude = abs(second_half_avg - first_half_avg) / first_half_avg if first_half_avg > 0 else 0
                
                trends[operation] = {
                    'direction': trend_direction,
                    'magnitude_percent': round(trend_magnitude * 100, 2),
                    'recent_avg_ms': round(second_half_avg, 2)
                }
        
        return trends
    
    def _generate_recommendations(self, system_stats: Dict[str, Any], 
                                operation_stats: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        # Memory recommendations
        memory_growth = system_stats.get('memory_growth_mb', 0)
        if memory_growth > 500:  # More than 500MB growth
            recommendations.append("Consider investigating memory growth - potential memory leak")
        
        current_memory = system_stats.get('memory', {}).get('rss_mb', 0)
        if current_memory > 2000:  # More than 2GB
            recommendations.append("High memory usage detected - consider optimizing data structures")
        
        # CPU recommendations
        cpu_percent = system_stats.get('cpu', {}).get('process_percent', 0)
        if cpu_percent > 80:
            recommendations.append("High CPU usage - consider optimizing algorithms or scaling")
        
        # Operation performance recommendations
        for operation, stats in operation_stats.items():
            if stats.get('success_rate', 1.0) < 0.9:
                recommendations.append(f"Low success rate for {operation}: {stats['success_rate']:.1%}")
            
            avg_time = stats.get('avg_time', 0)
            if 'search' in operation.lower() and avg_time > 2000:  # 2 seconds
                recommendations.append(f"Slow search performance in {operation}: {avg_time:.0f}ms average")
            elif 'embedding' in operation.lower() and avg_time > 5000:  # 5 seconds
                recommendations.append(f"Slow embedding generation in {operation}: {avg_time:.0f}ms average")
        
        return recommendations
    
    def export_metrics(self, format: str = 'json') -> str:
        """Export metrics in specified format."""
        if format.lower() == 'json':
            return json.dumps(self.get_performance_report(), indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def clear_metrics(self):
        """Clear all stored metrics and reset counters."""
        with self._lock:
            self.metrics.clear()
            self.timing_results.clear()
            self.operation_stats.clear()
            logger.info("Performance metrics cleared")


# Context manager for easy timing
@contextmanager
def TimingContext(operation: str, monitor: Optional[PerformanceMonitor] = None):
    """Simple context manager for timing operations."""
    if monitor is None:
        # Create a temporary monitor if none provided
        monitor = PerformanceMonitor()
    
    with monitor.time_operation(operation):
        yield


# Global performance monitor instance
performance_monitor = PerformanceMonitor()