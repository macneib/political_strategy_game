#!/usr/bin/env python3
"""
Population Skill Distribution System for Political Advisor System

This module implements population-wide skill distribution tracking with
mathematical realism, era-specific weightings, and computational efficiency
for large populations.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from dataclasses import dataclass
import numpy as np
import random
import math
from collections import defaultdict
import bisect

# Import from existing systems
from .citizen import Citizen, CitizenGenerator, SkillCategory, TraitCategory
from .technology_tree import TechnologyEra
from .advisor import AdvisorRole


@dataclass
class DistributionParams:
    """Parameters for statistical distributions."""
    distribution_type: str  # "normal", "pareto", "lognormal", "multimodal"
    mean: float = 0.5
    std_dev: float = 0.15
    shape: float = 1.16  # For Pareto distribution
    scale: float = 0.1   # For Pareto distribution
    min_val: float = 0.0
    max_val: float = 1.0
    modes: List[float] = None  # For multimodal distributions


@dataclass
class SkillStatistics:
    """Statistical summary of a skill in the population."""
    mean: float
    median: float
    std_dev: float
    min_val: float
    max_val: float
    percentiles: Dict[int, float]  # 10th, 25th, 75th, 90th, 95th, 99th
    distribution_shape: str


@dataclass
class CitizenSummary:
    """Lightweight citizen representation for statistical modeling."""
    id: str
    name: str
    skills: Dict[str, float]
    composite_score: float
    advisor_potential: float
    era_born: TechnologyEra
    age: int


class SkillDistribution:
    """
    Mathematical distribution generator for realistic population skill curves.
    
    Supports normal, Pareto, log-normal, and multimodal distributions for
    different types of skills and populations.
    """
    
    def __init__(self):
        self.distribution_cache = {}
        self.era_skill_params = self._initialize_era_skill_parameters()
    
    def _initialize_era_skill_parameters(self) -> Dict[TechnologyEra, Dict[str, DistributionParams]]:
        """Initialize skill distribution parameters for each era."""
        return {
            TechnologyEra.ANCIENT: {
                "combat": DistributionParams("normal", mean=0.4, std_dev=0.2),
                "crafting": DistributionParams("normal", mean=0.35, std_dev=0.18),
                "leadership": DistributionParams("pareto", shape=1.2, scale=0.1, mean=0.2),
                "agriculture": DistributionParams("normal", mean=0.45, std_dev=0.15),
                "engineering": DistributionParams("pareto", shape=1.8, scale=0.05, mean=0.1),
                "philosophy": DistributionParams("pareto", shape=1.5, scale=0.08, mean=0.15),
                "administration": DistributionParams("normal", mean=0.25, std_dev=0.12)
            },
            TechnologyEra.CLASSICAL: {
                "combat": DistributionParams("normal", mean=0.35, std_dev=0.18),
                "crafting": DistributionParams("normal", mean=0.4, std_dev=0.16),
                "leadership": DistributionParams("pareto", shape=1.2, scale=0.12, mean=0.25),
                "agriculture": DistributionParams("normal", mean=0.4, std_dev=0.14),
                "engineering": DistributionParams("pareto", shape=1.6, scale=0.08, mean=0.15),
                "philosophy": DistributionParams("pareto", shape=1.4, scale=0.1, mean=0.2),
                "administration": DistributionParams("normal", mean=0.3, std_dev=0.15),
                "scholarship": DistributionParams("pareto", shape=1.7, scale=0.06, mean=0.12)
            },
            TechnologyEra.MEDIEVAL: {
                "combat": DistributionParams("normal", mean=0.3, std_dev=0.16),
                "crafting": DistributionParams("normal", mean=0.45, std_dev=0.18),
                "leadership": DistributionParams("pareto", shape=1.15, scale=0.15, mean=0.28),
                "agriculture": DistributionParams("normal", mean=0.35, std_dev=0.13),
                "engineering": DistributionParams("pareto", shape=1.5, scale=0.1, mean=0.18),
                "philosophy": DistributionParams("pareto", shape=1.4, scale=0.1, mean=0.22),
                "administration": DistributionParams("normal", mean=0.35, std_dev=0.16),
                "trade": DistributionParams("normal", mean=0.3, std_dev=0.14),
                "arts": DistributionParams("pareto", shape=1.6, scale=0.08, mean=0.15)
            },
            TechnologyEra.RENAISSANCE: {
                "combat": DistributionParams("normal", mean=0.25, std_dev=0.14),
                "crafting": DistributionParams("normal", mean=0.4, std_dev=0.16),
                "leadership": DistributionParams("pareto", shape=1.1, scale=0.18, mean=0.32),
                "agriculture": DistributionParams("normal", mean=0.3, std_dev=0.12),
                "engineering": DistributionParams("pareto", shape=1.4, scale=0.12, mean=0.22),
                "philosophy": DistributionParams("pareto", shape=1.3, scale=0.12, mean=0.25),
                "administration": DistributionParams("normal", mean=0.4, std_dev=0.17),
                "trade": DistributionParams("normal", mean=0.35, std_dev=0.15),
                "arts": DistributionParams("pareto", shape=1.5, scale=0.1, mean=0.2),
                "scholarship": DistributionParams("pareto", shape=1.6, scale=0.08, mean=0.18),
                "innovation": DistributionParams("pareto", shape=1.8, scale=0.06, mean=0.12)
            },
            TechnologyEra.INDUSTRIAL: {
                "combat": DistributionParams("normal", mean=0.2, std_dev=0.12),
                "crafting": DistributionParams("normal", mean=0.35, std_dev=0.15),
                "leadership": DistributionParams("pareto", shape=1.1, scale=0.2, mean=0.35),
                "agriculture": DistributionParams("normal", mean=0.25, std_dev=0.11),
                "engineering": DistributionParams("normal", mean=0.4, std_dev=0.18),
                "philosophy": DistributionParams("pareto", shape=1.3, scale=0.12, mean=0.22),
                "administration": DistributionParams("normal", mean=0.45, std_dev=0.18),
                "trade": DistributionParams("normal", mean=0.4, std_dev=0.16),
                "science": DistributionParams("pareto", shape=1.5, scale=0.1, mean=0.25),
                "innovation": DistributionParams("pareto", shape=1.7, scale=0.08, mean=0.15),
                "technology": DistributionParams("pareto", shape=1.6, scale=0.09, mean=0.18)
            },
            TechnologyEra.MODERN: {
                "combat": DistributionParams("normal", mean=0.15, std_dev=0.1),
                "leadership": DistributionParams("pareto", shape=1.05, scale=0.22, mean=0.38),
                "engineering": DistributionParams("normal", mean=0.45, std_dev=0.2),
                "administration": DistributionParams("normal", mean=0.5, std_dev=0.19),
                "trade": DistributionParams("normal", mean=0.35, std_dev=0.15),
                "science": DistributionParams("normal", mean=0.4, std_dev=0.18),
                "medicine": DistributionParams("pareto", shape=1.4, scale=0.12, mean=0.3),
                "technology": DistributionParams("normal", mean=0.35, std_dev=0.16),
                "innovation": DistributionParams("pareto", shape=1.6, scale=0.1, mean=0.2)
            },
            TechnologyEra.CONTEMPORARY: {
                "leadership": DistributionParams("pareto", shape=1.0, scale=0.25, mean=0.4),
                "engineering": DistributionParams("normal", mean=0.4, std_dev=0.18),
                "administration": DistributionParams("normal", mean=0.55, std_dev=0.2),
                "trade": DistributionParams("normal", mean=0.3, std_dev=0.14),
                "science": DistributionParams("normal", mean=0.5, std_dev=0.2),
                "medicine": DistributionParams("normal", mean=0.4, std_dev=0.17),
                "technology": DistributionParams("normal", mean=0.5, std_dev=0.2),
                "innovation": DistributionParams("pareto", shape=1.5, scale=0.12, mean=0.25)
            },
            TechnologyEra.FUTURE: {
                "leadership": DistributionParams("pareto", shape=0.95, scale=0.28, mean=0.42),
                "engineering": DistributionParams("normal", mean=0.35, std_dev=0.16),
                "administration": DistributionParams("normal", mean=0.6, std_dev=0.21),
                "trade": DistributionParams("normal", mean=0.25, std_dev=0.12),
                "science": DistributionParams("normal", mean=0.6, std_dev=0.22),
                "medicine": DistributionParams("normal", mean=0.5, std_dev=0.19),
                "technology": DistributionParams("normal", mean=0.7, std_dev=0.25),
                "innovation": DistributionParams("normal", mean=0.5, std_dev=0.2)
            }
        }
    
    def generate_normal_distribution(self, mean: float, std_dev: float, size: int, 
                                   min_val: float = 0.0, max_val: float = 1.0) -> np.ndarray:
        """Generate truncated normal distribution within bounds."""
        # Generate more samples than needed to account for truncation
        samples_needed = int(size * 1.5)  # 50% buffer for truncation
        
        values = []
        attempts = 0
        max_attempts = 10
        
        while len(values) < size and attempts < max_attempts:
            # Generate normal samples
            raw_samples = np.random.normal(mean, std_dev, samples_needed)
            
            # Keep only values within bounds
            valid_samples = raw_samples[(raw_samples >= min_val) & (raw_samples <= max_val)]
            values.extend(valid_samples[:size - len(values)])
            
            attempts += 1
            samples_needed = size - len(values)
        
        # If we still don't have enough samples, fill with uniform distribution
        if len(values) < size:
            remaining = size - len(values)
            uniform_samples = np.random.uniform(min_val, max_val, remaining)
            values.extend(uniform_samples)
        
        return np.array(values[:size])
    
    def generate_pareto_distribution(self, shape: float, scale: float, size: int,
                                   min_val: float = 0.0, max_val: float = 1.0) -> np.ndarray:
        """Generate Pareto distribution scaled to fit within bounds."""
        # Generate Pareto samples
        raw_samples = np.random.pareto(shape, size) * scale + min_val
        
        # Truncate to bounds and normalize
        truncated = np.clip(raw_samples, min_val, max_val)
        
        # If too many samples hit the max, redistribute some randomly
        max_hits = np.sum(truncated == max_val)
        if max_hits > size * 0.1:  # More than 10% at max
            excess_indices = np.where(truncated == max_val)[0]
            # Redistribute half of the excess randomly
            redistribute_count = max_hits // 2
            if redistribute_count > 0:
                random_indices = np.random.choice(excess_indices, redistribute_count, replace=False)
                truncated[random_indices] = np.random.uniform(
                    max_val * 0.7, max_val * 0.95, redistribute_count
                )
        
        return truncated
    
    def generate_lognormal_distribution(self, mean: float, sigma: float, size: int,
                                      min_val: float = 0.0, max_val: float = 1.0) -> np.ndarray:
        """Generate log-normal distribution scaled to fit within bounds."""
        # Generate log-normal samples
        raw_samples = np.random.lognormal(mean, sigma, size)
        
        # Normalize to [0, 1] range first
        if len(raw_samples) > 0:
            min_sample = np.min(raw_samples)
            max_sample = np.max(raw_samples)
            if max_sample > min_sample:
                normalized = (raw_samples - min_sample) / (max_sample - min_sample)
            else:
                normalized = np.full(size, 0.5)
        else:
            normalized = np.full(size, 0.5)
        
        # Scale to desired range
        scaled = normalized * (max_val - min_val) + min_val
        
        return scaled
    
    def generate_multimodal_distribution(self, modes: List[float], std_dev: float, size: int,
                                       min_val: float = 0.0, max_val: float = 1.0) -> np.ndarray:
        """Generate multimodal distribution with specified modes."""
        if not modes:
            return self.generate_normal_distribution(0.5, std_dev, size, min_val, max_val)
        
        # Distribute samples among modes
        samples_per_mode = size // len(modes)
        remaining_samples = size % len(modes)
        
        all_samples = []
        
        for i, mode in enumerate(modes):
            mode_size = samples_per_mode + (1 if i < remaining_samples else 0)
            mode_samples = self.generate_normal_distribution(mode, std_dev, mode_size, min_val, max_val)
            all_samples.extend(mode_samples)
        
        # Shuffle to mix modes
        np.random.shuffle(all_samples)
        return np.array(all_samples)
    
    def generate_skill_distribution(self, skill: str, era: TechnologyEra, size: int) -> np.ndarray:
        """Generate skill distribution for a specific skill in a given era."""
        era_params = self.era_skill_params.get(era, {})
        params = era_params.get(skill)
        
        if params is None:
            # Use default normal distribution for unspecified skills
            params = DistributionParams("normal", mean=0.3, std_dev=0.15)
        
        cache_key = (skill, era.value, size, params.distribution_type)
        if cache_key in self.distribution_cache:
            return self.distribution_cache[cache_key].copy()
        
        if params.distribution_type == "normal":
            distribution = self.generate_normal_distribution(
                params.mean, params.std_dev, size, params.min_val, params.max_val
            )
        elif params.distribution_type == "pareto":
            distribution = self.generate_pareto_distribution(
                params.shape, params.scale, size, params.min_val, params.max_val
            )
        elif params.distribution_type == "lognormal":
            distribution = self.generate_lognormal_distribution(
                params.mean, params.std_dev, size, params.min_val, params.max_val
            )
        elif params.distribution_type == "multimodal":
            modes = params.modes or [0.3, 0.7]
            distribution = self.generate_multimodal_distribution(
                modes, params.std_dev, size, params.min_val, params.max_val
            )
        else:
            # Fallback to normal distribution
            distribution = self.generate_normal_distribution(
                params.mean, params.std_dev, size, params.min_val, params.max_val
            )
        
        # Cache smaller distributions for performance
        if size <= 10000:
            self.distribution_cache[cache_key] = distribution.copy()
        
        return distribution
    
    def calculate_distribution_statistics(self, distribution: np.ndarray) -> SkillStatistics:
        """Calculate comprehensive statistics for a skill distribution."""
        if len(distribution) == 0:
            return SkillStatistics(0, 0, 0, 0, 0, {}, "empty")
        
        mean_val = float(np.mean(distribution))
        median_val = float(np.median(distribution))
        std_val = float(np.std(distribution))
        min_val = float(np.min(distribution))
        max_val = float(np.max(distribution))
        
        percentiles = {
            10: float(np.percentile(distribution, 10)),
            25: float(np.percentile(distribution, 25)),
            75: float(np.percentile(distribution, 75)),
            90: float(np.percentile(distribution, 90)),
            95: float(np.percentile(distribution, 95)),
            99: float(np.percentile(distribution, 99))
        }
        
        # Determine distribution shape
        skewness = self._calculate_skewness(distribution)
        if abs(skewness) < 0.5:
            shape = "normal"
        elif skewness > 0.5:
            shape = "right_skewed"
        else:
            shape = "left_skewed"
        
        return SkillStatistics(
            mean=mean_val,
            median=median_val,
            std_dev=std_val,
            min_val=min_val,
            max_val=max_val,
            percentiles=percentiles,
            distribution_shape=shape
        )
    
    def _calculate_skewness(self, distribution: np.ndarray) -> float:
        """Calculate the skewness of a distribution."""
        if len(distribution) < 3:
            return 0.0
        
        mean_val = np.mean(distribution)
        std_val = np.std(distribution)
        
        if std_val == 0:
            return 0.0
        
        skewness = np.mean(((distribution - mean_val) / std_val) ** 3)
        return float(skewness)


def create_skill_distribution() -> SkillDistribution:
    """Factory function to create a skill distribution generator."""
    return SkillDistribution()
