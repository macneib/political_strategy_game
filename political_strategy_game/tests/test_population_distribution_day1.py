#!/usr/bin/env python3
"""
Tests for the Population Skill Distribution System - Day 1: Mathematical Distribution Framework.
"""

import pytest
import numpy as np
from typing import Dict, List
from src.core.population_distribution import (
    SkillDistribution, DistributionParams, SkillStatistics, CitizenSummary,
    create_skill_distribution
)
from src.core.technology_tree import TechnologyEra
from src.core.citizen import SkillCategory


class TestDistributionParams:
    """Test distribution parameter validation."""
    
    def test_distribution_params_creation(self):
        """Test creating distribution parameters."""
        params = DistributionParams(
            distribution_type="normal",
            mean=0.5,
            std_dev=0.15,
            min_val=0.0,
            max_val=1.0
        )
        
        assert params.distribution_type == "normal"
        assert params.mean == 0.5
        assert params.std_dev == 0.15
        assert params.min_val == 0.0
        assert params.max_val == 1.0
    
    def test_pareto_params(self):
        """Test Pareto distribution parameters."""
        params = DistributionParams(
            distribution_type="pareto",
            shape=1.16,
            scale=0.1,
            min_val=0.0,
            max_val=1.0
        )
        
        assert params.distribution_type == "pareto"
        assert params.shape == 1.16
        assert params.scale == 0.1


class TestSkillStatistics:
    """Test skill statistics calculation."""
    
    def test_skill_statistics_creation(self):
        """Test creating skill statistics."""
        stats = SkillStatistics(
            mean=0.5,
            median=0.48,
            std_dev=0.15,
            min_val=0.0,
            max_val=1.0,
            percentiles={10: 0.2, 90: 0.8},
            distribution_shape="normal"
        )
        
        assert stats.mean == 0.5
        assert stats.median == 0.48
        assert stats.std_dev == 0.15
        assert stats.distribution_shape == "normal"
        assert stats.percentiles[10] == 0.2
        assert stats.percentiles[90] == 0.8


class TestSkillDistribution:
    """Test the core skill distribution generator."""
    
    @pytest.fixture
    def skill_dist(self):
        """Create a skill distribution generator for testing."""
        return create_skill_distribution()
    
    def test_skill_distribution_creation(self, skill_dist):
        """Test skill distribution generator creation."""
        assert skill_dist is not None
        assert hasattr(skill_dist, 'era_skill_params')
        assert hasattr(skill_dist, 'distribution_cache')
    
    def test_era_skill_params_completeness(self, skill_dist):
        """Test that all eras have skill parameters defined."""
        for era in TechnologyEra:
            assert era in skill_dist.era_skill_params
            era_params = skill_dist.era_skill_params[era]
            assert isinstance(era_params, dict)
            assert len(era_params) > 0  # Should have at least some skills defined
    
    def test_normal_distribution_generation(self, skill_dist):
        """Test normal distribution generation."""
        mean = 0.5
        std_dev = 0.15
        size = 1000
        
        distribution = skill_dist.generate_normal_distribution(mean, std_dev, size)
        
        assert len(distribution) == size
        assert np.all(distribution >= 0.0)  # Within bounds
        assert np.all(distribution <= 1.0)
        
        # Statistical tests (with reasonable tolerance)
        actual_mean = np.mean(distribution)
        actual_std = np.std(distribution)
        
        assert abs(actual_mean - mean) < 0.1  # Within 10% of target
        # Standard deviation might be lower due to truncation
        assert actual_std > 0.05  # Should have some variation
    
    def test_pareto_distribution_generation(self, skill_dist):
        """Test Pareto distribution generation."""
        shape = 1.16
        scale = 0.1
        size = 1000
        
        distribution = skill_dist.generate_pareto_distribution(shape, scale, size)
        
        assert len(distribution) == size
        assert np.all(distribution >= 0.0)  # Within bounds
        assert np.all(distribution <= 1.0)
        
        # Pareto should be right-skewed (most values at lower end)
        median_val = np.median(distribution)
        assert median_val < 0.5  # Should be skewed toward lower values
    
    def test_lognormal_distribution_generation(self, skill_dist):
        """Test log-normal distribution generation."""
        mean = 0.0
        sigma = 0.5
        size = 1000
        
        distribution = skill_dist.generate_lognormal_distribution(mean, sigma, size)
        
        assert len(distribution) == size
        assert np.all(distribution >= 0.0)  # Within bounds
        assert np.all(distribution <= 1.0)
        
        # Should have some variation
        std_val = np.std(distribution)
        assert std_val > 0.05
    
    def test_multimodal_distribution_generation(self, skill_dist):
        """Test multimodal distribution generation."""
        modes = [0.2, 0.8]
        std_dev = 0.1
        size = 1000
        
        distribution = skill_dist.generate_multimodal_distribution(modes, std_dev, size)
        
        assert len(distribution) == size
        assert np.all(distribution >= 0.0)  # Within bounds
        assert np.all(distribution <= 1.0)
        
        # Should have peaks around the modes
        # Check that we have values clustered around both modes
        mode1_count = np.sum((distribution >= 0.1) & (distribution <= 0.3))
        mode2_count = np.sum((distribution >= 0.7) & (distribution <= 0.9))
        
        # Each mode should have a reasonable number of samples
        assert mode1_count > size * 0.2  # At least 20% around first mode
        assert mode2_count > size * 0.2  # At least 20% around second mode
    
    def test_skill_distribution_generation(self, skill_dist):
        """Test era-specific skill distribution generation."""
        skill = "combat"
        era = TechnologyEra.ANCIENT
        size = 1000
        
        distribution = skill_dist.generate_skill_distribution(skill, era, size)
        
        assert len(distribution) == size
        assert np.all(distribution >= 0.0)
        assert np.all(distribution <= 1.0)
        
        # Ancient era combat should have reasonable mean
        mean_val = np.mean(distribution)
        assert 0.2 <= mean_val <= 0.6  # Reasonable range for ancient combat
    
    def test_era_specific_skill_differences(self, skill_dist):
        """Test that different eras produce different skill distributions."""
        skill = "technology"
        size = 1000
        
        ancient_dist = skill_dist.generate_skill_distribution(skill, TechnologyEra.ANCIENT, size)
        future_dist = skill_dist.generate_skill_distribution(skill, TechnologyEra.FUTURE, size)
        
        ancient_mean = np.mean(ancient_dist)
        future_mean = np.mean(future_dist)
        
        # Future era should have higher technology skills than ancient era
        assert future_mean > ancient_mean
        
        # The difference should be substantial
        assert future_mean - ancient_mean > 0.2
    
    def test_distribution_caching(self, skill_dist):
        """Test that distributions are cached for performance."""
        skill = "leadership"
        era = TechnologyEra.CLASSICAL
        size = 1000
        
        # Generate same distribution twice
        dist1 = skill_dist.generate_skill_distribution(skill, era, size)
        dist2 = skill_dist.generate_skill_distribution(skill, era, size)
        
        # Should be cached (exact same values)
        assert np.array_equal(dist1, dist2)
        
        # Different parameters should not be cached together
        dist3 = skill_dist.generate_skill_distribution(skill, TechnologyEra.MODERN, size)
        assert not np.array_equal(dist1, dist3)
    
    def test_distribution_statistics_calculation(self, skill_dist):
        """Test distribution statistics calculation."""
        # Create a known distribution
        test_values = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
        
        stats = skill_dist.calculate_distribution_statistics(test_values)
        
        assert stats.mean == 0.5  # Mean of 0.1 to 0.9
        assert stats.median == 0.5  # Median of symmetric distribution
        assert stats.min_val == 0.1
        assert stats.max_val == 0.9
        assert stats.distribution_shape == "normal"  # Should be detected as normal
        
        # Check percentiles are reasonable
        assert 0.1 <= stats.percentiles[10] <= 0.3
        assert 0.7 <= stats.percentiles[90] <= 0.9
    
    def test_skewness_calculation(self, skill_dist):
        """Test skewness calculation for different distributions."""
        # Right-skewed distribution (Pareto-like)
        right_skewed = skill_dist.generate_pareto_distribution(1.2, 0.1, 1000)
        stats_right = skill_dist.calculate_distribution_statistics(right_skewed)
        
        # Should be detected as right-skewed
        assert stats_right.distribution_shape == "right_skewed"
        
        # Normal distribution
        normal_dist = skill_dist.generate_normal_distribution(0.5, 0.15, 1000)
        stats_normal = skill_dist.calculate_distribution_statistics(normal_dist)
        
        # Should be detected as normal (or close to it)
        assert stats_normal.distribution_shape in ["normal", "right_skewed", "left_skewed"]
    
    def test_empty_distribution_handling(self, skill_dist):
        """Test handling of empty distributions."""
        empty_array = np.array([])
        stats = skill_dist.calculate_distribution_statistics(empty_array)
        
        assert stats.mean == 0
        assert stats.median == 0
        assert stats.std_dev == 0
        assert stats.distribution_shape == "empty"
    
    def test_all_era_all_skills_generation(self, skill_dist):
        """Test generating distributions for all era-skill combinations."""
        size = 100  # Smaller size for performance
        
        for era in TechnologyEra:
            era_params = skill_dist.era_skill_params[era]
            for skill in era_params.keys():
                # Should not raise exceptions
                distribution = skill_dist.generate_skill_distribution(skill, era, size)
                assert len(distribution) == size
                assert np.all(distribution >= 0.0)
                assert np.all(distribution <= 1.0)
    
    def test_distribution_params_validation(self, skill_dist):
        """Test that distribution parameters are reasonable."""
        for era in TechnologyEra:
            era_params = skill_dist.era_skill_params[era]
            for skill, params in era_params.items():
                # Mean should be reasonable
                assert 0.0 <= params.mean <= 1.0
                
                # Standard deviation should be positive and reasonable
                assert 0.01 <= params.std_dev <= 0.5
                
                # Bounds should be valid
                assert params.min_val <= params.max_val
                assert 0.0 <= params.min_val <= 1.0
                assert 0.0 <= params.max_val <= 1.0
                
                # Pareto parameters should be positive
                if params.distribution_type == "pareto":
                    assert params.shape > 0
                    assert params.scale > 0


class TestCitizenSummary:
    """Test citizen summary for statistical modeling."""
    
    def test_citizen_summary_creation(self):
        """Test creating citizen summary."""
        summary = CitizenSummary(
            id="test_id",
            name="Test Citizen",
            skills={"combat": 0.8, "leadership": 0.6},
            composite_score=0.7,
            advisor_potential=0.75,
            era_born=TechnologyEra.ANCIENT,
            age=30
        )
        
        assert summary.id == "test_id"
        assert summary.name == "Test Citizen"
        assert summary.skills["combat"] == 0.8
        assert summary.composite_score == 0.7
        assert summary.advisor_potential == 0.75
        assert summary.era_born == TechnologyEra.ANCIENT
        assert summary.age == 30


class TestDistributionPerformance:
    """Test performance of distribution generation."""
    
    @pytest.fixture
    def skill_dist(self):
        """Create a skill distribution generator for testing."""
        return create_skill_distribution()
    
    def test_large_distribution_generation(self, skill_dist):
        """Test generation of large distributions for performance."""
        skill = "leadership"
        era = TechnologyEra.MODERN
        size = 10000  # Large population
        
        # Should complete in reasonable time
        distribution = skill_dist.generate_skill_distribution(skill, era, size)
        
        assert len(distribution) == size
        assert np.all(distribution >= 0.0)
        assert np.all(distribution <= 1.0)
        
        # Should have reasonable statistical properties
        mean_val = np.mean(distribution)
        std_val = np.std(distribution)
        
        assert 0.1 <= mean_val <= 0.9  # Reasonable mean
        assert std_val > 0.05  # Some variation
    
    def test_multiple_distribution_caching(self, skill_dist):
        """Test caching behavior with multiple distributions."""
        size = 1000
        
        # Generate several distributions to test caching
        for era in [TechnologyEra.ANCIENT, TechnologyEra.MODERN]:
            for skill in ["combat", "leadership", "science"]:
                dist = skill_dist.generate_skill_distribution(skill, era, size)
                assert len(dist) == size
        
        # Cache should have entries
        assert len(skill_dist.distribution_cache) > 0
        
        # Re-generating same distributions should use cache
        cached_dist = skill_dist.generate_skill_distribution("combat", TechnologyEra.ANCIENT, size)
        assert len(cached_dist) == size


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
