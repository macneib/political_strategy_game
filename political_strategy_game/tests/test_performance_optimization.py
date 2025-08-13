#!/usr/bin/env python3
"""
Comprehensive Tests for Performance Optimization System

Tests for Task 7.1 Performance Optimization including memory management,
LLM caching, concurrent processing, and benchmarking systems.
"""

import asyncio
import pytest
import tempfile
import time
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock

from src.performance.optimization_manager import (
    PerformanceOptimizationManager, OptimizationConfig, MemoryPool, 
    LLMQueryCache, LLMBatchProcessor, ConcurrentCivilizationProcessor
)
from src.performance.benchmark_suite import (
    PerformanceBenchmarkSuite, BenchmarkResult, BenchmarkSuite
)
from src.llm.llm_providers import LLMManager, LLMMessage, LLMResponse, LLMProvider
from src.llm.advanced_memory import AdvancedMemoryManager, MemoryType, MemoryImportance
from src.core.memory import MemoryManager, Memory
from src.core.civilization import Civilization
from src.core.leader import Leader, LeadershipStyle
from src.core.advisor import Advisor, AdvisorRole, PersonalityProfile


class TestMemoryPool:
    """Test memory pool functionality."""
    
    def test_memory_pool_creation(self):
        """Test memory pool creation and initialization."""
        pool = MemoryPool(dict, initial_size=5)
        
        assert len(pool.pool) == 5
        assert pool.stats["created"] == 5
        assert pool.stats["reused"] == 0
        assert pool.stats["returned"] == 0
    
    def test_memory_pool_get_and_return(self):
        """Test getting and returning objects from pool."""
        pool = MemoryPool(dict, initial_size=3)
        
        # Get object from pool
        obj1 = pool.get()
        assert pool.stats["reused"] == 1
        assert len(pool.pool) == 2
        
        # Return object to pool
        pool.return_object(obj1)
        assert pool.stats["returned"] == 1
        assert len(pool.pool) == 3
    
    def test_memory_pool_create_new_when_empty(self):
        """Test creating new objects when pool is empty."""
        pool = MemoryPool(dict, initial_size=1)
        
        # Empty the pool
        obj1 = pool.get()
        assert len(pool.pool) == 0
        
        # Get another object (should create new)
        obj2 = pool.get()
        assert pool.stats["created"] == 2  # 1 initial + 1 new
        assert obj1 is not obj2


class TestLLMQueryCache:
    """Test LLM query caching system."""
    
    def test_cache_creation(self):
        """Test cache creation and configuration."""
        cache = LLMQueryCache(max_size=10, ttl_seconds=60)
        
        assert cache.max_size == 10
        assert cache.ttl.total_seconds() == 60
        assert len(cache.cache) == 0
        assert cache.get_hit_rate() == 0.0
    
    def test_cache_put_and_get(self):
        """Test caching and retrieving responses."""
        cache = LLMQueryCache(max_size=10, ttl_seconds=60)
        
        messages = [LLMMessage(role="user", content="test query")]
        response = LLMResponse(
            content="test response",
            provider=LLMProvider.OPENAI,
            model="test"
        )
        
        # Cache response
        cache.put(messages, response)
        assert len(cache.cache) == 1
        
        # Retrieve cached response
        cached_response = cache.get(messages)
        assert cached_response is not None
        assert cached_response.content == "test response"
        assert cache.get_hit_rate() == 1.0
    
    def test_cache_miss(self):
        """Test cache miss for non-cached queries."""
        cache = LLMQueryCache(max_size=10, ttl_seconds=60)
        
        messages = [LLMMessage(role="user", content="uncached query")]
        cached_response = cache.get(messages)
        
        assert cached_response is None
        assert cache.get_hit_rate() == 0.0
    
    def test_cache_eviction(self):
        """Test cache eviction when max size is reached."""
        cache = LLMQueryCache(max_size=2, ttl_seconds=60)
        
        # Add items to fill cache
        for i in range(3):
            messages = [LLMMessage(role="user", content=f"query {i}")]
            response = LLMResponse(
                content=f"response {i}",
                provider=LLMProvider.OPENAI,
                model="test"
            )
            cache.put(messages, response)
        
        # Cache should not exceed max size
        assert len(cache.cache) <= 2
    
    def test_cache_ttl_expiration(self):
        """Test cache TTL expiration."""
        cache = LLMQueryCache(max_size=10, ttl_seconds=0.1)  # Very short TTL
        
        messages = [LLMMessage(role="user", content="expiring query")]
        response = LLMResponse(
            content="expiring response",
            provider=LLMProvider.OPENAI,
            model="test"
        )
        
        # Cache response
        cache.put(messages, response)
        
        # Should be cached initially
        cached_response = cache.get(messages)
        assert cached_response is not None
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should be expired now
        cached_response = cache.get(messages)
        assert cached_response is None


class TestLLMBatchProcessor:
    """Test LLM batch processing system."""
    
    @pytest.fixture
    def mock_llm_manager(self):
        """Create mock LLM manager."""
        manager = Mock()
        manager.generate = AsyncMock()
        return manager
    
    @pytest.mark.asyncio
    async def test_batch_processor_creation(self, mock_llm_manager):
        """Test batch processor creation."""
        processor = LLMBatchProcessor(mock_llm_manager, batch_size=3, batch_timeout=0.1)
        
        assert processor.llm_manager is mock_llm_manager
        assert processor.batch_size == 3
        assert processor.batch_timeout == 0.1
        assert len(processor.pending_queries) == 0
    
    @pytest.mark.asyncio
    async def test_single_query_processing(self, mock_llm_manager):
        """Test processing single query through batch processor."""
        mock_llm_manager.generate.return_value = LLMResponse(
            content="batch response",
            provider=LLMProvider.OPENAI,
            model="test"
        )
        
        processor = LLMBatchProcessor(mock_llm_manager, batch_size=3, batch_timeout=0.1)
        
        messages = [LLMMessage(role="user", content="batch test")]
        response = await processor.submit_query(messages)
        
        assert response.content == "batch response"
        mock_llm_manager.generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_multiple_query_batching(self, mock_llm_manager):
        """Test batching multiple queries."""
        mock_llm_manager.generate.return_value = LLMResponse(
            content="batch response",
            provider=LLMProvider.OPENAI,
            model="test"
        )
        
        processor = LLMBatchProcessor(mock_llm_manager, batch_size=2, batch_timeout=0.1)
        
        # Submit multiple queries
        tasks = []
        for i in range(2):
            messages = [LLMMessage(role="user", content=f"batch test {i}")]
            task = processor.submit_query(messages)
            tasks.append(task)
        
        # Wait for all to complete
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 2
        assert all(r.content == "batch response" for r in responses)


class TestConcurrentCivilizationProcessor:
    """Test concurrent civilization processing."""
    
    @pytest.fixture
    def mock_civilization(self):
        """Create mock civilization."""
        civ = Mock()
        civ.id = "test_civ"
        civ.process_turn.return_value = {
            "turn": 1,
            "events": [],
            "civilization_id": "test_civ"
        }
        return civ
    
    @pytest.mark.asyncio
    async def test_processor_creation(self):
        """Test processor creation."""
        processor = ConcurrentCivilizationProcessor(max_workers=2)
        
        assert processor.max_workers == 2
        assert len(processor.active_tasks) == 0
        
        processor.shutdown()
    
    @pytest.mark.asyncio
    async def test_single_civilization_processing(self, mock_civilization):
        """Test processing single civilization."""
        processor = ConcurrentCivilizationProcessor(max_workers=2)
        
        results = await processor.process_civilizations_concurrent([mock_civilization])
        
        assert len(results) == 1
        assert results[0]["civilization_id"] == "test_civ"
        assert "processing_time" in results[0]
        
        processor.shutdown()
    
    @pytest.mark.asyncio
    async def test_multiple_civilization_processing(self, mock_civilization):
        """Test processing multiple civilizations concurrently."""
        processor = ConcurrentCivilizationProcessor(max_workers=2)
        
        # Create multiple mock civilizations
        civs = []
        for i in range(3):
            civ = Mock()
            civ.id = f"test_civ_{i}"
            civ.process_turn.return_value = {
                "turn": 1,
                "events": [],
                "civilization_id": f"test_civ_{i}"
            }
            civs.append(civ)
        
        results = await processor.process_civilizations_concurrent(civs)
        
        assert len(results) == 3
        assert all("processing_time" in r for r in results)
        
        processor.shutdown()


class TestPerformanceOptimizationManager:
    """Test performance optimization manager."""
    
    @pytest.fixture
    def optimization_config(self):
        """Create test optimization configuration."""
        return OptimizationConfig(
            memory_cleanup_interval=1,  # Short interval for testing
            llm_cache_size=10,
            llm_cache_ttl=60,
            max_concurrent_civilizations=2,
            enable_memory_pooling=True,
            enable_llm_batching=False,  # Disable batching for testing to avoid hangs
            enable_concurrent_processing=True
        )
    
    @pytest.fixture
    def mock_llm_manager(self):
        """Create mock LLM manager."""
        manager = Mock()
        manager.generate = AsyncMock(return_value=LLMResponse(
            content="test response",
            provider=LLMProvider.OPENAI,
            model="test"
        ))
        return manager
    
    def test_manager_creation(self, optimization_config):
        """Test optimization manager creation."""
        manager = PerformanceOptimizationManager(optimization_config)
        
        assert manager.config == optimization_config
        assert not manager.running
        assert len(manager.memory_pools) == 0
        assert len(manager.managed_llm_managers) == 0
    
    def test_llm_manager_registration(self, optimization_config, mock_llm_manager):
        """Test LLM manager registration."""
        manager = PerformanceOptimizationManager(optimization_config)
        
        manager.register_llm_manager(mock_llm_manager)
        
        assert len(manager.managed_llm_managers) == 1
        # Batch processor is None when batching is disabled
        assert manager.llm_batch_processor is None
    
    def test_memory_manager_registration(self, optimization_config):
        """Test memory manager registration."""
        manager = PerformanceOptimizationManager(optimization_config)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_manager = MemoryManager(Path(temp_dir))
            manager.register_memory_manager(memory_manager)
            
            assert len(manager.managed_memory_managers) == 1
            assert "memory_entries" in manager.memory_pools
    
    @pytest.mark.asyncio
    async def test_optimization_lifecycle(self, optimization_config, mock_llm_manager):
        """Test optimization manager start/stop lifecycle."""
        manager = PerformanceOptimizationManager(optimization_config)
        manager.register_llm_manager(mock_llm_manager)
        
        # Start optimization
        await manager.start()
        assert manager.running
        assert len(manager.background_tasks) > 0
        assert manager.baseline_metrics is not None
        
        # Stop optimization
        await manager.stop()
        assert not manager.running
        assert len(manager.background_tasks) == 0
    
    @pytest.mark.asyncio
    async def test_llm_caching_integration(self, optimization_config, mock_llm_manager):
        """Test LLM caching through optimization manager."""
        manager = PerformanceOptimizationManager(optimization_config)
        manager.register_llm_manager(mock_llm_manager)
        
        await manager.start()
        
        try:
            # First call - should call underlying LLM
            messages = [LLMMessage(role="user", content="cache test")]
            response1 = await mock_llm_manager.generate(messages)
            
            # Second call with same content - should use cache
            response2 = await mock_llm_manager.generate(messages)
            
            assert response1.content == response2.content
            # Check cache hit rate
            cache_stats = manager.get_optimization_report()["llm_cache_stats"]
            assert cache_stats["hit_rate"] > 0
            
        finally:
            await manager.stop()
    
    def test_optimization_report(self, optimization_config):
        """Test optimization report generation."""
        manager = PerformanceOptimizationManager(optimization_config)
        
        report = manager.get_optimization_report()
        
        assert "optimization_status" in report
        assert "config" in report
        assert "llm_cache_stats" in report
        assert "memory_pool_stats" in report


class TestBenchmarkSuite:
    """Test performance benchmark suite."""
    
    @pytest.fixture
    def benchmark_suite(self):
        """Create benchmark suite with temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        return PerformanceBenchmarkSuite(temp_dir)
    
    def test_benchmark_suite_creation(self, benchmark_suite):
        """Test benchmark suite creation."""
        assert benchmark_suite.data_dir.exists()
        assert benchmark_suite.results_db_path.exists()
        assert "memory_operations_count" in benchmark_suite.benchmark_config
    
    @pytest.mark.asyncio
    async def test_memory_operations_benchmark(self, benchmark_suite):
        """Test memory operations benchmark."""
        result = await benchmark_suite._benchmark_memory_operations()
        
        assert result.test_name == "memory_operations"
        assert result.success
        assert result.duration_ms > 0
        assert result.operations_per_second > 0
        assert "operations_count" in result.metadata
    
    @pytest.mark.asyncio
    async def test_llm_query_benchmark(self, benchmark_suite):
        """Test LLM query performance benchmark."""
        result = await benchmark_suite._benchmark_llm_queries()
        
        assert result.test_name == "llm_query_performance"
        assert result.success
        assert result.duration_ms > 0
        assert result.operations_per_second > 0
        assert "query_count" in result.metadata
    
    @pytest.mark.asyncio
    async def test_llm_caching_benchmark(self, benchmark_suite):
        """Test LLM caching efficiency benchmark."""
        result = await benchmark_suite._benchmark_llm_caching()
        
        assert result.test_name == "llm_caching_efficiency"
        assert result.success
        assert result.operations_per_second > 0
        assert "hit_rate" in result.metadata
        assert result.metadata["hit_rate"] > 0.5  # Should have good hit rate
    
    @pytest.mark.asyncio
    async def test_memory_system_benchmark(self, benchmark_suite):
        """Test advanced memory system benchmark."""
        result = await benchmark_suite._benchmark_memory_system()
        
        assert result.test_name == "memory_system_performance"
        assert result.success
        assert result.operations_per_second > 0
        assert "memories_added" in result.metadata
        assert "successful_retrievals" in result.metadata
    
    @pytest.mark.asyncio
    async def test_civilization_processing_benchmark(self, benchmark_suite):
        """Test civilization processing benchmark."""
        result = await benchmark_suite._benchmark_civilization_processing()
        
        assert result.test_name == "civilization_processing"
        assert result.success
        assert result.operations_per_second > 0
        assert "turns_processed" in result.metadata
    
    @pytest.mark.asyncio
    async def test_concurrent_civilization_benchmark(self, benchmark_suite):
        """Test concurrent civilization processing benchmark."""
        result = await benchmark_suite._benchmark_concurrent_civilizations()
        
        assert result.test_name == "concurrent_civilization_processing"
        assert result.success
        assert result.operations_per_second > 0
        assert "civilizations_processed" in result.metadata
        assert "success_rate" in result.metadata
    
    @pytest.mark.asyncio
    async def test_database_operations_benchmark(self, benchmark_suite):
        """Test database operations benchmark."""
        result = await benchmark_suite._benchmark_database_operations()
        
        assert result.test_name == "database_operations"
        assert result.success
        assert result.operations_per_second > 0
        assert "memories_stored" in result.metadata
        assert "memories_retrieved" in result.metadata
    
    @pytest.mark.asyncio
    async def test_memory_management_benchmark(self, benchmark_suite):
        """Test memory management efficiency benchmark."""
        result = await benchmark_suite._benchmark_memory_management()
        
        assert result.test_name == "memory_management_efficiency"
        assert result.success
        assert result.operations_per_second > 0
        assert "memory_growth_mb" in result.metadata
        assert "gc_collected" in result.metadata
    
    @pytest.mark.asyncio
    async def test_optimization_effectiveness_benchmark(self, benchmark_suite):
        """Test optimization effectiveness benchmark."""
        result = await benchmark_suite._benchmark_optimization_effectiveness()
        
        assert result.test_name == "optimization_effectiveness"
        assert result.success
        assert result.operations_per_second > 0
        assert "cache_hit_rate" in result.metadata
        assert "optimization_active" in result.metadata
    
    @pytest.mark.asyncio
    async def test_regression_detection_benchmark(self, benchmark_suite):
        """Test regression detection benchmark."""
        result = await benchmark_suite._benchmark_regression_detection()
        
        assert result.test_name == "regression_detection"
        assert result.success
        assert result.operations_per_second > 0
        assert "regressions" in result.metadata
        assert "significant_regressions" in result.metadata
    
    @pytest.mark.asyncio
    async def test_full_benchmark_suite(self, benchmark_suite):
        """Test running the full benchmark suite."""
        # Reduce test counts for faster execution
        benchmark_suite.benchmark_config.update({
            "memory_operations_count": 100,
            "llm_queries_count": 10,
            "civilization_count": 2,
            "turns_to_simulate": 1
        })
        
        suite_result = await benchmark_suite.run_full_benchmark_suite(version="test")
        
        assert suite_result.suite_name == "performance_optimization"
        assert suite_result.version == "test"
        assert len(suite_result.results) == 10  # All benchmark tests
        assert suite_result.total_duration_ms > 0
        assert suite_result.peak_memory_mb > 0
        
        # Check summary
        summary = suite_result.get_summary()
        assert "total_tests" in summary
        assert "successful_tests" in summary
        assert "success_rate" in summary
        assert summary["total_tests"] == 10
    
    def test_benchmark_storage_and_retrieval(self, benchmark_suite):
        """Test storing and retrieving benchmark results."""
        # Create a test suite
        result = BenchmarkResult(
            test_name="test_benchmark",
            duration_ms=100.0,
            memory_usage_mb=10.0,
            cpu_usage_percent=5.0,
            operations_per_second=1000.0,
            success=True,
            metadata={"test": "data"}
        )
        
        suite = BenchmarkSuite(
            suite_name="test_suite",
            version="1.0",
            results=[result],
            total_duration_ms=100.0,
            peak_memory_mb=20.0,
            average_cpu_percent=5.0,
            overall_success=True
        )
        
        # Store the suite
        benchmark_suite._store_benchmark_suite(suite)
        
        # Retrieve historical results
        historical = benchmark_suite.get_historical_results(limit=1)
        
        assert len(historical) == 1
        assert historical[0].suite_name == "test_suite"
        assert historical[0].version == "1.0"
        assert len(historical[0].results) == 1
        assert historical[0].results[0].test_name == "test_benchmark"
    
    def test_regression_detection(self, benchmark_suite):
        """Test performance regression detection."""
        # Create baseline suite
        baseline_result = BenchmarkResult(
            test_name="performance_test",
            duration_ms=100.0,
            memory_usage_mb=10.0,
            cpu_usage_percent=5.0,
            operations_per_second=1000.0,
            success=True
        )
        
        baseline_suite = BenchmarkSuite(
            suite_name="test_suite",
            version="1.0",
            results=[baseline_result],
            total_duration_ms=100.0,
            peak_memory_mb=20.0,
            average_cpu_percent=5.0,
            overall_success=True
        )
        
        # Create regression suite (slower performance)
        regression_result = BenchmarkResult(
            test_name="performance_test",
            duration_ms=150.0,
            memory_usage_mb=15.0,
            cpu_usage_percent=8.0,
            operations_per_second=800.0,  # 20% slower
            success=True
        )
        
        regression_suite = BenchmarkSuite(
            suite_name="test_suite",
            version="1.1",
            results=[regression_result],
            total_duration_ms=150.0,
            peak_memory_mb=25.0,
            average_cpu_percent=8.0,
            overall_success=True
        )
        
        # Store both suites
        benchmark_suite._store_benchmark_suite(baseline_suite)
        benchmark_suite._store_benchmark_suite(regression_suite)
        
        # Detect regressions
        regression_analysis = benchmark_suite.detect_performance_regressions(tolerance_percent=5.0)
        
        assert regression_analysis["status"] == "complete"
        assert regression_analysis["regression_count"] > 0
        assert "performance_test" in regression_analysis["regressions"]


class TestIntegrationScenarios:
    """Test integration scenarios for performance optimization."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_optimization_scenario(self):
        """Test complete end-to-end optimization scenario."""
        # Create optimization manager with all features enabled (except batching for test stability)
        config = OptimizationConfig(
            memory_cleanup_interval=60,  # Longer interval to avoid background task issues
            llm_cache_size=50,
            llm_cache_ttl=300,
            max_concurrent_civilizations=2,
            enable_memory_pooling=True,
            enable_llm_batching=False,  # Disable to avoid hanging in tests
            enable_concurrent_processing=True
        )
        
        optimizer = PerformanceOptimizationManager(config)
        
        # Create mock LLM manager
        mock_llm = Mock()
        mock_llm.generate = AsyncMock(return_value=LLMResponse(
            content="optimized response",
            provider=LLMProvider.OPENAI,
            model="test"
        ))
        
        # Register components
        optimizer.register_llm_manager(mock_llm)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_manager = MemoryManager(Path(temp_dir))
            optimizer.register_memory_manager(memory_manager)
            
            # Start optimization
            await optimizer.start()
            
            try:
                # Simulate workload
                for i in range(10):
                    messages = [LLMMessage(role="user", content=f"test query {i % 3}")]
                    await mock_llm.generate(messages)
                
                # Get optimization report
                report = optimizer.get_optimization_report()
                
                assert report["optimization_status"] == "active"
                assert report["llm_cache_stats"]["hit_rate"] > 0
                assert len(report["memory_pool_stats"]) > 0
                
            finally:
                await optimizer.stop()
    
    @pytest.mark.asyncio
    async def test_benchmark_with_optimization(self):
        """Test running benchmarks with optimization enabled."""
        # Create optimization manager with batching disabled for test stability
        config = OptimizationConfig(
            enable_memory_pooling=True,
            enable_llm_batching=False,  # Disable to avoid hanging in tests
            enable_concurrent_processing=True
        )
        optimizer = PerformanceOptimizationManager(config)
        
        # Create benchmark suite
        benchmark_suite = PerformanceBenchmarkSuite()
        
        # Reduce test size for faster execution
        benchmark_suite.benchmark_config.update({
            "memory_operations_count": 50,
            "llm_queries_count": 5,
            "civilization_count": 1,
            "turns_to_simulate": 1
        })
        
        # Run benchmarks
        results = await benchmark_suite.run_full_benchmark_suite(version="optimized")
        
        assert results.overall_success
        assert len(results.results) > 0
        
        # Check that optimization-related benchmarks passed
        optimization_tests = [
            r for r in results.results 
            if "optimization" in r.test_name or "caching" in r.test_name
        ]
        
        assert len(optimization_tests) > 0
        assert all(t.success for t in optimization_tests)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
