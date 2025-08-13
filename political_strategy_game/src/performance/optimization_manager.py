#!/usr/bin/env python3
"""
Performance Optimization Manager for Political Strategy Game

This module implements comprehensive performance optimizations for Task 7.1,
including memory management, LLM caching, database optimization, and concurrent processing.
"""

import asyncio
import gc
import logging
import threading
import time
import json
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable, Tuple
from pathlib import Path
from collections import defaultdict, deque
import psutil
import weakref
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

from src.core.civilization import Civilization
from src.llm.llm_providers import LLMManager, LLMMessage, LLMResponse
from src.llm.advanced_memory import AdvancedMemoryManager, MemoryEntry, ContextPackage
from src.core.memory import MemoryManager
from src.bridge.performance_profiler import PerformanceProfiler


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking."""
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    llm_cache_hit_rate: float = 0.0
    llm_response_time_ms: float = 0.0
    memory_operation_time_ms: float = 0.0
    concurrent_civilizations: int = 0
    active_threads: int = 0
    gc_collections: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationConfig:
    """Configuration for performance optimization."""
    memory_cleanup_interval: int = 300  # seconds
    llm_cache_size: int = 1000
    llm_cache_ttl: int = 3600  # seconds
    max_concurrent_civilizations: int = 4
    memory_operation_timeout: float = 0.1  # seconds
    gc_threshold_mb: float = 500.0
    enable_memory_pooling: bool = True
    enable_llm_batching: bool = True
    enable_concurrent_processing: bool = True
    benchmark_interval: int = 60  # seconds


class MemoryPool:
    """Object pool for frequently created objects."""
    
    def __init__(self, object_type: type, initial_size: int = 10):
        self.object_type = object_type
        self.pool = deque(maxlen=100)  # Prevent unlimited growth
        self.stats = {"created": 0, "reused": 0, "returned": 0}
        
        # Pre-populate pool
        for _ in range(initial_size):
            self.pool.append(object_type())
            self.stats["created"] += 1
    
    def get(self) -> Any:
        """Get object from pool or create new one."""
        if self.pool:
            obj = self.pool.popleft()
            self.stats["reused"] += 1
            return obj
        else:
            obj = self.object_type()
            self.stats["created"] += 1
            return obj
    
    def return_object(self, obj: Any) -> None:
        """Return object to pool."""
        if hasattr(obj, 'reset'):
            obj.reset()
        elif hasattr(obj, 'clear'):
            obj.clear()
        
        self.pool.append(obj)
        self.stats["returned"] += 1


class LLMQueryCache:
    """Intelligent LLM query caching system."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl = timedelta(seconds=ttl_seconds)
        self.cache: Dict[str, Tuple[LLMResponse, datetime]] = {}
        self.access_times: Dict[str, datetime] = {}
        self.hit_count = 0
        self.miss_count = 0
        self.lock = threading.RLock()
    
    def _generate_cache_key(self, messages: List[LLMMessage], **kwargs) -> str:
        """Generate cache key for LLM query."""
        message_content = "".join([f"{msg.role}:{msg.content}" for msg in messages])
        kwargs_str = json.dumps(sorted(kwargs.items()), default=str)
        cache_input = f"{message_content}:{kwargs_str}"
        return hashlib.sha256(cache_input.encode()).hexdigest()[:16]
    
    def get(self, messages: List[LLMMessage], **kwargs) -> Optional[LLMResponse]:
        """Get cached response if available and valid."""
        cache_key = self._generate_cache_key(messages, **kwargs)
        
        with self.lock:
            if cache_key in self.cache:
                response, timestamp = self.cache[cache_key]
                
                # Check if still valid
                if datetime.now() - timestamp < self.ttl:
                    self.access_times[cache_key] = datetime.now()
                    self.hit_count += 1
                    return response
                else:
                    # Expired - remove from cache
                    del self.cache[cache_key]
                    if cache_key in self.access_times:
                        del self.access_times[cache_key]
            
            self.miss_count += 1
            return None
    
    def put(self, messages: List[LLMMessage], response: LLMResponse, **kwargs) -> None:
        """Cache LLM response."""
        cache_key = self._generate_cache_key(messages, **kwargs)
        
        with self.lock:
            # Remove old entries if cache is full
            if len(self.cache) >= self.max_size:
                self._evict_oldest()
            
            self.cache[cache_key] = (response, datetime.now())
            self.access_times[cache_key] = datetime.now()
    
    def _evict_oldest(self) -> None:
        """Evict least recently used entries."""
        if not self.access_times:
            return
        
        # Remove 20% of entries (oldest)
        sorted_keys = sorted(self.access_times.items(), key=lambda x: x[1])
        num_to_remove = max(1, len(sorted_keys) // 5)
        
        for cache_key, _ in sorted_keys[:num_to_remove]:
            if cache_key in self.cache:
                del self.cache[cache_key]
            if cache_key in self.access_times:
                del self.access_times[cache_key]
    
    def get_hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0
    
    def clear(self) -> None:
        """Clear the cache."""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.hit_count = 0
            self.miss_count = 0


class LLMBatchProcessor:
    """Batch processing for LLM queries."""
    
    def __init__(self, llm_manager: LLMManager, batch_size: int = 5, batch_timeout: float = 0.5):
        self.llm_manager = llm_manager
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.pending_queries: List[Tuple[List[LLMMessage], dict, asyncio.Future]] = []
        self.lock = asyncio.Lock()
        self.processing = False
        
    async def submit_query(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Submit query for batch processing."""
        future = asyncio.Future()
        
        async with self.lock:
            self.pending_queries.append((messages, kwargs, future))
            
            # Start batch processing if not already running
            if not self.processing:
                self.processing = True
                asyncio.create_task(self._process_batch())
        
        return await future
    
    async def _process_batch(self) -> None:
        """Process batch of queries."""
        try:
            # Wait for batch to fill or timeout
            start_time = asyncio.get_event_loop().time()
            
            while (len(self.pending_queries) < self.batch_size and 
                   asyncio.get_event_loop().time() - start_time < self.batch_timeout):
                await asyncio.sleep(0.01)
            
            async with self.lock:
                if not self.pending_queries:
                    return
                
                batch = self.pending_queries.copy()
                self.pending_queries.clear()
                
            # Process queries concurrently
            tasks = []
            for messages, kwargs, future in batch:
                task = asyncio.create_task(self._execute_query(messages, kwargs, future))
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
        finally:
            self.processing = False
    
    async def _execute_query(self, messages: List[LLMMessage], kwargs: dict, future: asyncio.Future) -> None:
        """Execute individual query."""
        try:
            response = await self.llm_manager.generate(messages, **kwargs)
            future.set_result(response)
        except Exception as e:
            future.set_exception(e)


class ConcurrentCivilizationProcessor:
    """Concurrent processing for multiple civilizations."""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks: Set[asyncio.Task] = set()
        
    async def process_civilizations_concurrent(self, civilizations: List[Civilization]) -> List[Dict[str, Any]]:
        """Process multiple civilizations concurrently."""
        # Group civilizations into batches
        batches = [civilizations[i:i + self.max_workers] 
                  for i in range(0, len(civilizations), self.max_workers)]
        
        all_results = []
        
        for batch in batches:
            # Process batch concurrently
            tasks = []
            for civ in batch:
                task = asyncio.create_task(self._process_civilization_async(civ))
                self.active_tasks.add(task)
                tasks.append(task)
            
            # Wait for batch to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Clean up completed tasks
            for task in tasks:
                self.active_tasks.discard(task)
            
            # Process results
            for result in batch_results:
                if isinstance(result, Exception):
                    # Log error but continue processing
                    logging.error(f"Civilization processing error: {result}")
                    all_results.append({"error": str(result)})
                else:
                    all_results.append(result)
        
        return all_results
    
    async def _process_civilization_async(self, civilization: Civilization) -> Dict[str, Any]:
        """Process single civilization asynchronously."""
        loop = asyncio.get_event_loop()
        
        # Run civilization processing in thread pool
        result = await loop.run_in_executor(
            self.executor,
            self._process_civilization_sync,
            civilization
        )
        
        return result
    
    def _process_civilization_sync(self, civilization: Civilization) -> Dict[str, Any]:
        """Process civilization synchronously (for thread pool)."""
        try:
            start_time = time.time()
            
            # Process civilization turn
            result = civilization.process_turn()
            
            # Add performance metrics
            result["processing_time"] = time.time() - start_time
            result["civilization_id"] = civilization.id
            
            return result
            
        except Exception as e:
            logging.error(f"Error processing civilization {civilization.id}: {e}")
            return {"error": str(e), "civilization_id": getattr(civilization, 'id', 'unknown')}
    
    def shutdown(self) -> None:
        """Shutdown the processor."""
        self.executor.shutdown(wait=True)


class PerformanceOptimizationManager:
    """Main performance optimization manager for Task 7.1."""
    
    def __init__(self, config: OptimizationConfig = None):
        self.config = config or OptimizationConfig()
        self.logger = logging.getLogger("performance_optimizer")
        
        # Performance monitoring
        self.profiler = PerformanceProfiler()
        self.metrics_history: List[PerformanceMetrics] = []
        self.baseline_metrics: Optional[PerformanceMetrics] = None
        
        # Optimization components
        self.memory_pools: Dict[str, MemoryPool] = {}
        self.llm_cache = LLMQueryCache(
            max_size=self.config.llm_cache_size,
            ttl_seconds=self.config.llm_cache_ttl
        )
        self.llm_batch_processor: Optional[LLMBatchProcessor] = None
        self.civilization_processor = ConcurrentCivilizationProcessor(
            max_workers=self.config.max_concurrent_civilizations
        )
        
        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()
        self.running = False
        
        # Weak references to managed objects
        self.managed_llm_managers: weakref.WeakSet = weakref.WeakSet()
        self.managed_memory_managers: weakref.WeakSet = weakref.WeakSet()
        
        self.logger.info("Performance Optimization Manager initialized")
    
    def register_llm_manager(self, llm_manager: LLMManager) -> None:
        """Register LLM manager for optimization."""
        self.managed_llm_managers.add(llm_manager)
        
        # Create batch processor if enabled
        if self.config.enable_llm_batching and not self.llm_batch_processor:
            self.llm_batch_processor = LLMBatchProcessor(llm_manager)
        
        # Wrap generate method for caching
        original_generate = llm_manager.generate
        
        async def cached_generate(messages: List[LLMMessage], **kwargs) -> LLMResponse:
            # Try cache first
            cached_response = self.llm_cache.get(messages, **kwargs)
            if cached_response:
                return cached_response
            
            # Use batch processor if enabled
            if self.config.enable_llm_batching and self.llm_batch_processor:
                response = await self.llm_batch_processor.submit_query(messages, **kwargs)
            else:
                response = await original_generate(messages, **kwargs)
            
            # Cache the response
            if not response.error:
                self.llm_cache.put(messages, response, **kwargs)
            
            return response
        
        llm_manager.generate = cached_generate
        self.logger.info("LLM manager registered for optimization")
    
    def register_memory_manager(self, memory_manager: MemoryManager) -> None:
        """Register memory manager for optimization."""
        self.managed_memory_managers.add(memory_manager)
        
        # Create object pools if enabled
        if self.config.enable_memory_pooling:
            self.memory_pools["memory_entries"] = MemoryPool(dict, initial_size=20)
        
        self.logger.info("Memory manager registered for optimization")
    
    async def start(self) -> None:
        """Start performance optimization services."""
        if self.running:
            return
        
        self.running = True
        self.profiler.start_monitoring()  # Start profiler monitoring
        
        # Start background tasks
        memory_cleanup_task = asyncio.create_task(self._memory_cleanup_loop())
        metrics_collection_task = asyncio.create_task(self._metrics_collection_loop())
        benchmark_task = asyncio.create_task(self._benchmark_loop())
        
        self.background_tasks.update([memory_cleanup_task, metrics_collection_task, benchmark_task])
        
        # Collect baseline metrics
        self.baseline_metrics = await self._collect_current_metrics()
        
        self.logger.info("Performance optimization started")
    
    async def stop(self) -> None:
        """Stop performance optimization services."""
        self.running = False
        
        # Stop profiler monitoring
        self.profiler.stop_monitoring()
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        self.background_tasks.clear()
        
        # Shutdown components
        self.civilization_processor.shutdown()
        
        self.logger.info("Performance optimization stopped")
    
    async def process_civilizations_optimized(self, civilizations: List[Civilization]) -> List[Dict[str, Any]]:
        """Process civilizations with performance optimization."""
        if not self.config.enable_concurrent_processing or len(civilizations) == 1:
            # Process sequentially
            results = []
            for civ in civilizations:
                result = civ.process_turn()
                results.append(result)
            return results
        
        # Process concurrently
        return await self.civilization_processor.process_civilizations_concurrent(civilizations)
    
    async def _memory_cleanup_loop(self) -> None:
        """Background memory cleanup loop."""
        while self.running:
            try:
                await asyncio.sleep(self.config.memory_cleanup_interval)
                
                # Get current memory usage
                process = psutil.Process()
                memory_mb = process.memory_info().rss / (1024 * 1024)
                
                if memory_mb > self.config.gc_threshold_mb:
                    self.logger.info(f"Memory usage {memory_mb:.1f}MB exceeds threshold, running cleanup")
                    
                    # Run garbage collection
                    collected = gc.collect()
                    
                    # Clean up caches
                    self._cleanup_caches()
                    
                    # Clean up memory pools
                    self._cleanup_memory_pools()
                    
                    new_memory_mb = process.memory_info().rss / (1024 * 1024)
                    freed_mb = memory_mb - new_memory_mb
                    
                    self.logger.info(f"Memory cleanup completed: freed {freed_mb:.1f}MB, collected {collected} objects")
                
            except Exception as e:
                self.logger.error(f"Memory cleanup error: {e}")
    
    async def _metrics_collection_loop(self) -> None:
        """Background metrics collection loop."""
        while self.running:
            try:
                await asyncio.sleep(10)  # Collect every 10 seconds
                
                metrics = await self._collect_current_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only recent metrics
                if len(self.metrics_history) > 360:  # 1 hour at 10s intervals
                    self.metrics_history = self.metrics_history[-360:]
                
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
    
    async def _benchmark_loop(self) -> None:
        """Background benchmarking loop."""
        while self.running:
            try:
                await asyncio.sleep(self.config.benchmark_interval)
                
                benchmark_results = await self._run_performance_benchmark()
                self._analyze_performance_regression(benchmark_results)
                
            except Exception as e:
                self.logger.error(f"Benchmark error: {e}")
    
    async def _collect_current_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics."""
        process = psutil.Process()
        
        return PerformanceMetrics(
            memory_usage_mb=process.memory_info().rss / (1024 * 1024),
            cpu_usage_percent=process.cpu_percent(),
            llm_cache_hit_rate=self.llm_cache.get_hit_rate(),
            llm_response_time_ms=0.0,  # Would be measured during actual operations
            memory_operation_time_ms=0.0,  # Would be measured during actual operations
            concurrent_civilizations=len(self.civilization_processor.active_tasks),
            active_threads=threading.active_count(),
            gc_collections=len(gc.get_stats()) if hasattr(gc, 'get_stats') else 0
        )
    
    def _cleanup_caches(self) -> None:
        """Clean up various caches."""
        # Clean up LLM cache (remove expired entries)
        with self.llm_cache.lock:
            current_time = datetime.now()
            expired_keys = [
                key for key, (_, timestamp) in self.llm_cache.cache.items()
                if current_time - timestamp > self.llm_cache.ttl
            ]
            
            for key in expired_keys:
                self.llm_cache.cache.pop(key, None)
                self.llm_cache.access_times.pop(key, None)
        
        # Clean up memory manager caches
        for memory_manager in self.managed_memory_managers:
            if hasattr(memory_manager, 'context_cache'):
                # Clean expired context cache entries
                current_time = datetime.now()
                expired_keys = [
                    key for key, context in memory_manager.context_cache.items()
                    if (current_time - context.relevant_memories[0].timestamp if context.relevant_memories 
                        else timedelta(hours=2)) > memory_manager.cache_timeout
                ]
                
                for key in expired_keys:
                    memory_manager.context_cache.pop(key, None)
    
    def _cleanup_memory_pools(self) -> None:
        """Clean up memory pools."""
        for pool_name, pool in self.memory_pools.items():
            # Remove excess objects from pools
            while len(pool.pool) > 10:
                pool.pool.pop()
    
    async def _run_performance_benchmark(self) -> Dict[str, float]:
        """Run performance benchmark."""
        benchmark_results = {}
        
        # Memory operation benchmark
        start_time = time.time()
        for _ in range(100):
            # Simulate memory operations
            test_dict = {"test": "data", "timestamp": datetime.now()}
            json.dumps(test_dict, default=str)
        
        benchmark_results["memory_operations_per_second"] = 100 / (time.time() - start_time)
        
        # LLM cache benchmark
        start_time = time.time()
        test_messages = [LLMMessage(role="user", content=f"Test message {i}") for i in range(10)]
        
        for messages in [test_messages]:
            self.llm_cache.get(messages)
        
        benchmark_results["cache_operations_per_second"] = 10 / (time.time() - start_time)
        
        return benchmark_results
    
    def _analyze_performance_regression(self, current_benchmark: Dict[str, float]) -> None:
        """Analyze performance regression."""
        if not self.baseline_metrics:
            return
        
        # Compare with baseline (implementation would include more sophisticated analysis)
        self.logger.info(f"Performance benchmark: {current_benchmark}")
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report."""
        current_metrics = asyncio.create_task(self._collect_current_metrics()) if self.running else None
        
        report = {
            "optimization_status": "active" if self.running else "inactive",
            "config": {
                "memory_cleanup_interval": self.config.memory_cleanup_interval,
                "llm_cache_size": self.config.llm_cache_size,
                "llm_cache_ttl": self.config.llm_cache_ttl,
                "max_concurrent_civilizations": self.config.max_concurrent_civilizations,
                "enable_memory_pooling": self.config.enable_memory_pooling,
                "enable_llm_batching": self.config.enable_llm_batching,
                "enable_concurrent_processing": self.config.enable_concurrent_processing
            },
            "llm_cache_stats": {
                "size": len(self.llm_cache.cache),
                "hit_rate": self.llm_cache.get_hit_rate(),
                "hit_count": self.llm_cache.hit_count,
                "miss_count": self.llm_cache.miss_count
            },
            "memory_pool_stats": {
                pool_name: {
                    "size": len(pool.pool),
                    "created": pool.stats["created"],
                    "reused": pool.stats["reused"],
                    "returned": pool.stats["returned"]
                }
                for pool_name, pool in self.memory_pools.items()
            },
            "metrics_history_size": len(self.metrics_history),
            "active_background_tasks": len(self.background_tasks),
            "managed_llm_managers": len(self.managed_llm_managers),
            "managed_memory_managers": len(self.managed_memory_managers)
        }
        
        if self.baseline_metrics:
            report["baseline_metrics"] = {
                "memory_usage_mb": self.baseline_metrics.memory_usage_mb,
                "cpu_usage_percent": self.baseline_metrics.cpu_usage_percent,
                "timestamp": self.baseline_metrics.timestamp.isoformat()
            }
        
        if self.metrics_history:
            latest = self.metrics_history[-1]
            report["current_metrics"] = {
                "memory_usage_mb": latest.memory_usage_mb,
                "cpu_usage_percent": latest.cpu_usage_percent,
                "llm_cache_hit_rate": latest.llm_cache_hit_rate,
                "concurrent_civilizations": latest.concurrent_civilizations,
                "active_threads": latest.active_threads,
                "timestamp": latest.timestamp.isoformat()
            }
        
        return report


# Factory function for easy setup
def create_optimization_manager(
    enable_memory_pooling: bool = True,
    enable_llm_caching: bool = True,
    enable_llm_batching: bool = True,
    enable_concurrent_processing: bool = True,
    max_concurrent_civilizations: int = 4,
    llm_cache_size: int = 1000
) -> PerformanceOptimizationManager:
    """Create and configure a performance optimization manager."""
    
    config = OptimizationConfig(
        enable_memory_pooling=enable_memory_pooling,
        enable_llm_batching=enable_llm_batching,
        enable_concurrent_processing=enable_concurrent_processing,
        max_concurrent_civilizations=max_concurrent_civilizations,
        llm_cache_size=llm_cache_size
    )
    
    return PerformanceOptimizationManager(config)


if __name__ == "__main__":
    # Example usage
    async def main():
        manager = create_optimization_manager()
        await manager.start()
        
        # Run for demo
        await asyncio.sleep(5)
        
        report = manager.get_optimization_report()
        print("Optimization Report:")
        print(json.dumps(report, indent=2, default=str))
        
        await manager.stop()
    
    asyncio.run(main())
